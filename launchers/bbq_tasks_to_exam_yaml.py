#!/usr/bin/env python3
"""Build exam YAML from a website-style bptools task CSV: one question per task.

Each resolved task runs its generator until one usable question appears, then
contributes that question. List-valued aliases create one task per script.
The local settings choose YMATCH for Matching and YWHICH for Which One? MC.
Quiz mode accepts MC, MA, MAT, and ORD of any size; exam mode keeps only
questions that fit a ZipGrade A-E bubble sheet. Drawing tables are rendered
to `<stem>_files/*.png`, and `<stem>-key.txt` holds the answers.
Tasks whose generator only emits skipped types (NUM, FIB, FIB_PLUS) or never
fits the mode are reported to stderr and left out.

Then run yaml_to_exam_docx.py on the YAML.
"""

# Standard Library
import os
import sys
import argparse
import datetime

# local repo modules
import ef_tools.bbq_html
import ef_tools.bbq_parse
import ef_tools.bbq_tasks
import ef_tools.zip_grade
import ef_tools.cli_checks
import ef_tools.question_utils
import ef_tools.exam_yaml_writer
import qti_package_maker.html_to_image.render_table

# repo-root bbq_settings.yml mirrors the website's aliases
DEFAULT_SETTINGS_FILE = os.path.join(
	os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bbq_settings.yml')


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Generate exam YAML with one question per bptools task"
	)
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help="Task CSV (subject,topic,script,flags,input,notes)"
	)
	parser.add_argument(
		'-s', '--settings', dest='settings_file', default=DEFAULT_SETTINGS_FILE,
		help="bbq_settings.yml with paths and script_aliases "
			"(default: the repo's bbq_settings.yml; the website copy also works)"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', default=None,
		help="Output YAML exam file. Defaults to <input-stem>.yml in CWD."
	)
	parser.add_argument(
		'-t', '--title', dest='exam_title', default=None,
		help="Exam title (default: Quiz or Exam by mode)"
	)
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument(
		'-e', '--exam', dest='mode', action='store_const', const='exam',
		help="Exam mode: keep only ZipGrade A-E compatible questions"
	)
	mode_group.add_argument(
		'-q', '--quiz', dest='mode', action='store_const', const='quiz',
		help="Quiz mode: any MC/MA/MAT/ORD question (default)"
	)
	parser.set_defaults(mode='quiz')
	args = parser.parse_args()
	return args


#============================================
def reject_quiz(question: dict) -> str:
	"""Quiz mode: every parsed question is printable."""
	return ''


#============================================
def reject_exam(question: dict) -> str:
	"""Exam mode: the ZipGrade A-E rules decide; '' means usable."""
	severity, _rule_id, message = ef_tools.zip_grade.classify_question(question)
	if severity is ef_tools.zip_grade.Severity.OK:
		return ''
	return message


#============================================
def chapter_label(topic: str) -> str:
	"""Turn a CSV topic such as dna_structure into a chapter heading."""
	label = topic.replace('_', ' ').capitalize()
	return label




#============================================
def collect_questions(tasks: list, pythonpath: str, reject_fn: object, media_dir: str) -> tuple:
	"""Generate one question per task.

	Returns:
		(sections, answers, sources, skipped): exam YAML sections grouped by
		topic, plus parallel answer and source lists, plus skip reasons.
	"""
	sections = []
	answers = []
	sources = []
	skipped = []
	current_topic = None
	with qti_package_maker.html_to_image.render_table.TableRenderer() as renderer:
		for index, task in enumerate(tasks, start=1):
			print(f"[{index}/{len(tasks)}] {task['label']}", file=sys.stderr)
			record, reason = ef_tools.bbq_tasks.generate_question(task, pythonpath, reject_fn)
			if record is None:
				skipped.append(reason)
				continue
			ef_tools.bbq_parse.render_record_tables(
				record, renderer, media_dir, record['answer']['code'])
			# a new chapter section starts whenever the topic changes
			if task['topic'] != current_topic:
				current_topic = task['topic']
				section = {'questions': []}
				if current_topic:
					section = {'chapter': chapter_label(current_topic), 'questions': []}
				sections.append(section)
			sections[-1]['questions'].append(record['question'])
			answers.append(record['answer'])
			sources.append(task['label'])
	return sections, answers, sources, skipped


#============================================
def write_outputs(exam_dict: dict, answers: list, sources: list, output_file: str) -> None:
	"""Write the exam YAML and its sibling answer key."""
	ef_tools.exam_yaml_writer.write_exam_yaml(exam_dict, output_file)
	questions = []
	for section in exam_dict['sections']:
		questions.extend(section['questions'])
	key_text = ef_tools.bbq_parse.format_answer_key(questions, answers, sources)
	key_path = os.path.splitext(output_file)[0] + '-key.txt'
	with open(key_path, 'w') as handle:
		handle.write(key_text)


#============================================
def main() -> None:
	"""Main entry point."""
	args = parse_args()
	ef_tools.cli_checks.require_extensions(args.input_file, ('.csv',), 'input')
	output_file = args.output_file
	if output_file is None:
		output_file = ef_tools.cli_checks.default_output_path(args.input_file, '.yml')
	ef_tools.cli_checks.require_extensions(output_file, ('.yml', '.yaml'), 'output')
	if args.mode == 'exam':
		reject_fn = reject_exam
		default_title = 'Exam'
	else:
		reject_fn = reject_quiz
		default_title = 'Quiz'
	title = args.exam_title if args.exam_title is not None else default_title

	settings = ef_tools.bbq_tasks.load_settings(args.settings_file)
	tasks = ef_tools.bbq_tasks.load_tasks(args.input_file, settings)
	pythonpath = ef_tools.bbq_tasks.build_pythonpath(settings)
	stem = os.path.splitext(os.path.basename(output_file))[0]
	media_dir = os.path.join(os.path.dirname(os.path.abspath(output_file)), f"{stem}_files")

	sections, answers, sources, skipped = collect_questions(tasks, pythonpath, reject_fn, media_dir)
	if not answers:
		raise ValueError(f"no usable questions from {len(tasks)} tasks")
	exam_dict = {
		'title': title,
		'date': datetime.date.today().isoformat(),
		'sections': sections,
	}
	write_outputs(exam_dict, answers, sources, output_file)

	for reason in skipped:
		print(f"SKIPPED {reason}", file=sys.stderr)
	question_count = ef_tools.question_utils.count_total_questions(sections)
	print(f"Exam YAML written to {output_file} "
		f"({question_count} questions, {len(skipped)} tasks skipped)")


#============================================
if __name__ == '__main__':
	main()
