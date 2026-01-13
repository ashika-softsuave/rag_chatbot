import smtplib
from email.message import EmailMessage
from backend.app.core.config import get_settings

settings = get_settings()

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Verification Code"
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email

    msg.set_content(f"""
Hello,

Your OTP for account verification is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.
""")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)
