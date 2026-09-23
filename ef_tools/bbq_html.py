"""Convert bptools bbq HTML fragments into exam YAML text and table sources.

bptools question text arrives as HTML: a leading `<p>CRC</p>` code, `<p>`
and `<h6>` blocks, colored `<span>` wrappers, and drawing `<table>`s (gels,
chi-square critical values, test-cross counts). The DOCX builder understands
only the inline tags in ef_tools.text_utils (sub, sup, b, strong, i, em,
code, tt), so
this module reduces the HTML to that vocabulary and pulls drawing tables out
for the rasterized fallback; the original table HTML remains available for
the optional native DOCX table backend.
"""

# Standard Library
import functools
import io
import os
import re
import base64

# PIP3 modules
import lxml.html
import PIL.Image
import PIL.ImageChops

# local repo modules
import ef_tools.html_parse
import ef_tools.style_loader
import ef_tools.text_utils
import ef_tools.statement_content
import qti_package_maker.html_to_image.selectors
import qti_package_maker.html_to_image.render_canvas
import qti_package_maker.html_to_image.render_table


# The table renderer screenshots CSS pixels at a device scale factor, so a
# rendered PNG carries DEVICE_SCALE_FACTOR physical pixels per CSS pixel. CSS
# itself is defined at 96 px/in, so the PNG's true resolution is the product.
# Deriving it from the renderer's own constant keeps one source of truth: if
# the renderer changes its scale factor, sizing follows automatically.
CSS_PIXELS_PER_INCH = 96
RENDER_DPI = CSS_PIXELS_PER_INCH * qti_package_maker.html_to_image.render_table.DEVICE_SCALE_FACTOR

# Outer bleed kept around the autocrop box, in rendered device pixels. Table
# borders are hairlines (`1px solid #999`), and antialiasing puts their faintest
# row right at the content edge; a small bleed keeps those from being shaved.
AUTOCROP_BLEED_PX = 2


# tags whose content is re-emitted wrapped in the same bare tag
INLINE_KEEP_TAGS = ('sub', 'sup', 'b', 'strong', 'i', 'em', 'code', 'tt')
# tags that only add a paragraph boundary around their content
BLOCK_TAGS = ('p', 'div', 'ul', 'ol')
# section headings become their own bold line
HEADING_TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
# empty tags that become a line break
BREAK_TAGS = ('br', 'hr')
# tags dropped entirely, keeping their text
UNWRAP_TAGS = ('span', 'font', 'a', 'u', 'small', 'big')
RDKIT_IMAGE_PREFIX = 'rdkit:'
MATHML_IMAGE_PREFIX = 'mathml:'

# whitespace normalization
_SPACE_RUN_RE = re.compile(r'[ \t]+')
_BLANK_LINE_RE = re.compile(r'\n\s*\n+')
_SPACE_AROUND_NEWLINE_RE = re.compile(r' *\n *')
#============================================
def _span_text_color(element: lxml.html.HtmlElement) -> str | None:
	"""Return a normalized hex text color from a span's inline style.

	Only the text-color declaration is part of the printable exam contract.
	Other span CSS (including anti-cheat font sizing) remains presentation
	metadata and is intentionally discarded.
	"""
	return ef_tools.text_utils.text_color_from_style(element.get('style', ''))


#============================================
def _parse(html: str) -> lxml.html.HtmlElement:
	"""Parse an HTML fragment into a wrapper div element."""
	root = qti_package_maker.html_to_image.selectors.parse_html_fragment(html)
	return root


