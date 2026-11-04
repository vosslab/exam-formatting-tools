#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

python3 tools/split_matching_yaml.py \
  -i task_files/matching_sets/hypothesis_testing_terms_split.json
mkdir -p generated
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'BIOL 318/418 Quiz 2' \
  -i task_files/biostats_quiz2.csv -o generated/biostats_quiz2.yaml
rm -f -- generated/biostats_quiz2.docx
python3 converters/yaml_to_exam_docx.py --page-break-sections \
  -i generated/biostats_quiz2.yaml \
  -o generated/biostats_quiz2.docx
bash converters/docx_to_pdf.sh \
  generated/biostats_quiz2.docx generated
