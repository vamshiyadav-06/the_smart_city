"""Email notification service."""

import logging
import smtplib
from email.mime.text import MIMEText
from threading import Thread

from backend.config import settings

logger = logging.getLogger(__name__)


def maybe_send_email(alert_type: str, description: str, severity: str = "High"):
    if not (settings.alert_email_to and settings.smtp_host):
        return
    Thread(target=_send_email_sync, args=(alert_type, description, severity), daemon=True).start()


def _send_email_sync(alert_type: str, description: str, severity: str):
    try:
        message = MIMEText(
            f"Smart City India Alert\n\nType: {alert_type}\n"
            f"Severity: {severity}\n\n{description}"
        )
        message["Subject"] = f"[{severity}] Smart City India: {alert_type}"
        message["From"] = settings.smtp_user
        message["To"] = settings.alert_email_to

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    except Exception as e:
        logger.warning("Email alert failed: %s", e)