#============================================
def render_rdkit_canvases(html: str, image_store: dict,
			field_name: str) -> str:
	"""Replace supported RDKit canvas markup with opaque image references.

	The source JavaScript is parsed only for the drawing values understood by
	qti-package-maker. It is never evaluated, and the known external loader is
	removed before this HTML reaches the exam text or table renderer.
	"""
	root = _parse(html)
	selectors = qti_package_maker.html_to_image.selectors
	loader_scripts = [
		script for script in root.xpath('.//script')
		if selectors.is_rdkit_loader_script(script)]
	selectors.remove_rdkit_loader_scripts(root)
	targets = selectors.iter_canvas_targets(root)
	if not targets and not loader_scripts:
		return html
	for canvas, script, source in targets:
		try:
			png_bytes = qti_package_maker.html_to_image.render_canvas.render_canvas_png(source)
		except (ImportError, ValueError) as exc:
			raise ValueError(f"{field_name}: {exc}") from exc
		key = str(len(image_store) + 1)
		image_store[key] = png_bytes
		image = lxml.html.Element('img')
		image.set('src', f"{RDKIT_IMAGE_PREFIX}{key}")
		image.set('alt', source.legend or 'Molecular structure')
		parent = canvas.getparent()
		parent.replace(canvas, image)
		# Keep any text following the drawing script when removing the consumed
		# script node. Current generators place the drawing script last.
		if script.tail:
			previous = script.getprevious()
			if previous is not None:
				previous.tail = (previous.tail or '') + script.tail
			else:
				script.getparent().text = (script.getparent().text or '') + script.tail
		script.getparent().remove(script)
	new_html = _serialize(root)
	return new_html


#============================================
def render_mathml_equations(html: str, image_store: dict,
			renderer: object, field_name: str) -> str:
	"""Replace supported MathML equations with rendered image references."""
	root = _parse(html)
	math_elements = root.xpath('.//math')
	if not math_elements:
		return html
	if renderer is None:
		raise ValueError(f"{field_name}: MathML equations need an image renderer")
	for math_element in math_elements:
		mathml_html = qti_package_maker.html_to_image.selectors.outer_html(math_element)
		try:
			png_bytes = renderer.render_mathml_png(mathml_html)
		except ValueError as exc:
			raise ValueError(f"{field_name}: {exc}") from exc
		key = str(len(image_store) + 1)
		image_store[key] = png_bytes
		image = lxml.html.Element('img')
		image.set('src', f"{MATHML_IMAGE_PREFIX}{key}")
		image.set('alt', 'Mathematical equation')
		image.tail = math_element.tail
		math_element.getparent().replace(math_element, image)
	new_html = _serialize(root)
	return new_html


#============================================
def is_rendered_image_ref(source: str) -> bool:
	"""Return whether source is an opaque reference to a generated PNG."""
	result = source.startswith((RDKIT_IMAGE_PREFIX, MATHML_IMAGE_PREFIX))
	return result


#============================================
def standalone_rendered_image_refs(html: str) -> list:
	"""Return generated image references outside drawing tables."""
	root = _parse(html)
	refs = []
	for image in root.xpath('.//img'):
		source = image.get('src', '')
		if not is_rendered_image_ref(source):
			continue
		if image.xpath('ancestor::table'):
			continue
		refs.append(source)
	return refs


#============================================
def embed_rendered_images_in_table(table_html: str, image_store: dict) -> str:
	"""Replace generated image references in a table with PNG data URLs."""
	if not any(prefix in table_html for prefix in (
			RDKIT_IMAGE_PREFIX, MATHML_IMAGE_PREFIX)):
		return table_html
	root = _parse(table_html)
	for image in root.xpath('.//img'):
		source = image.get('src', '')
		if not is_rendered_image_ref(source):
			continue
		if source.startswith(RDKIT_IMAGE_PREFIX):
			key = source[len(RDKIT_IMAGE_PREFIX):]
		else:
			key = source[len(MATHML_IMAGE_PREFIX):]
		if key not in image_store:
			raise ValueError(f"table refers to missing rendered image {key!r}")
		encoded = base64.b64encode(image_store[key]).decode('ascii')
		image.set('src', f'data:image/png;base64,{encoded}')
	return _serialize(root)


#============================================
def _serialize(root: lxml.html.HtmlElement) -> str:
	"""Serialize a wrapper element back to an ASCII HTML fragment."""
	html = qti_package_maker.html_to_image.selectors.serialize_fragment(root)
	return html


#============================================
def split_question_code(html: str) -> tuple:
	"""Split a leading `<p>CRC</p>` code paragraph off a bbq statement.

	Args:
		html: Statement HTML as written by bptools.

	Returns:
		(code, remaining_html); code is '' when no code paragraph leads.
	"""
	root = _parse(html)
	first = root[0] if len(root) > 0 else None
	# the code paragraph is the first element, holds only text, and matches
	# the CRC pattern (hex groups joined by underscores)
	if first is None or first.tag != 'p' or len(first) > 0:
		return '', html
	text = (first.text or '').strip()
	if not ef_tools.html_parse.is_question_code(text):
		return '', html
	# keep any tail text that followed the code paragraph
	tail = first.tail or ''
	root.remove(first)
	root.text = (root.text or '') + tail
	remaining = _serialize(root)
	return text, remaining


