"""Protect a synthetic task-CSV-to-YAML-to-DOCX workflow."""

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
class EmptyTableRenderer:
	"""Stand in for the renderer when the captured tasks contain no tables."""

	def __enter__(self) -> object:
		return self

	def __exit__(self, exc_type: object, exc_value: object,
			traceback: object) -> bool:
		return False

	def render_mathml_png(self, mathml_html: str) -> bytes:
		buffer = io.BytesIO()
		PIL.Image.new('RGB', (72, 28), color='white').save(buffer, format='PNG')
		return buffer.getvalue()


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
		'subject,topic,script,flags,input,notes,choice_font\n'
		'genetics,genetic_disorders,YMATCH,,,,\n'
		'genetics,genetic_disorders,YWHICH,,,,IBM Plex Sans Condensed\n',
		encoding='utf-8')
	settings_path = tmp_path / 'settings.yml'
	settings_path.write_text(yaml.safe_dump({
		'paths': {'bp_root': str(problem_root)},
		'script_aliases': {
			'YMATCH': str(matching_script),
			'YWHICH': str(which_script),
		},
	}), encoding='utf-8')

	lines = {
		'yaml_match_to_bbq.py': (
			'MAT\t<p>Match the terms.</p>\tFirst prompt\tFirst answer'
			'\tSecond prompt\tSecond answer'),
		'yaml_which_one_mc_to_bbq.py': (
			'MC\t<p>Which statement is correct?</p>'
			'\tCorrect choice\tCorrect\tOther choice\tIncorrect'),
	}

	def fake_generate_question(task: dict, pythonpath: str,
			reject_fn: object, math_renderer: object = None) -> tuple:
		line = lines[pathlib.Path(task['script']).name]
		record = ef_tools.bbq_parse.parse_bbq_line(
			line, math_renderer=math_renderer)
		return record, ''

	class_renderer = bbq_tasks_to_exam_yaml.qti_package_maker.html_to_image.render_table
	monkeypatch.setattr(class_renderer, 'TableRenderer', EmptyTableRenderer)
	monkeypatch.setattr(
		ef_tools.bbq_tasks, 'generate_question', fake_generate_question)
	monkeypatch.setattr(
		ef_tools.bbq_parse.random, 'sample',
		lambda population, count: list(population)[:count])

	yaml_path = tmp_path / 'quiz.yml'
	monkeypatch.setattr(sys, 'argv', [
		'bbq_tasks_to_exam_yaml.py', '-i', str(task_csv), '-s',
		str(settings_path), '-o', str(yaml_path), '--quiz', '--title',
		'Synthetic task quiz'])
	bbq_tasks_to_exam_yaml.main()

	exam_data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
	questions = exam_data['sections'][0]['questions']
	assert exam_data['title'] == 'Synthetic task quiz'
	assert exam_data['sections'][0]['chapter'] == 'Genetic disorders'
	assert len(questions) == 2
	assert questions[0]['prompts_list'] == [
		'First prompt', 'Second prompt']
	assert questions[1]['choices'] == ['Correct choice', 'Other choice']
	assert questions[1]['choice_font'] == 'IBM Plex Sans Condensed'
	answer_key = yaml_path.with_name('quiz-key.txt').read_text(encoding='utf-8')
	assert 'Q1-2. 1=A 2=B' in answer_key
	assert '3. A' in answer_key

	docx_path = tmp_path / 'quiz.docx'
	yaml_to_exam_docx.build_document(
		exam_data, str(docx_path), base_dir=str(tmp_path))
	document = docx.Document(docx_path)
	paragraph_text = [paragraph.text for paragraph in document.paragraphs]
	assert any('Match the terms.' in text for text in paragraph_text)
	assert any('First prompt' in text for text in paragraph_text)
	assert any('Which statement is correct?' in text for text in paragraph_text)
	assert any('Correct choice' in text for text in paragraph_text)
	choice_paragraph = next(
		paragraph for paragraph in document.paragraphs
		if 'Correct choice' in paragraph.text)
	assert any(
		run.font.name == 'IBM Plex Sans Condensed'
		for run in choice_paragraph.runs if 'Correct choice' in run.text)
	assert all('<p>' not in text for text in paragraph_text)


#============================================
def test_task_collector_passes_renderer_for_mathml_choices(
			tmp_path: pathlib.Path, monkeypatch: object) -> None:
	"""Task-imported MathML choices are saved as exam-relative PNG assets."""
	equation = (
		'<math xmlns="http://www.w3.org/1998/Math/MathML">'
		'<mi>pH</mi><mo>=</mo><mfenced><mfrac>'
		'<mrow><mi>A</mi></mrow><mrow><mi>HA</mi></mrow>'
		'</mfrac></mfenced></math>')
	line = (
		'MC\t<p>ef90</p><p>Pick the correct equation.</p>'
		'\t' + equation + '\tCorrect\tOther\tIncorrect')

	def fake_generate_question(task: dict, pythonpath: str,
			reject_fn: object, math_renderer: object = None) -> tuple:
		record = ef_tools.bbq_parse.parse_bbq_line(
			line, math_renderer=math_renderer)
		return record, ''

	monkeypatch.setattr(
		bbq_tasks_to_exam_yaml.qti_package_maker.html_to_image.render_table,
		'TableRenderer', EmptyTableRenderer)
	monkeypatch.setattr(
		ef_tools.bbq_tasks, 'generate_question', fake_generate_question)
	task = {'label': 'Henderson-Hasselbalch.py', 'topic': 'buffers'}
	media_dir = tmp_path / 'exam_files'
	sections, answers, sources, skipped = bbq_tasks_to_exam_yaml.collect_questions(
		[task], '', lambda question: '', str(media_dir))
	question = sections[0]['questions'][0]
	image_path = question['choices'][0]['image']
	assert image_path.startswith('exam_files/')
	with PIL.Image.open(tmp_path / image_path) as image:
		assert image.size == (72, 28)
	assert answers[0]['code'] == 'ef90'
	assert sources == ['Henderson-Hasselbalch.py']
	assert skipped == []


#============================================
def test_legacy_bbq_importer_renders_mathml_choice_asset(
			tmp_path: pathlib.Path, monkeypatch: object) -> None:
	"""The legacy text-file entry point saves equations through the same path."""
	equation = (
		'<math xmlns="http://www.w3.org/1998/Math/MathML">'
		'<mi>pH</mi><mo>=</mo><mfenced><mfrac>'
		'<mrow><mi>A</mi></mrow><mrow><mi>HA</mi></mrow>'
		'</mfrac></mfenced></math>')
	input_path = tmp_path / 'equation.txt'
	input_path.write_text(
		'MC\t<p>ef90</p><p>Pick the equation.</p>\t'
		+ equation + '\tCorrect\tOther\tIncorrect', encoding='utf-8')
	yaml_path = tmp_path / 'legacy.yml'
	monkeypatch.setattr(
		bbq_to_exam_yaml.qti_package_maker.html_to_image.render_table,
		'TableRenderer', EmptyTableRenderer)
	monkeypatch.setattr(sys, 'argv', [
		'bbq_to_exam_yaml.py', '-i', str(input_path), '-o', str(yaml_path)])
	bbq_to_exam_yaml.main()
	exam_data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
	image_path = exam_data['sections'][0]['questions'][0]['choices'][0]['image']
	with PIL.Image.open(tmp_path / image_path) as image:
		assert image.size == (72, 28)
