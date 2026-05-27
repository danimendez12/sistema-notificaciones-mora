from pathlib import Path
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

from Model import Persona


BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "Templates"
OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)

# ── Validación temprana del logo ──────────────────────────────────────────────
_logo = TEMPLATES_DIR / "assets" / "ENcabezado-Tesoreria.png"
if not _logo.exists():
    raise FileNotFoundError(f"Logo no encontrado: {_logo}")
logo_path = _logo.as_uri()

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)

# ── Mapa de plantillas ────────────────────────────────────────────────────────
MAPA_PLANTILLAS = {
    0: "Plantilla-1-AlDia.html",
    1: "Plantilla-2-CUotas-Atrasadas.html",
    2: "Plantilla-2-CUotas-Atrasadas.html",
    3: "Plantilla-2-CUotas-Atrasadas.html",
    4: "Plantilla-3-Aviso-Cobro.html",
}


def _resolver_plantilla(cuotas: int) -> str:
    """Devuelve el nombre de plantilla según las cuotas atrasadas."""
    return MAPA_PLANTILLAS.get(cuotas, "Plantilla-4-Cobro-Judicial.html")


# ── BrowserPool con thread-local storage ──────────────────────────────────────
class ThreadLocalBrowserPool:
    """Thread-local browser pool: cada thread tiene su propio browser."""

    def __init__(self):
        self._local = threading.local()
        self._master_lock = threading.Lock()
        self._all_browsers = []

    def get_browser(self):
        """Obtiene o crea un browser para el thread actual."""
        if not hasattr(self._local, 'pw') or not hasattr(self._local, 'browser'):
            self._local.pw = sync_playwright().start()
            self._local.browser = self._local.pw.chromium.launch()
            # Registra para cierre ordenado
            with self._master_lock:
                self._all_browsers.append((self._local.pw, self._local.browser))
        return self._local.browser

    def shutdown(self):
        """Cierra todos los browsers de todos los threads."""
        with self._master_lock:
            for pw, browser in self._all_browsers:
                try:
                    if browser:
                        browser.close()
                except Exception:
                    pass
                finally:
                    try:
                        if pw:
                            pw.stop()
                    except Exception:
                        pass
            self._all_browsers.clear()


_pool = ThreadLocalBrowserPool()


def html_to_pdf_sync(html_content: str, pdf_output: Path) -> None:
    """
    Convierte HTML a PDF usando un contexto aislado por conversión.
    Usa domcontentloaded en lugar de networkidle para archivos locales,
    lo cual es ~30-50 % más rápido.
    """
    temp_html = pdf_output.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")

    browser = _pool.get_browser()
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(temp_html.as_uri(), wait_until="domcontentloaded")
        page.pdf(path=str(pdf_output), format="A4", print_background=True)
    finally:
        context.close()
        temp_html.unlink(missing_ok=True)


def shutdown_playwright():
    """Cierra el browser y Playwright de forma ordenada."""
    _pool.shutdown()


# ── Generación de PDFs ────────────────────────────────────────────────────────
def _generar_todos_sync(
    template,
    templateFiador,
    context: dict,
    pdf_principal: Path,
    pdf_fiador_path: Path | None,
    auditoria_persona: dict,
) -> None:
    html = template.render(**context)
    html_to_pdf_sync(html, pdf_principal)
    auditoria_persona["notificacion_generada"] = True
    

    if templateFiador and pdf_fiador_path:
        html_fiador = templateFiador.render(**context)
        html_to_pdf_sync(html_fiador, pdf_fiador_path)
        auditoria_persona["notificacion_fiador_generada"] = True
        


