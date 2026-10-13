# Assessment creation and styling

This folder holds documentation and formatting configuration used to create assessments.
Its scope includes shared assignment, exam, and quiz conventions, presentation, question-selection decisions,
coverage planning, scoring decisions, and outstanding questions for individual assessments.
Despite the folder name, it covers more than visual styling.

## Scoring for every class

For all assignments, exams, and quizzes, each matching prompt is worth 0.5 point
(four matches = two points). Each MC or MA question is worth one point.
Numbered answer rows remain separate from the point total. The shared DOCX converter
calculates this total automatically unless an explicit `total_points` override is supplied.
Keep point values out of assessment titles and section headings. Put scoring information
in the score line or instructions.

For assessments using ZipGrade, also count the numbered answer rows: the form has
100 rows maximum. Each matching prompt consumes one row, and each MC/MA question
consumes one row, even when multiple letters are selected. Four matches therefore
use four rows but earn two points. Report both row count and point total when planning
an assessment; neither the number of question blocks nor the point total measures
answer-sheet capacity.

## Contents

- [YAML_EXAM_FORMAT.md](YAML_EXAM_FORMAT.md): canonical assessment YAML fields and examples.
- [EXAM_STYLE.md](EXAM_STYLE.md): general exam conventions, ZipGrade requirements, and shared
  DOCX formatting details.
- [QUIZ_STYLE.md](QUIZ_STYLE.md): general quiz presentation and scoring conventions.
- [GENETICS_EXAM1.md](GENETICS_EXAM1.md): selection, coverage, and decisions for Genetics Exam 1.
- [exam_styles.yaml](exam_styles.yaml): machine-readable formatting values used by the converters.

Put reusable guidance and assessment-specific creation notes here. Keep general conventions in
the exam and quiz guides; use separate assessment documents for their particular decisions.

Related resources have their own homes: [task_files/](../task_files/) holds question-selection
CSVs, [builders/](../builders/) holds assessment build commands, and
[converters/](../converters/) holds general conversion and validation commands.
[docs/](../docs/) holds general repository and tool documentation.

Reference full BPW task catalogs directly under
`~/nsh/PROBLEMS/biology-problems-website/task_files/`; do not mirror them here.
Local task CSVs hold only assessment-specific selections and settings.

## Reference archive names

Name assessment files in `ARTIFACTS/` as `YEAR_subject_assessment.ext`, using lowercase
subject and assessment names with underscores. Use the year printed in the exam title,
not an export date or the folder where an old exam was reused. Examples:
`2019_genetics_midterm.pdf`, `2026_biochemistry_exam1.docx`, and
`2019_biochemistry_final_part_a.pdf`. Corresponding PDF, DOCX, and ODT files share a stem.
Use meaningful qualifiers such as `part_a`; omit workflow labels such as `edit` or `best_version`.

For the genetics archive curation, retain complete representative exams and group alternate
forms and revised exports by substantive content. Set-aside imports are preserved outside
ARTIFACTS in `output_genetics_archive_review/set_aside/`. The archive's
`genetics_exam_sources.tsv` records imported source paths, and `artifact_renames.tsv`
records the naming migration. The 2018 midterm is set aside because its export has only
10 of its stated 11 pages.
