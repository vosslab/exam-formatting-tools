# Install

Installation makes the local Python dependencies available and enables the launcher commands. The core HTML, DOCX, and Oklahoma conversions use the dependencies in [../pip_requirements.txt](../pip_requirements.txt); BBQ table conversion adds sibling-repository requirements.

## Requirements

- Python 3.12 is the documented working runtime.
- Bash is required for [../source_me.sh](../source_me.sh), which loads the repository environment and sets `PYTHONPATH`.
- Runtime packages come from [../pip_requirements.txt](../pip_requirements.txt); development tools come from [../pip_requirements-dev.txt](../pip_requirements-dev.txt).
- Playwright Chromium is needed when BBQ drawing tables are rasterized.

## Install steps

From the repository root, install runtime and development dependencies:

```bash
source source_me.sh
python3 -m pip install -r pip_requirements.txt
python3 -m pip install -r pip_requirements-dev.txt
playwright install chromium
```

The `playwright install chromium` step is needed for table-image rendering and the real-generator E2E workflow. It is not needed for a YAML-to-DOCX run that already has its image files.

## Sibling repositories

The BBQ converters import `qti_package_maker.html_to_image` and may run generators from `biology-problems`:

- `~/nsh/PROBLEMS/qti-package-maker` is added to `PYTHONPATH` by [../source_me.sh](../source_me.sh) when present.
- The `paths` section of [../bbq_settings.yml](../bbq_settings.yml) points at the `biology-problems` generator tree and can be overridden with `-s`.
- The HTML-to-YAML and YAML-to-DOCX paths do not require the biology-problems generator tree.

## Verify install

Check the runtime imports and launcher help:

```bash
source source_me.sh && python3 -c "import lxml, PIL, docx, yaml, rdkit, playwright"
source source_me.sh && python3 launchers/yaml_to_exam_docx.py --help
```

For the repository test lane, use the commands in [DEVELOPMENT.md](DEVELOPMENT.md).
