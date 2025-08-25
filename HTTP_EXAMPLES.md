# Garth MCP Server - HTTP Mode Examples

## Starting the HTTP Server

```bash
# Basic HTTP server
garth-mcp-server --http

# Custom host and port
garth-mcp-server --http --host 127.0.0.1 --port 3000

# For production (accessible from other machines)
garth-mcp-server --http --host 0.0.0.0 --port 8000
```

## n8n MCP Client Configuration

In n8n MCP Client node:

1. **Server URL**: `http://your-server-ip:8000/`
2. **Authentication Type**: `Bearer`
3. **Token**: Your Garth token (output of `garth login`)

## HTTP API Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "server": "Garth MCP Server", 
  "version": "0.0.8",
  "authentication": "Bearer token required"
}
```

### 2. List Available Tools
```bash
curl -H "Authorization: Bearer <your_garth_token>" \
     http://localhost:8000/tools
```

Response:
```json
{
  "tools": [
    {"name": "user_profile", "description": "Get user profile information"},
    {"name": "daily_steps", "description": "Get daily steps data"},
    {"name": "get_activities", "description": "Get activities from Garmin Connect"}
  ],
  "count": 3
}
```

### 3. Execute Tools
```bash
# Get user profile
curl -H "Authorization: Bearer <your_garth_token>" \
     -H "Content-Type: application/json" \
     -d '{"tool": "user_profile", "arguments": {}}' \
     http://localhost:8000/

# Get daily steps
curl -H "Authorization: Bearer <your_garth_token>" \
     -H "Content-Type: application/json" \
     -d '{"tool": "daily_steps", "arguments": {"days": 7}}' \
     http://localhost:8000/

# Get activities
curl -H "Authorization: Bearer <your_garth_token>" \
     -H "Content-Type: application/json" \
     -d '{"tool": "get_activities", "arguments": {"limit": 10}}' \
     http://localhost:8000/
```

## Security Notes

- Always use HTTPS in production
- Keep your Garth token secure
- Consider running behind a reverse proxy with rate limiting
- The server binds to 0.0.0.0 by default - restrict access as needed

## Backward Compatibility

The server still supports the original stdio mode:

```bash
# Original stdio mode (default)
garth-mcp-server

# With environment variable
GARTH_TOKEN="your_token" garth-mcp-server
```