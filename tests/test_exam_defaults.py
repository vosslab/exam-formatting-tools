"""Test exam_defaults module."""

import ef_tools.exam_defaults


#============================================
def test_format_score_line_basic():
	"""Test format_score_line with basic inputs."""
	result = ef_tools.exam_defaults.format_score_line(50, 4)
	expected = "Final Score ____ / ____ / ____ / ____ / 50 pts"
	assert result == expected


#============================================
def test_format_score_line_single_section():
	"""Test format_score_line with single section."""
	result = ef_tools.exam_defaults.format_score_line(25, 1)
	expected = "Final Score ____ / 25 pts"
	assert result == expected
