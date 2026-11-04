# Release history

## v26.11 - 2026-11-04

### Highlights

- Choice layouts now select a column arrangement from the measured width of each complete
  formatted answer, including its label and inline font styling. Each answer must fit its actual
  tab slot and page margin with a half-em gap.
- Named DOCX styles now own choice labels, first-page boilerplate, score tabs, native-table text,
  and FIB_PLUS writing spacing. Question styles supply separation between question blocks.
- Choice labels use a 0.10-inch inset with shifted column tabs. Existing tab-based input and
  balanced row arrangements remain available.
- Every statement, choice, and matching picture insertion now explicitly sets zero image edge
  distance, including SVG and unsized raster images.

### Notable fixes

- Inline capture layout ignores HTML comments, avoiding a genetics-midterm artwork failure caused
  by a comment node without a style attribute.
- The image-choice calibration helper now uses the ordered statement schema and correct label
  origin.
- Added [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md), which documents formatted-answer
  measurement, slot calculations, fallback arrangements, style editing, and rendering limits.

### Compatibility notes

- Generated artifacts remain DOCX-first for LibreOffice editing and PDF export. The pipeline does
  not create an ODT unless an instructor explicitly chooses to save one.
- Explicit choice-layout overrides remain supported; automatic selection replaces character
  budgets with measured page geometry.

### Validation

- Rebuilt and inspected a 100-question genetics midterm. Formerly broken HLA-genotype and
  offspring-calculation five-column rows now use intact 3+2 layouts, while short answers retain
  dense rows.
- A PDF-coordinate diagnostic found no split-label rows in 15 matched measured multi-choice rows,
  compared with two in 24 matched baseline rows; visual review remains the primary check.
- Full pytest recorded 2,088 passing checks. Two unrelated checks remain unavailable because the
  Podman socket is absent and an unchanged Graphify helper has an unused variable.

## v26.09 - 2026-09-21

### Highlights

- Added [bbq_tasks_to_exam_yaml.py](../converters/bbq_tasks_to_exam_yaml.py), which reads the biology-problems-website task CSV contract and contributes one generated question per resolved task.
- Added shared task resolution, BBQ parsing, answer-key formatting, HTML cleanup, and table-image rendering modules under [../ef_tools/](../ef_tools/).
- Added image-capable matching prompts and choices. Rendered table drawings can now appear beside matching blanks or in tabbed image-choice layouts.
- Added `question_span()` as the shared numbering rule for matching blocks, question totals, ZipGrade filtering, DOCX rendering, and answer keys.
- Added an explicit E2E workflow for quiz and exam generation from a task CSV through YAML and DOCX.

### Notable fixes

- Relative image paths are resolved against the YAML file so YAML and its media directory can move together.
- The bootstrap now adds the sibling `qti-package-maker` checkout to `PYTHONPATH` when it is present.
- Shared parser, renderer, and style behavior is covered by focused tests instead of duplicated launcher logic.
- The repository documentation and support files adopted the `launchers/` and `devel/` directory layout.

### Compatibility notes

- The seven converter and validator scripts moved from the repository root into `launchers/`
  in this release. They now live in `converters/`; see [USAGE.md](USAGE.md) for current commands.
- NUM, FIB, and FIB_PLUS BBQ items are skipped because they have no supported print form; unknown BBQ types raise instead of disappearing silently.
- Exam mode retries or skips questions that do not fit ZipGrade's A-E rules; it does not trim six-choice questions.
- Direct ODT output and the legacy direct HTML-to-DOCX path remain out of scope.

### Validation

- The latest recorded fast suite passed 434 tests.
- The task-CSV E2E check passed in both quiz and exam modes, including YAML output, answer keys, rendered media, DOCX output, and ZipGrade validation.
- The recorded acceptance run processed 87 tasks into 82 question blocks and 119 numbered rows, with 68 rendered statement or choice images and no raw HTML in DOCX paragraphs.
