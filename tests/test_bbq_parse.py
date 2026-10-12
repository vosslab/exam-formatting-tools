"""Contracts for BBQ parsing and complete-context visual capture."""

import io
import os

import PIL.Image
import pytest

import ef_tools.bbq_parse


LETTERS = ef_tools.bbq_parse.LETTERS
MC_LINE = "MC\t<p>c555_9c1d</p> <p>What is 2+2?</p>\t3\tIncorrect\t4\tCorrect\t5\tIncorrect"
MA_LINE = "MA\t<p>Prime numbers?</p>\t2\tCorrect\t3\tCorrect\t4\tIncorrect"
MAT_LINE = "MAT\t<p>Match capitals</p>\tUSA\tWashington\tFrance\tParis\tJapan\tTokyo\tPeru\tLima"
ORD_LINE = "ORD\t<p>Order the steps</p>\tStep 1\tStep 2\tStep 3"
GEL_TABLE = "<table><tr><td bgcolor='#E0E0E0' style='border: 1px solid gray;'>gel</td></tr><tr><td>lane</td></tr></table>"


#============================================
def _png() -> bytes:
	buffer = io.BytesIO()
	PIL.Image.new('RGB', (1200, 600), color='white').save(
		buffer, format='PNG', dpi=(600, 600))
	return buffer.getvalue()


#============================================
class FakeRenderer:
	"""Capture requests without starting Chromium in parser tests."""

	def __init__(self, data: bytes | None = None) -> None:
		self.calls = []
		self.data = _png() if data is None else data

	def render(self, html: str, targets: dict, base_url: str = '',
			label: str = 'HTML') -> dict:
		self.calls.append((html, targets, base_url, label))
		return {selector: self.data for selector in targets}


#============================================
def test_mc_and_ma_letters_point_at_correct_choices() -> None:
	mc = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	assert mc['answer']['code'] == 'c555_9c1d'
	assert mc['question']['statement'] == [{'text': 'What is 2+2?'}]
	assert [mc['question']['choices'][LETTERS.index(x)] for x in mc['answer']['letters']] == ['4']
	ma = ef_tools.bbq_parse.parse_bbq_line(MA_LINE)
	assert [ma['question']['choices'][LETTERS.index(x)] for x in ma['answer']['letters']] == ['2', '3']


#============================================
def test_matching_and_ordering_keys_survive_choice_shuffle() -> None:
	matching = ef_tools.bbq_parse.parse_bbq_line(MAT_LINE)
	question = matching['question']
	assert question['prompts_list'] == ['USA', 'France', 'Japan', 'Peru']
	for index, letter in enumerate(matching['answer']['letters']):
		assert question['choices_list'][LETTERS.index(letter)] == [
			'Washington', 'Paris', 'Tokyo', 'Lima'][index]
	ordered = ef_tools.bbq_parse.parse_bbq_line(ORD_LINE)
	for index, letter in enumerate(ordered['answer']['letters']):
		assert ordered['question']['choices_list'][LETTERS.index(letter)] == f'Step {index + 1}'


#============================================
@pytest.mark.parametrize('extension', ['png', 'svg'])
def test_tables_in_statement_choice_and_prompt_become_images(
		tmp_path: object, extension: str) -> None:
	line = (f"MAT\t<p>ab12_cd34</p><p>Before.</p>{GEL_TABLE}<p>After.</p>"
		f"\t{GEL_TABLE}\tplain match\tB\t{GEL_TABLE}")
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	assert record['question']['statement'][1]['html_table'].startswith('<table')
	data = _png() if extension == 'png' else (
		b'<svg xmlns="http://www.w3.org/2000/svg" width="192px" height="96px"/>')
	renderer = FakeRenderer(data)
	ef_tools.bbq_parse.render_record_tables(record, renderer, str(tmp_path / 'q_files'), 'ab12')
	question = record['question']
	assert question['statement'][1]['image'] == f'q_files/ab12_table_1.{extension}'
	assert question['prompts_list'][0]['image'] == f'q_files/ab12_prompt0_table_1.{extension}'
	letter = record['answer']['letters'][1]
	expected_choice = f'q_files/ab12_choice1_table_1.{extension}'
	assert question['choices_list'][LETTERS.index(letter)]['image'] == expected_choice
	assert (tmp_path / question['statement'][1]['image']).read_bytes() == data


#============================================
def test_renderer_receives_shared_statement_script_for_choice_canvas(tmp_path: object) -> None:
	"""Question fields are captured in one browser document before parsing."""
	line = (
		'MC\t<p>ab12</p><script>window.drawShared = true;</script><p>Look.</p>'
		'\t<canvas id="choice-canvas" width="1200" height="600"></canvas>\tCorrect'
		'\tPlain\tIncorrect')
	renderer = FakeRenderer()
	record = ef_tools.bbq_parse.parse_bbq_line(line, math_renderer=renderer)
	assert len(renderer.calls) == 1
	html, targets, _base_url, label = renderer.calls[0]
	assert 'window.drawShared = true' in html
	assert 'choice-canvas' in html
	assert len(targets) == 1 and label == 'question ab12'
	choice = record['question']['choices'][0]
	assert choice['image'].startswith('rendered:')
	ef_tools.bbq_parse.render_record_tables(
		record, renderer, str(tmp_path / 'quiz_files'), 'ab12')
	assert os.path.isfile(tmp_path / choice['image'])
	assert 'script' not in str(record['question'])


#============================================
def test_answer_key_numbering_advances_by_span() -> None:
	mc = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	mat = ef_tools.bbq_parse.parse_bbq_line(MAT_LINE)
	key = ef_tools.bbq_parse.format_answer_key(
		[mc['question'], mat['question']], [mc['answer'], mat['answer']],
		['chargaff.py', 'yaml_match_to_bbq.py (capitals)'])
	lines = key.strip().split('\n')
	assert lines[0].startswith('1. B   c555_9c1d')
	assert lines[1].startswith('Q2-5. 2=')
