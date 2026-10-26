"""Filesystem repository for recipe JSON files."""

import json
import re
from pathlib import Path
from typing import Any

from recipe_mcp_project1.config import settings


def sanitize_filename(name: str) -> str:
    """Convert a dish name into a filesystem-safe directory name."""
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name.strip().lower())
    safe_name = re.sub(r"\s+", "_", safe_name)
    safe_name = safe_name.strip(" ._")[:200]
    return safe_name or "unknown_dish"


class RecipeRepository:
    """Loads and saves recipe records in JSON files."""

    def __init__(self, recipes_dir: Path | None = None) -> None:
        self.recipes_dir = recipes_dir or settings.recipes_dir

    def _ensure_directory(self, directory: Path) -> None:
        """Create a directory and check that writing is possible."""
        directory.mkdir(mode=0o755, parents=True, exist_ok=True)
        test_file = directory / ".write_test"

        try:
            test_file.write_text("test", encoding="utf-8")
        finally:
            test_file.unlink(missing_ok=True)

    def _load(self, file_path: Path) -> dict[str, Any]:
        """Load existing JSON data, falling back to an empty mapping."""
        if not file_path.exists():
            return {}

        try:
            with file_path.open("r", encoding="utf-8") as json_file:
                data = json.load(json_file)
        except (OSError, json.JSONDecodeError):
            return {}

        return data if isinstance(data, dict) else {}

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
        existing = self._load(file_path)
        existing.update(recipes)

        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(
                existing,
                json_file,
                indent=4,
                ensure_ascii=False,
            )

        return file_path
