# Contributing to LogicMem MCP

Thank you for your interest in contributing to LogicMem MCP.

## How to Contribute

1. **Fork the repo** and create your branch from `main`.
2. **Clone your fork.** SSH: `git clone git@github.com:your-username/LogicMem-mcp-.git`. HTTPS: `git clone https://github.com/your-username/LogicMem-mcp-.git`.
3. **Install for development:** `pip install -e ".[dev]"`. That extra already includes `httpx`, pytest, and the other dev tools. The `logicmem-server` console script is part of the base package, so this one install is enough for the checks in the next step. The `cli` extra also installs `httpx`, for people who want the server without the dev tools. It is not an extra requirement on top of `.[dev]` for `--help`.
4. **Check it locally, with no API key:** `python -c "import logicmem; print(logicmem.__version__)"`, `logicmem-server --help`, and `python -m logicmem.cli --help`. On 2026-11-09 those three exited 0 on Python 3.12.3 after `pip install -e ".[dev]"` and, separately, after `pip install -e .` with no extras (`httpx` absent; the server uses `urllib`). Offline tests live in `tests/test_local_kit.py` (`pytest tests/test_local_kit.py`). `tests/contract_tests.py` is a live-server harness for LogicMem's own servers, not the offline check; see [docs/CONTRACT-TESTS.md](docs/CONTRACT-TESTS.md). Do not point it at the public host.
5. **Make your changes** — add an offline test when you can, update docs, or improve code.
6. **Push to your fork** and open a Pull Request.

## Areas We Need Help

- **More MCP client examples** — Claude Desktop, Cursor, Windsurf, LM Studio, etc.
- **Framework integrations** — LangChain, LlamaIndex, AutoGPT, CrewAI, n8n
- **LogicMem sharing extensions** — this repo's API, not the Agent2Agent open protocol; pub/sub patterns, agent discovery
- **SDK ports** — JavaScript/TypeScript, Rust, Go
- **Documentation** — tutorials, integration guides, architecture diagrams

## Code Style

- Follow PEP 8 for Python
- Add type hints where possible
- Include docstrings for public APIs
- Add example usage in docstrings

## Reporting Issues

- Use [GitHub Issues](https://github.com/LogicMem/LogicMem-mcp-/issues) for bugs and feature requests
- For security issues, email security@logicmem.io directly (do NOT post publicly)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
