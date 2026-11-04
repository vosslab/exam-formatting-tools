#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p generated
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Quiz 1: Genetics (2026)' \
  -i task_files/genetics_quiz1.csv -o generated/genetics_quiz1.yaml
rm -f -- generated/genetics_quiz1.docx
python3 converters/yaml_to_exam_docx.py \
  -i generated/genetics_quiz1.yaml -o generated/genetics_quiz1.docx
bash converters/docx_to_pdf.sh generated/genetics_quiz1.docx generated
