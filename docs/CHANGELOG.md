# Changelog

## 2026-10-13

### Additions and New Features

- Recover the distinct 2018 genetics midterm from the original course folder and retain its
  PDF/ODT in `ARTIFACTS/`, with `past-exams/2018_genetics_midterm.md`. The October 22,
  2018 PDF contains 89 MC and three SA prompts on ten pages labeled 1-10 of 11.
  Preserve later native bonus content/changed skip instructions separately; update the index,
  archive mappings and audit to ten genetics exams/141 PDF pages.
- Add docs/GENETICS_LECTURE_BPQ_AUDIT.md with evidence from maintained 2025/2026
  lecture PDFs/ODPs. Revise the exam audit so current instruction governs priorities:
  carrier inference, phenotype conditioning, Z-linked lethality and unequal gamete weights.
  Identify selected-offspring BPQ reuse; lower exam-only AR + XLR, combined epistasis/
  incomplete dominance and Robertsonian dosage proposals pending teaching confirmation.
- Add four individual searchable biochemistry exam Markdown artifacts in `past-exams/`:
  the 2019 midterm, final parts A/B, and 2026 exam 1. Preserve extracted wording,
  numbering, choices and tables across 38 PDF pages; corroborate eight native sources.
  Link the originals through `past-exams/biochemistry_exams_index.md`.
- Add docs/GENETICS_EXAM_BPQ_AUDIT.md: survey all ten archived genetics exams
  against 130 configured genetics task rows and relevant BPQ source implementations.
  Separate current-course expansion candidates from intentionally retired lecture topics,
  time-limited inbreeding content, and reduced distance-matrix instruction. Preserve the
  earlier inventory-only audit in docs/archive as the starting reference.
- Add ten lossy, image-free searchable exam Markdown companions and an index under
  `past-exams/`. Preserve original numbering, choices, text tables, and source defects;
  flag omitted figures and corroborate the six DOCX/ODT companions. Keep original
  PDFs and native documents unchanged.

### Behavior or Interface Changes

- Follow the instructor's exam-artifact naming: keep the nine genetics companions and
  their index in tracked `past-exams/` with lower snake_case filenames. Update source
  links to `ARTIFACTS/` and audit links to the moved Markdown files.
- Add --paper-size letter|a4 to the DOCX converter, preserving Letter as its default.
  Set the Genetics Exam 1 builder to A4; its optional letter argument switches back.
  Set explicit page dimensions and adapt header, name/score, answer-choice, and matching
  tabs for A4 while preserving fonts, colors, margins, and drawing scale. Keep loaded
  base styles unchanged so switching sizes is reversible.

### Developer Tests and Notes

- Compare the 2018 exam with 2017: shared question families but different structure and all
  three SA prompts changed. Identify `old_exam1-midterm.pdf` as a legacy 2017 copy. Verify
  eight ODT copies are byte-identical; inspect PDF pages 1, 9 and 10. New Markdown retains
  289 nonblank non-header source lines, with ten page locators and explicit source limits.
  Search/comparison and byte-copy receipts: ignored `output_2018_midterm_search/`.
- Lecture audit: extract 61 instructional 2025 PDFs (2,417 pages) and inspect 58 paired
  ODPs; inspect 40 maintained 2026 PDFs/39 ODPs, of which 34 PDFs (1,261 pages) are
  instructional after announcement/`xlect` exclusion. Check source locators, notes and
  decisive rendered pages. Keep full text/hash manifests in ignored `output_genetics_audit/`.
  Treat current source coverage separately from classroom delivery or BPQ runtime acceptance.
- Biochemistry conversion checks: four files, 38 page locators, one H1 each, balanced
  fences, ASCII, image-free content, valid source links and full extracted-text retention.
  Source PDF hashes verified. The book validator's filename convention is superseded by
  the instructor's requested lower snake_case artifact names. Evidence lives in ignored
  `output_biochemistry_markdown/`; this documentation-only change does not require pytest.
- Genetics audit verification: 141 PDF pages accounted for; 4,079 non-header extracted
  lines retained; source PDF hashes, local links, ASCII, headings, fences, and absence
  of embedded images checked. Inspect 27 rendered source pages. The book-to-markdown
  validator reports only its book-specific filename convention, intentionally superseded
  by this repository's exam Markdown naming. No generator execution or full pytest run;
  this task changes documentation only. Local evidence: output_genetics_audit/.
