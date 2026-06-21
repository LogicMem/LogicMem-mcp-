"""
LogicMem — AI Agent Memory Infrastructure
=========================================

Persistent memory, A2A sharing, reasoning engine, and immutable audit trail
for AI agents via the Model Context Protocol.

Usage:
    from logicmem import LogicMem

    memory = LogicMem(api_key="your-api-key")
    memory.log("User prefers Telegram for urgent messages", category="preference")
    results = memory.recall("user communication preferences")
"""

from logicmem.client import LogicMem
from logicmem.exceptions import (
    LogicMemError,
    AuthenticationError,
    MemoryNotFoundError,
    RateLimitError,
    ServerError,
)

__version__ = "0.1.1"

__all__ = [
    "LogicMem",
    "LogicMemError",
    "AuthenticationError",
    "MemoryNotFoundError",
    "RateLimitError",
    "ServerError",
]
