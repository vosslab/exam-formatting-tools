# Release history

## v26.09 - 2026-09-21

### Highlights

- Added [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py), which reads the biology-problems-website task CSV contract and contributes one generated question per resolved task.
- Added shared task resolution, BBQ parsing, answer-key formatting, HTML cleanup, and table-image rendering modules under [../ef_tools/](../ef_tools/).
- Added image-capable matching prompts and choices. Rendered table drawings can now appear beside matching blanks or in tabbed image-choice layouts.
- Added `question_span()` as the shared numbering rule for matching blocks, question totals, ZipGrade filtering, DOCX rendering, and answer keys.
- Added an explicit E2E workflow for quiz and exam generation from a task CSV through YAML and DOCX.

### Notable fixes

- Relative image paths are resolved against the YAML file so YAML and its media directory can move together.
- The bootstrap now adds the sibling `qti-package-maker` checkout to `PYTHONPATH` when it is present.
- Shared parser, renderer, and style behavior is covered by focused tests instead of duplicated launcher logic.
- The repository documentation and support files now use the `launchers/` and `devel/` directory layout.

### Compatibility notes

- The seven converter and validator scripts moved from the repository root into `launchers/`.
- NUM, FIB, and FIB_PLUS BBQ items are skipped because they have no supported print form; unknown BBQ types raise instead of disappearing silently.
- Exam mode retries or skips questions that do not fit ZipGrade's A-E rules; it does not trim six-choice questions.
- Direct ODT output and the legacy direct HTML-to-DOCX path remain out of scope.

### Validation

- The latest recorded fast suite passed 434 tests.
- The task-CSV E2E check passed in both quiz and exam modes, including YAML output, answer keys, rendered media, DOCX output, and ZipGrade validation.
- The recorded acceptance run processed 87 tasks into 82 question blocks and 119 numbered rows, with 68 rendered statement or choice images and no raw HTML in DOCX paragraphs.
