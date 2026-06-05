from time import perf_counter
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import Converter
import Cargador
import EmailSender
import Auditoria
import Monitoreo
import sys


# ── Manejo global de excepciones ──────────────────────────────────
def _handle_uncaught(exc_type, exc_value, exc_tb):
    try:
        with open("error.log", "w", encoding="utf-8") as fh:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=fh)
    except Exception:
        pass
    try:
        import tkinter.messagebox as mb
        mb.showerror("Error de la aplicación", "Ocurrió un error. Revisá error.log para más detalles.")
    except Exception:
        pass


sys.excepthook = _handle_uncaught


def _thread_excepthook(args):
    _handle_uncaught(args.exc_type, args.exc_value, args.exc_traceback)


try:
    threading.excepthook = _thread_excepthook
except Exception:
    pass


# ── Helpers de UI ─────────────────────────────────────────────────
def seleccionar_archivo():
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
    )
    if ruta:
        entrada_archivo.set(ruta)


def log(mensaje, color="white"):
    """Thread-safe: encola la escritura en el hilo principal de Tkinter."""
    def _escribir():
        area_log.config(state="normal")
        area_log.insert(tk.END, mensaje + "\n", color)
        area_log.see(tk.END)
        area_log.config(state="disabled")
    ventana.after(0, _escribir)


def log_auditoria(nombre, info: dict):
    """Muestra el resumen de auditoría de una persona en el log."""
    pdf_ok      = "✅" if info.get("notificacion_generada")       else "❌"
    pdf_fiador  = "✅" if info.get("notificacion_fiador_generada") else "—"
    mail_deudor = "✅" if info.get("correo_deudor_enviado")        else "❌"
    mail_fiador = "✅" if info.get("correo_fiador_enviado")        else "—"
    cuotas      = info.get("cuotas_atrasadas", "?")
    total       = info.get("total", "?")
    mensaje     = info.get("mensaje", "")
    error_envio = info.get("error_envio", "")

    log(f"   ├ PDF:    notif. {pdf_ok}   fiador {pdf_fiador}")
    log(f"   ├ Correo: deudor {mail_deudor}   fiador {mail_fiador}")
    log(f"   ├ Cuotas atras.: {cuotas}   Total: {total}")

    if error_envio:
        log(f"   ├ ⚠️  {error_envio}", "warn")

    ultimo = mensaje or "Procesado correctamente"
    color_msg = "warn" if (mensaje and mensaje != "Procesado correctamente") else "white"
    log(f"   └ {ultimo}", color_msg)


# ── Cancelación ───────────────────────────────────────────────────
_cancelar_evento = threading.Event()


def cancelar_proceso():
    _cancelar_evento.set()
    log("🛑 Cancelación solicitada — esperando que terminen las tareas en curso...", "warn")
    ventana.after(0, lambda: boton_cancelar.config(state="disabled"))


