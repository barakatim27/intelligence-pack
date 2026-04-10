import smtplib
from email.mime.text import MIMEText


def send_email_digest(content: str):
    sender_email = "YOUR_EMAIL@gmail.com"
    sender_password = "YOUR_APP_PASSWORD"
    recipient = "timothybaraka39@gmail.com"

    msg = MIMEText(content)
    msg["Subject"] = "Daily News Intelligence Brief"
    msg["From"] = sender_email
    msg["To"] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)