- Rotate the changelog after it exceeds 800 lines, preserving the newest two date blocks
  and moving older complete blocks to CHANGELOG-2026-10a.md.

- Paper geometry, typography, style loading, and matching checks: 14 passed. Render
  two-page Letter and A4 samples in LibreOffice; confirm PDF page dimensions and inspect
  title/name/score alignment, subsequent-page headers, and five-choice rows. Samples are
  in /private/tmp/exam_paper_review. The full genetics exam was not regenerated.

## 2026-10-12

### Additions and New Features

- Refine the genetics archive to complete representative exams, grouping alternate forms
  and revised exports by content. Retain six new representatives (2016 and 2017 midterms
  and finals, 2018 final, 2019 midterm), alongside the existing 2019 final and 2025 exams.
  Move 46 imported variants, supporting files, and incomplete exports outside ARTIFACTS
  to output_genetics_archive_review/set_aside; update source mappings. Exclude the
  2018 midterm because its export contains only 10 of the stated 11 pages.

- Archive all 52 byte-unique files from the 79 entries in genetics_exam.md5sum under
  ARTIFACTS for later consideration, including listed supporting materials. Verify source
  and destination MD5 checksums, preserve existing files, disambiguate filename collisions,
  and record every source-to-artifact mapping in ARTIFACTS/genetics_exam_sources.tsv.

- Audit the BBQ image loader's Bandit B310 finding: local-file access is intentional
  for trusted authored exam HTML in this closed pipeline. Document that boundary and
  suppress only this call-site finding; retain the repository security test.

- Restore the existing high-density PNG capture for canvas-only drawings, including RDKit.
  Keep SVG for tables and MathML; select format in the existing renderer without YAML or
  DOCX sizing changes. Recheck source resolution on the PNG capture page so a fixed-size
  canvas is not mistaken for newly recovered detail.
- Compare BP acetate and Henderson-Hasselbalch output against the previous PNG capture
  through DOCX and the existing LibreOffice export script at 600 DPI. RDKit PNG bytes
  are identical to the previous capture, preserving bond appearance and dimensions;
  table and equation output retain vectors. The 256-pixel source canvas remains a source
  detail limitation, explicitly reported rather than claimed as 600-DPI molecular detail.
  Real-generator quiz/exam checks and LibreOffice PDF review passed. Final pytest: 1,739
  passed, with the same unchanged Bandit B310 failure in ef_tools/bbq_media.py. Comparison
  artifacts: output_vector_quality/. Byte equality was an observation, not an acceptance gate.

- Prefer SVG for all HTML capture targets through Chromium PDF output and Poppler.
  Preserve glyph outlines, borders, and embedded raster content. If an SVG export fails,
  capture that element as a 600-DPI PNG and report the reason.
- Embed generated SVG directly in DOCX for LibreOffice, preserving the existing image
  field and sizing rules without PNG companions or additional YAML fields. Keep SVG
  extensions when extracting these images back out of DOCX.
- Verify one-table cropping and the DOCX-to-LibreOffice PDF round trip, then BP
  Henderson-Hasselbalch MathML, RDKit canvas output, mixed table/canvas content, both
  import routes, selective PNG recovery, and the real-generator quiz/exam workflow.
  Bound the print viewport to prevent hidden surrounding content from shrinking narrow captures.
  The final comparison PDF retains vector text/borders and only rasterizes the source canvases.
  One warm table capture measured 19,689-byte SVG in 0.105 s versus 19,222-byte PNG
  in 0.220 s; this is a single local observation, not a benchmark guarantee.
  Full pytest: 1,697 passed, one unchanged Bandit B310 finding in image URL loading;
  the same finding was reproduced from HEAD. The SVG implementation passed its
  focused tests and a direct medium/high Bandit scan.

- Add native Playwright HTML capture using complete question context for tables, MathML,
  and JavaScript canvases. Calculate capture resolution for at least 600 effective DPI
  at the existing DOCX image sizes, preserving physical scale and PNG density metadata.
  Multiline HTML/scripts are supported; only BBQ input retains its one-record-per-line format.
  Temporary Chromium checks verified HTML and BBQ through DOCX, source-order preservation,
  target-only canvas readiness, and missing-resource diagnostics. Captured DOCX images met
  600 effective DPI at their measured placement sizes. These one-time fixtures were removed;
  permanent tests retain content, answer-mapping, and media-density contracts.

- Add `assessment_styles/README.md` to define the folder's broader scope: documentation for
  creating, styling, planning, and making decisions about assessments, plus shared formatting YAML.