#============================================
def pull_tables(html: str) -> tuple:
	"""Remove every table from html and return them separately for rendering.

	bptools uses tables as drawings: gels, chi-square critical values,
	metabolic pathways with arrows, genotype grids, and one-row DNA
	sequence strips with one boxed cell per base. Most carry bgcolor or
	border cell styles (qti_package_maker's drawing detector), but pathway
	and genotype tables style only the table element, so every table is
	rasterized; the boxes are the point of the drawing, so none is
	flattened to text.

	Args:
		html: Statement, prompt, or choice HTML.

	Returns:
		(html_without_tables, [table_html, ...]) in document order.
	"""
	root = _parse(html)
	tables = []
	# outermost tables only: a nested table (agglutination wells inside a
	# tray table) is part of its parent's drawing
	for table in root.xpath('.//table[not(ancestor::table)]'):
		tables.append(qti_package_maker.html_to_image.selectors.outer_html(table))
		# preserve tail text by moving it to the previous sibling or parent
		parent = table.getparent()
		previous = table.getprevious()
		tail = table.tail or ''
		if previous is not None:
			previous.tail = (previous.tail or '') + tail
		else:
			parent.text = (parent.text or '') + tail
		parent.remove(table)
	remaining = _serialize(root)
	return remaining, tables


#============================================
def _escape_text(text: str) -> str:
	"""Escape text for the exam YAML inline-HTML vocabulary.

	Keeps the output ASCII (entities for non-ASCII) and re-escapes `<`, `>`,
	and `&` so literal characters in question text survive the builder's
	tag parser.
	"""
	# non-breaking spaces are layout padding in bptools output
	plain = text.replace(' ', ' ')
	escaped = plain.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
	escaped = escaped.encode('ascii', 'xmlcharrefreplace').decode('ascii')
	return escaped


#============================================
def _emit(element: lxml.html.HtmlElement, parts: list) -> None:
	"""Append the exam-text rendering of element and its children to parts."""
	tag = element.tag
	# comments and processing instructions carry a callable tag; drop them
	if not isinstance(tag, str):
		return
	if tag == 'img':
		if not is_rendered_image_ref(element.get('src', '')):
			raise ValueError('unsupported image markup in answer choice')
		return
	span_color = _span_text_color(element) if tag == 'span' else None
	if tag in HEADING_TAGS:
		parts.append('\n<b>')
	elif tag in BLOCK_TAGS:
		parts.append('\n')
	elif tag == 'li':
		parts.append('\n- ')
	elif tag in BREAK_TAGS:
		parts.append('\n')
	elif tag in INLINE_KEEP_TAGS:
		parts.append(f'<{tag}>')
	elif span_color is not None:
		parts.append(f'<span style="color: {span_color};">')
	elif tag in UNWRAP_TAGS:
		pass
	else:
		raise ValueError(f"unsupported HTML tag in question text: <{tag}>")
	if element.text:
		parts.append(_escape_text(element.text))
	for child in element:
		_emit(child, parts)
		if child.tail:
			parts.append(_escape_text(child.tail))
	if tag in HEADING_TAGS:
		parts.append('</b>\n')
	elif tag in BLOCK_TAGS:
		parts.append('\n')
	elif tag in INLINE_KEEP_TAGS:
		parts.append(f'</{tag}>')
	elif span_color is not None:
		parts.append('</span>')


#============================================
def clean_inline_html(html: str) -> str:
	"""Reduce bptools HTML to the exam YAML inline vocabulary.

	Block tags become newlines (the DOCX builder turns each newline into a
	paragraph), `<h1>`-`<h6>` become bold lines, `<hr>` a line break, `<li>`
	a dash bullet, non-color styling wrappers are dropped, HTML comments
	vanish, and sub/sup/b/strong/i/em/code/tt plus hex text-color spans are
	kept.
	Any other tag raises ValueError.

	Args:
		html: Statement or choice HTML, tables already removed.

	Returns:
		Cleaned text with entities kept escaped.
	"""
	root = _parse(html)
	parts = []
	if root.text:
		parts.append(_escape_text(root.text))
	for child in root:
		_emit(child, parts)
		if child.tail:
			parts.append(_escape_text(child.tail))
	text = ''.join(parts)
	# normalize whitespace: single spaces, no blank lines, trimmed edges
	text = _SPACE_RUN_RE.sub(' ', text)
	text = _SPACE_AROUND_NEWLINE_RE.sub('\n', text)
	text = _BLANK_LINE_RE.sub('\n', text)
	cleaned = text.strip()
	return cleaned


