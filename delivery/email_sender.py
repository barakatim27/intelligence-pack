import smtplib
from email.mime.text import MIMEText
import env 


def send_email_digest(content: str):
    sender_email = env.get("SENDER_EMAIL")
    sender_password = env.get("SENDER_PASSWORD")
    recipient = env.get("RECIPIENT_EMAIL")

    msg = MIMEText(content)
    msg["Subject"] = "Daily News Intelligence Brief"
    msg["From"] = sender_email
    msg["To"] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)