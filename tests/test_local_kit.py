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
        result = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True, check=False
        )
        assert result.returncode == 0, result.stderr
        assert "logicmem" in (result.stdout + result.stderr).lower()


def test_no_real_tenant_string_outside_the_changelog_note():
    needle = "ed_creed"
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        skip = {".git", ".venv", "__pycache__", "artifacts"}
        if any(part in skip for part in path.parts):
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
    pages = list((ROOT / "docs").rglob("*.md"))
    pages += [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md"]
    for path in pages:
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
                slug = fragment
                dest_slugs = _heading_slugs(dest.read_text(encoding="utf-8"))
                if slug and slug not in dest_slugs:
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


def test_share_memory_argument_shapes():
    """category/importance may be arguments or keys inside memory. Keys win."""
    from logicmem.a2a import A2AClient

    sent = []

    class Stub(LogicMem):
        def __init__(self):
            pass

        def _post(self, path, payload):
            sent.append((path, payload))
            return {"ok": True}

    client = A2AClient(api_key="lm_offline", agent_id="agent-researcher")
    client.api_key = "lm_offline"

    def factory(*_a, **_k):
        return Stub()

    import logicmem.client as client_mod
    original = client_mod.LogicMem
    client_mod.LogicMem = factory
    try:
        client.share_memory(
            target_agent_id="agent-executor",
            memory={"text": "from-args"},
            category="task",
            importance=9,
            client_id="demo-tenant",
        )
        client.share_memory(
            target_agent_id="agent-executor",
            memory={"text": "inside", "category": "decision", "importance": 3},
            category="task",
            importance=9,
            client_id="demo-tenant",
        )
        client.share_memory(
            target_agent_id="agent-executor",
            memory={"text": "mixed", "category": "note"},
            importance=4,
            client_id="demo-tenant",
        )
    finally:
        client_mod.LogicMem = original

    assert sent[0][1]["category"] == "task" and sent[0][1]["importance"] == 9
    assert sent[1][1]["category"] == "decision" and sent[1][1]["importance"] == 3
    assert sent[2][1]["category"] == "note" and sent[2][1]["importance"] == 4
    assert all(row[1]["text"] for row in sent)


def test_urllib_fallback_does_not_set_user_agent_before_stdlib():
    import urllib.error
    import urllib.request

    from logicmem.cli import MemoryClient

    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["pre_ua"] = req.get_header("User-agent")
        opener = urllib.request.build_opener()
        captured["opener_ua"] = dict(opener.addheaders).get("User-agent")
        raise urllib.error.URLError("offline-stop")

    original = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    try:
        client = MemoryClient("http://127.0.0.1", "lm_offline", timeout=1)
        # Force the urllib branch even if httpx is installed in this venv.
        import logicmem.cli as cli_mod
        previous = cli_mod._HAS_HTTPX
        cli_mod._HAS_HTTPX = False
        try:
            client.get("/memory/health")
        except Exception as exc:
            assert "offline-stop" in str(exc)
        finally:
            cli_mod._HAS_HTTPX = previous
    finally:
        urllib.request.urlopen = original

    assert captured["pre_ua"] is None
    assert str(captured["opener_ua"]).startswith("Python-urllib/")


def test_audit_verify_is_get():
    source = inspect.getsource(AuditChain.verify)
    assert "_get(" in source
    assert "/memory/audit/verify" in source
