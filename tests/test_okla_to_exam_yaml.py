"""
Tests for okla_to_exam_yaml.py
"""

# PIP3 modules
import yaml

# local repo modules
import okla_to_exam_yaml


def test_strip_question_number():
	"""Test removal of question number prefix."""
	assert okla_to_exam_yaml.strip_question_number('1. Question text?') == 'Question text?'
	assert okla_to_exam_yaml.strip_question_number('12. What is this?') == 'What is this?'
	assert okla_to_exam_yaml.strip_question_number('100. Complex question?') == 'Complex question?'
	assert okla_to_exam_yaml.strip_question_number('Question with no number') == 'Question with no number'


def test_strip_choice_prefix_simple():
	"""Test removing choice letter prefix without asterisk."""
	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('a) First choice')
	assert text == 'First choice'
	assert is_correct == False

	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('b) Second choice')
	assert text == 'Second choice'
	assert is_correct == False


def test_strip_choice_prefix_with_asterisk():
	"""Test removing choice prefix with asterisk (correct answer)."""
	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('*a) Correct choice')
	assert text == 'Correct choice'
	assert is_correct == True

	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('*c) Also correct')
	assert text == 'Also correct'
	assert is_correct == True


def test_strip_choice_prefix_with_dot():
	"""Test choice prefix with dot instead of parenthesis."""
	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('a. Choice text')
	assert text == 'Choice text'
	assert is_correct == False

	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('*b. Correct choice')
	assert text == 'Correct choice'
	assert is_correct == True


def test_strip_choice_prefix_whitespace():
	"""Test handling extra whitespace."""
	text, is_correct = okla_to_exam_yaml.strip_choice_prefix('  a)   Choice with spaces  ')
	assert text == 'Choice with spaces'
	assert is_correct == False


