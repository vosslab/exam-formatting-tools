"""Question-level utility functions for exam formatting.

Provides question style selection and question counting.
"""


#============================================
def select_question_style(prev_element: str) -> str:
	"""Select appropriate question paragraph style based on previous element.

	Uses 'Question Heading' for questions following other questions or
	choices (normal flow), and 'Question Follow' for questions following
	headings, images, or tables (after a visual break).

	Args:
		prev_element: Type of the previous element
			('question', 'choices', 'chapter', 'table', 'image').

	Returns:
		Style name: 'Question Heading' or 'Question Follow'.
	"""
	if prev_element in ('question', 'choices'):
		style_name = 'Question Heading'
	else:
		# prev_element is 'chapter', 'table', or 'image'
		style_name = 'Question Follow'
	return style_name

assert select_question_style('question') == 'Question Heading'
assert select_question_style('choices') == 'Question Heading'
assert select_question_style('chapter') == 'Question Follow'
assert select_question_style('table') == 'Question Follow'
assert select_question_style('image') == 'Question Follow'


#============================================
def question_span(question: dict) -> int:
	"""Number of numbered rows one question block consumes.

	Matching and ordering blocks use prompts_list; each prompt consumes one
	question number, so a 4-prompt block spans 4 rows. Every other question
	spans 1. This is the single owner of that rule: the DOCX builder, the
	ZipGrade checks, total counts, and the answer key all call it.

	Args:
		question: One question dict from exam YAML.

	Returns:
		Row count, at least 1.
	"""
	# prompts_list is optional; absent or empty means a single-row question
	prompts_list = question.get('prompts_list', [])
	span = max(1, len(prompts_list))
	return span

assert question_span({}) == 1
assert question_span({'prompts_list': ['a', 'b', 'c']}) == 3


#============================================
def count_total_questions(sections: list) -> int:
	"""Count total number of questions across all sections.

	Args:
		sections: List of section dicts from exam data.

	Returns:
		Total count of questions.
	"""
	total = 0
	for section in sections:
		questions = section.get('questions', [])
		for question in questions:
			if isinstance(question, dict):
				total += question_span(question)
			else:
				total += 1
	return total

assert count_total_questions([]) == 0
assert count_total_questions([{'questions': [{}, {}, {}]}]) == 3
assert count_total_questions([{'questions': [{}]}, {'questions': [{}, {}]}]) == 3
assert count_total_questions([{'questions': [{'prompts_list': [1, 2, 3]}]}]) == 3