- Add the Genetics Exam 1 coverage selection and build recipe for Chapters 1-7, combining
  Quiz 1, Quiz 2, and the website genetics Tasks 1 scope. Prefer MATCH, medium difficulty,
  and full-pattern pedigrees; document overlapping variants in `docs/GENETICS_EXAM1.md`.
- Generate a provisional YAML, key, DOCX, and PDF in `output_genetics_exam1/` with
  ZipGrade A-E validation. Add an exam-specific DOCX formatter to keep each question's
  stem, images, and answer bank on one page when they fit.
- Add subject-independent `docs/EXAM_STYLE.md` and `docs/QUIZ_STYLE.md`. Keep the
  Genetics Exam 1 document focused on selection, coverage, and outstanding source banks.

### Behavior or Interface Changes

- Reduce Genetics Exam 1 genetic-disorders matching from four prompts to three at
  instructor request. The selection now has 54 blocks, 100 ZipGrade rows, and 70 raw
  points; retain all four shared-cross questions. Verify source counts.

- Use four consecutive unique_counts.py tasks for the same saved cross: each parent's
  gametes, offspring genotypes, and offspring phenotypes. The genetics builder creates
  parental scenario JSON once and reuses it on rebuilds. Keep all other selected tasks
  per instructor direction: the draft now has 54 blocks, 101 rows, and 70.5 raw points,
  pending the instructor's final cut. ZipGrade validation continues to enforce 100 rows.
  Verify the four CSV tasks through separate generator subprocesses with the same JSON.

- Set Genetics Exam 1 statement MC banks to five choices, retaining an explicit
  four-choice exception for nucleotide_components.yml. Five-choice generation yields
  no questions for that bank; all four other banks produce five-choice output. Verify
  20 generated items per bank at the selected count. The generator already defaults
  to five, so no generator change is needed. Exam rows and points are unchanged.

- Revise Genetics Exam 1 to 53 blocks and 100 answer rows (69.5 raw points): include
  both complementary-sequence forms and both end-type forms, request five blood-type
  agglutination choices, remove later-course progeny probability, and include two fly
  questions. Reduce unsplit meiosis matching to four prompts to retain both ABO questions
  and all 20 terms in the four five-prompt terminology blocks. Validate source counts;
  leave the instructor-deleted generated output folder absent.

- Use two disjoint five-term halves for each of the two 10-term genetics terminology
  banks. Use five prompts from the original meiosis_terms.yml without splitting it.
  Replace only the three affected matching blocks, regenerate their keys, and retain
  the other 46 questions: 51 blocks / 99 rows. Original homework banks remain intact.

- Opt both exam metabolic epistasis tasks into `--random`, preserving the generator's
  default even batch coverage. Existing generated questions and exam artifacts are unchanged.

- Audit all 73 Chapter 1-6 genetics homework catalog entries against exam coverage.
  Add the inverse epistasis ratio task and a second randomly selected metabolic pathway;
  retain one five-pedigree matching block. Preserve the original 47 questions and add two
  questions for 49 blocks / 86 rows. Withdraw historical-only expansion suggestions and
  document homework as the content boundary in the assessment-specific selection notes.
  Regenerate DOCX/PDF (20 pages); verify preserved questions, task/key counts, numbering,
  and ZipGrade compatibility. Generator checks: 404 focused tests pass; 70 single-question
  samples exercise all seven interaction ratios. Instructor owns final visual review.

- Standardize reference filenames as YEAR_subject_assessment with matching stems across
  PDF/DOCX/ODT; update references and save a checksum-verified rename manifest. Set aside
  redundant biochemistry exports with identical extracted content. Keep archive-specific
  curation guidance in assessment documentation rather than Human Guidance.

- Record the instructor's preference to keep point values out of assessment titles and
  headings in Human Guidance and shared assignment, exam, and quiz style documentation.

- Compare the generated Genetics Exam 1 with the archived 2025 genetics midterm,
  including short answers. Record coverage and sampling gaps plus a proposed 16-row
  expansion in assessment_styles/GENETICS_EXAM1.md. Distinguish the three biochemistry
  Exam 1 PDFs from the genetics source; leave exam questions and selections unchanged.

- Clarify the separate ZipGrade capacity criterion: at most 100 numbered answer rows,
  with one row per matching prompt or MC/MA question regardless of point weight.
  Document reporting both points and rows; the existing validator enforces capacity.

