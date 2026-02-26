# backend/app/services/emailer.py
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, text: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(text)

    host = settings.SMTP_HOST
    port = settings.SMTP_PORT

    context = ssl.create_default_context()

    # ВАЖНО: создаём SMTP сразу с host/port, тогда smtplib нормально знает server_hostname
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        # можно временно для отладки:
        # smtp.set_debuglevel(1)

        smtp.ehlo()
        smtp.starttls(context=context)   # <-- фикс
        smtp.ehlo()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)

def send_login_code(to_email: str, code: str) -> None:
    subject = "Код входа в Navio Learn"
    text = f"Ваш код входа:\n\n{code}\n\nЕсли вы не запрашивали код — игнорируйте письмо."
    try:
        send_email(to_email, subject, text)
    except Exception:
        logger.exception("Failed to send login code to %s", to_email)