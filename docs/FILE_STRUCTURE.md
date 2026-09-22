# File structure

Directory map for `exam-formatting-tools`. Companion to
[CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md), which explains how the
pieces work together.

## Top-level layout

```text
exam-formatting-tools/
+- README.md
+- AGENTS.md
+- CLAUDE.md
+- VERSION
+- LICENSE.LGPL_v3
+- LICENSE.CC_BY_4_0
+- source_me.sh
+- bbq_settings.yml
+- pip_requirements.txt
+- pip_requirements-dev.txt
+- pip_extras.txt
+- Brewfile
+- .gitignore
+- ef_tools/
+- styles/
+- launchers/   (CLI entry points: *_to_exam_*.py, validate_zip_grade_yaml.py)
+- tools/       (TOOLS_README.md only; standalone utilities go here)
+- tests/
+- devel/
+- docs/
`- ARTIFACTS/   (git-ignored; reference DOCX/ODT samples)
```

| Path | Purpose |
| --- | --- |
| [README.md](../README.md) | Project intro, quick start, doc index |
| [AGENTS.md](../AGENTS.md) | AI-agent rules and Python environment notes |
| [VERSION](../VERSION) | Single source of truth for the repo version (CalVer `0Y.0M`) |
| `LICENSE.LGPL_v3` | License for source code |
| `LICENSE.CC_BY_4_0` | License for non-code material (docs, prose) |
| [source_me.sh](../source_me.sh) | Bootstrap script; activates the repo Python environment |
| [bbq_settings.yml](../bbq_settings.yml) | Path and script aliases for `launchers/bbq_tasks_to_exam_yaml.py` (mirrors the website copy) |
| [pip_requirements.txt](../pip_requirements.txt) | Standard runtime Python dependencies |
| [pip_requirements-dev.txt](../pip_requirements-dev.txt) | Developer-only dependencies (pytest, pyflakes, etc.) |
| [pip_extras.txt](../pip_extras.txt) | Optional extras |
| [Brewfile](../Brewfile) | Homebrew system dependencies |
| `*_to_*.py` (root) | Single-purpose CLIs; see [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) for the table |

## Key subtrees

### `ef_tools/`

Reusable library modules consumed by the root scripts. Per
[PYTHON_STYLE.md](PYTHON_STYLE.md), `__init__.py` is a one-line docstring
only; callers import submodules directly (e.g.
`import ef_tools.docx_builder`).

```text
ef_tools/
+- __init__.py
+- bbq_html.py          (bptools HTML -> exam text; tables -> PNG)
+- bbq_parse.py         (bbq line -> question + answer letters; key text)
+- bbq_tasks.py         (website task CSV contract; generate with retry)
+- cli_checks.py        (input/output extension validation)
+- docx_builder.py      (style setup, layout, page header)
+- exam_defaults.py     (name line, score line)
+- exam_yaml_writer.py  (apostrophe-safe YAML dumper)
+- html_parse.py        (HTML XPath, choice-prefix regex, helpers)
+- layout.py            (auto_layout_for_choices)
+- question_utils.py    (style selection, question_span, count helpers)
+- rdkit_render.py      (canvas-to-PNG via rdkit)
+- style_loader.py      (load styles/exam_styles.yaml)
+- text_utils.py        (visible-width scoring, number-prefix stripping)
`- zip_grade.py         (ZipGrade severity, filter, line-tracking loader)
```

### `styles/`

```text
styles/
`- exam_styles.yaml     (page margins, fonts, sizes, tab stops, colors)
```

[exam_styles.yaml](../styles/exam_styles.yaml) is the single
source of truth for DOCX rendering values; whitelisted in
[.gitignore](../.gitignore) so it is tracked despite the global
`*.yaml` exclusion.

### `launchers/`

```text
launchers/
+- bbq_tasks_to_exam_yaml.py
+- bbq_to_exam_yaml.py
+- docx_to_exam_yaml.py
+- html_to_exam_yaml.py
+- okla_to_exam_yaml.py
+- validate_zip_grade_yaml.py
`- yaml_to_exam_docx.py
```

CLI scripts that import the `ef_tools` package (see [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md)). Run via `source source_me.sh && python3 launchers/<script>.py`. The image-choice calibration rig lives at `devel/measure_image_choices.py`;
output lands in `/tmp/image_choice_measure/`.

### `tests/`

