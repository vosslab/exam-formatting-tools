# Changelog

## 2026-05-07

### Additions and New Features

- Added ZipGrade compatibility tooling. `ef_tools/zip_grade.py` is a single shared validator that classifies every question as `OK`, `FIXABLE`, or `ERROR` against the ZipGrade 100-question bubble form (A-E only, up to 100 rows). Both `FIXABLE` and `ERROR` are non-OK: a 6-choice MC is `FIXABLE` because one distractor could be dropped, but tooling refuses to pick which (the YAML schema has no answer key per `docs/YAML_EXAM_FORMAT.md` lines 339-348), so nothing is rewritten silently. New `validate_zip_grade_yaml.py` repo-root script reports offenders with `<path>:<line> [SEVERITY] (Qn) <message>` line-anchored output (line numbers are the stable identifier; Q-numbers are dynamic and shown as parenthetical hints) via a `LineTrackingLoader` that subclasses `yaml.SafeLoader` to attach 1-based source lines to every mapping. With `-o`, the linter writes a filtered YAML containing only OK questions; without `-o`, it raises `ValueError` if any non-OK issue exists. New `--zip-grade` / `-z` flag on `yaml_to_exam_docx.py` builds a DOCX from only the OK subset, prints the same line-anchored removal report, and warns to stderr (but still builds) when the post-filter row total exceeds 100. Locked in `tests/test_zip_grade.py` (21 tests covering the full severity matrix, the `filter_exam` deep-copy and `__line__` strip contract, the loader, and the report formatter).
- Added `ef_tools/cli_checks.py` with two helpers: `require_extensions(path, allowed, role)` raises `ValueError` when a CLI input/output path has the wrong extension, and `default_output_path(input_path, new_ext)` derives an output basename in the current working directory by swapping the extension. Both helpers are wired into every root script so a wrong-format input fails loudly at startup instead of silently producing a near-empty file (the bug behind yesterday's confusion when `html_exam_docx_builder.py` was given a `.yml` input and wrote only the front page).
- Added `ef_tools/html_parse.py` containing the shared HTML parsing constants (`TAKE_QUESTION_XPATH`, `IMAGE_CLASS_XPATH`, `INLINE_TAGS`, `QUESTION_CODE_RE`, `CHOICE_PREFIX_RE`) and helpers (`extract_document_title`, `is_question_code`, `strip_choice_prefix`, `resolve_image_path`, `text_from_element`, `has_choice_labels`) extracted from the now-deleted `html_exam_docx_builder.py`. Consumed by `html_to_exam_yaml.py`.

### Behavior or Interface Changes

- Renamed `docx_exam_builder.py` to `yaml_to_exam_docx.py` (via `git mv`) so every root script reads as `<input-format>_to_exam_<output-format>.py` and the input/output direction is unambiguous at `ls`. Updated all references in `tools/measure_image_choices.py`, `tests/test_docx_choice_styles.py`, `tests/test_yaml_to_exam_docx_matching.py` (renamed from `test_docx_exam_builder_matching.py`), `README.md`, `docs/USAGE.md`, and `docs/YAML_EXAM_FORMAT.md`.
- All five root scripts (`bbq_to_exam_yaml.py`, `docx_to_exam_yaml.py`, `html_to_exam_yaml.py`, `okla_to_exam_yaml.py`, `yaml_to_exam_docx.py`) now make `-o/--output` optional. When omitted, output defaults to `<input-stem>` with the target extension in the current working directory (for `html_to_exam_yaml.py`, the first input's stem). Final CLI line is standardized to `Exam YAML written to <path> (NN questions)` or `Exam DOCX written to <path> (NN questions)`.
- All five root scripts now validate input and output extensions via `ef_tools.cli_checks.require_extensions` before doing any work. Allowed extensions: `bbq_to_exam_yaml.py` `.txt -> .yml/.yaml`; `docx_to_exam_yaml.py` `.docx -> .yml/.yaml`; `html_to_exam_yaml.py` `.html/.htm -> .yml/.yaml` (each input file is checked); `okla_to_exam_yaml.py` `.txt -> .yml/.yaml`; `yaml_to_exam_docx.py` `.yml/.yaml -> .docx`.

### Removals and Deprecations

- Deleted `html_exam_docx_builder.py` (and its test `tests/test_html_exam_docx_builder.py`). The HTML-to-DOCX direct path duplicated work already covered by `html_to_exam_yaml.py` followed by `yaml_to_exam_docx.py` and was the source of yesterday's silent-empty-DOCX bug when fed a YAML file. Anyone wanting HTML to DOCX now runs the two-step pipeline. Also removed the `test_add_choice_label_paragraph_routes_image_choices_through_tabbed` test in `tests/test_docx_builder_image_choices.py` (the only remaining caller of `html_exam_docx_builder.add_choice_label_paragraph`).

### Fixes and Maintenance

- Restored `Question Heading` and `Question Follow` styles to match the legacy ODT/DOCX artifacts in `ARTIFACTS/`. `Question Heading` is now bold italic at 11pt with hanging indent 0.2 in / -0.2 in, space-before 0.12 in, space-after 0.05 in; `Question Follow` now inherits from `Question Heading` and only overrides `space_before=0`, mirroring the artifact's `<w:basedOn w:val="QuestionHeading"/>` plus single-property override pattern. Verified against `ARTIFACTS/exam1.docx` (`<w:b/><w:i/><w:sz w:val="22"/>` and `<w:ind w:hanging="288" w:start="288"/>`). Updated `styles/exam_styles.yaml` (`sizes.question: 11`, `style_flags.question_bold/italic: true`, `spacing.question_indent: 0.2`, `question_hanging: -0.2`, `question_heading_space_before: 0.12`, `question_space_after: 0.05`) and refactored `Question Follow` setup in `ef_tools/docx_builder.py` to base on `Question Heading` instead of `Normal`. `Matching Prompt` keeps its existing explicit `bold=False/italic=False` overrides, so it still renders normal weight/style and now correctly inherits the new 11pt size from its parent (matching the artifact, where `Question` style inherits size from `QuestionHeading`).
- `html_to_exam_yaml.py` now registers a custom string representer that emits double-quoted YAML scalars for any string containing an apostrophe, instead of single-quoted with the `''` escape. The doubled-apostrophe form is valid YAML 1.1/1.2 and round-trips correctly through `yaml.safe_load`, but some lenient/legacy YAML validators flag `Chargaff''s` and `it''s` as syntax errors. Switching to double-quoted style produces `"Chargaff's"` literally, which every validator accepts. Strings without apostrophes keep PyYAML's default plain style, so the diff is limited to lines that previously carried `''`.

## 2026-05-06

### Additions and New Features

- Added `tools/measure_image_choices.py`, a repeatable measurement rig for image-choice column sizing. Generates noise PNGs, builds a one-question-per-col-count exam through the production pipeline (`docx_exam_builder.build_document`), converts each page to PNG via LibreOffice + ImageMagick, and prints a per-cols table comparing each rendered image's right edge to its target tab stop so future `IMAGE_CHOICE_MAX_WIDTH_BY_COLS`, `layout_tab_stops`, and `choice_indent` changes can be tuned without ad-hoc scratch scripts. Runs with `source source_me.sh && python3 tools/measure_image_choices.py`; output lands in `/tmp/image_choice_measure/` for inspection.
- Added `ef_tools/rdkit_render.py` to render RDKit HTML5 canvas widgets to PNG by extracting the inline `let smiles="..."` literal and re-drawing through `rdkit.Chem.Draw.MolToFile`. PNG filenames are derived from the source canvas id (e.g. `rdkit_canvas_3071.png`) so reruns overwrite stably.
- Wired `html_to_exam_yaml.py` to the new RDKit renderer so canvas widgets that the parser previously dropped silently now produce PNG files in the existing Blackboard `*_files/` directory and emit standard `images:` (and structured choice `image:`) references in the YAML. No YAML schema change.
- Added `html_to_exam_yaml.py` to convert cleaned Blackboard HTML exports into the repo's canonical exam YAML format while preserving statement images and image-based answer choices.
- Added `html_exam_docx_builder.py` to generate one styled DOCX exam directly from cleaned Blackboard HTML exports while preserving question text, matching blocks, statement images, and image-based answer choices.
- Extended the DOCX builder to render YAML `images` lists and structured choice objects with image paths.
- Updated HTML-to-YAML conversion so block breaks become plain YAML newlines rather than literal `<br/>` text, matching questions keep the original prompt/term list style, and compact chemistry notation preserves subscript/superscript spacing without removing prose spaces.
- Updated DOCX rich text rendering to turn YAML newlines and legacy `<br>` tags into Word line breaks.
- Updated DOCX image-choice rendering so graph/image answer options are laid out horizontally in a choice table when they fit on the page.

### Behavior or Interface Changes

- Refactored `parse_question` in `html_to_exam_yaml.py` to extract statements subtractively: the question body is deep-copied, choice/matching/noise subtrees are pruned from the copy, then `element_to_inline_html` is called once on what remains. Replaces the previous per-child loop that silently dropped `child.tail` text and stripped inline tag wrappers. Fixes truncated statements where the prose continued after an inline element (for example `The <b>y-intercept</b> of a Lineweaver-Burk plot is:` previously emitted only `'The y-intercept'`, and `If K&#8242;<sub>eq</sub> = 1, ...` previously emitted only `'If K&#8242;eq'`). Added module-level helpers `remove_node`, `remove_statement_noise`, `remove_choice_blocks` (leaf-only, never deletes ancestor `<div>`s), `remove_empty_blocks` (optional), and `remove_matching_blocks`.
- Tightened `MATCHING_PROMPT_MARKER_XPATH` in `html_to_exam_yaml.py` to require `contains(@style, 'border')` and `not(normalize-space(.))` in addition to `contains(@style, 'display:inline-block')`. Prevents hint legends styled with `display:inline-block` on bold terms from being misclassified as Blackboard matching prompt markers (which would dump bold terms into `prompts_list` and leave the question statement empty).
- Cleaned Blackboard `<canvas class="cleaned-statement-media">` widgets paired with an inline `initRDKitModule()` script no longer disappear during HTML-to-YAML conversion: the SMILES is extracted, rendered through RDKit (no headless browser), and saved as `rdkit_<canvas_id>.png` next to the existing `*_files/` content. Malformed SMILES or missing literals now raise instead of silently dropping the widget.
- Replaced the image-choice docx table layout with inline images positioned by paragraph tab stops; no docx tables are emitted for answer choices. Renamed `add_image_choices_table` to `add_image_choices_tabbed` in `ef_tools/docx_builder.py`; both YAML and HTML builders pass through the same tab-stop helper.
- Added `matching_terms` support so matching prompts can span question-number ranges like `Q5-8.` and each matching term consumes its own numbered blank.
- Reordered matching-question DOCX rendering to put lettered `choices_list` BEFORE the numbered `prompts_list` blanks, matching the reference exam style in `ARTIFACTS/`. Added `test_matching_renders_choices_before_prompts` to lock the order; updated `docs/YAML_EXAM_FORMAT.md` matching example accordingly.
- Added a `Matching Prompt` paragraph style in `ef_tools/docx_builder.py` modeled on the legacy `Question` style from `ARTIFACTS/2019_exam2-final.docx` (verified via the LibreOffice style dialog): inherits from `Question Heading`, turns off bold and italic, `left_indent=0.2"` with `first_line_indent=-0.2"` (hanging), `space_before=0.07"`, `space_after=0`, `line_spacing=1.25`, `keep_with_next=False`, two left tab stops at `0.5"` and `3.5"` for two-column prompt layout. Switched matching `prompts_list` paragraphs to this style instead of generic `Choice`. `choices_list` continues to render via `add_choices_paragraph` using `Choices 2/3/4/5`.
- Replaced `matching_terms` with bptools-style `prompts_list` + `choices_list` for matching questions (mirrors `MATCH(question_text, prompts_list, choices_list)` in `qti_package_maker/assessment_items/item_types.py`). `html_to_exam_yaml.py` now extracts the lettered (A./B./...) options into `choices_list` (with prefixes stripped) and the bond/term items into `prompts_list`; the lead-in prose stays in `statement` instead of carrying an inline `A. ... B. ...` enumeration. `docx_exam_builder.py` renders `choices_list` through the standard MC auto-layout so matching options look identical to MC choices. The legacy `matching_terms` field is no longer read or emitted.
- Added `styles/exam_styles.yaml`, the style configuration expected by the DOCX builders.
- Added tests for HTML exam builder and HTML-to-YAML helper functions.

### Fixes and Maintenance

- Reworked DOCX image-choice layout in `ef_tools/docx_builder.py:add_image_choices_tabbed`. Letter prefix and image now render on the SAME line per column in a single combined paragraph (`(A)<img> \t (B)<img> \t ...`); when at least one choice carries non-trivial alt text, a second paragraph below holds the alt-text row (suppressed when every alt is empty or the literal placeholder `image`). Image widths are clamped per column count via `IMAGE_CHOICE_MAX_WIDTH_BY_COLS = {2: 3.30, 3: 2.07, 4: 1.49, 5: 1.13}` (in inches), empirically tuned via `tools/measure_image_choices.py` to leave ~0.02" of dead space between an image's right edge and the next tab stop (was ~0.18-0.44" of dead space). The styles ceiling `choice_image_max_width` was raised from 3.00 to 3.40 so the per-col dict (not the global) is the binding constraint. New `fit_picture_kwargs(image_path, max_width, max_height)` reads source PNG dimensions via `PIL.Image` and chooses `add_picture(width=...)` or `(height=...)` based on which scale factor binds, preserving aspect ratio. New `_row_image_height()` walks every image in the row and returns the smallest rendered height so all images render at one shared height. New `_zero_inline_image_margins()` sets `distT/distB/distL/distR=0` on each `<wp:inline>` so images hug their run instead of carrying the default ~0.125" padding. Tab stops in `styles/exam_styles.yaml -> layout_tab_stops` are pre-offset by `choice_indent` (0.13") so OOXML's "tab stops measured from page left margin, not from indent" rule does not produce an uneven first column gap; `choice_indent` itself dropped from 0.28 to 0.13 so all `Choices N` rows (image and text) share the same modest indent.
- Fixed `docx_exam_builder.py` to render inline `- chapter: "..."` entries that appear inside a section's `questions:` list. Previously the builder only honored `chapter` at the section level, so YAML files that interleaved chapter markers between questions had every chapter silently dropped (each was parsed as an empty question and skipped). The question loop now detects entries that carry `chapter` without a `statement`, emits a `Chapter Heading` paragraph, sets `prev_element = 'chapter'`, and `continue`s without advancing the question counter. Regenerated `Final_Exam/final_exam_combined.docx` from `Final_Exam/final_exam_combined.yml` and verified all 14 chapter headings (Chapter 1 Life Molecules through Chapter 14 Senses) now appear.
- Fixed `ef_tools/layout.py:auto_layout_for_choices()` to score each YAML choice by its DOCX-visible width (`ef_tools.text_utils.choice_visible_width`) instead of the raw serialized YAML/HTML-entity length. Chemistry-style matching `choices_list` items containing entities like `&#8226;` (bullet) and `&#8801;` (triple bond) used to inflate the measured length by 7-9 raw characters per entity, pushing the algorithm past the `max_chars_4=23` and `max_chars_2=49` width budgets and collapsing to a single-column vertical stack on the bare `Choice` base style.
- Removed every paragraph assignment of the abstract base style `'Choice'` in `ef_tools/docx_builder.py`: the `has_images` override in `add_choices_paragraph` (lines 441-445) and the hardcoded assignment in `add_image_choices_tabbed` (line 392) both now route through the new `ef_tools.layout.choices_style_name(tab_style)` helper, which always returns one of `Choices 2/3/4/5`. `CHOICES_STYLE_NAME[1]` was retargeted from `'Choice'` to `'Choices 2'` so even the vertical-stack layout lands on a concrete child style. The `Choice` base style remains registered in `setup_styles` as the parent of `Choices 2..5`; it is never applied to a paragraph.
- Resolved statement truncation in HTML-to-YAML conversion: the Lineweaver-Burk question (`Final_Exam/Cleaned_Final_Exam_2A.html:3485-3552`) and the K'eq question (same file) now render full statements with inline `<b>`/`<i>`/`<sub>` wrapping intact in the regenerated `Final_Exam/Final_Exam_2A_2B_combined.yaml`. Test fixture in `tests/test_html_to_exam_yaml.py::test_parse_matching_block_emits_prompts_and_choices_lists` updated to use the realistic bordered empty-marker styling so it passes against the tightened `MATCHING_PROMPT_MARKER_XPATH`.
- Added `rdkit` to `pip_requirements.txt` (used by `ef_tools/rdkit_render.py`).
- Rewrote `README.md` to reflect the DOCX pipeline (the previous version still pointed at long-removed `odt_exam_builder.py`/`extract_odt_styles.py`/`propagate_odt_styles.py` scripts and `docs/ODT_EXAM_STYLES.md`).
- Added `docs/INSTALL.md` and `docs/USAGE.md` so the README can stay short and link out for setup and command-line examples.
- Fixed stale ODT references in `docs/YAML_EXAM_FORMAT.md` (header sentence and Images subsection now name the DOCX builders).
- Extracted `resolve_choice_layout()` helper in `docx_exam_builder.py` so MC `choices` and matching `choices_list` share one auto-layout/override path.

