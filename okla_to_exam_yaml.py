#!/usr/bin/env python3
"""
Convert okla_chrst_bqge format to exam YAML format.

The okla format uses block-based questions separated by blank lines.
MC questions have one asterisk marking the correct answer.
MA questions have multiple asterisks marking correct answers.
FIB (Fill in blank) and MATCH questions are skipped as not bubble-sheet compatible.
"""

# Standard Library
import argparse
import re

# PIP3 modules
import yaml

# Local Repo Modules
import ef_tools.cli_checks


def parse_args():
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description='Convert okla_chrst_bqge format to exam YAML format'
	)
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help='Input file in okla_chrst_bqge format'
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', default=None,
		help='Output YAML file. Defaults to <input-stem>.yml in CWD.'
	)
	parser.add_argument(
		'-t', '--title', dest='title', default='Exam',
		help='Exam title (default: Exam)'
	)
	args = parser.parse_args()
	return args


#============================================


def strip_question_number(text: str) -> str:
	"""
	Remove leading "1. " or "12. " prefix from question header.

	Args:
	    text: Question header line with potential number prefix

	Returns:
	    Question text without the number prefix
	"""
	# Match leading digits followed by dot and optional whitespace
	result = re.sub(r'^\d+\.\s*', '', text.strip())
	return result


#============================================


def strip_choice_prefix(text: str) -> tuple:
	"""
	Remove choice letter prefix and asterisk marker from choice line.

	Strips patterns like "a) ", "*a) ", "b) ", "*b) " and returns
	the cleaned text and whether the choice was marked as correct.

	Args:
	    text: Choice line with letter prefix and optional asterisk

	Returns:
	    Tuple of (cleaned_text, is_correct)
	"""
	# Match optional asterisk, single letter (a-z or A-Z), closing ) or ., and text
	# Require the closing punctuation to avoid false matches on random text
	match = re.match(r'(\*?)([a-zA-Z])[\)\.]?\s*(.+)', text.strip())
	if not match:
		return None, None

	# Only accept if there's a closing ) or . after the letter
	has_closing = re.match(r'(\*?)([a-zA-Z])[\)\.]', text.strip())
	if not has_closing:
		return None, None

	is_correct = bool(match.group(1))
	choice_text = match.group(3).strip()
	return choice_text, is_correct


#============================================


def parse_block(lines: list) -> dict:
	"""
	Parse one question block into a question dict.

	Detects MC vs MA based on number of correct answers.
	Skips FIB and MATCH question types.

	Args:
	    lines: Block lines (already split and stripped)

	Returns:
	    Dict with 'statement' and 'choices' keys, or None if invalid block
	"""
	if not lines:
		return None

	# Get the header line and clean it
	header = lines[0].strip()

	# Skip FIB (Fill in blank) questions
	if header.lower().startswith('blank'):
		return None

	# Skip MATCH questions
	if header.lower().startswith('match'):
		return None

	# Process MC/MA questions (should start with digit)
	if not re.match(r'^\d+\.', header):
		return None

	statement = strip_question_number(header)
	choices = []
	correct_answers = []

	# Parse choice lines
	for line in lines[1:]:
		choice_text, is_correct = strip_choice_prefix(line)
		if choice_text is None:
			continue
		choices.append(choice_text)
		if is_correct:
			correct_answers.append(choice_text)

	# Need at least one choice
	if not choices:
		return None

	question_dict = {
		'statement': statement,
		'choices': choices,
	}

	return question_dict


#============================================


def split_blocks(text: str) -> list:
	"""
	Split text into question blocks separated by blank lines.

	Args:
	    text: Full file content

	Returns:
	    List of block strings
	"""
	blocks = []
	current = []
	for line in text.splitlines():
		if line.strip() == '':
			if current:
				blocks.append('\n'.join(current))
				current = []
		else:
			current.append(line.rstrip())
	if current:
		blocks.append('\n'.join(current))
	return blocks


#============================================


def convert_okla_to_yaml(input_path: str, title: str) -> dict:
	"""
	Read okla format file and convert to exam YAML structure.

	Args:
	    input_path: Path to input file in okla_chrst_bqge format
	    title: Exam title

	Returns:
	    Dict with YAML exam structure (title, date, sections)
	"""
	with open(input_path, 'r', encoding='utf-8') as f:
		content = f.read()

	blocks = split_blocks(content)

	# Parse all questions
	questions = []
	for block in blocks:
		lines = block.strip().split('\n')
		question_dict = parse_block(lines)
		if question_dict:
			questions.append(question_dict)

	# Build YAML structure with single section
	exam_dict = {
		'title': title,
		'date': '2026-04-02',
		'sections': [
			{
				'chapter': 'Questions',
				'questions': questions,
			}
		]
	}

	return exam_dict


#============================================


def main():
	"""
	Main entry point.
	"""
	args = parse_args()

	# validate input extension and resolve default output
	ef_tools.cli_checks.require_extensions(args.input_file, ('.txt',), 'input')
	output_file = args.output_file
	if output_file is None:
		output_file = ef_tools.cli_checks.default_output_path(args.input_file, '.yml')
	ef_tools.cli_checks.require_extensions(output_file, ('.yml', '.yaml'), 'output')

	exam_dict = convert_okla_to_yaml(args.input_file, args.title)

	# Write YAML output
	with open(output_file, 'w', encoding='utf-8') as f:
		yaml.dump(
			exam_dict,
			f,
			default_flow_style=False,
			allow_unicode=True,
			sort_keys=False,
		)

	question_count = sum(len(section.get('questions', [])) for section in exam_dict['sections'])
	print(f"Exam YAML written to {output_file} ({question_count} questions)")


if __name__ == '__main__':
	main()
