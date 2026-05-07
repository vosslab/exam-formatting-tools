# Usage

All commands assume the bootstrap pattern `source source_me.sh && python3 ...`.

## Pipeline

The pipeline is `<source format> -> exam YAML -> DOCX`. Every root script
validates input/output extensions and reports the question count on success.
`-o/--output` is optional; when omitted, the output is `<input-stem>` with
the target extension in the current working directory.

## Build a DOCX exam from YAML

```bash
source source_me.sh && python3 yaml_to_exam_docx.py -i exam_data.yml
```

The YAML schema is documented in [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).
Style definitions come from [styles/exam_styles.yaml](../styles/exam_styles.yaml).

Note: `yaml_to_exam_docx.py` refuses to overwrite an existing output file
(it raises `FileExistsError`). To regenerate a shipped DOCX, write the new
output to `/tmp/` first and then `cp` it into place:

```bash
source source_me.sh && python3 yaml_to_exam_docx.py \
    -i Final_Exam/Final_Exam_2A_2B_combined.yml \
    -o /tmp/_regen_combined.docx
cp /tmp/_regen_combined.docx Final_Exam/Final_Exam_2A_2B_combined.docx
```

Image-based answer choices are laid out horizontally using paragraph tab stops
(no DOCX tables); see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).

## Convert question banks to exam YAML

Blackboard cleaned HTML to YAML (one or more files; first input's stem
drives the default output name):

```bash
source source_me.sh && python3 html_to_exam_yaml.py -i Cleaned_Final_Exam_2A.html
```

Matching questions are emitted as `prompts_list` plus `choices_list`; see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) for the schema.

RDKit HTML5 canvas widgets in the cleaned HTML are auto-rendered to PNG (named `rdkit_<canvas_id>.png`) inside the existing Blackboard `*_files/` directory and emitted as standard `images:` entries; nothing extra to configure on the command line.

Blackboard `.bbq` export to YAML:

```bash
source source_me.sh && python3 bbq_to_exam_yaml.py -i export.txt
```

Oklahoma export to YAML:

```bash
source source_me.sh && python3 okla_to_exam_yaml.py -i export.txt
```

## Convert DOCX back to YAML

```bash
source source_me.sh && python3 docx_to_exam_yaml.py -i exam.docx
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
