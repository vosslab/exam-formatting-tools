# Changelog

## 2026-04-01

### Additions and New Features

- Added `odt_utils.py` -- shared ODT utility module for reading/writing ODT files using `lxml` and `zipfile`. Includes ODF namespace registry, style accessors, round-trip read/write with ODF-compliant mimetype ordering, and canonical style comparison.
- Added `extract_odt_styles.py` -- extracts named styles from ODT files to YAML or content-free template ODT. Supports style comparison between two ODT files and family filtering. YAML output decodes ODF-encoded names to human-readable form.
- Added `propagate_odt_styles.py` -- applies named styles from a source ODT to target ODT files. Supports dry-run mode, backup creation, and optional page layout propagation. Never touches automatic styles.
- Added `odt_exam_builder.py` -- generates fully styled ODT exam documents from YAML input. Embeds all named styles from [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) including page layouts, question formatting, multiple choice layouts (Choices3/4/5), tables with colored headers, and image embedding.
- Added `lxml` and `pyyaml` to [pip_requirements.txt](pip_requirements.txt).
- Added test files: `tests/test_odt_utils.py`, `tests/test_extract_odt_styles.py`, `tests/test_propagate_odt_styles.py`, `tests/test_odt_exam_builder.py`.

### Fixes and Maintenance

- Fixed ODF style name encoding: real LibreOffice ODT files use `_20_` hex encoding for spaces in style names (e.g., `Question_20_Heading`). Updated all tools to use encoded names for compatibility with real exam documents.
- Added `encode_style_name()` and `decode_style_name()` to `odt_utils.py` for converting between human-readable and ODF-encoded style names.
- Updated `get_style_by_name()` to accept either human-readable or ODF-encoded names.
- Trimmed test suite: removed tests for trivial wrappers, excessive assertions, and exact-count checks per updated testing guidelines.

### Decisions and Failures

- Chose `lxml` + `zipfile` over `odfpy` for ODT manipulation per [docs/ROADMAP.md](docs/ROADMAP.md). This avoids a new dependency and gives full control over XML structure.
- Discovered ODF `_XX_` hex encoding for style names by examining real ARTIFACTS. Both 2019 and 2025 exams use this consistently.

### Developer Tests and Notes

- Full test suite: 140 passed, 0 skipped (with ARTIFACTS present).
- All new code passes pyflakes, bandit, shebang alignment, tab indentation, import requirements, and ASCII compliance checks.
