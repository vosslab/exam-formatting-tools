# YAML exam format

Version 1.0 -- exam-formatting-tools

This document specifies the YAML exam format used by [yaml_to_exam_docx.py](../yaml_to_exam_docx.py). It serves as the canonical reference for both human authors and machine readers/writers, including qti-package-maker engines.

## Overview

The format describes a printable exam document with sections, questions, choices, images, and tables. It uses sensible defaults (auto-numbering, auto-layout) so minimal YAML produces a complete exam.

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
| `statement` | string | yes | -- | Question stem/body text |
| `number` | integer | no | auto | Numeric override; does not change the "##." format |
| `choices` | list of strings or choice objects | no | -- | Answer choices (plain text, no letter prefixes), optionally with image paths |
| `prompts_list` | list of strings | no | -- | Numbered matching prompts; each consumes one question number and renders as `___ N.` |
| `choices_list` | list of strings | no | -- | Lettered matching choices rendered as `(A) (B) (C) ...` below the prompts |
| `layout` | integer | no | auto | Choices column layout: 3, 4, or 5 |
| `image` | string | no | -- | Relative path to an image file |
| `images` | list of strings | no | -- | Additional relative image paths for questions with multiple figures |
| `table` | object | no | -- | Data table (see below) |

### Statement text

The `statement` field contains the full question stem. It may include an existing number prefix (e.g., "22) Which of the following...") which the builder strips before re-numbering.

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

Engines writing exam YAML should preserve these inline HTML tags verbatim in statement and choice text. HTML entities (e.g., `&deg;`) should also be preserved as-is; the builder decodes them at render time.

### Question numbering

Questions are auto-numbered sequentially starting at 1, across all sections. The format is always `##. Question text` (period after number).

The `number` field overrides the counter value only. Example: `number: 15` makes the next question "15." and continues from there. It does not change the period format.

### Choices

Choices are plain text strings. The builder generates bold **(A) (B) (C) (D) (E)** letter prefixes during rendering.

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

Image widths are clamped per column count by
`ef_tools.docx_builder.IMAGE_CHOICE_MAX_WIDTH_BY_COLS`, which sets
empirical per-column caps that prevent a trailing image from pushing
the cursor past its tab stop and wrapping to a new line:

| Columns | Image width cap |
| --- | --- |
| 2 | 3.30in |
| 3 | 2.07in |
| 4 | 1.49in |
| 5 | 1.13in |

Caps are tuned via `tools/measure_image_choices.py` so each image's right
edge sits ~0.02in inside the next tab stop. Re-run that tool after
changing any of `IMAGE_CHOICE_MAX_WIDTH_BY_COLS`, `layout_tab_stops`, or
`choice_indent`.

The cap dominates `choice_image_max_width` and `choice_image_max_height`
in `styles/exam_styles.yaml` for any layout where the per-column budget
is tighter. All images in a row render at one shared height computed
from the binding-constraint image, and inline-image edge margins
(`distT`/`distB`/`distL`/`distR`) are zeroed so images pack tight.

**Layout policy: no docx tables for answer choices.** All answer choices --
text-only and image-based -- are rendered as inline runs in a single paragraph
positioned with paragraph tab stops, one column per choice. The DOCX builder
must not emit `<w:tbl>` table elements for choices, even when images are
present. This applies to MC `choices` and to matching `choices_list`. Data
tables declared via the question-level `table` field (a separate concept) are
still rendered as real tables.

### Matching

Matching questions use `prompts_list` (the numbered items students label) and
`choices_list` (the lettered options). The schema mirrors bptools/qti-package-maker
`MATCH(question_text, prompts_list, choices_list)`.

```yaml
- statement: "Match each functional group with its description."
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
- numbered blanks `___ 5. Phosphate` and `___ 6. Carboxyl`
- the next question starts at 7.

The lettered choices render before the numbered blanks so students see the
answer key first, matching the reference exam style in `ARTIFACTS/`.

Do not embed `A. ... B. ...` enumerations inside `statement` -- put the
options in `choices_list` so the builder formats them consistently.

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
| Choices 4 | 4 | 23 | 1.88in, 3.63in, 5.38in |
| Choices 3 | 3 | 30 | 2.46in, 4.80in |
| Choices 2 | 2 | 49 | 3.78in (two columns) |

Width budgets are empirically measured at 10pt Liberation Sans with
bold `(A) ` prefix. Tab-stop positions in `layout_tab_stops`
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
- statement: "A thermodynamically unfavorable reaction:"
  choices:
    - "Occurs spontaneously"
    - "Requires energy input"
  layout: 3
```

