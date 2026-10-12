# Exam style

These conventions apply to exams in every subject. Question selection belongs in the assessment's
task CSV; scope and coverage decisions belong in its selection notes. The shared DOCX formatting
reference below applies to both exams and quizzes. [exam_styles.yaml](exam_styles.yaml) holds
the machine-readable values.

## Questions and answer sheets

- Use ZipGrade-compatible questions with at most five lettered choices: A, B, C, D, E.
  This limit includes matching answer banks and multiple-answer questions.
- Prefer MATCH over WOMC when both assess the same content.
- Choose the version that covers the required material without repeating narrower variants.
  Retain separate questions when they assess different reasoning.
- Number answers continuously across sections. Each matching prompt uses one numbered row;
  a matching block heading shows its range, such as `Q12-15.`.
- Keep within the configured answer sheet's capacity. The current validator checks 100 rows.
- State when students must select multiple answers, and list every correct letter in the key.
- Set the point total deliberately. Numbered answer rows and grading weights are separate counts.

## Presentation

- Show the assessment title, student name line, and score line on the first page.
- Group questions under clear chapter or topic headings.
- Keep a question's stem, figures, choices, and matching prompts together when they fit on a page.
  A question taller than a page can flow across pages.
- Use one choice per line when longer choices are difficult to read in columns.
- Keep figures, sequence direction labels, tables, and matching blanks legible at print size.
- Include page numbers and student identification on later pages. Inspect the rendered PDF.

## Generation workflow

Use a short, flat shell script: generate YAML and key, validate, build DOCX, export PDF.
Common tools own formatting, pagination, validation, and conversion. Assessment scripts contain
the input paths and requested options; they do not implement document-processing logic.

- Generate with `bbq_tasks_to_exam_yaml.py --exam`.
- Validate with `validate_zip_grade_yaml.py` before building the document.
- Render with `yaml_to_exam_docx.py --keep-questions-together`.
- Export with `bash converters/docx_to_pdf.sh FILE.docx OUTPUT_DIR [DPI]`.

Review skipped tasks separately: a valid A-E document can still have missing coverage.
Preserve the generated YAML, media, and answer key when editing the document; rerunning the
generators selects new random questions. See [USAGE.md](../docs/USAGE.md) for exact commands and
[YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) for data fields.

## Shared DOCX formatting

These settings apply to both exams and quizzes.

### Base styles

| Style | Size | Weight | Main use |
| --- | ---: | --- | --- |
| Normal | 10pt | normal | Default body text and table content |
| Heading 1 | 18pt | bold, left-aligned | Exam title |
| Exam Heading 2 | 14pt | bold italic | Major section labels |
| Chapter Heading | 13pt | bold, purple | Topic or chapter headings |
| Header | 8pt | normal | Page number, date, and student line |

Regular text, headings, choices, and page headers use Atkinson Hyperlegible Next. Inline `<code>` and
`<tt>` text uses the Regular face of Atkinson Hyperlegible Mono to make upright-face selection
explicit in the DOCX. The DOCX records font names without embedding the font files, so both families
must be installed wherever the exam is opened. For text-only choices that need a narrower face, an
instructor can set `choice_font: IBM Plex Sans Condensed` on that question in exam YAML or the task
CSV. This is a manual override and leaves other questions on Atkinson Hyperlegible Next. Page
margins are 0.6 inches, and the header distance is 0.3 inches.

### Question styles

#### Question Heading

Question Heading is 11pt regular text with a 0.2 inch left indent and a -0.2 inch hanging indent.
The complete question label (for example, `3.` or `Q1-3.`) has a black rectangular outline with a
2pt border and 2pt padding. It keeps the question lead-in with the following content, with 0.12
inches before and 0.05 inches after.

#### Question Follow

Question Follow inherits Question Heading and removes the leading space. It is also regular and
non-italic. The builder selects it after a chapter heading, image, or table, and for subsequent
hard-break paragraphs within one question stem, so consecutive question text stays compact.

#### Matching Prompt

Matching Prompt is 11pt normal text with a 0.2 inch left indent and a -0.2 inch hanging indent. It uses 1.25 line spacing, 0.07 inches before, and tab stops at 0.5 and 3.5 inches for two-column prompt rows. A prompt may carry an image after its numbered blank.

### Choice styles

Choice paragraphs use a 0.13 inch left indent and 10pt text. The concrete `Choices 2` through `Choices 5` styles inherit the base Choice style and receive their tab stops from `layout_tab_stops` in the YAML configuration:

| Columns | Tab stops in inches |
| ---: | --- |
| 2 | 3.78 |
| 3 | 2.46, 4.80 |
| 4 | 1.88, 3.63, 5.38 |
| 5 | 1.53, 2.93, 4.33, 5.73 |

The layout algorithm scores visible text width and selects a concrete `Choices N` style. Long five-choice sets fall back to one choice per paragraph before text can wrap underneath a neighboring choice. Choice paragraphs have a small configured space before them to separate answer options from the question stem. Text and image choices use paragraph tab stops by default; the optional `--native-tables` mode uses the dedicated table backend for preserved simple HTML tables.

### Images and tables

- Ordinary images use fit boxes: standalone question images are capped at 5.6
  inches wide; image choices use a 3.40 inch width and 2.00 inch height
  ceiling; matching-prompt images use a 1.40 inch height cap. Wide one-row
  sequence strips with an aspect ratio of at least 4.0 use a 0.40 inch height
  cap.
- Rendered table drawings use the resolution recorded in each PNG multiplied
  by `table_image_scale`. They are not clamped to a page-role maximum, so an
  unusually wide drawing can overflow the text column. For fixed-scale image
  choices, per-column budgets decide whether a row fits; rows that do not fit
  are stacked instead of shrinking the drawings.
- Full-width image choices require the more conservative `choice_strip_min_aspect` threshold (8.0 in the shipped style), keeping shorter matching panels in the ordinary choice layout.
- Question-level data tables are built as DOCX tables; native HTML table conversion is isolated in `docx_table_builder.py` and is opt-in. The native backup accepts simple logical cell grids, while browser-positioned drawings and `colgroup` layout tables retain their PNG fallback.
- HTML drawing tables rasterized through Chromium use Atkinson Hyperlegible Next for regular
  table text and Atkinson Hyperlegible Mono for code or explicitly monospace content. Both fonts
  must be installed on the machine generating the PNGs.

### Page header

Body pages use the Header style with page numbering, the exam date, and a student name line separated by configured tab stops. The first page receives a separate header configuration so the title and student information do not inherit the body-page header.

### Pagination

The DOCX CLI flag `--keep-questions-together` chains
the paragraphs of each question, including its figures, table content, choices, and matching
prompts. The builder uses the question's rendering boundaries, without recognizing printed
numbers or subject-specific heading text. A block taller than one page can still split.

`--page-break-sections` places a page break before the first paragraph
of each section after the first. The exam recipe uses question grouping, and the biostatistics
quiz recipe uses section breaks. Other recipes keep their existing pagination.

### Source of truth

Edit [exam_styles.yaml](exam_styles.yaml) for stable layout values. Keep document styles and shared text helpers in [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py), answer and matching renderers in [../ef_tools/docx_choice_builder.py](../ef_tools/docx_choice_builder.py), image sizing and placement in [../ef_tools/docx_images.py](../ef_tools/docx_images.py), choice-width decisions in [../ef_tools/layout.py](../ef_tools/layout.py), and the exam field contract in [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md). Use [../tests/test_docx_choice_styles.py](../tests/test_docx_choice_styles.py) and the focused builder tests for demonstrated style invariants.
