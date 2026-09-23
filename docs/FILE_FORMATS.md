# File formats

This reference lists the source files accepted by the launchers and the artifacts they write. The field-level exam YAML contract remains in [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).

## Input formats

- Cleaned Blackboard HTML uses `.html` or `.htm` and is read by [html_to_exam_yaml.py](../launchers/html_to_exam_yaml.py).
- bptools BBQ text uses `.txt` and is read by [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py).
- Website task CSV uses `.csv` with `subject,topic,script,flags,input,notes` and may add the local `choice_font` column; [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) resolves aliases from [../bbq_settings.yml](../bbq_settings.yml).
- Oklahoma exports use `.txt` and are read by [okla_to_exam_yaml.py](../launchers/okla_to_exam_yaml.py).
- Existing exam DOCX files use `.docx` and are read by [docx_to_exam_yaml.py](../launchers/docx_to_exam_yaml.py).
- Exam YAML uses `.yml` or `.yaml` and is read by [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py) and [validate_zip_grade_yaml.py](../launchers/validate_zip_grade_yaml.py).

## Generated outputs

- YAML converters write an exam YAML file and report its question count.
- BBQ converters also write `<stem>-key.txt` and `<stem>_files/*.png` for answer keys and rendered tables.
- The task-CSV converter writes skipped-task messages to stderr and keeps the successful questions in the YAML.
- [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py) writes a printable `.docx` document.
- ZipGrade filtering writes a new YAML only when `-o` is provided; it never edits the source file.

## Path rules

- Image paths in YAML are relative to the YAML file. The DOCX builder resolves them against that file's directory.
- Generated media stays beside the YAML in `<stem>_files/` so a YAML file and its images can move together.
- Output files that already exist are rejected by the writers; write to a new path or use the documented `/tmp/` regeneration flow.
- Generated DOCX, YAML, ODT, and output directories are ignored by Git. The tracked exception is [../styles/exam_styles.yaml](../styles/exam_styles.yaml).
