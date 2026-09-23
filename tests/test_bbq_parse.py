"""Contracts for ef_tools.bbq_parse: answer letters stay correct after shuffling,
tables become images, and key numbering matches printed numbering."""

# Standard Library
import io
import os

# PIP3 modules
import PIL.Image

# local repo modules
import ef_tools.bbq_parse

LETTERS = ef_tools.bbq_parse.LETTERS

MC_LINE = "MC\t<p>c555_9c1d</p> <p>What is 2+2?</p>\t3\tIncorrect\t4\tCorrect\t5\tIncorrect"
MA_LINE = "MA\t<p>Prime numbers?</p>\t2\tCorrect\t3\tCorrect\t4\tIncorrect"
MAT_LINE = "MAT\t<p>Match capitals</p>\tUSA\tWashington\tFrance\tParis\tJapan\tTokyo\tPeru\tLima"
ORD_LINE = "ORD\t<p>Order the steps</p>\tStep 1\tStep 2\tStep 3"
GEL_TABLE = "<table><tr><td bgcolor='#E0E0E0' style='border: 1px solid gray;'>gel</td></tr><tr><td>lane</td></tr></table>"


class FakeRenderer:
	"""Stand-in for TableRenderer that returns a real one-color PNG."""

	def render_table_png(self, table_html: str) -> bytes:
		# The writer autocrops and re-encodes, so this must be a real image.
		buffer = io.BytesIO()
		PIL.Image.new('RGB', (40, 20), color='white').save(buffer, format='PNG')
		return buffer.getvalue()


#============================================
class InspectTableRenderer(FakeRenderer):
	"""Capture table input to prove canvases are resolved before screenshots."""

	def __init__(self) -> None:
		self.seen_html = []

	def render_table_png(self, table_html: str) -> bytes:
		self.seen_html.append(table_html)
		return super().render_table_png(table_html)


#============================================
def test_mc_and_ma_letters_point_at_correct_choices() -> None:
	mc = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	assert mc['answer']['code'] == 'c555_9c1d'
	assert mc['question']['statement'] == [{'text': 'What is 2+2?'}]
	assert [mc['question']['choices'][LETTERS.index(x)] for x in mc['answer']['letters']] == ['4']
	ma = ef_tools.bbq_parse.parse_bbq_line(MA_LINE)
	assert [ma['question']['choices'][LETTERS.index(x)] for x in ma['answer']['letters']] == ['2', '3']


#============================================
def test_mat_letters_map_prompts_back_to_original_matches() -> None:
	record = ef_tools.bbq_parse.parse_bbq_line(MAT_LINE)
	question = record['question']
	assert question['prompts_list'] == ['USA', 'France', 'Japan', 'Peru']
	expected = ['Washington', 'Paris', 'Tokyo', 'Lima']
	for i, letter in enumerate(record['answer']['letters']):
		assert question['choices_list'][LETTERS.index(letter)] == expected[i]


#============================================
def test_ord_becomes_position_blanks_with_letters_in_correct_order() -> None:
	record = ef_tools.bbq_parse.parse_bbq_line(ORD_LINE)
	question = record['question']
	assert question['prompts_list'] == ['Position 1', 'Position 2', 'Position 3']
	for i, letter in enumerate(record['answer']['letters']):
		assert question['choices_list'][LETTERS.index(letter)] == f"Step {i + 1}"


#============================================
def test_skipped_types_and_blank_lines_return_none() -> None:
	assert ef_tools.bbq_parse.parse_bbq_line("NUM\t<p>How many?</p>\t4\t0.1") is None
	assert ef_tools.bbq_parse.parse_bbq_line("FIB\t<p>Fill</p>\tword") is None
	assert ef_tools.bbq_parse.parse_bbq_line("   \t  ") is None


