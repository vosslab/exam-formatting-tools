#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p quiz2
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Quiz 2: Genetics (2026)' \
  -i task_files/genetics_quiz2.csv -o quiz2/quiz2.yaml
rm -f -- quiz2/quiz2.docx
python3 converters/yaml_to_exam_docx.py -i quiz2/quiz2.yaml -o quiz2/quiz2.docx
bash converters/docx_to_pdf.sh quiz2/quiz2.docx .
