"""
Audit Chain Tools
=================
Tamper-evident audit trail verification for LogicMem.
Key memory operations are logged to a cryptographically linked hash chain.
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
        Verify the integrity of the entire audit chain.

        Asks the server to re-check the hash links in the audit chain, so
        an edited, deleted or reordered entry shows up as a broken link.

        Returns:
            dict from the server describing whether the chain is intact.
            Print it or read fields with ``.get()``; exact field names are
            set by the server.
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

        Corrections are stored on the server and queued for its DPO
        training pipeline.

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