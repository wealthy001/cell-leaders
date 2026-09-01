# Contributing

Thank you for contributing. This document describes the expectations for code changes, tests, and commit hygiene.

Guidelines

- Branching: Use descriptive feature branches: `feature/<short-desc>`, `fix/<short-desc>`.
- Commits: Use conventional commits where possible: `feat:`, `fix:`, `docs:`, `chore:`.
- PRs: Include a short description, a testing checklist, and the impact scope.
- Tests: Add unit tests for parser edge-cases and a small integration test for `main.py` using a mock CSV.
- Code style: Follow PEP8; keep functions short and focused. Use type hints for public functions.

Review process

- At least one approving review for non-trivial changes.
- For automation changes, include a short risk assessment and rollback plan.

Contact

- If you're unsure about any change, open an issue describing the problem and label it `help-wanted`.
