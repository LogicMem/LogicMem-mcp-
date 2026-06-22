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

Tier availability:
    - Free tier (mk_* keys): log, recall, reason, audit, A2A — all work.
    - Pro tier (lm_* keys): log, recall, reason, audit, A2A + verify, reflect,
      intelligence. Methods `verify()`, `reflect()`, `intelligence()` on a
      free-tier key raise `NotImplementedError` directing you to upgrade.

Resilience:
    - Embedding calls run server-side via a 3-tier fallback chain
      (Cohere → Ollama local → TF-IDF). See docs/EMBEDDING-FALLBACK.md.
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
