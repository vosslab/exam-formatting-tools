#!/usr/bin/env python3
"""
Convert BBQ text format questions to YAML exam format.

Reads tab-separated bptools bbq questions and writes exam YAML plus a
`<stem>-key.txt` answer key. MC, MA, MAT, and ORD are printed; NUM, FIB, and
FIB_PLUS have no print form and are skipped. Drawing tables and supported
MathML equations become PNG assets beside the YAML.
"""

# Standard Library
import os
import argparse
import datetime

# Local Repo Modules
import ef_tools.bbq_html
import ef_tools.bbq_parse
import ef_tools.cli_checks
import ef_tools.question_utils
import ef_tools.exam_yaml_writer
import qti_package_maker.html_to_image.render_table


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Convert BBQ text format to YAML exam format"
	)
	parser.add_argument(
		'-i', '--input',
		dest='input_file',
		required=True,
		help="Input BBQ text file"
	)
	parser.add_argument(
		'-o', '--output',
		dest='output_file',
		default=None,
		help="Output YAML exam file. Defaults to <input-stem>.yml in CWD."
	)
	parser.add_argument(
		'-t', '--title',
		dest='exam_title',
		default='Exam',
		help="Exam title (default: Exam)"
	)
	args = parser.parse_args()
	return args


#============================================
def parse_bbq_file(input_path: str, math_renderer: object = None) -> list:
	"""Parse every printable bbq line in a file into records."""
	records = []
	with open(input_path, 'r') as handle:
		for line in handle:
			record = ef_tools.bbq_parse.parse_bbq_line(
				line, math_renderer=math_renderer)
			if record is not None:
				records.append(record)
	return records


#============================================
def render_record_tables(records: list, output_file: str,
			renderer: object = None) -> None:
	"""Rasterize drawing tables for every record and attach image paths.

	Uses one Chromium for drawing tables and does not open one for image-only
	records whose equations were already rendered during parsing.
	"""
	needs_tables = any(ef_tools.bbq_parse.has_tables(record) for record in records)
	needs_images = any(ef_tools.bbq_parse.has_rendered_images(record) for record in records)
	if not needs_tables and not needs_images:
		return
	stem = os.path.splitext(os.path.basename(output_file))[0]
	media_dir = os.path.join(os.path.dirname(os.path.abspath(output_file)), f"{stem}_files")
	if renderer is None and needs_tables:
		with qti_package_maker.html_to_image.render_table.TableRenderer() as active_renderer:
			_render_record_media(records, active_renderer, media_dir)
	else:
		_render_record_media(records, renderer, media_dir)


#============================================
def _render_record_media(records: list, renderer: object, media_dir: str) -> None:
	"""Save generated images and render any drawing tables in record order."""
	for index, record in enumerate(records, start=1):
		# lines without a CRC paragraph fall back to their position
		code = record['answer']['code'] or f"q{index:03d}"
		ef_tools.bbq_parse.render_record_tables(record, renderer, media_dir, code)


#============================================
def build_exam_dict(records: list, title: str) -> dict:
	"""Assemble the exam YAML structure from parsed records."""
	questions = [record['question'] for record in records]
	exam_dict = {
		'title': title,
		'date': datetime.date.today().isoformat(),
		'sections': [
			{
				'chapter': 'Questions',
				'questions': questions,
			}
		],
	}
	return exam_dict


#============================================
def write_outputs(exam_dict: dict, records: list, output_file: str, source: str) -> None:
	"""Write the exam YAML and its sibling answer key."""
	ef_tools.exam_yaml_writer.write_exam_yaml(exam_dict, output_file)
	questions = [record['question'] for record in records]
	answers = [record['answer'] for record in records]
	key_text = ef_tools.bbq_parse.format_answer_key(questions, answers, [source] * len(records))
	key_path = os.path.splitext(output_file)[0] + '-key.txt'
	with open(key_path, 'w') as handle:
		handle.write(key_text)


#============================================
def main() -> None:
	"""
	Main function: parse args, read input, convert, write output.
	"""
	args = parse_args()

	# validate input extension and resolve default output
	ef_tools.cli_checks.require_extensions(args.input_file, ('.txt',), 'input')
	output_file = args.output_file
	if output_file is None:
		output_file = ef_tools.cli_checks.default_output_path(args.input_file, '.yml')
	ef_tools.cli_checks.require_extensions(output_file, ('.yml', '.yaml'), 'output')

	with open(args.input_file, 'r') as handle:
		contains_mathml = '<math' in handle.read().lower()
	if contains_mathml:
		with qti_package_maker.html_to_image.render_table.TableRenderer() as renderer:
			records = parse_bbq_file(args.input_file, math_renderer=renderer)
			render_record_tables(records, output_file, renderer)
	else:
		records = parse_bbq_file(args.input_file)
		render_record_tables(records, output_file)
	exam_dict = build_exam_dict(records, args.exam_title)
	write_outputs(exam_dict, records, output_file, os.path.basename(args.input_file))

	question_count = ef_tools.question_utils.count_total_questions(exam_dict['sections'])
	print(f"Exam YAML written to {output_file} ({question_count} questions)")


if __name__ == '__main__':
	main()
