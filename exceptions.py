# exceptions.py

class WayfareError(Exception):
    """Base class for all app-specific errors. Lets calling code do
    `except WayfareError` to catch anything this app raises on purpose,
    as opposed to an unexpected bug surfacing as a generic Exception."""
    pass


class InvalidCurrencyCodeError(WayfareError):
    """Raised when a currency code doesn't even match the expected
    3-letter shape (e.g. 'US1', 'DOLLARS'). Caught before any API call
    is made, so it never wastes a network request on bad input."""
    pass


class InvalidAmountError(WayfareError):
    """Raised when a numeric amount is missing, non-numeric, zero, or negative."""
    pass


class CurrencyAPIError(WayfareError):
    """Raised when the exchange rate API responds but reports a failure
    (e.g. unsupported currency code that passed the shape check, or
    a malformed/expired API key)."""
    pass


class CurrencyNetworkError(WayfareError):
    """Raised when the exchange rate API can't be reached at all -
    timeout, DNS failure, connection refused, etc. Distinct from
    CurrencyAPIError because the fix is different (check your
    internet connection vs check your API key/currency code)."""
    pass


class HolidayAPIError(WayfareError):
    """Raised when the public holiday lookup fails (network issue or
    the holiday API reports an error)."""
    pass
