"""Test text_utils module."""

import ef_tools.text_utils


#============================================
def test_strip_number_prefix_parenthesis():
	"""Test stripping number with parenthesis prefix."""
	result = ef_tools.text_utils.strip_number_prefix("22) Which of the following")
	assert result == "Which of the following"


#============================================
def test_strip_number_prefix_no_prefix():
	"""Test that text without prefix is unchanged."""
	result = ef_tools.text_utils.strip_number_prefix("No prefix here")
	assert result == "No prefix here"


#============================================
def test_parse_rich_text_plain_text():
	"""Test that plain text returns single segment with no tags."""
	result = ef_tools.text_utils.parse_rich_text("hello world")
	assert result == [("hello world", frozenset())]


#============================================
def test_parse_rich_text_subscript():
	"""Test subscript tag parsing."""
	result = ef_tools.text_utils.parse_rich_text("H<sub>2</sub>O")
	assert result == [
		("H", frozenset()),
		("2", frozenset({"sub"})),
		("O", frozenset()),
	]


#============================================
def test_parse_rich_text_bold():
	"""Test bold tag parsing."""
	result = ef_tools.text_utils.parse_rich_text("<b>Note:</b> answer")
	assert result == [
		("Note:", frozenset({"b"})),
		(" answer", frozenset()),
	]


#============================================
def test_parse_rich_text_strong_normalizes_to_b():
	"""Test that strong tag normalizes to b."""
	result = ef_tools.text_utils.parse_rich_text("<strong>x</strong>")
	assert result[0][1] == frozenset({"b"})


#============================================
def test_parse_rich_text_em_normalizes_to_i():
	"""Test that em tag normalizes to i."""
	result = ef_tools.text_utils.parse_rich_text("<em>y</em>")
	assert result[0][1] == frozenset({"i"})


#============================================
def test_parse_rich_text_break_tag():
	"""Test that HTML break tags become line break segments."""
	result = ef_tools.text_utils.parse_rich_text("one<br/>two")
	assert result == [
		("one", frozenset()),
		("\n", frozenset()),
		("two", frozenset()),
	]


#============================================
def test_choice_visible_text_decodes_entities():
	"""HTML entities should be reduced to their visible glyphs."""
	raw = "C &#8801; C"
	result = ef_tools.text_utils.choice_visible_text(raw)
	assert len(result) < len(raw)


#============================================
def test_choice_visible_text_strips_supported_inline_tags():
	"""Inline tags strip to their inner text without the markup."""
	result = ef_tools.text_utils.choice_visible_text("H<sub>2</sub>O")
	assert result == "H2O"


#============================================
def test_choice_visible_text_image_only_dict_returns_empty():
	"""An image-only choice contributes no visible text."""
	result = ef_tools.text_utils.choice_visible_text({"image": "image.png"})
	assert result == ""


#============================================
def test_choice_visible_width_relationships():
	"""Wide glyphs score higher than narrow ones; entities below raw len."""
	wide = ef_tools.text_utils.choice_visible_width("MMMM")
	narrow = ef_tools.text_utils.choice_visible_width("iiii")
	assert wide > narrow
	raw = "C &#8801; C"
	assert ef_tools.text_utils.choice_visible_width(raw) < len(raw)


#============================================
def test_choice_visible_width_image_only_choice_is_zero():
	"""An image-only choice contributes zero width to the layout score."""
	width = ef_tools.text_utils.choice_visible_width({"image": "image.png"})
	assert width == 0.0
