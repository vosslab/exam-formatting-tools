"""Convert bptools bbq HTML fragments into exam YAML text and table sources.

bptools question text arrives as HTML: a leading `<p>CRC</p>` code, `<p>`
and `<h6>` blocks, colored `<span>` wrappers, and drawing `<table>`s (gels,
chi-square critical values, test-cross counts). The DOCX builder understands
only the inline tags in ef_tools.text_utils (sub, sup, b, strong, i, em,
code, tt), so
this module reduces the HTML to that vocabulary and pulls drawing tables out
for image capture; the original table HTML remains available for
the optional native DOCX table backend.
"""

# Standard Library
import os
import re
import html

# PIP3 modules
import lxml.html

# local repo modules
import ef_tools.html_parse
import ef_tools.svg_media
import ef_tools.text_utils
import ef_tools.statement_content


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
RENDERED_IMAGE_PREFIX = 'rendered:'

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
	root = lxml.html.fragment_fromstring(html or '<div></div>', create_parent='div')
	return root


#============================================
def is_rendered_image_ref(source: str) -> bool:
	"""Return whether source is an opaque reference to a generated image."""
	result = source.startswith(RENDERED_IMAGE_PREFIX)
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
def _serialize(root: lxml.html.HtmlElement) -> str:
	"""Serialize a wrapper element back to an ASCII HTML fragment."""
	parts = [html.escape(root.text or '', quote=False)]
	parts.extend(lxml.html.tostring(child, encoding='unicode') for child in root)
	serialized = ''.join(parts).encode('ascii', 'xmlcharrefreplace').decode('ascii')
	return serialized


#============================================
def outer_html(element: lxml.html.HtmlElement) -> str:
	"""Serialize an element without duplicating its following text."""
	serialized = lxml.html.tostring(element, encoding='unicode', with_tail=False)
	return serialized


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
	border cell styles on the cells, but pathway
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
		tables.append(outer_html(table))
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
		statement.append({'html_table': outer_html(element)})
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
def write_table_images(table_htmls: list, renderer: object, media_dir: str, stem: str,
			rendered_images: dict = None) -> list:
	"""Save table captures, returning paths relative to the YAML directory.

	Question-context captures are supplied by the parser. Standalone table
	callers use the same renderer directly. SVG and fallback PNG bytes are preserved.
	"""
	os.makedirs(media_dir, exist_ok=True)
	yaml_dir = os.path.dirname(os.path.abspath(media_dir))
	paths = []
	for index, table_html in enumerate(table_htmls, start=1):
		root = _parse(table_html)
		table = root.xpath('.//table')[0]
		key = table.get('data-ef-image')
		if key is not None:
			image_bytes = rendered_images[key]
		else:
			image_bytes = renderer.render(table_html, {'table': None})['table']
		extension = 'svg' if ef_tools.svg_media.is_svg(image_bytes) else 'png'
		image_path = os.path.join(media_dir, f"{stem}_table_{index}.{extension}")
		with open(image_path, 'wb') as handle:
			handle.write(image_bytes)
		paths.append(os.path.relpath(image_path, yaml_dir))
	return paths
