#!/usr/bin/env python3
"""Convert cleaned Blackboard HTML exam exports to exam YAML."""

# Standard Library
import argparse
import copy
import datetime
import html
import os
import re

# Pip Modules
import lxml.html
import yaml

# Local Repo Modules
import ef_tools.cli_checks
import ef_tools.html_parse
import ef_tools.rdkit_render


TAKE_QUESTION_XPATH = ef_tools.html_parse.TAKE_QUESTION_XPATH
IMAGE_CLASS_XPATH = ef_tools.html_parse.IMAGE_CLASS_XPATH
INLINE_TAGS = ef_tools.html_parse.INLINE_TAGS
CHOICE_ITEM_XPATH = (
	".//div[contains(concat(' ', normalize-space(@class), ' '), ' cleaned-choice-item ')]"
)
# Canvases that pair with an inline RDKit script. Both statement-media and
# choice-media classes are handled so future exams can place RDKit widgets
# inside answer choices.
RDKIT_CANVAS_XPATH = (
	".//canvas[contains(concat(' ', normalize-space(@class), ' '), ' cleaned-statement-media ') "
	"or contains(concat(' ', normalize-space(@class), ' '), ' cleaned-choice-media ')]"
)
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
def element_to_inline_html(element) -> str:
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
def is_matching_block(element) -> bool:
	"""Return whether an element contains a Blackboard matching block."""
	choices = element.xpath(MATCHING_CHOICE_XPATH)
	prompt_markers = element.xpath(MATCHING_PROMPT_MARKER_XPATH)
	result = len(choices) > 0 and len(prompt_markers) > 0
	return result


