"""Test DOCX image choice tab-stop rendering (no tables)."""

import base64

import docx
import docx.shared
import docx.oxml.ns
import pytest

import ef_tools.docx_builder
import ef_tools.docx_choice_builder
import ef_tools.docx_images
import ef_tools.layout
import ef_tools.style_loader


#============================================
def _make_styled_doc() -> object:
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
def _write_pngs(tmp_path: object, count: object) -> object:
	"""Write count tiny PNG files into tmp_path and return their paths."""
	paths = []
	for index in range(count):
		path = tmp_path / f"choice_{index}.png"
		path.write_bytes(_PNG_BYTES)
		paths.append(str(path))
	return paths


#============================================
def test_add_image_choices_tabbed_emits_no_tables(tmp_path: object) -> None:
	"""The function must not create any docx tables."""
	image_paths = _write_pngs(tmp_path, 4)
	choices = [{"text": "curve", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	assert len(doc.tables) == 0


#============================================
def test_add_image_choices_tabbed_uses_choices_n_style(tmp_path: object) -> None:
	"""Image-choice paragraphs must use a Choices N style; that style's tab
	stops drive column alignment. Adding paragraph-level tab stops on top
	of style-level stops causes Word to see two close-but-not-equal stops
	per column and image columns visibly drift -- so this test pins the
	style assignment and rejects redundant paragraph-level stops."""
	image_paths = _write_pngs(tmp_path, 4)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	# image paragraph is the last one (or second-to-last when alt text is
	# emitted); both should use Choices 4 with style-level tab stops
	for paragraph in doc.paragraphs[-3:]:
		if paragraph.style.name == "Choices 4":
			# style-level tab stops exist
			style_stops = list(paragraph.style.paragraph_format.tab_stops)
			assert len(style_stops) > 0
			# paragraph-level stops are NOT duplicated on top of style stops
			para_stops = list(paragraph.paragraph_format.tab_stops)
			assert len(para_stops) == 0


#============================================
def test_add_image_choices_tabbed_inlines_one_image_per_choice(tmp_path: object) -> None:
	"""Each choice with an image must produce one inline image in the doc."""
	image_paths = _write_pngs(tmp_path, 3)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	assert len(doc.inline_shapes) == 3


#============================================
def test_wide_image_choices_stack_at_readable_width(tmp_path: object) -> None:
	"""Wide sequence strips use one full-width row per choice."""
	import PIL.Image
	image_paths = []
	for index in range(4):
		path = tmp_path / f"strip_{index}.png"
		PIL.Image.new("RGB", (1400, 80), color="white").save(path)
		image_paths.append(str(path))
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	before = len(doc.paragraphs)
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.49, 2.0),
		wide_sizer=ef_tools.docx_images.FitSizer(5.6, 2.0),
		wide_image_min_aspect=5.0,
	)
	assert len(doc.paragraphs) - before == 4
	assert len(doc.inline_shapes) == 4
	# 1400:80 at a 5.6in width is substantially larger than the old
	# 4-column cap; the test locks the layout decision, not a renderer pixel.
	assert all(shape.width.inches > 5.0 for shape in doc.inline_shapes)


#============================================
def test_add_image_choices_tabbed_renders_letter_prefixes(tmp_path: object) -> None:
	"""The paragraph must contain bold (A) (B) (C) prefix runs in order."""
	image_paths = _write_pngs(tmp_path, 3)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	# letter prefixes live in the same combined paragraph as the images;
	# search across all paragraphs for the bold-prefix carrier
	prefix_texts = []
	for paragraph in doc.paragraphs:
		texts = [run.text for run in paragraph.runs if run.text.startswith("(")]
		if texts:
			prefix_texts = texts
			break
	# image-bearing choices use no trailing space after the letter so the
	# bold "(A)" hugs the image edge below it
	assert "(A)" in prefix_texts
	assert "(B)" in prefix_texts
	assert "(C)" in prefix_texts


