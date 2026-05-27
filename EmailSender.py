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
        outlook = win32.Dispatch("outlook.application")
        mail = outlook.CreateItem(0)

        mail.To = correo
        mail.Subject = asunto
        mail.Body = cuerpo

        mail.Attachments.Add(str(adjunto))
        mail.Send()

        print(f"✅ Correo enviado a {correo} (Asunto: {asunto})")
        return True

    except Exception as e:
        print(f"❌ Error enviando correo a {correo} (Asunto: {asunto}): {e}")
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
        errores = []

        # =====================
        # Correo principal
        # =====================
        if resultado.get("pdf_principal"):
            if persona.email:
                enviado = enviar_correo(
                    correo=persona.email,
                    asunto=(
                        "Notificación "
                        "Departamento Financiero"
                    ),
                    cuerpo=(
                        f"Estimado(a) {persona.nombre},\n\n"
                        "Adjunto encontrará la notificación correspondiente.\n\n"
                        "Departamento Financiero Contable\n"
                        "Instituto Tecnológico de Costa Rica"
                    ),
                    adjunto=resultado["pdf_principal"]
                )
                auditoria_envio["correo_deudor_enviado"] = enviado
                if not enviado:
                    errores.append("No se pudo enviar el correo al deudor")
            else:
                errores.append("Correo del deudor no proporcionado")

        # =====================
        # Correo fiador
        # =====================
        if resultado.get("pdf_fiador"):
            if persona.correo_fiador:
                enviado_fiador = enviar_correo(
                    correo=persona.correo_fiador,
                    asunto=(
                        "Notificación "
                        "Persona Fiadora"
                    ),
                    cuerpo=(
                        f"Estimado(a) {persona.fiador},\n\n"
                        "Adjunto encontrará la notificación correspondiente.\n\n"
                        "Departamento Financiero Contable\n"
                        "Instituto Tecnológico de Costa Rica"
                    ),
                    adjunto=resultado["pdf_fiador"]
                )
                auditoria_envio["correo_fiador_enviado"] = enviado_fiador
                if not enviado_fiador:
                    errores.append("No se pudo enviar el correo al fiador")
            else:
                errores.append("Correo del fiador no proporcionado")

        if errores:
            auditoria_envio["error_envio"] = "; ".join(errores)

    except Exception as e:
        auditoria_envio["error_envio"] = str(e)
    auditoria[
        persona.nombre
    ].update(auditoria_envio)

    return auditoria