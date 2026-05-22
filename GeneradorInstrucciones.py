from pathlib import Path
from datetime import datetime

from openpyxl import Workbook


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)





def generar_instrucciones(
    instrucciones: dict,
) -> Path:

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archivo_instrucciones = (
        OUTPUT_DIR
        / f"Instrucciones.xlsx"
    )

    wb = Workbook()

    ws = wb.active
    ws.title = "Envios"

    # Encabezados
    ws.append([
        "Nombre",
        "CorreoDeudor",
        "PDFDeudor",
        "CorreoFiador",
        "PDFFiador"
    ])

    # Datos
    for nombre, datos in instrucciones.items():

        ws.append([
            nombre,
            datos.get("correo_deudor"),
            datos.get("pdf_principal"),
            datos.get("correo_fiador"),
            datos.get("pdf_fiador")
        ])

    wb.save(archivo_instrucciones)

    return archivo_instrucciones