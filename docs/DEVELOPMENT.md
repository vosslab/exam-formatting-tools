# Development

This guide covers local validation and maintainer workflows for the Python CLI repository. User-facing conversion examples remain in [USAGE.md](USAGE.md).

## Environment

- Use Bash with Python 3.12 and run Python through `source source_me.sh && python3`.
- Install runtime and development dependencies from [../pip_requirements.txt](../pip_requirements.txt) and [../pip_requirements-dev.txt](../pip_requirements-dev.txt).
- Install Chromium when running table rendering or the real-generator E2E workflow.
- Keep temporary scripts, reproductions, and review renders under repository-root `_temp/`.
- Keep generated DOCX, YAML, media folders, and smoke outputs in the ignored paths described in [FILE_STRUCTURE.md](FILE_STRUCTURE.md).

## Test lanes

Run the fast suite after code changes:

```bash
source source_me.sh && python3 -m pytest tests/ -q
```

Run focused checks while developing, then run the relevant repository gates:

```bash
source source_me.sh && python3 -m pytest tests/test_bbq_parse.py tests/test_bbq_tasks.py -q
source source_me.sh && python3 -m pytest tests/test_markdown_links.py tests/test_ascii_compliance.py tests/test_pyflakes_code_lint.py -q
```

The real-generator workflow is intentionally outside the fast pytest lane. The
synthetic HTML-to-YAML-to-DOCX contract runs in pytest:

```bash
source source_me.sh && python3 tests/e2e/e2e_bbq_tasks_quiz.py
```

Permanent-test policy and fragile-test guidance live in [PYTEST_STYLE.md](PYTEST_STYLE.md); whole-system placement rules live in [E2E_TESTS.md](E2E_TESTS.md).

## Documentation checks

- Keep durable docs under `docs/` with uppercase underscore filenames.
- Run [../tests/test_markdown_links.py](../tests/test_markdown_links.py) after changing links.
- Run [../tests/test_readme_first_paragraph.py](../tests/test_readme_first_paragraph.py) after changing the README opening.
- Update [CHANGELOG.md](CHANGELOG.md) for repository changes, keeping day blocks in reverse chronological order.

## Release preparation

[../devel/make_release.py](../devel/make_release.py) prepares a manual source release from committed `HEAD`. The default is a dry run:

```bash
source source_me.sh && python3 devel/make_release.py --help
```

Without a `--notes-file`, the helper prints a release-note drafting prompt and exits before
release preparation. Use the current version from [../VERSION](../VERSION), not a copied older
version number. The write path requires a clean committed checkout. Human maintainers decide when to tag and publish. The release helper can write release docs only when explicitly run in its write mode; it does not create Git tags or commit changes.


## Visual formatting verification

- Keep the same representative assessment YAML/media when comparing choice-layout changes;
  inspect both dense text rows and drawing/matching questions.
- Use [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md) for font measurement and tab-slot ownership.
  Run its focused tests when changing measurement or selection.
- Export through [../converters/docx_to_pdf.sh](../converters/docx_to_pdf.sh). Commands that can
  invoke LibreOffice must run outside the sandbox on this macOS host.
- Inspect the resulting PDF; synthetic geometry tests do not verify final line wrapping.
- Inspect fresh full-suite failures before classifying them. Report environment failures and
  unrelated lint failures separately from focused layout validation; dated run results belong
  in [CHANGELOG.md](CHANGELOG.md).