#============================================
def test_tables_in_statement_choice_and_prompt_become_images(tmp_path: object) -> None:
	line = (f"MAT\t<p>ab12_cd34</p><p>Before the diagram.</p>{GEL_TABLE}"
		f"<p>After the diagram.</p>"
		f"\t{GEL_TABLE}\tplain match\tB\t{GEL_TABLE}")
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	statement = record['question']['statement']
	assert statement[0] == {'text': 'Before the diagram.'}
	assert statement[1]['html_table'].startswith('<table')
	assert 'gel' in statement[1]['html_table']
	assert statement[2] == {'text': 'After the diagram.'}
	ef_tools.bbq_parse.render_record_tables(record, FakeRenderer(), str(tmp_path / 'q_files'), 'ab12')
	question = record['question']
	assert question['statement'][1]['image'] == 'q_files/ab12_table_1.png'
	assert 'html_table' in question['statement'][1]
	assert '<table' in question['statement'][1]['html_table']
	assert 'gel' in question['statement'][1]['html_table']
	# prompt 0 was a table; prompts keep their order
	assert question['prompts_list'][0]['image'] == 'q_files/ab12_prompt0_table_1.png'
	assert '<table' in question['prompts_list'][0]['html_table']
	assert question['prompts_list'][1] == 'B'
	# the table match (original index 1) is found through its answer letter
	letter = record['answer']['letters'][1]
	assert question['choices_list'][LETTERS.index(letter)]['image'] == 'q_files/ab12_choice1_table_1.png'
	assert '<table' in question['choices_list'][LETTERS.index(letter)]['html_table']
	assert (tmp_path / 'q_files' / 'ab12_prompt0_table_1.png').stat().st_size > 0


#============================================
def _molecule_canvas(canvas_id: str, smiles: str, width: int, height: int,
			legend: str = '') -> str:
	"""Create the supported moleculelib HTML shape inline."""
	return (
		f'<p><canvas id="{canvas_id}" width="{width}" height="{height}"></canvas></p>'
		'<script>initRDKitModule().then(function(instance){RDKitModule=instance;'
		f'let/* */smiles="{smiles}";let/* */mol=RDKitModule.get_mol(smiles);'
		'let/* */mdetails={};'
		f'mdetails["legend"]="{legend}";'
		'mdetails["explicitMethyl"]=true;'
		f'canvas=document.getElementById("{canvas_id}");'
		'mol.draw_to_canvas_with_highlights(canvas,JSON.stringify(mdetails));'
		'});</script>')


#============================================
def test_statement_canvases_render_as_assets_and_table_inputs_are_static(
			tmp_path: object) -> None:
	"""Standalone canvases become files; table canvases become data URLs."""
	loader = (
		'<script src="https://unpkg.com/@rdkit/rdkit/dist/RDKit_minimal.js">'
		'</script>')
	standalone = _molecule_canvas('canvas_standalone', 'CCO', 120, 80, 'ethanol')
	inside_table = _molecule_canvas('canvas_table', 'CC(=O)O', 96, 72, 'acetate')
	line = (
		'MC\t<p>ab12</p>' + loader + '<p>Before.</p>' + standalone
		+ '<table><tr><td style="border: 1px solid #111;">' + inside_table
		+ '</td></tr></table><p>After.</p>\tA\tCorrect\tB\tIncorrect')
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	statement = record['question']['statement']
	assert statement[0] == {'text': 'Before.'}
	assert statement[1]['image'].startswith('rdkit:')
	assert 'rdkit:' in statement[2]['html_table']
	assert statement[3] == {'text': 'After.'}
	renderer = InspectTableRenderer()
	media_dir = tmp_path / 'quiz_files'
	ef_tools.bbq_parse.render_record_tables(
		record, renderer, str(media_dir), 'ab12')
	image_path = tmp_path / statement[1]['image']
	assert os.path.isfile(image_path)
	with PIL.Image.open(image_path) as image:
		assert image.size == (120, 80)
	assert len(renderer.seen_html) == 1
	assert 'data:image/png;base64,' in renderer.seen_html[0]
	assert '<script' not in renderer.seen_html[0]
	assert 'initRDKitModule' not in renderer.seen_html[0]
	assert 'RDKit_minimal.js' not in renderer.seen_html[0]
	assert os.path.isfile(tmp_path / statement[2]['image'])
	assert 'rendered_images' not in record


