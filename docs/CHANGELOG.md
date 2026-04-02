# Changelog

## 2026-04-02

### Additions and New Features

- Created `ef_tools/` package with shared exam formatting modules:
  - `ef_tools/text_utils.py` -- HTML entity decoding, number prefix stripping, rich text parsing for `<sub>`, `<sup>`, `<b>`, `<strong>`, `<i>`, `<em>` tags.
  - `ef_tools/layout.py` -- auto-layout algorithm for multiple choice column formatting, tab stop positions, style name mapping.
  - `ef_tools/question_utils.py` -- question style selection and total question counting.
  - `ef_tools/style_loader.py` -- loads style definitions from `styles/exam_styles.yaml`.
- Created `styles/exam_styles.yaml` -- externalized all hardcoded style values (fonts, sizes, colors, spacing, tab stops, layout limits) from `docx_exam_builder.py`. Style tweaks can now be made in YAML without editing Python.
- Added rich text rendering to DOCX builder: `<sub>`, `<sup>`, `<b>`, `<strong>`, `<i>`, `<em>` tags in question statements, choices, headings, and table cells now render with proper font formatting (subscript, superscript, bold, italic).

### Behavior or Interface Changes

- Moved `exam_defaults.py` into `ef_tools/exam_defaults.py` (via `git mv`). All imports updated.
- Removed first-line indent from choice paragraphs (was -0.05in hanging indent, now 0).
- `docx_exam_builder.py` now loads styles from `styles/exam_styles.yaml` at runtime instead of hardcoding values.
- Utility functions (`decode_html_entities`, `strip_number_prefix`, `auto_layout_for_choices`, `select_question_style`, `count_total_questions`) extracted from builder into `ef_tools/` modules.

### Fixes and Maintenance

- Added `docx_exam_builder.py` -- new DOCX output engine using python-docx. Same YAML input format as `odt_exam_builder.py`, ~300 lines vs ~750 for ODT. Features: auto-numbering, auto-layout with orphan-row avoidance, bold (A) choice prefixes, Question Heading/Follow auto-selection, Chapter Heading (purple), Heading 2 (bold italic), images with aspect ratio, tables, first page boilerplate, page headers with student name, HTML entity decoding, overwrite protection, and .docx extension enforcement.
- Added `exam_defaults.py` -- default boilerplate text (name line, score line format).
- Added `bbq_to_exam_yaml.py` -- imports bbq_text format to exam YAML (MC, MA, MAT, ORD).
- Added `okla_to_exam_yaml.py` -- imports okla_chrst_bqge format to exam YAML (MC, MA).
- Created `docs/YAML_EXAM_FORMAT.md` -- complete format spec with qti-package-maker compatibility section.

### Behavior or Interface Changes

- YAML format redesigned: `chapter` for chapter headings, `heading` for major section labels (Heading 2), `statement` for question stems, `choices` as plain list (builder generates bold (A) prefixes).
- Auto-layout engine avoids orphan rows: 4 long choices use 2+2 (not 3+1), 5 medium choices use 3+2 (not 4+1).
- Removed `_20_` encoding from all generated ODT style names; plain spaces used directly.
- Question Heading vs Question Follow auto-selected based on preceding element type.
- Images preserve original aspect ratio using PIL dimensions.
- HTML entities in YAML (`&Delta;`, `&alpha;`) decoded to Unicode in output.
- Builder strips existing number prefixes before re-numbering (`22)` -> `22.`).
- First page has no header; body pages show "Page X of Y | date | First Name:___".
- All page margins unified at 0.6in.
- `python-docx` and `pillow` added to `pip_requirements.txt`.
- `conftest.py` updated so `pytest tests/` works without `source source_me.sh`.

### Fixes and Maintenance

- Fixed pre-existing pyflakes unused import warnings in `odt_utils.py`, `extract_odt_styles.py`, `propagate_odt_styles.py`, and test files.
- Added `docx` import alias to `tests/test_import_requirements.py`.
- Removed skipped artifact-dependent tests; replaced with generated ODT fixtures.

