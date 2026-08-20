# Prompt in the MCP
Prompt in the MCP server helps to enhance user interactions by providing specilized and high-quality workflows.

**Prompts Feature Overview**
- Prompts allow the server to offer predefined commands, such as a "format" command that reformats document content into markdown syntax.
- These prompts improve user experience by providing well-crafted instructions that yield better results than ad hoc user inputs.

**Implementing a Prompt in MCP Server**
- Prompts are defined using a decorator with a name and optional description, similar to tools and resources.
- The prompt function returns a list of messages (user and assistant) that are sent to the AI model (Claude) for processing.

**How to utilise prompts**
In this specific project we have created a well crafted prompt called format. Now you can test it using MCP inspector or by running main.py file. If you run main.py then it will open a termial and you have to open "/format <doc_id>" then it will format that particular document for in markdown format.