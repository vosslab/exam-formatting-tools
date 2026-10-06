#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
source source_me.sh || exit 1
set -e

mkdir -p quiz2

JPEG_QUALITY=70
DPI=100
CONVERT_OPTIONS="pdf:writer_pdf_Export:{"\
"\"Quality\":{\"type\":\"long\",\"value\":\"$JPEG_QUALITY\"},"\
"\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"},"\
"\"MaxImageResolution\":{\"type\":\"long\",\"value\":\"$DPI\"},"\
"\"SelectPdfVersion\":{\"type\":\"long\",\"value\":\"3\"}"\
"}"

# 17 question blocks: 11 ordinary questions, five four-item matches,
# and one two-item pedigree match = 22 question equivalents.
python3 launchers/bbq_tasks_to_exam_yaml.py \
  -i genetics_tasks-quiz2.csv \
  --quiz --title 'Quiz 2: Genetics (2026)' \
  -o quiz2/quiz2.yaml

python3 launchers/yaml_to_exam_docx.py \
  -i quiz2/quiz2.yaml \
  -o quiz2/quiz2.docx

/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless \
  --norestore \
  --convert-to "$CONVERT_OPTIONS" \
  --outdir . \
  quiz2/quiz2.docx

ls -sh quiz2.pdf
