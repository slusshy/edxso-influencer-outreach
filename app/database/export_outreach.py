import sqlite3
import pandas as pd


DB_PATH = "data/outreach.db"
OUTPUT_PATH = "data/outreach_tracker.csv"


def export_outreach_tracker():
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

    print(f"Saved outreach tracker to {OUTPUT_PATH}")


if __name__ == "__main__":
    export_outreach_tracker()