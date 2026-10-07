#!/usr/bin/env python3
"""Apply Quiz 1 scoring and page layout; build with make_biostats_quiz1.sh.

DOCX layout reads section headings from the same-basename YAML beside the DOCX.
"""

# Standard Library
import argparse
import pathlib

# PIP3 modules
import docx
import yaml

# Local repo modules
import ef_tools.exam_yaml_writer


#============================================
def parse_args() -> argparse.Namespace:
	"""Read the generated document path and quiz point total."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-i', '--input', dest='input_file', required=True,
		type=pathlib.Path, help='Generated quiz YAML or DOCX (DOCX requires its matching YAML beside it)')
	parser.add_argument('-p', '--points', dest='total_points', type=float, default=9.5,
		help='Quiz point total (YAML only)')
	return parser.parse_args()


#============================================
def main() -> None:
	"""Apply layout to an existing YAML or DOCX without generating new questions."""
	args = parse_args()
	path = args.input_file
	if path.suffix not in ('.yaml', '.docx'):
		raise ValueError('Input must be a quiz YAML or DOCX file.')
	# ASVS 1.5.2: read generated YAML as plain data, never executable objects.
	exam = yaml.safe_load(path.with_suffix('.yaml').read_text(encoding='utf-8'))
	if path.suffix == '.yaml':
		if sum(len(section['questions']) for section in exam['sections']) != 6:
			raise ValueError('Quiz 1 requires all six selected question blocks.')
		exam['total_points'] = args.total_points
		for question in exam['sections'][0]['questions']:
			if 'choices' in question:
				question['layout'] = 1
		ef_tools.exam_yaml_writer.write_exam_yaml(exam, str(path))
	else:
		document = docx.Document(path)
		new_page_titles = [section['chapter'] for section in exam['sections'][1:]]
		for paragraph in document.paragraphs:
			if paragraph.text in new_page_titles:
				paragraph.paragraph_format.page_break_before = True
		document.save(path)


if __name__ == '__main__':
	main()
