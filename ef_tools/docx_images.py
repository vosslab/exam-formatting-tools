"""Sizing and placement rules for pictures inserted into the exam DOCX.

Two sizing models exist, and they are different enough to be separate types
rather than two branches of one function.

`DrawingSizer` handles renderer-produced drawings. Their printed width is a
pure function of their pixel width,

	inches = source_pixels / png_resolution * scale

with no bounding box and no clamp. This is what makes two drawings that are the
same size in the source HTML the same size in the DOCX. Fitting them to a box
instead normalizes their widths, which silently gives each drawing its own text
size -- the defect this module exists to prevent. A drawing too wide for the
text column overflows it; the instructor resizes those few by hand rather than
have every other drawing lose the shared scale.

`FitSizer` handles ordinary images (photographs, RDKit molecule drawings). They
are scaled to fill a bounding box, so each one ends up at whatever scale its box
demands. That is correct for pictures whose intrinsic size means nothing.

Both expose the same four operations, so the layout code never asks which kind
it holds: `kwargs`, `width_inches`, `narrowed`, `row_height` and `fits_columns`.

Drawing resolution is read from the PNG itself. The renderer writes its true
value into every file it produces (`ef_tools.bbq_html.RENDER_DPI` in the pHYs
chunk), so there is no configured resolution to drift out of sync with it -- a
drawing that does not declare its resolution is an error, not a default.
"""

# Pip Modules
import docx
import docx.shared
import docx.oxml
import docx.oxml.ns
import PIL.Image

# Local Repo Modules
import ef_tools.layout


# Per-column visible width budgets for a tabbed image-choice row, in inches.
# Going past these widths pushes a trailing image's cursor past its target tab
# stop, which then advances to the NEXT stop and creates a visible gap. Word's
# inline-image layout reserves more space per image than a naive cursor
# calculation predicts; values are set by viewing the rendered DOCX, not
# computed from page width.
IMAGE_CHOICE_MAX_WIDTH_BY_COLS = {
	2: 3.30,
	3: 2.07,
	4: 1.49,
	5: 1.13,
}

# Five captioned image choices need to remain one block below a question stem.
# A two-inch cap keeps the five labeled blocks on one page while making each
# tray substantially larger than the old five-column 1.13-inch images.
CAPTIONED_IMAGE_CHOICE_MAX_WIDTH = 2.0

# Body and choice text render at 10pt (styles/exam_styles.yaml sizes.choice).
# Baseline centering needs a font size to know where the line's visual middle
# sits; every paragraph that carries an inline drawing uses this size.
BASELINE_FONT_SIZE_PT = 10.0

# Fraction of the font size from the baseline up to the visual center of
# lowercase text. Roughly half the x-height for a humanist sans face, which is
# where LibreOffice's "Base line centered" places an as-character image.
BASELINE_CENTER_RATIO = 0.30


#============================================
def image_pixel_size(image_path: str) -> tuple:
	"""Return the (width, height) of an image in pixels."""
	with PIL.Image.open(image_path) as img:
		size = img.size
	return size


#============================================
def drawing_resolution(image_path: str) -> float:
	"""Return a rendered drawing's own resolution in pixels per inch.

	The value comes from the PNG's pHYs chunk, which the renderer writes. There
	is deliberately no configured fallback: a fallback is what let the DOCX side
	believe 96 px/in while the renderer produced 192, which reported every
	drawing at twice its size and left each one clamped to a different scale.
	Reading the file removes that whole class of drift.

	Args:
		image_path: Path to the rendered PNG.

	Returns:
		Horizontal resolution in pixels per inch.

	Raises:
		ValueError: The file declares no usable resolution.
	"""
	with PIL.Image.open(image_path) as img:
		recorded = img.info.get('dpi')
	# PIL reports dpi as an (x, y) pair; the renderer writes them equal.
	if recorded is None or not recorded[0]:
		raise ValueError(
			f"rendered drawing declares no resolution: {image_path}. "
			"Regenerate it with ef_tools.bbq_html.write_table_pngs.")
	resolution = float(recorded[0])
	if resolution <= 0:
		raise ValueError(f"drawing resolution must be positive: {image_path}")
	return resolution


