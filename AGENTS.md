# Repository rules

- docs/REPO_STYLE.md
- docs/PYTHON_STYLE.md
- docs/MARKDOWN_STYLE.md
- docs/PYTEST_STYLE.md
- docs/CHANGELOG.md

## Python runtime

- Run repository Python with `source source_me.sh && python3` using Python 3.12.
- Run focused tests when changing code; documentation-only changes do not require tests.
- Use `source source_me.sh && python3 -m pytest tests/` for the full pytest lane.

## Documentation changes

- Record repository edits in `docs/CHANGELOG.md`.
