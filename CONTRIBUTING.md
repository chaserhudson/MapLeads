# Contributing to MapLeads

Thank you for your interest in contributing to MapLeads! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/chaserhudson/MapLeads/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Suggesting Features

1. Check existing issues/discussions for similar ideas
2. Open a new issue with the "enhancement" label
3. Describe the feature and its use case
4. Explain why it would benefit MapLeads users

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests if applicable
5. Ensure code follows project style
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

### Pull Request Guidelines

- Reference any related issues
- Describe what the PR changes
- Include screenshots for UI changes
- Ensure all tests pass
- Keep PRs focused - one feature/fix per PR

## Development Setup

```bash
# Clone your fork
git clone https://github.com/chaserhudson/MapLeads.git
cd MapLeads

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions/classes
- Keep functions focused and small
- Comment complex logic

## Testing

Run tests before submitting PRs:

```bash
python -m pytest tests/
```

## Areas for Contribution

- **New notification channels** (Slack, Discord, SMS)
- **Additional data sources** (Yelp, Facebook Places)
- **UI improvements** (Web dashboard, mobile app)
- **Performance optimizations**
- **Documentation improvements**
- **Internationalization**

## Questions?

Feel free to open an issue for any questions about contributing!
