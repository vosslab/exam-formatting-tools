"""Test question_utils module."""

import ef_tools.question_utils


#============================================
def test_select_question_style_after_choices() -> None:
	"""Test style after choices uses Question Heading."""
	result = ef_tools.question_utils.select_question_style("choices")
	assert result == "Question Heading"


#============================================
def test_select_question_style_after_chapter() -> None:
	"""Test style after chapter uses Question Follow."""
	result = ef_tools.question_utils.select_question_style("chapter")
	assert result == "Question Follow"


#============================================
def test_question_span_matching_block_spans_prompts() -> None:
	"""A matching block spans one row per prompt; MC spans one row."""
	matching = {"statement": [{"text": "Match."}], "prompts_list": ["a", "b", "c", "d"], "choices_list": ["w"]}
	assert ef_tools.question_utils.question_span(matching) == 4
	assert ef_tools.question_utils.question_span({"statement": [{"text": "MC"}], "choices": ["a", "b"]}) == 1


#============================================
def test_count_total_questions_multiple_sections() -> None:
	"""Test counting questions across multiple sections."""
	sections = [
		{"questions": [1]},
		{"questions": [2, 3]},
	]
	result = ef_tools.question_utils.count_total_questions(sections)
	assert result == 3


#============================================
def test_count_total_questions_matching_prompts_list() -> None:
	"""A matching question contributes one slot per prompts_list entry.

	Prevents regression on the matching schema migration: each prompt
	consumes a question number, independently of its point value.
	"""
	sections = [
		{"questions": [
			{"statement": [{"text": "Match."}], "prompts_list": ["a", "b", "c"], "choices_list": ["x", "y", "z"]},
			{"statement": [{"text": "Plain MC."}], "choices": ["one", "two"]},
		]},
	]
	result = ef_tools.question_utils.count_total_questions(sections)
	assert result == 4


def test_point_total_weights_matching_without_changing_numbering() -> None:
	"""Four matches earn two points; MC and MA each earn one, regardless of key size."""
	sections = [{'questions': [
		{'prompts_list': ['a', 'b', 'c', 'd'], 'choices_list': ['w', 'x', 'y', 'z']},
		{'choices': {'A': 'one', 'B': 'two'}},
		{'choices': {'A': 'one', 'B': 'two', 'C': 'three'}},
	]}]
	assert ef_tools.question_utils.count_total_points(sections) == 4
	assert ef_tools.question_utils.count_total_questions(sections) == 6
