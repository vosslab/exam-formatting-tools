#!/usr/bin/env python3
"""Validate an exam YAML against ZipGrade 100-question form constraints.

ZipGrade compatibility is line-number anchored. This script reports each
incompatible question by source line and severity (ERROR or FIXABLE), and
optionally writes a filtered YAML containing only ZipGrade-OK questions.

Without -o (report-only mode):
	Prints the report and raises ValueError if any ERROR or FIXABLE
	issue exists. Exits 0 only when all questions are OK and the row
	total is <= 100.

With -o (filter-write mode):
	Writes a filtered YAML containing only OK questions; drops both
	ERROR and FIXABLE. Refuses to overwrite an existing file. Raises
	ValueError only when zero OK questions remain.

Authors are expected to use this in a tight edit loop. The DOCX flag
yaml_to_exam_docx.py --zip-grade is a separate, conservative path that
also drops both ERROR and FIXABLE before building the printable exam.
See docs/USAGE.md.
"""

# Standard Library
import os
import sys
import argparse

# Pip Modules
import yaml

# Local Repo Modules
import ef_tools.cli_checks
import ef_tools.zip_grade


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Validate exam YAML against ZipGrade A-E bubble form constraints"
	)
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help="Input exam YAML file"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', default=None,
		help="Optional output YAML file containing only OK questions. "
			"When omitted, runs in report-only mode."
	)
	args = parser.parse_args()
	return args


#============================================
def write_filtered_yaml(filtered: dict, output_path: str) -> None:
	"""Write the filtered exam dict to YAML, refusing to overwrite."""
	# safety check: never overwrite existing files (matches yaml_to_exam_docx.py policy)
	if os.path.exists(output_path):
		raise FileExistsError(f"Output file already exists: {output_path}")
	with open(output_path, 'w') as out_handle:
		yaml.safe_dump(filtered, out_handle, sort_keys=False, allow_unicode=False)


#============================================
def report_only(exam_data: dict, source_path: str) -> None:
	"""Run the linter in report-only mode and raise on any non-OK issue.

	The report includes both ERROR and FIXABLE issues; both are non-OK
	for ZipGrade.
	"""
	issues = ef_tools.zip_grade.validate(exam_data)
	if not issues:
		# count rows for the OK-summary line
		total_rows = ef_tools.zip_grade.filtered_total_rows(exam_data)
		print(f"ZipGrade compatibility OK ({total_rows} numbered rows / {ef_tools.zip_grade.MAX_TOTAL_ROWS})")
		return
	report_text = ef_tools.zip_grade.format_report(issues, source_path=source_path)
	print(report_text)
	# count by severity for the summary line
	error_count = sum(1 for issue in issues
		if issue.severity is ef_tools.zip_grade.Severity.ERROR)
	fixable_count = sum(1 for issue in issues
		if issue.severity is ef_tools.zip_grade.Severity.FIXABLE)
	summary = (f"Summary: {error_count} ERROR, {fixable_count} FIXABLE "
		f"(both are non-OK for ZipGrade).")
	print(summary, file=sys.stderr)
	# both ERROR and FIXABLE fail report-only mode
	raise ValueError("ZipGrade compatibility check failed; see report above")


#============================================
def filter_write(exam_data: dict, source_path: str, output_path: str) -> None:
	"""Filter exam to OK-only and write YAML.

	Prints the removal report (so the author sees what was dropped) plus
	a summary line. Warns but writes when post-filter row total still
	exceeds 100. Raises only when no OK questions remain to write.
	"""
	filtered, issues = ef_tools.zip_grade.filter_exam(exam_data)
	# print the removal report so the author sees what was dropped
	if issues:
		report_text = ef_tools.zip_grade.format_report(issues, source_path=source_path)
		print(report_text)
	# count remaining real questions (excluding inline-chapter pseudo-questions)
	kept_real_count = 0
	for section in filtered.get('sections', []):
		for question in section.get('questions', []):
			if 'chapter' in question and 'statement' not in question:
				continue
			kept_real_count += 1
	kept_rows = ef_tools.zip_grade.filtered_total_rows(filtered)
	# refuse to write an empty exam
	if kept_real_count == 0:
		raise ValueError(
			"No ZipGrade-compatible questions remain after filtering; "
			"refusing to write an empty exam YAML."
		)
	# summary line
	dropped = sum(1 for issue in issues
		if issue.question_number is not None)
	print(f"ZipGrade filter: kept {kept_real_count} questions ({kept_rows} rows), "
		f"dropped {dropped}.")
	# warn if even after filtering we still exceed 100 rows
	if kept_rows > ef_tools.zip_grade.MAX_TOTAL_ROWS:
		warning = (f"WARNING: {kept_rows} rows after filtering; "
			f"rows {ef_tools.zip_grade.MAX_TOTAL_ROWS + 1}-{kept_rows} "
			f"won't fit on a {ef_tools.zip_grade.MAX_TOTAL_ROWS}-row ZipGrade form.")
		print(warning, file=sys.stderr)
	# write the filtered YAML
	write_filtered_yaml(filtered, output_path)
	print(f"Filtered exam YAML written to {output_path}")


#============================================
def main():
	"""Main entry point."""
	args = parse_args()
	# validate input extension and resolve optional output
	ef_tools.cli_checks.require_extensions(args.input_file, ('.yml', '.yaml'), 'input')
	output_file = args.output_file
	if output_file is not None:
		ef_tools.cli_checks.require_extensions(output_file, ('.yml', '.yaml'), 'output')
	# load YAML through the line-tracking loader
	with open(args.input_file, 'r') as in_handle:
		# LineTrackingLoader extends yaml.SafeLoader, so this is safe
		exam_data = yaml.load(in_handle, Loader=ef_tools.zip_grade.LineTrackingLoader)  # nosec B506
	# dispatch
	if output_file is None:
		report_only(exam_data, args.input_file)
	else:
		filter_write(exam_data, args.input_file, output_file)


#============================================
if __name__ == '__main__':
	main()
