# Contributing to Poker Hand Analyzer

Thank you for your interest in contributing!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dev dependencies: `make install-dev`
5. Create a feature branch: `git checkout -b feature/my-feature`

## Code Standards

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions/classes
- Add tests for new features
- Run `make lint` and `make format` before committing

## Testing
```bash
# Run tests
make test

# Run specific test
pytest tests/test_card_detector.py -v
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit pull request with clear description

## Code Review

All submissions require review. We review for:
- Code quality and style
- Test coverage
- Documentation
- Performance impact