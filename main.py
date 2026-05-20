import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import traceback

import Converter
import Cargador
import EmailSender
import Auditoria


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
            log(f"📂  Cargando: {archivo}")

            registros, auditoria = Cargador.cargar_registros(archivo, auditoria)
            total_reg = len(registros)
            log(f"✅  {total_reg} registro(s) cargados.\n")

            ok = 0
            errores = 0

            for i, persona in enumerate(registros, 1):
                nombre = getattr(persona, "nombre", f"Registro {i}")
                log(f"🔄  [{i}/{total_reg}] {nombre}")

                try:
                    # ── Generar PDF ───────────────────────────────────
                    resultado, auditoria = Converter.generar_pdf(
                        persona, auditoria
                    )

                    # ── Enviar correos ────────────────────────────────
                    auditoria = EmailSender.enviar_correos(
                        persona, resultado, auditoria
                    )

                    ok += 1

                except Exception as e:
                    log(f"   ❌  {e}", "error")
                    log(traceback.format_exc(), "error")
                    errores += 1

                finally:
                    # Muestra lo que se logró, incluso si falló a mitad
                    log_auditoria(nombre, auditoria.get(nombre, {}))

            # ── Resumen final ────────────────────────────────────────
            log(f"\n{'─'*50}")
            log(
                f"✔️  Finalizó.  Correctos: {ok}   Con errores: {errores}",
                "ok" if errores == 0 else "warn"
            )
            Auditoria.generar_auditoria(auditoria)

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