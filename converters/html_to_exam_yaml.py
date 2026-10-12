#!/usr/bin/env python3
"""Convert cleaned Blackboard HTML exam exports to exam YAML."""

# Standard Library
import argparse
import copy
import datetime
import html
import os
import re
from pathlib import Path

# Pip Modules
import lxml.html

# Local Repo Modules
import ef_tools.cli_checks
import ef_tools.html_parse
import ef_tools.html_renderer
import ef_tools.exam_yaml_writer
import ef_tools.statement_content
import ef_tools.style_loader
import ef_tools.svg_media
import ef_tools.text_utils


TAKE_QUESTION_XPATH = ef_tools.html_parse.TAKE_QUESTION_XPATH
IMAGE_CLASS_XPATH = ef_tools.html_parse.IMAGE_CLASS_XPATH
INLINE_TAGS = ef_tools.html_parse.INLINE_TAGS
CHOICE_ITEM_XPATH = (
	".//div[contains(concat(' ', normalize-space(@class), ' '), ' cleaned-choice-item ')]"
)
CAPTURE_ATTRIBUTE = 'data-ef-capture'
# Lettered options (A./B./C./D.) live in spans with white-space:nowrap.
# In bptools MATCH terminology these are the choices_list.
MATCHING_CHOICE_XPATH = ".//span[contains(@style, 'white-space:nowrap')]"
# Numbered prompts (with the empty-box marker) live as inline-block spans.
# In bptools MATCH terminology these are the prompts_list. The marker is the
# bordered, empty inline-block span next to the prompt text; tightening the
# XPath to require both `border` styling and no inner text keeps non-matching
# hint legends (which use display:inline-block on bold terms) out of the
# matching branch.
MATCHING_PROMPT_MARKER_XPATH = (
	".//span[contains(@style, 'display:inline-block') "
	"and contains(@style, 'border') "
	"and not(normalize-space(.))]"
)


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Convert cleaned Blackboard HTML files into exam YAML."
	)
	parser.add_argument(
		"-i", "--input", dest="input_files", nargs="+", required=True,
		help="Input cleaned HTML file(s), in document order."
	)
	parser.add_argument(
		"-o", "--output", dest="output_file", default=None,
		help="Output YAML file path. Defaults to <first-input-stem>.yml in CWD."
	)
	parser.add_argument(
		"-t", "--title", dest="title", default="Final Exam",
		help="Exam title."
	)
	parser.add_argument(
		"--date", dest="date", default=None,
		help="ISO exam date. Defaults to today."
	)
	args = parser.parse_args()
	return args


#============================================
def escape_text(text: str) -> str:
	"""Escape plain text for inline HTML while keeping output ASCII."""
	normalized = re.sub(r"\s+", " ", text)
	escaped = html.escape(normalized, quote=False)
	escaped = escaped.encode("ascii", "xmlcharrefreplace").decode("ascii")
	return escaped


#============================================
def element_to_inline_html(element: object) -> str:
	"""Convert supported inline HTML content to a compact ASCII HTML string."""
	parts = []
	if element.text:
		parts.append(escape_text(element.text))
	for child in element:
		tag = child.tag.lower() if isinstance(child.tag, str) else ""
		if tag in ("input", "script", "style", "canvas", "img"):
			if child.tail:
				parts.append(escape_text(child.tail))
			continue
		if tag == "br":
			parts.append("\n")
		elif tag == "span":
			color = ef_tools.text_utils.text_color_from_style(child.get("style", ""))
			if color:
				parts.append(f'<span style="color: {color};">')
				parts.append(element_to_inline_html(child))
				parts.append("</span>")
			else:
				parts.append(element_to_inline_html(child))
		elif tag in INLINE_TAGS:
			canonical = tag
			if tag == "strong":
				canonical = "b"
			elif tag == "em":
				canonical = "i"
			parts.append(f"<{canonical}>")
			parts.append(element_to_inline_html(child))
			parts.append(f"</{canonical}>")
		else:
			parts.append(element_to_inline_html(child))
			if tag in ("div", "p", "li"):
				parts.append("\n")
		if child.tail:
			parts.append(escape_text(child.tail))
	result = "".join(parts)
	result = re.sub(r"[ \t\r\f\v]+", " ", result)
	result = re.sub(r" *\n *", "\n", result)
	result = re.sub(r"\n+", "\n", result)
	result = re.sub(r"<(sub|sup|b|i)>\s+", r"<\1>", result)
	result = re.sub(r"\s+</(sub|sup|b|i)>", r"</\1>", result)
	result = re.sub(r"\s+<(sub|sup)>", r"<\1>", result)
	result = re.sub(r"</(sub|sup)> +(?=[A-Z0-9(<])", r"</\1>", result)
	return result.strip()


