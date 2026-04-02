# ODT exam styles reference

Style definitions extracted from `ARTIFACTS/2025_genetics_final_exam2.odt` (December 2024) and `ARTIFACTS/exam1-midtermA2-best_version.odt` (2019).

## Page layouts

| Layout | Usage | Width | Height | Top | Bottom | Left | Right |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mpm1 (Standard) | Body pages | 8.5in | 11in | 0.6in | 0.6in | 0.6in | 0.6in |
| Mpm2 (First Page) | Title page | 8.5in | 11in | 0.5in | 0.5in | 1.0in | 1.0in |
| Mpm3 (HTML) | HTML import | 8.5in | 11in | 0.39in | 0.39in | 0.79in | 0.39in |

All layouts use portrait orientation, `lr-tb` writing mode, and standard letter size.

### Master pages

- **Standard**: uses Mpm1 layout (body pages)
- **First Page**: uses Mpm2 layout, next style is Standard
- **HTML**: uses Mpm3 layout

## Base text style (Standard)

| Property | Value |
| --- | --- |
| Font family | Liberation Sans |
| Font size | 11pt |
| Font type | swiss, variable pitch |
| Line height | 110% |
| Bottom margin | 0.05in |
| Top margin | 0in |
| Language | en-US |

## Paragraph styles

### Question Heading

Parent: Standard. Used for the bold/italic lead-in line before a question.

| Property | Value |
| --- | --- |
| Font weight | bold |
| Font style | italic |
| Font size | 11pt |
| Left margin | 0.2in |
| Text indent | -0.2in (hanging) |
| Top margin | 0.15in |
| Bottom margin | 0.02in |
| Keep with next | always |
| Auto text indent | false |
| Text autospace | none |

Auto-selected when the previous element is another question or choices.

### Question

Parent: Question Heading. Used for the question body text.

| Property | Value |
| --- | --- |
| Font weight | normal |
| Font style | normal |
| Line height | 125% |
| Left margin | 0.2in |
| Text indent | -0.2in (hanging) |
| Top margin | 0in |
| Bottom margin | 0.07in |
| Keep with next | auto |
| Orphans | 2 |
| Widows | 2 |
| Tab stops | 0.5in, 3.5in |

### Question Follow

Parent: Standard. Used for the first question after an image, table, or chapter heading.

Auto-selected when the previous element is an image, table, or chapter heading.

## Automatic question style selection

The `odt_exam_builder.py` module automatically selects the appropriate question
style based on what precedes the question in the document:

| Previous element | Selected style | Usage |
| --- | --- | --- |
| Another question statement | Question Heading | Normal flow between questions |
| Choices paragraph | Question Heading | Normal flow after multiple choice |
| Chapter/section heading | Question Follow | First question in a section |
| Table | Question Follow | First question after a matching table |
| Image | Question Follow | First question after an embedded image |

This auto-selection reduces spacing and visual awkwardness when questions follow
non-question elements (especially images and tables), while maintaining standard
formatting for questions in normal sequential flow.

### Choices (base)

Parent: Standard. Base style for multiple-choice answer lines.

| Property | Value |
| --- | --- |
| Font size | 10pt |
| Left margin | 0.15in |
| Text indent | -0.05in |
| Writing mode | page |

### Choices3 (2 columns of choices)

Parent: Choices.

| Tab stop | Position |
| --- | --- |
| 1 | 2.33in |
| 2 | 4.67in |

### Choices4 (3 columns of choices)

Parent: Choices.

| Tab stop | Position |
| --- | --- |
| 1 | 1.75in |
| 2 | 3.50in |
| 3 | 5.25in |

### Choices5 (4 columns of choices)

Parent: Choices.

| Tab stop | Position |
| --- | --- |
| 1 | 1.40in |
| 2 | 2.80in |
| 3 | 4.20in |
| 4 | 5.60in |

### Warning

Parent: Standard. Dark background block for warnings or special notices.

