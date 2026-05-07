# Exam formatting tools

Tools for building and converting styled exam documents. The pipeline is one-way: third-party question banks (Blackboard `.bbq`, Oklahoma exports, Blackboard HTML, DOCX) are converted into the shared YAML exam format, and `yaml_to_exam_docx.py` produces the final styled DOCX from that YAML.

## Quick start

Convert cleaned Blackboard HTML to exam YAML, then build a styled DOCX:

```bash
source source_me.sh && python3 html_to_exam_yaml.py -i Cleaned_Final_Exam_2A.html
source source_me.sh && python3 yaml_to_exam_docx.py -i Cleaned_Final_Exam_2A.yml
```

`-o` is optional on every script. When omitted, output is `<input-stem>` with the target extension in the current directory.

## Documentation

- [docs/INSTALL.md](docs/INSTALL.md): Setup steps and dependencies.
- [docs/USAGE.md](docs/USAGE.md): How to run each script with practical examples.
- [docs/YAML_EXAM_FORMAT.md](docs/YAML_EXAM_FORMAT.md): Exam YAML schema and rendering rules.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): Change history.
- [docs/ROADMAP.md](docs/ROADMAP.md): Planned and in-progress work.
- [docs/AUTHORS.md](docs/AUTHORS.md): Maintainers.
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md): Repository structure and naming.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md): Python coding style.
- [docs/PYTEST_STYLE.md](docs/PYTEST_STYLE.md): Pytest writing rules.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md): Markdown formatting.

## Testing

```bash
source source_me.sh && python3 -m pytest tests/ -q
```
