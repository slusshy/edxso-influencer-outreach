<<<<<<< HEAD
import csv
from pathlib import Path
from app.database.db import connect


=======
import sqlite3
import pandas as pd


DB_PATH = "data/outreach.db"
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
OUTPUT_PATH = "data/outreach_tracker.csv"


def export_outreach_tracker():
<<<<<<< HEAD
    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn, output.open("w", newline="", encoding="utf-8-sig") as tracker:
        rows = conn.execute("""
            SELECT influencer, email, message_generated, sent, sent_at, status, error
            FROM outreach_log
            ORDER BY id
        """).fetchall()
        writer = csv.writer(tracker)
        writer.writerow(["influencer", "email", "message_generated", "sent", "sent_at", "status", "error"])
        writer.writerows(rows)
=======
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            influencer,
            email,
            message_generated,
            sent,
            sent_at,
            status,
            error
        FROM outreach_log
        ORDER BY id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    df.to_csv(OUTPUT_PATH, index=False)
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e

    print(f"Saved outreach tracker to {OUTPUT_PATH}")


if __name__ == "__main__":
    export_outreach_tracker()