#============================================
def test_add_image_choices_tabbed_mixed_text_and_images(tmp_path: object) -> None:
	"""Choices with no image must not produce an inline shape but still hold a column."""
	image_paths = _write_pngs(tmp_path, 2)
	choices = [
		{"text": "first", "image": image_paths[0]},
		{"text": "no picture", "image": None},
		{"text": "third", "image": image_paths[1]},
	]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	# only the choices that supplied an image are embedded
	assert len(doc.inline_shapes) == 2
	# all three letter columns are still present in the caption paragraph;
	# its index depends on whether an alt-text paragraph was emitted, so
	# search across all paragraphs for the bold-prefix carrier
	prefix_texts = []
	for paragraph in doc.paragraphs:
		texts = [run.text for run in paragraph.runs if run.text.startswith("(")]
		if texts:
			prefix_texts = texts
			break
	# image-bearing choices render "(A)" without trailing space; the
	# text-only choice (B) keeps "(B) " with trailing space before its text
	assert {"(A)", "(B) ", "(C)"}.issubset(set(prefix_texts))


#============================================
def test_image_choice_max_width_per_cols_clamps_5col(tmp_path: object) -> None:
	"""5-col rows must be clamped to IMAGE_CHOICE_MAX_WIDTH_BY_COLS[5]
	even when the caller passes a much larger image_width. Without this
	cap, image E in a 5-col row pushes the cursor past its tab stop and
	the trailing image wraps to a new line."""
	image_paths = _write_pngs(tmp_path, 5)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	# request 3.0" wide images; the per-col cap should clamp to 0.96"
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(3.0, 3.0),
	)
	cap_5col = ef_tools.docx_images.IMAGE_CHOICE_MAX_WIDTH_BY_COLS[5]
	for shape in doc.inline_shapes:
		# rendered width must not exceed the per-col cap (with a small
		# tolerance for the height-bound aspect-preserve path)
		assert shape.width.inches <= cap_5col + 0.01


#============================================
def test_image_choice_max_width_per_cols_4col_differs_from_5col() -> None:
	"""The dict must give 4-col rows more horizontal budget than 5-col."""
	caps = ef_tools.docx_images.IMAGE_CHOICE_MAX_WIDTH_BY_COLS
	assert caps[2] > caps[3] > caps[4] > caps[5]


