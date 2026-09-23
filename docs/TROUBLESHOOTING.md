# Troubleshooting

Use this guide for failures reported by the launchers or by the repository's documented conversion paths. It records current behavior from the scripts and tests rather than speculative fixes.

## Missing sibling dependency

- Symptom: `source_me.sh` warns that `qti-package-maker` is not found, or a BBQ converter raises an import error for `qti_package_maker`.
- Cause: BBQ table rendering and task generation use the sibling checkout at `~/nsh/PROBLEMS/qti-package-maker`.
- Fix: obtain that checkout at the configured path, or update the `qti_package_maker` path in [../bbq_settings.yml](../bbq_settings.yml) and rerun the bootstrap.
- Scope: HTML-to-YAML, Oklahoma-to-YAML, DOCX-to-YAML, and YAML-to-DOCX do not need the biology generator tree.

## Chromium is unavailable

- Symptom: table rasterization or the real-generator E2E workflow cannot launch a browser.
- Cause: the Python Playwright package is installed without its Chromium browser.
- Fix: run `playwright install chromium` after installing [../pip_requirements.txt](../pip_requirements.txt).

## Output path collisions

- Some converters refuse to overwrite an existing output, while others replace it. Check the selected launcher's behavior before reusing a path.
- For an output that must be preserved, choose a new `-o` path and compare the generated artifact before replacing the original.

## No usable questions

- Symptom: `bbq_tasks_to_exam_yaml.py` reports skipped tasks or raises that no usable questions remain.
- Cause: generators may emit skipped types such as NUM, FIB, or FIB_PLUS, or exam mode may reject questions that do not fit the ZipGrade A-E rules.
- Fix: inspect the stderr skip reason, change the source task flags when appropriate, or run quiz mode when a non-ZipGrade question is intentional.

## ZipGrade issues

- Symptom: `validate_zip_grade_yaml.py` reports `ERROR` or `FIXABLE` issues.
- Cause: the form accepts five lettered choices per row and at most 100 numbered rows; matching blocks consume one row per prompt.
- Fix: edit the authored YAML or source question deliberately, then rerun the validator. `--zip-grade` removes nonconforming questions from the DOCX input but does not silently truncate choices.

## Missing or misplaced images

- Symptom: a DOCX build cannot find an image, or a drawing appears after the statement instead of at its source position.
- Cause: a statement image path does not resolve from the YAML file's directory, or the exam YAML does not preserve the source order of its statement blocks.
- Fix: give each `{image: ...}` block a path relative to the YAML file. The HTML importer rewrites source-image paths during conversion, and the DOCX builder emits text, drawings, and tables in block order. The automated synthetic pipeline case is in `tests/test_html_to_docx_pipeline.py`.
