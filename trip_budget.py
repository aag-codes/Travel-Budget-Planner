from expense import Expense
from currency_converter import CurrencyConverter
from validators import normalize_currency_code
from exceptions import InvalidAmountError

class TripBudget:
    """Manages a trip's budget and list of expenses."""

    def __init__(self, trip_name: str, total_budget: float, base_currency: str, duration_days: int = 1):
        if not trip_name or not trip_name.strip():
            raise ValueError("Trip name cannot be empty.")

        try:
            total_budget = float(total_budget)
        except (TypeError, ValueError) as e:
            raise InvalidAmountError(f"'{total_budget}' is not a valid budget amount.") from e
        if total_budget <= 0:
            raise InvalidAmountError("Total budget must be greater than zero.")

        try:
            duration_days = int(duration_days)
        except (TypeError, ValueError) as e:
            raise InvalidAmountError(f"'{duration_days}' is not a valid number of days.") from e
        if duration_days <= 0:
            raise InvalidAmountError("Trip duration must be at least 1 day.")

        self.trip_name = trip_name.strip()
        self.total_budget = total_budget
        self.base_currency = normalize_currency_code(base_currency)
        self.duration_days = duration_days
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

    def get_daily_limit(self) -> float:
        """
        Returns how much can be spent per day, on average, to stay within
        the total budget across the whole trip duration.
        e.g. a 700 USD budget over 7 days -> 100 USD/day.
        """
        return round(self.total_budget / self.duration_days, 2)

    def get_days_elapsed(self) -> int:
        """
        Returns the number of distinct calendar days on which at least one
        expense has been logged so far. Used to track pace against the
        daily limit as the trip progresses.
        """
        if not self.expenses:
            return 0
        days = {expense.date.split(" ")[0] for expense in self.expenses}
        return len(days)

    def get_daily_spending_status(self) -> dict:
        """
        Compares actual average daily spend so far against the planned
        daily limit, so the user can see if they're on pace, ahead, or
        falling behind their budget.
        """
        daily_limit = self.get_daily_limit()
        days_elapsed = self.get_days_elapsed()
        total_spent = self.get_total_spent()

        # Avoid division by zero when nothing has been logged yet.
        avg_daily_spend = round(total_spent / days_elapsed, 2) if days_elapsed > 0 else 0.0
        days_remaining = max(self.duration_days - days_elapsed, 0)
        remaining_budget = self.get_remaining_budget()
        # How much is left to spend per remaining day to stay on budget.
        # If no days remain, fall back to 0 rather than dividing by zero.
        suggested_remaining_daily = (
            round(remaining_budget / days_remaining, 2) if days_remaining > 0 else 0.0
        )

        return {
            "daily_limit": daily_limit,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "avg_daily_spend": avg_daily_spend,
            "is_over_daily_pace": avg_daily_spend > daily_limit,
            "suggested_remaining_daily_budget": suggested_remaining_daily,
        }

    def summary(self) -> dict:
        """Returns a full summary of the trip budget."""
        return {
            "trip_name": self.trip_name,
            "base_currency": self.base_currency,
            "total_budget": self.total_budget,
            "duration_days": self.duration_days,
            "daily_limit": self.get_daily_limit(),
            "total_spent": self.get_total_spent(),
            "remaining_budget": self.get_remaining_budget(),
            "number_of_expenses": len(self.expenses),
            "expenses_by_category": self.get_expenses_by_category(),
            "daily_spending_status": self.get_daily_spending_status(),
        }


class TripComparison:
    """
    Compares the estimated cost of two trips (e.g. two destinations) so a
    user can decide between them. Each trip is represented by its total
    estimated cost in its own local currency; both are converted into a
    single comparison currency so they can be compared like-for-like.
    """

    def __init__(self, comparison_currency: str):
        self.comparison_currency = normalize_currency_code(comparison_currency)
        self.converter = CurrencyConverter()

    def compare(
        self,
        name_a: str, estimated_cost_a: float, currency_a: str,
        name_b: str, estimated_cost_b: float, currency_b: str,
    ) -> dict:
        """
        Converts both estimated costs into the comparison currency and
        returns a side-by-side comparison, including which option is
        cheaper and by how much.
        """
        for label, amount in (("estimated_cost_a", estimated_cost_a), ("estimated_cost_b", estimated_cost_b)):
            try:
                amount = float(amount)
            except (TypeError, ValueError) as e:
                raise InvalidAmountError(f"'{amount}' ({label}) is not a valid number.") from e
            if amount <= 0:
                raise InvalidAmountError(f"{label} must be greater than zero.")

        currency_a = normalize_currency_code(currency_a)
        currency_b = normalize_currency_code(currency_b)

        converted_a = (
            float(estimated_cost_a) if currency_a == self.comparison_currency
            else self.converter.convert(estimated_cost_a, currency_a, self.comparison_currency)["converted_amount"]
        )
        converted_b = (
            float(estimated_cost_b) if currency_b == self.comparison_currency
            else self.converter.convert(estimated_cost_b, currency_b, self.comparison_currency)["converted_amount"]
        )

        difference = round(abs(converted_a - converted_b), 2)
        if converted_a < converted_b:
            cheaper = name_a
        elif converted_b < converted_a:
            cheaper = name_b
        else:
            cheaper = None  # exactly equal

        return {
            "comparison_currency": self.comparison_currency,
            "option_a": {
                "name": name_a,
                "original_amount": estimated_cost_a,
                "original_currency": currency_a,
                "converted_amount": round(converted_a, 2),
            },
            "option_b": {
                "name": name_b,
                "original_amount": estimated_cost_b,
                "original_currency": currency_b,
                "converted_amount": round(converted_b, 2),
            },
            "cheaper_option": cheaper,
            "difference": difference,
        }
