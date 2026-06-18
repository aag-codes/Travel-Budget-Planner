# expense.py

from datetime import datetime

class Expense:
    """Represents a single expense entry in a trip budget."""

    def __init__(self, description: str, amount: float, currency: str, category: str):
        self.description = description
        self.amount = amount
        self.currency = currency.upper()
        self.category = category
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