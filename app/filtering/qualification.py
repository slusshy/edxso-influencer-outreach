KEYWORDS = {"ai", "artificial intelligence", "machine learning", "llm", "chatgpt", "generative ai", "automation", "data science", "python"}


def classify_and_filter(creators: list[dict], min_subs: int = 5000, max_subs: int = 100000, min_engagement: float = 0.5) -> list[dict]:
    for c in creators:
        text = " ".join([c.get("channel_name", ""), c.get("description", ""), *c.get("recent_content", [])]).lower()
        matched = sorted(k for k in KEYWORDS if k in text)
        c["category"] = "Technology / AI" if matched else "Other / Unclear"
        c["content_themes"] = ", ".join(matched[:6]) if matched else "Not confidently identified"

        reasons = []
        subs = c.get("subscribers")
        er = c.get("engagement_rate")
        if subs is None:
            reasons.append("Subscriber count unavailable")
        elif not min_subs <= subs <= max_subs:
            reasons.append(f"Subscribers {subs:,} outside {min_subs:,}-{max_subs:,}")
        if not matched:
            reasons.append("Insufficient AI/technology relevance")
        if er is None:
            reasons.append("Engagement unavailable")
        elif er < min_engagement:
            reasons.append(f"Engagement {er:.2f}% below {min_engagement:.2f}%")

        c["status"] = "Qualified" if not reasons else "Rejected"
        c["filter_reason"] = "Passed follower, relevance and engagement criteria" if not reasons else "; ".join(reasons)
    return creators