#============================================
def _flush_statement_text(statement: list, parts: list, before_media: bool = False) -> None:
	"""Merge one adjacent text run into the ordered statement blocks."""
	if not parts:
		return
	text = ''.join(parts)
	text = re.sub(r"[ \t\r\f\v]+", " ", text)
	text = re.sub(r" *\n *", "\n", text)
	text = re.sub(r"\n+", "\n", text)
	text = re.sub(r"<(sub|sup|b|i)>\s+", r"<\1>", text)
	text = re.sub(r"\s+</(sub|sup|b|i)>", r"</\1>", text)
	text = re.sub(r"\s+<(sub|sup)>", r"<\1>", text)
	text = re.sub(r"</(sub|sup)> +(?=[A-Z0-9(<])", r"</\1>", text)
	if before_media:
		text = text.rstrip()
	if text:
		ef_tools.statement_content.append_text(statement, text)
	parts.clear()


#============================================
def element_to_statement_content(html_path: str, element: object,
		captured_media: dict[str, dict] | None = None) -> list:
	"""Convert a statement DOM subtree to ordered text and image blocks."""
	statement = []
	parts = []

	def append_text(text: str) -> None:
		if text:
			parts.append(escape_text(text))

	def append_media(media: dict, wrappers: tuple) -> None:
		parts.extend(pair[1] for pair in reversed(wrappers))
		_flush_statement_text(statement, parts, before_media=True)
		statement.append(media)
		parts.extend(pair[0] for pair in wrappers)

	def visit(node: object, wrappers: tuple = ()) -> None:
		tag = node.tag.lower() if isinstance(node.tag, str) else ""
		if tag in ("input", "script", "style", "h5"):
			return
		classes = set(node.get("class", "").split())
		capture_id = node.get(CAPTURE_ATTRIBUTE)
		if captured_media and capture_id in captured_media:
			append_media(captured_media[capture_id], wrappers)
			return
		if tag == "img" and "cleaned-statement-media" in classes:
			src = node.get("src", "")
			if src:
				append_media(
					{'image': ef_tools.html_parse.resolve_image_path(html_path, src)}, wrappers)
			return
		if tag == "br":
			append_text("\n")
			return
		active_wrappers = wrappers
		if tag in INLINE_TAGS:
			canonical = {"strong": "b", "em": "i"}.get(tag, tag)
			pair = (f"<{canonical}>", f"</{canonical}>")
			parts.append(pair[0])
			active_wrappers += (pair,)
		elif tag == "span":
			color = ef_tools.text_utils.text_color_from_style(node.get("style", ""))
			if color:
				pair = (f'<span style="color: {color};">', "</span>")
				parts.append(pair[0])
				active_wrappers += (pair,)
		if node.text:
			append_text(node.text)
		for child in node:
			visit(child, active_wrappers)
			if child.tail:
				append_text(child.tail)
		if tag in ("div", "p", "li"):
			append_text("\n")
		if active_wrappers != wrappers:
			parts.append(active_wrappers[-1][1])

	if element.text:
		append_text(element.text)
	for child in element:
		visit(child)
		if child.tail:
			append_text(child.tail)
	_flush_statement_text(statement, parts)
	# Block wrappers add hard breaks. They are meaningful between content, but
	# should not leave padding before the question number or after its final line.
	statement[:] = [
		block for block in statement
		if 'image' in block or block['text'].strip()
	]
	text_blocks = [block for block in statement if 'text' in block]
	if text_blocks:
		text_blocks[0]['text'] = text_blocks[0]['text'].lstrip()
		text_blocks[-1]['text'] = text_blocks[-1]['text'].rstrip()
	return statement