#============================================
def _normalize_statement_text(text: str) -> str:
	"""Apply the statement whitespace rules to one table-separated text run."""
	text = _SPACE_RUN_RE.sub(' ', text)
	text = _SPACE_AROUND_NEWLINE_RE.sub('\n', text)
	text = _BLANK_LINE_RE.sub('\n', text)
	cleaned = text.strip()
	return cleaned


#============================================
def _append_wrapped_text(parts: list, text: str, wrappers: tuple) -> None:
	"""Append escaped text with its active inline wrappers kept balanced."""
	if not text:
		return
	opening = ''.join(pair[0] for pair in wrappers)
	closing = ''.join(pair[1] for pair in reversed(wrappers))
	parts.append(opening + _escape_text(text) + closing)


#============================================
def _append_statement_text_block(statement: list, parts: list) -> None:
	"""Flush collected prose into one normalized statement text block."""
	if not parts:
		return
	text = _normalize_statement_text(''.join(parts))
	if text:
		ef_tools.statement_content.append_text(statement, text)
	parts.clear()


#============================================
def _emit_statement(element: lxml.html.HtmlElement, statement: list,
		parts: list, wrappers: tuple = ()) -> None:
	"""Walk BBQ markup once, retaining table positions in statement order."""
	tag = element.tag
	if not isinstance(tag, str):
		return
	if tag == 'img':
		source = element.get('src', '')
		if not is_rendered_image_ref(source):
			raise ValueError('unsupported image markup in question statement')
		_append_statement_text_block(statement, parts)
		statement.append({'image': source})
		return
	if tag == 'table':
		_append_statement_text_block(statement, parts)
		statement.append({'html_table': qti_package_maker.html_to_image.selectors.outer_html(element)})
		return
	span_color = _span_text_color(element) if tag == 'span' else None
	active_wrappers = wrappers
	if tag in HEADING_TAGS:
		_append_wrapped_text(parts, '\n', wrappers)
		active_wrappers += (('<b>', '</b>'),)
	elif tag in BLOCK_TAGS:
		_append_wrapped_text(parts, '\n', wrappers)
	elif tag == 'li':
		_append_wrapped_text(parts, '\n- ', wrappers)
	elif tag in BREAK_TAGS:
		_append_wrapped_text(parts, '\n', wrappers)
	elif tag in INLINE_KEEP_TAGS:
		active_wrappers += ((f'<{tag}>', f'</{tag}>'),)
	elif span_color is not None:
		active_wrappers += ((f'<span style="color: {span_color};">', '</span>'),)
	elif tag in UNWRAP_TAGS:
		pass
	else:
		raise ValueError(f"unsupported HTML tag in question text: <{tag}>")
	if element.text:
		_append_wrapped_text(parts, element.text, active_wrappers)
	for child in element:
		_emit_statement(child, statement, parts, active_wrappers)
		if child.tail:
			_append_wrapped_text(parts, child.tail, active_wrappers)
	if tag in HEADING_TAGS or tag in BLOCK_TAGS:
		_append_wrapped_text(parts, '\n', wrappers)


#============================================
def clean_statement_content(html: str) -> list:
	"""Convert BBQ statement HTML to ordered prose and drawing-table blocks."""
	root = _parse(html)
	statement = []
	parts = []
	if root.text:
		_append_wrapped_text(parts, root.text, ())
	for child in root:
		_emit_statement(child, statement, parts)
		if child.tail:
			_append_wrapped_text(parts, child.tail, ())
	_append_statement_text_block(statement, parts)
	return statement


