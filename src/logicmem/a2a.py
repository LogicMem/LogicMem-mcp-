"""
A2A — Agent-to-Agent Memory Sharing
====================================
Real-time memory sharing between AI agents via the A2A protocol.

Use this module when building multi-agent systems where agents need
to share context without a central orchestrator.
"""

from __future__ import annotations

from typing import Any, Literal

from logicmem.exceptions import ValidationError


class A2AClient:
    """
    Agent-to-Agent (A2A) client for real-time memory sharing.

    Register your agent in the A2A registry and share memories
    with other agents in real-time.

    Args:
        api_key: Your LogicMem API key.
        agent_id: Unique identifier for this agent (e.g., "claude-agent").
        base_url: Base URL of the A2A relay server.
                  Defaults to the production server.
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
            dict with ``agent_id``, ``registered_at``, and ``endpoint``.
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

        Returns:
            dict with ``acknowledged`` and ``server_time``.
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
        Share a memory entry with another agent in real-time.

        The target agent can retrieve shared memories via ``receive_memory()``.

        Args:
            target_agent_id: The recipient agent's ID.
            memory: The memory content to share (at minimum, ``text`` key).
            category: Category of the shared memory. Defaults to "general".
            importance: Importance level 1-10. Defaults to 7.
            is_private: If True, only the target agent can see this memory.
            tags: Optional tags for the shared memory.
            client_id: Client/organization ID. Defaults to "default".

        Returns:
            dict with ``share_id``, ``shared_at``, and ``delivered``.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)

        payload = {
            "agent_id": self.agent_id,
            "target_agent_id": target_agent_id,
            "text": memory.get("text", str(memory)),
            "category": category,
            "importance": importance,
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
            List of shared memory entries with ``share_id``, ``from_agent_id``,
            ``text``, ``shared_at``.
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

    def sync(self, since_timestamp: str = "") -> list[dict[str, Any]]:
        """
        Check for new shared memories from OTHER agents since last sync.

        Excludes memories shared by this agent (avoiding echo).

        Args:
            since_timestamp: ISO timestamp of last sync. Omit for all entries.

        Returns:
            List of new shared memory entries.
        """
        from logicmem.client import LogicMem
        client = LogicMem(api_key=self.api_key, base_url=self.base_url)
        payload = {
            "agent_id": self.agent_id,
            "since_timestamp": since_timestamp,
        }
        result = client._post("/memory/federation/query", payload)
        if isinstance(result, list):
            return result
        return result.get("entries", [])

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
            is_private: If True, only visible to this agent.
            tags: Optional tags.
            client_id: Client/organization ID.

        Returns:
            dict with ``entry_id`` and ``shared_at``.
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
