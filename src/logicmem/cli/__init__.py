#!/usr/bin/env python3
"""
LogicMem MCP Server — local stdio MCP server for OpenClaw and other MCP clients.

A small bridge between an MCP client (OpenClaw, Claude Code, etc.) and the
LogicMem REST API. It speaks MCP over stdin/stdout and serves logicmem_* tools.

Usage:
    logicmem-server                      # reads LOGICMEM_API_KEY from env
    logicmem-server --api-key lm_xxx     # or pass the key directly
    python -m logicmem.cli               # same thing, without the script
    logicmem-server --help

Environment:
    LOGICMEM_API_KEY     — your LogicMem API key (lm_...)
    LOGICMEM_SERVER_URL  — REST API URL (default: https://api.logicmem.io)
    LOGICMEM_CLIENT_ID   — default client_id (default: default)
    LOGICMEM_TIMEOUT     — HTTP timeout in seconds (default: 30)

Install:
    pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"

OpenClaw config (~/.openclaw/openclaw.json, under mcp.servers):
{
  "logicmem": {
    "command": "logicmem-server",
    "env": {
      "LOGICMEM_API_KEY": "lm_YOUR_API_KEY",
      "LOGICMEM_CLIENT_ID": "your-client-id"
    }
  }
}
"""

from __future__ import annotations

import json
import os
import sys
from urllib.parse import urlencode
from typing import Any

from logicmem import __version__

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False


# ── Config ─────────────────────────────────────────────────────────────────────

API_KEY = os.getenv("LOGICMEM_API_KEY", os.getenv("MEMORY_API_KEY", ""))
SERVER_URL = os.getenv("LOGICMEM_SERVER_URL", "https://api.logicmem.io").rstrip("/")
CLIENT_ID = os.getenv("LOGICMEM_CLIENT_ID", "default")
TIMEOUT = float(os.getenv("LOGICMEM_TIMEOUT", "30"))


# ── HTTP Client ───────────────────────────────────────────────────────────────

