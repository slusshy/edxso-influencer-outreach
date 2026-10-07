<<<<<<< HEAD
import json
from types import SimpleNamespace

from app.personalization.gemini import generate_batch


def test_generate_batch_does_not_require_live_api():
    class FakeModels:
        def generate_content(self, *, model, contents):
            return SimpleNamespace(text=json.dumps([{
                "channel_id": "channel-1",
                "email_pitch": "Email pitch",
                "instagram_dm": "Instagram message",
            }]))

    result = generate_batch(
        [{"channel_id": "channel-1", "channel_name": "AI Automation Labs"}],
        "Campaign",
        client=SimpleNamespace(models=FakeModels()),
    )

    assert result[0]["channel_id"] == "channel-1"
=======
from app.personalization.gemini import generate_messages

creator = {
    "channel_name": "AI Automation Labs",
    "platform": "YouTube",
    "subscribers": 56900,
    "category": "Technology / AI",
    "content_themes": "ai, automation, chatgpt",
}

messages = generate_messages(creator)

print("\nEMAIL:\n")
print(messages["email_pitch"])

print("\nINSTAGRAM DM:\n")
print(messages["instagram_dm"])
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
