# Usage

All commands assume the bootstrap pattern `source source_me.sh && python3 ...`.

## Pipeline

The pipeline is `<source format> -> exam YAML -> DOCX`. Every launcher
validates input/output extensions and reports the question count on success.
`-o/--output` is optional; when omitted, the output is `<input-stem>` with
the target extension in the current working directory.

## Course builds

Course-specific build scripts live in `builders/`. Run them with Bash from the repository root.
Each is a flat sequence of common commands with explicit titles, task CSVs, and output paths.
Builds generate new random questions; edit the
generated YAML and use the converter directly to preserve an existing question selection.

| Build script | Task selection | Outputs |
| --- | --- | --- |
| [build_genetics_exam1.sh](../builders/build_genetics_exam1.sh) | [genetics_exam1.csv](../task_files/genetics_exam1.csv) | `output_genetics_exam1/genetics_exam1.*` |
| [build_genetics_quiz1.sh](../builders/build_genetics_quiz1.sh) | [genetics_quiz1.csv](../task_files/genetics_quiz1.csv) | `quiz1/quiz1.*` and `quiz1.pdf` |
| [build_genetics_quiz2.sh](../builders/build_genetics_quiz2.sh) | [genetics_quiz2.csv](../task_files/genetics_quiz2.csv) | `quiz2/quiz2.*` and `quiz2.pdf` |
| [build_biostats_quiz1.sh](../builders/build_biostats_quiz1.sh) | [biostats_quiz1.csv](../task_files/biostats_quiz1.csv) | `output_biostats_quiz1/biostats_quiz1.*` |
| [build_biochem_exam1_study_guide.sh](../builders/build_biochem_exam1_study_guide.sh) | [biochem_exam1.csv](../task_files/biochem_exam1.csv) | `bchem1/bchem1.*` and `bchem1.pdf` |

```bash
bash builders/build_genetics_exam1.sh
```

The Exam 1 build uses `--exam` and validates the resulting YAML against ZipGrade's A-E limit
before creating the DOCX and PDF. Read the generator's skipped-task report when building;
compatibility validation checks the questions produced, not coverage of the original task list.
Each build also writes a sibling `*-key.txt` answer key.

Shared presentation rules live in [EXAM_STYLE.md](../assessment_styles/EXAM_STYLE.md) and [QUIZ_STYLE.md](../assessment_styles/QUIZ_STYLE.md).
Assessment-specific coverage stays in the task CSV and selection notes, such as
[GENETICS_EXAM1.md](../assessment_styles/GENETICS_EXAM1.md).

## Build a DOCX exam from YAML

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py -i exam_data.yml
```

Use `--keep-questions-together` to keep each question's stem, figures, and answer bank together
when they fit on one page. Use `--page-break-sections` to start later sections on new pages.
The Genetics Exam 1 and biostatistics quiz recipes select these options where needed.

For a backup DOCX that converts preserved simple bptools HTML drawing tables
to native Word tables, add `--native-tables`. Unsupported or nested tables use
the normal PNG representation instead:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i exam_data.yml --native-tables -o /tmp/exam_native_tables.docx
```

The YAML schema is documented in [YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md).
Style definitions come from [assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).

Note: `yaml_to_exam_docx.py` refuses to overwrite an existing output file
(it raises `FileExistsError`). To regenerate a shipped DOCX, write the new
output to `/tmp/` first and then `cp` it into place:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i Final_Exam/Final_Exam_2A_2B_combined.yml \
    -o /tmp/_regen_combined.docx
cp /tmp/_regen_combined.docx Final_Exam/Final_Exam_2A_2B_combined.docx
```

Image-based answer choices are laid out horizontally using paragraph tab stops
by default; the optional native-table backup is described in
[YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md).

## Export DOCX to PDF

The shared [docx_to_pdf.sh](../converters/docx_to_pdf.sh) command exports through the existing
macOS LibreOffice installation with 70 percent JPEG quality and PDF 1.7. It takes a DOCX path,
an output directory, and an optional image DPI (default 100). It replaces that document's PDF.

```bash
bash converters/docx_to_pdf.sh output_exam/exam.docx output_exam 150
```

## Validate ZipGrade compatibility

ZipGrade 100-question bubble forms accept five lettered choices per row
(A-E) for up to 100 rows. Two tools enforce this:

`validate_zip_grade_yaml.py` reports incompatible questions by source line
number. Each issue is labeled `ERROR` (cannot fit ZipGrade without a
rewrite) or `FIXABLE` (likely editable to fit). Both are non-OK; the
linter exits non-zero unless every question is OK.

```bash
source source_me.sh && python3 converters/validate_zip_grade_yaml.py -i exam.yml
```

Pass `-o` to write a filtered YAML containing only OK questions (drops
both ERROR and FIXABLE; the original YAML is not modified):

```bash
source source_me.sh && python3 converters/validate_zip_grade_yaml.py \
    -i exam.yml -o exam_zipgrade.yml
