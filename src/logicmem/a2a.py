"""
A2A — Agent-to-Agent Memory Sharing
====================================
Memory sharing between AI agents through the LogicMem server.

Use this module when building multi-agent systems where agents need
to share context without a central orchestrator.
"""

from __future__ import annotations

from typing import Any, Literal

from logicmem.exceptions import ValidationError


class A2AClient:
    """
    Agent-to-Agent (A2A) client for memory sharing.

    Register your agent in the registry, write shared memories, and poll
    for memories other agents shared.

    Args:
        api_key: Your LogicMem API key.
        agent_id: Unique identifier for this agent (e.g., "claude-agent").
        base_url: Base URL of the LogicMem REST API.
                  Defaults to https://api.logicmem.io.
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: str = "https://api.logicmem.io",
    ):
        if not agent_id:
            raise ValidationError("agent_id is required for A2A")
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = base_url.rstrip("/")

    # -------------------------------------------------------------------------
    # Registry Operations
    # -------------------------------------------------------------------------

    def register(
        self,
        name: str = "",
        agent_type: str = "agent",
        client_id: str = "default",
    ) -> dict[str, Any]:
        """
        Register this agent in the LogicMem agent registry.

        Other agents in the same ``client_id`` can discover and communicate
        with this agent after registration.

        Args:
            name: Human-readable agent name.
            agent_type: Type of agent (e.g., "agent", "assistant", "workflow").
            client_id: Organization/client ID for agent grouping.

        Returns:
            dict from the server.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        return client._post("/memory/agent/register", {
            "agent_id": self.agent_id,
            "name": name or self.agent_id,
            "agent_type": agent_type,
            "client_id": client_id,
        })

    def list_agents(self, client_id: str = "default") -> list[dict[str, Any]]:
        """
        List all registered agents for a client_id.

        Args:
            client_id: Organization/client ID to filter by.

        Returns:
            List of agent records with ``agent_id``, ``name``,
            ``agent_type``, and ``status``.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        # /memory/org/agents is a GET endpoint with client_id as a query param.
        result = client._get("/memory/org/agents", {"client_id": client_id})
        if isinstance(result, list):
            return result
        return result.get("agents", [])

    def heartbeat(self, status: str = "online", client_id: str = "default") -> dict[str, Any]:
        """
        Send a heartbeat to the A2A registry.

        Signals that this agent is alive. Call periodically to maintain
        presence in the registry.

        Args:
            status: Agent status — "online", "busy", or "away".

            client_id: Client/organization ID. Defaults to "default".

        Returns:
            dict from the server.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        # /memory/agent/heartbeat is POST with client_id, agent_id, status
        # all in the QUERY STRING (not the body). The agent must be
        # registered first via ``register()``.
        return client._post_with_query(
            "/memory/agent/heartbeat",
            {
                "client_id": client_id,
                "agent_id": self.agent_id,
                "status": status,
            },
        )

    # -------------------------------------------------------------------------
    # Memory Sharing
    # -------------------------------------------------------------------------

    def share_memory(
        self,
        target_agent_id: str,
        memory: dict[str, Any],
        category: str = "general",
        importance: int = 7,
        is_private: bool = False,
        tags: list[str] | None = None,
        client_id: str = "default",
    ) -> dict[str, Any]:
        """
        Share a memory entry with another agent.

        The target agent can retrieve shared memories via ``receive_memory()``.

        Args:
            target_agent_id: The recipient agent's ID.
            memory: The memory content to share (at minimum, a ``text`` key).
                    ``category`` and ``importance`` keys in this dict are
                    used when present.
            category: Category of the shared memory. Defaults to "general".
            importance: Importance level 1-10. Defaults to 7.
            is_private: If True, only the target agent can see this memory.
            tags: Optional tags for the shared memory.
            client_id: Client/organization ID. Defaults to "default".

        Returns:
            dict from the server.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)

        payload = {
            "agent_id": self.agent_id,
            "target_agent_id": target_agent_id,
            "text": memory.get("text", str(memory)),
            "category": memory.get("category", category),
            "importance": memory.get("importance", importance),
            "is_private": is_private,
            "client_id": client_id,
        }
        if tags:
            payload["tags"] = tags

        return client._post("/memory/shared/write", payload)

    def receive_memory(
        self,
        client_id: str = "default",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retrieve memories shared with this agent by other agents.

        Args:
            client_id: Client/organization ID. Defaults to "default".
            limit: Maximum number of shared memories to return.

        Returns:
            List of shared memory entries (dicts from the server).
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        # /memory/shared/updates is a GET endpoint on the server.
        result = client._get("/memory/shared/updates", {
            "agent_id": self.agent_id,
            "client_id": client_id,
            "limit": limit,
        })
        if isinstance(result, list):
            return result
        return result.get("entries", [])

    def sync(
        self,
        since_timestamp: str = "",
        client_id: str = "default",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Return shared memories from OTHER agents, optionally since a time.

        Reads the same shared-updates endpoint as ``receive_memory()`` and
        drops entries written by this agent. When ``since_timestamp`` is set,
        entries whose timestamp is older are dropped too.

        Args:
            since_timestamp: ISO 8601 timestamp of your last sync. Omit for all.
            client_id: Client/organization ID. Defaults to "default".
            limit: Maximum number of entries to fetch. Defaults to 50.

        Returns:
            List of shared memory entries (dicts from the server).
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        params: dict[str, Any] = {
            "agent_id": self.agent_id,
            "client_id": client_id,
            "limit": limit,
        }
        if since_timestamp:
            params["since_timestamp"] = since_timestamp
        result = client._get("/memory/shared/updates", params)
        entries = result if isinstance(result, list) else result.get("entries", [])
        out = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            author = e.get("from_agent_id") or e.get("agent_id")
            if author == self.agent_id:
                continue
            ts = e.get("shared_at") or e.get("created_at") or e.get("timestamp")
            if since_timestamp and isinstance(ts, str) and ts < since_timestamp:
                continue
            out.append(e)
        return out

    def write_shared(
        self,
        text: str,
        category: Literal["general", "a2a_discovery", "decision", "context"] = "general",
        importance: int = 7,
        is_private: bool = False,
        tags: list[str] | None = None,
        client_id: str = "default",
    ) -> dict[str, Any]:
        """
        Write a memory to the shared A2A pool.

        All agents in the same ``client_id`` can see non-private shared memories.

        Args:
            text: The memory text to share.
            category: Category for the shared memory.
            importance: Importance level 1-10.
            is_private: Sent to the server as the entry's private flag.
            tags: Optional tags.
            client_id: Client/organization ID.

        Returns:
            dict from the server.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        payload = {
            "agent_id": self.agent_id,
            "text": text,
            "category": category,
            "importance": importance,
            "is_private": is_private,
            "client_id": client_id,
        }
        if tags:
            payload["tags"] = tags

        return client._post("/memory/shared/write", payload)

    def __repr__(self) -> str:
        return f"A2AClient(agent_id={self.agent_id!r})"
