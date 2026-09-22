"""Test text_utils module."""

import ef_tools.text_utils


#============================================
def test_strip_number_prefix_parenthesis() -> None:
	"""Test stripping number with parenthesis prefix."""
	result = ef_tools.text_utils.strip_number_prefix("22) Which of the following")
	assert result == "Which of the following"


#============================================
def test_strip_number_prefix_no_prefix() -> None:
	"""Test that text without prefix is unchanged."""
	result = ef_tools.text_utils.strip_number_prefix("No prefix here")
	assert result == "No prefix here"


#============================================
def test_parse_rich_text_plain_text() -> None:
	"""Test that plain text returns single segment with no tags."""
	result = ef_tools.text_utils.parse_rich_text("hello world")
	assert result == [("hello world", frozenset())]


#============================================
def test_parse_rich_text_subscript() -> None:
	"""Test subscript tag parsing."""
	result = ef_tools.text_utils.parse_rich_text("H<sub>2</sub>O")
	assert result == [
		("H", frozenset()),
		("2", frozenset({"sub"})),
		("O", frozenset()),
	]


#============================================
def test_parse_rich_text_bold() -> None:
	"""Test bold tag parsing."""
	result = ef_tools.text_utils.parse_rich_text("<b>Note:</b> answer")
	assert result == [
		("Note:", frozenset({"b"})),
		(" answer", frozenset()),
	]


#============================================
def test_parse_rich_text_strong_normalizes_to_b() -> None:
	"""Test that strong tag normalizes to b."""
	result = ef_tools.text_utils.parse_rich_text("<strong>x</strong>")
	assert result[0][1] == frozenset({"b"})


#============================================
def test_parse_rich_text_em_normalizes_to_i() -> None:
	"""Test that em tag normalizes to i."""
	result = ef_tools.text_utils.parse_rich_text("<em>y</em>")
	assert result[0][1] == frozenset({"i"})


#============================================
def test_parse_rich_text_code_and_tt_use_monospace_tag() -> None:
	"""Code and legacy teletype markup share the monospace tag."""
	result = ef_tools.text_utils.parse_rich_text(
		"<code>ATGC</code> <tt>GCTA</tt>")
	assert result == [
		("ATGC", frozenset({"code"})),
		(" ", frozenset()),
		("GCTA", frozenset({"code"})),
	]


#============================================
def test_parse_rich_text_color_span() -> None:
	"""A bptools hex color becomes a run-level color tag."""
	result = ef_tools.text_utils.parse_rich_text(
		'<strong><span style="color: #9f342d;">A7</span></strong>')
	assert result == [('A7', frozenset({'b', 'color:#9f342d'}))]


#============================================
def test_parse_rich_text_break_tag() -> None:
	"""Test that HTML break tags become line break segments."""
	result = ef_tools.text_utils.parse_rich_text("one<br/>two")
	assert result == [
		("one", frozenset()),
		("\n", frozenset()),
		("two", frozenset()),
	]


#============================================
def test_choice_visible_text_decodes_entities() -> None:
	"""HTML entities should be reduced to their visible glyphs."""
	raw = "C &#8801; C"
	result = ef_tools.text_utils.choice_visible_text(raw)
	assert len(result) < len(raw)


#============================================
def test_choice_visible_text_strips_supported_inline_tags() -> None:
	"""Inline tags strip to their inner text without the markup."""
	result = ef_tools.text_utils.choice_visible_text("H<sub>2</sub>O")
	assert result == "H2O"


#============================================
def test_choice_visible_text_strips_code_markup() -> None:
	"""Code formatting does not alter the text used for choice layout."""
	result = ef_tools.text_utils.choice_visible_text("<code>ATGC</code>")
	assert result == "ATGC"


#============================================
def test_choice_visible_text_image_only_dict_returns_empty() -> None:
	"""An image-only choice contributes no visible text."""
	result = ef_tools.text_utils.choice_visible_text({"image": "image.png"})
	assert result == ""


#============================================
def test_choice_visible_width_relationships() -> None:
	"""Wide glyphs score higher than narrow ones; entities below raw len."""
	wide = ef_tools.text_utils.choice_visible_width("MMMM")
	narrow = ef_tools.text_utils.choice_visible_width("iiii")
	assert wide > narrow
	raw = "C &#8801; C"
	assert ef_tools.text_utils.choice_visible_width(raw) < len(raw)


#============================================
def test_choice_visible_width_image_only_choice_is_zero() -> None:
	"""An image-only choice contributes zero width to the layout score."""
	width = ef_tools.text_utils.choice_visible_width({"image": "image.png"})
	assert width == 0.0
