# Install

Installation prepares the local converter commands. The supported printable path is YAML to DOCX, then direct DOCX to PDF with LibreOffice; it does not create or modify an ODT intermediate. The core HTML, DOCX, and Oklahoma conversions use [../pip_requirements.txt](../pip_requirements.txt); task-CSV generation additionally uses sibling repositories.

## Requirements

- Python 3.12 is the documented working runtime.
- Bash is required for [../source_me.sh](../source_me.sh), which loads the repository environment and sets `PYTHONPATH`.
- Runtime packages come from [../pip_requirements.txt](../pip_requirements.txt); development tools come from [../pip_requirements-dev.txt](../pip_requirements-dev.txt).
- Playwright Chromium is needed to capture HTML tables, MathML, and JavaScript canvases.
- Poppler's `pdftocairo` enables SVG capture (`brew install poppler` on macOS,
  or `apt install poppler-utils` on Debian). Without it, captures use PNG and report a warning.
- PDF export requires LibreOffice installed at `/Applications/LibreOffice.app`; the supplied export script invokes that application directly.
- Fontconfig is required for automatic text-choice layout. The repository [../Brewfile](../Brewfile) declares `fontconfig`; `fc-match` resolves the installed assessment font faces that Pillow measures.

## Install steps

From the repository root, install runtime and development dependencies:

```bash
source source_me.sh
python3 -m pip install -r pip_requirements.txt
python3 -m pip install -r pip_requirements-dev.txt
playwright install chromium
```

The `playwright install chromium` step is needed for table-image rendering and the real-generator E2E workflow. It is not needed for a YAML-to-DOCX run that already has its image files. On macOS, install the declared system tools with `brew bundle`; install LibreOffice separately if it is not already present.

## Sibling repositories

Formatting saved BBQ or HTML content does not require QPM or Biology Problems. Task-CSV generation still runs BP generators, which depend on QPM:

- The configured `paths.qti_package_maker` checkout is added only to generator subprocesses' `PYTHONPATH`.
- The `paths` section of [../bbq_settings.yml](../bbq_settings.yml) points at the `biology-problems` generator tree and can be overridden with `-s`.
- The HTML-to-YAML and YAML-to-DOCX paths do not require the biology-problems generator tree.

## Verify install

Check the runtime imports and the DOCX launcher:

```bash
source source_me.sh && python3 -c "import lxml, PIL, docx, yaml, playwright"
source source_me.sh && python3 converters/yaml_to_exam_docx.py --help
```

For the repository test lane, use the commands in [DEVELOPMENT.md](DEVELOPMENT.md).

## Choice font measurement

Keep the configured fonts installed on the generation and LibreOffice machines; substituted fonts may have different widths. Text-choice layout measures the resolved regular, bold, italic, and monospace faces, including named variable-font instances. See [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md) for the measurement and slot-selection rules.

## Known gaps

- TODO: verify the documented LibreOffice application path if PDF export is needed on a nonstandard macOS installation.
