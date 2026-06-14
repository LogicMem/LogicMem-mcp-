"""
Memory Tools
============
Direct memory operation wrappers for advanced use cases.
These are also available on the main :class:`LogicMem` client.
"""

from __future__ import annotations

from typing import Any


class MemoryTools:
    """
    Low-level memory tool wrappers.

    In most cases, use the methods on :class:`logicmem.LogicMem` directly.
    This class exposes the same operations with slightly different
    ergonomics for advanced use.
    """

    def __init__(self, client: Any):
        self._client = client

    def log(
        self,
        text: str,
        category: str = "general",
        importance: int = 7,
        client_id: str = "default",
        tags: list[str] | None = None,
        source: str = "sdk",
    ) -> dict[str, Any]:
        """
        Store a memory. Alias for :meth:`LogicMem.log`.
        """
        return self._client.log(
            text=text,
            category=category,
            importance=importance,
            client_id=client_id,
            tags=tags,
            source=source,
        )

    def recall(
        self,
        query: str,
        limit: int = 5,
        client_id: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Search memories. Alias for :meth:`LogicMem.recall`.
        """
        return self._client.recall(
            query=query,
            limit=limit,
            client_id=client_id,
        )

    def session(self, client_id: str = "default") -> dict[str, Any]:
        """
        Get session context briefing. Alias for :meth:`LogicMem.session`.
        """
        return self._client.session(client_id=client_id)

    def stats(self) -> dict[str, Any]:
        """
        Get memory system statistics.

        Returns total entries, category breakdown, and storage usage.
        """
        return self._client._post("/memory/stats", {})

    def health(self) -> dict[str, Any]:
        """
        Check memory server health. Alias for :meth:`LogicMem.health`.
        """
        return self._client.health()
