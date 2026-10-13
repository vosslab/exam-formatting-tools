#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p output_genetics_exam1
# Keep the same parents across all four questions and subsequent rebuilds.
# Remove this JSON explicitly when a new random cross is wanted.
if [[ ! -f output_genetics_exam1/large_cross.json ]]; then
  (
    source ../biology-problems/source_me.sh
    python3 ../biology-problems/problems/inheritance-problems/large_crosses/unique_counts.py \
      --num-genes 4 --save-scenario output_genetics_exam1/large_cross.json
  )
fi
python3 converters/bbq_tasks_to_exam_yaml.py \
  --exam --title 'Exam 1: Genetics (2026) - Draft' \
  -i task_files/genetics_exam1.csv -o output_genetics_exam1/genetics_exam1.yaml
python3 converters/validate_zip_grade_yaml.py \
  -i output_genetics_exam1/genetics_exam1.yaml
rm -f -- output_genetics_exam1/genetics_exam1.docx
python3 converters/yaml_to_exam_docx.py --keep-questions-together \
  -i output_genetics_exam1/genetics_exam1.yaml \
  -o output_genetics_exam1/genetics_exam1.docx
bash converters/docx_to_pdf.sh \
  output_genetics_exam1/genetics_exam1.docx output_genetics_exam1 150
