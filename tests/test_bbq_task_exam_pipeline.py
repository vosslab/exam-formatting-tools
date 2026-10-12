"""Protect synthetic BBQ-to-YAML workflows without QPM rendering."""

import io
import pathlib
import sys

import docx
import PIL.Image
import yaml

import bbq_to_exam_yaml
import bbq_tasks_to_exam_yaml
import ef_tools.bbq_parse
import ef_tools.bbq_tasks
import yaml_to_exam_docx


#============================================
class FakeRenderer:
	"""Context-manager renderer double for converter integration tests."""

	def __init__(self) -> None:
		self.calls = []

	def __enter__(self) -> 'FakeRenderer':
		return self

	def __exit__(self, exc_type: object, exc_value: object,
			traceback: object) -> bool:
		return False

	def render(self, html: str, targets: dict, base_url: str = '',
			label: str = 'HTML') -> dict:
		self.calls.append((html, targets, base_url, label))
		buffer = io.BytesIO()
		PIL.Image.new('RGB', (1200, 600), color='white').save(
			buffer, format='PNG', dpi=(600, 600))
		return {selector: buffer.getvalue() for selector in targets}


#============================================
def test_task_csv_aliases_reach_exam_yaml_and_docx(
		tmp_path: pathlib.Path, monkeypatch: object) -> None:
	"""YMATCH and YWHICH each become one rendered question from a fake bank."""
	problem_root = tmp_path / 'biology-problems' / 'problems'
	matching_script = problem_root / 'matching_sets' / 'yaml_match_to_bbq.py'
	which_script = problem_root / 'matching_sets' / 'yaml_which_one_mc_to_bbq.py'
	matching_script.parent.mkdir(parents=True)
	matching_script.write_text('# synthetic generator')
	which_script.write_text('# synthetic generator')
	task_csv = tmp_path / 'tasks.csv'
	task_csv.write_text(
		'subject,topic,script,flags,input,notes,choice_font,layout\n'
		'genetics,genetic_disorders,YMATCH,,,,,\n'
		'genetics,genetic_disorders,YWHICH,,,,IBM Plex Sans Condensed,1\n',
		encoding='utf-8')
	settings_path = tmp_path / 'settings.yml'
	settings_path.write_text(yaml.safe_dump({
		'paths': {'bp_root': str(problem_root)},
		'script_aliases': {'YMATCH': str(matching_script), 'YWHICH': str(which_script)},
	}), encoding='utf-8')
	lines = {
		'yaml_match_to_bbq.py': 'MAT\t<p>Match the terms.</p>\tFirst prompt\tFirst answer\tSecond prompt\tSecond answer',
		'yaml_which_one_mc_to_bbq.py': 'MC\t<p>Which statement is correct?</p>\tCorrect choice\tCorrect\tOther choice\tIncorrect',
	}
	def fake_generate_question(task: dict, pythonpath: str, reject_fn: object,
			math_renderer: object = None) -> tuple:
		return ef_tools.bbq_parse.parse_bbq_line(lines[pathlib.Path(task['script']).name], math_renderer), ''
	renderer = FakeRenderer()
	monkeypatch.setattr(bbq_tasks_to_exam_yaml.ef_tools.html_renderer,
		'HtmlRenderer', lambda: renderer)
	monkeypatch.setattr(ef_tools.bbq_tasks, 'generate_question', fake_generate_question)
	monkeypatch.setattr(ef_tools.bbq_parse.random, 'sample',
		lambda population, count: list(population)[:count])
	yaml_path = tmp_path / 'quiz.yml'
	monkeypatch.setattr(sys, 'argv', [
		'bbq_tasks_to_exam_yaml.py', '-i', str(task_csv), '-s', str(settings_path),
		'-o', str(yaml_path), '--quiz', '--title', 'Synthetic task quiz', '--points', '2.5'])
	bbq_tasks_to_exam_yaml.main()
	exam_data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
	questions = exam_data['sections'][0]['questions']
	assert exam_data['total_points'] == 2.5
	assert questions[0]['prompts_list'] == ['First prompt', 'Second prompt']
	assert questions[1]['choices'] == ['Correct choice', 'Other choice']
	assert questions[1]['choice_font'] == 'IBM Plex Sans Condensed'
	docx_path = tmp_path / 'quiz.docx'
	yaml_to_exam_docx.build_document(exam_data, str(docx_path), base_dir=str(tmp_path))
	assert any('Match the terms.' in paragraph.text for paragraph in docx.Document(docx_path).paragraphs)


#============================================
def test_both_bbq_entry_points_use_native_renderer_for_visual_media(
		tmp_path: pathlib.Path, monkeypatch: object) -> None:
	"""Task CSV and saved BBQ input both save native-renderer PNG captures."""
	line = ('MC\t<p>ef90</p><p>Choose.</p>'
		'\t<table><tr><td>diagram</td></tr></table>\tCorrect\tOther\tIncorrect')
	renderer = FakeRenderer()
	def fake_generate_question(task: dict, pythonpath: str, reject_fn: object,
			math_renderer: object = None) -> tuple:
		return ef_tools.bbq_parse.parse_bbq_line(line, math_renderer), ''
	monkeypatch.setattr(bbq_tasks_to_exam_yaml.ef_tools.html_renderer,
		'HtmlRenderer', lambda: renderer)
	monkeypatch.setattr(ef_tools.bbq_tasks, 'generate_question', fake_generate_question)
	sections, _answers, _sources, skipped = bbq_tasks_to_exam_yaml.collect_questions(
		[{'label': 'diagram.py', 'topic': 'drawings'}], '', lambda question: '',
		str(tmp_path / 'task_files'))
	choice_path = sections[0]['questions'][0]['choices'][0]['image']
	with PIL.Image.open(tmp_path / choice_path) as image:
		assert abs(image.info['dpi'][0] - 600) < 0.1
	assert skipped == []
	input_path = tmp_path / 'saved.txt'
	input_path.write_text(line, encoding='utf-8')
	yaml_path = tmp_path / 'saved.yml'
	monkeypatch.setattr(bbq_to_exam_yaml.ef_tools.html_renderer,
		'HtmlRenderer', lambda: renderer)
	monkeypatch.setattr(sys, 'argv', ['bbq_to_exam_yaml.py', '-i', str(input_path), '-o', str(yaml_path)])
	bbq_to_exam_yaml.main()
	exam_data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
	image_path = exam_data['sections'][0]['questions'][0]['choices'][0]['image']
	with PIL.Image.open(tmp_path / image_path) as image:
		assert abs(image.info['dpi'][0] - 600) < 0.1
	assert len(renderer.calls) == 2
