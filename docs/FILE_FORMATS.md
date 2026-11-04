# File formats

This reference lists the source files accepted by the converters and the artifacts they write. The field-level exam YAML contract remains in [YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md).

## Input formats

- Cleaned Blackboard HTML uses `.html` or `.htm` and is read by [html_to_exam_yaml.py](../converters/html_to_exam_yaml.py).
- bptools BBQ text uses `.txt` and is read by [bbq_to_exam_yaml.py](../converters/bbq_to_exam_yaml.py).
- Website task CSV uses `.csv` with `subject,topic,script,flags,input,notes` and may add local `choice_font` and `layout` columns; [bbq_tasks_to_exam_yaml.py](../converters/bbq_tasks_to_exam_yaml.py) resolves aliases from [../bbq_settings.yml](../bbq_settings.yml).
- Oklahoma exports use `.txt` and are read by [okla_to_exam_yaml.py](../converters/okla_to_exam_yaml.py).
- Existing exam DOCX files use `.docx` and are read by [docx_to_exam_yaml.py](../converters/docx_to_exam_yaml.py).
- Exam YAML uses `.yml` or `.yaml` and is read by [yaml_to_exam_docx.py](../converters/yaml_to_exam_docx.py) and [validate_zip_grade_yaml.py](../converters/validate_zip_grade_yaml.py).

## Generated outputs

- YAML converters write an exam YAML file and report its question count.
- BBQ converters also write `<stem>-key.txt` and `<stem>_files/` SVG/PNG assets for answer keys and captured visuals.
- The task-CSV converter writes skipped-task messages to stderr and keeps the successful questions in the YAML.
- [yaml_to_exam_docx.py](../converters/yaml_to_exam_docx.py) writes a printable `.docx` document.
- [docx_to_pdf.sh](../converters/docx_to_pdf.sh) exports PDF through LibreOffice and replaces the
  matching PDF in the supplied destination. It does not create an ODT intermediate.
- ZipGrade filtering writes a new YAML only when `-o` is provided; it never edits the source file.

## Path rules

- Image paths in YAML are relative to the YAML file. The DOCX builder resolves them against that file's directory.
- Generated media stays beside the YAML in `<stem>_files/` so a YAML file and its images can move together.
- Overwrite policy depends on the command: HTML-to-YAML, YAML-to-DOCX, and filtered-YAML output reject existing destinations; shared BBQ YAML writing replaces its output. Assessment builders may explicitly remove prior files or output directories. Preserve edits and use a fresh path under repository-root `_temp/` for comparisons.
- Generated DOCX, YAML, ODT, and output directories are ignored by Git. The tracked exception is [../assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).


## Document modes and formatting

- YAML `document_type` distinguishes exam, quiz, and handout presentation. Handouts omit grading
  fields and can include supported paper answer blanks.
- Questions store ordered text, image, and table blocks. Image blocks can also retain source
  `html_table` markup for the optional native-table path.
- Paragraph styles and tab geometry are configured by
  [../assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).
  Text choices use the measurements documented in [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md).
- Specialized composition builders may additionally save scientific setup snapshots and
  explained answer keys. Keep assessment-specific outputs and regeneration instructions in
  the corresponding notes under [../assessment_styles/](../assessment_styles/).
