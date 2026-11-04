#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

OUTPUT_DIR="generated"
mkdir -p "$OUTPUT_DIR"
rm -f -- "$OUTPUT_DIR/testcross_handout.yaml" "$OUTPUT_DIR/testcross_handout-key.txt" \
	"$OUTPUT_DIR/testcross_handout.docx"
python3 converters/bbq_tasks_to_exam_yaml.py --handout \
	--title 'Fruit Fly Testcross Handout' -i task_files/testcross_handout.csv \
	-o "$OUTPUT_DIR/testcross_handout.yaml"
python3 converters/yaml_to_exam_docx.py -i "$OUTPUT_DIR/testcross_handout.yaml" \
	-o "$OUTPUT_DIR/testcross_handout.docx"
bash converters/docx_to_pdf.sh "$OUTPUT_DIR/testcross_handout.docx" "$OUTPUT_DIR"
