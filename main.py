from time import perf_counter
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import Converter
import Cargador
import EmailSender
import Auditoria
import Monitoreo


def seleccionar_archivo():
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
    )
    if ruta:
        entrada_archivo.set(ruta)


def log(mensaje, color="white"):
    area_log.config(state="normal")
    area_log.insert(tk.END, mensaje + "\n", color)
    area_log.see(tk.END)
    area_log.config(state="disabled")


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
    color  = "warn" if (mensaje and mensaje != "Procesado correctamente") else "white"
    log(f"   └ {ultimo}", color)


def ejecutar_proceso():
    archivo = entrada_archivo.get().strip()
    if not archivo:
        log("⚠️  Por favor seleccioná un archivo Excel primero.", "warn")
        return

    boton_ejecutar.config(state="disabled")
    area_log.config(state="normal")
    area_log.delete("1.0", tk.END)
    area_log.config(state="disabled")

    def proceso():
        try:
            auditoria = {}
            instrucciones = {}
            monitoreo = {}
            log(f"📂  Cargando: {archivo}")

            registros, auditoria, monitoreo = Cargador.cargar_registros(archivo, auditoria, monitoreo)
            total_reg = len(registros)
            log(f"✅  {total_reg} registro(s) cargados.\n")

            inicio_proceso = perf_counter()

            # ── FASE 1: Generar PDFs en paralelo ──────────────────────────────
            log("⏳ Fase 1: Generando PDFs en paralelo...")
            t_gen_inicio = perf_counter()
            
            tiempos_generacion = []
            resultados_pdf = {}  # {nombre: {"pdf_principal": Path, "pdf_fiador": Path}}
            auditoria_lock_gen = threading.Lock()
            
            def _generar_pdf_persona(persona):
                try:
                    resultado, aud= Converter.generar_pdf(persona, {})
                    t_gen = aud.get(persona.nombre, {}).get("tiempo_generacion", 0)
                    tiempos_generacion.append(t_gen)
                    
                    # Thread-safe update de auditoría
                    with auditoria_lock_gen:
                        auditoria.update(aud)
                    
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

            max_workers_pdf = min(4, total_reg)
            with ThreadPoolExecutor(max_workers=max_workers_pdf) as executor:
                futures = {executor.submit(_generar_pdf_persona, p): p for p in registros}
                for future in as_completed(futures):
                    try:
                        nombre, resultado = future.result()
                        resultados_pdf[nombre] = resultado
                    except Exception as e:
                        persona = futures[future]
                        log(f"   ⚠️  Excepción en thread PDF para {persona.nombre}: {e}", "warn")

            t_gen_total = perf_counter() - t_gen_inicio
            log(f"✅ PDFs generados en {t_gen_total:.2f}s (promedio: {sum(tiempos_generacion)/len(tiempos_generacion):.2f}s por PDF)\n" if tiempos_generacion else "✅ PDFs generados\n")

            # ── FASE 2: Enviar correos en paralelo ────────────────────────────
            log("⏳ Fase 2: Enviando correos en paralelo...")
            t_envio_inicio = perf_counter()
            
            tiempos_envio = []
            auditoria_lock = threading.Lock()
            
            def _enviar_correo_persona(persona):
                try:
                    resultado = resultados_pdf.get(persona.nombre, {"pdf_principal": None, "pdf_fiador": None})
                    t_env_inicio = perf_counter()
                    auditoria_actualizada = EmailSender.enviar_correos(persona, resultado, auditoria)
                    t_env = perf_counter() - t_env_inicio
                    tiempos_envio.append(t_env)
                    
                    # Thread-safe update de auditoría
                    with auditoria_lock:
                        auditoria.update(auditoria_actualizada)
                    
                    return persona.nombre
                except Exception as e:
                    log(f"   ❌ Error enviando correo para {persona.nombre}: {e}", "error")
                    with auditoria_lock:
                        if persona.nombre in auditoria:
                            auditoria[persona.nombre]["error_envio"] = str(e)
                    return persona.nombre

            max_workers_email = min(6, total_reg)
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

            t_envio_total = perf_counter() - t_envio_inicio
            log(f"✅ Correos enviados en {t_envio_total:.2f}s (promedio: {sum(tiempos_envio)/len(tiempos_envio):.2f}s por correo)\n" if tiempos_envio else "✅ Correos enviados\n")

            # ── Logs finales por persona ──────────────────────────────────────
            log("📋 Resumen de procesamiento:")
            ok = 0
            errores = 0
            for i, persona in enumerate(registros, 1):
                nombre = getattr(persona, "nombre", f"Registro {i}")
                info = auditoria.get(nombre, {})
                
                # Contar como éxito si se generó PDF y correo
                if info.get("notificacion_generada") or info.get("correo_deudor_enviado"):
                    ok += 1
                else:
                    errores += 1
                
                log(f"   [{i}/{total_reg}] {nombre}")
                log_auditoria(nombre, info)

            # ── Métricas finales ──────────────────────────────────────────────
            t_total = perf_counter() - inicio_proceso
            
            monitoreo["metricas_proceso"] = {
                "Tiempo_fase_generacion": round(t_gen_total, 4),
                "Tiempo_fase_envio": round(t_envio_total, 4),
                "Tiempo_promedio_generacion": round(sum(tiempos_generacion) / len(tiempos_generacion), 4) if tiempos_generacion else 0,
                "Tiempo_promedio_envio": round(sum(tiempos_envio) / len(tiempos_envio), 4) if tiempos_envio else 0,
                "Tiempo_total_proceso": round(t_total, 4),
                "Registros_procesados": total_reg,
                "Exitosos": ok,
                "Con_errores": errores,
                "Workers_PDF": max_workers_pdf,
                "Workers_Correo": max_workers_email,
            }

            # ── Resumen final ─────────────────────────────────────────────────
            log(f"\n{'─'*50}")
            log(
                f"✔️  Finalizó.  Correctos: {ok}   Con errores: {errores}",
                "ok" if errores == 0 else "warn"
            )
            log(f"Tiempo total: {t_total:.2f}s ({t_total/total_reg:.2f}s por registro)\n", "ok")
            
            Auditoria.generar_auditoria(auditoria)
            Monitoreo.generar_monitoreo(monitoreo)
            
            try:
                Converter.shutdown_playwright()
            except Exception:
                pass

        except Exception as e:
            log(f"\n❌  Error general: {e}", "error")
            log(traceback.format_exc(), "error")

        finally:
            boton_ejecutar.config(state="normal")

    threading.Thread(target=proceso, daemon=True).start()


