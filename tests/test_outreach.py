import csv
import tempfile
from unittest.mock import patch
from pathlib import Path

from app.database import db
from app.database import export_outreach
from app.outreach.email_sender import send_or_simulate


def valid_email():
    return " ".join(["message"] * 60)


def valid_dm():
    return " ".join(["message"] * 15)


def test_sender_rejects_invalid_messages():
    creator = {
        "channel_id": "channel-1",
        "contact_email": "creator@example.com",
        "email_pitch": "Too short",
        "instagram_dm": "Too short",
    }
    with patch("app.outreach.email_sender.already_contacted", return_value=False), patch(
        "app.outreach.email_sender.log_outreach"
    ) as log_outreach:
        result = send_or_simulate(creator, "campaign-1", "Subject")

    assert result == "Skipped - invalid message"
    log_outreach.assert_called_once()


def test_sender_simulates_valid_message():
    creator = {
        "channel_id": "channel-1",
        "contact_email": "creator@example.com",
        "email_pitch": valid_email(),
        "instagram_dm": valid_dm(),
    }
    with patch("app.outreach.email_sender.already_contacted", return_value=False), patch(
        "app.outreach.email_sender.log_outreach"
    ) as log_outreach:
        result = send_or_simulate(creator, "campaign-1", "Subject")

    assert result == "Simulated - ready for review"
    log_outreach.assert_called_once()


def test_sender_skips_duplicate_outreach():
    creator = {
        "channel_id": "channel-1",
        "contact_email": "creator@example.com",
        "email_pitch": valid_email(),
        "instagram_dm": valid_dm(),
    }
    with patch("app.outreach.email_sender.already_contacted", return_value=True), patch(
        "app.outreach.email_sender.log_outreach"
    ) as log_outreach:
        result = send_or_simulate(creator, "campaign-1", "Subject")

    assert result == "Skipped - duplicate prevented"
    log_outreach.assert_not_called()


def test_simulated_outreach_is_counted_as_contacted():
    with tempfile.TemporaryDirectory() as directory:
        with patch.object(db, "DB_PATH", Path(directory) / "outreach.db"):
            creator = {
                "channel_id": "channel-1",
                "channel_name": "AI Builder",
                "contact_email": "creator@example.com",
                "email_pitch": valid_email(),
                "instagram_dm": valid_dm(),
            }
            db.log_outreach("campaign-1", creator, False, "Simulated - ready for review")

            assert db.already_contacted("campaign-1", "channel-1")


def test_tracker_export_includes_outreach_log():
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "outreach.db"
        tracker = Path(directory) / "outreach_tracker.csv"
        with patch.object(db, "DB_PATH", database), patch.object(export_outreach, "OUTPUT_PATH", str(tracker)):
            creator = {
                "channel_id": "channel-1",
                "channel_name": "AI Builder",
                "contact_email": "creator@example.com",
                "email_pitch": valid_email(),
            }
            db.log_outreach("campaign-1", creator, False, "Simulated - ready for review")
            export_outreach.export_outreach_tracker()

        with tracker.open(newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["influencer"] == "AI Builder"
    assert rows[0]["status"] == "Simulated - ready for review"