# Roadmap

This roadmap records the current printable-assessment workflow and evidence-backed verification
work. Supported commands live in [USAGE.md](USAGE.md); known failure symptoms and remedies live
in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Current capabilities

- Converters accept task CSV, BBQ text, DOCX, Blackboard HTML, and Oklahoma sources through one
  ordered exam-YAML contract; assessment-specific recipes live in `builders/`.
- Exam, quiz, and handout modes preserve visual content and image-capable matching prompts.
  Handout mode adds printable NUM, FIB, and FIB_PLUS answer blanks.
- The renderer prefers SVG for supported visuals and keeps PNG for canvas captures or SVG export
  failures. Drawing scale remains independent of raster capture resolution.
- Named styles own reusable DOCX layout. Text-choice selection measures formatted answers
  against tab geometry; see [CHOICE_FORMATTING.md](CHOICE_FORMATTING.md).
- LibreOffice opens the generated DOCX for instructor editing and exports PDF without an ODT
  processing stage. Specialized composition builders can retain scientific setup snapshots.

## Verification priorities

- Keep generated content fixed when comparing formatting changes. Use a varied, fixed assessment
  for layout review, including both text-heavy and image-heavy questions.
- Investigate demonstrated bad choice rows using their font, paper size, layout override, and
  exact YAML before changing the width algorithm. Avoid speculative layout machinery.
- Run focused behavior checks after code edits and the repository pytest lane before closeout.
  Use real-generator E2E checks when changing the task-generation boundary.
- Inspect the LibreOffice-exported PDF for visual changes. Font metrics and DOCX geometry checks
  do not establish final wrapping or page layout on their own.
- Retain manual post-render page polishing; automatic page fitting is not a current objective.

## Scope boundaries

- Keep the inspectable YAML handoff; there is no planned direct HTML-to-DOCX shortcut.
- Add an ODT modification step only if a concrete LibreOffice compatibility problem requires it.
- Preserve explicit instructor layout/font choices and the tab-based editing interface.
- Keep content-generation changes in their owning sibling repository. Do not silently remove
  distractors to make a question fit ZipGrade.
