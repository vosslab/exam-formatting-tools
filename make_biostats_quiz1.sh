#!/usr/bin/env bash

# Edit these settings for this quiz.
TITLE='BIOL 318/418 Quiz 1'
JPEG_QUALITY=70
DPI=100
TOTAL_POINTS=9.5
TASKS='biostats_tasks_quiz1.csv'
OUTPUT_DIR='output_biostats_quiz1'
BASENAME='biostats_quiz1'

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
source source_me.sh || exit 1
set -e

mkdir -p "$OUTPUT_DIR"
YAML_FILE="$OUTPUT_DIR/$BASENAME.yaml"
DOCX_FILE="$OUTPUT_DIR/$BASENAME.docx"
PDF_FILE="$OUTPUT_DIR/$BASENAME.pdf"

CONVERT_OPTIONS="pdf:writer_pdf_Export:{"\
"\"Quality\":{\"type\":\"long\",\"value\":\"$JPEG_QUALITY\"},"\
"\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"},"\
"\"MaxImageResolution\":{\"type\":\"long\",\"value\":\"$DPI\"},"\
"\"SelectPdfVersion\":{\"type\":\"long\",\"value\":\"3\"}"\
"}"

# ASVS 1.2.5: quote settings so each value stays one command argument.
python3 launchers/bbq_tasks_to_exam_yaml.py \
  --quiz --title "$TITLE" \
  -i "$TASKS" -o "$YAML_FILE"

# Set the score line and put long MC choices on separate lines.
python3 make_biostats_quiz1.py -i "$YAML_FILE" -p "$TOTAL_POINTS"

# Replace only this build's generated document and PDF.
rm -f -- "$DOCX_FILE" "$PDF_FILE"
python3 launchers/yaml_to_exam_docx.py \
  -i "$YAML_FILE" -o "$DOCX_FILE"

# Start the measures-of-center section on a new page.
python3 make_biostats_quiz1.py -i "$DOCX_FILE"

/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless --norestore \
  --convert-to "$CONVERT_OPTIONS" \
  --outdir "$OUTPUT_DIR" "$DOCX_FILE"

test -f "$PDF_FILE"
ls -sh "$PDF_FILE" "$DOCX_FILE" "$OUTPUT_DIR/$BASENAME-key.txt"
