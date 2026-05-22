from pathlib import Path
import win32com.client as win32

from Model import Persona


def enviar_correo(
    correo: str,
    asunto: str,
    cuerpo: str,
    adjunto: Path
) -> bool:

    try:

        outlook = win32.Dispatch(
            "outlook.application"
        )

        mail = outlook.CreateItem(0)

        mail.To = correo
        mail.Subject = asunto
        mail.Body = cuerpo

        mail.Attachments.Add(
            str(adjunto)
        )

        mail.Send() #Para enviar cambiar a .Send()

        print(
            f"Correo enviado a {correo}"
        )

        return True

    except Exception as e:

        print(
            f"Error enviando correo a "
            f"{correo}: {e}"
        )

        return False


def enviar_correos(
    persona: Persona,
    resultado: dict,
    auditoria: dict
) -> dict:

    auditoria_envio = {
        "correo_deudor_enviado": False,
        "correo_fiador_enviado": False,
        "error_envio": ""
    }

    try:

        # =====================
        # Correo principal
        # =====================

        if (
            resultado["pdf_principal"]
            
        ):
            if (persona.email):

                enviado = enviar_correo(
                    correo=persona.email,

                    asunto=(
                        "Notificación "
                        "Departamento Financiero"
                    ),

                    cuerpo=(
                        f"Estimado(a) "
                        f"{persona.nombre},\n\n"
                        "Adjunto encontrará "
                        "la notificación "
                        "correspondiente.\n\n"
                        "Departamento Financiero "
                        "Contable\n"
                        "Instituto Tecnológico "
                        "de Costa Rica"
                    ),

                    adjunto=resultado[
                        "pdf_principal"
                    ]
                )

                auditoria_envio[
                    "correo_deudor_enviado"
                ] = enviado
            else:   
                    auditoria_envio[
                        "error_envio"
                    ] = "Correo del deudor no proporcionado"


        # =====================
        # Correo fiador
        # =====================

        if (
            resultado["pdf_fiador"]
        ):
            if (persona.correo_fiador):
                enviado_fiador = enviar_correo(
                    correo=persona.correo_fiador,

                    asunto=(
                        "Notificación "
                        "Persona Fiadora"
                    ),

                    cuerpo=(
                        f"Estimado(a) "
                        f"{persona.fiador},\n\n"
                        "Adjunto encontrará "
                        "la notificación "
                        "correspondiente.\n\n"
                        "Departamento Financiero "
                        "Contable\n"
                        "Instituto Tecnológico "
                        "de Costa Rica"
                    ),

                    adjunto=resultado[
                        "pdf_fiador"
                    ]
                )

                auditoria_envio[
                    "correo_fiador_enviado"
                ] = enviado_fiador
            else:
                auditoria_envio[
                    "error_envio"
                ] = "Correo del fiador no proporcionado"

    except Exception as e:

        auditoria_envio[
            "error_envio"
        ] = str(e)

    auditoria[
        persona.nombre
    ].update(auditoria_envio)

    return auditoria