# ── Proceso principal ─────────────────────────────────────────────
def ejecutar_proceso():
    archivo = entrada_archivo.get().strip()
    if not archivo:
        log("⚠️  Por favor seleccioná un archivo Excel primero.", "warn")
        return

    cuenta = cuenta_seleccionada.get().strip()
    if not cuenta:
        log("⚠️  Por favor seleccioná una cuenta de Outlook.", "warn")
        return

    _cancelar_evento.clear()
    boton_ejecutar.config(state="disabled")
    boton_cancelar.config(state="normal")
    area_log.config(state="normal")
    area_log.delete("1.0", tk.END)
    area_log.config(state="disabled")

    def proceso():
        try:
            auditoria = {}
            log(f"📂  Cargando: {archivo}")

            proceso_inicio = perf_counter()

            monitoreo = {}
            registros, auditoria, monitoreo = Cargador.cargar_registros(archivo, auditoria, monitoreo)

            total_reg = len(registros)
            if total_reg == 0:
                log("⚠️  No se encontraron registros para procesar.", "warn")
                return

            # ── FASE 1: Generar PDFs en paralelo ──────────────────────────────
            log("⏳ Fase 1: Generando PDFs en paralelo...")

            resultados_pdf = {}
            pdf_inicio = perf_counter()
            pdf_stats = {"exitos": 0, "fallidos": 0}
            pdf_stats_lock = threading.Lock()
            auditoria_lock_gen = threading.Lock()

            def _generar_pdf_persona(persona):
                if _cancelar_evento.is_set():
                    return persona.nombre, {"pdf_principal": None, "pdf_fiador": None}
                try:
                    resultado, aud = Converter.generar_pdf(persona, {})
                    with auditoria_lock_gen:
                        auditoria.update(aud)
                    with pdf_stats_lock:
                        if resultado.get("pdf_principal"):
                            pdf_stats["exitos"] += 1
                        else:
                            pdf_stats["fallidos"] += 1
                    return persona.nombre, resultado
                except Exception as e:
                    log(f"   ❌ Error generando PDF para {persona.nombre}: {e}", "error")
                    error_entry = {
                        "fecha": perf_counter(),
                        "estado": getattr(persona, "estado", None),
                        "cuotas_atrasadas": getattr(persona, "cuotas_atrasadas", 0),
                        "total": getattr(persona, "total", None),
                        "notificacion_generada": False,
                        "notificacion_fiador_generada": False,
                        "correo_fiador": False,
                        "correo_deudor_enviado": False,
                        "correo_fiador_enviado": False,
                        "error_envio": str(e),
                        "mensaje": f"Error en generación: {e}",
                    }
                    with auditoria_lock_gen:
                        auditoria[persona.nombre] = error_entry
                    return persona.nombre, {"pdf_principal": None, "pdf_fiador": None}

            max_workers_pdf = max(1, min(4, total_reg))
            with ThreadPoolExecutor(max_workers=max_workers_pdf) as executor:
                futures = {executor.submit(_generar_pdf_persona, p): p for p in registros}
                for future in as_completed(futures):
                    try:
                        nombre, resultado = future.result()
                        resultados_pdf[nombre] = resultado
                    except Exception as e:
                        persona = futures[future]
                        log(f"   ⚠️  Excepción en thread PDF para {persona.nombre}: {e}", "warn")
                        with pdf_stats_lock:
                            pdf_stats["fallidos"] += 1

            if _cancelar_evento.is_set():
                log("🛑 Proceso cancelado en Fase 1 (PDFs).", "warn")
                return

            monitoreo["pdf"] = {
                "tiempo_segundos": round(perf_counter() - pdf_inicio, 4),
                "registros_totales": total_reg,
                "registros_exitosos": pdf_stats["exitos"],
                "registros_fallidos": pdf_stats["fallidos"],
                "workers_usados": max_workers_pdf,
            }

            # ── FASE 2: Enviar correos en paralelo ────────────────────────────
            log("⏳ Fase 2: Enviando correos en paralelo...")
            max_workers_email = max(1, min(6, total_reg))
            t_envio_inicio = perf_counter()
            auditoria_lock = threading.Lock()

            def _enviar_correo_persona(persona):
                if _cancelar_evento.is_set():
                    return persona.nombre
                try:
                    resultado = resultados_pdf.get(persona.nombre, {"pdf_principal": None, "pdf_fiador": None})
                    auditoria_actualizada = EmailSender.enviar_correos(
                        persona,
                        resultado,
                        auditoria,
                        cuenta_smtp=cuenta
                    )
                    with auditoria_lock:
                        auditoria.update(auditoria_actualizada)
                    return persona.nombre
                except Exception as e:
                    log(f"   ❌ Error enviando correo para {persona.nombre}: {e}", "error")
                    with auditoria_lock:
                        if persona.nombre in auditoria:
                            auditoria[persona.nombre]["error_envio"] = str(e)
                    return persona.nombre

            with ThreadPoolExecutor(max_workers=max_workers_email) as executor:
                futures = {executor.submit(_enviar_correo_persona, p): p for p in registros}
                completados = 0
                for future in as_completed(futures):
                    try:
                        future.result()
                        completados += 1
                    except Exception as e:
                        persona = futures[future]
                        log(f"   ⚠️  Excepción en thread correo para {persona.nombre}: {e}", "warn")

            if _cancelar_evento.is_set():
                log("🛑 Proceso cancelado en Fase 2 (correos).", "warn")
                return

            envios_exitosos = sum(
                1 for persona in registros
                if auditoria.get(persona.nombre, {}).get("correo_deudor_enviado")
                or auditoria.get(persona.nombre, {}).get("correo_fiador_enviado")
            )
            envios_errores = sum(
                1 for persona in registros
                if auditoria.get(persona.nombre, {}).get("error_envio")
            )

            monitoreo["email"] = {
                "tiempo_segundos": round(perf_counter() - t_envio_inicio, 4),
                "registros_totales": total_reg,
                "envios_intentados": completados,
                "envios_exitosos": envios_exitosos,
                "errores": envios_errores,
                "workers_usados": max_workers_email,
            }

            # ── Logs finales por persona ──────────────────────────────────────
            log("📋 Resumen de procesamiento:")
            ok = 0
            errores = 0
            for i, persona in enumerate(registros, 1):
                nombre = getattr(persona, "nombre", f"Registro {i}")
                info = auditoria.get(nombre, {})
                if info.get("notificacion_generada") or info.get("correo_deudor_enviado"):
                    ok += 1
                else:
                    errores += 1
                log_auditoria(nombre, info)

            monitoreo["resumen"] = {
                "personas_totales": total_reg,
                "correctos": ok,
                "errores": errores,
                "porcentaje_exito": round(ok / total_reg * 100, 2) if total_reg else 0.0,
            }

            monitoreo["proceso"] = {
                "tiempo_total_segundos": round(perf_counter() - proceso_inicio, 4),
                "personas_totales": total_reg,
                "etapas": ["cargador", "pdf", "email", "resumen"],
            }

            # ── Resumen final ─────────────────────────────────────────────────
            log(f"\n{'─'*50}")
            log(
                f"✔️  Finalizó.  Correctos: {ok}   Con errores: {errores}",
                "ok" if errores == 0 else "warn"
            )
            Auditoria.generar_auditoria(auditoria)
            
            # Generar auditoría de errores si hay errores
            archivo_errores = Auditoria.generar_auditoria_errores(auditoria)
            if archivo_errores:
                log(f"⚠️  Auditoría de errores guardada en: {archivo_errores}", "warn")
            
            try:
                archivo_monitoreo = Monitoreo.generar_monitoreo(monitoreo)
                log(f"📊 Monitoreo guardado en: {archivo_monitoreo}")
            except Exception as e:
                log(f"⚠️  No se pudo generar el monitoreo: {e}", "warn")

            try:
                Converter.shutdown_playwright()
            except Exception:
                pass

        except Exception as e:
            log(f"\n❌  Error general: {e}", "error")
            log(traceback.format_exc(), "error")

        finally:
            def _restaurar_botones():
                boton_ejecutar.config(state="normal")
                boton_cancelar.config(state="disabled")
            ventana.after(0, _restaurar_botones)

    threading.Thread(target=proceso, daemon=True).start()


