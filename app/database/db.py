<<<<<<< HEAD
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.getenv("DATA_DIR", "data")) / "outreach.db"


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
=======
import sqlite3
from pathlib import Path

DB_PATH = Path("data/outreach.db")


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
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
<<<<<<< HEAD
    conn.execute("""
    CREATE TABLE IF NOT EXISTS campaign_runs (
        id TEXT PRIMARY KEY,
        campaign TEXT NOT NULL,
        created_at TEXT NOT NULL,
        discovered INTEGER NOT NULL,
        qualified INTEGER NOT NULL,
        snapshot TEXT NOT NULL
    )""")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
=======
    return conn
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e


def already_contacted(campaign_id: str, channel_id: str) -> bool:
    with connect() as conn:
<<<<<<< HEAD
        row = conn.execute("SELECT status FROM outreach_log WHERE campaign_id=? AND channel_id=?", (campaign_id, channel_id)).fetchone()
        return bool(row and row[0] in {"Sent", "Simulated - ready for review"})
=======
        row = conn.execute("SELECT sent FROM outreach_log WHERE campaign_id=? AND channel_id=?", (campaign_id, channel_id)).fetchone()
        return bool(row and row[0])
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e


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
<<<<<<< HEAD


def save_campaign_run(campaign_id: str, result: dict) -> None:
    summary = result["summary"]
    snapshot = {"summary": summary, "creators": result["creators"]}
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO campaign_runs(id, campaign, created_at, discovered, qualified, snapshot)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                summary["campaign"],
                datetime.now(timezone.utc).isoformat(),
                summary["discovered"],
                summary["qualified"],
                json.dumps(snapshot, ensure_ascii=False),
            ),
        )


def list_campaign_runs(limit: int = 20) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, campaign, created_at, discovered, qualified
            FROM campaign_runs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row[0],
            "campaign": row[1],
            "created_at": row[2],
            "discovered": row[3],
            "qualified": row[4],
        }
        for row in rows
    ]


def get_campaign_run(campaign_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT snapshot FROM campaign_runs WHERE id = ?",
            (campaign_id,),
        ).fetchone()
    return json.loads(row[0]) if row else None
=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