#============================================
class DrawingSizer:
	"""Fixed-scale sizing shared by every renderer-produced drawing.

	One instance is built per document and handed to every layout helper, which
	is what guarantees that drawings of equal HTML size print at equal DOCX
	size. The scale is the only knob; changing it rescales every drawing
	together and never changes their sizes relative to each other.
	"""

	#============================================
	def __init__(self, scale: float) -> None:
		"""Store the single global scale factor."""
		if scale <= 0:
			raise ValueError('drawing scale must be positive')
		self.scale = scale

	#============================================
	def width_inches(self, image_path: str) -> float:
		"""Return the printed width of one drawing."""
		src_w, _src_h = image_pixel_size(image_path)
		return src_w / drawing_resolution(image_path) * self.scale

	#============================================
	def kwargs(self, image_path: str) -> dict:
		"""Return add_picture kwargs for one drawing."""
		return {'width': docx.shared.Inches(self.width_inches(image_path))}

	#============================================
	def narrowed(self, max_width: float) -> 'DrawingSizer':
		"""Return self; a drawing's size does not answer to a width budget."""
		return self

	#============================================
	def row_height(self, choices: list) -> float:
		"""Return None; drawings in a row each keep their own height.

		A uniform row height would rescale each drawing by a different factor,
		which is exactly the per-image scaling this type removes.
		"""
		return None

	#============================================
	def fits_columns(self, choices: list, num_cols: int) -> bool:
		"""Return whether these drawings fit a tabbed row of num_cols.

		Fixed-scale sizing cannot squeeze a drawing into its column, so the
		column budget is a yes/no fit test. A row that does not fit is stacked
		instead, which keeps every drawing at the shared scale.
		"""
		budget = IMAGE_CHOICE_MAX_WIDTH_BY_COLS.get(
			num_cols, IMAGE_CHOICE_MAX_WIDTH_BY_COLS[5])
		for choice in choices:
			image_path = ef_tools.layout.choice_image(choice)
			if not image_path:
				continue
			if self.width_inches(image_path) > budget:
				return False
		return True


#============================================
class FitSizer:
	"""Bounding-box sizing for ordinary images.

	python-docx preserves aspect ratio when only one of width/height is set, so
	fitting a box means pinning whichever axis binds first. A wide strip may
	take a shorter height cap so that strips of different lengths share one cell
	height; that rule applies only here, because a drawing's height is already
	fixed by its scale.
	"""

	#============================================
	def __init__(self, max_width: float, max_height: float = None,
			strip_height: float = None, strip_min_aspect: float = None) -> None:
		"""Store the bounding box and the optional wide-strip height rule."""
		if max_width is None or max_width <= 0:
			raise ValueError('max_width must be positive')
		self.max_width = max_width
		self.max_height = max_height
		self.strip_height = strip_height
		self.strip_min_aspect = strip_min_aspect

	#============================================
	def _height_cap(self, image_path: str) -> float:
		"""Return the height cap for one image, applying the strip rule."""
		if self.strip_height is None or self.strip_min_aspect is None:
			return self.max_height
		src_w, src_h = image_pixel_size(image_path)
		if src_h > 0 and src_w / src_h >= self.strip_min_aspect:
			return self.strip_height
		return self.max_height

	#============================================
	def kwargs(self, image_path: str) -> dict:
		"""Return add_picture kwargs fitting the image into the box."""
		max_height = self._height_cap(image_path)
		if max_height is None:
			return {'width': docx.shared.Inches(self.max_width)}
		src_w, src_h = image_pixel_size(image_path)
		width_scale = self.max_width / src_w
		height_scale = max_height / src_h
		if width_scale <= height_scale:
			return {'width': docx.shared.Inches(self.max_width)}
		return {'height': docx.shared.Inches(max_height)}

	#============================================
	def width_inches(self, image_path: str) -> float:
		"""Return the printed width of one fitted image."""
		return rendered_width_inches(image_path, self.kwargs(image_path))

	#============================================
	def narrowed(self, max_width: float) -> 'FitSizer':
		"""Return a copy bounded by the tighter of the two widths."""
		return FitSizer(
			min(self.max_width, max_width), self.max_height,
			self.strip_height, self.strip_min_aspect)

	#============================================
	def row_height(self, choices: list) -> float:
		"""Single row-level height that lets every image fit its column box.

		For each image, compute the height it would be when scaled to fit the
		box preserving aspect, and return the minimum, so the binding
		constraint of the row sets a uniform height. Returns None when there is
		no height bound or no image, and the caller sizes each image on its own.
		"""
		if self.max_height is None:
			return None
		heights = []
		for choice in choices:
			image_path = ef_tools.layout.choice_image(choice)
			if not image_path:
				continue
			src_w, src_h = image_pixel_size(image_path)
			# height when width is the binding constraint
			h_at_max_w = self.max_width * src_h / src_w
			# this image's rendered height is whichever bound is tighter
			heights.append(min(h_at_max_w, self.max_height))
		if not heights:
			return None
		return min(heights)

	#============================================
	def fits_columns(self, choices: list, num_cols: int) -> bool:
		"""Return True; a fitted image is scaled into whatever column it gets."""
		return True


