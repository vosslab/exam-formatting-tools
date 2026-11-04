# Choice formatting

Generated DOCX answer choices use named paragraph styles and tab-separated columns.
Open the DOCX directly in LibreOffice Writer to make final layout edits. PDF export does not
require an ODT intermediate. This guide describes automatic text-choice selection, the
style contract, and the separate image-choice path.

## Styles and editing

`Choice` is the shared base for `Choices 2` through `Choices 5`. The concrete styles inherit
10pt text, single line spacing, zero space before and after, and the same hanging indent.
Each concrete style defines its own column tab stops. Question styles supply separation
between question blocks; emitters do not override choice-row spacing.

The shipped settings place the first choice label 0.10 inches inside the question edge.
Wrapped choice text starts at 0.26 inches, using a -0.16-inch first-line indent.
`Choice Label` supplies the bold letter prefix. Scientific markup and explicit `choice_font`
values retain their intended character formatting.

Each generated row is a separate paragraph; choices within that row are separated by tabs.
Changing Choices 3 to Choices 2 changes the tab grid while preserving shared formatting.
It does not redistribute answers between existing paragraphs. Move the tabs and paragraph
breaks as needed when editing a choice group manually.

An explicit question-level YAML `layout: 1` through `layout: 5` bypasses automatic text
measurement. The task CSV's optional `layout` column supplies the same field. `layout: 1`
means one choice per paragraph, rendered with the concrete `Choices 2` style; the style
name alone therefore does not establish how many choices a paragraph contains.

## Measuring formatted answers

[../ef_tools/choice_measurement.py](../ef_tools/choice_measurement.py) measures every complete
text answer in points, including its bold `(A) `, `(B) `, or subsequent letter prefix.
Both ordinary `choices` and matching `choices_list` use this method when they contain text.

The measurement follows the rich-text parser used by the DOCX renderer:

- Decode HTML entities before measuring; markup itself contributes no width.
- Use `choice_font` when supplied, otherwise the configured primary font.
- Resolve regular, bold, italic, and bold-italic faces separately.
- Use the configured monospace family for code runs, and 8pt for small-text runs.
- Measure subscript and superscript glyphs at full size as a conservative bound on Writer's
  reduced glyphs. Color and background-color markup do not change width.
- Follow the renderer's text-run normalization: skip standalone hard-break segments and
  flatten remaining newlines to spaces.

Fontconfig's `fc-match` resolves the font file and face index. The index matters for named
instances of variable fonts: opening only the file can measure regular instead of bold.
Pillow loads that face at size 1000, then scales its measurements to the configured point size.
Font faces are cached across answers.

For each run, the measured width is the larger of its advance width and its ink extent,
including any left overhang. This accounts conservatively for italic glyphs extending past
their advance. The complete answer width is the sum of its label and formatted-run widths.
See [INSTALL.md](INSTALL.md) for fontconfig and font installation requirements.

## Calculating each tab slot

[../ef_tools/layout.py](../ef_tools/layout.py) checks candidate layouts using the page and
tab geometry prepared by [../ef_tools/style_loader.py](../ef_tools/style_loader.py).
Positions are relative to the left text margin; inches are converted at 72 points per inch.

```text
first_origin = (choice_indent + choice_first_line_indent) * 72
right_edge = (page_width - 2 * page_margin) * 72
starts = [first_origin] + [each candidate tab stop * 72]
ends = starts[1:] + [right_edge]
gap = choice_font_size / 2

column = answer_index % column_count
fits = answer_width + gap <= ends[column] - starts[column]
```

Every answer must fit its own slot. The check includes the final column, whose slot ends at
the right text margin, and repeats for subsequent rows. It does not compare only the longest
answer with a generic column width. A4 uses its adapted tab stops and printable width, while
fonts and point sizes remain unchanged.

The gap is half an em: 5 points at the shipped 10pt choice size. It leaves visible separation
and prevents an answer from ending exactly at the next tab stop. The same reserve is applied
at the right edge.

For example, the shipped Letter Choices 3 first slot starts at 0.10 inches and ends at
2.43 inches, giving 167.76 points of space:

| Complete answer width | With 5pt gap | Result |
| ---: | ---: | --- |
| 160pt | 165pt | Fits |
| 165pt | 170pt | Reject this candidate layout |

These are illustrative Letter values, not additional thresholds. Configuration and paper
adaptation determine the slots used by the algorithm.

## Selecting the row arrangement

The selector tries these established arrangements in order and accepts the first for which
all answers pass the slot check:

| Answer count | Candidate columns, in order | Fallback |
| --- | --- | --- |
| 1 | None | One per paragraph |
| 2 | 2 | One per paragraph |
| 3 | 3 | One per paragraph |
| 4 | 4, then 2 | One per paragraph |
| 5 or more | 5, then 3 | One per paragraph |

For five answers, three columns produce a 3+2 arrangement. Four answers can use 2+2.
For larger banks, rows are chunked at the selected column count; the final row may be partial.
A fallback to one per paragraph lets long answers wrap with the normal hanging indent.
The previous `layout_limits` character-count budgets no longer control selection.

## Image choices and limitations

Image choices use the separate sizing and placement rules in
[../ef_tools/docx_images.py](../ef_tools/docx_images.py) and
[../ef_tools/docx_choice_builder.py](../ef_tools/docx_choice_builder.py).
The text-width selector does not replace image-column fit checks, wide-strip stacking,
caption handling, or fixed-scale drawing sizing. The optional native-table path also remains
separate. All shared picture insertion paths explicitly zero image edge distances.

An "actual slot" means the configured DOCX geometry, not a slot measured from a rendered
LibreOffice page. Pillow and LibreOffice are different layout engines. Font substitution,
font-version differences, and glyph fallback can change the result. Explicit layout overrides
can also force a row that does not fit. PDF inspection remains the final visual check.

## Verification and troubleshooting

Use the same representative assessment YAML and media for before/after comparisons, so random
question generation does not obscure layout changes. Include short and long answers, matching
blocks, mixed regular/code text, and borderline multi-column rows. Review both the DOCX in
LibreOffice and the exported PDF.

Dated validation results belong in [CHANGELOG.md](CHANGELOG.md); they describe a particular
run rather than a guarantee for future documents.

If a row still overruns, retain the exact YAML and inspect its `layout` override, `choice_font`,
resolved font face, paper size, and tab positions before tuning the algorithm. Fix the selection
or measurement at its source rather than adding direct formatting to the generated paragraph.
Permanent coverage lives in [../tests/test_layout.py](../tests/test_layout.py) and
[../tests/test_choice_measurement.py](../tests/test_choice_measurement.py).

Formatting values live in [../assessment_styles/exam_styles.yaml](../assessment_styles/exam_styles.yaml).
See [../assessment_styles/YAML_EXAM_FORMAT.md](../assessment_styles/YAML_EXAM_FORMAT.md) for
input fields and [../assessment_styles/EXAM_STYLE.md](../assessment_styles/EXAM_STYLE.md) for
the broader assessment presentation rules.
