### How to run this project?
- Step 1:  Navigate 2-claude-mcp-project folder
- Step 2:  Run the command `uv run main.py`
- Step 3:  Type your message and press Enter to chat with the model.

---
### How to setup Mondel Context Inspector?
- Step 1: Activate the virtual environment
  - Run the command `.\.venv\Scripts\activate`
- Step 2: Navigate to `2_clude-mcp-project` folder
- Step 3: Run the command `uv run mcp dev mcp_server.py`
- Step 4: Open the URL shown in the terminal to access the MCP Inspector

#### What does Server Inspector do?
It is a web application that allows you to interact with the MCP server and see the tools and resources etc.., that are available to the AI model.
![server-inspector](images/server-inspector.png)

> NOTE: Due to some unknown reason, I am able to access to the UI. But when I click on the the `Connect` button it is not working. However, if you click on the `Connect` button you should see the UI like shown in the above image. 
> TODO: Change `npx @modelcontextprotocol/inspector` to different version and experiment it to fix this issue. I have tried with latest and npx `@modelcontextprotocol/inspector@0.10.2 uv run  mcp_server.py` but not working


> **Troubleshooting:**
> - If you get `uv trampoline failed to canonicalize script path`, delete `.venv` and recreate it:
>   ```
>   Remove-Item -Recurse -Force .\.venv
>   uv sync
>   ```
> - If `mcp` is not recognized, use `uv run` as prefix (e.g., `uv run mcp dev mcp_server.py`) or activate the venv first (`.\.venv\Scripts\activate`).

### Architecture Overview (Mermaid Diagrams)

The detailed architectural diagrams, including High-Level System Architecture, Class relationships, and Request-Response Sequence flows, have been moved to a separate document:

👉 **[Architecture Overview & Diagrams](architecture.md)**


