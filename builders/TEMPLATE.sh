#!/usr/bin/env bash
# Copy to build_<assessment>.sh; replace assessment_name and the title below.
# Run from the repository root. Keep this script flat; put processing logic in Python.
source source_me.sh || exit 1
set -e

mkdir -p generated

# If needed, regenerate matching splits before drawing questions:
# python3 tools/split_matching_yaml.py -i task_files/matching_sets/assessment_name_split.json

# Select --quiz, --exam, or --handout for the assessment.
python3 converters/bbq_tasks_to_exam_yaml.py \
  --quiz --title 'Assessment title' \
  -i task_files/assessment_name.csv -o generated/assessment_name.yaml

# For a ZipGrade exam, validate before formatting:
# python3 converters/validate_zip_grade_yaml.py -i generated/assessment_name.yaml

rm -f -- generated/assessment_name.docx
python3 converters/yaml_to_exam_docx.py \
  -i generated/assessment_name.yaml -o generated/assessment_name.docx
bash converters/docx_to_pdf.sh generated/assessment_name.docx generated
