"""
Audit Chain Tools
=================
Tamper-evident audit trail verification for LogicMem.
Some operations are written to hash-linked records kept on the server.
This client asks the server to re-check the entries it still holds.
"""

from __future__ import annotations

from typing import Any


class AuditChain:
    """
    Tools for verifying the integrity of the LogicMem audit chain.

    The audit chain is a tamper-evident, hash-linked ledger of memory
    operations. Use these tools to check whether the audit chain has
    been altered.
    """

    def __init__(self, client: Any):
        self._client = client

    def verify(self) -> dict[str, Any]:
        """
        Ask the server to re-check hash links among entries it still holds.

        A modified, deleted, or reordered past entry that is still in the
        set the server checks shows up as a broken link. This call does
        not recompute hashes locally, and it does not detect removal of
        the newest entries by itself. There is no separate anchoring
        export in this package.

        Returns:
            The server's JSON. Field names are set by the server. Read
            them with ``.get()``.
        """
        # /memory/audit/verify is a GET endpoint on the server.
        return self._client._get("/memory/audit/verify", {})

    def log_correction(
        self,
        original: str,
        corrected: str,
        reason: str = "",
    ) -> dict[str, Any]:
        """
        Log a correction (what the agent got wrong and what is right).

        The client POSTs ``original``, ``corrected`` and ``reason`` to
        ``/memory/correction/log``. These docs describe that as stored
        and queued for the server's DPO training pipeline. The training
        job, what text it consumes, tenant separation, retention and
        any opt-out are not in this repository and were not verified here.

        Args:
            original: The incorrect statement or action.
            corrected: The correct statement or action.
            reason: Why the correction was made.

        Returns:
            dict from the server.
        """
        payload = {
            "original": original,
            "corrected": corrected,
            "reason": reason,
        }
        return self._client._post("/memory/correction/log", payload)

    def dpo_stats(self) -> dict[str, Any]:
        """
        Get DPO training statistics.

        Returns how many correction pairs are ready for training
        and the health of the training pipeline.
        """
        return self._client._post("/memory/dpo/stats", {})

    def run_dpo(self) -> dict[str, Any]:
        """
        Trigger a DPO training run.

        Requires a minimum number of correction pairs (configurable on the
        server). Returns a status dict indicating whether training started.
        """
        return self._client._post("/memory/dpo/run", {})

    def health(self) -> dict[str, Any]:
        """
        Check the health of the audit chain subsystem.

        Returns:
            dict from the server.
        """
        # /memory/audit is a GET endpoint on the server.
        return self._client._get("/memory/audit", {})