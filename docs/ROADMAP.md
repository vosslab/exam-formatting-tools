# Roadmap

Forward-looking work for `exam-formatting-tools`. Current pipeline is
`<source format> -> exam YAML -> DOCX`; for setup and command-line usage
see [INSTALL.md](INSTALL.md) and [USAGE.md](USAGE.md).

## Current state

- DOCX is the printable output. Builders read styles from
  [styles/exam_styles.yaml](../styles/exam_styles.yaml) and emit Word documents
  via [yaml_to_exam_docx.py](../yaml_to_exam_docx.py).
- Five converter scripts feed the YAML stage: BBQ, DOCX, HTML, Oklahoma, and the
  reverse DOCX-to-YAML round-trip.
- ZipGrade compatibility tooling lives in
  [validate_zip_grade_yaml.py](../validate_zip_grade_yaml.py) and the
  `--zip-grade` flag on `yaml_to_exam_docx.py`.

## Near-term

- Image-choice layout tuning is data-driven via `tools/measure_image_choices.py`;
  re-run after any change to `IMAGE_CHOICE_MAX_WIDTH_BY_COLS`,
  `layout_tab_stops`, or `choice_indent`.
- Keep [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) in sync with the
  qti-package-maker mapping notes when round-trip rules shift.

## Known gaps

- `docs/TROUBLESHOOTING.md` would help with recurring DOCX rendering
  surprises (refuse-to-overwrite policy, image-choice column counts).

## Out of scope

- Direct ODT output. The legacy ODT pipeline was removed; do not
  reintroduce it. Word-compatible DOCX is the only printable target.
- Re-adding a one-shot HTML-to-DOCX path. The two-step
  `html_to_exam_yaml.py` + `yaml_to_exam_docx.py` pipeline is the
  supported flow (see `docs/CHANGELOG.md` 2026-05-07).
