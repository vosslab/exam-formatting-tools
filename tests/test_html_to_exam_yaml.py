"""Test cleaned HTML to exam YAML conversion helpers."""

import lxml.html

import html_to_exam_yaml


#============================================
def test_element_to_inline_html_preserves_subscript_ascii():
	"""Test inline HTML conversion preserves subscript tags."""
	element = lxml.html.fromstring("<span>H<sub>2</sub>O &amp; &Delta;G</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	# behavioral checks: subscript tag survives, ampersand stays escaped, Delta encodes to a numeric entity
	assert "<sub>2</sub>" in result
	assert "&amp;" in result
	assert "&#" in result
	assert result.endswith("G")


#============================================
def test_element_to_inline_html_compacts_pretty_subscript():
	"""Test pretty-printed subscript tags become compact inline notation."""
	element = lxml.html.fromstring("<span>H <sub> 2 </sub> O</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	assert result == "H<sub>2</sub>O"


#============================================
def test_element_to_inline_html_keeps_prose_after_subscript():
	"""Test prose spacing after subscript tags is preserved."""
	element = lxml.html.fromstring("<span>P<sub>i</sub> and pK<sub>a</sub> values</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	assert result == "P<sub>i</sub> and pK<sub>a</sub> values"


#============================================
def test_clean_choice_html_removes_letter_prefix():
	"""Test exported choice letter cleanup."""
	result = html_to_exam_yaml.clean_choice_html("A. <b>metal ion</b>")
	assert result == "<b>metal ion</b>"


#============================================
def test_parse_question_with_text_choices():
	"""Test a small cleaned question parses into statement and choices."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>abcd_1234</p>
	<p>Which molecule is H<sub>2</sub>O?</p>
	<div>
	<label><input type="radio"/><span>A. Water</span></label>
	<label><input type="radio"/><span>B. Salt</span></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert result["statement"] == "Which molecule is H<sub>2</sub>O?"
	assert result["choices"] == ["Water", "Salt"]


#============================================
def test_parse_question_with_choice_image():
	"""Test a choice image is represented as structured YAML."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Choose an image.</p>
	<div>
	<label><input type="radio"/><img class="cleaned-choice-media" src="files/a.png"/></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert len(result["choices"]) == 1
	assert result["choices"][0]["image"].endswith("files/a.png")
	assert result["choices"][0].get("text", "") == ""


#============================================
def test_parse_question_with_cleaned_choice_item_image():
	"""Test Blackboard image-choice divs become structured choices."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Choose an image.</p>
	<div class="cleaned-choice-grid">
	<div class="cleaned-choice-item">
	<span><input type="radio"/>A.</span>
	<p>curve</p>
	<img class="cleaned-choice-media" src="files/a.png"/>
	</div>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert len(result["choices"]) == 1
	assert result["choices"][0]["text"] == "curve"
	assert result["choices"][0]["image"].endswith("files/a.png")


#============================================
def test_parse_question_keeps_body_text_statement():
	"""Test raw li text before choices becomes the statement."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	Which one is hydrophobic?
	<div><label><input type="radio"/><span>A. butane</span></label></div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert result["statement"] == "Which one is hydrophobic?"


#============================================
def test_parse_matching_block_adds_numbered_terms():
	"""Test matching blocks split prompts from numbered terms."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Match the terms.</p>
	<div>
	<div>
	<span style="white-space:nowrap">A. First prompt</span>
	<span style="white-space:nowrap">B. Second prompt</span>
	</div>
	<div>
	<div><span style="display:inline-block"></span><strong>Term 1</strong></div>
	<div><span style="display:inline-block"></span><strong>Term 2</strong></div>
	</div>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert "Match the terms." in result["statement"]
	assert "A. First prompt" in result["statement"]
	assert "B. Second prompt" in result["statement"]
	assert len(result["matching_terms"]) == 2
	assert "Term 1" in result["matching_terms"][0]
	assert "Term 2" in result["matching_terms"][1]
