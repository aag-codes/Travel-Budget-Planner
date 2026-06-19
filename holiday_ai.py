import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class HolidayAI:
    """Provides AI-powered travel advice using the Gemini API."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=self.api_key)

    def get_travel_advice(self, destination: str, budget: float, currency: str) -> str | None:
        prompt = f"""
        I am planning a trip to {destination} with a budget of {budget} {currency}.
        Please give me:
        1. Top 3 things to do
        2. Budget tips for this destination
        3. Best time to visit
        Keep the response concise and practical.
        """
        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text

    def get_packing_suggestions(self, destination: str, duration_days: int) -> str | None:
        prompt = f"""
        I am travelling to {destination} for {duration_days} days.
        Give me a concise packing list covering:
        1. Clothing
        2. Essentials
        3. Destination-specific items
        """
        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text

    def get_budget_breakdown_advice(self, destination: str, budget: float, currency: str) -> str | None:
        prompt = f"""
        I have a total travel budget of {budget} {currency} for a trip to {destination}.
        Suggest a realistic budget breakdown across these categories:
        - Accommodation
        - Food
        - Transport
        - Activities
        - Miscellaneous
        Give specific amounts in {currency} and brief tips for each category.
        """
        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
