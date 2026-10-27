"""Filesystem repository for storing and retrieving recipe data."""

import json
import re
from pathlib import Path
from typing import Any

from recipe_mcp_project1.config import settings


def sanitize_filename(name: str) -> str:
    """Convert a dish name into a filesystem-safe directory name."""
    safe_name = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        name.strip().lower(),
    )
    safe_name = re.sub(r"\s+", "_", safe_name)
    safe_name = safe_name.strip(" ._")[:200]

    return safe_name or "unknown_dish"


class RecipeRepository:
    """Load and save recipe records in JSON files."""

    def __init__(self, recipes_dir: Path | None = None) -> None:
        """Initialize the repository with an optional storage directory."""
        self.recipes_dir = (
            recipes_dir
            if recipes_dir is not None
            else settings.recipes_dir
        )

    def _ensure_directory(self, directory: Path) -> None:
        """Create a directory and verify that it is writable."""
        directory.mkdir(
            mode=0o755,
            parents=True,
            exist_ok=True,
        )

        test_file = directory / ".write_test"

        try:
            test_file.write_text("test", encoding="utf-8")
        finally:
            test_file.unlink(missing_ok=True)

    def _load(self, file_path: Path) -> dict[str, Any]:
        """Load existing JSON data or return an empty dictionary if absent."""
        if not file_path.exists():
            return {}

        with file_path.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Expected a JSON object in {file_path}."
            )

        return data

    def save_recipes(
        self,
        dish_name: str,
        recipes: dict[str, dict[str, Any]],
    ) -> Path:
        """Merge recipes into the dish's JSON file and return its path."""
        self._ensure_directory(self.recipes_dir)

        dish_dir = self.recipes_dir / sanitize_filename(dish_name)
        self._ensure_directory(dish_dir)

        file_path = dish_dir / "recipes_info.json"
        existing_recipes = self._load(file_path)
        existing_recipes.update(recipes)

        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(
                existing_recipes,
                json_file,
                indent=4,
                ensure_ascii=False,
            )

        return file_path

    def get_recipe_details(self, recipe_id: str) -> str:
        """Find a saved recipe by ID and return its details as JSON."""
        if not self.recipes_dir.exists():
            return f"Recipes directory does not exist: {self.recipes_dir}"

        for dish_dir in self.recipes_dir.iterdir():
            if not dish_dir.is_dir():
                continue

            file_path = dish_dir / "recipes_info.json"

            if not file_path.is_file():
                continue

            try:
                with file_path.open("r", encoding="utf-8") as json_file:
                    recipes = json.load(json_file)
            except (OSError, json.JSONDecodeError) as exc:
                print(f"Warning: Could not read {file_path}: {exc}")
                continue

            if not isinstance(recipes, dict):
                continue

            recipe = recipes.get(recipe_id)

            if recipe is not None:
                return json.dumps(
                    recipe,
                    indent=4,
                    ensure_ascii=False,
                )

        return f"No saved recipe found with ID: {recipe_id}"