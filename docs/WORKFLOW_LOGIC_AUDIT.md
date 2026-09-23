# Workflow logic audit

**Reviewed:** 2026-09-23

This note records workflow and ownership issues found in a focused review of
the converter paths. It is evidence for later planning, not an implementation
plan. Source locations describe the reviewed checkout and should be rechecked
when work begins.

## Findings

### High: converter workflows live in CLI launchers

The repository rule reserves `launchers/` for thin delegates into reusable
application code ([REPO_STYLE.md](REPO_STYLE.md#repository-structure)). Several
launchers currently own full workflows:

- [html_to_exam_yaml.py](../launchers/html_to_exam_yaml.py#L562) parses HTML,
  assembles exam data, rewrites media paths, validates destinations, and writes
  YAML through line 634.
- [yaml_to_exam_docx.py](../launchers/yaml_to_exam_docx.py#L189) contains the
  DOCX construction workflow through line 439, including schema traversal,
  image resolution, filtering, sizing, and rendering.
- [docx_to_exam_yaml.py](../launchers/docx_to_exam_yaml.py#L50) owns image and
  table extraction, DOCX parsing, exam-data assembly, and output writing.

This mixes reusable conversion behavior with command-line handling. Move
workflow functions behind cohesive `ef_tools/` boundaries and leave launchers
responsible for arguments, dispatch, and user-facing messages. Migrate one
converter path at a time, using its existing pipeline behavior as the contract.

### High: output publication has inconsistent replacement behavior

[html_to_exam_yaml.py](../launchers/html_to_exam_yaml.py#L608) refuses to write
when its YAML destination already exists. In contrast,
[docx_to_exam_yaml.py](../launchers/docx_to_exam_yaml.py#L63) reuses the image
directory, overwrites deterministic `exam_image_*` files at lines 99-104, then
truncates the YAML output at lines 456-458. The
[okla_to_exam_yaml.py](../launchers/okla_to_exam_yaml.py#L240) also truncates
its YAML destination at lines 242-250. A failed multi-file conversion can
therefore leave replaced media alongside old or missing YAML, while another
converter fails early on the same collision.

Choose one documented output-collision policy for converter outputs. For
multi-file output, generate into a temporary destination, validate the result,
then publish the complete artifact set. Avoid overwriting files in a shared
media directory before the YAML that references them is ready.

### Medium: converters serialize the shared YAML schema differently

[exam_yaml_writer.py](../ef_tools/exam_yaml_writer.py#L28) owns insertion-order
serialization and the apostrophe-aware ASCII output convention. The DOCX and
Oklahoma converters call `yaml.dump` directly with different settings:
[docx_to_exam_yaml.py](../launchers/docx_to_exam_yaml.py#L456) enables Unicode
and sets a line width, while
[okla_to_exam_yaml.py](../launchers/okla_to_exam_yaml.py#L242)
enables Unicode and preserves insertion order. Decide the canonical encoding,
ordering, quoting, and wrapping rules, then route every converter through that
single writer. Preserve Unicode only if it is part of the shared schema
contract.

### Medium: the local quiz script is destructive and host-specific

The local [make_quiz.sh](../make_quiz.sh#L4) recursively deletes `quiz1/`
before rebuilding it and hard-codes the LibreOffice application path at line
27. It already supplies both `--headless` and `--norestore`. If this becomes a
maintained repository workflow, constrain cleanup to a dedicated generated
directory and resolve the LibreOffice command through the repository's chosen
wrapper or configuration. Keep user-authored files outside the directory the
script clears.

## Suggested work order

1. Define output ownership and collision behavior, including how a multi-file
   result is published without leaving a partial conversion.
2. Move one reusable converter workflow out of its launcher and preserve the
   command-line interface.
3. Establish one exam-YAML serialization contract and apply it to all writers.
4. Decide whether `make_quiz.sh` is a supported project command or a local
   convenience script; make its output ownership explicit either way.

Plan execution can stay manager- and subagent-owned. Use synthetic input and
temporary output directories for conversion and failure-path evidence. Do not
make a manual visual review or human approval a completion gate. Add permanent
tests only for stable output contracts that lack existing coverage; use
temporary checks for implementation proof, following [PYTEST_STYLE.md](PYTEST_STYLE.md).

## Review limits

This audit did not change runtime behavior or run tests. The generated quiz
outputs were outside the converter review. Existing pipeline tests cover
HTML-to-YAML-to-DOCX and task-CSV-to-DOCX transitions, but they do not establish
a shared output-replacement policy for every converter.