def test_parse_block_mc_question():
	"""Test parsing a multiple choice question."""
	lines = [
		'1. What is the answer?',
		'a) Wrong',
		'*b) Correct',
		'c) Wrong',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is not None
	assert result['statement'] == 'What is the answer?'
	assert result['choices'] == ['Wrong', 'Correct', 'Wrong']


def test_parse_block_ma_question():
	"""Test parsing a multiple answer question."""
	lines = [
		'2. Select all that apply:',
		'*a) First correct',
		'*b) Second correct',
		'c) Wrong',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is not None
	assert result['statement'] == 'Select all that apply:'
	assert result['choices'] == ['First correct', 'Second correct', 'Wrong']


def test_parse_block_skips_fib():
	"""Test that FIB questions are skipped."""
	lines = [
		'BLANK 1. What is blank?',
		'a) Answer 1',
		'b) Answer 2',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is None


def test_parse_block_skips_match():
	"""Test that MATCH questions are skipped."""
	lines = [
		'MATCH 1. Match items:',
		'a) Item 1 / Match 1',
		'b) Item 2 / Match 2',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is None


def test_parse_block_no_number_prefix():
	"""Test that blocks without number prefix are skipped."""
	lines = [
		'No number here?',
		'a) Choice 1',
		'b) Choice 2',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is None


def test_parse_block_empty_choices():
	"""Test that block with no valid choices returns None."""
	lines = [
		'1. Question?',
		'Invalid line format',
	]
	result = okla_to_exam_yaml.parse_block(lines)
	assert result is None


def test_split_blocks():
	"""Test splitting content into blocks by blank lines."""
	content = """1. First question?
a) Option 1
*b) Option 2

2. Second question?
*a) Option A
b) Option B

3. Third question?
*c) Option C"""

	blocks = okla_to_exam_yaml.split_blocks(content)
	assert len(blocks) == 3
	assert blocks[0].startswith('1. First question?')
	assert blocks[1].startswith('2. Second question?')
	assert blocks[2].startswith('3. Third question?')


def test_split_blocks_leading_trailing_blank():
	"""Test that leading/trailing blank lines don't create empty blocks."""
	content = """
1. Question?
*a) Answer

"""
	blocks = okla_to_exam_yaml.split_blocks(content)
	assert len(blocks) == 1


def test_convert_okla_to_yaml(tmp_path):
	"""Test full conversion from okla format to YAML."""
	# Create a test input file
	input_content = """1. What is 2+2?
a) 3
*b) 4
c) 5

2. Which are primary colors?
*a) Red
*b) Blue
c) Green
d) Yellow
"""

	input_file = tmp_path / 'test_input.txt'
	input_file.write_text(input_content, encoding='utf-8')

	result = okla_to_exam_yaml.convert_okla_to_yaml(str(input_file), 'Test Exam')

	assert result['title'] == 'Test Exam'
	assert 'date' in result
	assert len(result['sections']) == 1
	assert result['sections'][0]['chapter'] == 'Questions'
	assert len(result['sections'][0]['questions']) == 2

	q1 = result['sections'][0]['questions'][0]
	assert q1['statement'] == 'What is 2+2?'
	assert q1['choices'] == ['3', '4', '5']

	q2 = result['sections'][0]['questions'][1]
	assert q2['statement'] == 'Which are primary colors?'
	assert q2['choices'] == ['Red', 'Blue', 'Green', 'Yellow']


def test_convert_okla_to_yaml_skips_fib_and_match(tmp_path):
	"""Test that FIB and MATCH questions are skipped during conversion."""
	input_content = """1. Normal MC question?
*a) Correct
b) Wrong

BLANK 1. Fill in blank:
a) Answer 1
b) Answer 2

2. Another MC question?
a) Option 1
*b) Option 2

MATCH 1. Match these:
a) A / 1
b) B / 2
"""

	input_file = tmp_path / 'test_skip.txt'
	input_file.write_text(input_content, encoding='utf-8')

	result = okla_to_exam_yaml.convert_okla_to_yaml(str(input_file), 'Filter Test')

	# Only 2 MC questions should be included
	questions = result['sections'][0]['questions']
	assert len(questions) == 2
	assert questions[0]['statement'] == 'Normal MC question?'
	assert questions[1]['statement'] == 'Another MC question?'


def test_yaml_output_format(tmp_path):
	"""Test that output YAML is properly formatted."""
	input_content = """1. Question 1?
*a) Answer
b) Wrong
"""

	input_file = tmp_path / 'test_input.txt'
	input_file.write_text(input_content, encoding='utf-8')

	output_file = tmp_path / 'output.yaml'

	result = okla_to_exam_yaml.convert_okla_to_yaml(str(input_file), 'Test Title')

	with open(str(output_file), 'w', encoding='utf-8') as f:
		yaml.dump(result, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

	# Read it back and verify structure
	with open(str(output_file), 'r', encoding='utf-8') as f:
		loaded = yaml.safe_load(f)

	assert loaded['title'] == 'Test Title'
	assert 'date' in loaded
	assert len(loaded['sections']) == 1
	assert len(loaded['sections'][0]['questions']) == 1
	assert loaded['sections'][0]['questions'][0]['statement'] == 'Question 1?'


def test_special_characters_in_questions(tmp_path):
	"""Test handling of special characters in questions and choices."""
	input_content = "1. What is the formula for H2O?\na) H + O\n*b) H2O molecule\nc) Water molecule\n"

	input_file = tmp_path / 'test_special.txt'
	input_file.write_text(input_content, encoding='utf-8')

	result = okla_to_exam_yaml.convert_okla_to_yaml(str(input_file), 'Chemistry')

	question = result['sections'][0]['questions'][0]
	assert 'H2O' in question['statement']
	assert 'H2O molecule' in question['choices']


def test_complex_question_text(tmp_path):
	"""Test questions with complex multi-line text patterns."""
	input_content = """1. Which statement best describes: (a) the rate of reaction; (b) temperature effects?
*a) Both increase with catalyst
b) Rate decreases with temperature
c) No relationship exists
"""

	input_file = tmp_path / 'test_complex.txt'
	input_file.write_text(input_content, encoding='utf-8')

	result = okla_to_exam_yaml.convert_okla_to_yaml(str(input_file), 'Complex')

	question = result['sections'][0]['questions'][0]
	assert 'rate of reaction' in question['statement']
	assert 'temperature effects' in question['statement']
	assert len(question['choices']) == 3