- Apply the instructor's scoring rule to all assignments, exams, and quizzes in all classes:
  matching prompts earn 0.5 point each; MC/MA questions earn one point each. Automatic DOCX
  score totals use these weights while numbering and explicit total_points overrides remain
  independent. Document the shared rule and update CLI help. Genetics Exam 1 totals 59.5
  points across 84 answer rows (49 matching prompts and 35 MC/MA questions).
  Full pytest: 1,741 passed. Re-render the saved questions and verify the PDF score line
  displays 59.5 points.

- Follow the instructor's removal of all Chapter 7 tasks from Genetics Exam 1. Rebuild
  Chapters 1-6: all 47 selected blocks, 84 numbered rows, zero skips, 19 PDF pages.
  Reconcile every task with the build trace, YAML, answer key, and PDF labels; confirm
  continuous numbering and Chapter 7 absence. ZipGrade validation passes.

- Request five consecutive choices for medium circular digestion in Genetics Exam 1.
  Retain medium difficulty after enumerating valid maps; document the fixed answer-set
  limitation of medium linear fragments under the five-choice constraint. Final rebuild:
  53 blocks, 93 rows, zero skips, 22 pages; ZipGrade passes and the circular page/key are checked.

- Request five choices for both linear digests and Punnett-square selection in Genetics Exam 1.
  Remove chi-square calculation/decision because it was not covered; update the coverage notes.
  Rebuild: 53 blocks, 93 rows, zero skips, 22 PDF pages. ZipGrade and 23 focused tests pass;
  visually review the changed pages and independently verify their keys.

- Remove direct QPM rendering requirements and molecular reconstruction from formatting.
  BP generator subprocesses retain their configured QPM path. Existing builders, question
  selection, ZipGrade rules, pagination, and PDF export settings are unchanged.
- Execute authored browser scripts for visual capture; required resources must be available.
  Report missing resources and insufficient source bitmap/canvas resolution without repairing
  source HTML or scientific content.

- Rename local selections to `genetics_quiz1.csv`, `genetics_quiz2.csv`,
  `genetics_exam1.csv`, and `biostats_quiz1.csv`. The two former Genetics Exam 1
  filenames held different selections: Quiz 1 (20 tasks) and Exam 1 (54 tasks).
- Retain the previously curated biochemistry selection as `biochem_exam1.csv`,
  following the instructor's clarification, and update its builder. Reference BPW directly
  for full source catalogs; retain local selections for individual assessments.
- Move the canonical YAML format reference to `assessment_styles/YAML_EXAM_FORMAT.md`
  and update documentation links and converter references.
- Follow concurrent CSV renames to `biochem_tasks-exam1.csv` and `genetics_tasks-exam1.csv`
  in the existing study-guide and Quiz 1 callers. Keep the separate 54-block Genetics Exam 1
  selection at `genetics_tasks_exam1.csv`.
- Place `GENETICS_EXAM1.md` in `assessment_styles/`, following the instructor's clarified
  destination. Keep its assessment-specific selection and coverage scope separate from the
  reusable exam and quiz conventions in the same folder.
- Separate dedicated assessment shell recipes into `builders/` and general converters,
  validators, and PDF export into `converters/`. Update build commands, test and maintainer
  import paths, bootstrap comments, and documentation. Preserve `ef_tools/` as shared
  implementation and the standalone `tools/` boundary without editing vendored checks.
- Consolidate reusable assessment styling in `assessment_styles/`: move the formatting YAML
  and exam/quiz guides there, and merge the DOCX reference into `EXAM_STYLE.md`. Update the
  loader, links, code references, and YAML ignore exception. Remove the empty `styles/`
  directory; keep `docs/GENETICS_EXAM1.md` for assessment-specific selection decisions.
- Move all five assessment task CSVs into `task_files/` using Git moves. Update dedicated
  shell recipes, usage examples, selection links, and the repository map. Keep general-purpose
  Python CLIs in `launchers/` and shared implementation in `ef_tools/`.
- Move course build scripts from the root into `launchers/` with descriptive
  `build_genetics_quiz1.sh`, `build_genetics_quiz2.sh`, `build_biostats_quiz1.sh`, and
  `build_biochem_exam1_study_guide.sh` names. Rename the biostatistics layout helper to
  `format_biostats_quiz1.py` and update its callers. Resolve the repository root through Git
  so the relocated shell commands can run from other directories.
