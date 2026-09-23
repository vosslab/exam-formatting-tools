# Roadmap

This roadmap records evidence-backed follow-up work for the source-to-YAML-to-DOCX exam pipeline. Current commands and supported behavior live in [USAGE.md](USAGE.md); unresolved symptoms belong in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Current state

- Seven launchers cover BBQ task CSV, BBQ text, DOCX, Blackboard HTML, Oklahoma, ZipGrade validation, and YAML-to-DOCX conversion.
- Matching prompts and choices can carry images, including rendered table drawings, pedigrees, and sequence strips.
- The DOCX builder reads layout values from [../styles/exam_styles.yaml](../styles/exam_styles.yaml).
- The 2026-09-23 changelog records the ordered-statement contract, task-CSV workflow, and automated HTML/task-CSV-to-DOCX checks.
- The fast pytest lane covers synthetic HTML-to-YAML-to-DOCX and task-CSV-to-YAML-to-DOCX transitions, including color, media paths, authored order, alias selection, and answer-key output.

## Automated completion gates

- Run `source source_me.sh && python3 -m pytest tests/` for the self-contained contract and rendering checks.
- Run `source source_me.sh && python3 tests/e2e/e2e_bbq_tasks_quiz.py` when the sibling biology-problems repository is available; its real-generator run adds evidence but is not a human sign-off gate.
- Keep the image-choice measurement script as a debug harness. Layout behavior that affects generated DOCX remains covered by automated geometry tests.

## Out of scope

- Direct ODT output is not part of the current printable pipeline.
- A one-shot HTML-to-DOCX path is not planned; use `html_to_exam_yaml.py` followed by `yaml_to_exam_docx.py`.
- Automatic trimming of six-choice questions is not planned because the YAML format does not store enough answer-key information to choose a distractor safely.
