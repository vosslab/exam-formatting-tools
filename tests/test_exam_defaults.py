"""Test exam_defaults module."""

import exam_defaults


#============================================
def test_format_score_line_basic():
	"""Test format_score_line with basic inputs."""
	result = exam_defaults.format_score_line(50, 4)
	expected = "Final Score ____ / ____ / ____ / ____ / 50 pts"
	assert result == expected


#============================================
def test_format_score_line_different_sections():
	"""Test format_score_line with different number of sections."""
	result = exam_defaults.format_score_line(100, 5)
	expected = "Final Score ____ / ____ / ____ / ____ / ____ / 100 pts"
	assert result == expected


#============================================
def test_format_score_line_single_section():
	"""Test format_score_line with single section."""
	result = exam_defaults.format_score_line(25, 1)
	expected = "Final Score ____ / 25 pts"
	assert result == expected


#============================================
def test_default_name_line():
	"""Test that default name line is defined."""
	assert exam_defaults.DEFAULT_NAME_LINE == "Full Name: __________________________"


#============================================
def test_default_scoring_sections():
	"""Test that default scoring sections count is defined."""
	assert exam_defaults.DEFAULT_SCORING_SECTIONS == 4