def generar_pdf(
    persona: Persona,
    auditoria: dict,
) -> tuple[dict[str, Path | None], dict, dict]:

    auditoria_persona = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": persona.estado,
        "cuotas_atrasadas": int(persona.cuotas_atrasadas),
        "total": persona.total_formateado,
        "notificacion_generada": False,
        "notificacion_fiador_generada": False,
        "correo_fiador": bool(persona.correo_fiador),
        "mensaje": "",
    }


    def _registrar_y_retornar(mensaje: str) -> tuple[dict[str, Path | None], dict, dict]:
        auditoria_persona["mensaje"] = mensaje
        auditoria[persona.nombre] = auditoria_persona
        return {"pdf_principal": None, "pdf_fiador": None}, auditoria
    # ── Validación de estado ──────────────────────────────────────────────────
    estado = persona.estado
    if estado != "NORMAL":
        return _registrar_y_retornar(f"Estado no reconocido: {estado}")

    # ── Selección de plantilla via mapa ───────────────────────────────────────
    cuotas = int(persona.cuotas_atrasadas)
    nombre_template = _resolver_plantilla(cuotas)
    template = env.get_template(nombre_template)

    # ── Fiador ────────────────────────────────────────────────────────────────
    templateFiador = None
    tiene_fiador = bool(persona.fiador and persona.correo_fiador)

    if cuotas >= 1 and tiene_fiador:
        templateFiador = env.get_template("Plantilla-5-Fiador.html")
    elif cuotas >= 1:
        auditoria_persona["mensaje"] = "Sin información de fiador"

    # ── Paths de salida ───────────────────────────────────────────────────────
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", persona.nombre)
    persona_dir = OUTPUT_DIR / safe_name
    persona_dir.mkdir(parents=True, exist_ok=True)

    pdf_principal = persona_dir / f"Notificacion-{safe_name}.pdf"
    pdf_fiador = persona_dir / f"Fiador-{safe_name}.pdf" if templateFiador else None

    context = {
        "nombre": persona.nombre,
        "estado": estado,
        "cuotas": cuotas,
        "fecha_proximo_pago": persona.fecha_proximo_pago,
        "total": persona.total_formateado,
        "fiador": persona.fiador,
        "correo_fiador": persona.correo_fiador,
        "logo_path": logo_path,
    }

    t_gen_inicio = time.perf_counter()
    _generar_todos_sync(
        template,
        templateFiador,
        context,
        pdf_principal,
        pdf_fiador,
        auditoria_persona,
    )
    auditoria_persona["tiempo_generacion"] = round(
        time.perf_counter() - t_gen_inicio, 4
    )

    if not auditoria_persona["mensaje"]:
        auditoria_persona["mensaje"] = "Procesado correctamente"

    auditoria[persona.nombre] = auditoria_persona

    return {"pdf_principal": pdf_principal, "pdf_fiador": pdf_fiador}, auditoria


# ── Procesamiento en paralelo ─────────────────────────────────────────────────
def procesar_lote(
    personas: list[Persona],
    max_workers: int = 4,
) -> tuple[dict, dict, dict]:
    """
    Procesa una lista de Persona en paralelo usando ThreadPoolExecutor.

    Retorna:
        auditoria    — resultado por persona
        metricas     — estadísticas del lote completo
    """
    auditoria: dict = {}
    _lock = threading.Lock()

    tiempos_generacion: list[float] = []
    errores: list[str] = []

    t_total_inicio = time.perf_counter()

    def _procesar_uno(persona: Persona) -> None:
        try:
            _, aud, inst = generar_pdf(persona, {}, {})
            with _lock:
                auditoria.update(aud)
                t_gen = aud.get(persona.nombre, {}).get("tiempo_generacion")
                if t_gen is not None:
                    tiempos_generacion.append(t_gen)
        except Exception as exc:
            with _lock:
                errores.append(f"{persona.nombre}: {exc}")

    workers = min(max_workers, len(personas))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_procesar_uno, p): p for p in personas}
        for future in as_completed(futures):
            # as_completed ya captura; re-raise solo si _procesar_uno no lo hizo
            exc = future.exception()
            if exc:
                persona = futures[future]
                with _lock:
                    errores.append(f"{persona.nombre}: {exc}")

    t_total = time.perf_counter() - t_total_inicio

    metricas = {
        "workers_usados": workers,
        "registros_procesados": len(personas),
        "exitosos": len(personas) - len(errores),
        "errores": len(errores),
        "detalle_errores": errores,
        "Tiempo_promedio_generacion": (
            round(sum(tiempos_generacion) / len(tiempos_generacion), 4)
            if tiempos_generacion else 0.0
        ),
        "Tiempo_total_proceso": round(t_total, 4),
        "Tiempo_por_registro": round(t_total / len(personas), 4) if personas else 0.0,
    }

    print(f"metricas_proceso: {metricas}")
    return auditoria, metricas