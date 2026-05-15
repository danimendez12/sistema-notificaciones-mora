from pathlib import Path
import asyncio

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

from Model import Persona


BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "Templates"
OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)
# Ruta absoluta de la imagen
logo_path = (
    TEMPLATES_DIR
    / "assets"
    / "ENcabezado-Tesoreria.png"
).as_uri()


env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)
def generar_pdf(persona: Persona) -> None:

    if (persona.coutoas_atrasadas  ==1) and (persona.rango_mora == "Cancelada"):
        template = env.get_template("Plantilla-1-AlDia.html")
    elif (persona.coutoas_atrasadas  >=1) and (persona.rango_mora == "normal"):
        template = env.get_template("Plantilla-2-CUotas-Atrasadas.html")
    elif (persona.coutoas_atrasadas  ==4  ):
        template = env.get_template("Plantilla-3-Aviso-Cobro.html")
    elif (persona.coutoas_atrasadas  >=5  ):
        template = env.get_template("Plantilla-4-Cobro-Judicial.html")

    html = template.render(
        nombre=persona.nombre,
        email=persona.email,
        estado=persona.estado,
        coutoas_atrasadas=persona.coutoas_atrasadas,
        fecha_proximo_pago=persona.fecha_proximo_pago,
        rango_mora=persona.rango_mora,
        correo_fiador=persona.correo_fiador,
        logo_path=logo_path
    )

    temp_html_path = OUTPUT_DIR / "temp.html"

    temp_html_path.write_text(
        html,
        encoding="utf-8"
    )


    async def html_to_pdf(html_file: Path, pdf_output: Path):

        async with async_playwright() as p:

            browser = await p.chromium.launch()

            page = await browser.new_page()

            await page.goto(
                html_file.as_uri(),
                wait_until="networkidle"
            )

            await page.pdf(
                path=str(pdf_output),
                format="A4",
                print_background=True
            )

            await browser.close()


    pdf_path = OUTPUT_DIR / f"Notificacion-{persona.nombre}.pdf"

    asyncio.run(
        html_to_pdf(
            temp_html_path,
            pdf_path
        )
)