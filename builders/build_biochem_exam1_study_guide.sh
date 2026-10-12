#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p bchem1
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Biochem Exam 1 Study Guide (2026)' \
  -i task_files/biochem_exam1.csv -o bchem1/bchem1.yaml
rm -f -- bchem1/bchem1.docx
python3 converters/yaml_to_exam_docx.py -i bchem1/bchem1.yaml -o bchem1/bchem1.docx
bash converters/docx_to_pdf.sh bchem1/bchem1.docx .
