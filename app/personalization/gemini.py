import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_batch(creators, campaign):
    creator_data = []

    for creator in creators:
        creator_data.append({
            "channel_id": creator.get("channel_id"),
            "channel_name": creator.get("channel_name"),
            "platform": creator.get("platform", "YouTube"),
            "subscribers": creator.get("subscriberCount"),
            "category": creator.get("category"),
            "content_themes": creator.get("content_themes"),
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

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


def personalize_qualified(creators, campaign, batch_size=4):

    # Only process qualified creators
    qualified = [
        creator
        for creator in creators
        if str(creator.get("status", "")).lower() == "qualified"
    ]

    print(f"Qualified creators: {len(qualified)}")

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

                break

            except Exception as e:

                error_text = str(e)

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                    wait_time = 60

                    print(
                        f"Rate limit reached. "
                        f"Waiting {wait_time}s..."
                    )

                    time.sleep(wait_time)

                else:
                    print(
                        f"✗ Batch failed: {e}"
                    )
                    break

    return creators