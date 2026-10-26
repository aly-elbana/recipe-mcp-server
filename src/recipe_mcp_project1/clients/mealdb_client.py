from typing import Any

import requests

from recipe_mcp_project1.config import settings


class MealDBClient:
    """Small client responsible only for communicating with TheMealDB."""

    def search_by_name(self, dish_name: str) -> list[dict[str, Any]]:
        """Search meals by name and return API meal records.

        Raises:
            requests.RequestException: If the HTTP request fails.
            ValueError: If the API response is not valid JSON.
        """
        response = requests.get(
            f"{settings.base_url}/search.php",
            params={"s": dish_name},
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        payload = response.json()

        meals = payload.get("meals")
        if not isinstance(meals, list):
            return []

        return [meal for meal in meals if isinstance(meal, dict)]
