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
	choices = ["a" * 25, "b" * 25, "c" * 25, "d" * 25]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (2, 2)


#============================================
def test_auto_layout_very_long_choices():
	"""Test very long choices get vertical stack."""
	choices = ["a" * 55, "b" * 55]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (1, 1)


#============================================
def test_auto_layout_five_medium_choices_anti_orphan():
	"""Test 5 medium choices use 3+2 layout to avoid orphan."""
	choices = ["a" * 18, "b" * 18, "c" * 18, "d" * 18, "e" * 18]
	result = ef_tools.layout.auto_layout_for_choices(choices)
	assert result == (3, 3)
