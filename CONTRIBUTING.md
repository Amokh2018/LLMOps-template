# Contributing to LLMOps Template

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

Be respectful and constructive in all interactions.

## Getting Started

1. **Fork and clone** the repository
2. **Create a branch** for your changes: `git checkout -b feature/your-feature-name`
3. **Follow the setup** in [docs/SETUP.md](docs/SETUP.md)

## Development Workflow

### Before You Start

1. Check existing [issues](../../issues) and [discussions](../../discussions)
2. Open an issue for new features or bugs
3. Wait for feedback before starting major work

### Code Style

We use:
- **ruff** for linting
- **mypy** for type checking
- **pytest** for testing

### Python Style Guide

```python
# Use type hints
def retrieve_documents(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve documents for a query."""
    pass

# Use descriptive names
response = generate_rag_response(user_query)

# Single responsibility
# ✓ Good - one thing
def validate_query(query: str) -> bool:
    return len(query) > 0 and len(query) <= 1000

# ✗ Avoid - multiple concerns
def validate_and_process_query(query):
    if len(query) == 0:
        return None
    # ... more logic
```

### Checking Your Code

```bash
# Lint
ruff check services/api

# Type check
mypy services/api

# Test
pytest services/api/tests

# Format
ruff format services/api
```

## Making Changes

### Services

Changes to services should:
1. Include tests for new functionality
2. Update `.env.example` if adding new config
3. Update relevant documentation
4. Pass linting and type checks

### Infrastructure

Changes to Terraform should:
1. Use `terraform plan` to verify changes
2. Include comments for non-obvious changes
3. Update [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) if needed

### Documentation

- Use clear, concise language
- Include examples where helpful
- Update table of contents if adding sections
- Fix typos and outdated info

## Submitting Changes

### Commit Messages

```
Type: Brief description

Longer explanation if needed.

Related issue: #123
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests
- `ci:` CI/CD changes

### Pull Requests

1. **Create a PR** against `main` or `develop`
2. **Fill out the template** completely
3. **Link related issues**
4. **Add tests** for new functionality
5. **Update docs** if needed

### PR Description Template

```markdown
## Description
Brief description of changes.

## Related Issue
Fixes #123

## Changes
- [ ] Change 1
- [ ] Change 2

## Testing
How to test these changes.

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Docs updated
- [ ] No breaking changes
```

## Testing

### Unit Tests

```bash
# Test a service
pytest services/api/tests

# Test with coverage
pytest --cov=services/api services/api/tests
```

### Integration Tests

Run against local GCP emulator or staging environment:

```bash
pytest services/api/tests/integration
```

### Writing Tests

```python
import pytest
from services.api.rag import RAGService

@pytest.fixture
def rag_service():
    return RAGService()

@pytest.mark.asyncio
async def test_retrieve_documents(rag_service):
    documents = await rag_service.retrieve_documents(
        "test query",
        top_k=5
    )
    assert len(documents) <= 5
    assert all(hasattr(doc, 'similarity_score') for doc in documents)
```

## Documentation

### Writing Docs

- Clear and concise
- Include examples
- Link to related docs
- Use proper markdown

### Doc Structure

```markdown
# Title

## Overview
Brief intro.

## Prerequisites
What's needed.

## Steps
1. Step 1
2. Step 2

## Example
Code example.

## Troubleshooting
Common issues.
```

## Reporting Issues

### Bug Reports

Include:
1. Description of the bug
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment (Python version, OS, etc.)
5. Logs or error messages

### Feature Requests

Include:
1. Use case/motivation
2. Proposed solution
3. Alternatives considered
4. Any concerns

## Review Process

1. **Automated checks** run (linting, tests)
2. **Code review** by maintainers
3. **Address feedback**
4. **Approval and merge**

### Review Criteria

- Correctness
- Code quality
- Test coverage
- Documentation
- Performance impact
- Security concerns

## Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Cloud Python Client Libraries](https://cloud.google.com/python/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)

## Questions?

- Open a [discussion](../../discussions)
- Check [docs/](docs/)
- Ask in issues

Thank you for contributing! 🙏
