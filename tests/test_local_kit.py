"""Offline checks for the public client kit. No network."""

from __future__ import annotations

import ast
import inspect
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("LOGICMEM_WEBHOOK_SECRET", "offline-test-not-a-credential")
os.environ.setdefault("THEMIS_CRON_SECRET", "offline-test-not-a-credential")

import importlib.util  # noqa: E402

import logicmem  # noqa: E402
from logicmem.a2a import A2AClient  # noqa: E402
from logicmem.audit import AuditChain  # noqa: E402
from logicmem.client import LogicMem  # noqa: E402
from logicmem.memory import MemoryTools  # noqa: E402
from logicmem.reasoning import ReasoningEngine  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "webhook_dispatcher", ROOT / "webhooks" / "dispatcher.py"
)
dispatcher = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dispatcher)


def test_version_matches_pyproject():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.1.2"' in text
    assert logicmem.__version__ == "0.1.2"


def test_unimplemented_rest_methods_raise():
    client = LogicMem(api_key="lm_offline_test")
    calls = (
        (client.verify, ("claim",)),
        (client.reflect, ("draft", "question")),
        (client.intelligence, ()),
    )
    for method, args in calls:
        try:
            method(*args)
        except NotImplementedError:
            continue
        raise AssertionError(method)
    engine = ReasoningEngine(client)
    try:
        engine.confidence("q", "a")
        raise AssertionError("confidence")
    except NotImplementedError:
        pass
    try:
        engine.trace("s")
        raise AssertionError("trace")
    except NotImplementedError:
        pass


def test_stats_uses_get_not_post():
    class Fake:
        def __init__(self):
            self.calls = []

        def _get(self, path, params=None):
            self.calls.append(("GET", path, params))
            return {"status": "ok"}

        def _post(self, path, payload):
            self.calls.append(("POST", path, payload))
            return {"status": "ok"}

    fake = Fake()
    assert MemoryTools(fake).stats() == {"status": "ok"}
    assert fake.calls == [("GET", "/memory/stats", None)]


def test_defaults_are_scoped_and_sync_does_not_page():
    assert inspect.signature(LogicMem.log).parameters["client_id"].default == "default"
    params = inspect.signature(A2AClient.sync).parameters
    assert params["limit"].default == 50
    assert "offset" not in params
    assert "cursor" not in params
    text = inspect.getsource(A2AClient.sync)
    assert "total_new" not in text.split("return out")[-1]


def test_dispatcher_contract_is_the_file_not_a_guarantee():
    assert dispatcher.MAX_ATTEMPTS == 5
    assert dispatcher.INITIAL_BACKOFF_SEC == 2
    assert dispatcher.MAX_BACKOFF_SEC == 300
    doc = dispatcher.__doc__ or ""
    assert "doesn't lose" not in doc.lower()
    assert "does not" in doc.lower() or "not " in doc.lower()
    assert "12 attempts" in doc


def test_help_commands_exit_zero():
    for cmd in (
        [sys.executable, "-m", "logicmem.cli", "--help"],
        [sys.executable, "-m", "logicmem.cli", "--version"],
    ):
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
        assert "logicmem" in (result.stdout + result.stderr).lower()


def test_no_real_tenant_string_outside_the_changelog_note():
    needle = "ed_creed"
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "__pycache__", "artifacts"} for part in path.parts):
            continue
        if path.suffix not in {".py", ".md", ".toml"}:
            continue
        if path.name in {"CHANGELOG.md", "test_local_kit.py"}:
            continue
        if needle in path.read_text(encoding="utf-8"):
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_python_fences_parse():
    errors = []
    for path in (ROOT / "docs").rglob("*.md"):
        errors.extend(_parse_fences(path))
    errors.extend(_parse_fences(ROOT / "README.md"))
    assert errors == []


def test_relative_links_and_anchors():
    errors = []
    for path in list((ROOT / "docs").rglob("*.md")) + [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md"]:
        text = path.read_text(encoding="utf-8")
        headings = _heading_slugs(text)
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part, _, fragment = target.partition("#")
            if path_part:
                dest = (path.parent / path_part).resolve()
                if not dest.is_file():
                    errors.append(f"{path.name}: missing {target}")
                    continue
                if fragment and fragment not in _heading_slugs(dest.read_text(encoding="utf-8")):
                    errors.append(f"{path.name}: bad fragment {target}")
            elif fragment and fragment not in headings:
                errors.append(f"{path.name}: bad self fragment #{fragment}")
    assert errors == []


def _parse_fences(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    for idx, body in enumerate(re.findall(r"```python\n(.*?)```", text, re.S), start=1):
        try:
            ast.parse(body)
        except SyntaxError as exc:
            errors.append(f"{path.name} fence {idx}: {exc}")
    return errors


def _heading_slugs(text: str) -> set[str]:
    slugs = set()
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        title = re.sub(r"^#+\s*", "", line).strip()
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
        slug = slug.replace("_", "")
        slug = re.sub(r"\s+", "-", slug.strip())
        slugs.add(slug)
    return slugs


def test_audit_verify_is_get():
    source = inspect.getsource(AuditChain.verify)
    assert "_get(" in source
    assert "/memory/audit/verify" in source