### Removals and Deprecations

- Removed legacy `matching_terms` field from the exam YAML schema. `docx_exam_builder.py` now raises `ValueError` if a question carries `matching_terms`, pointing authors at `prompts_list`/`choices_list` and the format spec.

### Decisions and Failures

- Reaffirmed layout policy in `docs/YAML_EXAM_FORMAT.md`: answer choices (MC `choices` and matching `choices_list`, text-only and image-based) are always laid out as inline runs with paragraph tab stops, never as docx tables. Question-level `table` data tables are unaffected.

### Developer Tests and Notes

- Added 7 image-choice regression tests in `tests/test_docx_builder_image_choices.py`: `test_image_choice_max_width_per_cols_clamps_5col` (per-col cap clamps an oversize request), `test_image_choice_max_width_per_cols_4col_differs_from_5col` (caps strictly decrease with column count), `test_zero_inline_image_margins_sets_dist_attrs_to_zero` (every emitted `<wp:inline>` has `distT/distB/distL/distR="0"`), `test_alt_text_paragraph_skipped_for_placeholder_image_text` (placeholder `text: image` does not emit an alt-text row), `test_alt_text_paragraph_emitted_for_meaningful_alt_text` (real captions DO emit and contain the captions), `test_fit_picture_kwargs_picks_height_when_height_binds` and `_picks_width_when_width_binds` (bounding-box scaler), `test_row_image_height_picks_smallest_binding_height` (mixed-aspect row renders at uniform height). Initial sizing was driven by an underscore-prefixed scratch rig (`_render_loop.sh`, `_measure.py`) plus `Final_Exam/_image_choice_test.yml`; that scratch rig was deleted once the per-col caps stabilized and replaced with the committed `tools/measure_image_choices.py` (see Additions above).
- Added `tests/test_docx_choice_styles.py` (7 tests) locking the invariant that no rendered choice paragraph carries the abstract base style `'Choice'`. Five focused unit cases (text-only, single-column formerly bare `Choice`, mixed text/image, all-image, base-style inheritance edge) plus two end-to-end tests via `docx_exam_builder.build_document`: `test_matching_choices_list_uses_multi_column_style` (matching render path) and `test_combined_yaml_no_paragraph_uses_choice_base_style` (full `Final_Exam/Final_Exam_2A_2B_combined.yaml` rebuild walks every paragraph and asserts none use `Choice`). The end-to-end tests directly lock Gate G4 from the implementation plan.
- Annotated `choice_visible_text` and `choice_visible_width` parameter types as `str | dict` for full signature typing.
- Collapsed redundant `(3, 3)` branches in the 5+ choices arm of `auto_layout_for_choices` (`max_chars_3` and `max_chars_2` arms produced identical results, so the bound was widened to `max_chars_2` directly).
- Refreshed `docs/YAML_EXAM_FORMAT.md` "Auto-layout algorithm" section: renamed "Max chars per choice" to "Max visible width", added prose on entity decoding and inline-tag stripping, fixed style-name spacing (`Choices 5` not `Choices5`), and documented the `Choices 2` fallback for the single-column case.
- Documented the `/tmp/` write-then-`cp` regeneration flow for `docx_exam_builder.py` in `docs/USAGE.md` (the script refuses to overwrite an existing output file).
- Extended `tests/test_text_utils.py` with `test_choice_visible_text_decodes_entities`, `test_choice_visible_text_strips_supported_inline_tags`, `test_choice_visible_text_image_only_dict_returns_empty`, `test_choice_visible_width_relationships`, and `test_choice_visible_width_image_only_choice_is_zero` covering the new visible-text/visible-width helpers.
- Extended `tests/test_layout.py` with `test_chemistry_matching_choices_use_multi_column` (real 4-item list from `Final_Exam/final_exam_combined.yml` resolves to multi-column with explicit `layout_limits`), `test_short_chemistry_choices_use_four_columns` (short `H<sub>2</sub>O`/`CO<sub>2</sub>`/`C &#8226; C`/`C &#8801; C` reach `(4, 4)`), and `test_choices_style_name_never_returns_choice`. Recalibrated the existing anti-orphan tests for the new width-based scoring (`"a" * 30` for 4-medium, `"a" * 65` for very-long, `"a" * 23` for 5-medium) so they still exercise the orphan-avoidance branches.
- Regenerated `Final_Exam/Final_Exam_2A_2B_combined.docx` from the existing combined YAML using the fixed builder; verified by paragraph-style audit: 31 `Choices 2`, 13 `Choices 3`, 12 `Choices 4`, 37 `Choices 5`, zero `Choice`. Used the write-then-`cp` flow (`/tmp/_regen_combined.docx` then `cp`) because `docx_exam_builder.py` rejects an existing output path.
- Ran focused tests: `source source_me.sh && python3 -m pytest tests/test_text_utils.py tests/test_layout.py tests/test_docx_choice_styles.py tests/test_docx_exam_builder_matching.py tests/test_docx_builder_image_choices.py tests/test_html_exam_docx_builder.py tests/test_html_to_exam_yaml.py -q` (67 passed) and full repo `pytest tests/ -q` (353 passed) plus `tests/test_bandit_security.py`, `tests/test_pyflakes_code_lint.py`, `tests/test_ascii_compliance.py`, `tests/test_import_requirements.py`.
- Added five regression tests in `tests/test_html_to_exam_yaml.py`: `test_parse_question_preserves_text_after_inline_bold` (Lineweaver-Burk shape), `test_parse_question_preserves_text_after_inline_italic_sub` (K'eq shape), `test_is_matching_block_rejects_styled_hint_legend` (negative case for tightened XPath), `test_real_matching_question_still_yields_lists` (positive case using realistic bordered empty marker), and `test_parse_question_preserves_statement_image` (deep-copy + prune does not drop statement-body images). Full file: 21 passed in 0.24s via `source source_me.sh && python3 -m pytest tests/test_html_to_exam_yaml.py -q`.
- Re-regenerated `Final_Exam/Final_Exam_2A_2B_combined.yaml` and `Final_Exam/Final_Exam_2A_2B_combined.docx` from `Cleaned_Final_Exam_2A.html` and `Cleaned_Final_Exam_2B.html` after the subtractive `parse_question` refactor (98 source items: 48 from 2A and 50 from 2B). Image-reference count unchanged at 48 vs the previous `final_exam_combined.yml`; both RDKit canvas PNGs (adenine and lysine-phenylalanine dipeptide) still ride through. Used the write-then-replace flow (`/tmp/_exam_regen.{yaml,docx}` then `cp`) because `html_to_exam_yaml.py:414` raises `FileExistsError` on existing outputs.
- Regenerated `Final_Exam/Final_Exam_2A_2B_combined.yaml` and `Final_Exam/Final_Exam_2A_2B_combined.docx` from `Cleaned_Final_Exam_2A.html` and `Cleaned_Final_Exam_2B.html` after the matching schema switch; matching items now have explicit `prompts_list` (bond/term names) and `choices_list` (formula options with leading `A.`/`B.`/`C.`/`D.` stripped).
- Verified the combined YAML contains 98 source items (48 from 2A and 50 from 2B), 125 numbered question slots after matching spans, 9 matching prompts, 46 image references, 38 structured image choices, no missing image files, and no empty question statements.
- Verified the regenerated YAML contains no literal `<br/>`, `&lt;br`, `</sub>and`, or `</sub>values` artifacts.
- Ran focused tests: `source source_me.sh && python3 -m pytest tests/test_html_to_exam_yaml.py tests/test_text_utils.py tests/test_html_exam_docx_builder.py tests/test_docx_builder_image_choices.py tests/test_layout.py -q`, `source source_me.sh && FAST_REPO_HYGIENE=1 python3 -m pytest tests/test_pyflakes_code_lint.py -q`, and `source source_me.sh && FAST_REPO_HYGIENE=1 python3 -m pytest tests/test_import_requirements.py -q`.
- Added unit tests in `tests/test_rdkit_render.py` and an end-to-end fixture test in `tests/test_html_to_exam_yaml.py::test_parse_question_renders_rdkit_canvas_to_png` covering SMILES extraction (including charged brackets and stereochemistry), PNG output, and the full HTML-to-YAML path. Added helper-coverage tests for `compute_rdkit_out_dir`, `find_rdkit_script_for_canvas`, and the canvas-without-script `ValueError` path. Re-ran the focused suite plus full-scope `tests/test_pyflakes_code_lint.py`, `tests/test_import_requirements.py`, `tests/test_ascii_compliance.py`, and `tests/test_bandit_security.py`.
- Re-regenerated `Final_Exam/Final_Exam_2A_2B_combined.{yaml,docx}` after wiring the RDKit renderer; two new `Final_Exam/Final_Exam_2A_files/rdkit_*.png` files (adenine and the lysine-phenylalanine dipeptide) now ride through the standard `images:` list.

## 2026-04-02

### Additions and New Features

- Created `ef_tools/docx_builder.py` -- moved all DOCX rendering helpers out of `docx_exam_builder.py`: style setup, font fallback XML, hex color parsing, rich text runs, choice paragraph layout, table building, page header configuration, and page number fields.
- Added `style_flags` section to `styles/exam_styles.yaml` -- bold, italic, centered flags for Heading 1, Question, Chapter Heading, Heading 2, and table headers are now YAML-configurable instead of hardcoded.
- Added `colors.heading_1`, `page.image_max_width`, `layout_tab_stops`, `fonts.header_primary`/`header_fallback`, and `spacing.header_space_after_pt` to `styles/exam_styles.yaml`.
- Page header now uses Liberation Sans Narrow / Arial Narrow at 8pt with a small gap before content.

### Behavior or Interface Changes

- `docx_exam_builder.py` reduced from ~550 lines to ~180 lines; all DOCX rendering delegated to `ef_tools/docx_builder.py`.
- `ef_tools/layout.py` `auto_layout_for_choices()` now accepts an optional `layout_limits` dict parameter to load character limits from YAML instead of using hardcoded defaults.
- Choice tab stop positions now loaded from `layout_tab_stops` in YAML rather than hardcoded in `layout.py`.

### Fixes and Maintenance

- Fixed crash: `setup_styles()` tried to create a new 'Header' style but python-docx already has a built-in one. Now modifies the existing 'Header' style in place.
- Fixed inconsistent top margins between first and body pages by setting a fixed `header_distance` (0.5in) on the section, configurable via `page.header_distance` in YAML.

- Created `ef_tools/` package with shared exam formatting modules:
  - `ef_tools/text_utils.py` -- HTML entity decoding, number prefix stripping, rich text parsing for `<sub>`, `<sup>`, `<b>`, `<strong>`, `<i>`, `<em>` tags.
  - `ef_tools/layout.py` -- auto-layout algorithm for multiple choice column formatting, tab stop positions, style name mapping.
  - `ef_tools/question_utils.py` -- question style selection and total question counting.
  - `ef_tools/style_loader.py` -- loads style definitions from `styles/exam_styles.yaml`.
- Created `styles/exam_styles.yaml` -- externalized all hardcoded style values (fonts, sizes, colors, spacing, tab stops, layout limits) from `docx_exam_builder.py`. Style tweaks can now be made in YAML without editing Python.
- Added rich text rendering to DOCX builder: `<sub>`, `<sup>`, `<b>`, `<strong>`, `<i>`, `<em>` tags in question statements, choices, headings, and table cells now render with proper font formatting (subscript, superscript, bold, italic).

### Behavior or Interface Changes

- Moved `exam_defaults.py` into `ef_tools/exam_defaults.py` (via `git mv`). All imports updated.
- Removed first-line indent from choice paragraphs (was -0.05in hanging indent, now 0).
- `docx_exam_builder.py` now loads styles from `styles/exam_styles.yaml` at runtime instead of hardcoding values.
- Utility functions (`decode_html_entities`, `strip_number_prefix`, `auto_layout_for_choices`, `select_question_style`, `count_total_questions`) extracted from builder into `ef_tools/` modules.

### Fixes and Maintenance

- Added `docx_exam_builder.py` -- new DOCX output engine using python-docx. Same YAML input format as `odt_exam_builder.py`, ~300 lines vs ~750 for ODT. Features: auto-numbering, auto-layout with orphan-row avoidance, bold (A) choice prefixes, Question Heading/Follow auto-selection, Chapter Heading (purple), Heading 2 (bold italic), images with aspect ratio, tables, first page boilerplate, page headers with student name, HTML entity decoding, overwrite protection, and .docx extension enforcement.
- Added `exam_defaults.py` -- default boilerplate text (name line, score line format).
- Added `bbq_to_exam_yaml.py` -- imports bbq_text format to exam YAML (MC, MA, MAT, ORD).
- Added `okla_to_exam_yaml.py` -- imports okla_chrst_bqge format to exam YAML (MC, MA).
- Created `docs/YAML_EXAM_FORMAT.md` -- complete format spec with qti-package-maker compatibility section.

### Behavior or Interface Changes

- YAML format redesigned: `chapter` for chapter headings, `heading` for major section labels (Heading 2), `statement` for question stems, `choices` as plain list (builder generates bold (A) prefixes).
- Auto-layout engine avoids orphan rows: 4 long choices use 2+2 (not 3+1), 5 medium choices use 3+2 (not 4+1).
- Removed `_20_` encoding from all generated ODT style names; plain spaces used directly.
- Question Heading vs Question Follow auto-selected based on preceding element type.
- Images preserve original aspect ratio using PIL dimensions.
- HTML entities in YAML (`&Delta;`, `&alpha;`) decoded to Unicode in output.
- Builder strips existing number prefixes before re-numbering (`22)` -> `22.`).
- First page has no header; body pages show "Page X of Y | date | First Name:___".
- All page margins unified at 0.6in.
- `python-docx` and `pillow` added to `pip_requirements.txt`.
- `conftest.py` updated so `pytest tests/` works without `source source_me.sh`.

### Fixes and Maintenance

- Fixed pre-existing pyflakes unused import warnings in `odt_utils.py`, `extract_odt_styles.py`, `propagate_odt_styles.py`, and test files.
- Added `docx` import alias to `tests/test_import_requirements.py`.
- Removed skipped artifact-dependent tests; replaced with generated ODT fixtures.

- **WP-4.1: Updated docx_to_exam_yaml.py to output new YAML format**
  - Modified `parse_inline_choices()` function to return plain choice text strings without letter prefixes (e.g., "Loss of atoms" instead of "A. Loss of atoms").
  - Updated `parse_docx_questions()` to use new YAML keys: `statement` (replaces `heading` for questions), `choices` as plain list (replaces dict with `layout`/`items`). Removed `number` fields from questions (auto-numbered by builder).
  - Changed section building in `build_yaml_structure()` to use `chapter` key (replaces `heading`) for section headings.
  - Added automatic stripping of letter prefixes from all choice patterns: inline choices, list paragraph choices, and text field choice parsing.
  - Appends `text` field content (if present) to question `statement` with newline separator, eliminating separate text field.
  - Fixed table attachment logic to assign tables to most recently parsed question.
  - Verified full end-to-end functionality: docx_to_exam_yaml.py -> odt_exam_builder.py produces valid styled ODT without errors.
  - Tested with Biochem_Exam_2_Spring_2026.docx: successfully parsed 50 questions with 8 embedded images.

- **WP-2.1: Default exam first page boilerplate with name and score lines**
  - Created new `exam_defaults.py` module with centralized defaults for exam boilerplate text.
  - Added `DEFAULT_NAME_LINE` constant: "Full Name: __________________________"
  - Added `DEFAULT_SCORING_SECTIONS` constant: 4 (number of scoring blanks on first page)
  - Implemented `format_score_line(total_points, num_sections)` function to generate "Final Score ____ / ____ / ... / total pts" lines with configurable section count.
  - Updated `build_document_body()` to build proper first page with three elements:
    - Line 1: Exam title (from YAML `title` field) in "Heading 1" style
    - Line 2: Name line (from YAML `student_line` field or default) in "Standard" style
    - Line 3: Score line (from YAML `total_points` field or auto-counted questions, with `scoring_sections` configurable) in "Standard" style
  - Added `count_total_questions(sections)` helper function to sum all questions across all sections when `total_points` is not explicitly provided.
  - YAML fields: `student_line` (optional, overrides default), `total_points` (optional, defaults to question count), `scoring_sections` (optional, defaults to 4)
  - Removed `date` paragraph from body (date moved to page header in WP-2.2)
  - Comprehensive unit test suite in `tests/test_exam_defaults.py` with 5 tests covering score line formatting with various section counts and default values.

- **WP-2.2: Added student name header to body pages (Standard master page)**
  - Updated `create_page_layouts()` function to accept optional `date_str` parameter for embedding date in page headers.
  - Added "Header" paragraph style (9pt font, Liberation Sans, with two tab stops: center tab at 3.65in and right tab at 7.3in) for consistent header formatting.
  - Standard master page (Mpm1/body pages) now includes header with three columns: "Page X of Y" (left), date (center), and "First Name:_____________________________" (right).
  - First Page master page (Mpm2/title page) includes an empty header to keep title page clean.
  - Added header-style properties to page layout Mpm1 with 0.2in margin below header.
  - Updated `assemble_odt()` to extract date from exam YAML and pass it to `create_page_layouts()`.
  - Uses ODF fields for automatic page numbering: `text:page-number` with `text:select-page="current"` for current page, `text:page-count` for total page count.

- **WP-3.2: Created okla_to_exam_yaml.py -- okla_chrst_bqge format to YAML converter**
  - New executable script converts okla_chrst_bqge format questions (from qti-package-maker) to the new exam YAML format.
  - Supports MC (multiple choice) and MA (multiple answer) question types; skips FIB (fill in blank) and MATCH questions as not compatible with bubble-sheet printing.
  - Automatically strips question number prefixes ("1. ", "12. ") from statement text.
  - Strips choice letter prefixes ("a) ", "b) ") and asterisk markers ("*a) ") from choice text, rendering as plain choice list.
  - Block-based format: questions separated by blank lines, with asterisk (*) marking correct answers (ignored in output).
  - Command-line interface: `-i input_file -o output_file -t title` (title optional, defaults to "Exam").
  - Output YAML includes required title, date (2026-04-02), and single "Questions" section with all parsed questions.
  - Comprehensive unit test suite (`tests/test_okla_to_exam_yaml.py`) with 18 tests covering MC/MA questions, skipping FIB/MATCH, edge cases (leading numbers, whitespace, special characters), and full end-to-end conversion with YAML output verification.

- **WP-3.1: Created bbq_to_exam_yaml.py -- BBQ text format to YAML converter**
  - New executable script converts BBQ text format questions (from qti-package-maker) to the new exam YAML format.
  - Supports MC (multiple choice), MA (multiple answer), MAT (matching), and ORD (ordering) question types.
  - Automatically strips correct/incorrect status markers from MC/MA questions; renders as plain choice list for exam output.
  - Converts MAT questions to YAML table format with columns ["Prompt", "Match"] and rows for each match pair.
  - Converts ORD questions to plain choice list (ordering info discarded for print-only output).
  - Command-line interface: `-i input_file -o output_file -t title` (title optional, defaults to "Exam").
  - Output YAML includes required title, date (2026-04-02), and single "Questions" section with all parsed questions.
  - Comprehensive unit test suite (`tests/test_bbq_to_exam_yaml.py`) with 14 tests covering each question type, edge cases (empty lines, whitespace), and full end-to-end conversion.

- **WP-1.4: Auto-select question style (Question Heading vs. Question Follow)**
  - Added `select_question_style()` function: automatically selects "Question Heading" or "Question Follow" style based on the previous element in the document.
  - "Question Heading" is used for questions in normal sequential flow (after other questions or choices).
  - "Question Follow" is used for questions immediately after images, tables, or chapter headings, reducing visual awkwardness and spacing issues.
  - Updated `build_document_body()` to track the previous element type (`prev_element` variable tracking 'chapter', 'question', 'choices', 'table', 'image') and call `select_question_style()` before creating each question paragraph.
  - Added comprehensive documentation to [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) explaining the auto-selection rules and when each style is used.

- **WP-1.2: Auto-numbering, auto-layout, and choice formatting in builder**
  - Added `auto_layout_for_choices()` function: automatically selects Choices3/4/5 layout based on choice count and max text length (5 short -> Choices5, 5 long -> Choices4 with overflow, 3 -> Choices3, 2 or 4 -> Choices4).
  - Implemented auto-numbering in `build_document_body()`: questions numbered sequentially starting at 1, with optional `number` field override. Question text prefixed with "##. statement" format (period, never parenthesis).
  - Updated `create_choices_paragraph()` to accept plain text choices list and auto-generate bold letter prefixes "(A) (B) (C)" via `text:span` with `AutoBold` automatic style.
  - Added `Chapter Heading` named style (14pt bold, dark purple #6600cc, Liberation Sans, keep-with-next).
  - Updated `build_document_body()` to use new YAML keys: `section.chapter` (not `heading`), `question.statement` (not `heading`/`text`), `question.choices` as plain list (not dict with `layout`/`items`), `question.layout` optional override at question level.

### Behavior or Interface Changes

- Builder now requires new YAML format. Old format with `heading`, `text`, and choices dict will not work.
- `create_choices_paragraph()` signature changed: now takes plain choices list and optional `auto_styles` parameter instead of pre-formatted items dict.
- Removed unused `copy` module import from `odt_exam_builder.py`.
- Converted `Biochem_Exam_2_Spring_2026.yaml` to new format: changed `heading` -> `chapter` (in sections), `heading` -> `statement` (in questions, with number prefix stripped), removed letter prefixes from choice items, removed explicit `number` fields, removed explicit `layout` fields. Text field contents appended to statement where present. All `image` and `table` fields preserved as-is.

### Removed `_20_` hex encoding from generated ODT style names

- Style names now use plain spaces directly (ODF spec allows this). Examples: `Question_20_Heading` -> `Question Heading`, `Table_20_Contents` -> `Table Contents`, `Heading_20_1` -> `Heading 1`, etc. Kept `encode_style_name()` and `decode_style_name()` functions in `odt_utils.py` for reading legacy ODT files. Updated `get_style_by_name()` to match both plain and encoded names for backwards compatibility.

### Created YAML format specification

- Created [docs/YAML_EXAM_FORMAT.md](docs/YAML_EXAM_FORMAT.md) with complete specification for the new simplified YAML exam format. Documents conventions for `title`, `date`, `total_points`, `sections[].chapter`, `sections[].questions[]` with `statement`, `number` (optional), `choices` (plain text, no letter prefixes), `layout` (optional, auto-determined), `image`, and `table` fields.
- Auto-layout algorithm: 5 short choices -> Choices5, 5 long choices -> Choices4 (2 rows), 3 choices -> Choices3, 2 or 4 choices -> Choices4 (with tabs). User can override with explicit `layout` field.
- Documented that `number` field is optional and serves as override only; questions are auto-numbered by order. Choice items are plain text without letter prefixes (builder generates bold `(A)` format).

## 2026-04-02 (earlier)

### Fixes and Maintenance

- Rewrote `README.md` to describe the actual exam formatting tools instead of the starter template boilerplate. Added quick start examples for all three CLI tools and linked all existing docs.

## 2026-04-01

### Additions and New Features

- Added `odt_utils.py` -- shared ODT utility module for reading/writing ODT files using `lxml` and `zipfile`. Includes ODF namespace registry, style accessors, round-trip read/write with ODF-compliant mimetype ordering, and canonical style comparison.
- Added `extract_odt_styles.py` -- extracts named styles from ODT files to YAML or content-free template ODT. Supports style comparison between two ODT files and family filtering. YAML output decodes ODF-encoded names to human-readable form.
- Added `propagate_odt_styles.py` -- applies named styles from a source ODT to target ODT files. Supports dry-run mode, backup creation, and optional page layout propagation. Never touches automatic styles.
- Added `odt_exam_builder.py` -- generates fully styled ODT exam documents from YAML input. Embeds all named styles from [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) including page layouts, question formatting, multiple choice layouts (Choices3/4/5), tables with colored headers, and image embedding.
- Added `lxml` and `pyyaml` to [pip_requirements.txt](pip_requirements.txt).
- Added test files: `tests/test_odt_utils.py`, `tests/test_extract_odt_styles.py`, `tests/test_propagate_odt_styles.py`, `tests/test_odt_exam_builder.py`.

### Fixes and Maintenance

- Fixed ODF style name encoding: real LibreOffice ODT files use `_20_` hex encoding for spaces in style names (e.g., `Question_20_Heading`). Updated all tools to use encoded names for compatibility with real exam documents.
- Added `encode_style_name()` and `decode_style_name()` to `odt_utils.py` for converting between human-readable and ODF-encoded style names.
- Updated `get_style_by_name()` to accept either human-readable or ODF-encoded names.
- Trimmed test suite: removed tests for trivial wrappers, excessive assertions, and exact-count checks per updated testing guidelines.

### Decisions and Failures

- Chose `lxml` + `zipfile` over `odfpy` for ODT manipulation per [docs/ROADMAP.md](docs/ROADMAP.md). This avoids a new dependency and gives full control over XML structure.
- Discovered ODF `_XX_` hex encoding for style names by examining real ARTIFACTS. Both 2019 and 2025 exams use this consistently.

### Developer Tests and Notes

- Full test suite: 140 passed, 0 skipped (with ARTIFACTS present).
- All new code passes pyflakes, bandit, shebang alignment, tab indentation, import requirements, and ASCII compliance checks.
