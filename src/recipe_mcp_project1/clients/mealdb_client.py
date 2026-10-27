"""Client for communicating with TheMealDB API."""

from typing import Any

import requests

from recipe_mcp_project1.config import settings


class MealDBClient:
    """Client responsible for communicating with TheMealDB API."""

    @staticmethod
    def _search(
        params: dict[str, str] | None = None,
        *,
        random_meal: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch meals, validate the response, and remove duplicates."""
        endpoint = "random.php" if random_meal else "search.php"

        response = requests.get(
            f"{settings.base_url}/{endpoint}",
            params=None if random_meal else params,
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
        return self._search({"s": dish_name})

    def search_by_first_letter(
        self,
        letter: str,
    ) -> list[dict[str, Any]]:
        """Search meals by their first letter."""
        if (
            not isinstance(letter, str)
            or len(letter) != 1
            or letter.lower() not in "abcdefghijklmnopqrstuvwxyz"
        ):
            raise ValueError("Please provide a single letter (a-z).")

        return self._search({"f": letter.lower()})

    def get_random_meal(self) -> list[dict[str, Any]]:
        """Retrieve a random meal."""
        return self._search(random_meal=True)

    def get_cuisines(self) -> list[str]:
        """Retrieve the cuisine names supported by TheMealDB."""
        response = requests.get(
            f"{settings.base_url}/list.php",
            params={"a": "list"},
            timeout=settings.request_timeout,
        )
        response.raise_for_status()

        payload = response.json()
        meals = payload.get("meals")
        if not isinstance(meals, list):
            return []

        cuisines = [
            meal["strArea"].strip()
            for meal in meals
            if isinstance(meal, dict)
            and isinstance(meal.get("strArea"), str)
            and meal["strArea"].strip()
        ]
        return list(dict.fromkeys(cuisines))
