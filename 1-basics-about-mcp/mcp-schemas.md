# MCP Schemas

In the Model Context Protocol (MCP), **Schemas** refer to structured definitions (written using the **JSON Schema** standard) that govern both the communication protocol and how tools declare their input requirements to Large Language Models (LLMs).

There are two primary types of schemas in MCP:

---

## 1. Tool Input Schemas (`inputSchema`)

When you define a tool in an MCP Server, the server generates and publishes an `inputSchema` that describes the expected parameters, types, and constraints for that tool.

### How it Works
1. **Definition:** When writing code for an MCP server (e.g., in Python or TypeScript), you define a tool function and decorate/register it.
2. **Exposition:** The MCP Server publishes the list of tools along with their `inputSchema` to the MCP Client.
3. **Execution:** The MCP Client passes these schemas to the LLM. The LLM reads the parameter names, types, and descriptions to figure out which tool to use and how to format the arguments correctly.

### Example Schema
Below is a conceptual JSON representation of the input schema for a document editing tool (`edit_document`):

```json
{
  "name": "edit_document",
  "description": "Edit a document by replacing a string in the document's content with a new string.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "doc_id": {
        "type": "string",
        "description": "ID of the document that will be edited."
      },
      "old_str": {
        "type": "string",
        "description": "The exact substring/text to replace."
      },
      "new_str": {
        "type": "string",
        "description": "The new text to insert in place of the old text."
      }
    },
    "required": [
      "doc_id",
      "old_str",
      "new_str"
    ]
  }
}
```

---

## 2. MCP Protocol Message Schemas

The Model Context Protocol specification itself defines JSON Schemas that validate the structure of messages sent back and forth between MCP Clients and MCP Servers.

### How it Works
* **Universal Contract:** Since MCP uses standard transports like JSON-RPC 2.0 (over Standard I/O, WebSockets, or HTTP SSE), the protocol schema acts as a strict contract.
* **Message Validation:** Every request and response (e.g., `ListToolsRequest`, `CallToolResult`, `ListResourcesRequest`) must conform to the schema defined in the official MCP specification.
* **Interoperability:** This allows an MCP client written in TypeScript (like Claude Desktop) to connect flawlessly with an MCP server written in Python (like a custom database searcher) because both follow the exact same message structures.
