# expense.py

from datetime import datetime

from validators import normalize_currency_code
from exceptions import InvalidAmountError

class Expense:
    """Represents a single expense entry in a trip budget."""

    def __init__(self, description: str, amount: float, currency: str, category: str):
        if not description or not description.strip():
            raise ValueError("Expense description cannot be empty.")

        try:
            amount = float(amount)
        except (TypeError, ValueError) as e:
            raise InvalidAmountError(f"'{amount}' is not a valid expense amount.") from e
        if amount <= 0:
            raise InvalidAmountError("Expense amount must be greater than zero.")

        if not category or not category.strip():
            raise ValueError("Expense category cannot be empty.")

        self.description = description.strip()
        self.amount = amount
        self.currency = normalize_currency_code(currency)
        self.category = category.strip()
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self) -> dict:
        """Converts the expense to a dictionary (useful for display and reports)."""
        return {
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "date": self.date,
        }

    def __repr__(self) -> str:
        """How the expense looks when printed."""
        return f"Expense({self.description}, {self.amount} {self.currency}, {self.category})"
