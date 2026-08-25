import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
URL_RE = re.compile(r"https?://[^\s<>\]\[)]+", re.I)


def _safe_public_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False


def enrich_contact(creators: list[dict], scrape_linked_pages: bool = True) -> list[dict]:
    """Use only publicly visible text/pages. Never guesses an email."""
    headers = {"User-Agent": "Mozilla/5.0 InfluencerResearchPrototype/1.0"}
    for creator in creators:
        description = creator.get("description", "") or ""
        emails = EMAIL_RE.findall(description)
        urls = [u.rstrip(".,") for u in URL_RE.findall(description) if _safe_public_url(u)]
        creator["website"] = urls[0] if urls else "Not Found"
        creator["contact_email"] = emails[0] if emails else "Not Found"

        if creator["contact_email"] == "Not Found" and scrape_linked_pages:
            for url in urls[:2]:
                try:
                    r = requests.get(url, timeout=6, headers=headers, allow_redirects=True)
                    if r.ok and "text/html" in r.headers.get("content-type", ""):
                        text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
                        matches = EMAIL_RE.findall(text)
                        if matches:
                            creator["contact_email"] = matches[0]
                            creator["email_source"] = r.url
                            break
                except requests.RequestException:
                    continue
        creator.setdefault("email_source", "channel description" if emails else "Not Found")
    return creators
