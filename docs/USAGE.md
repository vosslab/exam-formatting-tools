# Usage

All commands assume the bootstrap pattern `source source_me.sh && python3 ...`.

## Pipeline

The normal printable pipeline is `<source format> -> exam YAML -> DOCX -> PDF`. Open the generated DOCX directly in LibreOffice Writer and export its PDF with the supplied script; no raw ODT or ODT-modification stage is part of the workflow. Every launcher
validates input/output extensions and reports the question count on success.
`-o/--output` is optional; when omitted, the output is `<input-stem>` with
the target extension in the current working directory.

## Assessment recipes

Course recipes live in [../builders/](../builders/) and their current assessment notes live in
[../assessment_styles/](../assessment_styles/). They are examples, not the stable interface:
inspect a recipe before use because it may generate new randomized questions or reset its output
directory. Save manual YAML or DOCX edits outside that directory, then use the generic converters
below to reproduce a chosen YAML selection. Shared presentation rules are in
[EXAM_STYLE.md](../assessment_styles/EXAM_STYLE.md) and [QUIZ_STYLE.md](../assessment_styles/QUIZ_STYLE.md).

## Build a DOCX exam from YAML

```bash
mkdir -p _temp/example
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i exam.yml -o _temp/example/exam.docx
bash converters/docx_to_pdf.sh _temp/example/exam.docx _temp/example
```

The converter defaults to US Letter. Use `--paper-size a4` for A4 or
`--paper-size letter` to switch back. Paper size changes page geometry and horizontal
tab positions; fonts, colors, margins, and drawing scale retain the same style settings.
Review pagination after switching sizes.

Paper output uses compact formatting by default: recognized hint sections are
removed, recognized background text is 8pt, and bold lead-ins share a paragraph
with their prose. Use `--no-compact` to retain the unmodified rendering.

To change only the paper size of an edited YAML, create a new DOCX with the desired size:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i exam.yml --paper-size a4 -o _temp/example/exam_a4.docx
```

Use `--keep-questions-together` to keep each question's stem, figures, and answer bank together
when they fit on one page. Use `--page-break-sections` to start later sections on new pages.

For a backup DOCX that converts preserved simple bptools HTML drawing tables
to native Word tables, add `--native-tables`. Unsupported or nested tables use
the normal captured image representation instead:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i exam.yml --native-tables -o _temp/example/exam_native_tables.docx
```

The YAML schema is documented in [YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md).
Style definitions come from [assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).
See [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md) for answer measurement, tab-slot selection,
manual editing, and image-choice behavior.

Note: `yaml_to_exam_docx.py` refuses to overwrite an existing output file
(it raises `FileExistsError`). For a review copy, create a path under the
repository-root `_temp/` directory; after inspecting it in LibreOffice, replace a
canonical artifact deliberately if needed:

```bash
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i exam.yml -o _temp/example/exam_review.docx
```

Image-based answer choices are laid out horizontally using paragraph tab stops
by default; the optional native-table backup is described in
[YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md).

## Export DOCX to PDF

The shared [docx_to_pdf.sh](../converters/docx_to_pdf.sh) command exports through the existing
macOS LibreOffice installation with 70 percent JPEG quality and PDF 1.7. It takes a DOCX path,
an output directory, and an optional image DPI (default 100). It replaces that document's PDF.
Run it outside a sandbox on this macOS host, where LibreOffice must launch normally.

```bash
bash converters/docx_to_pdf.sh _temp/example/exam.docx _temp/example 150
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
source source_me.sh && python3 converters/html_to_exam_yaml.py \
    -i questions.html -o _temp/example/questions.yml
```

Matching questions are emitted as `prompts_list` plus `choices_list`; see [YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md) for the schema.

HTML drawing tables, MathML, and JavaScript-populated canvases are captured by the shared
Playwright renderer and saved beside the assessment. Existing images are embedded directly.
The browser runs authored scripts with their question context and source-relative resources;
required external scripts must be available. EF Tools does not reconstruct molecular drawings
or repair invalid HTML. No additional command-line options are needed.

bptools bbq text (`bbq-*-questions.txt`) to YAML plus an answer key:

```bash
source source_me.sh && python3 converters/bbq_to_exam_yaml.py \
    -i questions.txt -o _temp/example/questions.yml
```

