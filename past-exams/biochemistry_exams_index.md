# Biochemistry past-exam searchable text

This index holds the lossy, image-free Markdown companions for four biochemistry
exam families. The PDF remains the source of truth for figures, molecular structures,
colors, exact graphical layout, and any text placed only inside a diagram.

| Exam family | PDF pages | Searchable Markdown | Corroborating native sources |
| --- | ---: | --- | --- |
| 2019 final, part A | 8 | [2019_biochemistry_final_part_a.md](2019_biochemistry_final_part_a.md) | [2019_biochemistry_final_part_a.docx](../ARTIFACTS/2019_biochemistry_final_part_a.docx), [2019_biochemistry_final_part_a.odt](../ARTIFACTS/2019_biochemistry_final_part_a.odt), [2019_biochemistry_final_part_a.pdf](../ARTIFACTS/2019_biochemistry_final_part_a.pdf) |
| 2019 final, part B | 8 | [2019_biochemistry_final_part_b.md](2019_biochemistry_final_part_b.md) | [2019_biochemistry_final_part_b.docx](../ARTIFACTS/2019_biochemistry_final_part_b.docx), [2019_biochemistry_final_part_b.odt](../ARTIFACTS/2019_biochemistry_final_part_b.odt), [2019_biochemistry_final_part_b.pdf](../ARTIFACTS/2019_biochemistry_final_part_b.pdf) |
| 2019 midterm | 12 | [2019_biochemistry_midterm.md](2019_biochemistry_midterm.md) | [2019_biochemistry_midterm.docx](../ARTIFACTS/2019_biochemistry_midterm.docx), [2019_biochemistry_midterm.odt](../ARTIFACTS/2019_biochemistry_midterm.odt), [2019_biochemistry_midterm.pdf](../ARTIFACTS/2019_biochemistry_midterm.pdf) |
| 2026 exam 1 | 10 | [2026_biochemistry_exam1.md](2026_biochemistry_exam1.md) | [2026_biochemistry_exam1.docx](../ARTIFACTS/2026_biochemistry_exam1.docx), [2026_biochemistry_exam1.odt](../ARTIFACTS/2026_biochemistry_exam1.odt), [2026_biochemistry_exam1.pdf](../ARTIFACTS/2026_biochemistry_exam1.pdf) |

## Conversion method and limits

The Markdown uses `pdftotext -layout` for the canonical text because it retained
multiple-choice columns and simple table rows more reliably than raw reading-order
extraction. Each source PDF page is a separate fixed-width text block. Unicode symbols
were normalized to ASCII words or notation (`alpha`, `beta`, `Delta`, `->`, `^2`), so
the companions are greppable but are not visual recreations.

All eight DOCX and ODT companions were converted with Pandoc and compared as
corroborating sources. Their Pandoc exports differ in line wrapping, list markup, image
paths, and table serialization, but did not provide a confirmed alternate exam version.
The canonical Markdown therefore follows the PDF for numbering and page boundaries.
Questions that depend on a structure, graph, image, or unextracted table cell remain
present as text prompts with the missing visual content indicated by the surrounding
context; use the linked PDF to interpret them.

## Validation

The four PDF text layers measured usable by the book-to-markdown extractor. The final
companions contain one H1 each, 38 source-PDF page locators, balanced fixed-width fences,
ASCII-only text, no image markup, and local links to every original PDF, DOCX, and ODT.
The preserved layout-text copies and source/Markdown SHA-256 receipt are in the ignored
`output_biochemistry_markdown/` evidence directory.

The book-to-markdown delivery validator reports the expected filename-only exception:
its book-title convention does not accept these user-requested lower-snake-case artifact
filenames. All substantive content checks above pass.
