"""Test cleaned HTML exam DOCX builder helpers."""

import html_exam_docx_builder


#============================================
def test_strip_choice_prefix_removes_letter_dot():
	"""Test choice prefix cleanup."""
	result = html_exam_docx_builder.strip_choice_prefix("A. First choice")
	assert result == "First choice"


#============================================
def test_strip_choice_prefix_keeps_plain_choice():
	"""Test plain choices are not changed."""
	result = html_exam_docx_builder.strip_choice_prefix("First choice")
	assert result == "First choice"


#============================================
def test_is_question_code_for_blackboard_code():
	"""Test hidden Blackboard-style code detection."""
	result = html_exam_docx_builder.is_question_code("42a3_ab0b")
	assert result is True


#============================================
def test_is_question_code_rejects_normal_text():
	"""Test normal question text is not treated as a code."""
	result = html_exam_docx_builder.is_question_code("Which option is correct?")
	assert result is False


#============================================
def test_resolve_image_path_relative_to_html_file():
	"""Test image path resolution uses the HTML file location."""
	result = html_exam_docx_builder.resolve_image_path(
		"Final_Exam/Cleaned_Final_Exam_2A.html",
		"Final_Exam_2A_files/c2.png",
	)
	# assert by suffix so the test stays portable across path separators
	assert result.endswith("Final_Exam_2A_files/c2.png") or result.endswith(
		"Final_Exam_2A_files\\c2.png"
	)
