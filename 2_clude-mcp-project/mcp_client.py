"""
You can run it directly by using following command
uv run mcp_client.py

or through main.py also 
uv run main.py
"""
from mcp.types import CreateMessageRequestParams
from mcp.shared.context import RequestContext
from pydantic import validate_call_decorator
import sys
import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

import json
from pydantic import AnyUrl

from core.claude import Claude


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        # Step 1: Bundle the server launch details into a parameter object.
        #   - command : the executable to run (e.g. "uv" or "python")
        #   - args    : CLI arguments passed to that command (e.g. ["run", "mcp_server.py"])
        #   - env     : optional environment variables for the subprocess
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        # Step 2: Launch the MCP server as a subprocess and open a stdio transport.
        #   stdio_client(server_params) starts the server process and returns an
        #   async context manager that yields a (read_stream, write_stream) tuple.
        #   enter_async_context registers it with the exit stack so the subprocess
        #   is automatically cleaned up when the stack closes.
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Step 3: Unpack the two communication streams.
        #   _stdio  -> the read stream  (data coming FROM the server)
        #   _write  -> the write stream  (data going TO the server)
        _stdio, _write = stdio_transport

        # Step 4: Wrap the raw streams in a high-level ClientSession.
        #   ClientSession speaks the MCP JSON-RPC protocol on top of the raw
        #   read/write streams, giving us methods like list_tools(), call_tool(), etc.
        #   Again registered with the exit stack for automatic cleanup.
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write, sampling_callback=self.sampling_callback)
        )

        # Step 5: Perform the MCP handshake (initialize request).
        #   This exchanges protocol version and capability information between
        #   the client and the server, making the session ready to use.
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session


    # async def list_prompts(self) -> list[types.Prompt]:
    #     # TODO: Return a list of prompts defined by the MCP server
    #     return []

    # async def get_prompt(self, prompt_name, args: dict[str, str]):
    #     # TODO: Get a particular prompt defined by the MCP server
    #     return []

    # async def read_resource(self, uri: str) -> Any:
    #     # TODO: Read a resource, parse the contents and return it
    #     return []

    # Fetches all available tools from the MCP server so the AI model knows what actions it can perform.
    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    # Executes a specific tool on the MCP server by name with given inputs and returns the result.
    async def call_tool(
        self, tool_name: str, tool_input
    ) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)

    # Retrieves all prompt templates defined on the MCP server for structured AI interactions.
    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        return result.prompts

    # Fetches a specific prompt by name with arguments, returning the rendered messages ready for the AI.
    async def get_prompt(self, prompt_name, args: dict[str, str]):
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    # Reads a resource (file, data, etc.) from the MCP server by URI and auto-parses JSON content.
    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)

            return resource.text
    
    async def sampling_callback(
        self, context: RequestContext, params: CreateMessageRequestParams
    ) -> types.CreateMessageResult:
        print("\n[MCP SAMPLING CALLBACK] Received sampling request from MCP server...")
        import os
        model_name = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        claude_service = Claude(model=model_name)

        formatted_messages = []
        for msg in params.messages:
            content_text = (
                msg.content.text if hasattr(msg.content, "text") else str(msg.content)
            )
            formatted_messages.append({"role": msg.role, "content": content_text})

        response = claude_service.chat(
            messages=formatted_messages,
            system=params.systemPrompt,
        )

        response_text = claude_service.text_from_message(response)
        print(f"[MCP SAMPLING CALLBACK] Completed sampling response using model '{model_name}'.")

        return types.CreateMessageResult(
            role="assistant",
            content=types.TextContent(
                type="text",
                text=response_text,
            ),
            model=model_name,
        )

    # Gracefully shuts down the connection by closing the exit stack and clearing the session.
    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    # Enables `async with MCPClient(...)` syntax — automatically connects when entering the block.
    async def __aenter__(self):
        await self.connect()
        return self

    # Ensures cleanup runs automatically when exiting the `async with` block, even if an error occurs.
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        


# For testing
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        tools = await _client.list_tools()
        print(f"TOOLS : {[t.name for t in tools]}")

        result = await _client.list_prompts()
        print(f"PROMPTS : {[p.name for p in result]}")

        # Example: call summarize tool (triggers MCP Sampling back to client LLM)
        # summary_result = await _client.call_tool("summarize", {"text_to_summarize": "Model Context Protocol simplifies agent capabilities."})
        # print(f"SUMMARY RESULT: {summary_result}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
