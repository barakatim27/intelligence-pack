import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr
import ssl
import os
from dotenv import load_dotenv


load_dotenv()


class EmailDeliveryError(Exception):
    """Raised when email delivery fails."""


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _validate_email(address: str, field_name: str) -> str:
    _, parsed = parseaddr(address)
    if "@" not in parsed:
        raise ValueError(f"Invalid email address in {field_name}: {address!r}")
    return parsed


def send_email_digest(content: str) -> None:
    if not content or not content.strip():
        raise ValueError("Digest content must not be empty.")

    sender_email = _validate_email(_require_env("SENDER_EMAIL"), "SENDER_EMAIL")
    sender_password = _require_env("SENDER_PASSWORD")
    recipient = _validate_email(_require_env("RECIPIENT_EMAIL"), "RECIPIENT_EMAIL")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    msg = MIMEText(content, _subtype="plain", _charset="utf-8")
    msg["Subject"] = "Daily News Intelligence Brief"
    msg["From"] = sender_email
    msg["To"] = recipient

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailDeliveryError("Failed to send digest email.") from exc
