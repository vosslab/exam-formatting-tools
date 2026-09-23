"""Lock the invariant that no rendered choice paragraph carries the
abstract base style name 'Choice'.

The 'Choice' style is registered in setup_styles as the parent of
'Choices 2', 'Choices 3', 'Choices 4', and 'Choices 5'. It must
remain abstract -- only the concrete children should ever land on a
paragraph. Three previous bugs collapsed paragraphs to bare 'Choice':
the CHOICES_STYLE_NAME[1] mapping, an override in
add_choices_paragraph triggered by any image-bearing choice, and a
hardcoded assignment in add_image_choices_tabbed.
"""

import re
import sys
import base64

import docx

import file_utils
import ef_tools.docx_images
import ef_tools.docx_builder
import ef_tools.docx_choice_builder
import ef_tools.style_loader

# put the repo root on sys.path so yaml_to_exam_docx.py is importable
_REPO_ROOT = file_utils.get_repo_root()
if _REPO_ROOT not in sys.path:
	sys.path.insert(0, _REPO_ROOT)
import yaml_to_exam_docx


_CHOICES_N_PATTERN = re.compile(r"^Choices [2-5]$")

# smallest valid 1x1 transparent PNG, base64-encoded
_PNG_BYTES = base64.b64decode(
	"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


#============================================
def _make_styled_doc() -> object:
	"""Create a docx Document with the exam styles pre-loaded."""
	styles = ef_tools.style_loader.load_styles()
	doc = docx.Document()
	ef_tools.docx_builder.setup_styles(doc, styles)
	return doc


#============================================
def _write_png(tmp_path: object, name: object) -> object:
	"""Write a tiny PNG to tmp_path/name and return its path."""
	path = tmp_path / name
	path.write_bytes(_PNG_BYTES)
	return str(path)


#============================================
def test_text_choices_use_concrete_choices_n_style() -> None:
	"""Four short text choices land on a Choices [2-5] style."""
	doc = _make_styled_doc()
	choices = ["yes", "no", "maybe", "unknown"]
	ef_tools.docx_choice_builder.add_choices_paragraph(
		doc, choices, tab_style=4, items_per_row=4,
	)
	style_name = doc.paragraphs[-1].style.name
	assert _CHOICES_N_PATTERN.match(style_name), style_name
	assert doc.styles['Choice'].paragraph_format.space_before == docx.shared.Pt(4)


#============================================
def test_choice_rows_do_not_keep_with_the_next_paragraph() -> None:
	"""Choice rows can flow independently across page boundaries."""
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_choices_paragraph(
		doc, ['one', 'two', 'three', 'four', 'five'],
		tab_style=3, items_per_row=3,
	)
	choice_paragraphs = doc.paragraphs
	assert len(choice_paragraphs) == 2
	assert all(
		paragraph.paragraph_format.keep_with_next is not True
		and paragraph.style.paragraph_format.keep_with_next is False
		for paragraph in choice_paragraphs
	)
	assert doc.styles['Choice'].paragraph_format.keep_with_next is False
	for style_name in ('Choices 2', 'Choices 3', 'Choices 4', 'Choices 5'):
		assert doc.styles[style_name].paragraph_format.keep_with_next is False


#============================================
def test_long_text_choices_avoid_bare_choice_style() -> None:
	"""Single-column (vertical stack) layout still uses Choices N, not Choice."""
	doc = _make_styled_doc()
	# tab_style=1 used to map to bare 'Choice'; it now maps to Choices 2
	choices = ["a long answer", "another long answer"]
	ef_tools.docx_choice_builder.add_choices_paragraph(
		doc, choices, tab_style=1, items_per_row=1,
	)
	style_name = doc.paragraphs[-1].style.name
	assert _CHOICES_N_PATTERN.match(style_name), style_name
	assert all(
		paragraph.paragraph_format.keep_with_next is not True
		and paragraph.style.paragraph_format.keep_with_next is False
		for paragraph in doc.paragraphs
	)


#============================================
def test_mixed_text_image_choices_avoid_bare_choice_style(tmp_path: object) -> None:
	"""Mixed text+image choices route through Choices N, not bare Choice."""
	image_path = _write_png(tmp_path, "mix.png")
	choices = [
		{"text": "first option"},
		{"text": "second option with image", "image": image_path},
		{"text": "third option"},
	]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_choices_paragraph(
		doc, choices, tab_style=3, items_per_row=3,
		sizer=ef_tools.docx_images.FitSizer(1.0),
	)
	style_name = doc.paragraphs[-1].style.name
	assert _CHOICES_N_PATTERN.match(style_name), style_name


#============================================
def test_all_image_choices_avoid_bare_choice_style(tmp_path: object) -> None:
	"""add_image_choices_tabbed lands on a Choices [2-5] style."""
	images = [_write_png(tmp_path, f"img_{i}.png") for i in range(4)]
	choices = [{"text": "", "image": path} for path in images]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	style_name = doc.paragraphs[-1].style.name
	assert _CHOICES_N_PATTERN.match(style_name), style_name


#============================================
def test_choices_n_styles_inherit_from_choice_base() -> None:
	"""Each Choices N style declares Choice as its base_style.

	This locks the inheritance edge that motivates keeping Choice as a
	registered (but never paragraph-applied) abstract style.
	"""
	doc = _make_styled_doc()
	choices_two = doc.styles["Choices 2"]
	assert choices_two.base_style is not None
	assert choices_two.base_style.name == "Choice"


#============================================
def test_rich_text_color_span_sets_docx_run_color() -> None:
	"""A preserved bptools color span becomes a Word run color."""
	doc = _make_styled_doc()
	para = doc.add_paragraph()
	ef_tools.docx_builder.add_rich_text_runs(
		para, '<strong><span style="color: #9f342d;">A7</span></strong>')
	assert any(
		run.text == 'A7'
		and run.bold is True
		and str(run.font.color.rgb) == '9F342D'
		for run in para.runs)


#============================================
def test_manual_choice_font_preserves_markup_and_monospace() -> None:
	"""A question override changes choice prose while code stays monospace."""
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_choices_paragraph(
		doc,
		['<span style="color: #004d00;"><strong>adenine (A): 43%</strong></span>',
			'<code>ATGC</code>', '<i><code>GCTA</code></i>'],
		tab_style=3,
		items_per_row=3,
		font_family='IBM Plex Sans Condensed',
	)
	choice_para = doc.paragraphs[0]
	adenine = next(run for run in choice_para.runs if 'adenine' in run.text)
	code = next(run for run in choice_para.runs if run.text == 'ATGC')
	italic_code = next(run for run in choice_para.runs if run.text == 'GCTA')
	assert adenine.font.name == 'IBM Plex Sans Condensed'
	assert adenine.bold is True
	assert str(adenine.font.color.rgb) == '004D00'
	assert code.font.name == 'Atkinson Hyperlegible Mono Regular'
	assert code.italic is False
	assert italic_code.font.name == 'Atkinson Hyperlegible Mono Regular'
	assert italic_code.italic is True


#============================================
def test_matching_choices_list_uses_multi_column_style(tmp_path: object) -> None:
	"""A matching question's choices_list lands on a Choices [2-5] style.

	Goes through the full builder render path (`build_document`), which
	is the matching code path in yaml_to_exam_docx.py:202-208.
	"""
	# minimal YAML structure with one matching question; choices are short
	# chemistry formulae so the visible-width score allows a multi-column
	# layout (the regression collapsed this to bare Choice)
	exam_data = {
		"title": "Matching Render Path Test",
		"sections": [
			{
				"heading": "Test",
				"questions": [
					{
						"statement": [{"text": "Match each bond type with an example."}],
						"prompts_list": [
							"<b>non-polar covalent</b>",
							"<b>ionic</b>",
							"<b>hydrogen</b>",
							"<b>polar covalent</b>",
						],
						"choices_list": [
							"H<sub>2</sub>O",
							"CO<sub>2</sub>",
							"C &#8226; C",
							"C &#8801; C",
						],
					},
				],
			},
		],
	}
	output_path = str(tmp_path / "matching.docx")
	yaml_to_exam_docx.build_document(exam_data, output_path)
	doc = docx.Document(output_path)
	# find the choices_list paragraph: it carries the (A) prefix
	choices_paragraph = None
	for paragraph in doc.paragraphs:
		if paragraph.text.startswith("(A) "):
			choices_paragraph = paragraph
			break
	assert choices_paragraph is not None
	style_name = choices_paragraph.style.name
	assert _CHOICES_N_PATTERN.match(style_name), style_name
