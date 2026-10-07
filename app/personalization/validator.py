import re


def validate_messages(email_pitch: str, instagram_dm: str) -> list[str]:
	"""Return actionable validation errors for generated outreach messages."""
	errors = []
	email_words = re.findall(r"\b[\w'-]+\b", email_pitch or "")
	dm_words = re.findall(r"\b[\w'-]+\b", instagram_dm or "")

	if not 60 <= len(email_words) <= 90:
		errors.append(f"Email pitch must be 60-90 words (got {len(email_words)})")
	if not 15 <= len(dm_words) <= 30:
		errors.append(f"Instagram DM must be 15-30 words (got {len(dm_words)})")
	if re.search(r"\[[^\]]+\]", email_pitch or "") or re.search(r"\[[^\]]+\]", instagram_dm or ""):
		errors.append("Messages contain unresolved bracketed placeholders")

	return errors