MC and MA keep their choices; MAT becomes `prompts_list` plus a shuffled
`choices_list`; ORD becomes position blanks (`Position 1`, `Position 2`, ...)
plus shuffled items. NUM, FIB, and FIB_PLUS have no print form and are
skipped. Drawing tables (gels, chi-square tables) are rendered to
`<stem>_files/*.svg` through EF Tools' native Chromium renderer (see
[INSTALL.md](INSTALL.md)). The answer key lands in `<stem>-key.txt`.

Captures use Chromium PDF output and Poppler to preserve text as glyph outlines, borders,
and other vector content in SVG. Embedded raster images remain raster. The same capture
path handles tables, MathML, and JavaScript canvases, using their full question context.
SVG is embedded directly into DOCX for LibreOffice; no PNG companion or YAML field is needed.
Tables retain their shared physical scale, and standalone visuals use their existing fit boxes.

Canvas-only drawings (including RDKit) use the existing PNG capture path at at least
600 effective DPI for their DOCX placement. Tables and MathML prefer SVG, and mixed tables
retain vector text and borders alongside their raster canvas content. SVG export errors
also fall back to PNG per element. Source-resolution warnings identify insufficient raster
detail at the intended print size, including after PNG scripts rerun at higher device scale.
A 600-DPI screenshot does not restore detail absent from a fixed-resolution canvas.
The renderer waits for fonts, images, and populated canvases.
The PDF export settings are separate and may downsample raster content.

## Build a quiz or exam from a bptools task CSV

For shorter, curated matching blocks, follow
[SPLITTING_MATCHING_BANKS.md](SPLITTING_MATCHING_BANKS.md) before generating the assessment.

`bbq_tasks_to_exam_yaml.py` reads the task CSV format
(`subject,topic,script,flags,input,notes`), with optional local `choice_font`
and `layout` columns for typography and choice-column count (`{bp_root}`/`YMATCH`-style aliases
come from the repo's [bbq_settings.yml](../bbq_settings.yml), whose paths
follow the website settings; pass `-s` to use another) and contributes **one
question per resolved task**. The quiz settings define `YMATCH` as the
Matching generator and `YWHICH` as the "Which One?" multiple-choice
generator, so each matching task row chooses exactly one of those formats.
The website can keep its existing dual `YMATCH` alias. List-valued aliases in other settings
still expand to one task per script. Each generator runs with `-d 10 -x 10`, and
the builder randomly selects one emitted question (smaller pools are accepted). An
unusable candidate (skipped bbq type, or exam-mode rejection) triggers a
fresh run, up to three attempts, then the task is reported as `SKIPPED` on
stderr and left out.

`layout` accepts 1-5; leave it blank for automatic layout. `1` puts each choice on its own
line. Pass `--points 9.5` to write an explicit `total_points` value; otherwise the DOCX builder
uses the numbered answer count. See the repository's [../task_files/](../task_files/) and
[../bbq_settings.yml](../bbq_settings.yml) for the maintained task and alias contracts.

Quiz (default: any MC/MA/MAT/ORD, any number of choices):

```bash
source source_me.sh && python3 converters/bbq_tasks_to_exam_yaml.py -q -t "Quiz title" \
    -i tasks.csv -o _temp/example/quiz.yml
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i _temp/example/quiz.yml -o _temp/example/quiz.docx
```

Handout mode also prints NUM, FIB, and FIB_PLUS items with answer blanks and
keeps their values in the sibling key:

```bash
source source_me.sh && python3 converters/bbq_tasks_to_exam_yaml.py --handout \
    -i tasks.csv -o _temp/example/handout.yml
source source_me.sh && python3 converters/yaml_to_exam_docx.py \
    -i _temp/example/handout.yml -o _temp/example/handout.docx
```

Exam (`-e`): only questions that pass the ZipGrade A-E rules are kept;
generators with fixed six-choice flags (`-c 6`) are skipped after three
attempts, so edit their flags in the CSV.

Outputs: `<stem>.yml`, `<stem>-key.txt` (one line per question block, e.g.
`1. B   c555_9c1d   chargaff_dna_percent.py` or
`Q5-8. 5=C 6=A 7=D 8=B   ce62_1dbe   yaml_match_to_bbq.py (genetic_disorders)`),
and `<stem>_files/*.svg` (or PNG on capture failure) for rendered tables. The CSV `topic` column becomes
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

## Known gaps

- TODO: after installing on another platform, verify that the documented LibreOffice export path and the supported system-package commands apply there.
