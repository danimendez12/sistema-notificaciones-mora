from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Resultados"

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

            if isinstance(datos, dict):
                estado = datos.get('estado')
                cuotas = datos.get('cuotas_atrasadas')
                total = datos.get('total')
                fecha_proc = datos.get('fecha')
            else:
                estado = None
                cuotas = None
                total = None
                fecha_proc = None

            file.write(
                f"Estado: {estado}\n"
            )

            file.write(
                f"Cuotas atrasadas: {cuotas}\n"
            )

            file.write(
                f"Total pendiente: {total}\n"
            )

            file.write(
                f"Fecha procesamiento: {fecha_proc}\n"
            )

            if isinstance(datos, dict):
                file.write(
                    f"PDF principal generado: {'Se generó el documento' if datos.get('notificacion_generada') else 'No se generó el documento'}\n"
                )
                file.write(
                    f"PDF fiador generado: {'Se generó el documento' if datos.get('notificacion_fiador_generada') else 'No se generó el documento'}\n"
                )
                file.write(
                    f"Correo deudor enviado: {'Se envió el correo' if datos.get('correo_deudor_enviado') else 'No se envió el correo'}\n"
                )
                file.write(
                    f"Correo deudor: {datos.get('correo_deudor')}\n"
                )
                file.write(
                    f"Correo fiador enviado: {'Se envió el correo' if datos.get('correo_fiador_enviado') else 'No se envió el correo'}\n"
                )
                file.write(
                    f"Correo fiador: {datos.get('correo_fiador')}\n"
                )
                file.write(
                    f"Mensaje: {datos.get('mensaje')}\n"
                )
                if datos.get('error_envio'):
                    file.write(
                        f"Error envío: {datos.get('error_envio')}\n"
                    )
            else:
                file.write(
                    f"Mensaje: {datos}\n"
                )

            file.write(
                "-" * 80 + "\n"
            )

    print(
        f"Auditoría generada en: "
        f"{archivo_auditoria}"
    )

    return archivo_auditoria


def generar_auditoria_errores(
    auditoria: dict,
) -> Path | None:
    """
    Genera un archivo de auditoría que contiene solo los registros con errores.
    Retorna None si no hay errores.
    """
    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archivo_auditoria_errores = (
        OUTPUT_DIR
        / f"Auditoria_ERRORES_{fecha}.txt"
    )

    # Filtrar solo registros con error
    registros_con_error = {}
    for nombre, datos in auditoria.items():
        if isinstance(datos, dict):
            tiene_error = (
                not datos.get('correo_deudor_enviado') or
                not datos.get('notificacion_generada') or
                datos.get('error_envio') or
                not datos.get('correo_deudor') or  # Sin correo deudor
                not datos.get('correo_fiador')      # Sin información de fiador
            )
            if tiene_error:
                registros_con_error[nombre] = datos

    # Si no hay errores, no generar archivo
    if not registros_con_error:
        print(
            "✅ No se encontraron errores en la auditoría"
        )
        return None

    with open(
        archivo_auditoria_errores,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "=" * 80 + "\n"
        )

        file.write(
            "AUDITORÍA ERRORES - "
            "CUOTAS ATRASADAS\n"
        )

        file.write(
            f"Fecha generación: "
            f"{datetime.now()}\n"
        )

        file.write(
            f"Total registros con error: "
            f"{len(registros_con_error)}\n"
        )

        file.write(
            "=" * 80 + "\n\n"
        )

        for nombre, datos in registros_con_error.items():

            file.write(
                f"Persona: {nombre}\n"
            )

            if isinstance(datos, dict):
                estado = datos.get('estado')
                cuotas = datos.get('cuotas_atrasadas')
                total = datos.get('total')
                fecha_proc = datos.get('fecha')
            else:
                estado = None
                cuotas = None
                total = None
                fecha_proc = None

            file.write(
                f"Estado: {estado}\n"
            )

            file.write(
                f"Cuotas atrasadas: {cuotas}\n"
            )

            file.write(
                f"Total pendiente: {total}\n"
            )

            file.write(
                f"Fecha procesamiento: {fecha_proc}\n"
            )

            if isinstance(datos, dict):
                pdf_generado = datos.get('notificacion_generada')
                correo_enviado = datos.get('correo_deudor_enviado')
                correo_deudor = datos.get('correo_deudor')
                correo_fiador = datos.get('correo_fiador')
                
                file.write(
                    f"PDF generado: {'✅ Sí' if pdf_generado else '❌ No'}\n"
                )

                file.write(
                    f"Correo deudor disponible: {'✅ Sí' if correo_deudor else '❌ No'}\n"
                )

                if correo_deudor:
                    file.write(
                        f"Correo deudor: {correo_deudor}\n"
                    )
                    file.write(
                        f"Correo deudor enviado: {'✅ Sí' if correo_enviado else '❌ No'}\n"
                    )

                file.write(
                    f"Información fiador disponible: {'✅ Sí' if correo_fiador else '❌ No'}\n"
                )

                if correo_fiador:
                    file.write(
                        f"Correo fiador: {correo_fiador}\n"
                    )

                if datos.get('error_envio'):
                    file.write(
                        f"Error: {datos.get('error_envio')}\n"
                    )

                if datos.get('mensaje'):
                    file.write(
                        f"Mensaje: {datos.get('mensaje')}\n"
                    )
            else:
                file.write(
                    f"Mensaje: {datos}\n"
                )

            file.write(
                "-" * 80 + "\n"
            )

    print(
        f"Auditoría de errores generada en: "
        f"{archivo_auditoria_errores}"
    )

    return archivo_auditoria_errores