# Code architecture

Exam-formatting-tools converts third-party question banks into a shared
exam YAML format and renders them to printable DOCX. The pipeline is
intentionally one-way at the format level: many converters write YAML;
one builder reads YAML and emits DOCX.

## Overview

- Repo version is in [VERSION](../VERSION) (also tracked in
  [pyproject.toml](../pyproject.toml) when present); current value `26.02`.
- Source code is licensed [LGPL v3](../LICENSE.LGPL_v3); non-code material
  (docs, prose) is licensed [CC BY 4.0](../LICENSE.CC_BY_4_0). See the
  Licensing section in [REPO_STYLE.md](REPO_STYLE.md) for the policy.
- Python 3.12 throughout; activate the repo environment with
  `source source_me.sh && python3 ...` (see [INSTALL.md](INSTALL.md)).

## Major components

### Root scripts (entry points)

Single-purpose CLIs at the repo root, each with a `#!/usr/bin/env python3`
shebang and standard `-i/--input` and optional `-o/--output` flags
validated by [ef_tools/cli_checks.py](../ef_tools/cli_checks.py).

| Script | Direction | Allowed extensions |
| --- | --- | --- |
| [bbq_tasks_to_exam_yaml.py](../bbq_tasks_to_exam_yaml.py) | Website task CSV -> one generated question per task -> YAML + key | `.csv` -> `.yml` / `.yaml` |
| [bbq_to_exam_yaml.py](../bbq_to_exam_yaml.py) | bptools bbq text -> YAML + key | `.txt` -> `.yml` / `.yaml` |
| [docx_to_exam_yaml.py](../docx_to_exam_yaml.py) | DOCX -> YAML (round-trip) | `.docx` -> `.yml` / `.yaml` |
| [html_to_exam_yaml.py](../html_to_exam_yaml.py) | Cleaned Blackboard HTML -> YAML | `.html` / `.htm` -> `.yml` / `.yaml` |
| [okla_to_exam_yaml.py](../okla_to_exam_yaml.py) | Oklahoma export -> YAML | `.txt` -> `.yml` / `.yaml` |
| [yaml_to_exam_docx.py](../yaml_to_exam_docx.py) | Exam YAML -> printable DOCX | `.yml` / `.yaml` -> `.docx` |
| [validate_zip_grade_yaml.py](../validate_zip_grade_yaml.py) | YAML linter (ZipGrade compatibility) | `.yml` / `.yaml` -> `.yml` / `.yaml` (with `-o`) |

### Shared library: `ef_tools/`

Reusable modules. No public re-exports from `ef_tools/__init__.py` per
the repo's `__init__.py` policy in
[PYTHON_STYLE.md](PYTHON_STYLE.md); callers import submodules directly.

| Module | Role |
| --- | --- |
| [ef_tools/bbq_html.py](../ef_tools/bbq_html.py) | bptools HTML -> exam inline text; drawing-table extraction and PNG writing via `qti_package_maker.html_to_image` |
| [ef_tools/bbq_parse.py](../ef_tools/bbq_parse.py) | bbq line -> question dict + answer letters (MC/MA/MAT/ORD); answer-key formatter |
| [ef_tools/bbq_tasks.py](../ef_tools/bbq_tasks.py) | Website task-CSV contract (aliases, list scripts, `-y` inputs); one generator run per candidate with retry |
| [ef_tools/cli_checks.py](../ef_tools/cli_checks.py) | Input/output extension validation; default output path resolution |
| [ef_tools/docx_builder.py](../ef_tools/docx_builder.py) | Style setup, rich text runs, choice/image-choice layouts, tables, page header |
| [ef_tools/exam_defaults.py](../ef_tools/exam_defaults.py) | Default name line, scoring sections, score-line formatter |
| [ef_tools/exam_yaml_writer.py](../ef_tools/exam_yaml_writer.py) | YAML dumper that double-quotes strings containing apostrophes |
| [ef_tools/html_parse.py](../ef_tools/html_parse.py) | XPath constants, inline-tag set, choice-prefix regex; helpers for HTML-to-YAML |
| [ef_tools/layout.py](../ef_tools/layout.py) | `auto_layout_for_choices` width-budget algorithm; `Choices N` style picker |
| [ef_tools/question_utils.py](../ef_tools/question_utils.py) | Style selection between Question Heading / Follow; `question_span` (rows per block) and total-question count |
| [ef_tools/rdkit_render.py](../ef_tools/rdkit_render.py) | Render RDKit canvas widgets to PNG via `rdkit.Chem.Draw.MolToFile` |
| [ef_tools/style_loader.py](../ef_tools/style_loader.py) | Load [styles/exam_styles.yaml](../styles/exam_styles.yaml) into a styles dict |
| [ef_tools/text_utils.py](../ef_tools/text_utils.py) | Number-prefix stripping; visible-width scoring for HTML/entity-aware text |
| [ef_tools/zip_grade.py](../ef_tools/zip_grade.py) | Severity classification, line-tracking YAML loader, filter, report formatter |

### Style configuration

