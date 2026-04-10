import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv 


load_dotenv()

def send_email_digest(content: str):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")

    msg = MIMEText(content)
    msg["Subject"] = "Daily News Intelligence Brief"
    msg["From"] = sender_email
    msg["To"] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)