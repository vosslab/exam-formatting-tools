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


#============================================
# pattern to strip supported inline tags while preserving inner text
_INLINE_TAG_STRIP_PATTERN = re.compile(
	r'</?(?:sub|sup|b|strong|i|em)>',
	re.IGNORECASE,
)
# pattern to collapse runs of whitespace to a single space
_WHITESPACE_RUN_PATTERN = re.compile(r'\s+')


#============================================
def choice_visible_text(choice: str | dict) -> str:
	"""Return the DOCX-visible plain text for a YAML choice.

	Reduces a YAML choice (string or dict with optional text/image keys)
	to the plain text the DOCX builder will ultimately render: HTML
	entities are decoded, supported inline tags are stripped while
	preserving their inner text, and whitespace is normalized.

	Image-only dicts (no text or empty text) return an empty string.
	The returned value is intended for layout measurement, not for
	rendering -- it does not preserve sub/sup/bold/italic state.

	Args:
		choice: A YAML choice -- a plain string or a dict with
			optional 'text' and 'image' keys.

	Returns:
		The DOCX-visible plain-text representation, or '' for an
		image-only choice.
	"""
	# extract the raw text payload from string or dict
	if isinstance(choice, dict):
		# 'text' is optional on image-only choices; '' is intentional
		raw_text = choice.get('text', '')
	else:
		raw_text = choice
	if not raw_text:
		return ''
	# decode HTML entities (&#8226; -> bullet glyph, etc.)
	decoded = html.unescape(raw_text)
	# strip supported inline tags while preserving their inner text
	stripped = _INLINE_TAG_STRIP_PATTERN.sub('', decoded)
	# normalize whitespace runs and trim
	normalized = _WHITESPACE_RUN_PATTERN.sub(' ', stripped).strip()
	return normalized


#============================================
# character width weights for visible-width scoring
# weights are approximate -- they capture wide-vs-narrow ratios well
# enough for column-fit decisions without modeling real font metrics
_WIDTH_VERY_NARROW = set("ilI.,:;|!")
_WIDTH_NARROW = set("fjrt")
_WIDTH_GROUPING = set("+-=<>/\\*()[]{}")
_WIDTH_WIDE = set("MW@#%&")


#============================================
def choice_visible_width(choice: str | dict) -> float:
	"""Return an approximate visible-width score for a YAML choice.

	The score is a weighted sum of the DOCX-visible characters of the
	choice. Narrow glyphs (i, l, .) weigh less than typical letters;
	wide glyphs (M, W) weigh more. The score is explicitly approximate
	and is used to decide column layout in auto_layout_for_choices.

	Image-only choices score 0.0 because they contribute no text width
	to the choice paragraph (image rendering uses a separate column).

	Args:
		choice: A YAML choice -- a plain string or a dict with
			optional 'text' and 'image' keys.

	Returns:
		The weighted visible-width score as a float.
	"""
	text = choice_visible_text(choice)
	width = 0.0
	for ch in text:
		# whitespace and very narrow glyphs share the lowest weight
		if ch.isspace() or ch in _WIDTH_VERY_NARROW:
			width += 0.35
		elif ch in _WIDTH_NARROW:
			width += 0.55
		elif ch in _WIDTH_GROUPING:
			width += 0.65
		elif ch in _WIDTH_WIDE:
			width += 1.25
		elif ord(ch) > 127:
			# decoded entities like bullet, triple-bond, multiplication
			width += 0.9
		else:
			width += 0.8
	return width
