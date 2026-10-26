"""Run the Recipe MCP server."""

from recipe_mcp_project1.server import mcp


def main() -> None:
    """Start the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
