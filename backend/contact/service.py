from core.database import messages_collection
from core.config import settings
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class ContactService:

    @staticmethod
    def save_message(email: str, message: str):
        doc = {
            "email": email,
            "message": message,
            "timestamp": datetime.now(ZoneInfo("UTC"))
        }
        return messages_collection.insert_one(doc)

    @staticmethod
    def send_email(email: str, message: str):
        if not settings.OUTLOOK_USER:
            return

        msg = MIMEMultipart()
        msg["From"] = settings.OUTLOOK_USER
        msg["To"] = settings.OUTLOOK_USER
        msg["Subject"] = "New Contact Form Submission"

        msg.attach(MIMEText(f"From: {email}\n\n{message}", "plain"))

        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        server.starttls()
        server.login(settings.OUTLOOK_USER, settings.OUTLOOK_PASSWORD)
        server.sendmail(settings.OUTLOOK_USER, settings.OUTLOOK_USER, msg.as_string())
        server.quit()
