"""MCP prompts for researching recipes."""

from mcp.server import MCPServer


def register_recipe_prompts(mcp: MCPServer) -> None:
    """Register recipe-related prompts on the supplied MCP server."""

    @mcp.prompt(
        name="research_recipes",
        title="Research Recipes",
        description="Find and compare recipes for a dish.",
    )
    def research_recipes(dish_name: str) -> str:
        """Create instructions for searching recipes by dish name."""
        return (
            f"Research recipes for {dish_name!r}. Use the "
            "`search_recipes` tool to find matching recipes, then use "
            "`get_recipe_details_by_id` for the most relevant results. "
            "Compare the recipes by cuisine, ingredients, and instructions. "
            "Present recipe names, IDs, key ingredients, and source links "
            "when available. Do not invent details missing from the results."
        )

    @mcp.prompt(
        name="discover_recipes_by_first_letter",
        title="Discover Recipes by First Letter",
        description="Find recipes whose names start with a given letter.",
    )
    def discover_recipes_by_first_letter(first_letter: str) -> str:
        """Create instructions for searching recipes by initial letter."""
        return (
            f"Find recipes whose names start with {first_letter!r}. Use "
            "`search_recipes_by_first_letter` with this letter, then retrieve "
            "details for the returned recipe IDs using "
            "`get_recipe_details_by_id`. Summarize the available recipes "
            "with their names, cuisines, and a short description based only "
            "on the returned details."
        )

    @mcp.prompt(
        name="get_random_recipe_idea",
        title="Get a Random Recipe Idea",
        description="Fetch and present a random saved recipe.",
    )
    def get_random_recipe_idea() -> str:
        """Create instructions for retrieving a random recipe."""
        return (
            "Use the `get_random_recipe` tool to fetch a random recipe. "
            "Retrieve its details with `get_recipe_details_by_id`, then "
            "present its name, cuisine, ingredients, and preparation "
            "instructions. Include source links when available and do not "
            "invent missing details."
        )

    @mcp.prompt(
        name="analyze_recipe_database",
        title="Analyze Recipe Database",
        description="Summarize insights from the saved recipe database.",
    )
    def analyze_recipe_database() -> str:
        """Create instructions for analyzing saved-recipe statistics."""
        return (
            "Read the `recipe://database/stats` resource and explain the "
            "database size, cuisine and category distribution, and the "
            "provided insights. Clearly distinguish facts reported by the "
            "resource from any interpretation, and do not infer unavailable "
            "statistics."
        )
