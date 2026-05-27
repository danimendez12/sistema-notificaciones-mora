from pathlib import Path
from datetime import datetime

from openpyxl import Workbook


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)





def generar_monitoreo(
    logs: dict,
) -> Path:

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archivo_monitoreo = (
        OUTPUT_DIR
        / f"Monitoreo.txt"
    )


    with open(archivo_monitoreo, "w") as f:
        for nombre, datos in logs.items():
            f.write(f"{nombre}: {datos}\n")

    return archivo_monitoreo