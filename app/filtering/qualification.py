<<<<<<< HEAD
import re

KEYWORDS = {
    "ai", "artificial intelligence", "machine learning", "llm", "chatgpt",
    "generative ai", "automation", "data science", "python",
}
AI_KEYWORDS = KEYWORDS
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "into",
    "is", "it", "of", "on", "or", "the", "to", "with", "your",
}


def _contains_term(text: str, term: str) -> bool:
    escaped = re.escape(term.strip())
    if not escaped:
        return False
    return re.search(rf"(?<!\w){escaped}(?!\w)", text, flags=re.IGNORECASE) is not None


def _relevance_terms(terms: list[str] | None) -> set[str]:
    normalized: set[str] = set()
    for term in terms or []:
        phrase = " ".join(term.lower().split())
        if phrase:
            normalized.add(phrase)
            normalized.update(
                token for token in re.findall(r"[\w+#.-]+", phrase)
                if len(token) >= 3 and token not in STOP_WORDS
            )
    return normalized


def classify_and_filter(
    creators: list[dict],
    min_subs: int = 5000,
    max_subs: int = 100000,
    min_engagement: float = 0.5,
    relevance_terms: list[str] | None = None,
) -> list[dict]:
    search_terms = _relevance_terms(relevance_terms)
    for c in creators:
        parts = [c.get("channel_name", ""), c.get("description", "")]
        parts.extend(c.get("recent_content", []))
        text = " ".join(str(part) for part in parts if part).lower()
        matched = sorted(
            term for term in AI_KEYWORDS | search_terms
            if _contains_term(text, term)
        )
        c["category"] = (
            "Technology / AI"
            if any(_contains_term(text, term) for term in AI_KEYWORDS)
            else ("Relevant to search" if matched else "Other / Unclear")
        )
=======
KEYWORDS = {"ai", "artificial intelligence", "machine learning", "llm", "chatgpt", "generative ai", "automation", "data science", "python"}


def classify_and_filter(creators: list[dict], min_subs: int = 5000, max_subs: int = 100000, min_engagement: float = 0.5) -> list[dict]:
    for c in creators:
        text = " ".join([c.get("channel_name", ""), c.get("description", ""), *c.get("recent_content", [])]).lower()
        matched = sorted(k for k in KEYWORDS if k in text)
        c["category"] = "Technology / AI" if matched else "Other / Unclear"
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
        c["content_themes"] = ", ".join(matched[:6]) if matched else "Not confidently identified"

        reasons = []
        subs = c.get("subscribers")
        er = c.get("engagement_rate")
        if subs is None:
            reasons.append("Subscriber count unavailable")
        elif not min_subs <= subs <= max_subs:
            reasons.append(f"Subscribers {subs:,} outside {min_subs:,}-{max_subs:,}")
<<<<<<< HEAD
        if relevance_terms:
            if not any(_contains_term(text, term) for term in search_terms):
                reasons.append("Insufficient relevance to selected search phrases")
        elif not any(_contains_term(text, term) for term in AI_KEYWORDS):
=======
        if not matched:
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
            reasons.append("Insufficient AI/technology relevance")
        if er is None:
            reasons.append("Engagement unavailable")
        elif er < min_engagement:
            reasons.append(f"Engagement {er:.2f}% below {min_engagement:.2f}%")

        c["status"] = "Qualified" if not reasons else "Rejected"
        c["filter_reason"] = "Passed follower, relevance and engagement criteria" if not reasons else "; ".join(reasons)
    return creators
