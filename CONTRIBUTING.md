# CONTRIBUTING

# Contributing to nadzoring

We appreciate your interest in contributing to nadzoring! Please review these guidelines before submitting contributions.

## Code of Conduct

All contributors must adhere to our Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

## Contribution Workflow

### 1. Reporting Issues
- Check existing issues before creating new ones
- Provide detailed reproduction steps
- Include Python version and environment details

### 2. Feature Requests
- Explain the problem and proposed solution
- Include use cases and potential benefits
- Discuss alternatives considered

### 3. Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Implement your changes
4. Add tests covering all new functionality
5. Ensure 100% test coverage
6. Format code with Black (`black .`)
7. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.12+
- pip
- uv (recommended)

### Installation
```bash
git clone https://github.com/yourusername/nadzoring.git
cd nadzoring
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
uv sync
```

### Running Tests
```bash
pytest --cov=nadzoring --cov-report=term-missing
```

### Code Quality Checks
```bash
ruff check src/nadzoring
```

## Pull Request Guidelines
1. Maintain 100% test coverage
2. Update documentation if needed
3. Keep commits atomic and well-described
4. Reference related issues in PR description
5. Ensure all CI checks pass

## Code Standards
- Follow PEP 8 style guide
- Use type annotations for all functions
- Document public APIs with docstrings
- Keep functions small and focused
- Prefer composition over inheritance

## Review Process
- Maintainers will review within 3 business days
- Be responsive to feedback
- Address requested changes promptly
- Continuous integration must pass

## License
By contributing, you agree your contributions will be licensed under the project's MIT license.