# ── Ventana principal ──────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Procesador de Cuotas Atrasadas")
ventana.geometry("680x480")
ventana.resizable(False, False)

# ── Paleta institucional ───────────────────────────────────────────
COLOR_FONDO        = "#F4F6F9"   # Blanco grisáceo
COLOR_NAVY         = "#0A2342"   # Azul marino
COLOR_NAVY_LIGHT   = "#163B65"
COLOR_ROJO         = "#B22222"   # Rojo institucional
COLOR_BLANCO       = "#FFFFFF"
COLOR_TEXTO        = "#1F2937"
COLOR_BORDER       = "#CBD5E1"

ventana.configure(bg=COLOR_FONDO)

entrada_archivo = tk.StringVar()

FONT       = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)

# ── Sección selección de archivo ──────────────────────────────────
frame_top = tk.Frame(
    ventana,
    bg=COLOR_FONDO,
    pady=18
)
frame_top.pack(fill="x", padx=20)

tk.Label(
    frame_top,
    text="Archivo Excel",
    bg=COLOR_FONDO,
    fg=COLOR_NAVY,
    font=("Segoe UI", 10, "bold")
).pack(anchor="w")

frame_fila = tk.Frame(
    frame_top,
    bg=COLOR_FONDO
)
frame_fila.pack(fill="x", pady=(6, 0))

tk.Entry(
    frame_fila,
    textvariable=entrada_archivo,

    bg=COLOR_BLANCO,
    fg=COLOR_TEXTO,
    insertbackground=COLOR_NAVY,

    relief="flat",
    font=FONT,
    bd=0,

    highlightthickness=1,
    highlightbackground=COLOR_BORDER,
    highlightcolor=COLOR_NAVY_LIGHT

).pack(
    side="left",
    fill="x",
    expand=True,
    ipady=6,
    padx=(0, 8)
)

tk.Button(
    frame_fila,
    text="Buscar…",
    command=seleccionar_archivo,

    bg=COLOR_NAVY,
    fg=COLOR_BLANCO,

    activebackground=COLOR_NAVY_LIGHT,
    activeforeground=COLOR_BLANCO,

    relief="flat",
    font=FONT_LABEL,

    padx=12,
    pady=4,

    cursor="hand2",
    bd=0

).pack(side="left")

# ── Botón ejecutar ────────────────────────────────────────────────
boton_ejecutar = tk.Button(
    ventana,

    text="▶  Ejecutar proceso",
    command=ejecutar_proceso,

    bg=COLOR_ROJO,
    fg=COLOR_BLANCO,

    activebackground="#8B1E1E",
    activeforeground=COLOR_BLANCO,

    relief="flat",

    font=("Segoe UI", 11, "bold"),

    padx=20,
    pady=8,

    cursor="hand2",
    bd=0
)

boton_ejecutar.pack(
    pady=(0, 14)
)

# ── Área de log ───────────────────────────────────────────────────
frame_log = tk.Frame(
    ventana,
    bg=COLOR_FONDO,
    padx=20
)

frame_log.pack(
    fill="both",
    expand=True,
    pady=(0, 16)
)

tk.Label(
    frame_log,
    text="Log de ejecución",

    bg=COLOR_FONDO,
    fg=COLOR_NAVY,

    font=("Segoe UI", 9, "bold")

).pack(anchor="w", pady=(0, 4))

area_log = scrolledtext.ScrolledText(

    frame_log,

    bg=COLOR_BLANCO,
    fg=COLOR_TEXTO,

    insertbackground=COLOR_NAVY,

    relief="flat",

    font=FONT,

    state="disabled",
    wrap="word",

    bd=0,

    highlightthickness=1,
    highlightbackground=COLOR_BORDER

)

area_log.pack(fill="both", expand=True)

# ── Tags del log ──────────────────────────────────────────────────
area_log.tag_config(
    "ok",
    foreground="#1E7F37"
)

area_log.tag_config(
    "error",
    foreground=COLOR_ROJO
)

area_log.tag_config(
    "warn",
    foreground="#C77D00"
)

ventana.mainloop()