### Images

```yaml
- statement: "What type of reaction is shown?"
  image: images/exam_figure_01.png
  choices:
    - "Oxidation"
    - "Reduction"
```

Images are embedded in the DOCX with their original aspect ratio preserved. The image path is relative to the working directory.

For cleaned Blackboard HTML exports, use [html_to_exam_yaml.py](../html_to_exam_yaml.py) to create YAML first; it preserves statement images as `images` and image-based answer choices as structured choice objects.

RDKit HTML5 canvas widgets are also handled: when a `<canvas class="cleaned-statement-media">` is paired with an inline `initRDKitModule()` script, [ef_tools/rdkit_render.py](../ef_tools/rdkit_render.py) extracts the SMILES literal and renders a PNG into the existing `*_files/` directory. The PNG path is added to the standard `images` list (or to a structured choice `image` field for canvas-based answer choices), so the YAML schema is unchanged.

### Tables

```yaml
- statement: "Using the data below, determine Km:"
  table:
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
      - statement: "Which feature is essential for any chemical reaction to occur?"
        choices:
          - "Loss of atoms"
          - "Change in molecular identity"
          - "Release of heat"
          - "Decrease in entropy"
          - "Occurrence outside living systems"
      - statement: "A negative &Delta;G indicates:"
        choices:
          - "Energy must be added"
          - "The reaction proceeds spontaneously"
      - statement: "What type of enzymatic reaction is this:"
        image: images/exam_image_01.png
        choices:
          - "Hydrolase"
          - "Lyase"
          - "Ligase"
          - "Oxidoreductase"
          - "Isomerase"
  - chapter: "Chapter 2 -- Kinetics"
    questions:
      - statement: "Use the table below to determine Km:"
        table:
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
   - `question_text` = the `statement` field (strip any leading number prefix like "22) ")
   - For **MC**: `choices_list` = the `choices` field (already plain text, no prefixes)
   - For **MATCH**: `prompts_list` and `choices_list` come straight from the matching fields
   - `answer_text` = not available (this is a print format, not a grading format)

### Fields preserved during read

| Exam YAML field | qti-package-maker field | Notes |
| --- | --- | --- |
| `statement` | `question_text` | Strip number prefix |
| `choices` | `choices_list` | MC, direct mapping |
| `prompts_list` | `prompts_list` | MATCH, direct mapping |
| `choices_list` | `choices_list` | MATCH, direct mapping |

### Fields lost during read (print-only metadata)

These fields have no equivalent in the qti item model and are silently dropped:

- `title`, `date`, `student_line`, `total_points`, `scoring_sections`
- `heading`, `chapter` (section structure)
- `number`, `layout` (formatting hints)
- `image`, `images` (embedded figures)
- Answer correctness (not stored in exam YAML)

### Writing exam YAML from an ItemBank

A write engine should:

1. Build the YAML structure with sensible defaults:
   - `title`: use `package_name` or a default
   - `date`: use today's date in ISO format
   - `sections`: one section containing all questions
2. For each item in the ItemBank:
   - `statement` = `item.question_text` (preserve inline HTML tags: `<sub>`, `<sup>`, `<i>`, `<b>`, `<strong>`, `<em>`)
   - `choices` = `item.choices_list` (strip any prefixes with `remove_prefix_from_list()`; preserve inline HTML tags)
3. Item type mapping:
   - **MC**: `statement` + `choices` (answer_text is lost since exam YAML has no answer key)
   - **MA**: same as MC (multiple correct answers lost)
   - **MATCH**: emit `prompts_list` and `choices_list` directly (statement stays in `statement`; do not encode as a `table`)
   - **ORDER**: `statement` + `choices` (ordering information lost)
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

The recommended pipeline for LMS delivery is: source format -> qti-package-maker -> QTI/Blackboard. The recommended pipeline for print exams is: source format -> qti-package-maker -> bbq_text -> [bbq_to_exam_yaml.py](../bbq_to_exam_yaml.py) -> exam YAML -> [yaml_to_exam_docx.py](../yaml_to_exam_docx.py) -> DOCX.
