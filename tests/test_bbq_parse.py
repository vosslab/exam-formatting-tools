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
NUM_LINE = "NUM\t<p>n111</p><p>Calculate distance.</p>\t12.00000000\t0.10000000"
FIB_PLUS_LINE = (
	"FIB_PLUS\t<p>f222</p><p>Distance [AB] and order [order].</p>"
	"\tAB\t12\t\torder\tabc\tcba\t"
)
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
def test_handout_keeps_numeric_and_multi_blank_questions_with_prompt_blanks() -> None:
	"""Handout blanks stay in their authored prompt paragraphs."""
	assert ef_tools.bbq_parse.parse_bbq_line(NUM_LINE) is None
	numeric = ef_tools.bbq_parse.parse_bbq_line(NUM_LINE, handout=True)
	assert numeric['question']['question_type'] == 'NUM'
	assert numeric['question']['statement'][0]['text'].endswith(
		'Calculate distance. Answer: ____________________')
	assert 'answer_line' not in numeric['question']
	assert numeric['answer']['answer_text'] == '12.00000000'
	multi = ef_tools.bbq_parse.parse_bbq_line(FIB_PLUS_LINE, handout=True)
	assert multi['question']['question_type'] == 'FIB_PLUS'
	assert '____________________' in multi['question']['statement'][0]['text']
	assert 'order=abc / cba' in multi['answer']['answer_text']


#============================================
def test_handout_blank_precedes_trailing_hints_and_preserves_an_explicit_blank() -> None:
	"""NUM/FIB blanks target the prompt, without inventing alternate blank syntax."""
	line = (
		'FIB\t<p>f123</p><p>Give the gene name.</p><h6>Hints</h6>'
		'<p>Use the table.</p>\tabc')
	record = ef_tools.bbq_parse.parse_bbq_line(line, handout=True)
	text = record['question']['statement'][0]['text']
	assert 'Give the gene name. Answer: ____________________' in text
	assert '<b>Hints</b>\nUse the table.' in text
	explicit = ef_tools.bbq_parse.parse_bbq_line(
		'FIB\t<p>f456</p><p>Give the gene: ____________________</p>\tabc', handout=True)
	assert explicit['question']['statement'][0]['text'].count('____________________') == 1
	bold_prompt = ef_tools.bbq_parse.parse_bbq_line(
		'NUM\t<p>n789</p><p>Background.</p><h6>Hints</h6><p>Use it.</p>'
		'<h6>Determine the distance</h6>\t12\t0.1', handout=True)
	assert '<b>Determine the distance</b> Answer: ____________________' in (
		bold_prompt['question']['statement'][0]['text'])


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
def test_flex_drawing_panels_are_captured_once_in_authored_order() -> None:
	"""A flex drawing group remains side by side instead of becoming stacked tables."""
	first = '<table><tr><td>first panel</td></tr></table>'
	second = '<table><tr><td>second panel</td></tr></table>'
	line = (
		'MC\t<p>flex12</p><p>Compare the panels.</p>'
		'<div style="display: flex; gap: 16px;"><div>' + first + '</div><div>'
		+ second + '</div></div>\tYes\tCorrect\tNo\tIncorrect')
	renderer = FakeRenderer()
	record = ef_tools.bbq_parse.parse_bbq_line(line, math_renderer=renderer)
	html, targets, _base_url, _label = renderer.calls[0]
	assert len(targets) == 1
	assert html.index('first panel') < html.index('second panel')
	assert 'display: flex' in html
	assert 'html_table' not in str(record['question']['statement'])
	assert record['question']['statement'][1]['image'] == 'rendered:1'


#============================================
def test_authored_question_classes_explain_the_inline_style_requirement() -> None:
	"""BBQ content cannot silently depend on stylesheet-only layout classes."""
	line = 'MC\t<p>class12</p><div class="panels">Question.</div>\tYes\tCorrect'
	with pytest.raises(ValueError, match='cannot use a class attribute; use an inline style'):
		ef_tools.bbq_parse.parse_bbq_line(line)


#============================================
def test_non_flex_layout_preserves_individual_table_fallbacks() -> None:
	"""Only exact inline flex layout groups tables into one browser image."""
	line = (
		'MC\t<p>grid12</p><div style="display: grid;">'
		'<table><tr><td>first</td></tr></table>'
		'<table><tr><td>second</td></tr></table>'
		'</div>\tYes\tCorrect')
	renderer = FakeRenderer()
	record = ef_tools.bbq_parse.parse_bbq_line(line, math_renderer=renderer)
	assert len(renderer.calls[0][1]) == 2
	assert sum('html_table' in block for block in record['question']['statement']) == 2


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
