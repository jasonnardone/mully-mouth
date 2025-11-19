# Contributing to Mully Mouth

Thank you for your interest in contributing to Mully Mouth! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/mully-mouth.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black ruff mypy

# Validate setup
python validate.py
```

## Code Style

This project follows:
- **PEP 8** style guide
- **Black** code formatting (line length: 100)
- **Type hints** for all functions
- **Docstrings** for all public methods (Google style)

### Formatting

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_pattern_cache.py
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use fixtures for common setup
- Aim for >80% code coverage

## Project Structure

```
mully-mouth/
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   ├── cli/             # CLI interface
│   └── lib/             # Utilities and configuration
├── tests/               # Unit and integration tests
├── config/              # Configuration files
└── data/                # Runtime data (cache, sessions, etc.)
```

## Adding New Features

### Adding a New Personality

1. Create YAML file in `data/personalities/`:
```yaml
name: "My Personality"
description: "Brief description"
tone: "tone_type"
system_prompt: |
  System prompt for Claude...

example_phrases:
  fairway:
    - "Example phrase 1"
    - "Example phrase 2"
  # Add for all outcome types
```

2. Test with: `python -m src.cli.main --personality my_personality`

### Adding a New Service

1. Create service file in `src/services/`
2. Define service interface (follow existing patterns)
3. Add error handling with custom exceptions
4. Write unit tests in `tests/`
5. Update `src/cli/monitor.py` to integrate service
6. Document in README.md

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass: `pytest tests/`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if applicable)

### PR Description

Include:
- **Purpose**: What does this PR do?
- **Changes**: What was changed?
- **Testing**: How was it tested?
- **Screenshots**: If UI changes (optional)

### Commit Messages

Follow conventional commits:
- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `test: Add tests`
- `refactor: Refactor code`
- `chore: Update dependencies`

## Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Use case
- Proposed solution
- Alternatives considered
- Impact on existing functionality

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Questions?

- Open an issue with the `question` label
- Check existing issues and discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