#============================================
def clean_choice_html(text: str) -> str:
	"""Remove exported A./B. prefixes from choice text HTML."""
	text = re.sub(r"^\s*[A-Z][.)]\s+", "", text)
	return text.strip()


#============================================
def clean_statement_html(text: str) -> str:
	"""Remove leading hidden question codes from statement HTML."""
	text = re.sub(
		r"^\s*[0-9a-f]{2,}(?:_[0-9a-f]{2,})*\s+",
		"",
		text,
		flags=re.IGNORECASE,
	)
	return text.strip()


#============================================
def is_matching_block(element: object) -> bool:
	"""Return whether an element contains a Blackboard matching block."""
	choices = element.xpath(MATCHING_CHOICE_XPATH)
	prompt_markers = element.xpath(MATCHING_PROMPT_MARKER_XPATH)
	result = len(choices) > 0 and len(prompt_markers) > 0
	return result


#============================================
def parse_matching_block(element: object) -> tuple[list[str], list[str]]:
	"""Parse matching prompts and choices from a Blackboard matching block.

	Returns a (prompts_list, choices_list) tuple matching the bptools
	MATCH item shape: prompts_list are the numbered items, choices_list
	are the lettered (A/B/C/D) options.
	"""
	# Lettered choices: strip leading 'A. '/'B) ' style prefix.
	choices_list = []
	for choice_element in element.xpath(MATCHING_CHOICE_XPATH):
		choice = element_to_inline_html(choice_element)
		choice = clean_choice_html(choice)
		if choice:
			choices_list.append(choice)
	# Numbered prompts: anchored by the empty inline-block "blank" marker.
	prompts_list = []
	for marker in element.xpath(MATCHING_PROMPT_MARKER_XPATH):
		parent = marker.getparent()
		if parent is None:
			continue
		prompt = element_to_inline_html(parent)
		prompt = prompt.replace("&#160;", "").strip()
		if prompt:
			prompts_list.append(prompt)
	return prompts_list, choices_list


#============================================
def compute_rendered_out_dir(html_path: str, doc_root: object) -> str:
	"""Pick the directory where browser-rendered PNGs should be saved.

	Prefer an existing cleaned image directory. Otherwise use the matching
	Blackboard ``<stem>_files`` directory.
	"""
	for image in doc_root.xpath(IMAGE_CLASS_XPATH):
		src = image.get("src", "")
		if not src or src.startswith(("http://", "https://")):
			continue
		image_path = ef_tools.html_parse.resolve_image_path(html_path, src)
		out_dir = os.path.dirname(image_path)
		if out_dir:
			return out_dir
	stem = os.path.splitext(os.path.basename(html_path))[0]
	if stem.lower().startswith("cleaned_"):
		stem = stem[len("cleaned_"):]
	out_dir = os.path.join(os.path.dirname(html_path), f"{stem}_files")
	return out_dir


