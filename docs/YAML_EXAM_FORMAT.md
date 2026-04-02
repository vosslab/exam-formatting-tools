# YAML exam format

Exams are authored in YAML using a simple, human-readable format that emphasizes sensible defaults over configuration.

## Top-level fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | string | yes | Exam title (rendered in header) |
| `date` | ISO 8601 | yes | Date in YYYY-MM-DD format; rendered as "Mon DD, YYYY" in output |
| `total_points` | integer | no | Total exam points; defaults to number of questions |
| `sections` | list | yes | One or more section objects (chapters) |

## Sections

Each section object groups questions under a chapter heading.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `chapter` | string | yes | Section heading text; uses "Chapter Heading" style |
| `questions` | list | yes | One or more question objects |

## Questions

Each question object represents a single exam item.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `statement` | string | yes | Question stem/body text |
| `number` | integer | no | Numeric override (does not change "##." format); auto-numbered if omitted |
| `choices` | list | no | Plain list of choice text strings (no letter prefixes) |
| `layout` | integer | no | Choices style override (3, 4, or 5); auto-determined if omitted |
| `image` | string | no | Path to image file (relative to document root) |
| `table` | object | no | Table with `columns` (list) and `rows` (list of lists) |

## Choice formatting

Choices are plain text strings without letter prefixes. The builder automatically generates bold **(A) (B) (C)** format during document generation.

```yaml
choices:
  - "Loss of atoms"
  - "Change in molecular identity"
  - "Release of heat"
```

Output:
```
**(A)** Loss of atoms
**(B)** Change in molecular identity
**(C)** Release of heat
```

## Auto-layout algorithm

When `layout` is omitted, the builder auto-selects a Choices style based on choice count and text length:

- **5 short choices** (max ~15 chars): Choices5
- **5 long choices**: Choices4 with overflow (2 rows)
- **3 choices**: Choices3
- **2 choices**: Choices4 (fills row with extra tabs for spacing)
- **4 choices**: Choices4
- **Custom override**: set `layout: 3` or `layout: 4` or `layout: 5` explicitly

## Question numbering

Questions are automatically numbered sequentially starting at 1. The format is always "##. Question text" with a period, never parentheses.

Set `number: 15` to restart numbering mid-exam. This affects only the numeric value; the "##." format remains unchanged.

## Images

Include an optional image reference:

```yaml
- statement: "What type of reaction is shown?"
  choices:
    - "Oxidation"
    - "Reduction"
  image: images/exam_figure_01.png
```

The image path is relative to the document root.

## Tables

Include an optional table (e.g., data table for analysis questions):

```yaml
- statement: "Using the table below, what is the most likely enzyme?"
  choices:
    - "Enzyme A"
    - "Enzyme B"
    - "Enzyme C"
  table:
    columns:
      - "Temperature (C)"
      - "pH"
      - "Activity (%)"
    rows:
      - ["25", "5.0", "45"]
      - ["37", "7.0", "95"]
      - ["50", "8.5", "30"]
```

## Complete example

```yaml
title: "Spring 2026 Exam 2"
date: "2026-04-15"
total_points: 50
sections:
  - chapter: "Chapter 1 -- Thermodynamics"
    questions:
      - statement: "Which feature is essential for any chemical reaction to occur?"
        choices:
          - "Loss of atoms"
          - "Change in molecular identity"
          - "Release of heat"
          - "Decrease in entropy"
          - "Occurrence outside living systems"
      - statement: "A negative delta-G indicates:"
        choices:
          - "Energy must be added"
          - "The reaction proceeds spontaneously"
        layout: 3
      - statement: "Formation of macromolecules via dehydration synthesis:"
        choices:
          - "Requires energy input"
          - "Releases energy"
      - statement: "At pH 7.5 and 25 oC, which enzyme is most active?"
        choices:
          - "Enzyme A"
          - "Enzyme B"
          - "Enzyme C"
          - "Enzyme D"
        image: images/exam_figure_01.png
  - chapter: "Chapter 2 -- Kinetics"
    questions:
      - statement: "Use the table below to determine Km:"
        choices:
          - "2 mM"
          - "5 mM"
          - "10 mM"
          - "20 mM"
        table:
          columns:
            - "[S] (mM)"
            - "v (&micro;mol/min)"
          rows:
            - ["1", "10"]
            - ["2", "17"]
            - ["5", "25"]
            - ["10", "28"]
```

## Conventions

- Use YAML string syntax for titles and statements that contain special characters (colons, hyphens, etc.)
- Choice text should be concise but complete
- Image paths use forward slashes (e.g., `images/exam_figure_01.png`)
- Table cell values are strings (e.g., `"25"` not `25`)
- ISO date format is strict: `YYYY-MM-DD` (e.g., `2026-04-15`, not `04/15/26`)

## Date handling

The `date` field is required and must be in ISO 8601 `YYYY-MM-DD` format. The builder renders the date as "Mon DD, YYYY" in the exam header (e.g., "Tue 15, Apr 2026").

The builder warns if the date is in the past (earlier than today), but does not error. Historical exam rebuilds must remain possible.

## Total points

If `total_points` is omitted, it defaults to the total number of questions in the exam (1 point per question).

Override this default explicitly:

```yaml
total_points: 100
```
