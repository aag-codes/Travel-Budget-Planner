# currency_converter.py

import requests
import os
from dotenv import load_dotenv

from validators import normalize_currency_code
from exceptions import CurrencyAPIError, CurrencyNetworkError, InvalidAmountError

load_dotenv()

class CurrencyConverter:
    """Fetches live exchange rates and converts between currencies."""

    BASE_URL = "https://v6.exchangerate-api.com/v6"
    REQUEST_TIMEOUT_SECONDS = 10

    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not self.api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY not found in environment variables.")

    def _get(self, url: str) -> dict:
        """
        Shared request handler: makes the GET call and translates network-
        level failures (timeout, DNS, connection refused) and HTTP-level
        failures into our own exception types, so callers never have to
        know about `requests` internals to handle errors sensibly.
        """
        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise CurrencyNetworkError(
                "The exchange rate service took too long to respond. Please try again."
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise CurrencyNetworkError(
                "Couldn't reach the exchange rate service. Check your internet connection."
            ) from e
        except requests.exceptions.HTTPError as e:
            raise CurrencyAPIError(
                f"The exchange rate service returned an error (HTTP {response.status_code})."
            ) from e
        except requests.exceptions.RequestException as e:
            raise CurrencyNetworkError(f"Network error while contacting the exchange rate service: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise CurrencyAPIError("The exchange rate service returned an unreadable response.") from e

        if data.get("result") != "success":
            raise CurrencyAPIError(f"API error: {data.get('error-type', 'Unknown error')}")

        return data

    def get_exchange_rate(self, base_currency: str, target_currency: str) -> float:
        """
        Returns the exchange rate from base_currency to target_currency.
        Raises InvalidCurrencyCodeError if either code isn't shaped like a
        currency code (3 letters), and CurrencyAPIError if the API doesn't
        recognise a code that *is* correctly shaped (e.g. a typo like XYZ).
        """
        base_currency = normalize_currency_code(base_currency)
        target_currency = normalize_currency_code(target_currency)

        url = f"{self.BASE_URL}/{self.api_key}/pair/{base_currency}/{target_currency}"
        data = self._get(url)
        return data["conversion_rate"]

    def convert(self, amount: float, base_currency: str, target_currency: str) -> dict:
        """
        Converts an amount from base_currency to target_currency.
        Returns a dict with the rate and converted amount.
        """
        try:
            amount = float(amount)
        except (TypeError, ValueError) as e:
            raise InvalidAmountError(f"'{amount}' is not a valid number.") from e
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero.")

        base_currency = normalize_currency_code(base_currency)
        target_currency = normalize_currency_code(target_currency)

        rate = self.get_exchange_rate(base_currency, target_currency)
        converted = round(amount * rate, 2)

        return {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "rate": rate,
            "original_amount": amount,
            "converted_amount": converted,
        }

    def get_supported_currencies(self) -> list:
        """Returns a list of all supported currency codes."""
        url = f"{self.BASE_URL}/{self.api_key}/codes"
        data = self._get(url)
        # Each item is [code, name], we return just the codes
        return [item[0] for item in data["supported_codes"]]
