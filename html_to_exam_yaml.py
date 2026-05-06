#!/usr/bin/env python3
"""Convert cleaned Blackboard HTML exam exports to exam YAML."""

# Standard Library
import argparse
import datetime
import html
import os
import re

# Pip Modules
import lxml.html
import yaml

# Local Repo Modules
import html_exam_docx_builder


TAKE_QUESTION_XPATH = html_exam_docx_builder.TAKE_QUESTION_XPATH
IMAGE_CLASS_XPATH = html_exam_docx_builder.IMAGE_CLASS_XPATH
INLINE_TAGS = html_exam_docx_builder.INLINE_TAGS
CHOICE_ITEM_XPATH = (
	".//div[contains(concat(' ', normalize-space(@class), ' '), ' cleaned-choice-item ')]"
)
MATCHING_TERM_MARKER_XPATH = ".//span[contains(@style, 'display:inline-block')]"
MATCHING_PROMPT_XPATH = ".//span[contains(@style, 'white-space:nowrap')]"


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
		"-o", "--output", dest="output_file", required=True,
		help="Output YAML file path, which must not already exist."
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
	prompts = element.xpath(MATCHING_PROMPT_XPATH)
	term_markers = element.xpath(MATCHING_TERM_MARKER_XPATH)
	result = len(prompts) > 0 and len(term_markers) > 0
	return result


#============================================
def parse_matching_block(element) -> tuple[list[str], list[str]]:
	"""Parse matching prompts and terms from a Blackboard matching block."""
	prompts = []
	for prompt_element in element.xpath(MATCHING_PROMPT_XPATH):
		prompt = element_to_inline_html(prompt_element)
		if prompt:
			prompts.append(prompt)
	terms = []
	for marker in element.xpath(MATCHING_TERM_MARKER_XPATH):
		parent = marker.getparent()
		if parent is None:
			continue
		term = element_to_inline_html(parent)
		term = term.replace("&#160;", "").strip()
		if term:
			terms.append(term)
	return prompts, terms


#============================================
def resolve_images(html_path: str, element) -> list[str]:
	"""Resolve relevant images contained in an element."""
	images = []
	for image in element.xpath(IMAGE_CLASS_XPATH):
		src = image.get("src", "")
		if not src:
			continue
		image_path = html_exam_docx_builder.resolve_image_path(html_path, src)
		images.append(image_path)
	return images


#============================================
def parse_choices(html_path: str, element) -> list:
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
		images = resolve_images(html_path, choice_element)
		if images:
			choice["image"] = images[0]
		if set(choice.keys()) == {"text"}:
			choices.append(choice["text"])
		else:
			choices.append(choice)
	return choices


#============================================
def parse_question(html_path: str, question_div) -> dict:
	"""Parse one cleaned Blackboard question div into YAML data."""
	li_elements = question_div.xpath("./li")
	if li_elements:
		body = li_elements[0]
	else:
		body = question_div
	statement_parts = []
	images = []
	choices = []
	matching_terms = []
	if body.text and body.text.strip():
		body_text = escape_text(body.text.strip())
		if body_text:
			statement_parts.append(body_text)
	for child in body:
		tag = child.tag.lower() if isinstance(child.tag, str) else ""
		if tag in ("script", "style", "input", "h5"):
			continue
		if html_exam_docx_builder.has_choice_labels(child) or child.xpath(CHOICE_ITEM_XPATH):
			choices = parse_choices(html_path, child)
			continue
		if is_matching_block(child):
			prompts, terms = parse_matching_block(child)
			statement_parts.extend(prompts)
			matching_terms.extend(terms)
			continue
		text = html_exam_docx_builder.text_from_element(child)
		if html_exam_docx_builder.is_question_code(text):
			continue
		inline_text = element_to_inline_html(child)
		if inline_text:
			statement_parts.append(inline_text)
		images.extend(resolve_images(html_path, child))
	statement = clean_statement_html("\n".join(statement_parts))
	question = {
		"statement": statement,
	}
	if images:
		question["images"] = images
	if choices:
		question["choices"] = choices
	if matching_terms:
		question["matching_terms"] = matching_terms
	return question


#============================================
def parse_html_file(path: str) -> dict:
	"""Parse one cleaned Blackboard HTML file into a section dict."""
	with open(path, "r", encoding="utf-8") as handle:
		html_text = handle.read()
	html_doc = lxml.html.fromstring(html_text)
	questions = []
	for question_div in html_doc.xpath(TAKE_QUESTION_XPATH):
		questions.append(parse_question(path, question_div))
	section = {
		"heading": html_exam_docx_builder.extract_document_title(path),
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
	if os.path.exists(args.output_file):
		raise FileExistsError(f"Output file already exists: {args.output_file}")
	if args.date is None:
		date = datetime.date.today().isoformat()
	else:
		date = args.date
	exam_data = build_yaml(args.input_files, args.title, date)
	with open(args.output_file, "w", encoding="utf-8") as handle:
		yaml.safe_dump(exam_data, handle, sort_keys=False, allow_unicode=False)
	print(f"Exam YAML written to {args.output_file}")


#============================================
if __name__ == "__main__":
	main()
