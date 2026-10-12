#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p output_biostats_quiz1
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'BIOL 318/418 Quiz 1' --points 9.5 \
  -i task_files/biostats_quiz1.csv -o output_biostats_quiz1/biostats_quiz1.yaml
rm -f -- output_biostats_quiz1/biostats_quiz1.docx
python3 converters/yaml_to_exam_docx.py --page-break-sections \
  -i output_biostats_quiz1/biostats_quiz1.yaml \
  -o output_biostats_quiz1/biostats_quiz1.docx
bash converters/docx_to_pdf.sh \
  output_biostats_quiz1/biostats_quiz1.docx output_biostats_quiz1
