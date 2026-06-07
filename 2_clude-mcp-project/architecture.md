# Architecture Overview & Diagrams

This document provides a comprehensive overview of the architecture of the **clude-mcp-project**. It includes high-level architecture, class structures, and request-response flow diagrams designed using Mermaid.

---

## 1. High-Level Architecture

The system is structured as an interactive terminal CLI that communicates with a Claude AI Service. The AI Service can interactively execute tools and query resources hosted on an in-memory Model Context Protocol (MCP) Server via a secure stdio-based MCP Client connection.

```mermaid
flowchart TB
    subgraph User["👤 User"]
        Terminal["Terminal / CLI"]
    end

    subgraph EntryPoint["🚀 Entry Point — main.py"]
        Main["main()"]
        EnvConfig["Load .env\n(CLAUDE_MODEL, ANTHROPIC_API_KEY)"]
        Main --> EnvConfig
    end

    subgraph CLILayer["🖥️ CLI Layer"]
        CliApp["CliApp\n(core/cli.py)"]
        Completer["UnifiedCompleter\n(/ commands, @ resources)"]
        AutoSuggest["CommandAutoSuggest"]
        CliApp --> Completer
        CliApp --> AutoSuggest
    end

    subgraph ChatLayer["💬 Chat Layer"]
        CliChat["CliChat\n(core/cli_chat.py)"]
        ChatBase["Chat (Base Class)\n(core/chat.py)"]
        CliChat -->|inherits| ChatBase
    end

    subgraph AILayer["🤖 AI Service"]
        Claude["Claude\n(core/claude.py)"]
        AnthropicAPI["Anthropic API\n(Claude Model)"]
        Claude -->|HTTP Request| AnthropicAPI
    end

    subgraph MCPLayer["🔌 MCP Layer"]
        MCPClientClass["MCPClient\n(mcp_client.py)"]
        MCPServer["MCP Server\n(mcp_server.py — FastMCP)"]
        MCPClientClass -->|stdio transport| MCPServer
    end

    subgraph ServerCapabilities["📦 Server Capabilities"]
        Tools["🔧 Tools\n• read_doc_contents\n• edit_document"]
        Resources["📄 Resources\n• docs://documents\n• docs://documents/{id}"]
        Prompts["📝 Prompts\n• format (markdown rewrite)"]
        DocsStore["📚 In-Memory Document Store\n(6 documents)"]
        Tools --> DocsStore
        Resources --> DocsStore
    end

    subgraph ToolExecution["⚙️ Tool Manager"]
        ToolMgr["ToolManager\n(core/tools.py)"]
    end

    Terminal -->|user input| Main
    Main -->|initializes| CliApp
    Main -->|creates| Claude
    Main -->|creates| MCPClientClass
    CliApp -->|delegates to| CliChat
    CliChat -->|processes query| ChatBase
    ChatBase -->|sends messages| Claude
    ChatBase -->|tool execution| ToolMgr
    ToolMgr -->|calls tools via| MCPClientClass
    CliChat -->|reads resources| MCPClientClass
    CliChat -->|gets prompts| MCPClientClass
    MCPServer --> Tools
    MCPServer --> Resources
    MCPServer --> Prompts

    style User fill:#1a1a2e,stroke:#e94560,color:#fff
    style EntryPoint fill:#16213e,stroke:#0f3460,color:#fff
    style CLILayer fill:#0f3460,stroke:#533483,color:#fff
    style ChatLayer fill:#533483,stroke:#e94560,color:#fff
    style AILayer fill:#e94560,stroke:#f5a623,color:#fff
    style MCPLayer fill:#0a3d62,stroke:#38ada9,color:#fff
    style ServerCapabilities fill:#1e3799,stroke:#4a69bd,color:#fff
    style ToolExecution fill:#6a0572,stroke:#a239ca,color:#fff
```

---

## 2. Class Diagram

The class diagram maps the object-oriented structure of the CLI client, base chat service, and helper subsystems.

