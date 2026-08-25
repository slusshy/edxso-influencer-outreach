import sqlite3
from pathlib import Path

DB_PATH = Path("data/outreach.db")


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS outreach_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        influencer TEXT,
        email TEXT,
        message_generated INTEGER DEFAULT 0,
        sent INTEGER DEFAULT 0,
        sent_at TEXT,
        status TEXT,
        error TEXT,
        UNIQUE(campaign_id, channel_id)
    )""")
    return conn


def already_contacted(campaign_id: str, channel_id: str) -> bool:
    with connect() as conn:
        row = conn.execute("SELECT sent FROM outreach_log WHERE campaign_id=? AND channel_id=?", (campaign_id, channel_id)).fetchone()
        return bool(row and row[0])


def log_outreach(campaign_id: str, creator: dict, sent: bool, status: str, error: str | None = None, sent_at: str | None = None):
    with connect() as conn:
        conn.execute("""
        INSERT INTO outreach_log(campaign_id,channel_id,influencer,email,message_generated,sent,sent_at,status,error)
        VALUES(?,?,?,?,?,?,?,?,?)
        ON CONFLICT(campaign_id,channel_id) DO UPDATE SET
          email=excluded.email, message_generated=excluded.message_generated,
          sent=excluded.sent, sent_at=excluded.sent_at, status=excluded.status, error=excluded.error
        """, (campaign_id, creator["channel_id"], creator.get("channel_name"), creator.get("contact_email"),
              int(bool(creator.get("email_pitch"))), int(sent), sent_at, status, error))
