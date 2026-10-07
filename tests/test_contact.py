from unittest.mock import Mock, patch

from app.enrichment.contact import _get_public_page, _safe_public_url


def public_dns(*args, **kwargs):
    return [
        (2, 1, 6, "", ("8.8.8.8", 443)),
    ]


def private_dns(*args, **kwargs):
    return [
        (2, 1, 6, "", ("127.0.0.1", 80)),
    ]


def test_safe_public_url_rejects_local_addresses_and_unsafe_ports():
    assert not _safe_public_url("http://127.0.0.1/")
    assert not _safe_public_url("http://example.test:8080/")
    assert not _safe_public_url("https://user:password@example.test/")


def test_safe_public_url_rejects_private_dns_results():
    with patch("app.enrichment.contact.socket.getaddrinfo", side_effect=private_dns):
        assert not _safe_public_url("https://creator.example")


def test_safe_public_url_accepts_public_dns_results():
    with patch("app.enrichment.contact.socket.getaddrinfo", side_effect=public_dns):
        assert _safe_public_url("https://creator.example")


def test_public_page_redirect_is_revalidated_before_fetching():
    redirect = Mock(
        is_redirect=True,
        headers={"location": "http://127.0.0.1/admin"},
    )
    with patch("app.enrichment.contact.socket.getaddrinfo", side_effect=public_dns), patch(
        "app.enrichment.contact.requests.get", return_value=redirect
    ) as get:
        result = _get_public_page("https://creator.example", {})

    assert result is None
    get.assert_called_once()
