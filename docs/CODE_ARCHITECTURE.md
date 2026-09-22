# Code architecture

Exam-formatting-tools converts question-bank exports into a shared exam YAML format and renders that format as a printable DOCX. Several converters write YAML; one builder reads YAML and produces the final document.

## Overview

- The current repository version is `26.09`, recorded in [../VERSION](../VERSION).
- Source code uses [../LICENSE.LGPL-3.0](../LICENSE.LGPL-3.0); documentation uses [../LICENSE.CC-BY-4.0](../LICENSE.CC-BY-4.0).
- Python commands use `source source_me.sh && python3 ...`.
- The printable target is DOCX. ODT and direct HTML-to-DOCX paths are removed.

## Major components

### CLI launchers

The single-purpose entry points live in `launchers/`. They validate input and output extensions with [../ef_tools/cli_checks.py](../ef_tools/cli_checks.py), and optional output paths default to the input stem in the current directory.

| Script | Primary direction | Main output |
| --- | --- | --- |
| [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) | Website task CSV -> generated questions | YAML, answer key, media directory |
| [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py) | bptools BBQ text -> exam data | YAML, answer key, media directory |
| [docx_to_exam_yaml.py](../launchers/docx_to_exam_yaml.py) | DOCX -> exam data | YAML |
| [html_to_exam_yaml.py](../launchers/html_to_exam_yaml.py) | Cleaned Blackboard HTML -> exam data | YAML and referenced media |
| [okla_to_exam_yaml.py](../launchers/okla_to_exam_yaml.py) | Oklahoma export -> exam data | YAML |
| [validate_zip_grade_yaml.py](../launchers/validate_zip_grade_yaml.py) | Exam YAML validation/filtering | Report or filtered YAML |
| [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py) | Exam YAML -> printable document | DOCX |

### Shared library

The `ef_tools/` package contains reusable parsing, validation, rendering, and layout code. Modules are imported directly; `ef_tools/__init__.py` is not a re-export facade.

- [../ef_tools/bbq_tasks.py](../ef_tools/bbq_tasks.py) resolves task-CSV aliases and retries one generator candidate per task.
- [../ef_tools/bbq_parse.py](../ef_tools/bbq_parse.py) parses MC, MA, MAT, and ORD BBQ records, creates answer keys, and owns shared table-image attachment.
- [../ef_tools/bbq_html.py](../ef_tools/bbq_html.py) cleans inline HTML and rasterizes statement, choice, and matching-prompt tables through `qti_package_maker`.
- [../ef_tools/html_parse.py](../ef_tools/html_parse.py) owns Blackboard HTML selectors, inline-tag handling, and choice-prefix parsing.
- [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py) creates styles, rich text, tables, text choices, image choices, and matching prompts.
- [../ef_tools/layout.py](../ef_tools/layout.py) scores visible choice width and selects the `Choices 2` through `Choices 5` paragraph style.
- [../ef_tools/question_utils.py](../ef_tools/question_utils.py) owns question-block spans, numbering totals, and question-style selection.
- [../ef_tools/rdkit_render.py](../ef_tools/rdkit_render.py) turns supported RDKit HTML canvas widgets into PNG files.
- [../ef_tools/zip_grade.py](../ef_tools/zip_grade.py) classifies questions, tracks source lines, filters nonconforming questions, and reports row totals.

### Style configuration

[../styles/exam_styles.yaml](../styles/exam_styles.yaml) is the data source for page margins, fonts, spacing, colors, tab stops, image dimensions, and choice-layout limits. The DOCX builder reads this configuration instead of duplicating layout constants.

## Data flow

The primary Blackboard path is:

```text
Cleaned Blackboard HTML
    |
    | html_to_exam_yaml.py
    v
Exam YAML
    |
    | optional: validate_zip_grade_yaml.py or yaml_to_exam_docx.py --zip-grade
    v
Filtered or original YAML
    |
    | yaml_to_exam_docx.py
    | ef_tools.docx_builder + styles/exam_styles.yaml
    v
Printable DOCX
```

The task-CSV path adds external biology content and table rendering:

```text
biology-problems-website task CSV + bbq_settings.yml
    |
    | bbq_tasks_to_exam_yaml.py
    | ef_tools.bbq_tasks -> generator candidates
    | ef_tools.bbq_parse -> question records and answer keys
    | ef_tools.bbq_html -> cleaned text and PNG table media
    v
Exam YAML + answer key + <stem>_files/*.png
    |
    | yaml_to_exam_docx.py
    v
Printable DOCX
```

Matching blocks use one number per prompt. `question_span()` is the shared owner used by the DOCX builder, ZipGrade checks, question totals, and answer-key formatting. Prompt and choice objects may carry images, so pedigrees and sequence strips remain visible in print.

## Testing and verification

- The fast suite runs with `source source_me.sh && python3 -m pytest tests/ -q`.
- Repo-wide gates include [../tests/test_markdown_links.py](../tests/test_markdown_links.py), [../tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py), [../tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py), and [../tests/test_shebangs.py](../tests/test_shebangs.py).
- The real-generator workflow runs outside pytest through [../tests/e2e/e2e_bbq_tasks_quiz.py](../tests/e2e/e2e_bbq_tasks_quiz.py).
- Image-choice calibration is a maintainer check in [../devel/measure_image_choices.py](../devel/measure_image_choices.py).

## Extension points

- Add a converter under `launchers/` and emit the schema in [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).
- Add reusable parsing or rendering behavior under `ef_tools/` with focused tests under `tests/`.
- Add DOCX layout values to [../styles/exam_styles.yaml](../styles/exam_styles.yaml), then wire the behavior through [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py).
- Add a compatibility validator beside [../ef_tools/zip_grade.py](../ef_tools/zip_grade.py) and expose it through a launcher.

## Known gaps

- The task-CSV path has a recorded end-to-end check; the Blackboard HTML path still relies on the manual smoke commands in [USAGE.md](USAGE.md).
- Table images are appended after statement text even when the source table appears in the middle of a statement.