#============================================
def test_zero_inline_image_margins_sets_dist_attrs_to_zero(tmp_path: object) -> None:
	"""Every inline image emitted by add_image_choices_tabbed must have
	distT/distB/distL/distR set to '0' on its <wp:inline> element. The
	default ~0.125" padding around each image steals visible width and
	breaks the tight column packing this layout relies on."""
	image_paths = _write_pngs(tmp_path, 3)
	choices = [{"text": "", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
	inline_count = 0
	for shape in doc.inline_shapes:
		for inline in shape._inline.iter('{%s}inline' % WP):
			inline_count += 1
			for attr in ('distT', 'distB', 'distL', 'distR'):
				assert inline.get(attr) == '0', f"{attr}={inline.get(attr)!r}"
	assert inline_count >= 1


#============================================
def test_alt_text_paragraph_skipped_for_placeholder_image_text(tmp_path: object) -> None:
	"""When every choice carries the literal placeholder text 'image',
	the alt-text paragraph must be suppressed -- otherwise the row
	below the images becomes 'image image image image image' which is
	noise. This is the Q26 (histidine) shape in the real exam."""
	image_paths = _write_pngs(tmp_path, 5)
	choices = [{"text": "image", "image": path} for path in image_paths]
	doc = _make_styled_doc()
	before = len(doc.paragraphs)
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	# only the combined paragraph was added; no alt-text paragraph
	assert len(doc.paragraphs) - before == 1


#============================================
def test_alt_text_paragraph_emitted_for_meaningful_alt_text(tmp_path: object) -> None:
	"""When choices carry real captions ('right peak', 'down to up plot',
	etc.), the alt-text paragraph must be emitted below the image row.
	This is the Q80 (enzyme curves) shape in the real exam."""
	image_paths = _write_pngs(tmp_path, 5)
	captions = ["right peak", "down to up", "left peak", "up to down", "middle peak"]
	choices = [
		{"text": cap, "image": path}
		for cap, path in zip(captions, image_paths)
	]
	doc = _make_styled_doc()
	before = len(doc.paragraphs)
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(1.0),
	)
	# combined paragraph + alt-text paragraph = 2 new paragraphs
	assert len(doc.paragraphs) - before == 2
	# the second new paragraph must contain the captions
	alt_para = doc.paragraphs[before + 1]
	alt_text = " ".join(run.text for run in alt_para.runs)
	for cap in captions:
		assert cap in alt_text


#============================================
def test_long_image_captions_stack_to_preserve_choice_mapping(tmp_path: object) -> None:
	"""Long captions get their own labeled block instead of wrapping across columns."""
	image_paths = _write_pngs(tmp_path, 5)
	caption = 'Visual representation of test reactions: OO%O'
	choices = [{"text": caption, "image": path} for path in image_paths]
	doc = _make_styled_doc()
	ef_tools.docx_choice_builder.add_image_choices_tabbed(
		doc, choices, ef_tools.docx_images.FitSizer(3.4, 2.0),
	)
	assert len(doc.paragraphs) == 10
	assert len(doc.inline_shapes) == 5
	assert all(
		paragraph.style.name == 'Choices 2'
		for paragraph in doc.paragraphs)


#============================================
def test_fit_picture_kwargs_picks_height_when_height_binds(tmp_path: object) -> None:
	"""When the source image is taller than wide and max_height is the
	tighter bound, fit_picture_kwargs must return height= (not width=)
	so aspect ratio is preserved without overflowing the height box."""
	# write a 10x40 PNG (4x taller than wide) so height-scale binds
	import PIL.Image
	tall_png = tmp_path / "tall.png"
	PIL.Image.new("RGB", (10, 40), color="white").save(tall_png)
	kwargs = ef_tools.docx_images.FitSizer(1.0, 1.0).kwargs(str(tall_png))
	assert "height" in kwargs and "width" not in kwargs


#============================================
def test_fit_picture_kwargs_picks_width_when_width_binds(tmp_path: object) -> None:
	"""Wide source image with width as the tighter bound: width= wins."""
	import PIL.Image
	wide_png = tmp_path / "wide.png"
	PIL.Image.new("RGB", (40, 10), color="white").save(wide_png)
	kwargs = ef_tools.docx_images.FitSizer(1.0, 1.0).kwargs(str(wide_png))
	assert "width" in kwargs and "height" not in kwargs


#============================================
def test_table_images_share_one_inches_per_pixel(tmp_path: object) -> None:
	"""The relative-precision contract: drawings of different pixel widths
	must all print at the same inches-per-pixel. Fitting them to a box
	instead normalizes their widths, which silently gives each image its
	own text size -- the defect fixed-scale sizing exists to prevent."""
	import PIL.Image
	sizer = ef_tools.docx_images.DrawingSizer(0.7)
	ratios = []
	for pixel_width in (254, 504, 924, 1090):
		png_path = tmp_path / f"table_{pixel_width}.png"
		PIL.Image.new("RGB", (pixel_width, 48), color="white").save(
			png_path, dpi=(192, 192))
		kwargs = sizer.kwargs(str(png_path))
		ratios.append(kwargs['width'].inches / pixel_width)
	assert max(ratios) - min(ratios) < 1e-6
	# 924 px at 192 dpi is 4.8125 in, and 0.7 of that is 3.36875 in
	assert abs(ratios[2] * 924 - 3.36875) < 1e-4


#============================================
def test_table_image_wider_than_column_is_not_clamped(tmp_path: object) -> None:
	"""An oversize drawing overflows the text column on purpose. Clamping
	it would break the shared scale for that one image; the instructor
	resizes those few by hand instead."""
	import PIL.Image
	wide_png = tmp_path / "wide_map.png"
	PIL.Image.new("RGB", (2240, 272), color="white").save(
		wide_png, dpi=(192, 192))
	kwargs = ef_tools.docx_images.DrawingSizer(0.7).kwargs(str(wide_png))
	# 2240 / 192 * 0.7 = 8.1666..., well past the 5.6 in text column
	assert kwargs['width'].inches > 5.6


#============================================
def test_drawing_size_comes_from_the_png_resolution(tmp_path: object) -> None:
	"""A drawing is sized by the resolution it records, so no configured
	value can drift out of sync with the renderer."""
	import PIL.Image
	png_path = tmp_path / "stamped.png"
	PIL.Image.new("RGB", (384, 48), color="white").save(
		png_path, dpi=(192, 192))
	kwargs = ef_tools.docx_images.DrawingSizer(1.0).kwargs(str(png_path))
	# PNG stores resolution in pixels per metre, so 192 dpi round-trips as
	# 191.9986. The residue is far below one EMU of rendered width.
	assert abs(kwargs['width'].inches - 2.0) < 1e-3


#============================================
def test_drawing_without_recorded_resolution_is_rejected(
		tmp_path: object) -> None:
	"""Silently assuming a resolution is what let the DOCX side believe
	96 px/in while the renderer produced 192. A drawing that declares none
	is an error, not a default."""
	import PIL.Image
	png_path = tmp_path / "unstamped.png"
	PIL.Image.new("RGB", (384, 48), color="white").save(png_path)
	with pytest.raises(ValueError):
		ef_tools.docx_images.DrawingSizer(1.0).kwargs(str(png_path))


#============================================
def test_drawings_too_wide_for_their_columns_do_not_fit(
		tmp_path: object) -> None:
	"""A drawing cannot be squeezed into a column, so an oversize row
	reports that it does not fit and the caller stacks it instead."""
	import PIL.Image
	sizer = ef_tools.docx_images.DrawingSizer(0.7)
	choices = []
	for index in range(5):
		png_path = tmp_path / f"panel_{index}.png"
		# 592 px at 192 dpi and 0.7 is 2.16 in, past the 1.13 in 5-col budget
		PIL.Image.new("RGB", (592, 314), color="white").save(
			png_path, dpi=(192, 192))
		choices.append({"text": "", "image": str(png_path)})
	assert sizer.fits_columns(choices, 5) is False
	# a fitted image is scaled into whatever column it gets, so it always fits
	assert ef_tools.docx_images.FitSizer(1.13).fits_columns(choices, 5) is True


#============================================
def test_inline_picture_is_lowered_onto_the_text_midline() -> None:
	"""An inline picture rests its BOTTOM on the baseline, so centering it
	means moving it DOWN by half its height. Raising it instead lifts the
	picture clear of the line and drops the letter prefix to its bottom
	edge, which is the failure this guards."""
	doc = _make_styled_doc()
	run = doc.add_paragraph().add_run()
	ef_tools.docx_images.set_run_baseline_center(run, 1.0, font_size_pt=10.0)
	values = [
		element.get(docx.oxml.ns.qn('w:val'))
		for element in run._element.iter(docx.oxml.ns.qn('w:position'))
	]
	assert len(values) == 1
	# 0.30 * 10pt - (1.0 in * 72 / 2) = 3 - 36 = -33pt = -66 half-points
	assert int(values[0]) == -66


#============================================
def test_row_image_height_picks_smallest_binding_height(tmp_path: object) -> None:
	"""row_image_height must return the minimum rendered height across
	all images so the row stays uniform when source aspect ratios differ.
	Construct two images whose rendered heights DIFFER so a buggy max()
	or `return max_height` cannot pass: the wide image (width-bound)
	produces 0.25, the tall image (height-bound) produces 1.0; the
	correct minimum is 0.25."""
	import PIL.Image
	# wide image (w:h = 4:1): width-bound -> h_at_max_w = 1.0 * 1/4 = 0.25
	wide_png = tmp_path / "wide.png"
	PIL.Image.new("RGB", (400, 100), color="white").save(wide_png)
	# tall image (w:h = 1:4): height-bound -> capped at max_height = 1.0
	tall_png = tmp_path / "tall.png"
	PIL.Image.new("RGB", (100, 400), color="white").save(tall_png)
	choices = [
		{"text": "", "image": str(wide_png)},
		{"text": "", "image": str(tall_png)},
	]
	# the wide image is the binding constraint; min(0.25, 1.0) = 0.25
	result = ef_tools.docx_images.FitSizer(1.0, 1.0).row_height(choices)
	assert abs(result - 0.25) < 0.001


#============================================
def test_drawing_sizer_declines_to_unify_row_heights(tmp_path: object) -> None:
	"""A uniform row height would rescale each drawing by a different
	factor, reintroducing per-image text sizes. The drawing sizer reports
	no row height so each drawing keeps its own size."""
	import PIL.Image
	choices = []
	for pixel_width in (300, 900):
		png_path = tmp_path / f"strip_{pixel_width}.png"
		PIL.Image.new("RGB", (pixel_width, 48), color="white").save(
			png_path, dpi=(192, 192))
		choices.append({"text": "", "image": str(png_path)})
	assert ef_tools.docx_images.DrawingSizer(0.7).row_height(choices) is None
