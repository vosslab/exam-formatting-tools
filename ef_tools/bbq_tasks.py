"""Load website-style bptools task CSVs and generate one question per task.

The CSV contract mirrors biology-problems-website/run_bbq_tasks.py so website
task files work unchanged. An optional local ``choice_font`` column selects a
manual font override for text choices on one task:

	subject,topic,script,flags,input,notes,choice_font
	genetics,dna_structure,{bp_root}/molecular_biology-problems/chargaff_dna_percent.py,,,,IBM Plex Sans Condensed
	genetics,mendelian,YMATCH,,{bp_match}/inheritance/genetics_terminology.yml,,

Path aliases ({bp_root}, {bp_match}, ...) and script aliases come from
bbq_settings.yml. A script alias may expand to several scripts; each becomes
its own task. The local quiz settings split YMATCH (matching) from YWHICH
(Which One? MC); the website can retain its dual YMATCH alias. A row with
blank script and blank flags is a separator.
"""

# Standard Library
import os
import csv
import sys
import glob
import shlex
import tempfile
import subprocess

# PIP3 modules
import yaml

# local repo modules
import ef_tools.bbq_parse


# yaml-driven generators whose bare-basename input lives beside the script
INPUT_SCRIPT_BASENAMES = (
	'yaml_match_to_bbq.py',
	'yaml_which_one_mc_to_bbq.py',
	'yaml_make_which_one_multiple_choice.py',
	'yaml_mc_statements_to_bbq.py',
	'yaml_make_match_sets.py',
)
# Anti-cheat wrappers (hidden terms, no-click div) are opt-in flags in
# bptools (`--hidden-terms`, `--noclick-div`), so plain runs already produce
# print-clean text.
# the flag that hands a yaml input file to a generator
INPUT_FLAG = '-y'
# Attempts per task. Generators that exceed five choices do so through fixed
# flags (`-c 6`, `*-6_choices`), so every candidate from them fails exam mode
# and a fast, clear skip is the right outcome; variable-size generators
# (matching sets, ORD) fit within one or two attempts.
MAX_ATTEMPTS = 3
# tail of generator stderr kept in error messages
STDERR_TAIL_CHARS = 2000


#============================================
def load_settings(path: str) -> dict:
	"""Read the website bbq_settings.yml (paths and script_aliases)."""
	with open(path, 'r') as handle:
		settings = yaml.safe_load(handle)
	return settings


#============================================
def apply_aliases(text: str, aliases: dict) -> str:
	"""Replace every `{key}` in text with its alias value."""
	result = text
	for key, value in aliases.items():
		result = result.replace(f"{{{key}}}", value)
	return result


#============================================
def resolve_alias_map(paths: dict) -> dict:
	"""Expand aliases that reference each other, then expand `~`.

	Three passes cover the nesting depth used by the website settings
	(bp_match -> bp_root -> literal path).
	"""
	resolved = dict(paths)
	for _ in range(3):
		for key, value in resolved.items():
			resolved[key] = apply_aliases(value, resolved)
	for key, value in resolved.items():
		resolved[key] = os.path.expanduser(value)
	return resolved


#============================================
def resolve_script_alias(value: str, script_aliases: dict) -> str | list:
	"""Map `NAME` or `@NAME` to its alias (str or list); pass paths through."""
	key = value[1:] if value.startswith('@') else value
	if key in script_aliases:
		return script_aliases[key]
	return value


#============================================
def build_pythonpath(settings: dict) -> str:
	"""PYTHONPATH for generator subprocesses: bp repo root plus the current path.

	bp_root points at `<repo>/problems`; generators import bptools from the
	repo root, so the parent directory goes on the path.
	"""
	paths = resolve_alias_map(settings['paths'])
	bp_root = paths['bp_root']
	if os.path.basename(bp_root) == 'problems':
		bp_root = os.path.dirname(bp_root)
	parts = [os.path.abspath(bp_root)]
	existing = os.environ.get('PYTHONPATH', '')
	for part in existing.split(os.pathsep):
		if part and part not in parts:
			parts.append(part)
	pythonpath = os.pathsep.join(parts)
	return pythonpath


#============================================
def _normalize_path(value: str, aliases: dict, base_root: str) -> str:
	"""Expand aliases and `~`; anchor relative paths at base_root."""
	expanded = os.path.expanduser(apply_aliases(value, aliases))
	if not os.path.isabs(expanded):
		expanded = os.path.join(base_root, expanded)
	normalized = os.path.abspath(expanded)
	return normalized


#============================================
def _resolve_input_path(input_value: str, script_path: str, aliases: dict, base_root: str) -> str:
	"""Resolve the CSV input cell; a bare basename lives beside yaml-driven scripts."""
	if os.path.basename(input_value) == input_value:
		if os.path.basename(script_path) in INPUT_SCRIPT_BASENAMES:
			input_value = os.path.join(os.path.dirname(script_path), input_value)
	input_path = _normalize_path(input_value, aliases, base_root)
	return input_path


