"""Default boilerplate text and values for exam documents.

Centralized configuration for standard exam first-page elements,
scoring sections, and other defaults that can be overridden in YAML.
"""

DEFAULT_NAME_LINE = "Full Name: __________________________"
DEFAULT_SCORING_SECTIONS = 4


#============================================
def format_score_line(total_points: int, num_sections: int) -> str:
	"""Format the Final Score line with scoring section blanks.

	Args:
		total_points: Total points for the exam.
		num_sections: Number of scoring sections (blank slots).

	Returns:
		Formatted string like "Final Score ____ / ____ / ____ / ____ / 50 pts"
	"""
	# Build the blank sections: "____" separated by " / "
	blanks = " / ".join(["____"] * num_sections)
	score_line = f"Final Score {blanks} / {total_points} pts"
	return score_line