```mermaid
classDiagram
    class Main {
        +main() async
        -claude_model: str
        -anthropic_api_key: str
    }

    class Claude {
        -client: Anthropic
        -model: str
        +add_user_message(messages, message)
        +add_assistant_message(messages, message)
        +text_from_message(message) str
        +chat(messages, system, temperature, tools, thinking) Message
    }

    class MCPClient {
        -_command: str
        -_args: list
        -_env: dict
        -_session: ClientSession
        -_exit_stack: AsyncExitStack
        +connect() async
        +session() ClientSession
        +list_tools() list~Tool~
        +call_tool(tool_name, tool_input) CallToolResult
        +list_prompts() list~Prompt~
        +get_prompt(prompt_name, args) list~Message~
        +read_resource(uri) Any
        +cleanup() async
        +__aenter__() async
        +__aexit__() async
    }

    class Chat {
        #claude_service: Claude
        #clients: dict~str, MCPClient~
        #messages: list~MessageParam~
        +_process_query(query) async
        +run(query) str async
    }

    class CliChat {
        -doc_client: MCPClient
        +list_prompts() list~Prompt~ async
        +list_docs_ids() list~str~ async
        +get_doc_content(doc_id) str async
        +get_prompt(command, doc_id) list~PromptMessage~ async
        -_extract_resources(query) str async
        -_process_command(query) bool async
        +_process_query(query) async
    }

    class ToolManager {
        +get_all_tools(clients)$ list~Tool~ async
        +execute_tool_requests(clients, message)$ list async
        -_find_client_with_tool(clients, tool_name)$ MCPClient async
        -_build_tool_result_part(tool_use_id, text, status)$ dict
    }

    class CliApp {
        -agent: CliChat
        -resources: list
        -prompts: list
        -completer: UnifiedCompleter
        -command_autosuggester: CommandAutoSuggest
        -session: PromptSession
        +initialize() async
        +refresh_resources() async
        +refresh_prompts() async
        +run() async
    }

    class UnifiedCompleter {
        -prompts: list
        -prompt_dict: dict
        -resources: list
        +update_prompts(prompts)
        +update_resources(resources)
        +get_completions(document, event)
    }

    class CommandAutoSuggest {
        -prompts: list
        -prompt_dict: dict
        +get_suggestion(buffer, document) Suggestion
    }

    class FastMCP_Server {
        +read_doc_contents(doc_id) str
        +edit_document(doc_id, old_str, new_str)
        +list_docs() list~str~ [resource]
        +fetch_doc(doc_id) str [resource]
        +format_document(doc_id) list~Message~ [prompt]
    }

    Chat <|-- CliChat : inherits
    Chat --> Claude : uses
    Chat --> ToolManager : uses
    CliChat --> MCPClient : doc_client
    CliApp --> CliChat : agent
    CliApp --> UnifiedCompleter : completer
    CliApp --> CommandAutoSuggest : auto_suggest
    ToolManager --> MCPClient : calls tools via
    MCPClient ..> FastMCP_Server : stdio transport
    Main --> CliApp : creates
    Main --> Claude : creates
    Main --> MCPClient : creates
```

---

## 3. Request-Response Sequence Diagram

This sequence diagram displays the initialization sequence, resources load phase, direct chat query phase, and dynamic loop during tool execution request-response roundtrips.

```mermaid
sequenceDiagram
    actor User
    participant CLI as CliApp
    participant Chat as CliChat / Chat
    participant Claude as Claude Service
    participant API as Anthropic API
    participant TM as ToolManager
    participant MCP as MCPClient
    participant Server as MCP Server

    Note over User,Server: 🔵 Initialization Phase
    User->>CLI: uv run main.py
    CLI->>MCP: connect() via AsyncExitStack
    MCP->>Server: stdio_client (spawn process)
    Server-->>MCP: session initialized
    CLI->>Chat: refresh_resources()
    Chat->>MCP: read_resource("docs://documents")
    MCP->>Server: list documents
    Server-->>MCP: ["deposition.md", "report.pdf", ...]
    MCP-->>Chat: document IDs
    CLI->>Chat: refresh_prompts()
    Chat->>MCP: list_prompts()
    MCP->>Server: list prompts
    Server-->>MCP: [format, ...]
    MCP-->>Chat: prompt list

    Note over User,Server: 🟢 Chat Loop — Normal Query
    User->>CLI: "Tell me about @deposition.md"
    CLI->>Chat: run(query)
    Chat->>Chat: _extract_resources("@deposition.md")
    Chat->>MCP: read_resource("docs://documents/deposition.md")
    MCP->>Server: fetch doc content
    Server-->>MCP: "This deposition covers..."
    MCP-->>Chat: document content
    Chat->>Chat: Build prompt with context
    Chat->>Claude: chat(messages, tools)
    Claude->>API: POST /messages
    API-->>Claude: Response (stop_reason: "end_turn")
    Claude-->>Chat: final text
    Chat-->>CLI: response text
    CLI-->>User: Display response

    Note over User,Server: 🟡 Chat Loop — With Tool Use
    User->>CLI: "/format deposition.md"
    CLI->>Chat: run(command)
    Chat->>Chat: _process_command()
    Chat->>MCP: get_prompt("format", {doc_id})
    MCP->>Server: get prompt
    Server-->>MCP: prompt messages
    MCP-->>Chat: formatted prompt
    Chat->>Claude: chat(messages, tools)
    Claude->>API: POST /messages
    API-->>Claude: Response (stop_reason: "tool_use")

    loop Tool Use Loop (until stop_reason ≠ "tool_use")
        Claude-->>Chat: tool_use request (edit_document)
        Chat->>TM: execute_tool_requests()
        TM->>MCP: call_tool("edit_document", input)
        MCP->>Server: execute tool
        Server-->>MCP: tool result
        MCP-->>TM: CallToolResult
        TM-->>Chat: tool_result_parts
        Chat->>Claude: chat(messages + tool_results, tools)
        Claude->>API: POST /messages
        API-->>Claude: Response
    end

    Claude-->>Chat: final text (stop_reason: "end_turn")
    Chat-->>CLI: response text
    CLI-->>User: Display formatted document
```