```

`yaml_to_exam_docx.py --zip-grade` (or `-z`) builds a DOCX containing
only ZipGrade-compatible questions in one shot. It also drops both ERROR
and FIXABLE, prints a per-question removal report (line-anchored), and
warns if the post-filter row total still exceeds 100:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py -i exam.yml -z
```

The flag never silently rewrites questions. A 6-choice question is
classified `FIXABLE` (the author may drop one distractor by hand) but is
removed from the DOCX, not auto-truncated -- the YAML schema does not
store the correct answer, so tooling cannot pick which option to drop.

## Convert question banks to exam YAML

Blackboard cleaned HTML to YAML (one or more files; first input's stem
drives the default output name):

```bash
source source_me.sh && python3 converters/html_to_exam_yaml.py -i Cleaned_Final_Exam_2A.html
```

Matching questions are emitted as `prompts_list` plus `choices_list`; see [YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md) for the schema.

HTML drawing tables, MathML, and JavaScript-populated canvases are captured by the shared
Playwright renderer and saved beside the assessment. Existing images are embedded directly.
The browser runs authored scripts with their question context and source-relative resources;
required external scripts must be available. EF Tools does not reconstruct molecular drawings
or repair invalid HTML. No additional command-line options are needed.

bptools bbq text (`bbq-*-questions.txt`) to YAML plus an answer key:

```bash
source source_me.sh && python3 converters/bbq_to_exam_yaml.py -i bbq-chargaff-questions.txt
```

MC and MA keep their choices; MAT becomes `prompts_list` plus a shuffled
`choices_list`; ORD becomes position blanks (`Position 1`, `Position 2`, ...)
plus shuffled items. NUM, FIB, and FIB_PLUS have no print form and are
skipped. Drawing tables (gels, chi-square tables) are rendered to
`<stem>_files/*.png` through EF Tools' native Chromium renderer (see
[INSTALL.md](INSTALL.md)). The answer key lands in `<stem>-key.txt`.

Captures supply at least 600 effective DPI for their DOCX placement: tables retain their
shared physical scale, while standalone visuals have enough pixels for the largest existing
image fit box. Increasing capture density does not enlarge the printed drawing. The renderer
waits for fonts, images, and populated canvases, and reports browser failures with input context.
Source bitmaps and canvas backing buffers can still lack detail; enlarging them does not
restore it. The renderer reports that limitation rather than recreating their content.
The PDF export settings are separate and may downsample DOCX images.

## Build a quiz or exam from a bptools task CSV

`bbq_tasks_to_exam_yaml.py` reads the website task CSV format
(`subject,topic,script,flags,input,notes`), with optional local `choice_font`
and `layout` columns for typography and choice-column count (`{bp_root}`/`YMATCH`-style aliases
come from the repo's [bbq_settings.yml](../bbq_settings.yml), whose paths
follow the website settings; pass `-s` to use another) and contributes **one
question per resolved task**. The quiz settings define `YMATCH` as the
Matching generator and `YWHICH` as the "Which One?" multiple-choice
generator, so each matching task row chooses exactly one of those formats.
The website can keep its existing dual `YMATCH` alias. List-valued aliases in other settings
still expand to one task per script. Each generator runs with `-d 1 -x 1`; an
unusable candidate (skipped bbq type, or exam-mode rejection) triggers a
fresh run, up to three attempts, then the task is reported as `SKIPPED` on
stderr and left out.

`layout` accepts 1-5; leave it blank for automatic layout. For example, `1` puts each choice
on its own line. The value becomes the existing question-level YAML `layout` field.
Pass `--points 9.5` to write an explicit `total_points` value for the score line; without it,
the DOCX builder uses the numbered answer count.

```csv
subject,topic,script,flags,input,notes,choice_font
genetics,dna_structure,{bp_root}/molecular_biology-problems/chargaff_dna_percent.py,,,,IBM Plex Sans Condensed
genetics,dna_structure,YMCS,,{bp_mcs}/biochemistry/dna_structure.yml,,
genetics,mendelian,YMATCH,,{bp_match}/inheritance/genetics_terminology.yml,,
genetics,dna_profiling,{bp_root}/dna_profiling-problems/who_father_html.py,--easy,,,
```

Use `YMATCH` for the matching version or `YWHICH` for the "Which One?" MC
version of a YAML source. The website's own `YMATCH` alias may continue
generating both formats.

Quiz (default: any MC/MA/MAT/ORD, any number of choices):

```bash
source source_me.sh && python3 converters/bbq_tasks_to_exam_yaml.py -q -t "Genetics Quiz 1" \
    -i task_files/genetics_quiz1.csv \
    -o output_quiz/genetics_quiz1.yml
source source_me.sh && python3 converters/yaml_to_exam_docx.py -i output_quiz/genetics_quiz1.yml
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
source source_me.sh && python3 converters/okla_to_exam_yaml.py -i export.txt
```

## Convert DOCX back to YAML

```bash
source source_me.sh && python3 converters/docx_to_exam_yaml.py -i exam.docx
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
