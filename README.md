# Exam formatting tools

Tools for working with ODT exam documents -- extracting styles, propagating styles between files, and building fully styled exams from YAML input. Built for instructors who maintain exam formatting consistency across semesters using LibreOffice.

## Quick start

Build an exam from a YAML definition:

```bash
source source_me.sh && python3 odt_exam_builder.py -i exam_data.yaml -o exam_output.odt
```

Extract styles from an existing exam:

```bash
source source_me.sh && python3 extract_odt_styles.py -i exam.odt -o styles.yaml
```

Propagate styles from one exam to another:

```bash
source source_me.sh && python3 propagate_odt_styles.py -s source.odt -t target.odt
```

## Documentation

- [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md): Style definitions for page layouts, paragraphs, tables, and choice formatting.
- [docs/ROADMAP.md](docs/ROADMAP.md): Implementation plan and phasing for the four core tools.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): Change history.
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md): Repository structure, naming, and versioning conventions.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md): Python coding style rules.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md): Markdown formatting conventions.
- [docs/AUTHORS.md](docs/AUTHORS.md): Maintainers.
- [docs/CLAUDE_HOOK_USAGE_GUIDE.md](docs/CLAUDE_HOOK_USAGE_GUIDE.md): AI agent hook rules.

## Testing

```bash
source source_me.sh && python3 -m pytest tests/ -q
```
