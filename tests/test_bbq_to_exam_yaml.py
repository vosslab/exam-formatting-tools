"""
Unit tests for bbq_to_exam_yaml converter.
"""

# local repo modules
import bbq_to_exam_yaml


#============================================
def test_parse_mc_line():
	"""
	Test parsing MC (multiple choice) line.
	"""
	parts = ['MC', 'What is 2+2?', '3', 'incorrect', '4', 'correct', '5', 'incorrect']
	result = bbq_to_exam_yaml.parse_mc_line(parts)
	assert result['statement'] == 'What is 2+2?'
	assert result['choices'] == ['3', '4', '5']


#============================================
def test_parse_ma_line():
	"""
	Test parsing MA (multiple answer) line.
	"""
	parts = ['MA', 'Prime numbers?', '2', 'correct', '3', 'correct', '4', 'incorrect']
	result = bbq_to_exam_yaml.parse_ma_line(parts) if hasattr(bbq_to_exam_yaml, 'parse_ma_line') else bbq_to_exam_yaml.parse_mc_line(parts)
	assert result['statement'] == 'Prime numbers?'
	assert result['choices'] == ['2', '3', '4']


#============================================
def test_parse_mat_line():
	"""
	Test parsing MAT (matching) line.
	"""
	parts = ['MAT', 'Match capitals', 'USA', 'Washington', 'France', 'Paris']
	result = bbq_to_exam_yaml.parse_mat_line(parts)
	assert result['statement'] == 'Match capitals'
	assert result['table']['columns'] == ['Prompt', 'Match']
	assert result['table']['rows'] == [['USA', 'Washington'], ['France', 'Paris']]


#============================================
def test_parse_ord_line():
	"""
	Test parsing ORD (ordering) line.
	"""
	parts = ['ORD', 'Order the steps', 'Step 1', 'Step 2', 'Step 3']
	result = bbq_to_exam_yaml.parse_ord_line(parts)
	assert result['statement'] == 'Order the steps'
	assert result['choices'] == ['Step 1', 'Step 2', 'Step 3']


#============================================
def test_parse_bbq_line_mc():
	"""
	Test parse_bbq_line with MC question.
	"""
	line = "MC\tWhat is 2+2?\t3\tincorrect\t4\tcorrect"
	result = bbq_to_exam_yaml.parse_bbq_line(line)
	assert result is not None
	assert result['statement'] == 'What is 2+2?'
	assert result['choices'] == ['3', '4']


#============================================
def test_parse_bbq_line_mat():
	"""
	Test parse_bbq_line with MAT question.
	"""
	line = "MAT\tMatch capitals\tUSA\tWashington\tFrance\tParis"
	result = bbq_to_exam_yaml.parse_bbq_line(line)
	assert result is not None
	assert result['statement'] == 'Match capitals'
	assert 'table' in result


#============================================
def test_parse_bbq_line_ord():
	"""
	Test parse_bbq_line with ORD question.
	"""
	line = "ORD\tOrder these\tOne\tTwo\tThree"
	result = bbq_to_exam_yaml.parse_bbq_line(line)
	assert result is not None
	assert result['statement'] == 'Order these'
	assert result['choices'] == ['One', 'Two', 'Three']


#============================================
def test_parse_bbq_line_empty():
	"""
	Test parse_bbq_line with empty line.
	"""
	result = bbq_to_exam_yaml.parse_bbq_line("")
	assert result is None


#============================================
def test_parse_bbq_line_whitespace():
	"""
	Test parse_bbq_line with whitespace-only line.
	"""
	result = bbq_to_exam_yaml.parse_bbq_line("   \t  ")
	assert result is None


#============================================
def test_parse_bbq_line_unknown_type():
	"""
	Test parse_bbq_line with unknown question type.
	"""
	line = "INVALID\tSome question"
	result = bbq_to_exam_yaml.parse_bbq_line(line)
	assert result is None


#============================================
def test_convert_bbq_to_yaml(tmp_path):
	"""
	Test full conversion from BBQ file to YAML structure.
	"""
	# Create test input file
	input_file = tmp_path / 'test_input.bbq'
	content = '''MC\tWhat is 2+2?\t3\tincorrect\t4\tcorrect
MA\tPrime numbers?\t2\tcorrect\t3\tcorrect\t4\tincorrect
MAT\tMatch capitals\tUSA\tWashington\tFrance\tParis
ORD\tOrder these\tOne\tTwo\tThree
'''
	input_file.write_text(content)

	# Convert
	result = bbq_to_exam_yaml.convert_bbq_to_yaml(str(input_file), 'Test Exam')

	# Verify structure
	assert result['title'] == 'Test Exam'
	assert 'date' in result
	assert 'sections' in result
	assert len(result['sections']) == 1
	assert result['sections'][0]['chapter'] == 'Questions'
	assert len(result['sections'][0]['questions']) == 4

	# Verify question contents
	questions = result['sections'][0]['questions']
	assert questions[0]['statement'] == 'What is 2+2?'
	assert questions[1]['statement'] == 'Prime numbers?'
	assert questions[2]['statement'] == 'Match capitals'
	assert 'table' in questions[2]
	assert questions[3]['statement'] == 'Order these'


#============================================
def test_convert_bbq_to_yaml_mixed(tmp_path):
	"""
	Test conversion with mixed questions and empty lines.
	"""
	input_file = tmp_path / 'test_mixed.bbq'
	content = '''MC\tQ1\tA\tincorrect\tB\tcorrect

MC\tQ2\tC\tcorrect\tD\tincorrect
'''
	input_file.write_text(content)

	result = bbq_to_exam_yaml.convert_bbq_to_yaml(str(input_file), 'Mixed Test')

	# Should have 2 questions (empty line skipped)
	assert len(result['sections'][0]['questions']) == 2


#============================================
def test_parse_mc_with_whitespace():
	"""
	Test parsing MC with extra whitespace.
	"""
	parts = ['MC', '  What is the answer?  ', '  A  ', '  incorrect  ', '  B  ', '  correct  ']
	result = bbq_to_exam_yaml.parse_mc_line(parts)
	assert result['statement'] == 'What is the answer?'
	assert result['choices'] == ['A', 'B']


#============================================
def test_parse_mat_with_whitespace():
	"""
	Test parsing MAT with extra whitespace.
	"""
	parts = ['MAT', '  Match items  ', '  Item 1  ', '  Choice 1  ', '  Item 2  ', '  Choice 2  ']
	result = bbq_to_exam_yaml.parse_mat_line(parts)
	assert result['statement'] == 'Match items'
	assert result['table']['rows'] == [['Item 1', 'Choice 1'], ['Item 2', 'Choice 2']]
