#!/usr/bin/env bash


rm -fr quiz1/
mkdir quiz1/

JPEG_QUALITY=70
DPI=100
CONVERT_OPTIONS="pdf:writer_pdf_Export:{"\
"\"Quality\":{\"type\":\"long\",\"value\":\"$JPEG_QUALITY\"},"\
"\"ReduceImageResolution\":{\"type\":\"boolean\",\"value\":\"true\"},"\
"\"MaxImageResolution\":{\"type\":\"long\",\"value\":\"$DPI\"},"\
"\"SelectPdfVersion\":{\"type\":\"long\",\"value\":\"3\"}"\
"}"


source source_me.sh && \
./launchers/bbq_tasks_to_exam_yaml.py \
  -i genetics_tasks1.csv \
  --quiz --title 'Quiz 1: Genetics (2026)' \
  -o quiz1/quiz1.yaml \
&& \
./launchers/yaml_to_exam_docx.py \
  -i quiz1/quiz1.yaml \
  -o quiz1/quiz1.docx \
&& \
/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless \
  --norestore \
  --convert-to "$CONVERT_OPTIONS" \
  quiz1/quiz1.docx \
&& \
ls -sh quiz1.pdf
