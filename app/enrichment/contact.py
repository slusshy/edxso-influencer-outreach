<<<<<<< HEAD
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse
=======
import re
from urllib.parse import urlparse
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
URL_RE = re.compile(r"https?://[^\s<>\]\[)]+", re.I)


def _safe_public_url(url: str) -> bool:
    try:
        p = urlparse(url)
<<<<<<< HEAD
        hostname = p.hostname
        if (
            p.scheme not in {"http", "https"}
            or not hostname
            or p.username is not None
            or p.password is not None
            or p.port not in {None, 80, 443}
        ):
            return False
        try:
            addresses = [ipaddress.ip_address(hostname)]
        except ValueError:
            addresses = [
                ipaddress.ip_address(address[4][0])
                for address in socket.getaddrinfo(hostname, p.port or 443, type=socket.SOCK_STREAM)
            ]
        return bool(addresses) and all(address.is_global for address in addresses)
    except (OSError, ValueError):
        return False


def _get_public_page(url: str, headers: dict) -> tuple[str, str] | None:
    current_url = url
    for _ in range(4):
        if not _safe_public_url(current_url):
            return None
        response = requests.get(
            current_url,
            timeout=6,
            headers=headers,
            allow_redirects=False,
        )
        if response.is_redirect:
            location = response.headers.get("location")
            if not location:
                return None
            current_url = urljoin(current_url, location)
            continue
        if response.ok and "text/html" in response.headers.get("content-type", ""):
            return response.text, response.url
        return None
    return None


=======
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False


>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
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
<<<<<<< HEAD
                    page = _get_public_page(url, headers)
                    if page:
                        html, page_url = page
                        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
                        matches = EMAIL_RE.findall(text)
                        if matches:
                            creator["contact_email"] = matches[0]
                            creator["email_source"] = page_url
=======
                    r = requests.get(url, timeout=6, headers=headers, allow_redirects=True)
                    if r.ok and "text/html" in r.headers.get("content-type", ""):
                        text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
                        matches = EMAIL_RE.findall(text)
                        if matches:
                            creator["contact_email"] = matches[0]
                            creator["email_source"] = r.url
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
                            break
                except requests.RequestException:
                    continue
        creator.setdefault("email_source", "channel description" if emails else "Not Found")
    return creators
