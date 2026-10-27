"""MCP resource for available recipe cuisines."""

from collections import Counter
import json
from typing import Any
from urllib.parse import quote

from mcp.server import MCPServer

from recipe_mcp_project1.clients.mealdb_client import MealDBClient
from recipe_mcp_project1.storage.recipe_repository import RecipeRepository


def format_cuisines_markdown(cuisines: list[str]) -> str:
    """Format cuisine names as a Markdown list."""
    if not cuisines:
        return "# Available Cuisines\n\nNo cuisines are currently available."

    cuisine_list = "\n".join(f"- {cuisine}" for cuisine in cuisines)
    return f"# Available Cuisines\n\n{cuisine_list}"


def format_recipe_database_stats(
    recipes: dict[str, dict[str, Any]],
) -> str:
    """Summarize saved recipes and provide distribution insights."""
    cuisine_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    ingredient_counts: Counter[str] = Counter()

    for recipe in recipes.values():
        cuisine = recipe.get("cuisine")
        if isinstance(cuisine, str) and cuisine.strip() and cuisine != "Unknown":
            cuisine_counts[cuisine.strip()] += 1

        category = recipe.get("category")
        if (
            isinstance(category, str)
            and category.strip()
            and category != "Unknown"
        ):
            category_counts[category.strip()] += 1

        ingredients = recipe.get("ingredients")
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                if isinstance(ingredient, dict):
                    name = ingredient.get("ingredient")
                    if isinstance(name, str) and name.strip():
                        ingredient_counts[name.strip()] += 1

    lines = [
        "# Recipe Database Statistics",
        "",
        f"- **Unique recipes:** {len(recipes)}",
        f"- **Cuisines represented:** {len(cuisine_counts)}",
        f"- **Categories represented:** {len(category_counts)}",
        f"- **Distinct ingredients:** {len(ingredient_counts)}",
    ]

    if not recipes:
        lines.extend(["", "No saved recipes are available yet."])
        return "\n".join(lines)

    lines.extend(["", "## Cuisine distribution"])
    if cuisine_counts:
        lines.extend(
            f"- {name}: {count}"
            for name, count in cuisine_counts.most_common()
        )
    else:
        lines.append("- No cuisine data is available.")

    lines.extend(["", "## Category distribution"])
    if category_counts:
        lines.extend(
            f"- {name}: {count}"
            for name, count in category_counts.most_common()
        )
    else:
        lines.append("- No category data is available.")

    lines.extend(["", "## Insights"])
    if cuisine_counts:
        cuisine, count = cuisine_counts.most_common(1)[0]
        lines.append(
            f"- Most represented cuisine: **{cuisine}** ({count} recipes)."
        )
    if category_counts:
        category, count = category_counts.most_common(1)[0]
        lines.append(
            f"- Most represented category: **{category}** "
            f"({count} recipes)."
        )
    if ingredient_counts:
        ingredient, count = ingredient_counts.most_common(1)[0]
        lines.append(
            f"- Most frequently used ingredient: **{ingredient}** "
            f"(appears in {count} recipes)."
        )
    if not cuisine_counts and not category_counts and not ingredient_counts:
        lines.append("- Saved recipes do not contain enough data for insights.")

    return "\n".join(lines)


def format_saved_recipes_markdown(
    recipes: dict[str, dict[str, Any]],
) -> str:
    """Render saved recipes as a Markdown index with detail resource links."""
    if not recipes:
        return "# Saved Recipes\n\nNo recipes have been saved yet."

    lines = ["# Saved Recipes", ""]
    sorted_recipes = sorted(
        recipes.items(),
        key=lambda item: (
            str(item[1].get("name") or "Unknown").casefold(),
            item[0],
        ),
    )

    for recipe_id, recipe in sorted_recipes:
        name = recipe.get("name")
        name = name if isinstance(name, str) and name.strip() else "Unknown"
        cuisine = recipe.get("cuisine")
        category = recipe.get("category")
        details = [
            value.strip()
            for value in (cuisine, category)
            if isinstance(value, str)
            and value.strip()
            and value != "Unknown"
        ]
        detail_text = f" — {'; '.join(details)}" if details else ""
        recipe_uri = quote(recipe_id, safe="")
        lines.append(
            f"- [{name}](recipe://recipes/{recipe_uri}) "
            f"(ID: `{recipe_id}`){detail_text}"
        )

    return "\n".join(lines)


def register_recipe_resources(
    mcp: MCPServer,
    client: MealDBClient | None = None,
    repository: RecipeRepository | None = None,
) -> None:
    """Register recipe-related resources on the supplied MCP server."""
    mealdb_client = client if client is not None else MealDBClient()
    recipe_repository = (
        repository if repository is not None else RecipeRepository()
    )

    @mcp.resource(
        "recipe://cuisines",
        name="Recipe Cuisines",
        description=(
            "Cuisine names available from TheMealDB, formatted as Markdown."
        ),
        mime_type="text/markdown",
    )
    def get_cuisines() -> str:
        """Return available cuisine names as Markdown."""
        cuisines = mealdb_client.get_cuisines()
        return format_cuisines_markdown(cuisines)

    @mcp.resource(
        "recipe://database/stats",
        name="Recipe Database Statistics",
        description=(
            "Statistics and insights about recipes saved in the local database."
        ),
        mime_type="text/markdown",
    )
    def get_recipe_database_stats() -> str:
        """Return saved recipe statistics and insights as Markdown."""
        recipes = recipe_repository.get_all_recipes()
        return format_recipe_database_stats(recipes)

    @mcp.resource(
        "recipe://database/recipes",
        name="Saved Recipe Index",
        description=(
            "An index of locally saved recipes with links to their details."
        ),
        mime_type="text/markdown",
    )
    def get_saved_recipes() -> str:
        """Return the saved recipes as a Markdown index."""
        recipes = recipe_repository.get_all_recipes()
        return format_saved_recipes_markdown(recipes)

    @mcp.resource(
        "recipe://recipes/{recipe_id}",
        name="Saved Recipe Details",
        description="Details for a recipe saved in the local recipe database.",
        mime_type="application/json",
    )
    def get_saved_recipe(recipe_id: str) -> str:
        """Return one saved recipe's details as JSON."""
        recipe = recipe_repository.get_all_recipes().get(recipe_id)
        if recipe is None:
            raise ValueError(f"No saved recipe found with ID: {recipe_id}")

        return json.dumps(recipe, indent=4, ensure_ascii=False)
