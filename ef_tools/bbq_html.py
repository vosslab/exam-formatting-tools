"""Convert bptools bbq HTML fragments into exam YAML text and table sources.

bptools question text arrives as HTML: a leading `<p>CRC</p>` code, `<p>`
and `<h6>` blocks, colored `<span>` wrappers, and drawing `<table>`s (gels,
chi-square critical values, test-cross counts). The DOCX builder understands
only the inline tags in ef_tools.text_utils (sub, sup, b, strong, i, em), so
this module reduces the HTML to that vocabulary and pulls drawing tables out
for the rasterized fallback; the original table HTML remains available for
the optional native DOCX table backend.
"""

# Standard Library
import os
import re

# PIP3 modules
import lxml.html

# local repo modules
import ef_tools.html_parse
import qti_package_maker.html_to_image.selectors


# tags whose content is re-emitted wrapped in the same bare tag
INLINE_KEEP_TAGS = ('sub', 'sup', 'b', 'strong', 'i', 'em')
# tags that only add a paragraph boundary around their content
BLOCK_TAGS = ('p', 'div', 'ul', 'ol')
# section headings become their own bold line
HEADING_TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
# empty tags that become a line break
BREAK_TAGS = ('br', 'hr')
# tags dropped entirely, keeping their text
UNWRAP_TAGS = ('span', 'font', 'a', 'u', 'small', 'big', 'code', 'tt')

# whitespace normalization
_SPACE_RUN_RE = re.compile(r'[ \t]+')
_BLANK_LINE_RE = re.compile(r'\n\s*\n+')
_SPACE_AROUND_NEWLINE_RE = re.compile(r' *\n *')
_HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$')


#============================================
def _span_text_color(element: lxml.html.HtmlElement) -> str | None:
	"""Return a normalized hex text color from a span's inline style.

	Only the text-color declaration is part of the printable exam contract.
	Other span CSS (including anti-cheat font sizing) remains presentation
	metadata and is intentionally discarded.
	"""
	style = element.get('style', '')
	for declaration in style.split(';'):
		if ':' not in declaration:
			continue
		property_name, value = declaration.split(':', 1)
		if property_name.strip().lower() != 'color':
			continue
		color = value.strip()
		if not _HEX_COLOR_RE.fullmatch(color):
			return None
		if len(color) == 4:
			color = '#' + ''.join(character * 2 for character in color[1:])
		return color.lower()
	return None


#============================================
def _parse(html: str) -> lxml.html.HtmlElement:
	"""Parse an HTML fragment into a wrapper div element."""
	root = qti_package_maker.html_to_image.selectors.parse_html_fragment(html)
	return root


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
	vanish, and sub/sup/b/strong/i/em plus hex text-color spans are kept.
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
		png_bytes = renderer.render_table_png(table_html)
		png_path = os.path.join(media_dir, f"{stem}_table_{index}.png")
		with open(png_path, 'wb') as handle:
			handle.write(png_bytes)
		paths.append(os.path.relpath(png_path, yaml_dir))
	return paths