[styles/exam_styles.yaml](../styles/exam_styles.yaml) is the single
source of truth for all DOCX rendering values: page margins, font sizes,
indents, tab stops, colors, and per-column image-choice width caps.
Builders read this dict instead of hardcoding values, so layout tuning
is data-driven.

### Tools

[tools/measure_image_choices.py](../tools/measure_image_choices.py) is
the calibration rig for image-choice column sizing. It generates noise
PNGs, builds a one-question-per-col-count exam through the production
DOCX builder, renders to PNG via LibreOffice and ImageMagick, and prints
a per-column-count table comparing rendered right edges to target tab
stops. Re-run after any change to
`IMAGE_CHOICE_MAX_WIDTH_BY_COLS`, `layout_tab_stops`, or
`choice_indent`.

### Tests

Pytest under [tests/](../tests/). Conventions in
[PYTEST_STYLE.md](PYTEST_STYLE.md) and slow end-to-end checks in
[E2E_TESTS.md](E2E_TESTS.md). Repo-wide gates:
[tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py),
[tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py),
[tests/test_shebangs.py](../tests/test_shebangs.py),
[tests/test_bandit_security.py](../tests/test_bandit_security.py).

## Data flow

Primary use case: convert a Blackboard HTML export to a printable exam.

```text
Blackboard HTML
   |
   |  html_to_exam_yaml.py (uses ef_tools.html_parse, ef_tools.rdkit_render)
   v
Exam YAML  (schema in docs/YAML_EXAM_FORMAT.md)
   |
   |  optional: validate_zip_grade_yaml.py (uses ef_tools.zip_grade)
   |    -> reports ZipGrade [ERROR] / [FIXABLE] issues by source line
   |    -> with -o, writes a filtered YAML containing only OK questions
   |
   |  yaml_to_exam_docx.py (uses ef_tools.docx_builder, ef_tools.layout,
   |                        ef_tools.style_loader)
   |    -> reads styles/exam_styles.yaml
   |    -> with --zip-grade, drops ERROR + FIXABLE before building
   v
Printable DOCX
```

A reverse round-trip is provided by
[docx_to_exam_yaml.py](../docx_to_exam_yaml.py) for re-extracting an
existing DOCX into the YAML format.

Second use case: one question per bptools generator, straight from the
website task CSV.

```text
genetics_tasks1.csv + bbq_settings.yml
   |
   |  bbq_tasks_to_exam_yaml.py
   |    -> ef_tools.bbq_tasks: resolve aliases, run each generator (-d 1 -x 1),
   |       retry up to 3 times until a candidate parses and fits the mode
   |    -> ef_tools.bbq_parse: bbq line -> question + answer letters
   |    -> ef_tools.bbq_html: clean inline HTML; drawing tables -> PNG
   |       (qti_package_maker.html_to_image, headless Chromium)
   v
Exam YAML + <stem>-key.txt + <stem>_files/*.png
   |
   |  yaml_to_exam_docx.py (image paths resolved against the YAML's folder)
   v
Printable DOCX
```

Row numbering (a matching block spans one row per prompt) has one owner,
`ef_tools.question_utils.question_span`, used by the DOCX builder, the
ZipGrade checks, total counts, and the answer key.

## Testing and verification

- Full suite: `source source_me.sh && python3 -m pytest tests/ -q`.
- Lint gates run as part of the suite and can be invoked individually:
  `tests/test_pyflakes_code_lint.py`, `tests/test_ascii_compliance.py`,
  `tests/test_shebangs.py`, `tests/test_bandit_security.py`.
- Image-choice calibration is run manually via
  `tools/measure_image_choices.py`; see the docstring for the outputs in
  `/tmp/image_choice_measure/`.

## Extension points

- New input format: add `<format>_to_exam_yaml.py` at the repo root that
  emits the YAML schema documented in
  [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md). Reuse
  `ef_tools.cli_checks` for argument validation.
- New paragraph or choice style: add to
  [styles/exam_styles.yaml](../styles/exam_styles.yaml) and wire into
  [ef_tools/docx_builder.py](../ef_tools/docx_builder.py) `setup_styles`.
- New question type: extend the YAML schema doc and the question loop in
  [yaml_to_exam_docx.py](../yaml_to_exam_docx.py); add a sample to
  [tests/test_yaml_to_exam_docx_matching.py](../tests/test_yaml_to_exam_docx_matching.py).
- New compatibility check (analogous to ZipGrade): add a sibling module
  to [ef_tools/zip_grade.py](../ef_tools/zip_grade.py) and a root-level
  validator script.

## Known gaps

- The only end-to-end check is
  [tests/e2e/e2e_bbq_tasks_quiz.py](../tests/e2e/e2e_bbq_tasks_quiz.py)
  (bptools task CSV -> YAML -> DOCX). The Blackboard HTML path still relies
  on the manual smoke commands in [USAGE.md](USAGE.md).
- bptools table images render after the full statement text, even when the
  source placed the table mid-statement (e.g. gel before the background
  paragraphs).
- Container packaging is not in scope; no `docs/CONTAINER.md` exists.
- `docs/TROUBLESHOOTING.md` would benefit from real recurring symptoms
  (overwrite-refusal, image-column overflow) once cataloged.