#============================================
def rendered_width_inches(image_path: str, kwargs: dict) -> float:
	"""Width in inches that add_picture will give this image."""
	if 'width' in kwargs:
		return kwargs['width'].inches
	src_w, src_h = image_pixel_size(image_path)
	return kwargs['height'].inches * src_w / src_h


#============================================
def rendered_height_inches(image_path: str, kwargs: dict) -> float:
	"""Height in inches that add_picture will give this image.

	python-docx derives the unset axis from the aspect ratio, so the height is
	recoverable from whichever axis the caller pinned.
	"""
	if 'height' in kwargs:
		return kwargs['height'].inches
	src_w, src_h = image_pixel_size(image_path)
	return kwargs['width'].inches * src_h / src_w


#============================================
def zero_inline_image_margins(run: object) -> None:
	"""Set distT/distB/distL/distR=0 on every <wp:inline> in this run.

	Inline images in OOXML carry top/bottom/left/right distance attributes
	that act as outer padding around the picture. python-docx's add_picture
	leaves them at default values (often 114300 EMU = 0.125"), which chews
	visible space around each picture in a tight tab-separated row. Zeroing
	them lets the image hug its run's edges so the per-column budget can
	hold a wider visible image at the same docx column width.
	"""
	WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
	for inline in run.element.iter('{%s}inline' % WP):
		for attr in ('distT', 'distB', 'distL', 'distR'):
			inline.set(attr, '0')


#============================================
def set_run_baseline_center(run: object, height_inches: float,
		font_size_pt: float = BASELINE_FONT_SIZE_PT) -> None:
	"""Center an as-character picture on its text line with a signed offset.

	An inline picture rests its BOTTOM edge on the baseline, so it occupies the
	band from the baseline up to its own height and its center sits far above
	the text it shares a line with. OOXML's run-level w:position shifts a run by
	a signed number of half-points, so moving the picture down by half its
	height, less the short distance from the baseline up to the middle of the
	text, puts its center on the line's visual midline. That is what
	LibreOffice shows as Align Objects -> Base line centered, and the As
	Character anchor is untouched.

	Args:
		run: The run holding the picture.
		height_inches: The picture's rendered height.
		font_size_pt: Point size of the text on the same line.
	"""
	text_center_pt = font_size_pt * BASELINE_CENTER_RATIO
	# Negative lowers the run, which is the usual case: a picture is nearly
	# always taller than the text it sits beside.
	offset_pt = text_center_pt - (height_inches * 72.0) / 2.0
	offset_half_points = int(round(offset_pt * 2.0))
	if offset_half_points == 0:
		return
	position = docx.oxml.OxmlElement('w:position')
	position.set(docx.oxml.ns.qn('w:val'), str(offset_half_points))
	run._element.get_or_add_rPr().append(position)


#============================================
def place_inline_picture(run: object, image_path: str, kwargs: dict) -> None:
	"""Insert one picture into a run with the shared inline treatment.

	Every inline picture in the exam gets the same three steps: the picture,
	zeroed edge distances so it hugs its run, and a signed baseline offset so it
	centers on its text line.
	"""
	run.add_picture(image_path, **kwargs)
	zero_inline_image_margins(run)
	set_run_baseline_center(run, rendered_height_inches(image_path, kwargs))


#============================================
def is_wide_image_choice(choice: object, min_aspect: float) -> bool:
	"""Return whether an image choice is a wide strip at the given threshold."""
	image_path = ef_tools.layout.choice_image(choice)
	if not image_path:
		return False
	src_w, src_h = image_pixel_size(image_path)
	return src_h > 0 and src_w / src_h >= min_aspect
