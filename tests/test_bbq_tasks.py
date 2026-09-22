"""Tests for ef_tools.bbq_tasks: website CSV contract and retry generation."""

# Standard Library
import os

# PIP3 modules
import pytest

# local repo modules
import ef_tools.bbq_tasks

# rows copied from biology-problems-website genetics_tasks1.csv
CSV_ROWS = (
	"subject,topic,script,flags,input,notes\n"
	"genetics,genetic_disorders,YMATCH,,{bp_match}/inheritance/genetic_disorders.yml,\n"
	",,,,,\n"
	"genetics,dna_structure,{bp_root}/molecular_biology-problems/complementary_sequences.py,--mc --prime,,\n"
	"genetics,dna_structure,YMCS,,{bp_mcs}/biochemistry/dna_structure.yml,\n"
	"genetics,dna_profiling,{bp_root}/dna_profiling-problems/who_father_html.py,--easy,,\n"
)

SCRIPT_FILES = (
	"problems/matching_sets/yaml_match_to_bbq.py",
	"problems/matching_sets/yaml_which_one_mc_to_bbq.py",
	"problems/multiple_choice_statements/yaml_mc_statements_to_bbq.py",
	"problems/molecular_biology-problems/complementary_sequences.py",
	"problems/dna_profiling-problems/who_father_html.py",
)


#============================================
def _settings(repo_dir: str) -> dict:
	settings = {
		'paths': {
			'bp_root': os.path.join(repo_dir, 'problems'),
			'bp_match': '{bp_root}/matching_sets',
			'bp_mcs': '{bp_root}/multiple_choice_statements',
		},
		'script_aliases': {
			'YMATCH': ['{bp_match}/yaml_match_to_bbq.py', '{bp_match}/yaml_which_one_mc_to_bbq.py'],
			'YMCS': '{bp_mcs}/yaml_mc_statements_to_bbq.py',
		},
	}
	return settings


#============================================
@pytest.fixture
def task_repo(tmp_path: object) -> tuple:
	"""Fake biology-problems checkout with empty generator scripts and a CSV."""
	repo_dir = tmp_path / 'biology-problems'
	for relative in SCRIPT_FILES:
		path = repo_dir / relative
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text('')
	csv_path = tmp_path / 'tasks.csv'
	csv_path.write_text(CSV_ROWS)
	return str(repo_dir), str(csv_path)


#============================================
def test_load_tasks_expands_list_alias_and_skips_separator(task_repo: tuple) -> None:
	repo_dir, csv_path = task_repo
	tasks = ef_tools.bbq_tasks.load_tasks(csv_path, _settings(repo_dir))
	labels = [task['label'] for task in tasks]
	assert labels == [
		'yaml_match_to_bbq.py (genetic_disorders)',
		'yaml_which_one_mc_to_bbq.py (genetic_disorders)',
		'complementary_sequences.py',
		'yaml_mc_statements_to_bbq.py (dna_structure)',
		'who_father_html.py',
	]


#============================================
def test_load_tasks_resolves_input_and_flags(task_repo: tuple) -> None:
	repo_dir, csv_path = task_repo
	tasks = ef_tools.bbq_tasks.load_tasks(csv_path, _settings(repo_dir))
	ymcs = tasks[3]
	expected_input = os.path.join(
		repo_dir, 'problems', 'multiple_choice_statements', 'biochemistry', 'dna_structure.yml')
	assert ymcs['args'] == ['-y', expected_input]
	assert tasks[2]['args'] == ['--mc', '--prime']
	assert tasks[4]['topic'] == 'dna_profiling'


#============================================
def test_load_tasks_missing_script_names_csv_line(task_repo: tuple) -> None:
	repo_dir, csv_path = task_repo
	with open(csv_path, 'a') as handle:
		handle.write("genetics,x,{bp_root}/nope/missing.py,,,\n")
	with pytest.raises(FileNotFoundError, match=r'tasks.csv:7'):
		ef_tools.bbq_tasks.load_tasks(csv_path, _settings(repo_dir))


#============================================
def test_build_pythonpath_uses_repo_root_above_problems(task_repo: tuple, monkeypatch: object) -> None:
	repo_dir, _ = task_repo
	monkeypatch.setenv('PYTHONPATH', '/somewhere/else')
	pythonpath = ef_tools.bbq_tasks.build_pythonpath(_settings(repo_dir))
	assert pythonpath.split(os.pathsep) == [repo_dir, '/somewhere/else']


#============================================
def _no_reject(question: dict) -> str:
	return ''


#============================================
def test_generate_question_retries_past_skipped_type() -> None:
	lines = iter(["NUM\t<p>How many?</p>\t4\t0", "MC\t<p>Pick</p>\ta\tCorrect\tb\tIncorrect"])

	def fake_candidate(task: dict, pythonpath: str) -> str:
		return next(lines)

	task = {'script': 'x.py', 'args': [], 'topic': '', 'label': 'x.py'}
	record, reason = ef_tools.bbq_tasks.generate_question(
		task, '', _no_reject, candidate_fn=fake_candidate)
	assert reason == ''
	assert record['question']['choices'] == ['a', 'b']


#============================================
def test_generate_question_retries_past_unprintable_candidate() -> None:
	gel = "<table><tr><td bgcolor='#eee'>gel</td></tr><tr><td>lane</td></tr></table>"
	# a choice holding two sibling tables has no exam YAML form
	lines = iter([f"MC\t<p>Pick</p>\t{gel}{gel}\tCorrect\tb\tIncorrect",
		"MC\t<p>Pick</p>\ta\tCorrect\tb\tIncorrect"])

	def fake_candidate(task: dict, pythonpath: str) -> str:
		return next(lines)

	task = {'script': 'x.py', 'args': [], 'topic': '', 'label': 'x.py'}
	record, reason = ef_tools.bbq_tasks.generate_question(
		task, '', _no_reject, candidate_fn=fake_candidate)
	assert reason == '' and 'choices' in record['question']


#============================================
def test_generate_question_gives_up_with_labelled_reason() -> None:
	def fake_candidate(task: dict, pythonpath: str) -> str:
		return "FIB\t<p>Fill</p>\tword"

	task = {'script': 'fib.py', 'args': [], 'topic': '', 'label': 'fib.py'}
	record, reason = ef_tools.bbq_tasks.generate_question(
		task, '', _no_reject, candidate_fn=fake_candidate)
	assert record is None
	assert reason.startswith('fib.py: no usable question')
	assert 'skipped type FIB' in reason
