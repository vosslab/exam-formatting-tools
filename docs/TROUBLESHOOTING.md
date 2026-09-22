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

## Output already exists

- Symptom: a launcher raises `FileExistsError` for the requested YAML or DOCX output.
- Cause: the conversion tools protect existing authored or generated files instead of overwriting them.
- Fix: choose a new `-o` path. For regeneration, write to `/tmp/` and copy the verified artifact into place as shown in [USAGE.md](USAGE.md).

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
- Cause: image paths are resolved relative to the YAML file, and table images are currently appended after cleaned statement text.
- Fix: keep `<stem>_files/` beside the YAML and check the paths described in [FILE_FORMATS.md](FILE_FORMATS.md). Mid-statement placement is a tracked roadmap item.