```text
tests/
+- conftest.py
+- file_utils.py
+- check_ascii_compliance.py        (single-file ASCII checker)
+- fix_ascii_compliance.py          (single-file ASCII fixer)
+- fix_whitespace.py                (single-file whitespace fixer)
+- test_ascii_compliance.py         (repo-wide gate)
+- test_pyflakes_code_lint.py       (repo-wide gate)
+- test_shebangs.py                 (repo-wide gate)
+- test_bandit_security.py          (repo-wide gate)
+- test_import_dot.py
+- test_import_requirements.py
+- test_import_star.py
+- test_indentation.py
+- test_init_files.py
+- test_whitespace.py
+- test_*_to_*.py                   (per-converter unit tests)
+- test_docx_*.py                   (DOCX builder/styles/layout tests)
+- test_yaml_to_exam_docx_matching.py
+- test_zip_grade.py
+- test_<module>.py                 (per-ef_tools module tests)
`- e2e/
   `- e2e_bbq_tasks_quiz.py         (real generators + Chromium + DOCX; outside pytest)
```

Conventions in [PYTEST_STYLE.md](PYTEST_STYLE.md). End-to-end checks
that exceed pytest's speed budget live in `tests/e2e/` per
[E2E_TESTS.md](E2E_TESTS.md) and run with
`source source_me.sh && python3 tests/e2e/e2e_bbq_tasks_quiz.py`.

### `devel/`

```text
devel/
+- DEVEL_README.md              (index of the vendored maintainer scripts)
+- measure_image_choices.py     (image-choice column-cap calibration rig; repo-local)
+- setup_playwright.sh          (browser install helper; repo-local)
+- commit_changelog.py, rotate_changelog.py, query_changelog.py, changelog_*.py
+- bump_version.py, version_*.py, make_release.py, clean_build.sh, dist_clean.sh
`- graphify_*.py, markdown_section_sizes.py, flatten_broken_md_links.py
```

Maintainer and repository-engineering scripts; the vendored ones are
described in [DEVEL_README.md](../devel/DEVEL_README.md). Not part of the
runtime path.

## Generated artifacts

Listed in [.gitignore](../.gitignore):

- `report_*.txt` (bandit and other reports)
- `.DS_Store` (macOS Finder metadata)
- `ARTIFACTS/` (reference exam DOCX/ODT samples; large, untracked)
- `images/` (extracted exam images; untracked)
- `*.docx` (generated exam outputs; untracked)
- `*.yaml` except `styles/*.yaml` (generated exam YAML; untracked)
- `*.odt` (legacy ODT outputs; untracked)
- `.~lock.*` (LibreOffice lock files)
- `output_smoke/` (smoke and E2E run outputs)
- `output_quiz/` (generated quiz/exam YAML, DOCX, key, and `*_files/` PNGs)

## Documentation map

```text
docs/
+- CHANGELOG.md             (dated change log; rotates per REPO_STYLE.md)
+- INSTALL.md               (setup, dependencies, environment)
+- USAGE.md                 (commands and examples)
+- ROADMAP.md               (forward-looking work, known gaps)
+- AUTHORS.md               (maintainers; centrally maintained)
+- CODE_ARCHITECTURE.md     (this repo's component map -- see CODE_ARCHITECTURE.md)
+- FILE_STRUCTURE.md        (this file)
+- YAML_EXAM_FORMAT.md      (canonical exam YAML schema)
+- EXAM_DOCUMENT_STYLES.md  (DOCX style reference)
+- E2E_TESTS.md             (slow end-to-end test conventions)
+- PYTEST_STYLE.md          (pytest writing rules)
+- PYTHON_STYLE.md          (Python coding style)
+- REPO_STYLE.md            (repo-wide organization and naming)
+- MARKDOWN_STYLE.md        (Markdown formatting)
+- CLAUDE_HOOK_USAGE_GUIDE.md  (Claude Code permission rules; centrally maintained)
`- RELATED_PROJECTS.md      (sibling repos and integration points)
```

Root-level docs at `README.md`, `AGENTS.md`, `CLAUDE.md`, `VERSION`,
and the two `LICENSE.*` files.

## Where to add new work

| Adding... | Place it in... |
| --- | --- |
| New input-format converter | `launchers/<format>_to_exam_yaml.py` |
| New library helper | `ef_tools/<module>.py` (one purpose per module) |
| New DOCX style values | [exam_styles.yaml](../styles/exam_styles.yaml) |
| New unit test | `tests/test_<module>.py`, mirroring the source module name |
| New end-to-end script | `tests/e2e/e2e_<name>.{sh,py}` |
| New calibration or maintainer script | `devel/<script>.py` |
| New documentation | `docs/<TOPIC>.md` (ALL CAPS with underscores) |
| New maintainer script | `devel/<script>.py` |
