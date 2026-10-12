#!/usr/bin/env bash

set -e
DOCX_FILE="${1:?Usage: docx_to_pdf.sh FILE.docx OUTPUT_DIR [DPI]}"
OUTPUT_DIR="${2:?Supply the PDF output directory}"
DPI="${3:-100}"
[[ "$DOCX_FILE" == *.docx ]]
test -f "$DOCX_FILE"
mkdir -p "$OUTPUT_DIR"
PDF_FILE="$OUTPUT_DIR/$(basename "${DOCX_FILE%.docx}").pdf"

CONVERT_OPTIONS="pdf:writer_pdf_Export:{"\
"\"Quality\":{\"type\":\"long\",\"value\":\"70\"},"\
"\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"},"\
"\"MaxImageResolution\":{\"type\":\"long\",\"value\":\"$DPI\"},"\
"\"SelectPdfVersion\":{\"type\":\"long\",\"value\":\"3\"}"\
"}"

# ASVS 1.2.5: keep paths and conversion options as separate quoted arguments.
rm -f -- "$PDF_FILE"
/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless --norestore --convert-to "$CONVERT_OPTIONS" \
  --outdir "$OUTPUT_DIR" "$DOCX_FILE"
test -f "$PDF_FILE"
ls -sh "$PDF_FILE"