- Replace recursive quiz/study-guide directory deletion with removal of only the generated
  DOCX after YAML generation succeeds. Preserve the existing quiz output locations.
- Record the instructor's Exam 1 overlap, MATCH, and five-choice requirements in human guidance.
- Simplify the five course build recipes to flat 12-17-line shell scripts run from the
  repository root. Consolidate LibreOffice export settings in `launchers/docx_to_pdf.sh`.
  This supersedes the root-discovery wrappers and assessment-specific formatters above.
- Remove both per-assessment Python formatters. The common DOCX builder now supports
  optional question grouping and section page breaks, applied at rendering boundaries.
  The existing task importer accepts `--points` and a CSV `layout` column, preserving
  the biostatistics quiz's score and one-choice-per-line statement questions.

### Decisions and Failures

- The provisional build produces 51 of 54 blocks, 91 numbered rows, and 21 PDF pages.
  Exam mode skips the linear fragment digest, six-choice Punnett-square selection, and
  six-choice chi-square calculation/decision selection. Source-side five-choice support
  is pending an instructor decision. The strand and circular digest banks also need that
  support for repeatable builds; their accepted candidates fit A-E in this run.
- Use four choices for the DNA statement banks after a five-choice nucleotide-components
  run produced no candidates. The four-gene unique-gamete bank already has five options
  and does not accept `--num-choices`.
- Keep configuration tied to demonstrated callers. Pagination uses two common CLI options;
  do not add parallel YAML settings. Extend the existing importer contract test for point
  totals and choice layout; keep the rendering-boundary check temporary.

### Developer Tests and Notes

- Native-renderer cleanup: 397 focused converter, DOCX, import, typing, lint, and
  documentation checks passed; the final HTML-media regression check passed all 20
  HTML-importer tests. Browser/DOCX acceptance checks were temporary, not added to CI.
- Pass 256 focused converter, import-boundary, and documentation checks after splitting
  entry points. All seven Python converter CLIs load with `--help`; shell syntax passes.
  The existing checker permits converter-to-`ef_tools` imports and rejects the same import
  from `tools/`, without vendored modifications or exclusions.
- Complete isolated Genetics Exam 1 and biostatistics Quiz 1 builds through PDF export.
  Re-render saved questions through the relocated converter and confirm equivalent exam
  and quiz DOCX content. The fresh random exam build has 88 rows and six rejected tasks;
  the quiz has 17 rows with no skipped tasks. These are workflow checks, not full exam
  coverage approval. Retain evidence in `output_reorganization/` and remove temporary scripts.
- Pass 67 existing style-loader, DOCX formatting, matching, and Markdown-link checks after
  consolidating `assessment_styles/`. Formatting values are unchanged; no new tests or
  configuration switches were added.
- Validate the task-file relocation: all 146 tasks across the five CSVs resolve their
  generators and YAML inputs. Pass 63 focused importer, pipeline, Markdown-link, and shell
  checks plus Bash syntax checks. No new tests or regenerated assessment outputs are needed
  for the path-only change.
- Pass 247 focused task-pipeline, ZipGrade, matching-rendering, script-budget, Markdown-link,
  and executable-file checks. Shell syntax and formatter pyflakes checks pass; the relocated
  biostatistics formatter runs on copies of both current quiz artifacts.
- Inspect all 21 rendered draft pages after the pagination adjustment. This verifies draft
  rendering and A-E compatibility, not complete coverage or a fresh full pytest suite.
- Pass 293 final executable-file, Markdown-link, guidance-format, and function-typing checks.
  Verify all 91 key numbers are consecutive and all key letters are A-E. Remove the temporary
  candidate inventory and contact-sheet scripts after retaining their output as draft evidence.
- Verify the shared-tool refactor with 56 focused task-import, ZipGrade, matching, and DOCX
  tests plus a temporary pagination check. Shell syntax, lint, documentation links, and
  repository checks pass. Remove temporary verification scripts after retaining their results.
- The earlier generated draft directories were absent when refactor verification started.
  Compare old and new formatting using the same fresh exam and quiz inputs in
  `output_style_review/`; preserve all existing reference DOCX/PDF files by checksum.
  Review the 21-page exam and two-page quiz: DOCX content and extracted PDF text match.
  The quiz pages also match exactly; two exam pages show font/rendering differences, and
  a repeated export of the unchanged baseline also varies. Treat equality as diagnostic
  evidence, not an acceptance requirement. No fresh full pytest suite was run.
