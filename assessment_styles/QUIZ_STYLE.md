# Quiz style

These conventions apply to quizzes in every subject. Use the task CSV for the selected content
and assessment-specific notes for scope and scoring decisions. Shared typography and drawing
settings are documented in [EXAM_STYLE.md](EXAM_STYLE.md#shared-docx-formatting).

## Content and scoring

- Keep coverage focused on the material taught before the quiz.
- Prefer medium difficulty when a question family offers difficulty levels.
- Prefer MATCH over WOMC for equivalent content, including terminology questions.
- Avoid repeating alternate formats of the same reasoning task.
- Quizzes may use more than five choices. Apply [EXAM_STYLE.md](EXAM_STYLE.md)'s A-E limit when
  a quiz will use ZipGrade; ordinary `--quiz` mode does not enforce it.
- Number each matching prompt individually, and show the block's question range.
- Choose and display the point total explicitly. Matching prompts may carry fractional points;
  numbered answer count is not automatically the grading total.

## Presentation

- Show a clear quiz title, student name line, and score line.
- Group related questions under topic headings; include scoring information when useful.
- Keep matching choices and prompts easy to compare, with enough space to write each answer.
- Use one choice per line for long statements rather than crowding neighboring columns.
- Start a topic on a new page when its matching block or overall layout benefits. This is an
  assessment choice, not a required page break for every quiz section.
- Preserve readable diagrams and tables. Check the rendered PDF before classroom use.

## Generation workflow

Use a flat shell script to call the common tools. Select `--quiz` on the task importer and
use `--points` to set the total. A task CSV `layout` value of `1` prints that question's choices
one per line; a blank value uses automatic layout.

The common DOCX converter accepts `--page-break-sections` and `--keep-questions-together`
when needed. Export through `bash converters/docx_to_pdf.sh FILE.docx OUTPUT_DIR [DPI]`.
Keep these behaviors in the shared tools rather than creating a Python formatter for each quiz.

Keep YAML, media, and the matching answer key together. Rebuild from saved YAML to preserve
the questions; rerunning generators draws new questions. See [USAGE.md](../docs/USAGE.md) and
[YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md) for the common interfaces.
