# MCP Client
The **MCP Client** provides communication between your server and a MCP server. The communication between the client and server can be done over many different ways.

For example, if you have MCP client and MCP server on your same local machine then this communication is done through `Standard IO`. They can also have capability to connect on `HTTP` or `Web Socket` etc..,

The **MCP Specifications** defines different types of messages that can be exchanged. For example:
- **ListToolRequest**: Gives a list of tools
- **ListToolResult**:Here are the tools can run
- **CallToolRequest**: Run a particular Tool with these arguments
- **CallToolResult**: Here is the result of Tool Run.
![MCP Requests Flow](images/mcp_requests_flow.png)
source: Anthropic Academy