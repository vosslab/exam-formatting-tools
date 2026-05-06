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

For development (running the test suite, linters), also install:

```bash
pip install -r pip_requirements-dev.txt
```

## Environment bootstrap

This repo uses a `source_me.sh` bootstrap script that exports `PYTHONUNBUFFERED=1`,
`PYTHONDONTWRITEBYTECODE=1`, and adds the repo root to `PYTHONPATH`. Run all
repo-local Python via:

```bash
source source_me.sh && python3 <script>.py
```

## Verify the install

```bash
source source_me.sh && python3 -m pytest tests/ -q
```