- **WP-4.1: Updated docx_to_exam_yaml.py to output new YAML format**
  - Modified `parse_inline_choices()` function to return plain choice text strings without letter prefixes (e.g., "Loss of atoms" instead of "A. Loss of atoms").
  - Updated `parse_docx_questions()` to use new YAML keys: `statement` (replaces `heading` for questions), `choices` as plain list (replaces dict with `layout`/`items`). Removed `number` fields from questions (auto-numbered by builder).
  - Changed section building in `build_yaml_structure()` to use `chapter` key (replaces `heading`) for section headings.
  - Added automatic stripping of letter prefixes from all choice patterns: inline choices, list paragraph choices, and text field choice parsing.
  - Appends `text` field content (if present) to question `statement` with newline separator, eliminating separate text field.
  - Fixed table attachment logic to assign tables to most recently parsed question.
  - Verified full end-to-end functionality: docx_to_exam_yaml.py -> odt_exam_builder.py produces valid styled ODT without errors.
  - Tested with Biochem_Exam_2_Spring_2026.docx: successfully parsed 50 questions with 8 embedded images.

- **WP-2.1: Default exam first page boilerplate with name and score lines**
  - Created new `exam_defaults.py` module with centralized defaults for exam boilerplate text.
  - Added `DEFAULT_NAME_LINE` constant: "Full Name: __________________________"
  - Added `DEFAULT_SCORING_SECTIONS` constant: 4 (number of scoring blanks on first page)
  - Implemented `format_score_line(total_points, num_sections)` function to generate "Final Score ____ / ____ / ... / total pts" lines with configurable section count.
  - Updated `build_document_body()` to build proper first page with three elements:
    - Line 1: Exam title (from YAML `title` field) in "Heading 1" style
    - Line 2: Name line (from YAML `student_line` field or default) in "Standard" style
    - Line 3: Score line (from YAML `total_points` field or auto-counted questions, with `scoring_sections` configurable) in "Standard" style
  - Added `count_total_questions(sections)` helper function to sum all questions across all sections when `total_points` is not explicitly provided.
  - YAML fields: `student_line` (optional, overrides default), `total_points` (optional, defaults to question count), `scoring_sections` (optional, defaults to 4)
  - Removed `date` paragraph from body (date moved to page header in WP-2.2)
  - Comprehensive unit test suite in `tests/test_exam_defaults.py` with 5 tests covering score line formatting with various section counts and default values.

- **WP-2.2: Added student name header to body pages (Standard master page)**
  - Updated `create_page_layouts()` function to accept optional `date_str` parameter for embedding date in page headers.
  - Added "Header" paragraph style (9pt font, Liberation Sans, with two tab stops: center tab at 3.65in and right tab at 7.3in) for consistent header formatting.
  - Standard master page (Mpm1/body pages) now includes header with three columns: "Page X of Y" (left), date (center), and "First Name:_____________________________" (right).
  - First Page master page (Mpm2/title page) includes an empty header to keep title page clean.
  - Added header-style properties to page layout Mpm1 with 0.2in margin below header.
  - Updated `assemble_odt()` to extract date from exam YAML and pass it to `create_page_layouts()`.
  - Uses ODF fields for automatic page numbering: `text:page-number` with `text:select-page="current"` for current page, `text:page-count` for total page count.

- **WP-3.2: Created okla_to_exam_yaml.py -- okla_chrst_bqge format to YAML converter**
  - New executable script converts okla_chrst_bqge format questions (from qti-package-maker) to the new exam YAML format.
  - Supports MC (multiple choice) and MA (multiple answer) question types; skips FIB (fill in blank) and MATCH questions as not compatible with bubble-sheet printing.
  - Automatically strips question number prefixes ("1. ", "12. ") from statement text.
  - Strips choice letter prefixes ("a) ", "b) ") and asterisk markers ("*a) ") from choice text, rendering as plain choice list.
  - Block-based format: questions separated by blank lines, with asterisk (*) marking correct answers (ignored in output).
  - Command-line interface: `-i input_file -o output_file -t title` (title optional, defaults to "Exam").
  - Output YAML includes required title, date (2026-04-02), and single "Questions" section with all parsed questions.
  - Comprehensive unit test suite (`tests/test_okla_to_exam_yaml.py`) with 18 tests covering MC/MA questions, skipping FIB/MATCH, edge cases (leading numbers, whitespace, special characters), and full end-to-end conversion with YAML output verification.

