## LibreOffice: never run inside the sandbox

On this macOS host, LibreOffice crashes when launched inside the sandbox. Run every command
that can invoke LibreOffice outside the sandbox (`sandbox_permissions="require_escalated"`),
using the provided repository scripts. This includes PDF builds/exports, conversion tests,
and ODP imports: the importer can launch LibreOffice indirectly to convert metafiles to SVG.
Do not retry a sandboxed LibreOffice crash or assume an import is LibreOffice-free.

## Temporary files
Use `_temp/` at the repository root for temporary scripts, renders, and review artifacts.

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
