# Usage

All commands assume the bootstrap pattern `source source_me.sh && python3 ...`.

## Build a DOCX exam from YAML

```bash
source source_me.sh && python3 docx_exam_builder.py \
    -i exam_data.yaml \
    -o exam_output.docx
```

The YAML schema is documented in [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).
Style definitions come from [styles/exam_styles.yaml](../styles/exam_styles.yaml).

## Build a DOCX exam directly from cleaned Blackboard HTML

Combine one or more cleaned HTML exports into a single styled DOCX exam:

```bash
source source_me.sh && python3 html_exam_docx_builder.py \
    -i Final_Exam/Cleaned_Final_Exam_2A.html Final_Exam/Cleaned_Final_Exam_2B.html \
    -o final_combined.docx \
    -t "Final Exam"
```

Image-based answer choices are laid out horizontally using paragraph tab stops
(no DOCX tables); see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).

## Convert question banks to exam YAML

Blackboard cleaned HTML to YAML:

```bash
source source_me.sh && python3 html_to_exam_yaml.py \
    -i Cleaned_Final_Exam_2A.html \
    -o exam_2A.yaml
```

Matching questions are emitted as `prompts_list` plus `choices_list`; see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) for the schema.

RDKit HTML5 canvas widgets in the cleaned HTML are auto-rendered to PNG (named `rdkit_<canvas_id>.png`) inside the existing Blackboard `*_files/` directory and emitted as standard `images:` entries; nothing extra to configure on the command line.

Blackboard `.bbq` export to YAML:

```bash
source source_me.sh && python3 bbq_to_exam_yaml.py -i export.bbq -o exam.yaml
```

Oklahoma export to YAML:

```bash
source source_me.sh && python3 okla_to_exam_yaml.py -i export.txt -o exam.yaml
```

## Convert DOCX back to YAML

```bash
source source_me.sh && python3 docx_to_exam_yaml.py -i exam.docx -o exam.yaml
```

## Run the test suite

Full suite:

```bash
source source_me.sh && python3 -m pytest tests/ -q
```

Focused (single file or `-k` filter):

```bash
source source_me.sh && python3 -m pytest tests/test_html_to_exam_yaml.py -q
source source_me.sh && python3 -m pytest tests/ -k docx_builder -q
```

Repo-wide lint gates:

```bash
source source_me.sh && python3 -m pytest \
    tests/test_pyflakes_code_lint.py \
    tests/test_import_requirements.py \
    tests/test_ascii_compliance.py -q
```