- **WP-3.1: Created bbq_to_exam_yaml.py -- BBQ text format to YAML converter**
  - New executable script converts BBQ text format questions (from qti-package-maker) to the new exam YAML format.
  - Supports MC (multiple choice), MA (multiple answer), MAT (matching), and ORD (ordering) question types.
  - Automatically strips correct/incorrect status markers from MC/MA questions; renders as plain choice list for exam output.
  - Converts MAT questions to YAML table format with columns ["Prompt", "Match"] and rows for each match pair.
  - Converts ORD questions to plain choice list (ordering info discarded for print-only output).
  - Command-line interface: `-i input_file -o output_file -t title` (title optional, defaults to "Exam").
  - Output YAML includes required title, date (2026-04-02), and single "Questions" section with all parsed questions.
  - Comprehensive unit test suite (`tests/test_bbq_to_exam_yaml.py`) with 14 tests covering each question type, edge cases (empty lines, whitespace), and full end-to-end conversion.

- **WP-1.4: Auto-select question style (Question Heading vs. Question Follow)**
  - Added `select_question_style()` function: automatically selects "Question Heading" or "Question Follow" style based on the previous element in the document.
  - "Question Heading" is used for questions in normal sequential flow (after other questions or choices).
  - "Question Follow" is used for questions immediately after images, tables, or chapter headings, reducing visual awkwardness and spacing issues.
  - Updated `build_document_body()` to track the previous element type (`prev_element` variable tracking 'chapter', 'question', 'choices', 'table', 'image') and call `select_question_style()` before creating each question paragraph.
  - Added comprehensive documentation to [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) explaining the auto-selection rules and when each style is used.

- **WP-1.2: Auto-numbering, auto-layout, and choice formatting in builder**
  - Added `auto_layout_for_choices()` function: automatically selects Choices3/4/5 layout based on choice count and max text length (5 short -> Choices5, 5 long -> Choices4 with overflow, 3 -> Choices3, 2 or 4 -> Choices4).
  - Implemented auto-numbering in `build_document_body()`: questions numbered sequentially starting at 1, with optional `number` field override. Question text prefixed with "##. statement" format (period, never parenthesis).
  - Updated `create_choices_paragraph()` to accept plain text choices list and auto-generate bold letter prefixes "(A) (B) (C)" via `text:span` with `AutoBold` automatic style.
  - Added `Chapter Heading` named style (14pt bold, dark purple #6600cc, Liberation Sans, keep-with-next).
  - Updated `build_document_body()` to use new YAML keys: `section.chapter` (not `heading`), `question.statement` (not `heading`/`text`), `question.choices` as plain list (not dict with `layout`/`items`), `question.layout` optional override at question level.

### Behavior or Interface Changes

- Builder now requires new YAML format. Old format with `heading`, `text`, and choices dict will not work.
- `create_choices_paragraph()` signature changed: now takes plain choices list and optional `auto_styles` parameter instead of pre-formatted items dict.
- Removed unused `copy` module import from `odt_exam_builder.py`.
- Converted `Biochem_Exam_2_Spring_2026.yaml` to new format: changed `heading` -> `chapter` (in sections), `heading` -> `statement` (in questions, with number prefix stripped), removed letter prefixes from choice items, removed explicit `number` fields, removed explicit `layout` fields. Text field contents appended to statement where present. All `image` and `table` fields preserved as-is.

### Removed `_20_` hex encoding from generated ODT style names

- Style names now use plain spaces directly (ODF spec allows this). Examples: `Question_20_Heading` -> `Question Heading`, `Table_20_Contents` -> `Table Contents`, `Heading_20_1` -> `Heading 1`, etc. Kept `encode_style_name()` and `decode_style_name()` functions in `odt_utils.py` for reading legacy ODT files. Updated `get_style_by_name()` to match both plain and encoded names for backwards compatibility.

### Created YAML format specification

- Created [docs/YAML_EXAM_FORMAT.md](docs/YAML_EXAM_FORMAT.md) with complete specification for the new simplified YAML exam format. Documents conventions for `title`, `date`, `total_points`, `sections[].chapter`, `sections[].questions[]` with `statement`, `number` (optional), `choices` (plain text, no letter prefixes), `layout` (optional, auto-determined), `image`, and `table` fields.
- Auto-layout algorithm: 5 short choices -> Choices5, 5 long choices -> Choices4 (2 rows), 3 choices -> Choices3, 2 or 4 choices -> Choices4 (with tabs). User can override with explicit `layout` field.
- Documented that `number` field is optional and serves as override only; questions are auto-numbered by order. Choice items are plain text without letter prefixes (builder generates bold `(A)` format).

## 2026-04-02 (earlier)

### Fixes and Maintenance

- Rewrote `README.md` to describe the actual exam formatting tools instead of the starter template boilerplate. Added quick start examples for all three CLI tools and linked all existing docs.

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
