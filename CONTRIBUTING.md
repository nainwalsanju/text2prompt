# Contributing to text2prompt

Thank you for your interest in contributing! This project uses TDD (Test-Driven Development) for all changes.

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Run tests: `pytest tests/ -v`

## How to Contribute

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Write tests first** following TDD principles
4. **Implement** the minimal code to pass tests
5. **Run all tests**: `pytest tests/ -v`
6. **Commit** with clear messages: `git commit -m "feat: add my feature"`
7. **Push** and create a Pull Request

## Code Style

- Follow existing patterns in the codebase
- Use type hints for all functions
- Write docstrings for public functions
- Keep functions focused and small

## Testing

- Every new feature needs tests
- Run tests before submitting: `pytest tests/ -v`
- Aim for high coverage, but prioritize meaningful tests

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the CHANGELOG.md if applicable
5. Request review from maintainers

## Questions?

Open an issue for any questions about contributing.