#============================================
def test_choice_canvases_become_resolvable_image_choices(tmp_path: object,
			monkeypatch: object) -> None:
	"""RDKit canvases in matching choices render without active scripts."""
	first = _molecule_canvas('canvas_first', 'CCO', 100, 70, 'ethanol')
	second = _molecule_canvas('canvas_second', 'O', 90, 60, 'water')
	line = (
		'MAT\t<p>cd34</p><p>Match each structure.</p>'
		'\tAlcohol\t' + first + '\tWater\t' + second)
	monkeypatch.setattr(ef_tools.bbq_parse.random, 'sample',
		lambda population, count: list(population)[:count])
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	assert all(isinstance(choice, dict) for choice in record['question']['choices_list'])
	assert all('rdkit:' in choice['image']
		for choice in record['question']['choices_list'])
	ef_tools.bbq_parse.render_record_tables(
		record, FakeRenderer(), str(tmp_path / 'match_files'), 'cd34')
	for choice in record['question']['choices_list']:
		image_path = tmp_path / choice['image']
		assert os.path.isfile(image_path)
		with PIL.Image.open(image_path) as image:
			assert image.width in (90, 100)
		assert '<script' not in choice.get('text', '')
	assert 'RDKit_minimal.js' not in str(record['question'])


#============================================
class MathMLRenderer(InspectTableRenderer):
	"""Return equation PNGs while retaining the HTML sent to table screenshots."""

	def __init__(self) -> None:
		super().__init__()
		self.seen_mathml = []

	def render_mathml_png(self, mathml_html: str) -> bytes:
		self.seen_mathml.append(mathml_html)
		buffer = io.BytesIO()
		PIL.Image.new('RGB', (80, 32), color='white').save(buffer, format='PNG')
		return buffer.getvalue()


#============================================
def test_mathml_in_statement_table_and_choice_becomes_static_images(
			tmp_path: object) -> None:
	"""Supported equation markup becomes resolvable PNGs in every field."""
	equation = (
		'<math xmlns="http://www.w3.org/1998/Math/MathML">'
		'<mi>pH</mi><mo>&#8201;</mo><mo>=</mo>'
		'<msub><mi>pK</mi><mi>a</mi></msub><mo>+</mo>'
		'<msub><mo>log</mo><mn>10</mn></msub>'
		'<mfenced><mfrac><mrow>'
		'<msup><mi mathvariant="normal">A</mi><mo>&#8211;</mo></msup>'
		'</mrow><mrow><mi>HA</mi></mrow></mfrac></mfenced>'
		'</math>')
	line = (
		'MC\t<p>ab12</p><p>Choose the equation.</p><p>' + equation + '</p>'
		'<table><tr><td>' + equation + '</td></tr></table>'
		'\t<p>Use ' + equation + ' here.</p>\tCorrect\tOther\tIncorrect')
	renderer = MathMLRenderer()
	record = ef_tools.bbq_parse.parse_bbq_line(line, math_renderer=renderer)
	assert len(renderer.seen_mathml) == 3
	assert all('mfenced' in markup for markup in renderer.seen_mathml)
	assert any(block.get('image', '').startswith('mathml:')
		for block in record['question']['statement'])
	assert any('mathml:' in block.get('html_table', '')
		for block in record['question']['statement'])
	assert record['question']['choices'][0]['text'] == 'Use here.'
	assert record['question']['choices'][0]['image'].startswith('mathml:')

	media_dir = tmp_path / 'quiz_files'
	ef_tools.bbq_parse.render_record_tables(record, renderer, str(media_dir), 'ab12')
	statement_images = [
		block['image'] for block in record['question']['statement']
		if 'html_table' not in block and 'image' in block]
	for image_path in statement_images:
		with PIL.Image.open(tmp_path / image_path) as image:
			assert image.size == (80, 32)
	choice_path = tmp_path / record['question']['choices'][0]['image']
	with PIL.Image.open(choice_path) as image:
		assert image.size == (80, 32)
	table_html = renderer.seen_html[0]
	assert 'data:image/png;base64,' in table_html
	assert '<math' not in table_html
	assert '<script' not in table_html
	assert 'rendered_images' not in record


#============================================
def test_answer_key_numbering_advances_by_span() -> None:
	mc = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	mat = ef_tools.bbq_parse.parse_bbq_line(MAT_LINE)
	key = ef_tools.bbq_parse.format_answer_key(
		[mc['question'], mat['question']],
		[mc['answer'], mat['answer']],
		['chargaff.py', 'yaml_match_to_bbq.py (capitals)'])
	lines = key.strip().split('\n')
	assert len(lines) == 2
	assert lines[0].startswith('1. B   c555_9c1d')
	assert lines[1].startswith('Q2-5. 2=')
