import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_welcome_email(to_email: str, full_name: str):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials not found. Skipping welcome email.")
        return

    subject = "Welcome to CareerForge AI"
    body = f"""
Hello {full_name},

Thank you for choosing CareerForge AI.

Your account has been created successfully.

Best regards,
CareerForge AI Team
""".strip()

    _send_email(to_email, subject, body)


def send_resume_generated_email(to_email: str, full_name: str):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials not found. Skipping resume email.")
        return

    subject = "Your Resume is Ready - CareerForge AI"
    body = f"""
Hello {full_name},

Thank you for choosing CareerForge AI.

Your resume has been generated successfully and is ready.

We are happy to support you in building your professional career.

Best regards,
CareerForge AI Team
""".strip()

    _send_email(to_email, subject, body)


def _send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print("Failed to send email:", e)