#!/usr/bin/env python3
"""
LogicMem MCP Server — Local stdio MCP server for OpenClaw and other MCP clients.

This module provides a local MCP server that acts as a bridge between MCP clients
(OpenClaw, Claude Code, etc.) and the LogicMem cloud API or a self-hosted
LogicMem Open server.

Usage:
    # Via pip-installed CLI
    logicmem-server --api-key YOUR_KEY

    # Via OpenClaw MCP config
    openclaw mcp add logicmem -- python3 -m logicmem.server

Environment:
    LOGICMEM_API_KEY     — your LogicMem API key (Bearer lm_xxx)
    LOGICMEM_SERVER_URL  — memory server URL (default: https://api.logicmem.io)
    LOGICMEM_CLIENT_ID   — default client_id (default: default)

Install:
    pip install logicmem

For OpenClaw users: add this to your openclaw.json mcp.servers section:
{
  "logicmem": {
    "command": "python3",
    "args": ["-m", "logicmem.server"],
    "env": {
      "LOGICMEM_API_KEY": "your-lm_xxx-key",
      "LOGICMEM_CLIENT_ID": "your-client-id"
    }
  }
}
"""

from __future__ import annotations

import json
import os
import sys
import threading
from typing import Any

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

    def post(self, path: str, body: dict) -> Any:
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

    def get(self, path: str) -> Any:
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
        "description": "Record whether a stored memory was useful. Feeds the DPO training pipeline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_ids": {"type": "array", "items": {"type": "string"}},
                "success":    {"type": "boolean"},
                "magnitude":  {"type": "number", "default": 0.5},
            },
            "required": ["memory_ids", "success"],
        },
    },
    {
        "name": "logicmem_memory_reflect",
        "description": "Self-critique: evaluate a draft answer against retrieved memories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "draft_answer": {"type": "string"},
                "question":     {"type": "string"},
                "memory_query": {"type": "string"},
            },
            "required": ["draft_answer", "question"],
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
        "description": "Check for new shared memories from other agents since last sync.",
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
    client_id = args.pop("client_id", CLIENT_ID)

    if name == "logicmem_memory_log":
        return _client.post("/memory/log", {**args, "client_id": client_id})

    elif name == "logicmem_memory_recall":
        return _client.post("/memory/recall", {**args, "client_id": client_id})

    elif name == "logicmem_memory_session":
        return _client.post("/memory/session", {"client_id": client_id})

    elif name == "logicmem_memory_outcome":
        return _client.post("/memory/outcome", args)

    elif name == "logicmem_memory_stats":
        return _client.post("/memory/stats", {})

    elif name == "logicmem_memory_health":
        try:
            result = _client.get("/memory/health")
            return {"status": "healthy", "server": SERVER_URL, "data": result}
        except Exception as e:
            return {"status": "unhealthy", "server": SERVER_URL, "error": str(e)}

    elif name == "logicmem_memory_reflect":
        return _client.post("/memory/reflect", {**args, "client_id": client_id})

    elif name == "logicmem_a2a_register":
        return _client.post("/memory/agent/register", args)

    elif name == "logicmem_a2a_heartbeat":
        return _client.post("/memory/agent/heartbeat", args)

    elif name == "logicmem_a2a_list_agents":
        return _client.get(f"/memory/agents?client_id={args['client_id']}")

    elif name == "logicmem_a2a_write_shared":
        return _client.post("/memory/shared/write", args)

    elif name == "logicmem_a2a_sync":
        params = f"client_id={args['client_id']}&agent_id={args['agent_id']}"
        if args.get("since_timestamp"):
            params += f"&since_timestamp={args['since_timestamp']}"
        return _client.get(f"/memory/shared/updates?{params}")

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
                "version": "1.0.0",
            },
            "instructions": (
                "LogicMem — persistent memory for AI agents. "
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


def main():
    _main()


if __name__ == "__main__":
    main()
