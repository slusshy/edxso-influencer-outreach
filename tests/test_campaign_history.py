import tempfile
from pathlib import Path
from unittest.mock import patch

from app.database import db


def test_campaign_snapshot_round_trip_and_history_order():
    with tempfile.TemporaryDirectory() as directory:
        with patch.object(db, "DB_PATH", Path(directory) / "outreach.db"):
            result = {
                "summary": {"campaign": "AI launch", "discovered": 1, "qualified": 1},
                "creators": [{"channel_id": "creator-1", "channel_name": "AI Studio"}],
            }
            db.save_campaign_run("run-1", result)

            snapshot = db.get_campaign_run("run-1")
            history = db.list_campaign_runs()

    assert snapshot == result
    assert history[0]["id"] == "run-1"
    assert history[0]["campaign"] == "AI launch"
    assert history[0]["qualified"] == 1


def test_safe_error_message_redacts_api_credentials():
    from app.errors import safe_provider_error

    with patch.dict("os.environ", {"YOUTUBE_API_KEY": "local-test-secret"}):
        message = safe_provider_error(
            RuntimeError(
                "https://example.test/api?key=local-test-secret&alt=json"
            )
        )

    assert "local-test-secret" not in message
    assert "[redacted]" in message


def test_safe_provider_error_maps_disabled_account_authentication():
    from app.errors import safe_provider_error

    message = safe_provider_error(
        RuntimeError("401 UNAUTHENTICATED: bound service account is disabled"),
        provider="Gemini",
    )

    assert "disabled or deleted Google service account" in message
    assert "fresh API key" in message


def test_analysis_summary_preserves_the_campaign_guardrails():
    from main import run_analysis

    result = {
        "discovered": 5,
        "qualified": 2,
        "campaign": "Skincare partnership",
        "creators": [],
    }
    with patch("main.run", return_value=result):
        response = run_analysis(
            target=15,
            personalize=False,
            simulate_send=False,
            campaign="Skincare partnership",
            queries=["skincare creators", "ingredient education"],
            min_subs=1000,
            max_subs=75000,
            min_engagement=1.2,
        )

    assert response["success"]
    assert response["summary"]["target"] == 15
    assert response["summary"]["search_phrases"] == ["skincare creators", "ingredient education"]
    assert response["summary"]["min_subs"] == 1000
    assert response["summary"]["max_subs"] == 75000
    assert response["summary"]["min_engagement"] == 1.2
