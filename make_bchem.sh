#!/usr/bin/env bash


rm -fr bchem1/
mkdir bchem1/

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
  -i biochem_tasks1.csv \
  --quiz --title 'Biochem Exam 1 Study Guide (2026)' \
  -o bchem1/bchem1.yaml \
&& \
./launchers/yaml_to_exam_docx.py \
  -i bchem1/bchem1.yaml \
  -o bchem1/bchem1.docx \
&& \
/Applications/LibreOffice.app/Contents/MacOS/soffice \
  --headless \
  --norestore \
  --convert-to "$CONVERT_OPTIONS" \
  bchem1/bchem1.docx \
&& \
ls -sh bchem1.pdf
