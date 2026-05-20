from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(exist_ok=True)


def generar_auditoria(
    auditoria: dict,
) -> Path:

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archivo_auditoria = (
        OUTPUT_DIR
        / f"Auditoria_{fecha}.txt"
    )

    with open(
        archivo_auditoria,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "=" * 80 + "\n"
        )

        file.write(
            "AUDITORÍA PROCESO "
            "CUOTAS ATRASADAS\n"
        )

        file.write(
            f"Fecha generación: "
            f"{datetime.now()}\n"
        )

        file.write(
            "=" * 80 + "\n\n"
        )

        for nombre, datos in auditoria.items():

            file.write(
                f"Persona: {nombre}\n"
            )

            file.write(
                f"Estado: "
                f"{datos.get('estado')}\n"
            )

            file.write(
                f"Cuotas atrasadas: "
                f"{datos.get('cuotas_atrasadas')}\n"
            )

            file.write(
                f"Total pendiente: "
                f"{datos.get('total')}\n"
            )

            file.write(
                f"Fecha procesamiento: "
                f"{datos.get('fecha')}\n"
            )

            file.write(
                f"PDF principal generado: "
                "Se genero el documento" if datos.get("notificacion_generada") else "No se genero el documento\n"
            )

            file.write(
                f"PDF fiador generado: "
                "Se genero el documento" if datos.get("notificacion_fiador_generada") else "No se genero el documento\n"
            )

            file.write(
                f"Correo deudor enviado: "
                "Se envió el correo" if datos.get("correo_deudor_enviado") else "No se envió el correo\n"
            )

            file.write(
                f"Correo fiador enviado: "
                "Se envió el correo" if datos.get("correo_fiador_enviado") else "No se envió el correo\n"
            )

            file.write(
                f"Mensaje: "
                f"{datos.get('mensaje')}\n"
            )

            file.write(
                "-" * 80 + "\n"
            )

    print(
        f"Auditoría generada en: "
        f"{archivo_auditoria}"
    )

    return archivo_auditoria