# currency_converter.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

class CurrencyConverter:
    """Fetches live exchange rates and converts between currencies."""

    BASE_URL = "https://v6.exchangerate-api.com/v6"

    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not self.api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY not found in environment variables.")

    def get_exchange_rate(self, base_currency: str, target_currency: str) -> float:
        """
        Returns the exchange rate from base_currency to target_currency.
        """
        url = f"{self.BASE_URL}/{self.api_key}/pair/{base_currency}/{target_currency}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            raise ValueError(f"API error: {data.get('error-type', 'Unknown error')}")

        return data["conversion_rate"]

    def convert(self, amount: float, base_currency: str, target_currency: str) -> dict:
        """
        Converts an amount from base_currency to target_currency.
        Returns a dict with the rate and converted amount.
        """
        rate = self.get_exchange_rate(base_currency, target_currency)
        converted = round(amount * rate, 2)

        return {
            "base_currency": base_currency.upper(),
            "target_currency": target_currency.upper(),
            "rate": rate,
            "original_amount": amount,
            "converted_amount": converted,
        }

    def get_supported_currencies(self) -> list:
        """Returns a list of all supported currency codes."""
        url = f"{self.BASE_URL}/{self.api_key}/codes"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            raise ValueError(f"API error: {data.get('error-type', 'Unknown error')}")

        # Each item is [code, name], we return just the codes
        return [item[0] for item in data["supported_codes"]]
