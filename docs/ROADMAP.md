# Roadmap

Implementation plan for ODT exam formatting tools. Styles reference: [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md).

## Phase 1: Shared ODT utility module

**File**: `odt_utils.py`

Shared module for reading and writing ODT files using `lxml` and `zipfile` (no `odfpy` dependency).

- Parse ODT ZIP archive, extract `styles.xml` and `content.xml`
- Namespace registry for all ODF namespaces (`fo:`, `style:`, `text:`, `draw:`, `table:`, etc.)
- Read named styles from `styles.xml` (`office:styles` section)
- Read automatic styles from `content.xml` (`office:automatic-styles` section)
- Read page layouts and master pages
- Write modified XML back into a valid ODT ZIP archive (preserving `meta.xml`, `manifest.xml`, images, etc.)
- Helper to compare two style elements for equality

**Verification**: unit tests that round-trip an ODT (read then write) and confirm the output opens in LibreOffice.

## Phase 2: Style template extractor

**File**: `extract_odt_styles.py`

Reads one or more ODT files and extracts named styles to YAML or a minimal template ODT.

### Features

- Extract all named paragraph, text, table, page-layout, and list styles from an ODT
- Output as YAML (human-readable style catalog) or as a content-free template ODT (styles only, no body text)
- Compare mode: diff styles between two ODT files, report added/removed/changed styles
- Filter by style family (`paragraph`, `text`, `table`, `table-cell`, `page-layout`)

### CLI

```
extract_odt_styles.py -i exam.odt -o styles.yaml
extract_odt_styles.py -i exam.odt -o template.odt --template
extract_odt_styles.py --compare old.odt new.odt
```

**Verification**: extract styles from `ARTIFACTS/2025_genetics_final_exam2.odt`, confirm YAML output matches [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) values.

## Phase 3: Style propagation tool

**File**: `propagate_odt_styles.py`

Applies styles from a source ODT to one or more target ODT files, preserving target content.

### Features

- Read named styles from source ODT
- Replace or merge named styles in target ODT's `styles.xml`
- Optionally propagate page layouts and master pages
- Dry-run mode that reports what would change without modifying files
- Backup target before overwriting (copy to `_backup/` or `/tmp/`)

### CLI

```
propagate_odt_styles.py -s source.odt -t target1.odt target2.odt
propagate_odt_styles.py -s source.odt -t target.odt --dry-run
propagate_odt_styles.py -s source.odt -t target.odt --include-page-layout
```

### Edge cases

- Target uses a style name that source does not define: leave unchanged
- Source defines a style that target does not use: add it (styles are harmless if unused)
- Automatic styles in `content.xml`: do NOT propagate (they are element-specific)

**Verification**: propagate styles from 2025 exam to 2019 exam, open result in LibreOffice, confirm formatting matches and content is intact.

## Phase 4: ODT exam builder

**File**: `odt_exam_builder.py`

Generates a fully styled ODT exam document from structured input data (YAML).

### Input format (YAML)

```yaml
title: "Genetics Final Exam"
date: "2025-12-10"
student_line: "Name: ________________  Score: ____/100"
sections:
  - heading: "Chapter 1 -- Foundations"
    questions:
      - number: 1
        heading: "1. Which of the following is NOT a nucleotide base?"
        text: "Select the best answer."
        choices:
          layout: 4  # uses Choices4 style (3 columns)
          items: ["adenine", "cytosine", "ribose", "guanine", "thymine"]
      - number: 2
        heading: "2. Matching question"
        table:
          columns: ["Term", "Definition"]
          rows:
            - ["Gene", "Unit of heredity"]
            - ["Allele", "Variant of a gene"]
```

### Features

- Create ODT with all named styles from [docs/ODT_EXAM_STYLES.md](docs/ODT_EXAM_STYLES.md) embedded
- First Page master page for title, Standard master page for body
- Question numbering with Question Heading and Question styles
- Multiple choice with Choices3/4/5 tab-aligned layouts
- Tables with header row (gray #f2f2f2) and optional cell coloring
- Embed images from file paths
- Page breaks between sections (optional)

### CLI

```
odt_exam_builder.py -i exam_data.yaml -o exam_output.odt
```

**Verification**: build an exam from sample YAML, open in LibreOffice, visually compare against `ARTIFACTS/2025_genetics_final_exam2.odt`.

## Dependency order

```
Phase 1 (odt_utils.py)
  |
  +---> Phase 2 (extract_odt_styles.py)
  |
  +---> Phase 3 (propagate_odt_styles.py)
  |
  +---> Phase 4 (odt_exam_builder.py)
```

Phases 2, 3, and 4 all depend on Phase 1 but are independent of each other and can be built in parallel after Phase 1 is complete.

## Requirements

No new pip dependencies needed. Uses:

- `lxml` (already installed, v6.0.2)
- `zipfile` (stdlib)
- `xml.etree.ElementTree` (stdlib, fallback)
- `pyyaml` (already installed, for YAML input/output)

Optional future addition: `odfpy` for higher-level ODF API if manipulation becomes complex.
