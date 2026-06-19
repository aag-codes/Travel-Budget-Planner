# validators.py

import re

# Three uppercase letters, e.g. USD, NGN, GBP. Case-insensitive on input,
# but the canonical form we accept/return is always uppercase.
CURRENCY_CODE_PATTERN = re.compile(r"^[A-Za-z]{3}$")

# Matches a number that may have thousands separators and/or a decimal part,
# e.g. "1200", "1,200.50", "99.99". Used to pull a price out of free text
# like "I spent about 45.50 on lunch" or "budget: 1,200 NGN".
PRICE_PATTERN = re.compile(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?")


def is_valid_currency_code(code: str) -> bool:
    """
    Returns True if `code` is exactly three alphabetic characters
    (the ISO 4217 shape, e.g. USD, NGN, GBP). Does not check that the
    code is a *real* currency - that's the converter's job, since the
    list of valid codes changes over time and lives behind the API.
    """
    if not isinstance(code, str):
        return False
    return bool(CURRENCY_CODE_PATTERN.match(code.strip()))


def normalize_currency_code(code: str) -> str:
    """
    Validates and uppercases a currency code.
    Raises ValueError if the shape is invalid (not exactly 3 letters).
    """
    if not is_valid_currency_code(code):
        raise ValueError(
            f"'{code}' is not a valid currency code. "
            "Currency codes must be exactly 3 letters, e.g. USD, NGN, GBP."
        )
    return code.strip().upper()


def extract_price_from_text(text: str) -> float | None:
    """
    Extracts the first numeric price-like value from free text.
    e.g. "about 1,200.50 NGN for the hotel" -> 1200.50
         "no price mentioned here"          -> None
    Returns a float, or None if nothing price-shaped was found.
    """
    if not text:
        return None
    match = PRICE_PATTERN.search(text)
    if not match:
        return None
    raw = match.group().replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def extract_currency_code_from_text(text: str, known_codes: set[str] | None = None) -> str | None:
    """
    Extracts the first 3-letter currency-code-shaped token from free text,
    e.g. "1200 NGN for the hotel" -> "NGN". Returns None if none found.

    IMPORTANT: a bare 3-letter shape match will also match ordinary 3-letter
    words ("the", "for", "and"...). If `known_codes` is provided (e.g. the
    list from CurrencyConverter.get_supported_currencies(), or the
    COMMON_CURRENCIES list in app.py), only tokens that are actually in that
    set are returned, which avoids that false-positive problem. Without
    `known_codes`, this falls back to an uppercase-only match, since real
    currency codes are conventionally written in caps (NGN, not ngn or Ngn),
    which filters out most ordinary lowercase words.
    """
    if not text:
        return None

    if known_codes:
        upper_codes = {c.upper() for c in known_codes}
        for token in re.findall(r"\b[A-Za-z]{3}\b", text):
            if token.upper() in upper_codes:
                return token.upper()
        return None

    match = re.search(r"\b[A-Z]{3}\b", text)
    return match.group() if match else None
