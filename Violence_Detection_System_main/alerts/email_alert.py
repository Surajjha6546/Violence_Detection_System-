import smtplib
from email.message import EmailMessage
from datetime import datetime


def send_email_alert(
    to_email: str,
    severity: str,
    confidence: float,
    source: str
) -> bool:
    """
    Sends a one-time email alert when violence is detected.
    """

    EMAIL_ADDRESS = "gj565767@gmail.com"
    EMAIL_APP_PASSWORD = "baobhzxyzptzhwau"

    msg = EmailMessage()
    msg["Subject"] = "🚨 VIOLENCE DETECTED - CCTV ALERT"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(f"""
AI VIOLENCE DETECTION ALERT

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: {source}

Severity: {severity}
Confidence: {confidence:.2f}

Please review the incident immediately.

— AI Surveillance System
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True

    except Exception as e:
        print("Email error:", e)
        return False
