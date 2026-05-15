"""
Generador de certificados PDF usando Jinja2 + WeasyPrint.
Uso:
    python generar_certificado.py --nombre "Daniel Méndez" --salida salida.pdf
    python generar_certificado.py --datos datos.json        # generación en lote
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# ── WeasyPrint (falla temprano con mensaje claro) ──────────────────────────────
try:
    from weasyprint import HTML as WeasyprintHTML
    from weasyprint.logger import PROGRESS_LOGGER
except ImportError as exc:
    sys.exit(
        "WeasyPrint no está instalado o faltan dependencias nativas.\n"
        "Guía de instalación: "
        "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation\n"
        f"Detalle: {exc}"
    )

# ── Rutas base ─────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "Templates"
OUTPUT_DIR    = BASE_DIR / "output"
TEMPLATE_NAME = "Plantilla-1-AlDia.html"

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
PROGRESS_LOGGER.setLevel(logging.WARNING)   # silencia el verbose de WeasyPrint


# ── Jinja2 ─────────────────────────────────────────────────────────────────────
def _build_env() -> Environment:
    if not TEMPLATES_DIR.is_dir():
        sys.exit(f"Carpeta de templates no encontrada: {TEMPLATES_DIR}")
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )


def render_template(env: Environment, context: dict[str, Any]) -> str:
    """Renderiza el template con el contexto dado."""
    try:
        template = env.get_template(TEMPLATE_NAME)
    except TemplateNotFound:
        sys.exit(f"Template no encontrado: {TEMPLATES_DIR / TEMPLATE_NAME}")
    return template.render(**context)


# ── PDF ────────────────────────────────────────────────────────────────────────
def html_to_pdf(html: str, dest: Path) -> None:
    from playwright.sync_api import sync_playwright

    dest.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, base_url=TEMPLATES_DIR.as_uri())
        page.pdf(
            path=str(dest),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    log.info("PDF generado → %s", dest)

# ── Generación individual ──────────────────────────────────────────────────────
def generar_uno(env: Environment, context: dict[str, Any], salida: Path) -> None:
    html = render_template(env, context)
    html_to_pdf(html, salida)


# ── Generación en lote ─────────────────────────────────────────────────────────
def generar_lote(env: Environment, datos_path: Path) -> None:
    """
    Lee un JSON con lista de registros, p.ej.:
        [
          {"nombre": "Ana López",    "salida": "ana_lopez.pdf"},
          {"nombre": "Luis Pérez",   "salida": "luis_perez.pdf"}
        ]
    Si "salida" no está presente, deriva el nombre del campo "nombre".
    """
    registros: list[dict] = json.loads(datos_path.read_text(encoding="utf-8"))
    log.info("Procesando %d registros…", len(registros))

    errores: list[str] = []
    for i, rec in enumerate(registros, 1):
        nombre_archivo = rec.pop("salida", None) or _nombre_seguro(rec.get("nombre", f"registro_{i}"))
        dest = OUTPUT_DIR / nombre_archivo
        try:
            generar_uno(env, rec, dest)
        except Exception as exc:          # noqa: BLE001
            log.error("Error en registro %d (%s): %s", i, dest.name, exc)
            errores.append(dest.name)

    if errores:
        log.warning("Fallaron %d archivos: %s", len(errores), errores)
    else:
        log.info("Lote completado sin errores.")


def _nombre_seguro(texto: str) -> str:
    """Convierte un nombre a un nombre de archivo seguro."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in texto).strip("_") + ".pdf"


# ── CLI ────────────────────────────────────────────────────────────────────────
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera certificados PDF desde una plantilla HTML.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--nombre", help="Nombre del estudiante (generación individual)")
    group.add_argument("--datos",  help="Ruta a JSON para generación en lote")

    parser.add_argument(
        "--salida",
        default=None,
        help="Nombre del PDF de salida (solo con --nombre). Default: output/<nombre>.pdf",
    )
    return parser.parse_args()


def main() -> None:
    args   = _parse_args()
    env    = _build_env()

    if args.nombre:
        dest = OUTPUT_DIR / (args.salida or _nombre_seguro(args.nombre))
        generar_uno(env, {"nombre": args.nombre}, dest)
    else:
        datos_path = Path(args.datos)
        if not datos_path.is_file():
            sys.exit(f"Archivo de datos no encontrado: {datos_path}")
        generar_lote(env, datos_path)


if __name__ == "__main__":
    main()