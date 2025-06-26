# Resume Builder Tests

This directory contains the test suite for the Resume Builder application. The tests are written using pytest and cover various aspects of the application including form processing, PDF generation, and template rendering.

## Test Structure

- `test_app.py`: Basic application tests including route testing and utility functions
- `test_form_processing.py`: Tests for form data processing and validation
- `test_pdf_generation.py`: Tests for PDF generation functionality
- `test_template_rendering.py`: Tests for template rendering and preview functionality

## Running Tests

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Run all tests:
```bash
pytest
```

3. Run tests with coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

4. Run specific test file:
```bash
pytest tests/test_app.py
```

## Code Quality

This project uses several tools to maintain code quality:

1. Black for code formatting:
```bash
black .
```

2. Flake8 for linting:
```bash
flake8
```

## Test Configuration

- `pytest.ini`: Main pytest configuration
- `pyproject.toml`: Black configuration
- `.flake8`: Flake8 configuration

## Writing New Tests

When adding new features, please:

1. Create corresponding test files in the `tests` directory
2. Follow the existing test structure and naming conventions
3. Use appropriate fixtures from `conftest.py` or create new ones
4. Ensure all tests pass before submitting changes
5. Maintain or improve code coverage

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main branch
- Daily scheduled runs

## Test Coverage Goals

- Maintain minimum 80% code coverage
- Focus on critical path testing
- Include both positive and negative test cases
- Test edge cases and error conditions