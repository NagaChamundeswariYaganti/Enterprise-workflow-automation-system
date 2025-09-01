# Contributing to Enterprise Workflow Automation

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please open an issue with:
- Clear description of the feature
- Use cases and benefits
- Any implementation ideas

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Write meaningful commit messages
- Keep functions small and focused
- Add comments for complex logic

### Testing

- Write unit tests for new features
- Ensure existing tests pass
- Run: `python -m pytest tests/`

## Development Setup

1. Clone your fork
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `python -m pytest tests/`

## Questions?

Feel free to open an issue for any questions!
