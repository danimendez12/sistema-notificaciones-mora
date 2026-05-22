from pathlib import Path
import asyncio
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from Model import Persona


BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "Templates"
OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)

logo_path = (
    TEMPLATES_DIR
    / "assets"
    / "ENcabezado-Tesoreria.png"
).as_uri()

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)


async def _generar_todos(
    template,
    templateFiador,
    context: dict,
    pdf_principal: Path,
    pdf_fiador_path: Path | None,
    auditoria_persona: dict,
    instrucciones_persona: dict,
):
    html = template.render(**context)
    await html_to_pdf(html, pdf_principal)
    auditoria_persona["notificacion_generada"] = True
    instrucciones_persona["pdf_principal"] = str(
        pdf_principal.relative_to(OUTPUT_DIR)
    )

    if templateFiador and pdf_fiador_path:
        html_fiador = templateFiador.render(**context)
        await html_to_pdf(html_fiador, pdf_fiador_path)
        auditoria_persona["notificacion_fiador_generada"] = True
        instrucciones_persona["pdf_fiador"] = str(
            pdf_fiador_path.relative_to(OUTPUT_DIR)
        )


async def html_to_pdf(html_content: str, pdf_output: Path) -> None:
    temp_html = pdf_output.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(temp_html.as_uri(), wait_until="networkidle")
            await page.pdf(path=str(pdf_output), format="A4", print_background=True)
        finally:
            await browser.close()
            temp_html.unlink(missing_ok=True)  # siempre limpia


def generar_pdf(
    persona: Persona,
    auditoria: dict,
    instrucciones: dict,
) -> tuple[dict[str, Path | None], dict, dict]:  # siempre 3 elementos

    auditoria_persona = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": persona.estado,
        "cuotas_atrasadas": int(persona.cuotas_atrasadas),
        "total": persona.total,
        "notificacion_generada": False,
        "notificacion_fiador_generada": False,
        "correo_fiador": bool(persona.correo_fiador),
        "mensaje": "",
    }

    instrucciones_persona = {
        "nombre": persona.nombre,
        "estado": persona.estado,
        "correo_deudor": persona.email,
        "pdf_principal": None,
        "correo_fiador": persona.correo_fiador,
        "pdf_fiador": None,
        "incluir_fiador": False,
    }

    def _registrar_y_retornar(mensaje: str) -> tuple[dict[str, Path | None], dict, dict]:
        auditoria_persona["mensaje"] = mensaje
        auditoria_persona["mensaje"] = mensaje
        auditoria[persona.nombre] = auditoria_persona
        instrucciones[persona.nombre] = instrucciones_persona
        return {"pdf_principal": None, "pdf_fiador": None}, auditoria, instrucciones

    # ── Selección de plantilla ────────────────────────────────────────────────
    cuotas = int(persona.cuotas_atrasadas)
    estado = persona.estado

    MAPA_PLANTILLAS = {
        (0, "NORMAL"): "Plantilla-1-AlDia.html",
    }

    if estado != "NORMAL":
        return _registrar_y_retornar(f"Estado no reconocido: {estado}")

    if cuotas == 0:
        nombre_template = "Plantilla-1-AlDia.html"
    elif 1 <= cuotas <= 3:
        nombre_template = "Plantilla-2-CUotas-Atrasadas.html"
    elif cuotas == 4:
        nombre_template = "Plantilla-3-Aviso-Cobro.html"
    else:
        nombre_template = "Plantilla-4-Cobro-Judicial.html"

    template = env.get_template(nombre_template)

    # ── Fiador ────────────────────────────────────────────────────────────────
    templateFiador = None
    tiene_fiador = bool(persona.fiador and persona.correo_fiador)

    if cuotas >= 1 and tiene_fiador:
        templateFiador = env.get_template("Plantilla-5-Fiador.html")
        instrucciones_persona["incluir_fiador"] = True
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
        "total": persona.total,
        "fiador": persona.fiador,
        "correo_fiador": persona.correo_fiador,
        "logo_path": logo_path,
    }

    asyncio.run(
        _generar_todos(
            template,
            templateFiador,
            context,
            pdf_principal,
            pdf_fiador,
            auditoria_persona,
            instrucciones_persona,
        )
    )

    if not auditoria_persona["mensaje"]:
        auditoria_persona["mensaje"] = "Procesado correctamente"

    auditoria[persona.nombre] = auditoria_persona
    instrucciones[persona.nombre] = instrucciones_persona

    return {"pdf_principal": pdf_principal, "pdf_fiador": pdf_fiador}, auditoria, instrucciones