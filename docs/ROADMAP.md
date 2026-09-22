# Roadmap

This roadmap records evidence-backed follow-up work for the source-to-YAML-to-DOCX exam pipeline. Current commands and supported behavior live in [USAGE.md](USAGE.md); unresolved symptoms belong in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Current state

- Seven launchers cover BBQ task CSV, BBQ text, DOCX, Blackboard HTML, Oklahoma, ZipGrade validation, and YAML-to-DOCX conversion.
- Matching prompts and choices can carry images, including rendered table drawings, pedigrees, and sequence strips.
- The DOCX builder reads layout values from [../styles/exam_styles.yaml](../styles/exam_styles.yaml).
- The 2026-09-21 changelog records the current task-CSV, answer-key, table-rendering, and E2E workflow.

## Near-term

- Add a real end-to-end check for the Blackboard HTML path, which currently relies on the manual smoke commands in [USAGE.md](USAGE.md).
- Preserve source placement when table images occur in the middle of a statement instead of appending them after the cleaned text.
- Keep the task-CSV acceptance run aligned with the website's current task files and generator flags.
- Re-run [../devel/measure_image_choices.py](../devel/measure_image_choices.py) when image-choice caps, tab stops, or choice indentation changes.

## Out of scope

- Direct ODT output is not part of the current printable pipeline.
- A one-shot HTML-to-DOCX path is not planned; use `html_to_exam_yaml.py` followed by `yaml_to_exam_docx.py`.
- Automatic trimming of six-choice questions is not planned because the YAML format does not store enough answer-key information to choose a distractor safely.
