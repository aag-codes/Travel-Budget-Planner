import csv
import io
import json

from trip_budget import TripBudget

class BudgetReport:
    """Generates a readable report from a TripBudget."""

    def __init__(self, trip_budget: TripBudget):
        self.trip_budget = trip_budget

    def generate_report(self) -> str:
        """Returns a formatted text report of the trip budget."""
        summary = self.trip_budget.summary()

        report = []
        report.append(f"Trip Report: {summary['trip_name']}")
        report.append(f"Base Currency: {summary['base_currency']}")
        report.append(f"Total Budget: {summary['total_budget']} {summary['base_currency']}")
        report.append(f"Daily Limit: {summary['daily_limit']} {summary['base_currency']}/day")
        report.append(f"Total Spent: {summary['total_spent']} {summary['base_currency']}")
        report.append(f"Remaining Budget: {summary['remaining_budget']} {summary['base_currency']}")
        report.append(f"Number of Expenses: {summary['number_of_expenses']}")
        report.append("")
        report.append("Breakdown by Category:")

        for category, amount in summary["expenses_by_category"].items():
            report.append(f"  - {category}: {amount} {summary['base_currency']}")

        report.append("")
        report.append("All Expenses:")
        for expense in self.trip_budget.expenses:
            report.append(f"  - {expense.date} | {expense.description} | {expense.amount} {expense.currency} | {expense.category}")

        return "\n".join(report)

    def to_dict(self) -> dict:
        """Returns the report as a dictionary (useful for the frontend)."""
        return {
            "summary": self.trip_budget.summary(),
            "expenses": [expense.to_dict() for expense in self.trip_budget.expenses],
        }

    def to_json(self, indent: int = 2) -> str:
        """Returns the full report (summary + expenses) as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def export_json(self, filepath: str) -> str:
        """Writes the full report as JSON to disk. Returns the filepath written."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        return filepath

    def to_csv(self) -> str:
        """
        Returns the expense list as a CSV string (date, description, amount,
        currency, category). Note: CSV is row-based, so this exports the
        expense log rather than the nested summary - use to_json()/export_json()
        if you need the full summary (totals, daily limit, etc.) exported too.
        """
        buffer = io.StringIO()
        fieldnames = ["date", "description", "amount", "currency", "category"]
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for expense in self.trip_budget.expenses:
            writer.writerow(expense.to_dict())
        return buffer.getvalue()

    def export_csv(self, filepath: str) -> str:
        """Writes the expense list as CSV to disk. Returns the filepath written."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(self.to_csv())
        return filepath
