import os
<<<<<<< HEAD
import re
=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from app.database.db import already_contacted, log_outreach
<<<<<<< HEAD
from app.personalization.validator import validate_messages


def send_or_simulate(creator: dict, campaign_id: str, subject: str, dry_run: bool = True) -> str:
    email = str(creator.get("contact_email", "Not Found")).strip()
    if email == "Not Found":
        log_outreach(campaign_id, creator, False, "Skipped - email not found")
        return "Skipped - email not found"
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        log_outreach(campaign_id, creator, False, "Skipped - invalid email")
        return "Skipped - invalid email"
=======


def send_or_simulate(creator: dict, campaign_id: str, subject: str, dry_run: bool = True) -> str:
    email = creator.get("contact_email", "Not Found")
    if email == "Not Found":
        log_outreach(campaign_id, creator, False, "Skipped - email not found")
        return "Skipped - email not found"
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
    if already_contacted(campaign_id, creator["channel_id"]):
        return "Skipped - duplicate prevented"
    if not creator.get("email_pitch"):
        log_outreach(campaign_id, creator, False, "Skipped - message missing")
        return "Skipped - message missing"
<<<<<<< HEAD
    message_errors = validate_messages(creator["email_pitch"], creator.get("instagram_dm", ""))
    if message_errors:
        status = "Skipped - invalid message"
        log_outreach(campaign_id, creator, False, status, error="; ".join(message_errors))
        return status
=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e

    if dry_run:
        log_outreach(campaign_id, creator, False, "Simulated - ready for review")
        return "Simulated - ready for review"

    host, port = os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587"))
    user, password = os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
    if not all([host, user, password]):
        raise RuntimeError("SMTP settings missing")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, email, subject
    msg.set_content(creator["email_pitch"])
    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls(); smtp.login(user, password); smtp.send_message(msg)
        now = datetime.now(timezone.utc).isoformat()
        log_outreach(campaign_id, creator, True, "Sent", sent_at=now)
        return "Sent"
    except Exception as exc:
        log_outreach(campaign_id, creator, False, "Failed", error=str(exc))
        return f"Failed: {exc}"
