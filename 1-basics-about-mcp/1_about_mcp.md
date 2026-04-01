## Model Context Protocol (MCP)
MCP is a **Communication Layer** and it solves a common problem in AI: how to give LLMs (Large Language Models) seamless access to data and tools across different platforms?

Think of it like a USB port 🔌 for AI. Before USB, every device (printers, mice, keyboards) needed a unique connector. MCP acts as that universal connector, allowing AI models to securely plug into various data sources—like Google Drive, Slack, GitHub, or local databases—without developers needing to write custom code for every single integration.

For example, if you want to pull latest pull requests information from GitHub, you might have to write you own `Tool`(e.g: git_pull_request) and it's definition. With MCP your tool and definition writing handled by MCP sever and this server communicate with the GitHub and sends you the response.

![MCP server and client](images\mcp_client_server.png)
source: Anthropic Academy

### Common Questions
Q1. **Who builds MCP servers?**

Often Service providers like GitHub, Slack itself makes their own MCP server implementation. You can make a MCP server to wrap up access to some services.

Q2. **How it different from calling an API?**

MCP server provides tool schemas and functions.

Q3. **MCP Servers and Tools are same things?**

In MCP provides tool schemas and functions already defined for you. Tools that you have to write manually and call by your self.