#!/usr/bin/env bash
# Run from the repository root; use a new output folder for each new version.
source source_me.sh || exit 1
set -e

OUTPUT_DIR="${1:-generated/genetics_quiz3}"
python3 builders/make_genetics_quiz3.py -o "$OUTPUT_DIR/quiz3.yaml"
python3 converters/yaml_to_exam_docx.py -i "$OUTPUT_DIR/quiz3.yaml" \
	-o "$OUTPUT_DIR/quiz3.docx" --page-break-sections --keep-questions-together
bash converters/docx_to_pdf.sh "$OUTPUT_DIR/quiz3.docx" "$OUTPUT_DIR" 300
