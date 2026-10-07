import os
import re


def safe_provider_error(error: Exception, provider: str = "AI service") -> str:
    message = str(error)
    for name in ("YOUTUBE_API_KEY", "GEMINI_API_KEY", "SMTP_PASSWORD"):
        secret = os.getenv(name)
        if secret:
            message = message.replace(secret, "[redacted]")
    message = re.sub(
        r"(?i)([?&](?:key|api_key)=)[^&\s\"']+",
        r"\1[redacted]",
        message,
    )
    lowered = message.casefold()
    if "service account" in lowered and any(term in lowered for term in ("disabled", "deleted", "account_state_invalid")):
        return (
            f"{provider} is bound to a disabled or deleted Google service account. "
            "Re-enable that account or create a fresh API key in an active Google Cloud project."
        )
    if any(term in lowered for term in ("401", "unauthenticated", "api key not valid", "invalid api key")):
        return f"{provider} authentication failed. Check that the configured API key is valid and enabled."
    if any(term in lowered for term in ("429", "resource_exhausted", "rate limit")):
        return f"{provider} rate limit reached. Wait briefly or check the account quota."
    return message or type(error).__name__
