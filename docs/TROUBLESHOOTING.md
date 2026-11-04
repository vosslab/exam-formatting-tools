# Troubleshooting

Use this guide for failures reported by the converters or by the repository's documented conversion paths. It records current behavior from the scripts and tests rather than speculative fixes.

## Missing sibling dependency

- Symptom: a task-CSV generator subprocess cannot import `bptools` or `qti_package_maker`.
- Cause: question generation uses sibling checkouts configured in [../bbq_settings.yml](../bbq_settings.yml).
- Fix: obtain those checkouts or correct their configured paths.
- Scope: formatting existing BBQ, HTML, or YAML does not require those checkouts.

## Chromium is unavailable

- Symptom: table rasterization or the real-generator E2E workflow cannot launch a browser.
- Cause: the Python Playwright package is installed without its Chromium browser.
- Fix: run `playwright install chromium` after installing [../pip_requirements.txt](../pip_requirements.txt).

## Output path collisions

- Some converters refuse to overwrite an existing output, while others replace it. Check the selected launcher's behavior before reusing a path.
- For an output that must be preserved, choose a new `-o` path and compare the generated artifact before replacing the original.

## No usable questions

- Symptom: `bbq_tasks_to_exam_yaml.py` reports skipped tasks or raises that no usable questions remain.
- Cause: NUM, FIB, and FIB_PLUS are skipped outside handout mode, or exam mode rejects questions that do not fit the ZipGrade A-E rules.
- Fix: inspect the reported skip reason. Use `--handout` for supported paper answer blanks; use quiz mode when a non-ZipGrade question is intentional.

## ZipGrade issues

- Symptom: `validate_zip_grade_yaml.py` reports `ERROR` or `FIXABLE` issues.
- Cause: the form accepts five lettered choices per row and at most 100 numbered rows; matching blocks consume one row per prompt.
- Fix: edit the authored YAML or source question deliberately, then rerun the validator. `--zip-grade` removes nonconforming questions from the DOCX input but does not silently truncate choices.

## Missing or misplaced images

- Symptom: a drawing is absent, or appears at the wrong position in the question. Missing statement image files are currently omitted by the DOCX builder.
- Cause: a statement image path does not resolve from the YAML file's directory, or the exam YAML does not preserve the source order of its statement blocks.
- Fix: give each `{image: ...}` block a path relative to the YAML file. The HTML importer rewrites source-image paths during conversion, and the DOCX builder emits text, drawings, and tables in block order. The automated synthetic pipeline case is in `tests/test_html_to_docx_pipeline.py`.


## LibreOffice and Chromium sandbox failures

- LibreOffice crashes when launched inside this host's sandbox. Run commands that can invoke
  it outside the sandbox using the repository scripts, including PDF conversion checks.
- Chromium's `bootstrap_check_in ... Permission denied` can also be a macOS sandbox restriction.
  Distinguish that error from an absent browser installation before changing dependencies.
- Preserve source documents and use repository-root `_temp/` for reproduction files and renders.

## Choice wrapping or spacing

- Check for an explicit `layout` field first: it bypasses automatic font measurement and may
  force too many columns. A `choice_font` override also changes the width being measured.
- Confirm the configured fonts are installed and `fc-match` resolves the intended face. Font
  substitution in LibreOffice can invalidate the generator's measured fit.
- Consult [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md) for the per-slot calculation and fallback
  rules. Retain the exact YAML and paper size when reproducing a bad row.
- New choice paragraphs inherit spacing from named styles. Older generated documents may retain
  direct overrides; rebuilding does not migrate an instructor-edited DOCX in place.
