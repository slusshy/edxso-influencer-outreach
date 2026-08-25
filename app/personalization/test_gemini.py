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