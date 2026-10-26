"""Register recipe-related MCP tools."""

from mcp.server import MCPServer

from recipe_mcp_project1.services.recipe_service import RecipeService


def register_recipe_tools(
    mcp: MCPServer,
    recipe_service: RecipeService | None = None,
) -> None:
    """Register recipe tools on the supplied MCP server."""
    service = recipe_service or RecipeService()

    @mcp.tool()
    def search_recipes(dish_name: str, max_results: int = 5) -> list[str]:
        """Search TheMealDB and save details for matching recipes.

        Args:
            dish_name: Name of the dish to search for.
            max_results: Maximum number of recipes to save (1 to 25).

        Returns:
            Recipe IDs for successful results, or a readable error message.
        """
        return service.search_recipes(dish_name, max_results)
