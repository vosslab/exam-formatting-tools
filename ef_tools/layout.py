"""Auto-layout algorithm and constants for multiple choice formatting.

Determines optimal column layout for exam choices based on count
and text length, avoiding orphan rows.
"""


# default character limits for auto-layout, empirically measured at 10pt
# Liberation Sans with bold "(A) " prefix, minus 1 safety margin
DEFAULT_MAX_CHARS_5 = 17
DEFAULT_MAX_CHARS_4 = 23
DEFAULT_MAX_CHARS_3 = 30
DEFAULT_MAX_CHARS_2 = 49

# default tab stop positions for each choices layout (in inches)
CHOICES_TAB_STOPS = {
	1: [],
	2: [3.65],
	3: [2.33, 4.67],
	4: [1.75, 3.50, 5.25],
	5: [1.40, 2.80, 4.20, 5.60],
}

# style name for each tab layout
CHOICES_STYLE_NAME = {
	1: 'Choice',
	2: 'Choices 2',
	3: 'Choices 3',
	4: 'Choices 4',
	5: 'Choices 5',
}


#============================================
def choice_text(choice) -> str:
	"""Return display text for a string or structured choice.

	Choice may be a plain string or a dict with optional ``text`` and
	``image`` keys; both keys are intentionally optional, so missing
	``text`` returns an empty string.
	"""
	if isinstance(choice, dict):
		# 'text' is optional on image-only choices; empty default is intentional
		text = choice.get('text', '')
	else:
		text = choice
	return text


#============================================
def choice_image(choice) -> str:
	"""Return image path for a structured choice, or None if absent.

	Plain string choices have no image; dict choices may omit the
	``image`` key for text-only entries.
	"""
	if isinstance(choice, dict):
		# 'image' is optional on text-only choices; None default is intentional
		image_path = choice.get('image', None)
	else:
		image_path = None
	return image_path


#============================================
def auto_layout_for_choices(choices: list, layout_limits: dict = None) -> tuple:
	"""Determine the best layout for choices based on count and text length.

	Returns a (tab_style, items_per_row) tuple. The tab_style selects which
	set of tab stops to use (3, 4, or 5). The items_per_row controls how many
	choices go on each line. These can differ: e.g., tab_style=4 with
	items_per_row=2 gives a "Choices 2" layout using Choices 4 tab stops.

	Layout rules to avoid orphan rows (1 item on last row):
	- 2 items: Choices 2 tabs, 2 per row (even spacing)
	- 3 items: Choices 3 (all on one row) if they fit; else vertical
	- 4 items: Choices 4 if they fit; else 2+2 (Choices 2 tabs, 2 per row);
	  never Choices 3 which gives 3+1 orphan
	- 5 items: Choices 5 if they fit; Choices 3 gives 3+2 (no orphan);
	  skip Choices 4 (4+1 orphan) and Choices 2 (2+2+1 orphan)

	Args:
		choices: List of choice text strings.
		layout_limits: Optional dict with max_chars_5/4/3/2 keys from YAML.
			Falls back to built-in defaults if None.

	Returns:
		Tuple of (tab_style, items_per_row).
	"""
	# load character limits from YAML dict or use defaults
	if layout_limits is not None:
		max_chars_5 = layout_limits['max_chars_5']
		max_chars_4 = layout_limits['max_chars_4']
		max_chars_3 = layout_limits['max_chars_3']
		max_chars_2 = layout_limits['max_chars_2']
	else:
		max_chars_5 = DEFAULT_MAX_CHARS_5
		max_chars_4 = DEFAULT_MAX_CHARS_4
		max_chars_3 = DEFAULT_MAX_CHARS_3
		max_chars_2 = DEFAULT_MAX_CHARS_2

	count = len(choices)
	if count < 1:
		return (5, 5)
	max_len = max(len(choice_text(c)) for c in choices)

	if count == 2:
		# 2 items: dedicated Choices 2 layout
		if max_len <= max_chars_2:
			return (2, 2)
		# very long: vertical stack
		return (1, 1)

	if count == 3:
		# prefer all 3 on one row
		if max_len <= max_chars_3:
			return (3, 3)
		# too long: vertical stack
		return (1, 1)

	if count == 4:
		# prefer 4 on one row
		if max_len <= max_chars_4:
			return (4, 4)
		# doesn't fit 4/row: use 2+2 layout (NOT Choices 3 which gives 3+1 orphan)
		if max_len <= max_chars_2:
			return (2, 2)
		# very long: vertical stack
		return (1, 1)

	# 5+ choices
	if max_len <= max_chars_5:
		# all 5 on one row
		return (5, 5)
	if max_len <= max_chars_3:
		# Choices 3 gives 3+2 (no orphan) -- skip Choices 4 which gives 4+1 orphan
		return (3, 3)
	if max_len <= max_chars_2:
		# long text: still use 3+2 with Choices 3 columns
		return (3, 3)
	# very long: vertical stack
	return (1, 1)

# test: short choices get 5-column layout
assert auto_layout_for_choices(["a", "b", "c", "d", "e"]) == (5, 5)
# test: 2 items get Choices 2 layout
assert auto_layout_for_choices(["yes", "no"]) == (2, 2)
# test: 4 medium choices get 2+2 layout to avoid orphan
assert auto_layout_for_choices(["a" * 25, "b" * 25, "c" * 25, "d" * 25]) == (2, 2)
# test: very long choices get vertical stack
assert auto_layout_for_choices(["a" * 55, "b" * 55]) == (1, 1)
