# YAML exam format

Version 2.0 -- exam-formatting-tools

This document specifies the YAML exam format used by [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py). It serves as the canonical reference for both human authors and machine readers/writers, including qti-package-maker engines.

## Overview

The format describes a printable exam document with sections, questions, choices, images, and tables. It uses sensible defaults (auto-numbering, auto-layout) so minimal YAML produces a complete exam.

To check whether an exam will fit a ZipGrade A-E bubble form, run [validate_zip_grade_yaml.py](../launchers/validate_zip_grade_yaml.py); to build a DOCX containing only ZipGrade-compatible questions, pass `--zip-grade` to [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py). The optional `--native-tables` flag uses preserved simple HTML tables as Word tables and falls back to the normal rasterized drawings for unsupported layouts. See [USAGE.md](USAGE.md) for both commands.

## Top-level fields

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `title` | string | yes | -- | Exam title rendered on the first page |
| `date` | string | yes | -- | ISO 8601 `YYYY-MM-DD`; rendered as "Mon DD, YYYY" in page headers |
| `total_points` | integer | no | question count | Total exam points for the score line |
| `student_line` | string | no | "Full Name: \_\_\_\_\_\_\_" | Name line on the first page |
| `scoring_sections` | integer | no | 4 | Number of \_\_\_\_ blanks in the score line |
| `sections` | list | yes | -- | One or more section objects |

## Sections

