# FAQ

Short answers to recurring questions about the exam conversion pipeline.

## Why use YAML in the middle?

YAML gives every converter one inspectable handoff format. It also lets authors validate, filter, and render the same exam data without rerunning the original question-bank parser.

## Why does a matching block use several numbers?

Each prompt is a separately graded row. The shared `question_span()` rule counts those prompt rows for DOCX numbering, ZipGrade validation, totals, and answer keys.

## Why does exam mode skip a question?

Exam mode keeps questions compatible with the ZipGrade A-E form. It retries generator candidates and reports a task as skipped when no candidate fits; it does not choose a distractor or truncate a six-choice question automatically.

## Why are some table drawings PNG files?

Table-cell drawings such as gels, pedigrees, and sequence strips carry visual meaning that plain text cannot preserve. The default BBQ path rasterizes them into `<stem>_files/` and records relative image paths in YAML. The optional `yaml_to_exam_docx.py --native-tables` path converts supported simple cell grids into editable Word tables; nested, malformed, browser-positioned, and `colgroup` layout drawings retain the PNG fallback.

## Why is there no direct HTML-to-DOCX command?

The two-step HTML-to-YAML-to-DOCX path keeps parsing and document layout independently testable. The former direct HTML-to-DOCX path was removed because it duplicated that pipeline.
