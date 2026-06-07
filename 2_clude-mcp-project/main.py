# Standard library imports for async programming, system arguments, and environment variables
import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

# Local imports for MCP client, Claude service, and CLI components
from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

# Load environment variables from .env file
load_dotenv()

# Retrieve Anthropic API configuration from environment variables
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

# Validate that required configuration values are set in the environment
assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


# Main async function that sets up MCP clients and runs the CLI chat interface
async def main():
    # Initialize the Claude AI service with the configured model
    claude_service = Claude(model=claude_model)

    # Get server scripts from command-line arguments
    server_scripts = sys.argv[1:]
    # Dictionary to store all MCP client connections
    clients = {}

    # Determine the command and args for running the main MCP server
    # Use 'uv' package manager if USE_UV env var is set to "1", otherwise use 'python'
    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    # Create an async context manager to handle client lifecycle
    # This ensures all clients are properly closed when exiting the block
    async with AsyncExitStack() as stack:
        # Initialize and register the main documentation MCP client
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        # Initialize and register additional MCP clients from command-line server scripts
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # Create the chat interface with the initialized clients and Claude service
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        # Initialize and run the command-line application
        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


# Entry point for the script
if __name__ == "__main__":
    # On Windows, use the ProactorEventLoopPolicy for better async support
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # Run the async main function
    asyncio.run(main())