#============================================
def _task_label(script_path: str, input_path: str) -> str:
	"""Short name for reports: script basename plus the input stem if any."""
	label = os.path.basename(script_path)
	if input_path:
		input_stem = os.path.splitext(os.path.basename(input_path))[0]
		label = f"{label} ({input_stem})"
	return label


#============================================
def load_tasks(csv_path: str, settings: dict) -> list:
	"""Resolve every CSV row into tasks the way the website runner does.

	Returns:
		List of task dicts, one per resolved script. A non-empty optional
		``choice_font`` value is carried through to the generated question.

	Raises:
		FileNotFoundError: a resolved script path does not exist.
	"""
	aliases = resolve_alias_map(settings['paths'])
	script_aliases = {}
	for key, value in settings['script_aliases'].items():
		if isinstance(value, list):
			script_aliases[key] = [apply_aliases(item, aliases) for item in value]
		else:
			script_aliases[key] = apply_aliases(value, aliases)
	base_root = aliases['bp_root']
	tasks = []
	with open(csv_path, newline='') as handle:
		reader = csv.DictReader(handle)
		for row in reader:
			script = (row['script'] or '').strip()
			flags = (row['flags'] or '').strip()
			input_value = (row['input'] or '').strip()
			topic = (row['topic'] or '').strip()
			choice_font = (row.get('choice_font') or '').strip()
			# separator row
			if not script and not flags:
				continue
			resolved = resolve_script_alias(script, script_aliases)
			script_values = resolved if isinstance(resolved, list) else [resolved]
			base_args = shlex.split(apply_aliases(flags, aliases))
			for script_value in script_values:
				script_path = _normalize_path(script_value, aliases, base_root)
				if not os.path.isfile(script_path):
					raise FileNotFoundError(
						f"{csv_path}:{reader.line_num}: script not found: {script_path}")
				args = list(base_args)
				input_path = ''
				if input_value:
					input_path = _resolve_input_path(input_value, script_path, aliases, base_root)
					args.extend([INPUT_FLAG, input_path])
				task = {
					'script': script_path,
					'args': args,
					'topic': topic,
					'label': _task_label(script_path, input_path),
				}
				if choice_font:
					task['choice_font'] = choice_font
				tasks.append(task)
	return tasks


#============================================
def generate_candidate(task: dict, pythonpath: str) -> str:
	"""Run the generator once and return its single bbq line.

	The generator writes `bbq-*-questions.txt` into its working directory,
	so each run gets a fresh temporary directory.

	Raises:
		RuntimeError: nonzero exit, or the output file is missing/ambiguous.
	"""
	command = [sys.executable, task['script'], *task['args'], '-d', '1', '-x', '1']
	env = dict(os.environ)
	env['PYTHONPATH'] = pythonpath
	with tempfile.TemporaryDirectory() as workdir:
		completed = subprocess.run(
			command, cwd=workdir, env=env, text=True, capture_output=True, check=False)
		if completed.returncode != 0:
			tail = completed.stderr[-STDERR_TAIL_CHARS:]
			raise RuntimeError(f"{task['label']}: exit {completed.returncode}\n{tail}")
		outputs = glob.glob(os.path.join(workdir, 'bbq-*-questions.txt'))
		if len(outputs) != 1:
			names = [os.path.basename(path) for path in outputs]
			raise RuntimeError(f"{task['label']}: expected one bbq output, found {names}")
		with open(outputs[0], 'r') as handle:
			lines = [line for line in handle if line.strip()]
	if not lines:
		raise RuntimeError(f"{task['label']}: generator wrote no questions")
	return lines[0]


#============================================
def generate_question(task: dict, pythonpath: str, reject_fn: object,
		candidate_fn: object = generate_candidate,
		math_renderer: object = None) -> tuple:
	"""Generate candidates until one parses and passes the mode rule.

	Args:
		task: A task dict from load_tasks.
		pythonpath: Value from build_pythonpath.
		reject_fn: Callable(question_dict) -> '' when the question is usable,
			otherwise a short reason (the quiz/exam rule).
		candidate_fn: Callable(task, pythonpath) -> bbq line (test seam).
		math_renderer: Optional renderer for supported MathML equations.

	Returns:
		(record, '') on success, or (None, reason) after MAX_ATTEMPTS
		unusable candidates. A generator crash propagates as RuntimeError.
	"""
	last_reason = ''
	for _ in range(MAX_ATTEMPTS):
		line = candidate_fn(task, pythonpath)
		# an unprintable candidate (e.g. table-drawing matching prompts) is
		# a reason to try again, the same as a skipped type
		try:
			record = ef_tools.bbq_parse.parse_bbq_line(
				line, math_renderer=math_renderer)
		except ef_tools.bbq_parse.UnprintableQuestion as exc:
			last_reason = f"unprintable: {exc}"
			continue
		except ValueError as exc:
			raise ValueError(f"{task['label']}: {exc}") from exc
		if record is None:
			question_type = line.split('\t')[0].strip()
			last_reason = f"skipped type {question_type}"
			continue
		last_reason = reject_fn(record['question'])
		if not last_reason:
			return record, ''
	reason = f"{task['label']}: no usable question in {MAX_ATTEMPTS} attempts ({last_reason})"
	return None, reason
