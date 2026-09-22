# Usage

All commands assume the bootstrap pattern `source source_me.sh && python3 ...`.

## Pipeline

The pipeline is `<source format> -> exam YAML -> DOCX`. Every root script
validates input/output extensions and reports the question count on success.
`-o/--output` is optional; when omitted, the output is `<input-stem>` with
the target extension in the current working directory.

## Build a DOCX exam from YAML

```bash
source source_me.sh && python3 launchers/yaml_to_exam_docx.py -i exam_data.yml
```

The YAML schema is documented in [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).
Style definitions come from [styles/exam_styles.yaml](../styles/exam_styles.yaml).

Note: `yaml_to_exam_docx.py` refuses to overwrite an existing output file
(it raises `FileExistsError`). To regenerate a shipped DOCX, write the new
output to `/tmp/` first and then `cp` it into place:

```bash
source source_me.sh && python3 launchers/yaml_to_exam_docx.py \
    -i Final_Exam/Final_Exam_2A_2B_combined.yml \
    -o /tmp/_regen_combined.docx
cp /tmp/_regen_combined.docx Final_Exam/Final_Exam_2A_2B_combined.docx
```

Image-based answer choices are laid out horizontally using paragraph tab stops
(no DOCX tables); see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md).

## Validate ZipGrade compatibility

ZipGrade 100-question bubble forms accept five lettered choices per row
(A-E) for up to 100 rows. Two tools enforce this:

`validate_zip_grade_yaml.py` reports incompatible questions by source line
number. Each issue is labeled `ERROR` (cannot fit ZipGrade without a
rewrite) or `FIXABLE` (likely editable to fit). Both are non-OK; the
linter exits non-zero unless every question is OK.

```bash
source source_me.sh && python3 launchers/validate_zip_grade_yaml.py -i exam.yml
```

Pass `-o` to write a filtered YAML containing only OK questions (drops
both ERROR and FIXABLE; the original YAML is not modified):

```bash
source source_me.sh && python3 launchers/validate_zip_grade_yaml.py \
    -i exam.yml -o exam_zipgrade.yml
```

`yaml_to_exam_docx.py --zip-grade` (or `-z`) builds a DOCX containing
only ZipGrade-compatible questions in one shot. It also drops both ERROR
and FIXABLE, prints a per-question removal report (line-anchored), and
warns if the post-filter row total still exceeds 100:

```bash
source source_me.sh && python3 launchers/yaml_to_exam_docx.py -i exam.yml -z
```

The flag never silently rewrites questions. A 6-choice question is
classified `FIXABLE` (the author may drop one distractor by hand) but is
removed from the DOCX, not auto-truncated -- the YAML schema does not
store the correct answer, so tooling cannot pick which option to drop.

## Convert question banks to exam YAML

Blackboard cleaned HTML to YAML (one or more files; first input's stem
drives the default output name):

```bash
source source_me.sh && python3 launchers/html_to_exam_yaml.py -i Cleaned_Final_Exam_2A.html
```

Matching questions are emitted as `prompts_list` plus `choices_list`; see [docs/YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) for the schema.

RDKit HTML5 canvas widgets in the cleaned HTML are auto-rendered to PNG (named `rdkit_<canvas_id>.png`) inside the existing Blackboard `*_files/` directory and emitted as standard `images:` entries; nothing extra to configure on the command line.

bptools bbq text (`bbq-*-questions.txt`) to YAML plus an answer key:

```bash
source source_me.sh && python3 launchers/bbq_to_exam_yaml.py -i bbq-chargaff-questions.txt
```

MC and MA keep their choices; MAT becomes `prompts_list` plus a shuffled
`choices_list`; ORD becomes position blanks (`Position 1`, `Position 2`, ...)
plus shuffled items. NUM, FIB, and FIB_PLUS have no print form and are
skipped. Drawing tables (gels, chi-square tables) are rendered to
`<stem>_files/*.png` through the sibling `qti-package-maker` checkout (see
[docs/INSTALL.md](INSTALL.md)). The answer key lands in `<stem>-key.txt`.

## Build a quiz or exam from a bptools task CSV

`bbq_tasks_to_exam_yaml.py` reads the website task CSV format unchanged
(`subject,topic,script,flags,input,notes`; `{bp_root}`/`YMATCH`-style aliases
come from the repo's [bbq_settings.yml](../bbq_settings.yml), a copy of the
website's; pass `-s` to use another) and contributes **one question per
resolved task**. A
list alias such as `YMATCH` expands to two scripts and therefore two
questions. Each generator runs with `-d 1 -x 1`; an unusable candidate
(skipped bbq type, or exam-mode rejection) triggers a fresh run, up to three
attempts, then the task is reported as `SKIPPED` on stderr and left out.

```csv
subject,topic,script,flags,input,notes
genetics,dna_structure,{bp_root}/molecular_biology-problems/chargaff_dna_percent.py,,,
genetics,dna_structure,YMCS,,{bp_mcs}/biochemistry/dna_structure.yml,
genetics,mendelian,YMATCH,,{bp_match}/inheritance/genetics_terminology.yml,
genetics,dna_profiling,{bp_root}/dna_profiling-problems/who_father_html.py,--easy,,
```

Quiz (default: any MC/MA/MAT/ORD, any number of choices):

```bash
source source_me.sh && python3 launchers/bbq_tasks_to_exam_yaml.py -q -t "Genetics Quiz 1" \
    -i ~/nsh/PROBLEMS/biology-problems-website/bbq_control/task_files/genetics_tasks1.csv \
    -o output_quiz/genetics_quiz1.yml
source source_me.sh && python3 launchers/yaml_to_exam_docx.py -i output_quiz/genetics_quiz1.yml
```

Exam (`-e`): only questions that pass the ZipGrade A-E rules are kept;
generators with fixed six-choice flags (`-c 6`) are skipped after three
attempts, so edit their flags in the CSV.

Outputs: `<stem>.yml`, `<stem>-key.txt` (one line per question block, e.g.
`1. B   c555_9c1d   chargaff_dna_percent.py` or
`Q5-8. 5=C 6=A 7=D 8=B   ce62_1dbe   yaml_match_to_bbq.py (genetic_disorders)`),
and `<stem>_files/*.png` for rendered tables. The CSV `topic` column becomes
the chapter heading whenever it changes.

Oklahoma export to YAML:

```bash
source source_me.sh && python3 launchers/okla_to_exam_yaml.py -i export.txt
```

## Convert DOCX back to YAML

```bash
source source_me.sh && python3 launchers/docx_to_exam_yaml.py -i exam.docx
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
