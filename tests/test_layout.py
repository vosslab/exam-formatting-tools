"""Test layout module."""

import ef_tools.layout


#============================================
def test_auto_layout_five_short_choices():
	"""Test 5 short choices fit in 5-column layout."""
	choices = ["a", "b", "c", "d", "e"]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (5, 5)


#============================================
def test_auto_layout_two_choices():
	"""Test 2 choices use 2-column layout."""
	choices = ["yes", "no"]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (2, 2)


#============================================
def test_auto_layout_four_medium_choices_anti_orphan():
	"""Test 4 medium choices use 2+2 layout to avoid orphan."""
	# 30 typical ASCII chars at 0.8 width = 24, just over max_chars_4 (23)
	choices = ["a" * 30, "b" * 30, "c" * 30, "d" * 30]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (2, 2)


#============================================
def test_auto_layout_very_long_choices():
	"""Test very long choices get vertical stack."""
	# 65 typical ASCII chars at 0.8 width = 52, over max_chars_2 (49)
	choices = ["a" * 65, "b" * 65]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (1, 1)


#============================================
def test_auto_layout_five_medium_choices_anti_orphan():
	"""Test 5 medium choices use 3+2 layout to avoid orphan."""
	# 23 typical ASCII chars at 0.8 width = 18.4, over max_chars_5 (17)
	choices = ["a" * 23, "b" * 23, "c" * 23, "d" * 23, "e" * 23]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (3, 3)


#============================================
def test_chemistry_matching_choices_use_multi_column():
	"""HTML entities and inline tags are scored as visible glyphs.

	The 4-item list from Final_Exam/final_exam_combined.yml regressed
	to bare Choice (vertical stack) when measurement counted raw YAML
	string length. With visible-width scoring the layout drops only to
	2+2, never to vertical stack.
	"""
	# pin thresholds so the test is stable if repo defaults change
	limits = {
		"max_chars_5": 17,
		"max_chars_4": 23,
		"max_chars_3": 30,
		"max_chars_2": 49,
	}
	choices = [
		"C - O (in carbon monoxide, CO)",
		"Mg 2+ &#8226; 2&#215; Cl - (magnesium chloride)",
		"C &#8801; C (in acetylene, C 2 H 2 )",
		"N-H | | | | N (bond represented by the vertical lines)",
	]
	result = ef_tools.layout.auto_layout_for_choices(choices, limits)
	# the longest item really is over the 4-column width budget, so the
	# algorithm correctly drops to 2+2 -- the regression was a collapse
	# all the way to (1, 1) with the bare Choice base style
	assert result == (2, 2)


#============================================
def test_short_chemistry_choices_use_four_columns():
	"""Short chemistry choices with HTML entities fit four columns.

	The visible-width scoring counts &#8226; and &#8801; as single
	glyphs, so a 4-item list of short formulas resolves to Choices 4.
	"""
	limits = {
		"max_chars_5": 17,
		"max_chars_4": 23,
		"max_chars_3": 30,
		"max_chars_2": 49,
	}
	choices = [
		"H<sub>2</sub>O",
		"CO<sub>2</sub>",
		"C &#8226; C",
		"C &#8801; C",
	]
	result = ef_tools.layout.auto_layout_for_choices(choices, limits)
	assert result == (4, 4)


#============================================
def test_choices_style_name_never_returns_choice():
	"""Every legal tab_style maps to a concrete Choices N style."""
	for tab_style in range(1, 6):
		assert ef_tools.layout.choices_style_name(tab_style) != "Choice"
