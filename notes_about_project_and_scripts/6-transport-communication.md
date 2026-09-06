## Transport and Communication
In this section, we will discuss the various ways in which messages are transported and communicated between the client and the server.

### MCP Messages Formats
- There are many types of messages, each designed to achieve particular goal (list tools, call tools and get resource etc ..,)
- Client and Server communicates using JSON-RPC 2.0 protocol.
- Here is the example for call tool request and response
  - Call Tool Request
    ```json
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "add", "arguments": {"a": 4, "b": 6}
        }
    }
    ```
  - Call Tool Response
    ```json
    {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "10"}]
            "isError": false,  
        }
    }
    ```
- There are two types of messages, "Request-Result" Messages and
  "Notification" Messages
  - Request-Result Messages:
    - These messages are sent from the client to the server and have a corresponding response message.
    - For example:
      - Call Tool Request <--> Call Tool Result
      - List Tools Request <--> List Tools Result
      - List Contexts Request <--> List Contexts Result
      - Create Context Request <--> Create Context Result
      - Update Context Request <--> Update Context Result
      - Delete Context Request <--> Delete Context Result
      - List Resources Request <--> List Resources Result
      - Get Resource Request <--> Get Resource Result
  - Notification Messages
    - Messages types where we are informing the client and server about some event but don't need a response.
    - For example
      - Progress Notifications
      - Logging Message Notifications
      - Tool List Changed Notifications
      - Resource Update Notification

- All the Message (Note: Not in a json format but in a ts format): https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/schema/draft/schema.ts
    
