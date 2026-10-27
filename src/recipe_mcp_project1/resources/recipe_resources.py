"""MCP resource for available recipe cuisines."""

from mcp.server import MCPServer

from recipe_mcp_project1.clients.mealdb_client import MealDBClient


def format_cuisines_markdown(cuisines: list[str]) -> str:
    """Format cuisine names as a Markdown list."""
    if not cuisines:
        return "# Available Cuisines\n\nNo cuisines are currently available."

    cuisine_list = "\n".join(f"- {cuisine}" for cuisine in cuisines)
    return f"# Available Cuisines\n\n{cuisine_list}"


def register_recipe_resources(
    mcp: MCPServer,
    client: MealDBClient | None = None,
) -> None:
    """Register recipe-related resources on the supplied MCP server."""
    mealdb_client = client if client is not None else MealDBClient()

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