class MemoryClient:
    """HTTP client for LogicMem REST API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def post(self, path: str, body: dict, params: dict | None = None) -> Any:
        if params:
            path = f"{path}?{urlencode(params)}"
        if not _HAS_HTTPX:
            import urllib.request, urllib.error
            url = f"{self.base_url}{path}"
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                url, data=data, headers=self._headers(), method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                body_text = e.read().decode() if e.fp else ""
                raise Exception(f"API {e.code}: {body_text}")
        else:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}{path}",
                    json=body,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        if params:
            path = f"{path}?{urlencode(params)}"
        if not _HAS_HTTPX:
            import urllib.request
            url = f"{self.base_url}{path}"
            req = urllib.request.Request(url, headers=self._headers(), method="GET")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        else:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}{path}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                return resp.json()


_client = MemoryClient(SERVER_URL, API_KEY, TIMEOUT)


# ── Tool Definitions ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "logicmem_memory_log",
        "description": (
            "Store a new memory. The agent's memory is permanent and searchable "
            "across sessions. Be specific — include who, what, when, why."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text":       {"type": "string", "description": "What to remember."},
                "category":   {"type": "string", "description": "general | client_identity | decision | preference | contract | correction | interaction | complaint", "default": "general"},
                "importance": {"type": "number", "description": "1-10 importance", "default": 7},
                "tags":       {"type": "array",  "items": {"type": "string"}, "description": "Optional tags"},
                "client_id":  {"type": "string", "description": "Client ID"},
                "source":     {"type": "string", "description": "voice_call | chat | email | meeting | document | manual | system", "default": "openclaw-mcp"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "logicmem_memory_recall",
        "description": "Search memory for relevant entries.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query":    {"type": "string", "description": "Search query"},
                "limit":    {"type": "number", "description": "Max entries", "default": 5},
                "client_id": {"type": "string", "description": "Client ID"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "logicmem_memory_session",
        "description": "Full memory session briefing — recall + sentiment + constraints + intelligence + gaps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client ID"},
            },
        },
    },
    {
        "name": "logicmem_memory_stats",
        "description": "Get memory system stats — total entries, categories, storage.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "logicmem_memory_health",
        "description": "Check if the LogicMem memory server is healthy.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "logicmem_memory_outcome",
        "description": "Record how useful a stored memory was (score) for a given entry_id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entry_id": {"type": "string", "description": "Entry ID from recall results"},
                "score":    {"type": "number", "description": "Usefulness score"},
            },
            "required": ["entry_id", "score"],
        },
    },
    {
        "name": "logicmem_a2a_register",
        "description": "Register this agent in the A2A registry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id":   {"type": "string"},
                "client_id":  {"type": "string"},
                "name":       {"type": "string"},
                "agent_type": {"type": "string"},
            },
            "required": ["agent_id", "client_id"],
        },
    },
    {
        "name": "logicmem_a2a_heartbeat",
        "description": "Send a heartbeat to the A2A registry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id":  {"type": "string"},
                "client_id": {"type": "string"},
                "status":    {"type": "string"},
            },
            "required": ["agent_id", "client_id"],
        },
    },
    {
        "name": "logicmem_a2a_list_agents",
        "description": "List all registered agents for a client_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"client_id": {"type": "string"}},
            "required": ["client_id"],
        },
    },
    {
        "name": "logicmem_a2a_write_shared",
        "description": "Write a memory to the shared A2A pool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id":   {"type": "string"},
                "client_id":  {"type": "string"},
                "text":       {"type": "string"},
                "category":    {"type": "string"},
                "importance": {"type": "number"},
                "is_private": {"type": "boolean"},
                "tags":       {"type": "array", "items": {"type": "string"}},
            },
            "required": ["agent_id", "client_id", "text"],
        },
    },
    {
        "name": "logicmem_a2a_sync",
        "description": "Get shared memories for this agent (optionally since a timestamp).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id":      {"type": "string"},
                "client_id":     {"type": "string"},
                "since_timestamp": {"type": "string"},
                "limit":         {"type": "number"},
            },
            "required": ["agent_id", "client_id"],
        },
    },
]


# ── Tool Executor ─────────────────────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> Any:
    args = dict(args or {})
    client_id = args.pop("client_id", None) or CLIENT_ID

    if name == "logicmem_memory_log":
        return _client.post("/memory/log", {**args, "client_id": client_id})

    elif name == "logicmem_memory_recall":
        return _client.post("/memory/recall", {**args, "client_id": client_id})

    elif name == "logicmem_memory_session":
        return _client.post("/memory/session", {"client_id": client_id})

    elif name == "logicmem_memory_outcome":
        return _client.post("/memory/outcome", args)

    elif name == "logicmem_memory_stats":
        return _client.get("/memory/stats")

    elif name == "logicmem_memory_health":
        try:
            result = _client.get("/memory/health")
            return {"status": "healthy", "server": SERVER_URL, "data": result}
        except Exception as e:
            return {"status": "unhealthy", "server": SERVER_URL, "error": str(e)}

    elif name == "logicmem_a2a_register":
        body = {**args, "client_id": client_id}
        body.setdefault("name", body.get("agent_id", ""))
        return _client.post("/memory/agent/register", body)

    elif name == "logicmem_a2a_heartbeat":
        # The server reads heartbeat fields from the query string.
        return _client.post("/memory/agent/heartbeat", {}, params={
            "client_id": client_id,
            "agent_id": args["agent_id"],
            "status": args.get("status", "online"),
        })

    elif name == "logicmem_a2a_list_agents":
        return _client.get("/memory/org/agents", {"client_id": client_id})

    elif name == "logicmem_a2a_write_shared":
        return _client.post("/memory/shared/write", {**args, "client_id": client_id})

    elif name == "logicmem_a2a_sync":
        params = {"client_id": client_id, "agent_id": args["agent_id"]}
        if args.get("since_timestamp"):
            params["since_timestamp"] = args["since_timestamp"]
        if args.get("limit"):
            params["limit"] = int(args["limit"])
        return _client.get("/memory/shared/updates", params)

    else:
        raise ValueError(f"Unknown tool: {name}")


# ── MCP JSON-RPC Handlers ─────────────────────────────────────────────────────

def handle_initialize(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "logicmem",
                "version": __version__,
            },
            "instructions": (
                "LogicMem — tamper-evident records of what your AI agents did. "
                "Use logicmem_memory_log to store important facts, "
                "logicmem_memory_recall to retrieve them. "
                "Also supports A2A shared memory for multi-agent systems."
            ),
        },
    }


def handle_list_tools(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"tools": TOOLS},
    }


def handle_call_tool(req_id, name, args):
    try:
        result = execute_tool(name, args)
        text = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": False,
            },
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True,
            },
        }


# ── Stdin/Stdout Protocol ─────────────────────────────────────────────────────

def read_request():
    """Read one JSON-RPC request line from stdin."""
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)


def send_response(resp: dict):
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def _main():
    # Send initial server capabilities
    sys.stderr.write(
        "[logicmem] MCP server starting — "
        f"server={SERVER_URL} client_id={CLIENT_ID}\n"
    )
    sys.stderr.flush()

    while True:
        try:
            req = read_request()
        except (EOFError, ValueError, json.JSONDecodeError):
            break

        method = req.get("method", "")
        req_id = req.get("id")

        if method == "initialize":
            send_response(handle_initialize(req_id))
        elif method == "tools/list":
            send_response(handle_list_tools(req_id))
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {})
            send_response(handle_call_tool(req_id, name, args))
        elif method == "notifications/initialized":
            pass  # Acknowledge and continue
        else:
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"},
            })


def main(argv: list[str] | None = None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="logicmem-server",
        description=(
            "Local stdio MCP server for LogicMem. Speaks MCP (JSON-RPC, one "
            "message per line) on stdin/stdout and forwards logicmem_* tool "
            "calls to the LogicMem REST API. Normally started by your MCP "
            "client, not by hand."
        ),
        epilog="API keys are issued to pilot teams: https://logicmem.io/design-partner/",
    )
    parser.add_argument("--api-key", help="LogicMem API key (default: $LOGICMEM_API_KEY)")
    parser.add_argument("--server-url", help="REST API URL (default: $LOGICMEM_SERVER_URL or https://api.logicmem.io)")
    parser.add_argument("--client-id", help="Default client_id (default: $LOGICMEM_CLIENT_ID or 'default')")
    parser.add_argument("--version", action="version", version=f"logicmem {__version__}")
    opts = parser.parse_args(argv)

    global _client, SERVER_URL, CLIENT_ID
    if opts.server_url:
        SERVER_URL = opts.server_url.rstrip("/")
    if opts.client_id:
        CLIENT_ID = opts.client_id
    _client = MemoryClient(SERVER_URL, opts.api_key or API_KEY, TIMEOUT)
    if not _client.api_key:
        sys.stderr.write("[logicmem] warning: no API key set (LOGICMEM_API_KEY or --api-key); tool calls will fail with 401.\n")
    _main()


if __name__ == "__main__":
    main()
