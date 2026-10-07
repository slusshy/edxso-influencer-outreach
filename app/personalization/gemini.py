import os
import json
<<<<<<< HEAD
import re
import time
from app.errors import safe_provider_error
from app.personalization.validator import validate_messages


def get_client():
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env")
    from google import genai

    return genai.Client(api_key=api_key)


def generate_batch(creators, campaign, client=None):
    client = client or get_client()
=======
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_batch(creators, campaign):
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
    creator_data = []

    for creator in creators:
        creator_data.append({
            "channel_id": creator.get("channel_id"),
            "channel_name": creator.get("channel_name"),
            "platform": creator.get("platform", "YouTube"),
<<<<<<< HEAD
            "subscribers": creator.get("subscribers"),
            "category": creator.get("category"),
            "content_themes": creator.get("content_themes"),
            "recent_content": creator.get("recent_content", []),
=======
            "subscribers": creator.get("subscriberCount"),
            "category": creator.get("category"),
            "content_themes": creator.get("content_themes"),
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
        })

    prompt = f"""
You are an influencer marketing specialist.

Campaign:
{campaign}

Create personalized outreach messages for EVERY creator below.

Creators:
{json.dumps(creator_data, indent=2)}

For each creator generate:

1. Email collaboration pitch
- 60-90 words
- Natural and professional
- Personalized to their niche/content
- Suggest a relevant collaboration
- Explain the value proposition
<<<<<<< HEAD
- Do not include bracketed placeholders such as [Creator Name] or [Your Company Name]
=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e

2. Instagram DM
- 15-30 words
- Casual and natural
- Personalized to their niche/content

IMPORTANT:
- Use ONLY the information provided.
- Do NOT invent recent videos.
- Do NOT invent audience demographics.
- Do NOT invent achievements.
- Do NOT invent brands or partnerships.
- Do NOT invent contact information.
- Do not use the same generic message for every creator.

Return ONLY valid JSON in this format:

[
  {{
    "channel_id": "...",
    "email_pitch": "...",
    "instagram_dm": "..."
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

<<<<<<< HEAD
    text = (response.text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    results = json.loads(text)
    if not isinstance(results, list):
        raise ValueError("Gemini response must be a JSON list")
    return results
=======
    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e


def personalize_qualified(creators, campaign, batch_size=4):

    # Only process qualified creators
    qualified = [
        creator
        for creator in creators
        if str(creator.get("status", "")).lower() == "qualified"
    ]

    print(f"Qualified creators: {len(qualified)}")

<<<<<<< HEAD
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

=======
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
    # Process in small batches
    for start in range(0, len(qualified), batch_size):

        batch = qualified[start:start + batch_size]

        print(
            f"\nProcessing batch "
            f"{start // batch_size + 1}..."
        )

        # Retry a batch if Gemini returns 429
        max_retries = 3

        for attempt in range(max_retries):

            try:
                results = generate_batch(batch, campaign)

                # Match Gemini results back using channel_id
                result_map = {
                    result["channel_id"]: result
                    for result in results
                }

                for creator in batch:

                    channel_id = creator.get("channel_id")

                    result = result_map.get(channel_id)

                    if result:
<<<<<<< HEAD
                        email_pitch = str(result.get("email_pitch", ""))
                        instagram_dm = str(result.get("instagram_dm", ""))
                        errors = validate_messages(email_pitch, instagram_dm)
                        creator["email_pitch"] = email_pitch
                        creator["instagram_dm"] = instagram_dm
                        creator["personalization_status"] = "Ready" if not errors else "Invalid"
                        creator["message_validation_errors"] = "; ".join(errors)

                        print(f"Generated: {creator.get('channel_name')}")

                    else:
                        creator["personalization_status"] = "Failed"
                        creator["message_validation_errors"] = "Gemini returned no result for this creator"
                        print(f"No Gemini result for: {creator.get('channel_name')}")
=======
                        creator["email_pitch"] = result["email_pitch"]
                        creator["instagram_dm"] = result["instagram_dm"]

                        print(
                            f"✓ Generated: "
                            f"{creator.get('channel_name')}"
                        )

                    else:
                        print(
                            f"⚠ No Gemini result for: "
                            f"{creator.get('channel_name')}"
                        )
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e

                break

            except Exception as e:

<<<<<<< HEAD
                error_text = safe_provider_error(e, provider="Gemini")

                if "rate limit reached" in error_text.casefold():
                    if attempt + 1 == max_retries:
                        for creator in batch:
                            creator["personalization_status"] = "Failed"
                            creator["message_validation_errors"] = error_text
                        break
=======
                error_text = str(e)

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e

                    wait_time = 60

                    print(
                        f"Rate limit reached. "
                        f"Waiting {wait_time}s..."
                    )

                    time.sleep(wait_time)

                else:
<<<<<<< HEAD
                    for creator in batch:
                        creator["personalization_status"] = "Failed"
                        creator["message_validation_errors"] = error_text
                    print(f"Batch failed: {e}")
=======
                    print(
                        f"✗ Batch failed: {e}"
                    )
>>>>>>> a44596b3980b5be3485c1a62188cff87cebbd26e
                    break

    return creators