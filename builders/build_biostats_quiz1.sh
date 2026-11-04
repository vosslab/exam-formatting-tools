#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p generated
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'BIOL 318/418 Quiz 1' --points 9.5 \
  -i task_files/biostats_quiz1.csv -o generated/biostats_quiz1.yaml
rm -f -- generated/biostats_quiz1.docx
python3 converters/yaml_to_exam_docx.py --page-break-sections \
  -i generated/biostats_quiz1.yaml \
  -o generated/biostats_quiz1.docx
bash converters/docx_to_pdf.sh \
  generated/biostats_quiz1.docx generated
