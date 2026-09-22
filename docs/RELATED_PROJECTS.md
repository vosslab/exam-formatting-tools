# Related projects

Sibling repositories that integrate with `exam-formatting-tools` or
share its pipeline conventions.

## qti-package-maker

- Repository: https://github.com/vosslab/qti-package-maker
- Role: Builds QTI packages and bbq_text exports from authored question
  banks. Its `MATCH(question_text, prompts_list, choices_list)` and MC
  item shape are the source of the matching schema in
  [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).
- How this repo uses it: bbq_text from qti-package-maker is the input
  to [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py); the YAML schema in
  [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) is designed to be a
  lossy-but-faithful print export of qti-package-maker items (see the
  "qti-package-maker compatibility" section of that file for the field
  mapping).
- Recommended pipeline for print exams: source format -> qti-package-maker
  -> bbq_text -> [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py) -> exam YAML
  -> [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py) -> DOCX.
- Imported at runtime: [ef_tools/bbq_html.py](../ef_tools/bbq_html.py)
  uses `qti_package_maker.html_to_image.selectors` (drawing-table detector)
  and `qti_package_maker.html_to_image.render_table.TableRenderer`
  (headless Chromium screenshot) to turn bptools gel and data-drawing
  tables into PNGs. The sibling checkout at `~/nsh/PROBLEMS/qti-package-maker`
  is added to `PYTHONPATH` by `source_me.sh`; see [INSTALL.md](INSTALL.md).

## biology-problems

- Repository: https://github.com/vosslab/biology-problems
- Role: Authoring repository for biology question banks; uses
  qti-package-maker via `bptools` to emit BBQ/QTI output.
- How this repo uses it: biology-problems is one upstream content
  source for the converters in this repo, and
  [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) runs its
  generator scripts directly (`-d 1 -x 1`) to build a quiz with one
  question per task. The repo style and Python conventions are kept in
  sync with biology-problems' style guides (tabs, snake_case, no
  try/except, etc.).

## biology-problems-website

- Repository: https://github.com/vosslab/biology-problems-website
- Role: MkDocs site that batch-runs bptools generators from task CSVs
  (`bbq_control/task_files/*.csv`, aliases in `bbq_control/bbq_settings.yml`).
- How this repo uses it: the same task CSV and settings file feed
  [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) unchanged;
  [ef_tools/bbq_tasks.py](../ef_tools/bbq_tasks.py) mirrors the CSV
  contract of its `run_bbq_tasks.py`.

## Known gaps

- Add direct links once `docs/COOKBOOK.md` exists and shows a full
  source-to-print example.
