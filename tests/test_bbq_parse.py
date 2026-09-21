"""Tests for ef_tools.bbq_parse: bbq lines -> exam questions and answer keys."""

# PIP3 modules
import pytest

# local repo modules
import ef_tools.bbq_parse

LETTERS = ef_tools.bbq_parse.LETTERS

MC_LINE = "MC\t<p>c555_9c1d</p> <p>What is 2+2?</p>\t3\tIncorrect\t4\tCorrect\t5\tIncorrect"
MA_LINE = "MA\t<p>Prime numbers?</p>\t2\tCorrect\t3\tCorrect\t4\tIncorrect"
MAT_LINE = "MAT\t<p>Match capitals</p>\tUSA\tWashington\tFrance\tParis\tJapan\tTokyo\tPeru\tLima"
ORD_LINE = "ORD\t<p>Order the steps</p>\tStep 1\tStep 2\tStep 3"
GEL_TABLE = "<table><tr><td bgcolor='#E0E0E0' style='border: 1px solid gray;'>gel</td></tr><tr><td>lane</td></tr></table>"


#============================================
def test_mc_letter_points_at_correct_choice():
	record = ef_tools.bbq_parse.parse_bbq_line(MC_LINE)
	question = record['question']
	assert question['statement'] == 'What is 2+2?'
	assert record['answer']['code'] == 'c555_9c1d'
	letter = record['answer']['letters'][0]
	assert question['choices'][LETTERS.index(letter)] == '4'


#============================================
def test_ma_letters_point_at_every_correct_choice():
	record = ef_tools.bbq_parse.parse_bbq_line(MA_LINE)
	chosen = [record['question']['choices'][LETTERS.index(x)] for x in record['answer']['letters']]
	assert chosen == ['2', '3']


#============================================
def test_mat_letters_map_prompts_back_to_original_matches():
	record = ef_tools.bbq_parse.parse_bbq_line(MAT_LINE)
	question = record['question']
	assert question['prompts_list'] == ['USA', 'France', 'Japan', 'Peru']
	assert sorted(question['choices_list']) == ['Lima', 'Paris', 'Tokyo', 'Washington']
	expected = ['Washington', 'Paris', 'Tokyo', 'Lima']
	for i, letter in enumerate(record['answer']['letters']):
		assert question['choices_list'][LETTERS.index(letter)] == expected[i]


#============================================
def test_ord_becomes_position_blanks_with_letters_in_correct_order():
	record = ef_tools.bbq_parse.parse_bbq_line(ORD_LINE)
	question = record['question']
	assert question['prompts_list'] == ['Position 1', 'Position 2', 'Position 3']
	for i, letter in enumerate(record['answer']['letters']):
		assert question['choices_list'][LETTERS.index(letter)] == f"Step {i + 1}"


#============================================
def test_skipped_and_blank_lines_return_none():
	assert ef_tools.bbq_parse.parse_bbq_line("NUM\t<p>How many?</p>\t4\t0.1") is None
	assert ef_tools.bbq_parse.parse_bbq_line("FIB\t<p>Fill</p>\tword") is None
	assert ef_tools.bbq_parse.parse_bbq_line("   \t  ") is None


#============================================
def test_unknown_type_raises():
	with pytest.raises(ValueError, match='INVALID'):
		ef_tools.bbq_parse.parse_bbq_line("INVALID\tSome question")


#============================================
def test_statement_tables_are_pulled_and_attached_as_images():
	line = f"MC\t<p>ab12_cd34</p><p>Who?</p>{GEL_TABLE}\tMale 1\tCorrect\tMale 2\tIncorrect"
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	assert len(record['statement_tables']) == 1
	assert '<table' not in record['question']['statement']
	ef_tools.bbq_parse.attach_table_images(record, ['q_files/ab12_cd34_table_1.png'], {})
	assert record['question']['images'] == ['q_files/ab12_cd34_table_1.png']


#============================================
def test_choice_table_becomes_choice_image_after_shuffle():
	line = f"MAT\t<p>Match gels</p>\tA\t{GEL_TABLE}\tB\tplain text"
	record = ef_tools.bbq_parse.parse_bbq_line(line)
	assert list(record['choice_tables']) == [0]
	ef_tools.bbq_parse.attach_table_images(record, [], {0: ['q_files/x_table_1.png']})
	letter_for_a = record['answer']['letters'][0]
	choice = record['question']['choices_list'][LETTERS.index(letter_for_a)]
	assert choice['image'] == 'q_files/x_table_1.png'


#============================================
def test_answer_key_numbering_advances_by_span():
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
