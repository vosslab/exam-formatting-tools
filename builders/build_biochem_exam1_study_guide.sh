#!/usr/bin/env bash
# Run from the repository root.
source source_me.sh || exit 1
set -e

mkdir -p generated
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Biochem Exam 1 Study Guide (2026)' \
  -i task_files/biochem_exam1.csv -o generated/biochem_exam1_study_guide.yaml
rm -f -- generated/biochem_exam1_study_guide.docx
python3 converters/yaml_to_exam_docx.py \
  -i generated/biochem_exam1_study_guide.yaml \
  -o generated/biochem_exam1_study_guide.docx
bash converters/docx_to_pdf.sh \
  generated/biochem_exam1_study_guide.docx generated
