"""Application configuration."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable settings loaded from environment variables."""

    project_root: Path = PROJECT_ROOT
    recipes_dir: Path = Path(
        os.getenv("RECIPES_DIR", str(PROJECT_ROOT / "recipes"))
    )
    port: int = int(os.getenv("PORT", "8000"))
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "10"))
    base_url: str = "https://www.themealdb.com/api/json/v1/1"

    def __post_init__(self) -> None:
        """Resolve relative storage paths against the project root."""
        if not self.recipes_dir.is_absolute():
            object.__setattr__(
                self,
                "recipes_dir",
                (self.project_root / self.recipes_dir).resolve(),
            )


settings = Settings()
