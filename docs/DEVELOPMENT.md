# Development

This guide covers local validation and maintainer workflows for the Python CLI repository. User-facing conversion examples remain in [USAGE.md](USAGE.md).

## Environment

- Use Bash and run Python through `source source_me.sh && python3`.
- Install runtime and development dependencies from [../pip_requirements.txt](../pip_requirements.txt) and [../pip_requirements-dev.txt](../pip_requirements-dev.txt).
- Install Chromium when running table rendering or the real-generator E2E workflow.
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

The real-generator workflow is intentionally outside the fast pytest lane:

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
source source_me.sh && python3 devel/make_release.py 26.09 --dry-run
```

Human maintainers decide when to tag and publish. The release helper can write release docs only when explicitly run in its write mode; it does not create Git tags or commit changes.
