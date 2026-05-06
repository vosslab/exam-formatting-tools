"""Test cleaned HTML to exam YAML conversion helpers."""

# Standard Library
import os

# Pip Modules
import lxml.html
import pytest

# Local Repo Modules
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
def test_parse_matching_block_emits_prompts_and_choices_lists():
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
	<div><span style="display:inline-block"></span><strong>Term 1</strong></div>
	<div><span style="display:inline-block"></span><strong>Term 2</strong></div>
	</div>
	</div>
	</li>
	</div>
	"""
	question_div = lxml.html.fromstring(html_text)
	result = html_to_exam_yaml.parse_question("Final_Exam/source.html", question_div)
	# lead-in prose remains in statement; lettered options must NOT
	assert "Match the terms." in result["statement"]
	assert "A. First option" not in result["statement"]
	assert "B. Second option" not in result["statement"]
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
def test_parse_question_renders_rdkit_canvas_to_png(tmp_path):
	"""RDKit canvas widgets become PNG entries in the question images list."""
	html_path = tmp_path / "Cleaned_sample.html"
	# Write the HTML to disk so resolve_image_path / out-dir resolution
	# behave the same as in the real pipeline.
	html_text = (
		"<html><body>"
		"<div class='takeQuestionDiv'><li>"
		"<p>Identify the molecule shown.</p>"
		"<table><tr><td><p>"
		"<canvas class='cleaned-statement-media' id='canvas_test_1' width='480' height='480'></canvas>"
		"</p></td>"
		"<td><script>"
		"/* */initRDKitModule().then(function(instance){"
		"RDKitModule=instance;"
		"let smiles=\"C1=NC2=NC=NC(=C2N1)N\";"
		"let mol=RDKitModule.get_mol(smiles);"
		"canvas=document.getElementById(\"canvas_test_1\");"
		"});"
		"</script></td></tr></table>"
		"<div><label><input type='radio'/><span>A. Adenine</span></label></div>"
		"</li></div>"
		"</body></html>"
	)
	html_path.write_text(html_text, encoding="utf-8")
	html_doc = lxml.html.fromstring(html_text)
	question_div = html_doc.xpath(html_to_exam_yaml.TAKE_QUESTION_XPATH)[0]
	rdkit_out_dir = html_to_exam_yaml.compute_rdkit_out_dir(str(html_path), html_doc)
	result = html_to_exam_yaml.parse_question(str(html_path), question_div, rdkit_out_dir)
	# The statement keeps the lead-in prose and does not leak script source.
	assert "Identify the molecule shown." in result["statement"]
	assert "initRDKitModule" not in result["statement"]
	assert "canvas_test_1" not in result["statement"]
	# A PNG path was emitted into the standard images list.
	assert "images" in result
	assert any(path.endswith(".png") for path in result["images"])
	# The PNG actually exists on disk.
	for path in result["images"]:
		if path.endswith(".png") and "rdkit_" in os.path.basename(path):
			assert os.path.isfile(path)
			return
	raise AssertionError("expected an rdkit_*.png entry in question images")


#============================================
def test_compute_rdkit_out_dir_uses_existing_image_directory(tmp_path):
	"""When the doc has a cleaned image, RDKit PNGs share that directory."""
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
	out_dir = html_to_exam_yaml.compute_rdkit_out_dir(str(html_path), doc)
	# Compare resolved paths so /tmp vs /private/tmp on macOS does not flake.
	assert os.path.realpath(out_dir) == os.path.realpath(str(images_dir))


#============================================
def test_compute_rdkit_out_dir_strips_cleaned_prefix(tmp_path):
	"""Without an existing image, the stem fallback drops the Cleaned_ prefix."""
	html_path = tmp_path / "Cleaned_Exam_2A.html"
	html_path.write_text("<html><body></body></html>", encoding="utf-8")
	doc = lxml.html.fromstring("<html><body></body></html>")
	out_dir = html_to_exam_yaml.compute_rdkit_out_dir(str(html_path), doc)
	assert os.path.basename(out_dir) == "Exam_2A_files"


#============================================
def test_compute_rdkit_out_dir_uses_plain_stem_when_no_prefix(tmp_path):
	"""Without an existing image and without a Cleaned_ prefix, use the bare stem."""
	html_path = tmp_path / "midterm.html"
	html_path.write_text("<html><body></body></html>", encoding="utf-8")
	doc = lxml.html.fromstring("<html><body></body></html>")
	out_dir = html_to_exam_yaml.compute_rdkit_out_dir(str(html_path), doc)
	assert os.path.basename(out_dir) == "midterm_files"


#============================================
def test_resolve_rdkit_canvases_raises_when_canvas_has_no_script(tmp_path):
	"""A canvas with no matching RDKit script must fail loudly, not drop silently."""
	# Canvas carries an explicit id so the failure is unambiguously the
	# missing-script branch and not the falsy-id short-circuit.
	html_text = (
		"<html><body><div class='takeQuestionDiv'><li>"
		"<canvas class='cleaned-statement-media' id='canvas_orphan_99'></canvas>"
		"</li></div></body></html>"
	)
	doc = lxml.html.fromstring(html_text)
	question_div = doc.xpath(html_to_exam_yaml.TAKE_QUESTION_XPATH)[0]
	with pytest.raises(ValueError):
		html_to_exam_yaml.resolve_rdkit_canvases(
			"sample.html", question_div, question_div, str(tmp_path)
		)


#============================================
def test_find_rdkit_script_for_canvas_returns_none_when_id_missing():
	"""Falsy canvas ids short-circuit and return None."""
	result = html_to_exam_yaml.find_rdkit_script_for_canvas([], "")
	assert result is None
	result = html_to_exam_yaml.find_rdkit_script_for_canvas([], None)
	assert result is None


#============================================
def test_find_rdkit_script_for_canvas_returns_none_when_no_script_matches():
	"""A non-empty script list with no matching id falls through to None."""
	wrapper = lxml.html.fromstring(
		"<div>"
		"<script>initRDKitModule();/*canvas_other*/let smiles=\"CC\";</script>"
		"<script>console.log('unrelated');</script>"
		"</div>"
	)
	scripts = wrapper.xpath(".//script")
	result = html_to_exam_yaml.find_rdkit_script_for_canvas(scripts, "canvas_missing")
	assert result is None