# ── Ventana principal ──────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Procesador de Cuotas Atrasadas")
ventana.geometry("680x480")
ventana.resizable(False, False)

# ── Paleta institucional ───────────────────────────────────────────
COLOR_FONDO      = "#F4F6F9"
COLOR_NAVY       = "#0A2342"
COLOR_NAVY_LIGHT = "#163B65"
COLOR_ROJO       = "#B22222"
COLOR_BLANCO     = "#FFFFFF"
COLOR_TEXTO      = "#1F2937"
COLOR_BORDER     = "#CBD5E1"

ventana.configure(bg=COLOR_FONDO)

entrada_archivo    = tk.StringVar()
cuenta_seleccionada = tk.StringVar()

FONT       = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)

# ── Sección selección de archivo ──────────────────────────────────
frame_top = tk.Frame(ventana, bg=COLOR_FONDO, pady=18)
frame_top.pack(fill="x", padx=20)

tk.Label(
    frame_top, text="Archivo Excel",
    bg=COLOR_FONDO, fg=COLOR_NAVY,
    font=("Segoe UI", 10, "bold")
).pack(anchor="w")

frame_fila = tk.Frame(frame_top, bg=COLOR_FONDO)
frame_fila.pack(fill="x", pady=(6, 0))

tk.Entry(
    frame_fila, textvariable=entrada_archivo,
    bg=COLOR_BLANCO, fg=COLOR_TEXTO,
    insertbackground=COLOR_NAVY,
    relief="flat", font=FONT, bd=0,
    highlightthickness=1,
    highlightbackground=COLOR_BORDER,
    highlightcolor=COLOR_NAVY_LIGHT
).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

tk.Button(
    frame_fila, text="Buscar…", command=seleccionar_archivo,
    bg=COLOR_NAVY, fg=COLOR_BLANCO,
    activebackground=COLOR_NAVY_LIGHT, activeforeground=COLOR_BLANCO,
    relief="flat", font=FONT_LABEL,
    padx=12, pady=4, cursor="hand2", bd=0
).pack(side="left")

# ── Sección selección de cuenta ───────────────────────────────────
frame_cuenta = tk.Frame(ventana, bg=COLOR_FONDO, pady=16)
frame_cuenta.pack(fill="x", padx=20)