Each section groups questions under an optional heading. A section may have a major heading, a chapter heading, or both.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `heading` | string | no | -- | Major section label (e.g., "Multiple Choice"); rendered with Heading 2 style (14pt bold italic, bottom border) |
| `chapter` | string | no | -- | Chapter heading (e.g., "Chapter 1 -- Thermodynamics"); rendered with Chapter Heading style (14pt bold, dark purple #6600cc) |
| `questions` | list | yes | -- | One or more question objects |

### When to use `heading` vs `chapter`

- Use `heading` for top-level exam divisions like "Multiple Choice", "Short Answer", or "Part A". These are structural labels, not content topics.
- Use `chapter` for content-topic labels like "Chapter 1 -- Thermodynamics" or "Enzymes and Kinetics". These identify the subject matter.
- A section may have both: a `heading` followed by a `chapter`.
- A section may have neither, in which case questions follow directly from the previous section.

## Questions

Each question object represents a single exam item.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `statement` | list of content blocks | yes | -- | Ordered stem/body text, images, and tables |
| `number` | integer | no | auto | Numeric override; does not change the "##." format |
| `choices` | list of strings or choice objects | no | -- | Answer choices (plain text, no letter prefixes), optionally with image paths |
| `prompts_list` | list of strings or choice objects | no | -- | Numbered matching prompts; each consumes one question number and renders as `___ N.`; a `{text, image}` object puts a drawing (DNA strip, pedigree) beside the blank |
| `choices_list` | list of strings or choice objects | no | -- | Lettered matching choices rendered as `(A) (B) (C) ...` below the prompts; image objects use the tabbed image-choice layout |
| `layout` | integer | no | auto | Choices column layout: 3, 4, or 5 |
| `choice_font` | string | no | inherited | Optional font-family override for text-only `choices` or `choices_list` paragraphs; for example, `IBM Plex Sans Condensed` |

### Statement text

The `statement` field is an ordered list. Every text run, image, or table is a
separate block, and the DOCX builder emits those blocks in list order. Text
blocks may include an existing number prefix (e.g., "22) Which of the
following...") which the builder strips before re-numbering.

Every question must have at least one non-empty text, image, or table block.
Structured tables use `{table: {columns: [...], rows: [[...], ...]}}`; each row
has one string cell per column.

```yaml
statement:
  - text: "Look at the pathway below."
  - image: exam_files/pathway.png
  - text: "Which metabolite is missing?"
```

Supported statement blocks are `{text: ...}`, `{image: ...}`, and
`{table: {columns: [...], rows: [...]}}`. An image block may also include `html_table`, which preserves a
source drawing table for the optional `--native-tables` DOCX path while the
`image` remains its faithful raster fallback. Structured data tables use a
`table` block and render at their position in the statement.

HTML entities are supported for special characters: `&Delta;`, `&alpha;`, `&beta;`, `&deg;`, `&prime;`, `&rarr;`, `&micro;`.

Inline HTML tags are supported for formatting within statement and choice text:

| Tag | Effect | Example |
| --- | --- | --- |
| `<sub>`, `</sub>` | Subscript | `H<sub>2</sub>O` |
| `<sup>`, `</sup>` | Superscript | `x<sup>2</sup>` |
| `<b>`, `</b>` | Bold | `<b>Note:</b> important` |
| `<strong>`, `</strong>` | Bold (alias for `<b>`) | `<strong>key term</strong>` |
| `<i>`, `</i>` | Italic | `<i>in vivo</i>` |
| `<em>`, `</em>` | Italic (alias for `<i>`) | `<em>emphasis</em>` |
| `<code>`, `</code>` | Atkinson Hyperlegible Mono | `<code>ATGC</code>` |
| `<tt>`, `</tt>` | Atkinson Hyperlegible Mono (legacy alias) | `<tt>ATGC</tt>` |
| `<span style="color: #rrggbb;">`, `</span>` | Hex text color | `<span style="color: #ba372a;">FALSE</span>` |

Engines writing exam YAML should preserve these inline HTML tags verbatim in statement text blocks and choice text. HTML entities (e.g., `&deg;`) should also be preserved as-is; the builder decodes them at render time. Color spans preserve only a three- or six-digit hexadecimal `color` declaration in canonical lowercase `#rrggbb` form; importers normalize bptools' bare hex values and discard unrelated span CSS.

### Question numbering

Questions are auto-numbered sequentially starting at 1, across all sections. The text label remains
`##.` (period after number); DOCX output draws a 2pt rectangular outline around that label. Matching
question ranges such as `Q1-3.` use the same outline. Matching prompt numbers such as `___ 1.` remain
unboxed.

The `number` field overrides the counter value only. Example: `number: 15` makes the next question "15." and continues from there. It does not change the period format.

### Choices

Choices are plain text strings. The builder generates bold **(A) (B) (C) (D) (E)** letter prefixes during rendering.
Set `choice_font` on an individual question when text-only answers need a
narrower face. This is a manual instructor decision; the default remains the
configured Atkinson Hyperlegible Next face. The named font must be installed
where the DOCX is rendered or opened. Inline `<code>`/`<tt>` keeps the
configured monospace face. Text baked into choice images or preserved tables
keeps its source appearance.

```yaml
choices:
  - "Loss of atoms"
  - "Change in molecular identity"
  - "Release of heat"
```

Rendered output: **(A)** Loss of atoms, **(B)** Change in molecular identity, **(C)** Release of heat

For image-based choices, use choice objects. The `text` field is treated
as alt text and rendered as a small caption row below the image row, but
only when the alt text is meaningful -- empty strings and the literal
placeholder `image` are skipped so a row of placeholder captions does not
clutter the page.

```yaml
choices:
  - text: "Titration curve A"
    image: Final_Exam/Final_Exam_2A_files/titration_a.png.jpg
  - image: Final_Exam/Final_Exam_2A_files/titration_b.png.jpg
```

The BBQ converters may also add `html_table` to a structured choice or
prompt object. This preserves the source drawing table beside its PNG
fallback. `yaml_to_exam_docx.py --native-tables` renders a set of table-based
choices as labeled native Word tables; nested, malformed, browser-positioned,
or `colgroup` layout tables continue to use their PNGs.

Ordinary image-choice widths are fitted to per-column limits owned by
`ef_tools.docx_images.IMAGE_CHOICE_MAX_WIDTH_BY_COLS`. Renderer-produced
drawings keep their configured fixed scale; the same limits are a fit check
that stacks a row when a drawing would push the cursor past its tab stop:

| Columns | Image width cap |
| --- | --- |
| 2 | 3.30in |
| 3 | 2.07in |
| 4 | 1.49in |
| 5 | 1.13in |

The ordinary-image caps were tuned via `devel/measure_image_choices.py` so
each image's right edge sits ~0.02in inside the next tab stop. Re-run that
tool after changing any of `IMAGE_CHOICE_MAX_WIDTH_BY_COLS`,
`layout_tab_stops`, or `choice_indent`.

For ordinary images, the per-column cap can be tighter than
`choice_image_max_width` or `choice_image_max_height` in
`styles/exam_styles.yaml`. Images in an ordinary-image row share the height
implied by its most constrained image. Inline-image edge margins
(`distT`/`distB`/`distL`/`distR`) are zeroed so images pack tight.

Wide image choices such as DNA sequence strips are detected by aspect ratio
(`choice_strip_min_aspect`) and rendered one choice per paragraph at up to
`choice_strip_max_width`. Each strip occupies its own paragraph and can flow
independently across page breaks.

By default, answer choices -- text-only and ordinary image-based -- are
rendered as inline runs in paragraphs positioned with paragraph tab stops, one
column per choice. Wide strip choices use one inline image per paragraph to
remain readable. With `--native-tables`, a choice set whose entries all carry
`html_table` is instead rendered as one labeled native Word table per choice;
unsupported tables retain the PNG fallback. Browser-positioned drawing tables
and `colgroup`-based layout tables are intentionally unsupported because their
meaning depends on rendered geometry rather than a logical cell grid.
Structured data tables use a `{table: ...}` statement block and render as real
Word tables at that point in the statement.

### Matching

Matching questions use `prompts_list` (the numbered items students label) and
`choices_list` (the lettered options). The schema mirrors bptools/qti-package-maker
`MATCH(question_text, prompts_list, choices_list)`.

```yaml
- statement:
    - text: "Match each functional group with its description."
  prompts_list:
    - "Phosphate"
    - "Carboxyl"
  choices_list:
    - "Energy transfer"
    - "C-terminus"
```

If this question starts at number 5, the DOCX builder renders:

- header `Q5-6. Match each functional group with its description.`
- lettered options `(A) Energy transfer  (B) C-terminus` (auto-laid-out like MC)
- numbered blanks `___ 5. Phosphate` and `___ 6. Carboxyl` on one two-column row when both prompts are plain text
- the next question starts at 7.

The lettered choices render before the numbered blanks so students see the
answer key first, matching the reference exam style in `ARTIFACTS/`.

Do not embed `A. ... B. ...` enumerations inside `statement` -- put the
options in `choices_list` so the builder formats them consistently.

Prompt and choice entries may be `{text, image}` objects. A prompt image
renders inline after `___ N.`; its height is capped by
`prompt_image_max_height` in `styles/exam_styles.yaml`, and wide one-row
strips (aspect at least `prompt_strip_min_aspect`) by `prompt_strip_max_height`
so short and long DNA strips share one cell size.

Ordering questions (bbq `ORD`) use the same block: `prompts_list` holds
`Position 1`, `Position 2`, ... and `choices_list` holds the shuffled items,
so the student writes the letter of the item that belongs at each position.

### Auto-layout algorithm

When `layout` is omitted, the builder selects a `Choices N` paragraph
style based on a weighted **visible-width score** of the longest
choice. The score is a sum of per-character weights (narrow glyphs
like `i`, `l`, `.` count less than typical letters; wide glyphs like
`M`, `W` count more). Crucially, HTML entities and inline tags are
reduced to their visible text before scoring -- `&#8226;`,
`&#8801;`, `<sub>2</sub>`, `<b>...</b>` each contribute their
rendered glyphs, not their serialized YAML length.

| Layout | Items per row | Max visible width | Tab-stop position |
| --- | --- | --- | --- |
| Choices 5 | 5 | 17 | 1.53in, 2.93in, 4.33in, 5.73in |
| Choices 4 | 4 | 17 | 1.88in, 3.63in, 5.38in |
| Choices 3 | 3 | 30 | 2.46in, 4.80in |
| Choices 2 | 2 | 49 | 3.78in (two columns) |

Width scores use approximate character weights and do not measure the
installed DOCX font directly. The thresholds are configured in
`layout_limits`. Tab-stop positions in `layout_tab_stops`
(`styles/exam_styles.yaml`) are pre-offset by `choice_indent` (0.13in)
because OOXML measures tab stops from the page left margin, not from
the paragraph indent -- without the offset the first column gap would
be shorter than the rest. When the longest choice's visible-width
score exceeds the budget, the next wider layout is selected; if no
layout fits, the builder falls back to a single-column vertical stack
rendered with the `Choices 2` style. The abstract `Choice` base style
is never applied to a paragraph.

Override with an explicit `layout` value when needed:

```yaml
- statement:
    - text: "A thermodynamically unfavorable reaction:"
  choices:
    - "Occurs spontaneously"
    - "Requires energy input"
  layout: 3
```

### Images

```yaml
- statement:
    - text: "What type of reaction is shown?"
    - image: images/exam_figure_01.png
  choices:
    - "Oxidation"
    - "Reduction"
```

Images are embedded in the DOCX with their original aspect ratio preserved. A relative statement image path is resolved against the directory of the YAML file, so a YAML and its `<stem>_files/` folder move together. Absolute paths pass through unchanged. Statement images remain between their surrounding text blocks.

PNG table drawings rendered by the BBQ converters use the resolution recorded
in each PNG, multiplied by the single `table_image_scale` value in
`styles/exam_styles.yaml`. They are not clamped to page-role width or height
limits; unusually wide drawings can extend beyond the text column. Fixed-scale
image-choice rows that exceed their per-column fit budget are stacked rather
than shrunk. Ordinary images use their configured fit boxes and strip-height
limits instead.

bptools drawing tables (gels, chi-square critical values, test-cross counts, metabolic pathways, genotype grids) are rendered to PNG by [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py) and [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) through `qti_package_maker.html_to_image`. Each drawing occupies an image block at its authored position; its source HTML is kept on that block for the optional native-table path.

For cleaned Blackboard HTML exports, use [html_to_exam_yaml.py](../launchers/html_to_exam_yaml.py) to create YAML first; it preserves the DOM order of statement text and images and keeps image-based answer choices as structured choice objects.

RDKit HTML5 canvas widgets are also handled: when a `<canvas class="cleaned-statement-media">` is paired with an inline `initRDKitModule()` script, [ef_tools/rdkit_render.py](../ef_tools/rdkit_render.py) extracts the SMILES literal and renders a PNG into the existing `*_files/` directory. The PNG is emitted as an image block in statement order (or as a structured choice `image` field for canvas-based answer choices).

### Tables

```yaml
- statement:
    - text: "Using the data below, determine Km:"
    - table:
        columns:
          - "[S] (mM)"
          - "v (&micro;mol/min)"
        rows:
          - ["1", "10"]
          - ["2", "17"]
          - ["5", "25"]
  choices:
    - "2 mM"
    - "5 mM"
```

Table cells are always strings. The header row uses bold centered text with a light gray background.

## Style rendering

The builder applies these named paragraph styles automatically:

| Style name | When applied |
| --- | --- |
| Heading 1 | Exam title on the first page |
| Heading 2 | Major section headings (`heading` field) -- 14pt bold italic |
| Chapter Heading | Chapter headings (`chapter` field) -- 14pt bold, dark purple #6600cc |
| Question Heading | Questions following other questions or choices (normal flow) |
| Question Follow | Questions following an image, table, or heading (after a visual break) |
| Choices3 / Choices4 / Choices5 | Multiple choice answer rows |
| Matching Prompt | Numbered fill-in lines for matching questions (`___ N. text`); two-column tab stops at 0.5" and 3.5", inherits from Question Heading. See `ARTIFACTS/2019_exam2-final.docx` |
| Standard | Default body text |

Style selection between "Question Heading" and "Question Follow" is automatic based on the preceding element.
Question Heading and Question Follow keep with the next paragraph; answer-choice
styles do not. This keeps question text attached while allowing choices to flow
independently across pages.

## Date handling

The `date` field must be ISO 8601 `YYYY-MM-DD`. The builder renders it as "Mon DD, YYYY" in the page header on body pages (e.g., "Apr 02, 2026"). The builder warns on past dates but does not error.

## Total points

If `total_points` is omitted, it defaults to the total number of questions (1 point per question). The score line reads: "Final Score \_\_\_\_ / \_\_\_\_ / \_\_\_\_ / \_\_\_\_ / {total} pts"

## Complete example

```yaml
title: "Spring 2026 Exam 2 (100 points)"
date: "2026-04-02"
student_line: "Name:_____________________________"
sections:
  - heading: "Multiple Choice"
    questions:
      - statement:
          - text: "Which feature is essential for any chemical reaction to occur?"
        choices:
          - "Loss of atoms"
          - "Change in molecular identity"
          - "Release of heat"
          - "Decrease in entropy"
          - "Occurrence outside living systems"
      - statement:
          - text: "A negative &Delta;G indicates:"
        choices:
          - "Energy must be added"
          - "The reaction proceeds spontaneously"
      - statement:
          - text: "What type of enzymatic reaction is this:"
          - image: images/exam_image_01.png
        choices:
          - "Hydrolase"
          - "Lyase"
          - "Ligase"
          - "Oxidoreductase"
          - "Isomerase"
  - chapter: "Chapter 2 -- Kinetics"
    questions:
      - statement:
          - text: "Use the table below to determine Km:"
          - table:
              columns:
                - "[S] (mM)"
                - "v (&micro;mol/min)"
              rows:
                - ["1", "10"]
                - ["2", "17"]
                - ["5", "25"]
        choices:
          - "2 mM"
          - "5 mM"
          - "10 mM"
          - "20 mM"
```

## qti-package-maker compatibility

This section defines how to map between exam YAML and the qti-package-maker item model.

### Reading exam YAML into an ItemBank

A read engine should:

1. Parse the YAML file with `yaml.safe_load()`
2. Iterate over `sections[].questions[]`
3. For each question, determine the item type:
   - Has `prompts_list` and `choices_list` -> **MATCH**
   - Has `choices` list -> **MC** (single answer; answer key is not stored in this format)
4. Create item objects:
   - `question_text` = the text blocks in `statement`, joined in order (strip any leading number prefix like "22) ")
   - For **MC**: `choices_list` = the `choices` field (already plain text, no prefixes)
   - For **MATCH**: `prompts_list` and `choices_list` come straight from the matching fields
   - `answer_text` = not available (this is a print format, not a grading format)

### Fields preserved during read

| Exam YAML field | qti-package-maker field | Notes |
| --- | --- | --- |
| `statement` | `question_text` | Join text blocks in order, then strip number prefix |
| `choices` | `choices_list` | MC, direct mapping |
| `prompts_list` | `prompts_list` | MATCH, direct mapping |
| `choices_list` | `choices_list` | MATCH, direct mapping |

### Fields lost during read (print-only metadata)

These fields have no equivalent in the qti item model and are silently dropped:

- `title`, `date`, `student_line`, `total_points`, `scoring_sections`
- `heading`, `chapter` (section structure)
- `number`, `layout` (formatting hints)
- Statement images and tables (embedded figures)
- Answer correctness (not stored in exam YAML)

### Writing exam YAML from an ItemBank

A write engine should:

1. Build the YAML structure with sensible defaults:
   - `title`: use `package_name` or a default
   - `date`: use today's date in ISO format
   - `sections`: one section containing all questions
2. For each item in the ItemBank:
   - `statement` = one `{text: ...}` block containing `item.question_text` (preserve inline HTML tags: `<sub>`, `<sup>`, `<i>`, `<b>`, `<strong>`, `<em>`)
   - `choices` = `item.choices_list` (strip any prefixes with `remove_prefix_from_list()`; preserve inline HTML tags)
3. Item type mapping:
   - **MC**: `statement` + `choices` (answer_text is lost since exam YAML has no answer key)
   - **MA**: same as MC (multiple correct answers lost)
   - **MATCH**: emit `prompts_list` and `choices_list` directly (statement stays in `statement`; do not encode as a `table`)
   - **ORDER**: `prompts_list` of `Position N` labels + shuffled `choices_list` (the correct order lives only in the sibling answer key)
   - **NUM**: `statement` only (numeric answer/tolerance lost)
   - **FIB**: `statement` only (fill-in answers lost)

### Fields lost during write (assessment-only metadata)

These qti item fields have no equivalent in exam YAML:

- `answer_text`, `answers_list`, `answer_index` (correct answers)
- `answer_float`, `tolerance_float` (numeric answers)
- `answer_map` (multi-fill-in-blank)
- `ordered_answers_list` ordering semantics (choices written but order meaning lost)
- `item_crc16`, `question_crc16`, `secondary_crc16` (CRC hashes)
- `feedback_correct`, `feedback_incorrect` (item feedback)
- `min_answers_required`, `allow_all_correct` (MA constraints)
- `tolerance_message` (NUM display setting)

### Round-trip limitations

Exam YAML is a **print-document format**, not an assessment interchange format. Round-tripping through exam YAML loses answer keys, item metadata, and section structure. Use exam YAML as a one-way export target for generating printable exams, not as a lossless storage format.

The recommended pipeline for LMS delivery is: source format -> qti-package-maker -> QTI/Blackboard. The recommended pipeline for print exams is: source format -> qti-package-maker -> bbq_text -> [bbq_to_exam_yaml.py](../launchers/bbq_to_exam_yaml.py) -> exam YAML -> [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py) -> DOCX. For one question per bptools generator, [bbq_tasks_to_exam_yaml.py](../launchers/bbq_tasks_to_exam_yaml.py) runs the generators from a website task CSV and writes the exam YAML directly (see [USAGE.md](USAGE.md)). Both bbq converters write a sibling `<stem>-key.txt` answer key, since exam YAML itself carries no answers.
