"""
This script gives an idea about how stdio transport works. This script
you can run it on your terminal. Make sure you have used printed Json
messages for the communication.

RUN: uv run stdio_demo_server.py

Example JSON messages to communicate (paste one per line):

1. Initialize the connection:
   This must be sent first. It negotiates the protocol version and capabilities.
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"terminal-client","version":"1.0.0"}}}

2. Send initialized notification:
   After receiving the initialize response, confirm with this notification
   (no "id" — it's a notification, so no response is expected).
   {"jsonrpc":"2.0","method":"notifications/initialized"}

3. List available tools:
   Discover what tools the server exposes (the "add" tool in this case).
   {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}

4. Call the add tool (a=3, b=5):
   Invoke the "add" tool with arguments a=3 and b=5. The server will return 8.
   {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add","arguments":{"a":3,"b":5}}}
"""
from mcp.server.fastmcp import FastMCP, Context
import asyncio


mcp = FastMCP(name="Stdio Demo Server", log_level="ERROR")


@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    await ctx.info("Preparing to sum...")
    await asyncio.sleep(2)
    await ctx.report_progress(80, 100)
    return a + b


if __name__ == '__main__':
    print("Starting Server ...")
    mcp.run(transport="stdio")
    print("Started !!!")

