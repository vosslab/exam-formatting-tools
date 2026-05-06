# Exam formatting tools

Tools for building and converting styled exam documents. The current pipeline produces DOCX exams from a YAML definition or directly from cleaned Blackboard HTML exports, and converts third-party question banks (Blackboard `.bbq`, Oklahoma exports, Blackboard HTML) into the shared YAML exam format.

## Quick start

Build a styled DOCX exam from a YAML definition:

```bash
source source_me.sh && python3 docx_exam_builder.py -i exam_data.yaml -o exam_output.docx
```

Build a styled DOCX exam directly from cleaned Blackboard HTML exports:

```bash
source source_me.sh && python3 html_exam_docx_builder.py -i Final_Exam/Cleaned_Final_Exam_2A.html -o exam_output.docx -t "Final Exam"
```

Convert cleaned Blackboard HTML to exam YAML:

```bash
source source_me.sh && python3 html_to_exam_yaml.py -i Cleaned_Final_Exam_2A.html -o exam_2A.yaml
```

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
