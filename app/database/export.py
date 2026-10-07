import csv
from pathlib import Path

<<<<<<< HEAD
FIELDS = [
    "channel_id", "channel_name", "platform", "profile_url", "discovery_query",
    "subscribers", "engagement_rate", "avg_views", "total_views", "video_count",
    "category", "content_themes", "recent_content", "contact_email", "email_source",
    "website", "country", "status", "filter_reason", "email_pitch", "instagram_dm",
    "personalization_status", "message_validation_errors", "send_status",
]
=======
FIELDS = ["channel_name","platform","profile_url","subscribers","engagement_rate","category","content_themes","contact_email","website","country","avg_views","status","filter_reason","email_pitch","instagram_dm"]
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e


def export_csv(creators: list[dict], path: str = "data/influencers.csv"):
    p = Path(path); p.parent.mkdir(exist_ok=True)
    with p.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(creators)
