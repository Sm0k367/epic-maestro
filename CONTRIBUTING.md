# Contributing to Epic Maestro

Epic Maestro is an intelligent reasoning system for autonomous orchestration. We welcome contributions that make it smarter, faster, and more capable.

## Core Principles

1. **Reasoning > Automation** — We focus on *why* decisions are made, not just what gets done
2. **Learning > Configuration** — The system learns from patterns, not complex config files
3. **Healing > Failure** — Detect failures and prevent them autonomously
4. **Intelligence > Scale** — Better decisions matter more than processing more jobs

## Development Setup

```bash
git clone https://github.com/yourusername/epic-maestro
cd epic-maestro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov black pylint

# Run tests
pytest tests/
```

## Project Structure

```
epic-maestro/
├── core/
│   ├── reasoner.py          # The thinking engine
│   ├── windows_integration.ps1
│   └── healer.py            # Self-healing logic (TODO)
├── api/
│   ├── server.py            # FastAPI application
│   └── models.py            # Pydantic models (TODO)
├── workers/                 # Execution nodes
├── examples/                # Real-world examples
├── tests/                   # Test suite (TODO)
└── docs/                    # Documentation
```

## Key Files to Understand

- **`core/reasoner.py`** — The heart of Epic. This is where reasoning happens. When you want to add intelligence, it goes here.
- **`api/server.py`** — The interface. RESTful and WebSocket APIs for external systems to use the reasoner.
- **`core/windows_integration.ps1`** — Integration with your Windows infrastructure.

## How to Contribute

### Bug Reports

Found a reasoning mistake or API issue? Open an issue with:
- What happened
- What you expected
- Your infrastructure context (which nodes you have)
- Steps to reproduce

### Feature Requests

Want to add intelligence? Ideas:

1. **Better Pattern Recognition** — Improve how we detect workflow patterns
2. **Predictive Scaling** — Predict when fleet will be bottlenecked
3. **Cost Optimization** — Route jobs to minimize resource usage
4. **Advanced Healing** — Detect more subtle failure modes
5. **Plugin System** — Let users extend reasoning with custom logic

### Code Contributions

1. **Fork** the repository
2. **Branch** from `develop`: `git checkout -b feature/my-idea`
3. **Write tests** for your changes
4. **Ensure code quality**:
   ```bash
   black core/ api/
   pylint core/ api/
   pytest tests/
   ```
5. **Commit** with clear messages
6. **Push** to your fork
7. **Open a PR** with description of your changes

### Adding Reasoning

If you're improving the reasoning engine:

1. Add your logic to `core/reasoner.py`
2. Add a test case in `tests/test_reasoner.py`
3. Document the *why* behind your decision
4. Add to `examples/` showing how it works

Example:

```python
# BEFORE: Reasoner routes all work to least busy node
best_node = min(nodes, key=lambda n: n.utilization)

# AFTER: Consider predicted future state too
current_load = min(nodes, key=lambda n: n.utilization)
future_load = self._predict_load_in(current_load, seconds=30)
if future_load > 0.8:
    # This node will be busy, route to second-best
    best_node = sorted(nodes, key=lambda n: n.utilization)[1]
```

## Testing

We use pytest. Every contribution should include tests:

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_reasoner.py::test_pattern_detection

# Run with coverage
pytest --cov=core --cov=api
```

## Documentation

- Update README.md if you change user-facing behavior
- Add docstrings to new functions
- Include examples in comments for complex logic

## Code Style

- Use Python 3.10+ features (type hints, f-strings)
- Follow PEP 8
- Format with `black`
- Lint with `pylint`

## Commit Messages

```
feat: Add predictive scaling to fleet intelligence
fix: Prevent double-counting utilization
docs: Explain reasoning engine architecture
refactor: Simplify pattern matching
test: Add test for failure healing
```

## Questions?

- Check `/docs` for architecture details
- Review existing issues for similar topics
- Ask in discussions (or open an issue with [QUESTION])

## License

By contributing, you agree your work will be licensed under the same license as Epic Maestro.

---

**Thank you for contributing to making Epic Maestro smarter!**
