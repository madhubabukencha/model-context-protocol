# Sampling in Model Context Protocol
In MCP, Sampling is the feature that lets a server ask the client to run an LLM completion — flipping the usual direction of control.

## The Normal Flow
Client (with an LLM) → calls tools/resources on the Server. The server just does work and returns data; it has no LLM of its own.

## With Sampling
The Server can send a `sampling/createMessage` request back to the Client, asking the Client's LLM to generate text on its behalf. The server describes what it wants (messages, system prompt, model preferences, max tokens), and the client's LLM produces a completion and sends it back.

## Why this exists:
A lot of MCP servers do useful work (querying a DB, hitting an API, parsing files) but don't have their own LLM. Instead of every server needing its own API key and model integration, sampling lets servers "borrow" the LLM the client already has — for things like:

- Summarizing large tool output before returning it
- Making a judgment call mid-workflow (e.g., "does this data look anomalous?")
- Generating natural language from structured data
- Multi-step agentic reasoning inside a tool call

---

## Code Examples

### 1. Server-Side Implementation (`mcp_server.py`)

In [mcp_server.py](file:///d:/Artificial_Intelligence/model-context-protocol/2_clude-mcp-project/mcp_server.py#L114-L138), the server tool uses `ctx.session.create_message()` to request LLM sampling from the connected client:

```python
from mcp.types import TextContent, SamplingMessage
from mcp.server.fastmcp import FastMCP, Context

@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    prompt = f"""
    Please summarize the following text:

    {text_to_summarize}
    """

    # Request the client's LLM to generate a completion
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=prompt
                )
            )
        ],
        max_tokens=4000,
        system_prompt="Your are a helpful research assistant"
    )

    if result.content.type == "text":
        return result.content.text
    else:
        raise ValueError("Sampling failed")
```

---

### 2. Client-Side Implementation (`mcp_client.py`)

In [mcp_client.py](file:///d:/Artificial_Intelligence/model-context-protocol/2_clude-mcp-project/mcp_client.py#L127-L155), the client registers `sampling_callback` to receive server sampling requests, query Claude, and return the result:

#### Step A: Registering `sampling_callback` in `ClientSession`
```python
from mcp.types import CreateMessageRequestParams
from mcp.shared.context import RequestContext
from mcp import ClientSession, types

# Register sampling_callback when initializing ClientSession
self._session = await self._exit_stack.enter_async_context(
    ClientSession(_stdio, _write, sampling_callback=self.sampling_callback)
)
```

#### Step B: Handling the `sampling_callback`
```python
from core.claude import Claude

async def sampling_callback(
    self, context: RequestContext, params: CreateMessageRequestParams
) -> types.CreateMessageResult:
    import os
    model_name = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    claude_service = Claude(model=model_name)

    # 1. Format incoming sampling messages for the LLM
    formatted_messages = []
    for msg in params.messages:
        content_text = (
            msg.content.text if hasattr(msg.content, "text") else str(msg.content)
        )
        formatted_messages.append({"role": msg.role, "content": content_text})

    # 2. Call the Client's LLM (Claude)
    response = claude_service.chat(
        messages=formatted_messages,
        system=params.systemPrompt,
    )

    response_text = claude_service.text_from_message(response)

    # 3. Return CreateMessageResult back to the MCP server
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text=response_text,
        ),
        model=model_name,
    )

---

## Key Tips & Debugging Sampling in CLI

### 1. Observing Sampling Execution in CLI
In `mcp_client.py`, add print logs inside `sampling_callback` to monitor when the MCP server requests sampling:

```python
async def sampling_callback(
    self, context: RequestContext, params: CreateMessageRequestParams
) -> types.CreateMessageResult:
    print("\n[MCP SAMPLING CALLBACK] Received sampling request from MCP server...")
    ...
    print(f"[MCP SAMPLING CALLBACK] Completed sampling response using model '{model_name}'.")
```

### 2. Triggering the Tool via Prompting
When chatting with the LLM in a CLI environment, the model decides dynamically whether to execute a tool or answer directly using its own capabilities:

- **Implicit Prompt**: `"summarize the following text..."`
  - The client LLM may generate a summary directly (`stop_reason == "end_turn"`). No tool is called, and `sampling_callback` will **not** run.
- **Explicit Prompt**: `"Use the summarize tool to summarize the text..."`
  - Forces the client LLM to invoke the tool (`stop_reason == "tool_use"`). The server runs `summarize()`, which sends a `sampling/createMessage` request back to `mcp_client.py` and triggers `sampling_callback`.
```