tk.Label(
    frame_cuenta, text="Cuenta de Outlook",
    bg=COLOR_FONDO, fg=COLOR_NAVY,
    font=("Segoe UI", 10, "bold")
).pack(anchor="w")

frame_cuenta_fila = tk.Frame(frame_cuenta, bg=COLOR_FONDO)
frame_cuenta_fila.pack(fill="x", pady=(6, 0))

combo_cuentas = ttk.Combobox(
    frame_cuenta_fila,
    textvariable=cuenta_seleccionada,
    state="readonly", width=40, font=FONT
)
combo_cuentas.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))

# FIX: separar creación del widget de su empaquetado para conservar la referencia
boton_refrescar_cuentas = tk.Button(
    frame_cuenta_fila, text="🔄 Refrescar",
    command=lambda: refrescar_cuentas(),
    bg=COLOR_NAVY, fg=COLOR_BLANCO,
    activebackground=COLOR_NAVY_LIGHT, activeforeground=COLOR_BLANCO,
    relief="flat", font=FONT_LABEL,
    padx=12, pady=4, cursor="hand2", bd=0
)
boton_refrescar_cuentas.pack(side="left")

# ── Funciones para manejar cuentas ────────────────────────────────
def cargar_cuentas_outlook():
    try:
        cuentas = EmailSender.obtener_cuentas_outlook()
        if cuentas:
            combo_cuentas['values'] = cuentas
            combo_cuentas.set(cuentas[0])
            boton_refrescar_cuentas.config(state="normal")
            return True
        else:
            combo_cuentas['values'] = []
            combo_cuentas.set("")
            messagebox.showwarning("Sin cuentas", "No se encontraron cuentas configuradas en Outlook.")
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar cuentas de Outlook: {e}")
        combo_cuentas['values'] = []
        return False


def refrescar_cuentas():
    boton_refrescar_cuentas.config(state="disabled")
    if cargar_cuentas_outlook():
        log("✅ Cuentas recargadas", "ok")
    else:
        log("❌ Error al recargar cuentas", "error")


# ── Botones ejecutar / cancelar ───────────────────────────────────
frame_botones = tk.Frame(ventana, bg=COLOR_FONDO)
frame_botones.pack(pady=(0, 14))

boton_ejecutar = tk.Button(
    frame_botones, text="▶  Ejecutar proceso",
    command=ejecutar_proceso,
    bg=COLOR_ROJO, fg=COLOR_BLANCO,
    activebackground="#8B1E1E", activeforeground=COLOR_BLANCO,
    relief="flat", font=("Segoe UI", 11, "bold"),
    padx=20, pady=8, cursor="hand2", bd=0
)
boton_ejecutar.pack(side="left", padx=(0, 8))

boton_cancelar = tk.Button(
    frame_botones, text="✖  Cancelar",
    command=cancelar_proceso,
    bg="#6B7280", fg=COLOR_BLANCO,
    activebackground="#4B5563", activeforeground=COLOR_BLANCO,
    relief="flat", font=("Segoe UI", 11, "bold"),
    padx=20, pady=8, cursor="hand2", bd=0,
    state="disabled"
)
boton_cancelar.pack(side="left")

# ── Área de log ───────────────────────────────────────────────────
frame_log = tk.Frame(ventana, bg=COLOR_FONDO, padx=20)
frame_log.pack(fill="both", expand=True, pady=(0, 16))

tk.Label(
    frame_log, text="Log de ejecución",
    bg=COLOR_FONDO, fg=COLOR_NAVY,
    font=("Segoe UI", 9, "bold")
).pack(anchor="w", pady=(0, 4))

area_log = scrolledtext.ScrolledText(
    frame_log,
    bg=COLOR_BLANCO, fg=COLOR_TEXTO,
    insertbackground=COLOR_NAVY,
    relief="flat", font=FONT,
    state="disabled", wrap="word",
    bd=0, highlightthickness=1,
    highlightbackground=COLOR_BORDER
)
area_log.pack(fill="both", expand=True)

# ── Tags del log ──────────────────────────────────────────────────
area_log.tag_config("ok",    foreground="#1E7F37")
area_log.tag_config("error", foreground=COLOR_ROJO)
area_log.tag_config("warn",  foreground="#C77D00")

# ── Cargar cuentas al iniciar ──────────────────────────────────────
ventana.after(100, cargar_cuentas_outlook)

ventana.mainloop()