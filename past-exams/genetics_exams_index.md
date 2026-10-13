# Searchable genetics exams

Ten exam families, 141 PDF pages. These image-free Markdown companions are lossy search
references, not replacements for the archived PDFs or editable sources. See the
[GENETICS_EXAM_BPQ_AUDIT.md](../docs/GENETICS_EXAM_BPQ_AUDIT.md) for the coverage survey.
Each exam has its own lower snake_case Markdown file in tracked `past-exams/`.

## Exam inventory

| Searchable text | PDF authority | Pages | Native companions |
| --- | --- | ---: | --- |
| [2016_genetics_final.md](2016_genetics_final.md) | `2016_genetics_final.pdf` | 11 | None supplied |
| [2016_genetics_midterm.md](2016_genetics_midterm.md) | `2016_genetics_midterm.pdf` | 13 | None supplied |
| [2017_genetics_final.md](2017_genetics_final.md) | `2017_genetics_final.pdf` | 15 | None supplied |
| [2017_genetics_midterm.md](2017_genetics_midterm.md) | `2017_genetics_midterm.pdf` | 13 | None supplied |
| [2018_genetics_final.md](2018_genetics_final.md) | `2018_genetics_final.pdf` | 16 | None supplied |
| [2018_genetics_midterm.md](2018_genetics_midterm.md) | `2018_genetics_midterm.pdf` | 10 | `2018_genetics_midterm.odt`; later edited; PDF page 11 absent |
| [2019_genetics_final.md](2019_genetics_final.md) | `2019_genetics_final.pdf` | 18 | `2019_genetics_final.docx`, `2019_genetics_final.odt` |
| [2019_genetics_midterm.md](2019_genetics_midterm.md) | `2019_genetics_midterm.pdf` | 14 | None supplied |
| [2025_genetics_final.md](2025_genetics_final.md) | `2025_genetics_final.pdf` | 18 | `2025_genetics_final.docx`, `2025_genetics_final.odt` |
| [2025_genetics_midterm.md](2025_genetics_midterm.md) | `2025_genetics_midterm.pdf` | 13 | `2025_genetics_midterm.docx`, `2025_genetics_midterm.odt` |

## Conversion method

Applied the book-to-markdown skill on 2026-10-13: measured PDF extraction, compared a bounded
four-page sample, compared native conversions, selected the least destructive extraction,
then checked the complete corpus. The installed tools have moved from the skill's older
`tools/` paths into `extract/`, `cleanup/`, and `audit/` in the book-to-markdown checkout.

- Primary text: Poppler `pdftotext -layout`; every non-header text line is retained.
- Sample comparison: the skill raw-text extractor retained words but flattened a growth matrix
  into one-token lines; layout extraction preserved its rows and answer-choice groupings.
- Native comparison: Pandoc GFM for all seven DOCX/ODT files. The skill Lua filter failed with
  `Cannot get Attr from TypeNil`; plain Pandoc succeeded. No upstream tools were modified.
- One canonical text per exam family. DOCX/ODT list numbering is not substituted for PDF numbers.
- Chapter/section headings support navigation; quoted PDF page locators support source lookup.
  Running headers, name/score blanks, blank writing space and rendered images are omitted.
- Fixed-width text blocks protect extracted tables and choice layouts. Line breaks within prose
  remain where removing them might mix columns or detach a question from its choices.
- Unicode signs are normalized into searchable ASCII: `chi`, `male`, `female`, `x`, `sqrt`,
  `->`, `1/2`, `^2`, and so on. Some superscripts were already flattened by PDF extraction.
- Figure labels may survive while connections, positions, colors and bands do not. Omission
  notes identify important figure-dependent sections. Never infer a pedigree or tree from
  the remaining labels alone.
- No OCR or manual answer reconstruction. Embedded-image text, including critical-value tables,
  may be absent. Stacked fractions/formulas can be ambiguous. Consult the original PDF.
- Preserve typos, contradictory data, skipped numbers and draft material. Conversion notes are
  clearly distinguished from source text. No question or solution is invented to fill a gap.

## Validation evidence

- Ten outputs have one H1 each, balanced code fences, ASCII text and no embedded images.
- All 141 page locators are present; retained source-line checks cover every PDF text page.
- Native-text checks corroborate the 2025 midterm Q84-to-Q92 jump and short-answer topics;
  both 2019 final native formats also contain the extra sparrow/pigeon draft material.
- The skill cleaner uses image/HTML/ASCII passes with reflow, figure-debris deletion and
  dehyphenation disabled to protect exam choices and tables.
- The book delivery validator has a book-specific `Title-YYYY.md` naming rule. These files
  follow the instructor's lower snake_case artifact convention and exam filenames;
  filename-shape findings are documented rather than renaming exams as books.
- Markdown companions live in tracked `past-exams/`; original PDF/native sources remain
  in `ARTIFACTS/`. No source archive move is appropriate.
- Conversion receipts, native comparisons, sample output and rendered review sheets are local
  working evidence under `output_genetics_audit/`, outside version control.

## Recovered 2018 midterm

The source is `2018-Genetics-2fall/2018-EXAM_QUIZ/exam1-midterm.pdf`, dated October 22, 2018.
It is distinct from 2017: 89 multiple-choice items and three different short answers. It contains
all those numbered prompts but has ten physical pages, labeled 1-10 of 11. The earlier archive
pass excluded it on that page-count discrepancy; it is now retained with the limitation explicit.

The native ODT contains Fun Points but was last edited in December 2019 and changes the
short-answer skip instructions. Its eight archive copies are byte-identical. The Markdown uses
the dated PDF and does not merge later native text or invent PDF page 11. The 2018 directory's
`old_exam1-midterm.pdf` is a legacy 2017 version. Search/comparison and restoration receipts are
in `output_2018_midterm_search/`.

## PDF snapshot hashes

SHA-256 identifies the exact PDF underlying each searchable companion.

| PDF | SHA-256 |
| --- | --- |
| 2016_genetics_final.pdf | `56809e6d965c232f66089a3f057bf4f396eb4990b171f57b2b2da90ccb2e396c` |
| 2016_genetics_midterm.pdf | `a8bd53b4eb0057223a08f2e43aea6fdc939bce438b4eec6ab2c0220aaf242a45` |
| 2017_genetics_final.pdf | `89809db4fb097c23dfcafad032030d7006101c99b94fe3d82d62fd1ff6e0f091` |
| 2017_genetics_midterm.pdf | `393e86d2a5e90f576ddfdff8b6f15bad7861fa9f8ecf45471dc849f36d5cd3d4` |
| 2018_genetics_final.pdf | `f0a8c28bfbb8f08b18562cb4fd3430d78e62d719a0b7dbe7aa2ad264b0a1dd59` |
| 2018_genetics_midterm.pdf | `29543db68f54355f3059f5fafd63e46fc5ba60768f8e6bb97434956bf2690677` |
| 2019_genetics_final.pdf | `83cda1c3386cad12f9c32ba50b7377ed7565c8eae67edec2ce352455b5ae9bd8` |
| 2019_genetics_midterm.pdf | `b6f0ba6d4f6d3743521176deb8e2dd07d0bc90abdef600b95880a4ab3c5edf80` |
| 2025_genetics_final.pdf | `93711826c038733fd7c6474ffe2d90a47b675740798a85d7c34880a1062d9524` |
| 2025_genetics_midterm.pdf | `85c59bb5bec15f26b6a165dfef647009d54db467af796816dce63ae301783e49` |
