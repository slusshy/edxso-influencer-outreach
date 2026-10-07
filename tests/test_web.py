from unittest.mock import patch

import server


def test_web_home_and_health_routes():
    client = server.app.test_client()

    assert client.get("/").status_code == 200
    assert b"Fieldnotes" in client.get("/").data
    assert client.get("/api/health").json == {"status": "ok"}


def test_mindpal_workflow_is_not_included():
    home = server.app.test_client().get("/")

    assert b"workflow.getmindpal.com" not in home.data
    assert b"personal-agent" not in home.data
    assert server.app.test_client().get("/agent").status_code == 404


def test_run_route_rejects_invalid_audience_range():
    with patch.object(server, "run_analysis") as run_analysis:
        response = server.app.test_client().post(
            "/api/run",
            json={
                "target": 20,
                "campaign": "A campaign",
                "queries": ["AI"],
                "min_subs": 100000,
                "max_subs": 5000,
            },
        )

    assert response.status_code == 422
    assert "minimum cannot exceed" in response.json["error"]
    run_analysis.assert_not_called()


def test_run_route_saves_and_returns_campaign_snapshot():
    result = {
        "success": True,
        "summary": {"discovered": 1, "qualified": 1, "campaign": "A campaign"},
        "creators": [{"channel_id": "creator-1", "status": "Qualified"}],
    }
    with patch.object(server, "run_analysis", return_value=result) as run_analysis, patch.object(
        server, "save_campaign_run"
    ) as save_campaign_run:
        response = server.app.test_client().post(
            "/api/run",
            json={
                "target": 20,
                "campaign": "A campaign",
                "queries": ["AI", "AI tools"],
                "min_subs": 1000,
                "max_subs": 50000,
                "min_engagement": 0.2,
                "personalize": True,
                "review_log": False,
            },
        )

    assert response.status_code == 200
    assert response.json["run_id"]
    assert response.json["creators"] == result["creators"]
    run_analysis.assert_called_once_with(
        target=20,
        personalize=True,
        simulate_send=False,
        campaign="A campaign",
        queries=["AI", "AI tools"],
        min_subs=1000,
        max_subs=50000,
        min_engagement=0.2,
    )
    save_campaign_run.assert_called_once_with(response.json["run_id"], result)


def test_campaign_snapshot_and_csv_export():
    snapshot = {
        "summary": {"campaign": "Spring launch"},
        "creators": [{"channel_id": "creator-1", "channel_name": "AI Studio"}],
    }
    with patch.object(server, "get_campaign_run", return_value=snapshot):
        client = server.app.test_client()
        response = client.get("/api/history/run-123")
        csv_response = client.get("/api/history/run-123/export.csv")

    assert response.status_code == 200
    assert response.json["run_id"] == "run-123"
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.content_type
    assert b"creator-1" in csv_response.data
    assert b"AI Studio" in csv_response.data


def test_campaign_snapshot_returns_not_found_for_unknown_id():
    with patch.object(server, "get_campaign_run", return_value=None):
        response = server.app.test_client().get("/api/history/missing")

    assert response.status_code == 404


def test_run_route_rejects_non_finite_engagement_guardrail():
    response = server.app.test_client().post(
        "/api/run",
        json={
            "target": 20,
            "campaign": "A campaign",
            "queries": ["AI"],
            "min_subs": 0,
            "max_subs": 50000,
            "min_engagement": float("nan"),
        },
    )

    assert response.status_code == 422
    assert "engagement" in response.json["error"]


def test_run_route_rejects_search_phrases_without_a_topic():
    with patch.object(server, "run_analysis") as run_analysis:
        response = server.app.test_client().post(
            "/api/run",
            json={
                "target": 20,
                "campaign": "A campaign",
                "queries": ["the and for"],
                "min_subs": 0,
                "max_subs": 50000,
                "min_engagement": 0,
            },
        )

    assert response.status_code == 422
    assert "meaningful topic" in response.json["error"]
    run_analysis.assert_not_called()


def test_search_suggestion_route_uses_model_and_returns_valid_phrases():
    class FakeModels:
        def generate_content(self, *, model, contents):
            assert model == "gemini-2.5-flash"
            assert "productivity" in contents
            return type("Response", (), {"text": '["AI workflow tutorials", "productivity creators"]'})()

    with patch.object(
        server, "get_client", return_value=type("Client", (), {"models": FakeModels()})()
    ):
        response = server.app.test_client().post(
            "/api/suggest-searches",
            json={"campaign": "AI productivity tool for teams"},
        )

    assert response.status_code == 200
    assert response.json["queries"] == ["AI workflow tutorials", "productivity creators"]


def test_search_suggestion_route_requires_campaign_brief():
    response = server.app.test_client().post("/api/suggest-searches", json={"campaign": "  "})

    assert response.status_code == 422


def test_search_suggestion_route_explains_gemini_authentication_failure():
    with patch.object(server, "get_client", side_effect=RuntimeError("401 UNAUTHENTICATED")):
        response = server.app.test_client().post(
            "/api/suggest-searches",
            json={"campaign": "AI productivity tool"},
        )

    assert response.status_code == 502
    assert "Gemini authentication failed" in response.json["error"]
