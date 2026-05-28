"""Sensitive data privacy redactor."""

import re

# High-fidelity regular expression patterns for redacting sensitive values
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+?\b\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,9}[-.\s]?\d{1,9}\b')
API_KEY_REGEX = re.compile(r'\b(sk-[a-zA-Z0-9]{40,60}|[a-zA-Z0-9]{32}|AIzaSy[a-zA-Z0-9_-]{33})\b')

# Generic secret patterns matching standard credential keys (e.g. password="foo")
# The inner group excludes quote characters to avoid swallowing enclosing quotes.
GENERIC_SECRET_REGEX = re.compile(
    r'\b(?:key|secret|password|passwd|token|auth)\b\s*[:=]\s*["\']?([a-zA-Z0-9_\-@#%^&*()+={}\[\]|\\:;<>,.?/~`]{8,})["\']?',
    re.IGNORECASE
)


def redact_text(text: str) -> str:
    """Redact sensitive information (API keys, emails, phone numbers, secrets) from text.

    Args:
        text: The generated prompt text to clean.

    Returns:
        The text with all sensitive matched structures replaced by redactor tags.
    """
    if not text:
        return text

    # 1. Redact email addresses
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)

    # 2. Redact OpenAI / Google Cloud API keys
    text = API_KEY_REGEX.sub("[REDACTED_API_KEY]", text)

    # 3. Redact phone numbers (with guard for years/short numbers)
    def phone_repl(match):
        val = match.group(0)
        # Skip pure 4-digit numbers as they are highly likely to be years
        if val.isdigit() and len(val) == 4:
            return val
        return "[REDACTED_PHONE]"
    text = PHONE_REGEX.sub(phone_repl, text)

    # 4. Redact credentials/generic secrets
    def secret_repl(match):
        full_match = match.group(0)
        secret_val = match.group(1)
        # Keep the key prefix, substitute only the raw credential value
        start = full_match.find(secret_val)
        return full_match[:start] + "[REDACTED_SECRET]" + full_match[start + len(secret_val):]
    text = GENERIC_SECRET_REGEX.sub(secret_repl, text)

    return text
