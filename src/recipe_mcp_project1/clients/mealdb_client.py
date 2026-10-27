from typing import Any

import requests

from recipe_mcp_project1.config import settings

class MealDBClient:
    """Client responsible for communicating with TheMealDB API."""

    @staticmethod
    def _search(params: dict[str, str]) -> list[dict[str, Any]]:
        """Execute a meal search and return valid, unique records."""
        response = requests.get(
            f"{settings.base_url}/search.php",
            params=params,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()

        payload = response.json()
        meals = payload.get("meals")

        if not isinstance(meals, list):
            return []

        valid_meals = [
            meal for meal in meals
            if isinstance(meal, dict)
        ]

        return MealDBClient.remove_duplicates(valid_meals)

    @staticmethod
    def remove_duplicates(
        meals: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove duplicate meals by ID while preserving order."""
        unique_meals: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for meal in meals:
            meal_id = meal.get("idMeal")

            if not meal_id:
                unique_meals.append(meal)
                continue

            meal_id = str(meal_id)

            if meal_id not in seen_ids:
                seen_ids.add(meal_id)
                unique_meals.append(meal)

        return unique_meals

    def search_by_name(self, dish_name: str) -> list[dict[str, Any]]:
        """Search meals by name."""
        return MealDBClient._search({"s": dish_name})

    def search_by_first_letter(self, letter: str) -> list[dict[str, Any]]:
        """Search meals by their first letter."""
        return MealDBClient._search({"f": letter.lower()})
