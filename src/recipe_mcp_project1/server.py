"""Configure the Recipe MCP server and register its tools."""

from mcp.server import MCPServer

from recipe_mcp_project1.resources.recipe_resources import register_recipe_resources
from recipe_mcp_project1.tools.recipe_tools import register_recipe_tools

mcp = MCPServer("Recipe_Research")
register_recipe_tools(mcp)
register_recipe_resources(mcp)
