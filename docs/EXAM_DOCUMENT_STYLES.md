# Exam document styles

This reference describes the current DOCX styles loaded from [../styles/exam_styles.yaml](../styles/exam_styles.yaml) and applied by [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py). Legacy ODT artifacts remain useful as visual references, but the ODT builder is not part of the supported pipeline.

## Base styles

| Style | Size | Weight | Main use |
| --- | ---: | --- | --- |
| Normal | 10pt | normal | Default body text and table content |
| Heading 1 | 18pt | bold, left-aligned | Exam title |
| Exam Heading 2 | 14pt | bold italic | Major section labels |
| Chapter Heading | 13pt | bold, purple | Topic or chapter headings |
| Header | 8pt | normal | Page number, date, and student line |

Regular text, headings, choices, and page headers use Atkinson Hyperlegible Next. Inline `<code>` and
`<tt>` text uses Atkinson Hyperlegible Mono. The DOCX records these font names without embedding
the font files, so they must be installed wherever the exam is opened. An instructor can apply IBM
Plex Sans Condensed manually in Word after generation. Page margins are 0.6 inches, and the header
distance is 0.5 inches.

## Question styles

### Question Heading

Question Heading is 11pt regular text with a 0.2 inch left indent and a -0.2 inch hanging indent.
The complete question label (for example, `3.` or `Q1-3.`) has a black rectangular outline with a
2pt border and 2pt padding. It keeps the question lead-in with the following content, with 0.12
inches before and 0.05 inches after.

### Question Follow

Question Follow inherits Question Heading and removes the leading space. It is also regular and
non-italic. The builder selects it after a chapter heading, image, or table, and for subsequent
hard-break paragraphs within one question stem, so consecutive question text stays compact.

### Matching Prompt

Matching Prompt is 11pt normal text with a 0.2 inch left indent and a -0.2 inch hanging indent. It uses 1.25 line spacing, 0.07 inches before, and tab stops at 0.5 and 3.5 inches for two-column prompt rows. A prompt may carry an image after its numbered blank.

## Choice styles

Choice paragraphs use a 0.13 inch left indent and 10pt text. The concrete `Choices 2` through `Choices 5` styles inherit the base Choice style and receive their tab stops from `layout_tab_stops` in the YAML configuration:

| Columns | Tab stops in inches |
| ---: | --- |
| 2 | 3.78 |
| 3 | 2.46, 4.80 |
| 4 | 1.88, 3.63, 5.38 |
| 5 | 1.53, 2.93, 4.33, 5.73 |

The layout algorithm scores visible text width and selects a concrete `Choices N` style. Long five-choice sets fall back to one choice per paragraph before text can wrap underneath a neighboring choice. Choice paragraphs have a small configured space before them to separate answer options from the question stem. Text and image choices use paragraph tab stops by default; the optional `--native-tables` mode uses the dedicated table backend for preserved simple HTML tables.

## Images and tables

- A standalone question image is capped at 5.6 inches wide.
- Rendered table PNGs use their intrinsic 96 CSS-pixels-per-inch size as an
  additional upper bound before these caps, so small source tables are not
  silently enlarged.
- Image choices use a 3.40 inch global width ceiling, a 2.00 inch height ceiling, and lower per-column caps in the builder.
- Matching-prompt images use a 1.40 inch height cap.
- Wide one-row sequence strips with an aspect ratio of at least 4.0 use a 0.40 inch height cap.
- Full-width image choices require the more conservative `choice_strip_min_aspect` threshold (8.0 in the shipped style), keeping shorter matching panels in the ordinary choice layout.
- Question-level data tables are built as DOCX tables; native HTML table conversion is isolated in `docx_table_builder.py` and is opt-in. The native backup accepts simple logical cell grids, while browser-positioned drawings and `colgroup` layout tables retain their PNG fallback.
- HTML drawing tables rasterized through Chromium use Atkinson Hyperlegible Next for regular
  table text and Atkinson Hyperlegible Mono for code or explicitly monospace content. Both fonts
  must be installed on the machine generating the PNGs.

## Page header

Body pages use the Header style with page numbering, the exam date, and a student name line separated by configured tab stops. The first page receives a separate header configuration so the title and student information do not inherit the body-page header.

## Source of truth

Edit [../styles/exam_styles.yaml](../styles/exam_styles.yaml) for stable layout values. Keep rendering behavior in [../ef_tools/docx_builder.py](../ef_tools/docx_builder.py), choice-width decisions in [../ef_tools/layout.py](../ef_tools/layout.py), and the exam field contract in [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md). Use [../tests/test_docx_choice_styles.py](../tests/test_docx_choice_styles.py) and the focused builder tests for demonstrated style invariants.
