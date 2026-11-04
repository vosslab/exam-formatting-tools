#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p generated
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Quiz 2: Genetics (2026)' \
  -i task_files/genetics_quiz2.csv -o generated/genetics_quiz2.yaml
rm -f -- generated/genetics_quiz2.docx
python3 converters/yaml_to_exam_docx.py \
  -i generated/genetics_quiz2.yaml -o generated/genetics_quiz2.docx
bash converters/docx_to_pdf.sh generated/genetics_quiz2.docx generated
