# Contributing to LogicMem MCP

Thank you for your interest in contributing to LogicMem MCP.

## How to Contribute

1. **Fork the repo** and create your branch from `main`.
2. **Clone your fork:** `git clone git@github.com:your-username/LogicMem-mcp-.git`
3. **Install dev dependencies:** `pip install -e ".[dev]"`
4. **Check it installs and runs:** `python -c "import logicmem"` and `logicmem-server --help` (install with `pip install -e ".[dev,cli]"`). `tests/contract_tests.py` is a live-server harness; see [docs/CONTRACT-TESTS.md](docs/CONTRACT-TESTS.md).
5. **Make your changes** — add tests, update docs, or improve code.
6. **Push to your fork** and open a Pull Request.

## Areas We Need Help

- **More MCP client examples** — Claude Desktop, Cursor, Windsurf, LM Studio, etc.
- **Framework integrations** — LangChain, LlamaIndex, AutoGPT, CrewAI, n8n
- **A2A protocol extensions** — pub/sub patterns, agent discovery
- **SDK ports** — JavaScript/TypeScript, Rust, Go
- **Documentation** — tutorials, integration guides, architecture diagrams

## Code Style

- Follow PEP 8 for Python
- Add type hints where possible
- Include docstrings for public APIs
- Add example usage in docstrings

## Reporting Issues

- Use GitHub Issues for bugs and feature requests
- For security issues, email security@logicmem.io directly (do NOT post publicly)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
