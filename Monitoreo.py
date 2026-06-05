from pathlib import Path
from datetime import datetime
import json


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)





def generar_monitoreo(
    logs: dict,
) -> Path:

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archivo_monitoreo = OUTPUT_DIR / f"Monitoreo_{fecha}.json"


    with open(archivo_monitoreo, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generado_el": datetime.now().isoformat(),
                "monitoreo": logs,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return archivo_monitoreo