#============================================
def _flatten_on_white(image: PIL.Image.Image) -> PIL.Image.Image:
	"""Return an RGB copy of image composited over a white background.

	Element screenshots can carry an alpha channel. Comparing such an image
	against solid white directly would treat transparent pixels as content, so
	the alpha is resolved against white first -- the same background the
	renderer draws on.
	"""
	if image.mode == 'RGB':
		return image.convert('RGB')
	rgba = image.convert('RGBA')
	backdrop = PIL.Image.new('RGBA', rgba.size, (255, 255, 255, 255))
	flattened = PIL.Image.alpha_composite(backdrop, rgba).convert('RGB')
	return flattened


#============================================
def autocrop_white_border(image: PIL.Image.Image) -> PIL.Image.Image:
	"""Trim the uniform white margin around a rendered drawing.

	The renderer screenshots a table element, but a drawing can still sit
	inside a fixed-size wrapper whose declared height and width leave dead
	space (the restriction maps declare a 136 px tall box around a 6 px bar).
	Cropping removes only outer pixels; the pixels-per-inch of what remains is
	unchanged, so the printed size of the content inside is identical. That is
	what lets autocrop coexist with fixed-scale sizing.

	Args:
		image: The rendered PNG, any mode.

	Returns:
		The cropped RGB image, or the flattened original when it is blank.
	"""
	flattened = _flatten_on_white(image)
	white = PIL.Image.new('RGB', flattened.size, (255, 255, 255))
	difference = PIL.ImageChops.difference(flattened, white)
	bbox = difference.getbbox()
	# An all-white render has no content box; keep it rather than crop to nothing.
	if bbox is None:
		return flattened
	left, top, right, bottom = bbox
	# Grow the box by the bleed, clamped to the image so the crop stays valid.
	left = max(0, left - AUTOCROP_BLEED_PX)
	top = max(0, top - AUTOCROP_BLEED_PX)
	right = min(flattened.width, right + AUTOCROP_BLEED_PX)
	bottom = min(flattened.height, bottom + AUTOCROP_BLEED_PX)
	cropped = flattened.crop((left, top, right, bottom))
	return cropped


#============================================
def _write_rendered_png(png_bytes: bytes, png_path: str) -> None:
	"""Autocrop one rendered PNG and save it carrying its true resolution.

	The saved pHYs chunk records RENDER_DPI so the DOCX builder can recover the
	image's real physical size instead of assuming a 96 px/in baseline.
	"""
	with PIL.Image.open(io.BytesIO(png_bytes)) as image:
		cropped = autocrop_white_border(image)
	cropped.save(png_path, format='PNG', dpi=(RENDER_DPI, RENDER_DPI))


#============================================
@functools.lru_cache(maxsize=1)
def _html_table_font_style() -> str:
	"""Return the exam font rules for Chromium-rendered drawing tables."""
	fonts = ef_tools.style_loader.load_styles()['fonts']
	primary = fonts['primary'].replace('"', '\\"')
	monospace = fonts['monospace'].replace('"', '\\"')
	return (
		'<style>'
		f'table {{ font-family: "{primary}", sans-serif; }}'
		'table [style*="monospace" i], table code, table tt '
		f'{{ font-family: "{monospace}", monospace !important; }}'
		'</style>'
	)


#============================================
def write_table_pngs(table_htmls: list, renderer: object, media_dir: str, stem: str) -> list:
	"""Rasterize drawing tables to PNG files beside the exam YAML.

	Args:
		table_htmls: Table HTML strings from pull_tables.
		renderer: Object with render_table_png(html) -> bytes, normally
			qti_package_maker.html_to_image.render_table.TableRenderer.
		media_dir: Directory for the PNG files, e.g. `<yaml_dir>/<stem>_files`.
		stem: Filename stem, e.g. the question code.

	Returns:
		PNG paths relative to the parent of media_dir (the YAML directory).
	"""
	os.makedirs(media_dir, exist_ok=True)
	yaml_dir = os.path.dirname(os.path.abspath(media_dir))
	paths = []
	for index, table_html in enumerate(table_htmls, start=1):
		styled_table_html = _html_table_font_style() + table_html
		png_bytes = renderer.render_table_png(styled_table_html)
		png_path = os.path.join(media_dir, f"{stem}_table_{index}.png")
		_write_rendered_png(png_bytes, png_path)
		paths.append(os.path.relpath(png_path, yaml_dir))
	return paths
