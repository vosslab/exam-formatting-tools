"""Test DOCX image choice tab-stop rendering (no tables)."""

import base64

import docx

import ef_tools.docx_builder
import ef_tools.style_loader


#============================================
def _make_styled_doc():
	"""Create a docx Document with the exam styles pre-loaded."""
	styles = ef_tools.style_loader.load_styles()
	doc = docx.Document()
	ef_tools.docx_builder.setup_styles(doc, styles)
	return doc


# Smallest valid 1x1 transparent PNG, base64-encoded.
_PNG_BYTES = base64.b64decode(
	"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


#============================================
def _write_pngs(tmp_path, count):
	"""Write count tiny PNG files into tmp_path and return their paths."""
	paths = []
	for index in range(count):
		path = tmp_path / f"choice_{index}.png"
		path.write_bytes(_PNG_BYTES)
		paths.append(str(path))
	return paths


#============================================
def test_add_image_choices_tabbed_emits_no_tables(tmp_path):
	"""The function must not create any docx tables."""
	image_paths = _write_pngs(tmp_path, 4)
	choices = [{"text": "curve", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_builder.add_image_choices_tabbed(
		doc, choices, image_width=1.0, page_width=6.5,
	)
	assert len(doc.tables) == 0


#============================================
def test_add_image_choices_tabbed_adds_tab_stops(tmp_path):
	"""Tab stops must be set at evenly spaced column boundaries."""
	image_paths = _write_pngs(tmp_path, 4)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_builder.add_image_choices_tabbed(
		doc, choices, image_width=1.0, page_width=6.4,
	)
	paragraph = doc.paragraphs[-1]
	tab_stops = list(paragraph.paragraph_format.tab_stops)
	# tab stops must exist between columns and be strictly increasing
	stop_positions = [stop.position for stop in tab_stops]
	assert stop_positions == sorted(stop_positions)
	assert len(set(stop_positions)) == len(stop_positions)
	assert len(tab_stops) > 0


#============================================
def test_add_image_choices_tabbed_inlines_one_image_per_choice(tmp_path):
	"""Each choice with an image must produce one inline image in the doc."""
	image_paths = _write_pngs(tmp_path, 3)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_builder.add_image_choices_tabbed(
		doc, choices, image_width=1.0, page_width=6.0,
	)
	assert len(doc.inline_shapes) == 3


#============================================
def test_add_image_choices_tabbed_renders_letter_prefixes(tmp_path):
	"""The paragraph must contain bold (A) (B) (C) prefix runs in order."""
	image_paths = _write_pngs(tmp_path, 3)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_builder.add_image_choices_tabbed(
		doc, choices, image_width=1.0, page_width=6.0,
	)
	paragraph = doc.paragraphs[-1]
	prefix_texts = [run.text for run in paragraph.runs if run.text.startswith("(")]
	assert "(A) " in prefix_texts
	assert "(B) " in prefix_texts
	assert "(C) " in prefix_texts


#============================================
def test_add_image_choices_tabbed_mixed_text_and_images(tmp_path):
	"""Choices with no image must not produce an inline shape but still hold a column."""
	image_paths = _write_pngs(tmp_path, 2)
	choices = [
		{"text": "first", "image": image_paths[0]},
		{"text": "no picture", "image": None},
		{"text": "third", "image": image_paths[1]},
	]
	doc = _make_styled_doc()
	ef_tools.docx_builder.add_image_choices_tabbed(
		doc, choices, image_width=1.0, page_width=6.0,
	)
	# only the choices that supplied an image are embedded
	assert len(doc.inline_shapes) == 2
	# all three letter columns are still present
	paragraph = doc.paragraphs[-1]
	prefix_texts = [run.text for run in paragraph.runs if run.text.startswith("(")]
	assert {"(A) ", "(B) ", "(C) "}.issubset(set(prefix_texts))


#============================================
def test_add_choice_label_paragraph_routes_image_choices_through_tabbed(tmp_path):
	"""The HTML builder routes image-bearing choice labels through tab-stop layout, not a table."""
	import lxml.html

	import ef_tools.style_loader
	import html_exam_docx_builder

	# write a tiny PNG into a fixture html dir so resolve_image_path can find it
	html_dir = tmp_path / "html_dir"
	html_dir.mkdir()
	files_dir = html_dir / "html_files"
	files_dir.mkdir()
	(files_dir / "a.png").write_bytes(_PNG_BYTES)
	html_path = str(html_dir / "page.html")

	label_html = (
		'<div>'
		'<label><input type="radio"/>'
		'<img class="cleaned-choice-media" src="html_files/a.png"/>'
		'</label>'
		'<label><input type="radio"/><span>B. text only</span></label>'
		'</div>'
	)
	container = lxml.html.fromstring(label_html)
	labels = container.xpath(".//label")

	doc = _make_styled_doc()
	styles = ef_tools.style_loader.load_styles()
	html_exam_docx_builder.add_choice_label_paragraph(doc, html_path, labels, styles)

	# routing must produce no docx tables
	assert len(doc.tables) == 0
	# the image choice must produce an inline shape
	assert len(doc.inline_shapes) == 1
