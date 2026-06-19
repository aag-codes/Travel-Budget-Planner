# holiday_checker.py

# holiday_checker.py

import requests
from datetime import date, datetime, timedelta

from exceptions import HolidayAPIError


class HolidayChecker:
    """
    Checks whether dates fall on public holidays in a given country, using
    the free Nager.Date public holiday API (no API key required).

    Note: this is unrelated to HolidayAI, which generates AI travel advice -
    this class does a factual lookup against a real holiday calendar.
    """

    BASE_URL = "https://date.nager.at/api/v3"
    REQUEST_TIMEOUT_SECONDS = 10

    def _get(self, url: str):
        if not isinstance(url, str) or not url.strip():
            raise HolidayAPIError("Invalid URL supplied.")

        try:
            response = requests.get(
                url,
                timeout=self.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()

        except requests.exceptions.Timeout as e:
            raise HolidayAPIError(
                "The holiday lookup service took too long to respond. Please try again."
            ) from e

        except requests.exceptions.ConnectionError as e:
            raise HolidayAPIError(
                "Couldn't reach the holiday lookup service. Check your internet connection."
            ) from e

        except requests.exceptions.HTTPError as e:
            status_code = getattr(
                e.response,
                "status_code",
                None
            )

            if status_code == 404:
                raise HolidayAPIError(
                    "No holiday data is available for that country code. "
                    "Double check it's a valid 2-letter ISO country code, e.g. US, GB, NG."
                ) from e

            raise HolidayAPIError(
                f"Holiday service returned an error (HTTP {status_code})."
            ) from e

        except requests.exceptions.RequestException as e:
            raise HolidayAPIError(
                f"Network error while checking holidays: {e}"
            ) from e

        try:
            return response.json()

        except ValueError as e:
            raise HolidayAPIError(
                "The holiday service returned an unreadable response."
            ) from e

    def get_public_holidays(
        self,
        year: int,
        country_code: str
    ) -> list[dict]:
        """
        Returns all public holidays for the given year and 2-letter country
        code (e.g. 'US', 'GB', 'NG').
        """

        if not isinstance(country_code, str):
            raise ValueError(
                "Country code must be a string."
            )

        country_code = country_code.strip().upper()

        if len(country_code) != 2:
            raise ValueError(
                "Country code must be exactly 2 letters."
            )

        try:
            year = int(year)
        except (TypeError, ValueError) as e:
            raise ValueError(
                "Year must be a valid integer."
            ) from e

        url = (
            f"{self.BASE_URL}/PublicHolidays/"
            f"{year}/{country_code}"
        )

        data = self._get(url)

        if not isinstance(data, list):
            raise HolidayAPIError(
                "Unexpected response shape from the holiday service."
            )

        return data

    def check_date_range(
        self,
        start_date: date,
        end_date: date,
        country_code: str
    ) -> list[dict]:
        """
        Returns the list of public holidays (date + name) that fall within
        [start_date, end_date] inclusive.
        """

        if not isinstance(start_date, date):
            raise ValueError(
                "start_date must be a date object."
            )

        if not isinstance(end_date, date):
            raise ValueError(
                "end_date must be a date object."
            )

        if end_date < start_date:
            raise ValueError(
                "End date cannot be before start date."
            )

        years_needed = {
            start_date.year,
            end_date.year
        }

        all_holidays = []

        for year in years_needed:
            all_holidays.extend(
                self.get_public_holidays(
                    year,
                    country_code
                )
            )

        matches = []

        for holiday in all_holidays:
            try:
                holiday_date = datetime.strptime(
                    holiday["date"],
                    "%Y-%m-%d"
                ).date()

            except (
                KeyError,
                ValueError,
                TypeError
            ):
                continue

            if start_date <= holiday_date <= end_date:
                matches.append(holiday)

        matches.sort(
            key=lambda h: h.get(
                "date",
                ""
            )
        )

        return matches

    def check_trip_dates(
        self,
        start_date: date,
        duration_days: int,
        country_code: str
    ) -> list[dict]:
        """
        Convenience wrapper: given a trip start date and a duration in days,
        returns any public holidays that fall within the trip.
        """

        if not isinstance(start_date, date):
            raise ValueError(
                "start_date must be a date object."
            )

        try:
            duration_days = int(duration_days)

        except (TypeError, ValueError) as e:
            raise ValueError(
                "Trip duration must be a valid integer."
            ) from e

        if duration_days <= 0:
            raise ValueError(
                "Trip duration must be at least 1 day."
            )

        end_date = start_date + timedelta(
            days=duration_days - 1
        )

        return self.check_date_range(
            start_date,
            end_date,
            country_code
        )