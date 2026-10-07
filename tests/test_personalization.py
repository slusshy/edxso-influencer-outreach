import json
from types import SimpleNamespace

from app.personalization import gemini
from app.personalization.validator import validate_messages


def valid_email():
    return " ".join(["message"] * 60)


def valid_dm():
    return " ".join(["message"] * 15)


def test_message_validator_accepts_required_lengths():
    assert validate_messages(valid_email(), valid_dm()) == []


def test_message_validator_rejects_length_and_placeholders():
    errors = validate_messages("Hi [Creator Name]", "Hi there")

    assert any("Email pitch must be 60-90 words" in error for error in errors)
    assert any("Instagram DM must be 15-30 words" in error for error in errors)
    assert any("placeholders" in error for error in errors)


def test_generate_batch_uses_discovered_metrics_and_content():
    prompts = []

    class FakeModels:
        def generate_content(self, *, model, contents):
            prompts.append(contents)
            result = [{"channel_id": "channel-1", "email_pitch": valid_email(), "instagram_dm": valid_dm()}]
            return SimpleNamespace(text=json.dumps(result))

    creator = {
        "channel_id": "channel-1",
        "channel_name": "AI Builder",
        "subscribers": 12345,
        "recent_content": ["Building an AI workflow"],
        "content_themes": "ai, automation",
    }
    response = gemini.generate_batch([creator], "Campaign", client=SimpleNamespace(models=FakeModels()))

    assert response[0]["channel_id"] == "channel-1"
    assert '"subscribers": 12345' in prompts[0]
    assert "Building an AI workflow" in prompts[0]


def test_personalization_marks_invalid_generated_copy(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "generate_batch",
        lambda creators, campaign: [{
            "channel_id": "channel-1",
            "email_pitch": "Too short",
            "instagram_dm": "Too short",
        }],
    )
    creator = {"channel_id": "channel-1", "status": "Qualified"}

    gemini.personalize_qualified([creator], "Campaign")

    assert creator["personalization_status"] == "Invalid"
    assert "Email pitch must be 60-90 words" in creator["message_validation_errors"]