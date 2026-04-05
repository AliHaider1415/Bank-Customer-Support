import re

# ── Blocked topic categories (off-domain) ─────────────────────────────
OFF_TOPIC_PATTERNS = [
    r"\b(recipe|cook|food|restaurant|movie|film|song|music|lyrics|sport|game|score)\b",
    r"\b(weather|forecast|temperature|climate)\b",
    r"\b(dating|relationship|love|girlfriend|boyfriend)\b",
    r"\b(politic|election|vote|president|minister)\b",
    r"\b(religion|pray|church|mosque|temple)\b",
]

# ── Harmful / dangerous content patterns ──────────────────────────────
HARMFUL_PATTERNS = [
    r"\b(kill|murder|attack|bomb|weapon|exploit|hack)\b",
    r"\b(suicide|self[- ]?harm|hurt\s+(my|your)self)\b",
    r"\b(drug|cocaine|heroin|meth|illegal\s+substance)\b",
    r"\b(terror|extremis[mt]|radicali[sz])\b",
    r"\b(launder|fraud|scam|phish|counterfeit)\b",
    r"\b(steal|rob|theft|embezzle)\b",
]

# ── Prompt injection / jailbreak patterns ─────────────────────────────
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)",
    r"ignore\s+your\s+(instructions|rules|guidelines|programming)",
    r"you\s+are\s+now\s+(?!a\s+banking)",
    r"act\s+as\s+(?!a\s+(banking|helpful|bank))",
    r"pretend\s+(you\s+are|to\s+be)\s+(?!a\s+bank)",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"\bDAN\b",
    r"do\s+anything\s+now",
    r"jailbreak",
    r"bypass\s+(filter|safety|guard|restriction|rule)",
    r"override\s+(instruction|rule|policy|safety)",
    r"forget\s+(everything|your\s+(rules|instructions|training))",
    r"new\s+persona",
    r"enter\s+developer\s+mode",
    r"sudo\s+mode",
    r"reveal\s+(your|the)\s+(system|initial|original)\s+(prompt|instruction|message)",
    r"repeat\s+(your|the)\s+(system|initial)\s+(prompt|instruction)",
    r"what\s+(is|are)\s+your\s+(system|initial)\s+(prompt|instruction|rule)",
]

# ── Sensitive data patterns (PII leakage prevention) ──────────────────
PII_PATTERNS = [
    r"\b\d{5}[-\s]?\d{7}[-\s]?\d{1}\b",      # CNIC-like: 12345-1234567-1
    r"\b\d{13}\b",                              # 13-digit number (CNIC without dashes)
    r"\b\d{16}\b",                              # Credit/debit card number
    r"\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b", # Card with dashes/spaces
    r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",       # IBAN
]

SAFE_REFUSAL = (
    "I'm sorry, but I can only help with banking and account-related questions. "
    "Please ask something related to our bank's products or services."
)

HARMFUL_REFUSAL = (
    "I'm unable to respond to that request. If you need help, "
    "please contact our customer support helpline."
)

INJECTION_REFUSAL = (
    "Your message appears to contain instructions that conflict with my guidelines. "
    "I can only answer banking-related questions based on our knowledge base."
)


def _matches_any(text: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def validate_input(query: str) -> tuple[bool, str]:
    """
    Validate user input before processing.
    Returns (is_safe, reason). If is_safe is False, reason contains
    the user-facing refusal message.
    """
    stripped = query.strip()

    if len(stripped) < 2:
        return False, "Please enter a valid question."

    if len(stripped) > 2000:
        return False, "Your message is too long. Please keep it under 2000 characters."

    if _matches_any(stripped, INJECTION_PATTERNS):
        return False, INJECTION_REFUSAL

    if _matches_any(stripped, HARMFUL_PATTERNS):
        return False, HARMFUL_REFUSAL

    if _matches_any(stripped, OFF_TOPIC_PATTERNS):
        return False, SAFE_REFUSAL

    return True, ""


def sanitize_input(query: str) -> str:
    """
    Sanitize user input to reduce prompt injection risk.
    Strips control characters and normalizes whitespace.
    """
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", query)

    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    return sanitized


def validate_output(response: str) -> tuple[bool, str]:
    """
    Validate LLM output before displaying to the user.
    Redacts PII and checks for policy-violating content.
    Returns (is_safe, cleaned_response).
    """
    cleaned = response

    for pattern in PII_PATTERNS:
        cleaned = re.sub(pattern, "[REDACTED]", cleaned)

    if _matches_any(cleaned, HARMFUL_PATTERNS):
        return False, (
            "The generated response was filtered due to policy guidelines. "
            "Please rephrase your question."
        )

    return True, cleaned
