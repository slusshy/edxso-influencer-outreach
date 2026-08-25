import csv
from pathlib import Path

FIELDS = ["channel_name","platform","profile_url","subscribers","engagement_rate","category","content_themes","contact_email","website","country","avg_views","status","filter_reason","email_pitch","instagram_dm"]


def export_csv(creators: list[dict], path: str = "data/influencers.csv"):
    p = Path(path); p.parent.mkdir(exist_ok=True)
    with p.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(creators)
