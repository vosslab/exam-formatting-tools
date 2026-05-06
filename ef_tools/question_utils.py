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
				# matching items use prompts_list; each prompt consumes one
				# question slot, so a 4-prompt block counts as 4 questions.
				prompts_list = question.get('prompts_list', [])
				total += max(1, len(prompts_list))
			else:
				total += 1
	return total

assert count_total_questions([]) == 0
assert count_total_questions([{'questions': [{}, {}, {}]}]) == 3
assert count_total_questions([{'questions': [{}]}, {'questions': [{}, {}]}]) == 3
assert count_total_questions([{'questions': [{'prompts_list': [1, 2, 3]}]}]) == 3