#============================================
def resolve_images(html_path: str, element: object,
		captured_media: dict[str, dict] | None = None) -> list[dict]:
	"""Resolve direct images and browser captures in DOM order."""
	images = []
	for node in element.iter():
		tag = node.tag.lower() if isinstance(node.tag, str) else ""
		classes = set(node.get("class", "").split())
		if tag == "img" and classes & {
			"cleaned-statement-media", "cleaned-choice-media"}:
			src = node.get("src", "")
			if src:
				images.append({'image': ef_tools.html_parse.resolve_image_path(html_path, src)})
		capture_id = node.get(CAPTURE_ATTRIBUTE)
		if captured_media and capture_id in captured_media:
			images.append(captured_media[capture_id])
	return images


#============================================
def _is_capture_table(table: object) -> bool:
	"""Return whether a table needs browser capture rather than text parsing."""
	return table.get('role') == 'img'


#============================================
def _captured_table_html(table: object) -> str:
	"""Serialize table source for the optional native-DOCX table path."""
	table_copy = copy.deepcopy(table)
	table_copy.attrib.pop(CAPTURE_ATTRIBUTE, None)
	return lxml.html.tostring(table_copy, encoding='unicode', method='html')


#============================================
def _capture_question_media(html_path: str, question_div: object,
		renderer: object, html_context: object | None, label: str,
		out_dir: str) -> dict[str, dict]:
	"""Capture unsupported browser content and return YAML media mappings.

	The complete document is supplied when available. This lets a loader script
	in one part of a Blackboard question populate a canvas elsewhere in it.
	"""
	targets = {}
	target_metadata = {}
	selector_ids = {}
	capture_nodes = []
	for table in question_div.xpath('.//table'):
		if not _is_capture_table(table):
			continue
		if any(ancestor in capture_nodes for ancestor in table.iterancestors()):
			continue
		capture_nodes.append(table)
	for node in question_div.xpath('.//canvas | .//*[local-name() = "math"]'):
		if any(ancestor in capture_nodes for ancestor in node.iterancestors()):
			continue
		capture_nodes.append(node)
	styles = ef_tools.style_loader.load_styles()
	standalone_width = styles['page']['image_max_width']
	for index, node in enumerate(capture_nodes, start=1):
		capture_id = f'{label}-{index}'
		node.set(CAPTURE_ATTRIBUTE, capture_id)
		selector = f'[{CAPTURE_ATTRIBUTE}="{capture_id}"]'
		is_table = node.tag.lower() == 'table'
		targets[selector] = None if is_table else standalone_width
		selector_ids[selector] = capture_id
		target_metadata[capture_id] = {
			'is_table': is_table,
			'table_html': _captured_table_html(node) if is_table else None,
		}
	if not targets:
		return {}
	if html_context is None:
		html_context = lxml.html.tostring(question_div, encoding='unicode', method='html')
	elif not isinstance(html_context, str):
		html_context = lxml.html.tostring(html_context, encoding='unicode', method='html')
	captures = renderer.render(
		html_context, targets, base_url=Path(html_path).resolve().as_uri(), label=label)
	if set(captures) != set(targets):
		missing = sorted(set(targets) - set(captures))
		extra = sorted(set(captures) - set(targets))
		raise ValueError(
			f'{label}: renderer returned unexpected capture targets; '
			f'missing={missing}, extra={extra}')
	os.makedirs(out_dir, exist_ok=True)
	media = {}
	for selector, image_bytes in captures.items():
		capture_id = selector_ids[selector]
		metadata = target_metadata[capture_id]
		extension = 'svg' if ef_tools.svg_media.is_svg(image_bytes) else 'png'
		path = os.path.join(out_dir, f'rendered_{capture_id}.{extension}')
		with open(path, 'wb') as handle:
			handle.write(image_bytes)
		block = {'image': path}
		if metadata['is_table']:
			block['html_table'] = metadata['table_html']
		media[capture_id] = block
	return media


