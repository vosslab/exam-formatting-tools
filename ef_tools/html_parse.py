"""Shared HTML parsing helpers for cleaned Blackboard exam exports."""

# Standard Library
import os
import re

# Pip Modules
import lxml.html


# XPath: every cleaned-export question lives in a div.takeQuestionDiv
TAKE_QUESTION_XPATH = (
	"//div[contains(concat(' ', normalize-space(@class), ' '), ' takeQuestionDiv ')]"
)
# XPath: relevant images carry one of two classes added during cleaning
IMAGE_CLASS_XPATH = (
	".//img[contains(concat(' ', normalize-space(@class), ' '), ' cleaned-statement-media ') "
	"or contains(concat(' ', normalize-space(@class), ' '), ' cleaned-choice-media ')]"
)
# Hidden Blackboard-ish question codes look like 42a3_ab0b (hex underscored)
QUESTION_CODE_RE = re.compile(r"^[0-9a-f]{2,}(?:_[0-9a-f]{2,})*$", re.IGNORECASE)
# Leading "A. " or "B) " prefixes on exported choice text
CHOICE_PREFIX_RE = re.compile(r"^[A-Z][.)]\s+")
# Inline HTML tags whose styling is preserved in DOCX output
INLINE_TAGS = {
	"b",
	"strong",
	"i",
	"em",
	"sub",
	"sup",
}


#============================================
def extract_document_title(path: str) -> str:
	"""Extract a readable title from an HTML document."""
	with open(path, "r", encoding="utf-8") as handle:
		text = handle.read()
	doc = lxml.html.fromstring(text)
	title = doc.xpath("string(//title)").strip()
	title = re.sub(r"\s+", " ", title)
	title = title.replace("Preview Test:", "").strip()
	if " - " in title:
		title = title.split(" - ", 1)[0].strip()
	if "-" in title:
		title = title.split("-", 1)[0].strip()
	return title


#============================================
def is_question_code(text: str) -> bool:
	"""Return whether text is a hidden Blackboard-ish question code."""
	clean_text = re.sub(r"\s+", "", text)
	result = bool(QUESTION_CODE_RE.match(clean_text))
	return result


#============================================
def strip_choice_prefix(text: str) -> str:
	"""Remove an existing A./B. choice prefix from exported choice text."""
	clean_text = re.sub(r"\s+", " ", text).strip()
	clean_text = CHOICE_PREFIX_RE.sub("", clean_text)
	return clean_text


#============================================
def resolve_image_path(html_path: str, src: str) -> str:
	"""Resolve an image src relative to its HTML file."""
	if src.startswith(("http://", "https://")):
		raise ValueError(f"Remote image sources are not supported: {src}")
	base_dir = os.path.dirname(html_path)
	image_path = os.path.normpath(os.path.join(base_dir, src))
	return image_path


#============================================
def text_from_element(element) -> str:
	"""Extract normalized text from an HTML element."""
	text = element.text_content()
	text = re.sub(r"\s+", " ", text).strip()
	return text


#============================================
def has_choice_labels(element) -> bool:
	"""Return whether an element contains exported multiple-choice labels."""
	labels = element.xpath(".//label[.//input]")
	result = len(labels) > 0
	return result
