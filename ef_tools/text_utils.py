"""Text utility functions for exam formatting.

Provides HTML entity decoding, number prefix stripping, and rich text
parsing for inline HTML tags (sub, sup, b, strong, i, em).
"""

# Standard Library
import re
import html


#============================================
def decode_html_entities(text: str) -> str:
	"""Decode HTML entities to Unicode characters for document output.

	YAML files use ASCII HTML entities (e.g., &Delta;, &alpha;) for
	special characters. This converts them to Unicode for rendering.

	Args:
		text: Text that may contain HTML entities.

	Returns:
		Text with entities decoded to Unicode.
	"""
	decoded = html.unescape(text)
	return decoded

assert decode_html_entities("&Delta;G") == "\u0394G"
assert decode_html_entities("plain text") == "plain text"
assert decode_html_entities("&alpha; &beta;") == "\u03b1 \u03b2"


#============================================
def strip_number_prefix(text: str) -> str:
	"""Strip leading question number prefix from statement text.

	Removes patterns like '22) ', '22. ', '3. ' from the start.

	Args:
		text: Statement text that may have a number prefix.

	Returns:
		Text with number prefix removed.
	"""
	stripped = re.sub(r'^\d+[).]\s*', '', text)
	return stripped

assert strip_number_prefix("22) Which of the following") == "Which of the following"
assert strip_number_prefix("3. What is") == "What is"
assert strip_number_prefix("No prefix here") == "No prefix here"


#============================================
# regex pattern to match supported inline HTML tags
# matches <sub>, </sub>, <sup>, </sup>, <b>, </b>, <strong>, </strong>,
# <i>, </i>, <em>, </em>, and <br> variants
_RICH_TEXT_TAG_PATTERN = re.compile(
	r'(<br\s*/?>|</?(?:sub|sup|b|strong|i|em)>)',
	re.IGNORECASE,
)

# map tag names to canonical names for consistent handling
_TAG_ALIASES = {
	'strong': 'b',
	'em': 'i',
}


#============================================
def parse_rich_text(text: str) -> list:
	"""Parse text with inline HTML tags into styled segments.

	Splits text on supported HTML tags and returns a list of
	(text, tags) tuples where tags is a frozenset of active formatting
	tag names. Supported tags: sub, sup, b, strong, i, em.
	Tags strong and em are normalized to b and i respectively.

	Does not handle nested tags of the same type or malformed HTML.
	HTML entities (e.g., &Delta;) are NOT processed here -- use
	decode_html_entities() separately.

	Args:
		text: Text that may contain inline HTML tags.

	Returns:
		List of (text_segment, tags_frozenset) tuples.
	"""
	# split text on tag boundaries, keeping the delimiters
	parts = _RICH_TEXT_TAG_PATTERN.split(text)
	segments = []
	# track currently active tags
	active_tags = set()

	for part in parts:
		if not part:
			continue
		# check if this part is an HTML tag
		if re.match(r'^<br\s*/?>$', part, re.IGNORECASE):
			segments.append(("\n", frozenset(active_tags)))
			continue
		tag_match = re.match(r'^<(/?)(\w+)>$', part)
		if tag_match:
			is_closing = tag_match.group(1) == '/'
			tag_name = tag_match.group(2).lower()
			# normalize aliases
			canonical = _TAG_ALIASES.get(tag_name, tag_name)
			if is_closing:
				active_tags.discard(canonical)
			else:
				active_tags.add(canonical)
		else:
			# plain text segment -- attach current formatting state
			segments.append((part, frozenset(active_tags)))

	return segments

# test: plain text returns single segment with no tags
assert parse_rich_text("hello") == [("hello", frozenset())]
# test: subscript tag
assert parse_rich_text("H<sub>2</sub>O") == [
	("H", frozenset()), ("2", frozenset({"sub"})), ("O", frozenset()),
]
# test: bold tag
assert parse_rich_text("<b>Note:</b> answer") == [
	("Note:", frozenset({"b"})), (" answer", frozenset()),
]
# test: strong normalizes to b
assert parse_rich_text("<strong>x</strong>") == [
	("x", frozenset({"b"})),
]
# test: em normalizes to i
assert parse_rich_text("<em>y</em>") == [
	("y", frozenset({"i"})),
]
