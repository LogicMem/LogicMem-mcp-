"""
LogicMem — prove what your AI did
=================================

Python SDK and MCP connector for LogicMem: tamper-evident, hash-chained
records of what your AI agents did, plus memory, A2A sharing and reasoning.

Usage:
    from logicmem import LogicMem

    memory = LogicMem(api_key="your-api-key")
    memory.log("User prefers Telegram for urgent messages", category="preference")
    results = memory.recall("user communication preferences")

What the SDK covers:
    - log, recall, session, reason, health, the audit chain and A2A sharing
      go to the LogicMem REST API (https://api.logicmem.io).
    - verify(), reflect() and intelligence() always raise
      NotImplementedError: those run only as logicframe_verify,
      logicframe_reflect and logicframe_intelligence tools on the hosted
      MCP server at https://mcp.logicmem.io/mcp.

API keys (lm_...) are issued to pilot teams: https://logicmem.io/design-partner/
"""

from logicmem.client import LogicMem
from logicmem.exceptions import (
    LogicMemError,
    AuthenticationError,
    MemoryNotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    NetworkError,
)

__version__ = "0.1.2"

__all__ = [
    "LogicMem",
    "LogicMemError",
    "AuthenticationError",
    "MemoryNotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "NetworkError",
]
