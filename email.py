import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.config import settings


# =====================================================
# SEND GENERIC EMAIL
# =====================================================

async def send_email(
    to_email: List[str],
    subject: str,
    body: str,
    html: bool = True
):
    """Send email using SMTP"""

    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_FROM
        message["To"] = ", ".join(to_email)
        message["Subject"] = subject

        # Attach body
        if html:
            message.attach(MIMEText(body, "html"))
        else:
            message.attach(MIMEText(body, "plain"))

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# =====================================================
# CONTACT FORM EMAIL
# =====================================================

async def send_contact_notification(name: str, email: str, subject: str, message: str):
    """Send notification email when contact form is submitted"""

    email_body = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:8px;">
            <h2 style="color:#3b82f6;">New Contact Form Submission</h2>

            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Subject:</b> {subject}</p>
            <p><b>Message:</b></p>

            <p>{message}</p>

            <hr>

            <p style="font-size:12px;color:gray;">
            Sent from your Portfolio Website
            </p>
        </div>
    </body>
    </html>
    """

    return await send_email(
        to_email=[settings.ADMIN_EMAIL],
        subject=f"Portfolio Contact: {subject}",
        body=email_body,
        html=True
    )


# =====================================================
# WELCOME EMAIL
# =====================================================

async def send_welcome_email(to_email: str, name: str):
    """Send welcome email to new user"""

    email_body = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:8px;">

            <h1 style="color:#3b82f6;">Welcome {name} 👋</h1>

            <p>
            Thank you for registering on our portfolio platform.
            Your account has been created successfully.
            </p>

            <p>
            You can now explore projects and connect with us.
            </p>

            <hr>

            <p style="font-size:12px;color:gray;">
            © 2026 Portfolio Backend API
            </p>

        </div>
    </body>
    </html>
    """

    return await send_email(
        to_email=[to_email],
        subject="Welcome to Portfolio Platform",
        body=email_body,
        html=True
    )