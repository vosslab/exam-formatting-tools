# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

- Exam 1 covers Quiz 1, Quiz 2, and the genetics Tasks 1 website CSV. Avoid repeating
  overlapping question variants; use full pedigrees in place of autosomal-only pedigrees.
- Prefer MATCH over WOMC versions of the same content.
- Exams use ZipGrade: every answer bank has at most five choices, A through E.
- Give root-level build scripts descriptive names and organize them by their purpose.
- Prefer flat shell scripts for assessment generation. Put reusable complexity in common tools.
- My quizzes have a style and my exams have a style. Document those general conventions
  separately from the subject or individual assessment.
- There are no calculators on quizzes or exams. Show the arithmetic and evaluated results
  in calculation choices, as in my historical assessment artifacts.
- Use en dashes for negative signs and subtraction in assessment calculations; hyphens are too small.
- Always pair alpha with its name, level of significance, and write null hypothesis
  (H0) rather than a standalone H0. Follow `chi-square_terms.yml` for statistical term colors.
- Apply KISS aggressively. Add mechanisms and configuration only for demonstrated needs;
  prefer sensible fixed behavior for internal decisions.
- Ground acceptance checks in actual requirements and known failures. Byte or pixel equality
  and arbitrary performance thresholds should not constrain useful improvements.
- Treat permanent tests as liabilities as well as assets. Protect important, stable behavior;
  use ignored `tests/_temp/` checks for one-time proof and remove them when finished.

- For all assignments, exams, and quizzes in all classes, each matching prompt counts as
  1/2 point (four matches = two points); each MC/MA question counts as one point.
- Also track the number of questions as rows to fill in on ZipGrade, separately from
  points. My ZipGrade form has only 100 question bubble rows.
- I prefer to keep point values out of headings for assignments, exams, and quizzes.
- Human Guidance is for durable, reusable preferences, not one-off task instructions.

- I use LibreOffice Writer to open generated DOCX files; DOCX is an intermediate because its
  Python tooling is better. Additional ODT artifacts are unnecessary unless an actual problem
  requires ODT modification.
- Reusable document formatting should live in named styles so I can change choice layouts manually.
  A 0.10-inch inset for choices is enough; use the genetics midterm for varied layout review.

- Keep reusable guides generic: document stable conversion and editing workflows rather than a
  current quiz. Put assessment-specific recipes in their notes and dated results in the changelog.
