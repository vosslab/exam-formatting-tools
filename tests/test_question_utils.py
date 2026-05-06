"""Test question_utils module."""

import ef_tools.question_utils


#============================================
def test_select_question_style_after_choices():
	"""Test style after choices uses Question Heading."""
	result = ef_tools.question_utils.select_question_style("choices")
	assert result == "Question Heading"


#============================================
def test_select_question_style_after_chapter():
	"""Test style after chapter uses Question Follow."""
	result = ef_tools.question_utils.select_question_style("chapter")
	assert result == "Question Follow"


#============================================
def test_count_total_questions_multiple_sections():
	"""Test counting questions across multiple sections."""
	sections = [
		{"questions": [1]},
		{"questions": [2, 3]},
	]
	result = ef_tools.question_utils.count_total_questions(sections)
	assert result == 3


#============================================
def test_count_total_questions_matching_prompts_list():
	"""A matching question contributes one slot per prompts_list entry.

	Prevents regression on the matching schema migration: each prompt
	consumes a question number, so the score-line total must reflect
	the prompt count instead of treating the matching block as 1.
	"""
	sections = [
		{"questions": [
			{"statement": "Match.", "prompts_list": ["a", "b", "c"], "choices_list": ["x", "y", "z"]},
			{"statement": "Plain MC.", "choices": ["one", "two"]},
		]},
	]
	result = ef_tools.question_utils.count_total_questions(sections)
	assert result == 4