| Property | Value |
| --- | --- |
| Background color | #333333 |
| Fill | solid |
| Shadow | none |

### Preformatted Text

Parent: Standard. Monospace block for code or fixed-width content.

| Property | Value |
| --- | --- |
| Font family | Courier New |
| Font size | 10pt |
| Font pitch | fixed |
| Top margin | 0in |
| Bottom margin | 0in |

### Table Contents

Parent: Standard. Text inside table cells.

| Property | Value |
| --- | --- |
| Line height | 90% |
| Top margin | 0in |
| Bottom margin | 0in |
| Line numbering | disabled |

### Table Heading

Parent: Standard. Bold centered text for table header rows.

## Heading styles

| Style | Font size | Weight | Notes |
| --- | --- | --- | --- |
| Heading (base) | 14pt | normal | Liberation Sans, keep-with-next, top 0.17in, bottom 0.08in |
| Heading 1 | 115% | bold | Exam title |
| Heading 2 | 14pt | bold italic | Section divider, bottom border |
| Heading 3 | 12pt | bold | Subsection |
| Heading 4 | 11pt | bold | Chapter headings (e.g., "Chapter 1 -- Foundations") |

## Table cell colors

Used for answer-key tables and grading indicators.

| Color | Hex | RGB | Meaning |
| --- | --- | --- | --- |
| Light red | #ffe6e6 | 255, 230, 230 | Incorrect answer |
| Light blue | #e6f3ff | 230, 243, 255 | Correct answer |
| Light green | #e6ffe6 | 230, 255, 230 | Partial credit |
| Light gray | #f2f2f2 | 242, 242, 242 | Header / neutral |

Common table cell properties: vertical-align middle, padding 0.0194in, border none.

## List / numbering styles

Four list styles found: WWNum1, WWNum2, RTF_Num 2, RTF_Num 3.

Typical level formatting:

| Level | Format | Suffix | Tab stop | Indent | Margin |
| --- | --- | --- | --- | --- | --- |
| 1 | 1, 2, 3 | . | 0.5in | -0.25in | 0.5in |
| 2 | a, b, c | . | 1.0in | -0.25in | 1.0in |
| 3 | i, ii, iii | . | 1.5in | -0.25in | 1.5in |

## Font families

| Font | Role |
| --- | --- |
| Liberation Sans | Primary exam font (questions, headings, body) |
| Liberation Serif | Secondary body text |
| Courier New | Monospace / preformatted text |
| Times New Roman | Fallback serif |
| OpenSymbol | Special characters and symbols |
| WenQuanYi Zen Hei | Asian text fallback |

## Document structure patterns

Typical exam document order:

1. First Page master page with wider margins
2. Exam title in Heading 1 style
3. Student info line (name, score) in Standard style
4. Section headers in Heading 4 (e.g., "Chapter 1 -- Foundations")
5. Question Heading paragraph (bold italic lead-in)
6. Question paragraph (question body, 125% line height)
7. Choices3/4/5 paragraph (tab-separated answer options)
8. Tables with colored cells for matching or answer keys
9. Embedded images anchored in table cells or paragraphs

## ODT technical notes

- ODT files are ZIP archives containing `styles.xml`, `content.xml`, `meta.xml`, `manifest.xml`
- Named styles live in `styles.xml` under `office:styles`
- Automatic (per-element) styles live in `content.xml` under `office:automatic-styles`
- The 2025 final exam has 1,731 automatic styles; the 2019 exam has 628
- Key XML namespaces: `fo:` (formatting objects), `style:` (style properties), `text:` (text content), `draw:` (graphics), `table:` (tables)
- `odfpy` is not currently installed; use `lxml` + `zipfile` for manipulation

## Future tools

Planned tools to work with these styles:

- **odt_exam_builder.py**: generate properly-styled ODT exams from question data
- **extract_odt_styles.py**: extract and compare styles across ODT files
- **propagate_odt_styles.py**: apply a source ODT's styles to target ODT files
