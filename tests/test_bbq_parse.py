"""Contracts for ef_tools.bbq_parse: answer letters stay correct after shuffling,
tables become images, and key numbering matches printed numbering."""

# Standard Library
import io

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
def test_mc_and_ma_letters_point_at_correct_choices() -> None:
	mc = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	assert mc['answer']['code'] == 'c555_9c1d'
	assert mc['question']['statement'] == 'What is 2+2?'
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
	line = (f"MAT\t<p>ab12_cd34</p><p>Match gels</p>{GEL_TABLE}"
		f"\t{GEL_TABLE}\tplain match\tB\t{GEL_TABLE}")
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	assert '<table' not in record['question']['statement']
	ef_tools.bbq_parse.render_record_tables(record, FakeRenderer(), str(tmp_path / 'q_files'), 'ab12')
	question = record['question']
	assert question['images'] == ['q_files/ab12_table_1.png']
	assert len(question['html_tables']) == 1
	assert '<table' in question['html_tables'][0]
	assert 'gel' in question['html_tables'][0]
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
