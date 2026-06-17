from expense import Expense
from currency_converter import CurrencyConverter

class TripBudget:
    """Manages a trip's budget and list of expenses."""

    def __init__(self, trip_name: str, total_budget: float, base_currency: str):
        self.trip_name = trip_name
        self.total_budget = total_budget
        self.base_currency = base_currency.upper()
        self.expenses = []
        self.converter = CurrencyConverter()

    def add_expense(self, description: str, amount: float, currency: str, category: str):
        """Creates an Expense and adds it to the list."""
        expense = Expense(description, amount, currency, category)
        self.expenses.append(expense)

    def get_total_spent(self) -> float:
        """
        Adds up all expenses, converting each one to the base currency.
        e.g. if base is USD, a 50 EUR expense gets converted to USD first.
        """
        total = 0.0
        for expense in self.expenses:
            if expense.currency == self.base_currency:
                total += expense.amount
            else:
                result = self.converter.convert(expense.amount, expense.currency, self.base_currency)
                total += result["converted_amount"]
        return round(total, 2)

    def get_remaining_budget(self) -> float:
        """Returns how much budget is left."""
        return round(self.total_budget - self.get_total_spent(), 2)

    def get_expenses_by_category(self) -> dict:
        """Groups expenses by category and totals each one."""
        categories = {}
        for expense in self.expenses:
            if expense.currency == self.base_currency:
                amount = expense.amount
            else:
                result = self.converter.convert(expense.amount, expense.currency, self.base_currency)
                amount = result["converted_amount"]

            if expense.category in categories:
                categories[expense.category] += amount
            else:
                categories[expense.category] = amount

        return {k: round(v, 2) for k, v in categories.items()}

    def summary(self) -> dict:
        """Returns a full summary of the trip budget."""
        return {
            "trip_name": self.trip_name,
            "base_currency": self.base_currency,
            "total_budget": self.total_budget,
            "total_spent": self.get_total_spent(),
            "remaining_budget": self.get_remaining_budget(),
            "number_of_expenses": len(self.expenses),
            "expenses_by_category": self.get_expenses_by_category(),
        }s