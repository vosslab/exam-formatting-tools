#!/usr/bin/env python3
"""E2E: task CSV -> bbq_tasks_to_exam_yaml.py -> yaml_to_exam_docx.py.

Uses the real sibling repos (biology-problems generators, qti-package-maker
renderer with headless Chromium). Run with:

	source source_me.sh && python3 tests/e2e/e2e_bbq_tasks_quiz.py

Exits 1 with the failing check named.
"""

# Standard Library
import os
import re
import sys
import subprocess

# PIP3 modules
import docx
import yaml

# local repo modules (tests/ is on sys.path via the shebang-run cwd)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import file_utils

REPO_ROOT = file_utils.get_repo_root()
sys.path.insert(0, REPO_ROOT)
import ef_tools.question_utils

SETTINGS = os.path.join(REPO_ROOT, 'bbq_settings.yml')
OUT_DIR = os.path.join(REPO_ROOT, 'output_smoke', 'e2e_bbq_tasks')

CSV_ROWS = (
	"subject,topic,script,flags,input,notes\n"
	"genetics,dna_structure,{bp_root}/molecular_biology-problems/chargaff_dna_percent.py,,,\n"
	"genetics,dna_structure,YMCS,,{bp_mcs}/biochemistry/dna_structure.yml,\n"
	"genetics,mendelian,YMATCH,,{bp_match}/inheritance/genetics_terminology.yml,\n"
	"genetics,dna_profiling,{bp_root}/dna_profiling-problems/who_father_html.py,--easy,,\n"
)
KEY_NUMBER_RE = re.compile(r'^(?:Q(\d+)-(\d+)|(\d+))\.')


#============================================
def check(condition: bool, name: str) -> None:
	"""Print a named check result; exit 1 on failure."""
	if condition:
		print(f"OK   {name}")
		return
	print(f"FAIL {name}")
	raise SystemExit(1)


#============================================
def run(command: list) -> subprocess.CompletedProcess:
	"""Run a repo script from REPO_ROOT and echo its last output line."""
	completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
	if completed.returncode != 0:
		print(completed.stdout)
		print(completed.stderr)
		check(False, f"command exit 0: {' '.join(command[:2])}")
	print(completed.stdout.strip().split('\n')[-1])
	return completed


#============================================
def remove_outputs(stem: str) -> None:
	"""Remove a previous run's outputs so the DOCX builder can write."""
	for suffix in ('.yml', '-key.txt', '.docx'):
		path = os.path.join(OUT_DIR, stem + suffix)
		if os.path.isfile(path):
			os.remove(path)
	media_dir = os.path.join(OUT_DIR, f"{stem}_files")
	if os.path.isdir(media_dir):
		for name in os.listdir(media_dir):
			os.remove(os.path.join(media_dir, name))


#============================================
def build(stem: str, mode_flag: str) -> dict:
	"""Run the CSV converter and the DOCX builder for one mode."""
	remove_outputs(stem)
	csv_path = os.path.join(OUT_DIR, 'tasks.csv')
	yaml_path = os.path.join(OUT_DIR, stem + '.yml')
	run([sys.executable, 'launchers/bbq_tasks_to_exam_yaml.py', mode_flag,
		'-i', csv_path, '-s', SETTINGS, '-o', yaml_path])
	run([sys.executable, 'launchers/yaml_to_exam_docx.py', '-i', yaml_path,
		'-o', os.path.join(OUT_DIR, stem + '.docx')])
	with open(yaml_path) as handle:
		exam = yaml.safe_load(handle)
	return exam


#============================================
def check_quiz(exam: dict) -> None:
	"""Quiz-mode checks: images, key numbering, clean DOCX text."""
	questions = []
	for section in exam['sections']:
		questions.extend(section['questions'])
	with_images = [
		q for q in questions
		if any('image' in block for block in q['statement'])]
	check(len(with_images) >= 1, "at least one question carries rendered table images")
	for question in with_images:
		for block in question['statement']:
			if 'image' not in block:
				continue
			path = block['image']
			full = os.path.join(OUT_DIR, path)
			check(os.path.isfile(full) and os.path.getsize(full) > 0, f"png exists: {path}")
	with open(os.path.join(OUT_DIR, 'quiz-key.txt')) as handle:
		key_lines = [line for line in handle if line.strip()]
	check(len(key_lines) == len(questions), "one key line per question block")
	span_total = sum(ef_tools.question_utils.question_span(q) for q in questions)
	last = KEY_NUMBER_RE.match(key_lines[-1])
	highest = int(last.group(2) or last.group(3))
	check(highest == span_total, "highest key number equals total numbered rows")
	check(any(line.startswith('Q') for line in key_lines), "a matching block appears in the key")
	document = docx.Document(os.path.join(OUT_DIR, 'quiz.docx'))
	tagged = [p.text for p in document.paragraphs if re.search(r'<(p|span|table)\b', p.text)]
	check(tagged == [], "DOCX paragraphs carry no raw HTML tags")
	check(len(document.inline_shapes) >= 1, "DOCX embeds at least one image")


#============================================
def check_exam(exam: dict) -> None:
	"""Exam-mode check: the ZipGrade validator reports no issues."""
	completed = subprocess.run(
		[sys.executable, 'launchers/validate_zip_grade_yaml.py', '-i', os.path.join(OUT_DIR, 'exam.yml')],
		cwd=REPO_ROOT, text=True, capture_output=True)
	print(completed.stdout.strip().split('\n')[-1])
	check(completed.returncode == 0, "exam YAML passes the ZipGrade validator")


#============================================
def main() -> None:
	os.makedirs(OUT_DIR, exist_ok=True)
	with open(os.path.join(OUT_DIR, 'tasks.csv'), 'w') as handle:
		handle.write(CSV_ROWS)
	quiz = build('quiz', '-q')
	check_quiz(quiz)
	exam = build('exam', '-e')
	check_exam(exam)
	print("E2E PASS")


if __name__ == '__main__':
	main()
