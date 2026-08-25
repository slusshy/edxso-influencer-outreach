from app.discovery.youtube import get_youtube_client, _chunks


def enrich_engagement(creators: list[dict], recent_videos: int = 5) -> list[dict]:
    """Estimate engagement as avg(likes+comments)/subscribers*100 over recent public videos."""
    youtube = get_youtube_client()
    video_to_creator: dict[str, dict] = {}

    for creator in creators:
        playlist = creator.get("uploads_playlist")
        if not playlist:
            creator.update({"engagement_rate": None, "recent_content": [], "avg_views": None})
            continue
        try:
            res = youtube.playlistItems().list(
                part="snippet,contentDetails", playlistId=playlist, maxResults=recent_videos
            ).execute()
            titles = []
            for item in res.get("items", []):
                vid = item.get("contentDetails", {}).get("videoId")
                if vid:
                    video_to_creator[vid] = creator
                    titles.append(item.get("snippet", {}).get("title", ""))
            creator["recent_content"] = titles
            creator["_video_metrics"] = []
        except Exception:
            creator.update({"engagement_rate": None, "recent_content": [], "avg_views": None})

    ids = list(video_to_creator)
    for batch in _chunks(ids):
        res = youtube.videos().list(part="statistics", id=",".join(batch), maxResults=50).execute()
        for item in res.get("items", []):
            creator = video_to_creator.get(item["id"])
            if creator is None:
                continue
            s = item.get("statistics", {})
            creator.setdefault("_video_metrics", []).append({
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
            })

    for creator in creators:
        metrics = creator.pop("_video_metrics", [])
        subs = creator.get("subscribers") or 0
        if metrics:
            creator["avg_views"] = round(sum(x["views"] for x in metrics) / len(metrics), 2)
            avg_interactions = sum(x["likes"] + x["comments"] for x in metrics) / len(metrics)
            creator["engagement_rate"] = round((avg_interactions / subs) * 100, 2) if subs else None
        else:
            creator.setdefault("avg_views", None)
            creator.setdefault("engagement_rate", None)
    return creators
