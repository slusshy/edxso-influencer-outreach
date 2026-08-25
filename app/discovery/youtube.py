import os
from typing import Iterable
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()


def get_youtube_client():
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is missing from .env")
    return build("youtube", "v3", developerKey=key)


def _chunks(values: list[str], size: int = 50) -> Iterable[list[str]]:
    for i in range(0, len(values), size):
        yield values[i:i + size]


def search_channels(query: str, max_results: int = 50) -> list[dict]:
    """Discover channels and enrich them with channel-level metadata in batches."""
    youtube = get_youtube_client()
    found: dict[str, dict] = {}
    token = None

    while len(found) < max_results:
        take = min(50, max_results - len(found))
        request = youtube.search().list(
            part="snippet", q=query, type="channel", maxResults=take, pageToken=token
        )
        response = request.execute()
        for item in response.get("items", []):
            cid = item["id"]["channelId"]
            found[cid] = {
                "channel_id": cid,
                "channel_name": item["snippet"]["title"],
                "platform": "YouTube",
                "profile_url": f"https://www.youtube.com/channel/{cid}",
            }
        token = response.get("nextPageToken")
        if not token:
            break

    ids = list(found)
    for batch in _chunks(ids):
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails,brandingSettings",
            id=",".join(batch),
            maxResults=50,
        ).execute()
        for item in response.get("items", []):
            cid = item["id"]
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            branding = item.get("brandingSettings", {}).get("channel", {})
            found[cid].update({
                "channel_name": snippet.get("title", found[cid]["channel_name"]),
                "description": snippet.get("description", ""),
                "country": snippet.get("country", branding.get("country", "Not Found")),
                "subscribers": int(stats.get("subscriberCount", 0)) if not stats.get("hiddenSubscriberCount") else None,
                "total_views": int(stats.get("viewCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "uploads_playlist": item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads"),
            })
    return list(found.values())


def discover_multiple_queries(queries: list[str], target: int = 80) -> list[dict]:
    """Run several niche queries and deduplicate by channel_id."""
    all_creators: dict[str, dict] = {}
    per_query = min(50, max(10, target // max(1, len(queries)) + 10))
    for query in queries:
        for creator in search_channels(query, per_query):
            creator["discovery_query"] = query
            all_creators.setdefault(creator["channel_id"], creator)
            if len(all_creators) >= target:
                return list(all_creators.values())
    return list(all_creators.values())
