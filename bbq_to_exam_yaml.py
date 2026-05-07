#!/usr/bin/env python3
"""
Convert BBQ text format questions to YAML exam format.

Reads tab-separated BBQ questions and outputs YAML suitable for exam formatting.
Supports MC, MA, MAT, and ORD question types.
"""

# Standard Library
import argparse

# Pip Modules
import yaml

# Local Repo Modules
import ef_tools.cli_checks


#============================================
def parse_args():
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
def parse_mc_line(parts: list) -> dict:
	"""
	Parse MC or MA question from parts list.
	Returns dict with statement and choices (correct/incorrect markers stripped).
	For MC: find single correct answer.
	For MA: find all correct answers.
	Format: MC/MA\tquestion\tchoice1\tstatus1\tchoice2\tstatus2...
	"""
	statement = parts[1].strip()
	# Extract choices at even indices (2, 4, 6, ...) and skip statuses at odd indices (3, 5, 7, ...)
	choices = parts[2::2]

	# Strip whitespace from choices
	choices = [c.strip() for c in choices]

	question_dict = {
		'statement': statement,
		'choices': choices,
	}
	return question_dict


#============================================
def parse_mat_line(parts: list) -> dict:
	"""
	Parse MAT (matching) question from parts list.
	Format: MAT\tquestion\tprompt1\tchoice1\tprompt2\tchoice2...
	Returns dict with statement and table (columns=['Prompt', 'Match'], rows=[...]).
	"""
	statement = parts[1].strip()
	# Extract prompts at even indices (2, 4, 6, ...) and choices at odd indices (3, 5, 7, ...)
	prompts = parts[2::2]
	choices = parts[3::2]

	# Strip whitespace
	prompts = [p.strip() for p in prompts]
	choices = [c.strip() for c in choices]

	# Build rows list where each row is [prompt, choice]
	rows = [[prompts[i], choices[i]] for i in range(len(prompts))]

	question_dict = {
		'statement': statement,
		'table': {
			'columns': ['Prompt', 'Match'],
			'rows': rows,
		},
	}
	return question_dict


#============================================
def parse_ord_line(parts: list) -> dict:
	"""
	Parse ORD (ordering) question from parts list.
	Format: ORD\tquestion\tanswer1\tanswer2\tanswer3...
	Returns dict with statement and choices (ordering info stripped).
	"""
	statement = parts[1].strip()
	# All subsequent parts are answer choices in order
	choices = parts[2:]
	# Strip whitespace from choices
	choices = [c.strip() for c in choices]

	question_dict = {
		'statement': statement,
		'choices': choices,
	}
	return question_dict


#============================================
def parse_bbq_line(line: str) -> dict:
	"""
	Parse one BBQ text line into a question dict.
	Detects question type and delegates to appropriate parser.
	Returns None if line is empty or invalid.
	"""
	line = line.strip()
	# Skip empty lines
	if not line:
		return None

	parts = line.split('\t')
	if not parts:
		return None

	question_type = parts[0].strip().upper()

	if question_type == 'MC':
		return parse_mc_line(parts)
	elif question_type == 'MA':
		return parse_mc_line(parts)
	elif question_type == 'MAT':
		return parse_mat_line(parts)
	elif question_type == 'ORD':
		return parse_ord_line(parts)
	else:
		return None


#============================================
def convert_bbq_to_yaml(input_path: str, title: str) -> dict:
	"""
	Read BBQ text file and convert to exam YAML structure.
	Returns dict with keys: title, date, sections.
	"""
	questions = []

	with open(input_path, 'r') as f:
		for line in f:
			question_dict = parse_bbq_line(line)
			if question_dict:
				questions.append(question_dict)

	# Build YAML structure
	exam_dict = {
		'title': title,
		'date': '2026-04-02',
		'sections': [
			{
				'chapter': 'Questions',
				'questions': questions,
			}
		],
	}
	return exam_dict


#============================================
def main():
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

	# Read and convert
	exam_dict = convert_bbq_to_yaml(args.input_file, args.exam_title)

	# Write output as YAML
	with open(output_file, 'w') as f:
		yaml.dump(exam_dict, f, default_flow_style=False, sort_keys=False)

	question_count = sum(len(section.get('questions', [])) for section in exam_dict['sections'])
	print(f"Exam YAML written to {output_file} ({question_count} questions)")


if __name__ == '__main__':
	main()
