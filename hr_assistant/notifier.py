"""
HR Assistant - Notifier
=======================
Actually SENDS the email / WhatsApp message, instead of just simulating it
in the chat reply.

- Email is sent via Gmail SMTP (works with any Gmail account + an "App
  Password" — no paid service needed).
- WhatsApp is sent via Twilio's WhatsApp API (needs a free Twilio account;
  the sandbox number works for testing without any approval process).

All credentials are read from environment variables (via a local .env file,
never hardcoded, never committed). If credentials are missing, both
functions fail gracefully and tell you exactly what's missing instead of
crashing the app.
"""

import os
import re
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()  # reads a .env file in the project root, if present

# =====================================================
# EMAIL (Gmail SMTP)
# =====================================================

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_real_email(to_address, subject, body):
    """Returns (success: bool, message: str)."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return False, (
            "Email not sent — GMAIL_ADDRESS / GMAIL_APP_PASSWORD are not set "
            "in your .env file. See hr_assistant/EMAIL_WHATSAPP_SETUP.md."
        )

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, [to_address], msg.as_string())

        return True, f"Email sent to {to_address}"
    except Exception as e:
        return False, f"Email failed to send: {e}"


# =====================================================
# WHATSAPP (Twilio)
# =====================================================

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")


def _format_whatsapp_number(raw_number):
    """Turns a 10-digit Indian number into Twilio's required whatsapp:+91XXXXXXXXXX format."""
    digits = re.sub(r"\D", "", raw_number)
    if len(digits) == 10:
        digits = "91" + digits  # assume India if no country code given
    return f"whatsapp:+{digits}"


def send_real_whatsapp(to_number, body):
    """Returns (success: bool, message: str)."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return False, (
            "WhatsApp message not sent — TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN "
            "are not set in your .env file. See hr_assistant/EMAIL_WHATSAPP_SETUP.md."
        )

    try:
        from twilio.rest import Client  # imported lazily so the app still runs without twilio installed

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        to_whatsapp = _format_whatsapp_number(to_number)

        message = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=body,
            to=to_whatsapp,
        )
        return True, f"WhatsApp message sent to {to_whatsapp} (sid={message.sid})"
    except Exception as e:
        return False, f"WhatsApp message failed to send: {e}"
