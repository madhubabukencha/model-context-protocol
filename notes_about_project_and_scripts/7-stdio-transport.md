# Stdio Transport in MCP
- The **client spawns the MCP server as a child process** (e.g., using `subprocess` in Python or `child_process` in Node.js). The server's lifecycle is fully managed by the client.
- The client communicates with the server by writing **JSON-RPC messages to the server's `stdin`** stream.
- The server processes requests and sends responses back by writing to its **`stdout`** stream. Each message is a single line of JSON terminated by a newline (`\n`).
- **Communication is bidirectional and asynchronous** — either side can send a message at any time (requests, responses, or notifications), making it a full-duplex channel over two half-duplex pipes.
- **`stderr` is reserved for logging/diagnostics** — servers must never write protocol messages to `stderr`; it is used solely for human-readable logs and debug output.
- This transport is **only suitable when both client and server run on the same machine**, since it relies on OS-level process pipes rather than a network connection.