#============================================
def parse_matching_block(element) -> tuple[list[str], list[str]]:
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
def compute_rdkit_out_dir(html_path: str, doc_root) -> str:
	"""Pick the directory where RDKit-rendered PNGs should be saved.

	Prefers the directory of an existing cleaned image (so RDKit PNGs sit
	beside Blackboard's exported `*_files/` content). Falls back to a
	`<stem>_files` directory derived from the HTML filename, with any
	leading `Cleaned_` prefix stripped to match Blackboard's convention.

	Args:
		html_path: Path to the source HTML file.
		doc_root: Parsed lxml document root for the same HTML.

	Returns:
		Absolute or repo-relative directory path; not guaranteed to exist
		(`render_smiles_to_png` creates it on first write).
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
def find_rdkit_script_for_canvas(scripts: list, canvas_id: str):
	"""Return the RDKit script element that draws the given canvas id.

	Args:
		scripts: list of lxml `<script>` elements drawn from the question
			subtree (typically `question_div.xpath(".//script")`).
		canvas_id: id attribute of the target `<canvas>` element.

	Returns:
		The first script element whose source contains both the canvas id
		and the `initRDKitModule` token, or None when canvas_id is falsy
		or no script in the list matches.
	"""
	if not canvas_id:
		return None
	for script in scripts:
		text = script.text or ""
		if canvas_id in text and "initRDKitModule" in text:
			return script
	return None


#============================================
def resolve_rdkit_canvases(
	html_path: str, element, script_scope, out_dir: str
) -> list[str]:
	"""Render RDKit canvas widgets in element to PNGs and return paths.

	Canvas elements are searched within `element` only, but the matching
	scripts are searched within `script_scope` because Blackboard cleaned
	exports often place the inline RDKit script in a different `<td>` of
	the same question. Each canvas without a matching script raises
	ValueError to surface conversion gaps loudly.

	Args:
		html_path: Source HTML path (used for error messages only).
		element: lxml subtree to scan for `<canvas>` widgets.
		script_scope: lxml subtree to scan for matching `<script>` blocks.
		out_dir: Destination directory for the generated PNGs.

	Returns:
		Absolute paths of the rendered PNG files in canvas document order.
	"""
	paths = []
	canvases = element.xpath(RDKIT_CANVAS_XPATH)
	if not canvases:
		return paths
	scripts = script_scope.xpath(".//script")
	for canvas in canvases:
		canvas_id = canvas.get("id")
		script = find_rdkit_script_for_canvas(scripts, canvas_id)
		if script is None:
			raise ValueError(
				f"RDKit canvas {canvas_id!r} in {html_path} has no matching script"
			)
		# find_rdkit_script_for_canvas already required initRDKitModule in
		# the script text, so extract_smiles_from_rdkit_script can only
		# return a string here or raise; no None branch to handle.
		smiles = ef_tools.rdkit_render.extract_smiles_from_rdkit_script(script)
		# Filename uses the canvas id directly so each rendered PNG maps
		# obviously back to the source widget on disk.
		basename = f"rdkit_{canvas_id}"
		png_path = ef_tools.rdkit_render.render_smiles_to_png(
			smiles, out_dir, basename=basename
		)
		paths.append(png_path)
	return paths


#============================================
def resolve_images(
	html_path: str, element, script_scope=None, rdkit_out_dir: str | None = None
) -> list[str]:
	"""Resolve relevant images contained in an element.

	Image sources are returned in document order: `<img>` tags first, then
	RDKit canvases re-rendered to PNG via `ef_tools.rdkit_render`. The
	`script_scope` and `rdkit_out_dir` arguments default to None so the
	function can also be used from callers that only need `<img>`
	resolution; current callers always pass both.
	"""
	images = []
	for image in element.xpath(IMAGE_CLASS_XPATH):
		src = image.get("src", "")
		if not src:
			continue
		image_path = ef_tools.html_parse.resolve_image_path(html_path, src)
		images.append(image_path)
	if script_scope is not None and rdkit_out_dir is not None:
		images.extend(resolve_rdkit_canvases(html_path, element, script_scope, rdkit_out_dir))
	return images


#============================================
def parse_choices(
	html_path: str, element, script_scope=None, rdkit_out_dir: str | None = None
) -> list:
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
		images = resolve_images(html_path, choice_element, script_scope, rdkit_out_dir)
		if images:
			choice["image"] = images[0]
		if set(choice.keys()) == {"text"}:
			choices.append(choice["text"])
		else:
			choices.append(choice)
	return choices


#============================================
def remove_node(element) -> None:
	"""Detach an element from its parent if it has one."""
	parent = element.getparent()
	if parent is not None:
		parent.remove(element)


#============================================
def remove_statement_noise(element) -> None:
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
		text = ef_tools.html_parse.text_from_element(child)
		if ef_tools.html_parse.is_question_code(text):
			remove_node(child)


#============================================
def remove_choice_blocks(element) -> None:
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
def remove_matching_blocks(element) -> None:
	"""Remove direct-child matching blocks from a deep-copied body.

	Matching blocks contribute prompts_list/choices_list separately and
	must not bleed into the statement.
	"""
	for child in list(element):
		if is_matching_block(child):
			remove_node(child)


#============================================
def parse_question(
	html_path: str, question_div, rdkit_out_dir: str | None = None
) -> dict:
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
	# Choices and matching are extracted from the original (un-pruned) body
	# so that image/RDKit canvas resolution scope is unchanged.
	choices = []
	prompts_list = []
	choices_list = []
	for child in body:
		if ef_tools.html_parse.has_choice_labels(child) or child.xpath(CHOICE_ITEM_XPATH):
			choices = parse_choices(html_path, child, question_div, rdkit_out_dir)
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
	statement = clean_statement_html(element_to_inline_html(statement_body))
	# Image resolution runs against the pruned body so we don't pull in
	# images that belonged to choices; RDKit script_scope stays the full
	# question_div so canvases on the statement still find their script.
	images = resolve_images(html_path, statement_body, question_div, rdkit_out_dir)
	question = {
		"statement": statement,
	}
	if images:
		question["images"] = images
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
	rdkit_out_dir = compute_rdkit_out_dir(path, html_doc)
	questions = []
	for question_div in html_doc.xpath(TAKE_QUESTION_XPATH):
		questions.append(parse_question(path, question_div, rdkit_out_dir))
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
	# Custom string representer: when a string contains an apostrophe, dump
	# it as a double-quoted scalar instead of single-quoted. PyYAML's default
	# single-quoted form escapes ' as '' (valid YAML 1.1/1.2), but some
	# lenient/legacy validators reject the doubled form, so we sidestep it.
	def _str_representer(dumper: yaml.SafeDumper, value: str):
		if "'" in value:
			return dumper.represent_scalar("tag:yaml.org,2002:str", value, style='"')
		return dumper.represent_scalar("tag:yaml.org,2002:str", value)
	yaml.add_representer(str, _str_representer, Dumper=yaml.SafeDumper)
	with open(output_file, "w", encoding="utf-8") as handle:
		yaml.safe_dump(exam_data, handle, sort_keys=False, allow_unicode=False)
	question_count = sum(len(section.get("questions", [])) for section in exam_data["sections"])
	print(f"Exam YAML written to {output_file} ({question_count} questions)")


#============================================
if __name__ == "__main__":
	main()
