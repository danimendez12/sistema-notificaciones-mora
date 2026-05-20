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


async def html_to_pdf(
    html_content: str,
    pdf_output: Path
):

    temp_html = pdf_output.with_suffix(".html")

    temp_html.write_text(
        html_content,
        encoding="utf-8"
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch()

        page = await browser.new_page()

        await page.goto(
            temp_html.as_uri(),
            wait_until="networkidle"
        )

        await page.pdf(
            path=str(pdf_output),
            format="A4",
            print_background=True
        )

        await browser.close()

    temp_html.unlink(missing_ok=True)


def generar_pdf(persona: Persona, auditoria: dict) -> tuple[dict[str, Path | None], dict]:

    auditoria_persona = {
        "fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "estado": persona.estado,
        "cuotas_atrasadas": int(
            persona.cuotas_atrasadas
        ),
        "total": persona.total,
        "notificacion_generada": False,
        "notificacion_fiador_generada": False,
        "correo_fiador": bool(
            persona.correo_fiador and (persona.correo_fiador != "")
        ),
        "mensaje": ""
    }
    templateFiador = None

    # Sanitizar nombre
    safe_name = re.sub(
        r'[\\/*?:"<>|]',
        "_",
        persona.nombre
    )

    # Selección plantilla principal
    if (
        persona.cuotas_atrasadas == 0
        and persona.estado == "NORMAL"
    ):

        template = env.get_template(
            "Plantilla-1-AlDia.html"
        )

    elif (
        1 <= persona.cuotas_atrasadas <= 3
        and persona.estado == "NORMAL"
    ):

        template = env.get_template(
            "Plantilla-2-CUotas-Atrasadas.html"
        )

    elif (
        persona.cuotas_atrasadas == 4
        and persona.estado == "NORMAL"
    ):

        template = env.get_template(
            "Plantilla-3-Aviso-Cobro.html"
        )

    elif (
        persona.cuotas_atrasadas >= 5
        and persona.estado == "NORMAL"
    ):

        template = env.get_template(
            "Plantilla-4-Cobro-Judicial.html"
        )

    else:

        

        auditoria_persona["mensaje"] = (
            f"Estado {persona.estado}"
        )

        auditoria[persona.nombre] = (
            auditoria_persona
        )
        return {
            "pdf_principal": None,
            "pdf_fiador": None
        }, auditoria

    # Determinar si lleva fiador
    tiene_fiador = (
        persona.fiador
        and persona.correo_fiador
    )

    if (
        persona.cuotas_atrasadas >= 1
        and tiene_fiador
    ):

        templateFiador = env.get_template(
            "Plantilla-5-Fiador.html"
        )

    elif persona.cuotas_atrasadas >= 1:

        

        auditoria_persona["mensaje"] = (
            "Sin información de fiador"
        )

    # Crear carpeta
    persona_dir = OUTPUT_DIR / safe_name

    persona_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    context = {
        "nombre": persona.nombre,
        "estado": persona.estado,
        "cuotas": int(persona.cuotas_atrasadas),
        "fecha_proximo_pago": persona.fecha_proximo_pago,
        "total": persona.total,
        "fiador": persona.fiador,
        "correo_fiador": persona.correo_fiador,
        "logo_path": logo_path
    }

    # Rutas PDF
    pdf_principal = (
        persona_dir
        / f"Notificacion-{safe_name}.pdf"
    )

    pdf_fiador = None

    async def generar_todos():

        nonlocal pdf_fiador

        # PDF principal
        html = template.render(**context)

        await html_to_pdf(
            html,
            pdf_principal
        )
        auditoria_persona[
            "notificacion_generada"
        ] = True

        # PDF fiador
        if templateFiador:

            html_fiador = templateFiador.render(
                **context
            )

            pdf_fiador = (
                persona_dir
                / f"Fiador-{safe_name}.pdf"
            )

            await html_to_pdf(
                html_fiador,
                pdf_fiador
            )

            auditoria_persona[
                "notificacion_fiador_generada"
            ] = True
    asyncio.run(generar_todos())

    if not auditoria_persona["mensaje"]:

        auditoria_persona["mensaje"] = (
            "Procesado correctamente"
        )

    auditoria[persona.nombre] = (
        auditoria_persona
    )

    return {
        "pdf_principal": pdf_principal,
        "pdf_fiador": pdf_fiador
    }, auditoria