#============================================
def parse_choices(html_path: str, element: object,
		captured_media: dict[str, dict] | None = None) -> list:
	"""Parse multiple-choice labels from an HTML element."""
	choices = []
	labels = element.xpath(".//label[.//input]")
	choice_elements = labels
	if not choice_elements:
		choice_elements = element.xpath(CHOICE_ITEM_XPATH)
	for choice_element in choice_elements:
		choice = {}
		text = clean_choice_html(element_to_inline_html(choice_element))
		if text:
			choice["text"] = text
		images = resolve_images(html_path, choice_element, captured_media)
		if images:
			choice.update(images[0])
		if set(choice.keys()) == {"text"}:
			choices.append(choice["text"])
		else:
			choices.append(choice)
	return choices


#============================================
def remove_node(element: object) -> None:
	"""Detach an element from its parent if it has one."""
	parent = element.getparent()
	if parent is not None:
		parent.remove(element)


#============================================
def remove_statement_noise(element: object) -> None:
	"""Remove non-statement scaffolding from a deep-copied question body.

	Strips script/style/input/h5 nodes (Blackboard scaffolding that never
	belongs in the prose) and any direct child whose text is just a hidden
	question-code marker.
	"""
	for child in list(element):
		tag = child.tag.lower() if isinstance(child.tag, str) else ""
		if tag in ("script", "style", "input", "h5"):
			remove_node(child)
			continue
		if child.get(CAPTURE_ATTRIBUTE) or child.xpath(f'.//*[@{CAPTURE_ATTRIBUTE}]'):
			continue
		text = ef_tools.html_parse.text_from_element(child)
		if ef_tools.html_parse.is_question_code(text):
			remove_node(child)


#============================================
def remove_choice_blocks(element: object) -> None:
	"""Remove only the leaf choice nodes from a deep-copied question body.

	Leaf-only by design: a wrapper <div> may contain BOTH statement text
	and the choice labels, so removing ancestor divs would silently drop
	statement prose. Empty wrapper divs left behind are absorbed by
	element_to_inline_html's whitespace collapsing.
	"""
	for node in element.xpath(".//label[.//input]"):
		remove_node(node)
	for node in element.xpath(CHOICE_ITEM_XPATH):
		remove_node(node)


#============================================
def remove_matching_blocks(element: object) -> None:
	"""Remove direct-child matching blocks from a deep-copied body.

	Matching blocks contribute prompts_list/choices_list separately and
	must not bleed into the statement.
	"""
	for child in list(element):
		if is_matching_block(child):
			remove_node(child)


#============================================
def parse_question(html_path: str, question_div: object,
		renderer: object = None, html_context: object | None = None,
		rendered_out_dir: str | None = None, label: str = 'question') -> dict:
	"""Parse one cleaned Blackboard question div into YAML data.

	Statement extraction is subtractive: the question body is deep-copied,
	choice/matching/noise subtrees are pruned from the copy, and
	element_to_inline_html is called once on what remains. This preserves
	lxml's natural ordering of .text, child text, inline tag wrappers, and
	.tail in one pass instead of trying to glue inline fragments back
	together in a Python loop.
	"""
	li_elements = question_div.xpath("./li")
	if li_elements:
		body = li_elements[0]
	else:
		body = question_div
	if renderer is None:
		with ef_tools.html_renderer.HtmlRenderer() as active_renderer:
			return parse_question(
				html_path, question_div, active_renderer, html_context,
				rendered_out_dir, label)
	if rendered_out_dir is None:
		rendered_out_dir = compute_rendered_out_dir(html_path, question_div)
	captured_media = _capture_question_media(
		html_path, question_div, renderer, html_context, label, rendered_out_dir)
	# Choices and matching are extracted from the original (un-pruned) body
	# so browser captures retain their original question context.
	choices = []
	prompts_list = []
	choices_list = []
	for child in body:
		if ef_tools.html_parse.has_choice_labels(child) or child.xpath(CHOICE_ITEM_XPATH):
			choices = parse_choices(html_path, child, captured_media)
			continue
		if is_matching_block(child):
			block_prompts, block_choices = parse_matching_block(child)
			prompts_list.extend(block_prompts)
			choices_list.extend(block_choices)
			continue
	# Build the statement on a pruned deep copy so .tail and inline tag
	# wrappers (<b>, <i>, <sub>, <sup>) round-trip correctly.
	statement_body = copy.deepcopy(body)
	remove_statement_noise(statement_body)
	remove_choice_blocks(statement_body)
	remove_matching_blocks(statement_body)
	# Resolve text and media together against the pruned body so their source
	# order is preserved and choice images cannot leak into the statement.
	statement = element_to_statement_content(
		html_path, statement_body, captured_media)
	question = {
		"statement": statement,
	}
	if choices:
		question["choices"] = choices
	if prompts_list:
		question["prompts_list"] = prompts_list
	if choices_list:
		question["choices_list"] = choices_list
	return question


