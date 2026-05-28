"""Tests for privacy redactor module."""

from text2prompt.utils.redactor import redact_text


def test_redact_emails():
    """Emails should be replaced with [REDACTED_EMAIL]."""
    text = "Please contact me at admin@example.com or support-team@host.co.uk immediately."
    cleaned = redact_text(text)
    assert "admin@example.com" not in cleaned
    assert "support-team@host.co.uk" not in cleaned
    assert "contact me at [REDACTED_EMAIL] or [REDACTED_EMAIL]" in cleaned


def test_redact_api_keys():
    """API Keys should be replaced with [REDACTED_API_KEY]."""
    openai_key = "sk-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12"  # gitleaks:allow
    gcp_key = "AIzaSyAzByCxDwExFvGuHtIsJrKqLpMoNnOlPkQ"  # gitleaks:allow
    text = f"Use OpenAI key {openai_key} and GCP key {gcp_key} for this request."
    cleaned = redact_text(text)
    assert openai_key not in cleaned
    assert gcp_key not in cleaned
    assert "OpenAI key [REDACTED_API_KEY] and GCP key [REDACTED_API_KEY]" in cleaned


def test_redact_phone_numbers():
    """Phone numbers should be replaced with [REDACTED_PHONE]."""
    text = "Call me at +1-555-0199 or 5550293 for details. The year is 2026."
    cleaned = redact_text(text)
    assert "555-0199" not in cleaned
    assert "5550293" not in cleaned
    assert "2026" in cleaned  # Should NOT redact 4-digit years!
    assert "Call me at [REDACTED_PHONE] or [REDACTED_PHONE] for details." in cleaned


def test_redact_secrets():
    """Inline credentials/secrets should be replaced with [REDACTED_SECRET]."""
    text = 'Set password="super_secret_123" and token: "auth_token_xyz" in config.'
    cleaned = redact_text(text)
    assert "super_secret_123" not in cleaned
    assert "auth_token_xyz" not in cleaned
    assert 'Set password="[REDACTED_SECRET]" and token: "[REDACTED_SECRET]" in config.' in cleaned
