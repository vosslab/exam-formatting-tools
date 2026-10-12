"""Test cleaned HTML to exam YAML conversion helpers."""

# Standard Library
import os

# Pip Modules
import lxml.html
# Local Repo Modules
import html_to_exam_yaml
import ef_tools.statement_content


#============================================
def statement_text(question: dict) -> str:
	"""Join statement prose for assertions that do not inspect block order."""
	return ef_tools.statement_content.text_content(question["statement"])


#============================================
def test_element_to_inline_html_preserves_subscript_ascii() -> None:
	"""Test inline HTML conversion preserves subscript tags."""
	element = lxml.html.fromstring("<span>H<sub>2</sub>O &amp; &Delta;G</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	# behavioral checks: subscript tag survives, ampersand stays escaped, Delta encodes to a numeric entity
	assert "<sub>2</sub>" in result
	assert "&amp;" in result
	assert "&#" in result
	assert result.endswith("G")


#============================================
def test_element_to_inline_html_compacts_pretty_subscript() -> None:
	"""Test pretty-printed subscript tags become compact inline notation."""
	element = lxml.html.fromstring("<span>H <sub> 2 </sub> O</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	assert result == "H<sub>2</sub>O"


#============================================
def test_element_to_inline_html_keeps_prose_after_subscript() -> None:
	"""Test prose spacing after subscript tags is preserved."""
	element = lxml.html.fromstring("<span>P<sub>i</sub> and pK<sub>a</sub> values</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	assert result == "P<sub>i</sub> and pK<sub>a</sub> values"


#============================================
def test_element_to_inline_html_preserves_code_markup() -> None:
	"""Code and teletype spans survive Blackboard HTML conversion."""
	element = lxml.html.fromstring(
		"<span>Use <code>ATGC</code> and <tt>GCTA</tt>.</span>")
	result = html_to_exam_yaml.element_to_inline_html(element)
	assert result == "Use <code>ATGC</code> and <tt>GCTA</tt>."


#============================================
def test_clean_choice_html_removes_letter_prefix() -> None:
	"""Test exported choice letter cleanup."""
	result = html_to_exam_yaml.clean_choice_html("A. <b>metal ion</b>")
	assert result == "<b>metal ion</b>"


#============================================
def test_parse_question_with_text_choices() -> None:
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
	assert statement_text(result) == "Which molecule is H<sub>2</sub>O?"
	assert result["choices"] == ["Water", "Salt"]


#============================================
def test_parse_question_with_choice_image() -> None:
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
def test_parse_question_with_cleaned_choice_item_image() -> None:
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
def test_parse_question_keeps_body_text_statement() -> None:
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
	assert statement_text(result) == "Which one is hydrophobic?"


#============================================
def test_parse_matching_block_emits_prompts_and_choices_lists() -> None:
	"""Matching blocks emit bptools-style prompts_list and choices_list.

	The lead-in prose stays in `statement`, the lettered (A./B./...) options
	land in `choices_list` (with prefixes stripped), and the numbered items
	students label land in `prompts_list`. The legacy `matching_terms`
	field is no longer emitted.
	"""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Match the terms.</p>
	<div>
	<div>
	<span style="white-space:nowrap">A. First option</span>
	<span style="white-space:nowrap">B. Second option</span>
	</div>
	<div>
	<div><span style="display:inline-block; width:30px; height:22px; border:2px solid #333;"></span><strong>Term 1</strong></div>
	<div><span style="display:inline-block; width:30px; height:22px; border:2px solid #333;"></span><strong>Term 2</strong></div>
	</div>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	# lead-in prose remains in statement; lettered options must NOT
	assert "Match the terms." in statement_text(result)
	assert "A. First option" not in statement_text(result)
	assert "B. Second option" not in statement_text(result)
	# choices_list holds lettered options with the 'A. '/'B. ' prefix stripped
	assert result["choices_list"] == ["First option", "Second option"]
	# prompts_list holds the numbered items, preserving inline markup,
	# and must not absorb any of the lettered-option text.
	assert "Term 1" in result["prompts_list"][0]
	assert "Term 2" in result["prompts_list"][1]
	for prompt in result["prompts_list"]:
		assert "A. " not in prompt
		assert "B. " not in prompt
		assert "First option" not in prompt
		assert "Second option" not in prompt
	# legacy field is gone
	assert "matching_terms" not in result


#============================================
def test_parse_question_preserves_text_after_inline_bold() -> None:
	"""Statement text following an inline <b> child (the .tail) is kept."""
	# Mirrors the Lineweaver-Burk question shape from
	# Final_Exam/Cleaned_Final_Exam_2A.html:3485-3552.
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	The <b>y-intercept</b> of a Lineweaver-Burk plot is:
	<div>
	<label><input type="radio"/><span>A. 1/V<sub>0</sub></span></label>
	<label><input type="radio"/><span>B. 1/V<sub>max</sub></span></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	statement = statement_text(result)
	# Text after the inline <b> wrapper survives.
	assert "Lineweaver-Burk plot is:" in statement
	# Inline tag wrapping survives, not just the inner text.
	assert "<b>y-intercept</b>" in statement


#============================================
def test_parse_question_preserves_text_after_inline_italic_sub() -> None:
	"""Statement text following <i>...<sub/></i> survives as a tail."""
	# Mirrors the K'eq question shape: prose continues after the italic
	# wrapper that contains a numeric character entity and a subscript.
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	If <i>K&#8242;<sub>eq</sub></i> = 1, what is the value of &#916;G&#176;&#8242;?
	<div>
	<label><input type="radio"/><span>A. 0</span></label>
	<label><input type="radio"/><span>B. negative</span></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	statement = statement_text(result)
	# Entity for the prime character round-trips as ASCII.
	assert "K&#8242;" in statement
	# Subscript inside the italic wrapper is preserved.
	assert "<sub>eq</sub>" in statement
	# The .tail (everything after </i>) survives.
	assert "= 1" in statement


#============================================
def test_is_matching_block_rejects_styled_hint_legend() -> None:
	"""A hint legend using bold inline-block spans must not look like matching.

	Without the bordered/empty-marker check, `display:inline-block` styled
	bold terms in a legend would falsely classify the surrounding div as a
	matching block, dumping bold terms into prompts_list and dropping the
	statement text.
	"""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	Which class of biomolecules stores genetic information?
	<div>
	<span style="white-space:nowrap; display:inline-block;"><b>proteins</b></span>
	<span style="white-space:nowrap; display:inline-block;"><b>nucleic acids</b></span>
	<span style="white-space:nowrap; display:inline-block;"><b>carbohydrates</b></span>
	<span style="white-space:nowrap; display:inline-block;"><b>lipids</b></span>
	</div>
	<div>
	<label><input type="radio"/><span>A. proteins</span></label>
	<label><input type="radio"/><span>B. nucleic acids</span></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	hint_div = question_div.xpath(".//div[span[contains(@style, 'display:inline-block')]]")[0]
	assert html_to_exam_yaml.is_matching_block(hint_div) is False
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert "genetic information" in statement_text(result)
	assert "prompts_list" not in result
	# Order-independent: both choice texts present, nothing extra leaked.
	assert set(result["choices"]) >= {"proteins", "nucleic acids"}


#============================================
def test_matching_marker_xpath_requires_border() -> None:
	"""A bare display:inline-block empty span must not classify as a marker.

	Locks the tightened MATCHING_PROMPT_MARKER_XPATH boundary directly:
	the marker must carry both `border` styling and empty content.
	"""
	wrapper = lxml.html.fromstring(
		"<div>"
		"<span style=\"white-space:nowrap\">A. only choice</span>"
		"<span style=\"display:inline-block; width:30px;\"></span>"
		"</div>"
	)
	# is_matching_block requires both a choice span AND a marker;
	# without `border` styling the inline-block span is not a marker,
	# so the whole div fails to classify.
	assert html_to_exam_yaml.is_matching_block(wrapper) is False


#============================================
def test_real_matching_question_still_yields_lists() -> None:
	"""A realistic matching block (bordered empty marker) still classifies."""
	# Marker styling matches the real cleaned HTML at
	# Final_Exam/Cleaned_Final_Exam_2A.html:59 et al.
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Match each bond to a type.</p>
	<div>
	<div>
	<span style="white-space:nowrap">A. ionic</span>
	<span style="white-space:nowrap">B. covalent</span>
	</div>
	<div>
	<div><span style="display:inline-block; width:30px; height:22px; border:2px solid #333;"></span><strong>Na-Cl</strong></div>
	<div><span style="display:inline-block; width:30px; height:22px; border:2px solid #333;"></span><strong>C-C</strong></div>
	</div>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	# Order-independent: both lettered options reach choices_list.
	assert set(result["choices_list"]) >= {"ionic", "covalent"}
	assert any("Na-Cl" in p for p in result["prompts_list"])
	assert any("C-C" in p for p in result["prompts_list"])


#============================================
def test_parse_question_preserves_statement_image() -> None:
	"""A statement-body <img> survives the deep-copy + prune flow."""
	html_text = """
	<div class="takeQuestionDiv">
	<li>
	<p>Identify the structure shown below.</p>
	<p><img class="cleaned-statement-media" src="files/structure.png"/></p>
	<div>
	<label><input type="radio"/><span>A. glucose</span></label>
	<label><input type="radio"/><span>B. fructose</span></label>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	assert result["statement"] == [
		{"text": "Identify the structure shown below."},
		{"image": os.path.join("Final_Exam", "files/structure.png")},
	]


#============================================
class FakeRenderer:
	"""Small renderer substitute that records the authored capture request."""

	#============================================
	def __init__(self) -> None:
		self.html = ''
		self.targets = {}

	#============================================
	def render(self, html: str, targets: dict, **_kwargs: object) -> dict:
		self.html = html
		self.targets = targets
		return {selector: b'PNG' for selector in targets}


#============================================
def test_parse_question_captures_canvas_table_from_complete_html(tmp_path: object) -> None:
	"""A drawing table is captured in its script-bearing question context."""
	html_path = tmp_path / "Cleaned_sample.html"
	html_text = (
		"<html><body>"
		"<div class='takeQuestionDiv'><li>"
		"<p>Identify the molecule shown.</p>"
		"<table role='img'><tr><td><p>"
		"<canvas class='cleaned-statement-media' id='canvas_test_1' width='480' height='480'></canvas>"
		"</p></td>"
		"<td><script>"
		"document.getElementById('canvas_test_1').getContext('2d').fillRect(0, 0, 1, 1);"
		"</script></td></tr></table>"
		"<math><mi>AB</mi></math>"
		"<div><label><input type='radio'/><span>A. Adenine</span></label></div>"
		"</li></div>"
		"</body></html>"
	)
	html_path.write_text(html_text, encoding="utf-8")
	html_doc = lxml.html.fromstring(html_text)
	question_div = html_doc.xpath(html_to_exam_yaml.TAKE_QUESTION_XPATH)[0]
	renderer = FakeRenderer()
	result = html_to_exam_yaml.parse_question(
		str(html_path), question_div, renderer, html_doc,
		str(tmp_path / 'sample_files'), label='question-1')
	assert "Identify the molecule shown." in statement_text(result)
	assert result["statement"][0] == {"text": "Identify the molecule shown."}
	assert result['statement'][1]['html_table'].startswith('<table')
	path = result['statement'][1]['image']
	assert os.path.isfile(path)
	assert 'fillRect' in renderer.html
	# Math labels that resemble hex question codes must remain visible media.
	assert 'image' in result['statement'][2]


#============================================
def test_compute_rendered_out_dir_uses_existing_image_directory(tmp_path: object) -> None:
	"""Browser captures share an existing cleaned image directory."""
	html_path = tmp_path / "Cleaned_exam.html"
	images_dir = tmp_path / "exam_files"
	images_dir.mkdir()
	(images_dir / "fig.png").write_bytes(b"\x89PNG\r\n")
	html_text = (
		"<html><body>"
		"<img class='cleaned-statement-media' src='exam_files/fig.png'/>"
		"</body></html>"
	)
	html_path.write_text(html_text, encoding="utf-8")
	doc = lxml.html.fromstring(html_text)
	out_dir = html_to_exam_yaml.compute_rendered_out_dir(str(html_path), doc)
	# Compare resolved paths so /tmp vs /private/tmp on macOS does not flake.
	assert os.path.realpath(out_dir) == os.path.realpath(str(images_dir))


#============================================
def test_compute_rendered_out_dir_strips_cleaned_prefix(tmp_path: object) -> None:
	"""Without an existing image, the fallback drops the Cleaned_ prefix."""
	html_path = tmp_path / "Cleaned_Exam_2A.html"
	html_path.write_text("<html><body></body></html>", encoding="utf-8")
	doc = lxml.html.fromstring("<html><body></body></html>")
	out_dir = html_to_exam_yaml.compute_rendered_out_dir(str(html_path), doc)
	assert os.path.basename(out_dir) == "Exam_2A_files"


#============================================
def test_compute_rendered_out_dir_uses_plain_stem_when_no_prefix(tmp_path: object) -> None:
	"""Without an existing image and without a Cleaned_ prefix, use the bare stem."""
	html_path = tmp_path / "midterm.html"
	html_path.write_text("<html><body></body></html>", encoding="utf-8")
	doc = lxml.html.fromstring("<html><body></body></html>")
	out_dir = html_to_exam_yaml.compute_rendered_out_dir(str(html_path), doc)
	assert os.path.basename(out_dir) == "midterm_files"
