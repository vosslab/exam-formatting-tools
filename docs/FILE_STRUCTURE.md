# File structure

This map shows where runtime code, converter entry points, generated artifacts, tests, and documentation belong. See [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) for responsibilities and data flow.

## Top-level layout

```text
exam-formatting-tools/
+- README.md
+- AGENTS.md
+- CLAUDE.md
+- VERSION
+- REPO_TYPE
+- bbq_settings.yml
+- LICENSE.LGPL-3.0
+- LICENSE.CC-BY-4.0
+- source_me.sh
+- pip_requirements*.txt
+- Brewfile
+- ef_tools/
+- launchers/
+- styles/
+- tests/
+- devel/
+- tools/
`- docs/
```

| Path | Purpose |
| --- | --- |
| [../bbq_settings.yml](../bbq_settings.yml) | Default paths and script aliases for website task CSVs |
| [../source_me.sh](../source_me.sh) | Bash bootstrap and sibling-checkout `PYTHONPATH` setup |
| [../ef_tools/](../ef_tools/) | Shared parsing, validation, layout, and rendering modules |
| [../launchers/](../launchers/) | User-facing format converters and validators |
| [../styles/](../styles/) | YAML-controlled DOCX styles and layout values |
| [../tests/](../tests/) | Fast tests, explicit E2E checks, and repository gates |
| [../devel/](../devel/) | Maintainer, calibration, changelog, and release scripts |
| [../tools/](../tools/) | Standalone utilities; keep repo-package imports out of this directory |
| [docs](.) | User, maintainer, schema, and repository guidance |

## Key subtrees

### `launchers/`

Each launcher has one primary direction and a small argparse surface. Run a launcher through `source source_me.sh && python3 launchers/<script>.py`; see [USAGE.md](USAGE.md) for examples.

### `ef_tools/`

Modules are single-purpose and imported directly. Add a matching test named `tests/test_<module>.py` when a new stable behavior warrants permanent coverage.

DOCX assembly and shared text formatting live in `docx_builder.py`; answer choices and matching prompts live in `docx_choice_builder.py`; image sizing and native table conversion each have their own modules.

### `tests/`

Fast unit and integration tests live at the top level, including a synthetic
HTML-to-YAML-to-DOCX pipeline. The real-generator workflow runs through
[../tests/e2e/e2e_bbq_tasks_quiz.py](../tests/e2e/e2e_bbq_tasks_quiz.py), outside
the ordinary pytest lane. Browser-specific tests belong under `tests/playwright/`.

### `devel/`

Maintainer scripts include changelog rotation and release preparation, version helpers, Playwright setup, Markdown diagnostics, and image-choice calibration. They are not the runtime path for exam conversion.

## Generated artifacts

The following outputs are ignored by Git and should not be used as committed fixtures:

- `ARTIFACTS/` for local reference DOCX/ODT samples.
- `output_smoke/` and `output_quiz/` for smoke and task-CSV runs.
- `*.docx`, generated YAML, and `*.odt` for local exam outputs.
- `images/` and `<stem>_files/` directories for extracted or rendered media.
- `report_*.txt`, `.pytest_cache/`, `__pycache__/`, and LibreOffice lock files.

Tracked configuration is the exception to the broad YAML ignore: [../styles/exam_styles.yaml](../styles/exam_styles.yaml) remains committed.

## Documentation map

| Document | Audience and purpose |
| --- | --- |
| [README.md](../README.md) | Newcomer overview and first successful workflow |
| [INSTALL.md](INSTALL.md) | Dependencies, sibling repositories, and install verification |
| [USAGE.md](USAGE.md) | CLI workflows and examples |
| [FILE_FORMATS.md](FILE_FORMATS.md) | Input and output artifact reference |
| [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) | Canonical exam YAML schema |
| [EXAM_DOCUMENT_STYLES.md](EXAM_DOCUMENT_STYLES.md) | Current DOCX style reference |
| [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) | Components and data flow |
| [WORKFLOW_LOGIC_AUDIT.md](WORKFLOW_LOGIC_AUDIT.md) | Converter ownership, output publication, and follow-up priorities |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Symptoms, causes, and recovery steps |
| [FAQ.md](FAQ.md) | Short answers to recurring workflow questions |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Test, documentation, and release workflows |
| [ROADMAP.md](ROADMAP.md) | Forward-looking work and scope boundaries |
| [RELATED_PROJECTS.md](RELATED_PROJECTS.md) | Upstream content and companion tooling |
| [NEWS.md](NEWS.md) | Curated release highlights |
| [RELEASE_HISTORY.md](RELEASE_HISTORY.md) | Detailed release record |
| [CHANGELOG.md](CHANGELOG.md) | Dated implementation history |
| [REPO_STYLE.md](REPO_STYLE.md) | Repository organization and naming rules |
| [PYTHON_STYLE.md](PYTHON_STYLE.md) | Python coding conventions |
| [PYTEST_STYLE.md](PYTEST_STYLE.md) | Permanent-test policy and pytest lanes |
| [MARKDOWN_STYLE.md](MARKDOWN_STYLE.md) | Markdown formatting conventions |

## Where to add new work

| Adding... | Place it in... |
| --- | --- |
| Input-format converter | `launchers/<format>_to_exam_yaml.py` |
| Shared parser or renderer | `ef_tools/<module>.py` |
| DOCX style value | [../styles/exam_styles.yaml](../styles/exam_styles.yaml) |
| Focused unit test | `tests/test_<module>.py` |
| Whole-system test | `tests/e2e/e2e_<name>.{sh,py}` |
| Maintainer or calibration script | `devel/<script>.py` |
| Durable documentation | `docs/<TOPIC>.md` using uppercase underscores |
