"""Register recipe-related MCP tools."""

from mcp.server import MCPServer

from recipe_mcp_project1.services.recipe_service import RecipeService


def register_recipe_tools(
    mcp: MCPServer,
    recipe_service: RecipeService | None = None,
) -> None:
    """Register recipe-related tools on the supplied MCP server."""
    service = (
        recipe_service
        if recipe_service is not None
        else RecipeService()
    )

    @mcp.tool()
    def search_recipes(
        dish_name: str,
        max_results: int = 5,
    ) -> list[str]:
        """Search TheMealDB and save matching recipe details.

        Args:
            dish_name: Name of the dish to search for.
            max_results: Maximum number of recipes to save (1 to 25).

        Returns:
            A list of recipe IDs.
        """
        return service.search_recipes(dish_name, max_results)

    @mcp.tool()
    def search_recipes_by_first_letter(
        first_letter: str,
        max_results: int = 5,
    ) -> list[str]:
        """Search TheMealDB by a recipe's first letter and save matches.

        Args:
            first_letter: The single letter (a-z) to search by.
            max_results: Maximum number of recipes to save (1 to 25).

        Returns:
            A list of recipe IDs.
        """
        return service.search_recipes_by_first_letter(first_letter, max_results)

    @mcp.tool()
    def get_recipe_details_by_id(recipe_id: str) -> str | list[str]:
        """Retrieve recipe details using a recipe ID.

        Args:
            recipe_id: ID of the recipe to retrieve.

        Returns:
            Recipe details or a readable error message.
        """
        return service.get_recipe_by_id(recipe_id)
