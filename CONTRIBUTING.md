# Contributing to Qwen Profiler

Thank you for your interest in contributing to Qwen Profiler! We welcome contributions from the community and are grateful for your efforts.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites
- Python 3.9 or higher
- UV package manager

### Setting up the Development Environment
1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/qwen-profiler.git
   cd qwen-profiler
   ```
3. Set up the virtual environment using UV:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

2. Make your changes following the code style guidelines

3. Add tests for your changes if applicable

4. Run the tests to ensure everything is working:
   ```bash
   python -m pytest
   ```

5. Commit your changes following the commit message guidelines

6. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a pull request to the main repository

## Code Style

- Follow PEP 8 guidelines for Python code
- Use type hints for all function parameters and return types
- Write docstrings for all public classes, functions, and modules using Google style
- Keep functions focused and less than 50 lines when possible
- Use meaningful variable and function names

## Testing

- Write unit tests for all new functionality
- Maintain high test coverage (target 90%+)
- Use pytest for testing
- Follow the Arrange-Act-Assert pattern in tests
- Test both happy path and error conditions

To run the tests:
```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=qwen_profiler

# Run specific test file
python -m pytest tests/test_specific_file.py
```

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Add tests for new functionality
3. Update documentation if necessary
4. Ensure all tests pass
5. Describe your changes in the pull request description
6. Link to any relevant issues (use "Fixes #issue-number" to automatically close issues)
7. Submit your pull request to the `main` branch

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.