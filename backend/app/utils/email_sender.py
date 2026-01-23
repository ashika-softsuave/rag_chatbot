import smtplib
from email.message import EmailMessage
from backend.app.core.config import get_settings
import os

settings = get_settings()

def send_email_with_pdf(
    to_email: str,
    subject: str,
    body: str,
    pdf_path: str
):
    msg = EmailMessage()
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach PDF
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    pdf_name = os.path.basename(pdf_path)
    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=pdf_name
    )

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
