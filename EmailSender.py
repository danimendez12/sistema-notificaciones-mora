from pathlib import Path
import win32com.client as win32

from Model import Persona


def _asunto_por_cuotas(cuotas: int) -> str:
    """Retorna el asunto del correo según las cuotas atrasadas."""
    if cuotas == 0:
        return "Notificacion de estado de cuenta - Al día Instituto Tecnológico de Costa Rica"
    if 1 <= cuotas <= 3:
        return "Notificacion de atraso - Pago Beca Prestamos - Instituto Tecnológico de Costa Rica"
    if cuotas == 4:
        return "Notificacion de Cobro Judicial - Pago Beca Prestamos - Instituto Tecnológico de Costa Rica"
    return "Notificacion de Traslado a Cobro Judicial - Pago Beca Prestamos - Instituto Tecnológico de Costa Rica"


def _seleccionar_cuenta_outlook(outlook, smtp_address: str):
    cuenta_envio = None
    for account in outlook.Session.Accounts:
        if getattr(account, "SmtpAddress", "").lower() == smtp_address.lower():
            cuenta_envio = account
            break

    if cuenta_envio is None:
        raise RuntimeError(
            f"La cuenta {smtp_address} no está configurada en Outlook."
        )

    return cuenta_envio


def enviar_correo(
    correo: str,
    asunto: str,
    cuerpo: str,
    adjunto: Path,
    cuenta_smtp: str = "tec@estudiantec.cr"
) -> bool:

    try:
        outlook = win32.Dispatch("outlook.application")
        mail = outlook.CreateItem(0)
        cuenta_envio = _seleccionar_cuenta_outlook(outlook, cuenta_smtp)
        mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta_envio))

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
                asunto_correo = _asunto_por_cuotas(int(persona.cuotas_atrasadas))
                enviado = enviar_correo(
                    correo=persona.email,
                    asunto=asunto_correo,
                    cuerpo=(
                        f"Estimado(a) {persona.nombre},\n\n"
                        "Adjunto encontrará la notificación correspondiente.\n\n"
                        "Departamento Financiero Contable\n"
                        "Instituto Tecnológico de Costa Rica"
                    ),
                    adjunto=resultado["pdf_principal"]
                )
                auditoria_envio["correo_deudor_enviado"] = enviado
                auditoria_envio["correo_deudor"] = persona.email
                auditoria_envio["asunto_deudor"] = asunto_correo
                if not enviado:
                    errores.append("No se pudo enviar el correo al deudor")
            else:
                errores.append("Correo del deudor no proporcionado")

        # =====================
        # Correo fiador
        # =====================
        if resultado.get("pdf_fiador"):
            if persona.correo_fiador:
                asunto_fiador = _asunto_por_cuotas(int(persona.cuotas_atrasadas))
                enviado_fiador = enviar_correo(
                    correo=persona.correo_fiador,
                    asunto=asunto_fiador,
                    cuerpo=(
                        f"Estimado(a) {persona.fiador},\n\n"
                        "Adjunto encontrará la notificación correspondiente.\n\n"
                        "Departamento Financiero Contable\n"
                        "Instituto Tecnológico de Costa Rica"
                    ),
                    adjunto=resultado["pdf_fiador"]
                )
                auditoria_envio["correo_fiador_enviado"] = enviado_fiador
                auditoria_envio["correo_fiador"] = persona.correo_fiador
                auditoria_envio["asunto_fiador"] = asunto_fiador
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