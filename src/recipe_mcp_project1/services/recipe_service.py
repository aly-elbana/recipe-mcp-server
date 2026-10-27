"""Application logic for recipe search and normalization."""

from typing import Any

import requests

from recipe_mcp_project1.clients.mealdb_client import MealDBClient
from recipe_mcp_project1.storage.recipe_repository import RecipeRepository


def extract_ingredients(meal: dict[str, Any]) -> list[dict[str, str]]:
    """Extract non-empty ingredients and their measurements from a meal."""
    ingredients = []

    for index in range(1, 21):
        ingredient = meal.get(f"strIngredient{index}")
        measure = meal.get(f"strMeasure{index}")

        if isinstance(ingredient, str) and ingredient.strip():
            ingredients.append(
                {
                    "ingredient": ingredient.strip(),
                    "measure": (
                        measure.strip()
                        if isinstance(measure, str)
                        else ""
                    ),
                }
            )

    return ingredients


def normalize_recipe(meal: dict[str, Any]) -> dict[str, Any]:
    """Convert a TheMealDB record into the application's recipe format."""
    raw_tags = meal.get("strTags") or ""

    return {
        "id": str(meal.get("idMeal", "")),
        "name": meal.get("strMeal") or "Unknown",
        "cuisine": meal.get("strArea") or "Unknown",
        "category": meal.get("strCategory") or "Unknown",
        "instructions": (
            meal.get("strInstructions") or "No instructions provided"
        ),
        "image_url": meal.get("strMealThumb") or "",
        "youtube_url": meal.get("strYoutube") or "",
        "source_url": meal.get("strSource") or "",
        "ingredients": extract_ingredients(meal),
        "tags": [
            tag.strip()
            for tag in raw_tags.split(",")
            if tag.strip()
        ],
    }


class RecipeService:
    """Coordinate recipe searches, normalization, and persistence."""

    def __init__(
        self,
        client: MealDBClient | None = None,
        repository: RecipeRepository | None = None,
    ) -> None:
        """Initialize the service with injectable dependencies."""
        self.client = (
            client if client is not None else MealDBClient()
        )
        self.repository = (
            repository
            if repository is not None
            else RecipeRepository()
        )

    def search_recipes(
        self,
        dish_name: str,
        max_results: int = 5,
    ) -> list[str]:
        """Search for recipes, save their details, and return their IDs."""
        if not isinstance(dish_name, str) or not dish_name.strip():
            return ["Error: dish_name must be a non-empty string."]

        if (
            not isinstance(max_results, int)
            or isinstance(max_results, bool)
            or not 1 <= max_results <= 25
        ):
            return ["Error: max_results must be an integer between 1 and 25."]

        dish_name = dish_name.strip()

        try:
            meals = self.client.search_by_name(dish_name)
        except requests.Timeout:
            return ["Error: The recipe API request timed out."]
        except requests.RequestException as exc:
            return [f"Error: Recipe API request failed: {exc}"]
        except ValueError:
            return ["Error: The recipe API returned invalid JSON."]

        if not meals:
            return [f"No recipes found for dish: {dish_name}"]

        recipes = {}

        for meal in meals[:max_results]:
            recipe_id = meal.get("idMeal")

            if not recipe_id:
                continue

            recipes[str(recipe_id)] = normalize_recipe(meal)

        if not recipes:
            return [
                "Error: The API response did not contain valid recipe IDs."
            ]

        try:
            self.repository.save_recipes(dish_name, recipes)
        except OSError as exc:
            return [f"Error: Could not save recipe information: {exc}"]

        return list(recipes)

    def get_recipe_by_id(self, recipe_id: str) -> str| list[str]:
        """Retrieve a saved recipe by its ID."""
        if not isinstance(recipe_id, str) or not recipe_id.strip():
            return ["Error: recipe_id must be a non-empty string."]

        try:
            return self.repository.get_recipe_details(recipe_id.strip())
        except OSError as exc:
            return [f"Error: Could not load recipe information: {exc}"]
        
    def search_recipes_by_first_letter(
        self,
        first_letter: str,
        max_results: int = 5,
    ) -> list[str]:
        """Search by initial letter, save recipes, and return their IDs."""
        if not isinstance(first_letter, str):
            return ["Error: first_letter must be a single letter (a-z)."]

        first_letter = first_letter.strip().lower()
        if len(first_letter) != 1 or first_letter not in "abcdefghijklmnopqrstuvwxyz":
            return ["Error: first_letter must be a single letter (a-z)."]

        if (
            not isinstance(max_results, int)
            or isinstance(max_results, bool)
            or not 1 <= max_results <= 25
        ):
            return ["Error: max_results must be an integer between 1 and 25."]


        try:
            meals = self.client.search_by_first_letter(first_letter)
        except requests.Timeout:
            return ["Error: The recipe API request timed out."]
        except requests.RequestException as exc:
            return [f"Error: Recipe API request failed: {exc}"]
        except ValueError:
            return ["Error: The recipe API returned invalid JSON."]

        if not meals:
            return [f"No recipes found starting with: {first_letter}"]

        recipes: dict[str, dict[str, Any]] = {}

        for meal in meals[:max_results]:
            recipe_id = meal.get("idMeal")

            if not recipe_id:
                continue

            recipes[str(recipe_id)] = normalize_recipe(meal)

        if not recipes:
            return [
                "Error: The API response did not contain valid recipe IDs."
            ]

        try:
            self.repository.save_recipes(first_letter, recipes)
        except OSError as exc:
            return [f"Error: Could not save recipe information: {exc}"]

        return list(recipes)