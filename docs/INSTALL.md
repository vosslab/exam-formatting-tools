# Install

## Requirements

- Python 3.12 (Homebrew on macOS, or system Python on Linux)
- Bash shell (the bootstrap `source_me.sh` targets Bash semantics)

## Python dependencies

Install the runtime dependencies listed in [pip_requirements.txt](../pip_requirements.txt):

```bash
pip install -r pip_requirements.txt
```

Runtime packages:

- `lxml`: HTML and XML parsing for Blackboard exports.
- `pillow`: image I/O and aspect-ratio detection for inline answer images.
- `python-docx`: Word `.docx` reading and writing.
- `pyyaml`: YAML parsing and serialization.
- `rdkit`: cheminformatics toolkit; renders RDKit HTML5 canvas widgets to PNG when converting cleaned Blackboard exports. Installed via the `rdkit` pip wheel; no Homebrew formula required.
- `playwright`: headless Chromium that rasterizes bptools drawing tables (gels, chi-square
  tables) to PNG for the bbq converters. After the pip install, fetch the browser once:

```bash
playwright install chromium
```

## Sibling repositories (bbq converters only)

[bbq_tasks_to_exam_yaml.py](../bbq_tasks_to_exam_yaml.py) and
[bbq_to_exam_yaml.py](../bbq_to_exam_yaml.py) import `qti_package_maker.html_to_image` from a
sibling checkout and run generator scripts from `biology-problems`:

- `~/nsh/PROBLEMS/qti-package-maker` (added to `PYTHONPATH` by `source_me.sh` when present)
- `~/nsh/PROBLEMS/biology-problems` (path comes from the website `bbq_settings.yml`)

For development (running the test suite, linters), also install:

```bash
pip install -r pip_requirements-dev.txt
```

## Environment bootstrap

This repo uses a `source_me.sh` bootstrap script that exports `PYTHONUNBUFFERED=1`,
`PYTHONDONTWRITEBYTECODE=1`, and prepends the `qti-package-maker` sibling checkout to
`PYTHONPATH` when it exists. Run all repo-local Python via:

```bash
source source_me.sh && python3 <script>.py
```

## Verify the install

```bash
source source_me.sh && python3 -m pytest tests/ -q
```