#============================================
def parse_html_file(path: str) -> dict:
	"""Parse one cleaned Blackboard HTML file into a section dict."""
	with open(path, "r", encoding="utf-8") as handle:
		html_text = handle.read()
	html_doc = lxml.html.fromstring(html_text)
	rendered_out_dir = compute_rendered_out_dir(path, html_doc)
	questions = []
	with ef_tools.html_renderer.HtmlRenderer() as renderer:
		for index, question_div in enumerate(html_doc.xpath(TAKE_QUESTION_XPATH), start=1):
			questions.append(parse_question(
				path, question_div, renderer, html_doc, rendered_out_dir,
				label=f'question-{index}'))
	section = {
		"heading": ef_tools.html_parse.extract_document_title(path),
		"questions": questions,
	}
	return section


#============================================
def build_yaml(input_files: list[str], title: str, date: str) -> dict:
	"""Build complete exam YAML data from cleaned HTML files."""
	sections = []
	for input_file in input_files:
		sections.append(parse_html_file(input_file))
	exam_data = {
		"title": title,
		"date": date,
		"sections": sections,
	}
	return exam_data


#============================================
def relativize_image_paths(exam_data: dict, yaml_dir: str) -> None:
	"""Rewrite every image path in exam_data relative to yaml_dir, in place.

	Covers ordered statement blocks and structured choice objects.
	"""
	for section in exam_data["sections"]:
		for question in section.get("questions", []):
			for block in question.get("statement", []):
				if block.get("image"):
					block["image"] = os.path.relpath(block["image"], yaml_dir)
			for choice in question.get("choices", []):
				if isinstance(choice, dict) and choice.get("image"):
					choice["image"] = os.path.relpath(choice["image"], yaml_dir)


#============================================
def main() -> None:
	"""Main entry point."""
	args = parse_args()
	# validate every input HTML extension
	for input_file in args.input_files:
		ef_tools.cli_checks.require_extensions(input_file, ('.html', '.htm'), 'input')
	# resolve default output (first input's stem) and validate extension
	output_file = args.output_file
	if output_file is None:
		output_file = ef_tools.cli_checks.default_output_path(args.input_files[0], '.yml')
	ef_tools.cli_checks.require_extensions(output_file, ('.yml', '.yaml'), 'output')
	if os.path.exists(output_file):
		raise FileExistsError(f"Output file already exists: {output_file}")
	if args.date is None:
		date = datetime.date.today().isoformat()
	else:
		date = args.date
	exam_data = build_yaml(args.input_files, args.title, date)
	# image paths are stored relative to the YAML file so the YAML and its
	# media folder can move together (yaml_to_exam_docx.py resolves them
	# against the YAML's directory)
	yaml_dir = os.path.dirname(os.path.abspath(output_file))
	relativize_image_paths(exam_data, yaml_dir)
	ef_tools.exam_yaml_writer.write_exam_yaml(exam_data, output_file)
	question_count = sum(len(section.get("questions", [])) for section in exam_data["sections"])
	print(f"Exam YAML written to {output_file} ({question_count} questions)")


#============================================
if __name__ == "__main__":
	main()
