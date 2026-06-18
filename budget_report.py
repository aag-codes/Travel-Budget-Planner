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