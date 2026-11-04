"""Auto-layout algorithm and constants for multiple choice formatting.

Selects a tab layout using complete formatted answer widths and the actual
page geometry, while retaining the established balanced row arrangements.
"""

# Caption-only heuristic; text-choice layout uses measured widths.
DEFAULT_MAX_CHARS_5 = 17

# default tab stop positions for each choices layout (in inches)
CHOICES_TAB_STOPS = {
	1: [],
	2: [3.75],
	3: [2.43, 4.77],
	4: [1.85, 3.60, 5.35],
	5: [1.50, 2.90, 4.30, 5.70],
}

# style name for each tab layout
# 'Choice' is the abstract base style and must never appear here as
# a value; tab_style=1 (vertical stack) intentionally maps to the
# concrete 'Choices 2' style so no rendered paragraph carries the
# bare base style.
CHOICES_STYLE_NAME = {
	1: 'Choices 2',
	2: 'Choices 2',
	3: 'Choices 3',
	4: 'Choices 4',
	5: 'Choices 5',
}


#============================================
def choices_style_name(tab_style: int) -> str:
	"""Return the paragraph style name for a tab_style value.

	Centralizes style-name resolution for the choice paragraph
	emitters. Always returns one of 'Choices 2', 'Choices 3',
	'Choices 4', or 'Choices 5'; never returns the abstract base
	style name 'Choice'.

	Args:
		tab_style: An integer in 1..5 returned by
			auto_layout_for_choices.

	Returns:
		The paragraph style name to apply.
	"""
	if tab_style not in CHOICES_STYLE_NAME:
		raise ValueError(f"invalid tab_style {tab_style}; expected 1..5")
	return CHOICES_STYLE_NAME[tab_style]


#============================================
def choice_text(choice: object) -> str:
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
def choice_image(choice: object) -> str:
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
def auto_layout_for_choices(widths: list, styles: dict) -> tuple:
	"""Choose the densest established row arrangement whose complete answers fit.

	Widths include labels and all formatted text, in points. Every answer is
	checked against its own next tab or the right margin. A half-em gap keeps
	neighboring answers visibly separate and avoids landing on a tab boundary.
	"""
	count = len(widths)
	if count < 1:
		return (5, 5)
	candidates = {1: [], 2: [2], 3: [3], 4: [4, 2]}.get(count, [5, 3])
	page = styles['page']
	right = (page['width'] - 2 * page['margin']) * 72
	spacing = styles['spacing']
	origin = (spacing['choice_indent'] + spacing['choice_first_line_indent']) * 72
	gap = styles['sizes']['choice'] / 2
	for columns in candidates:
		stops = styles['layout_tab_stops'][columns]
		starts = [origin] + [stop * 72 for stop in stops]
		ends = starts[1:] + [right]
		if all(width + gap <= ends[index % columns] - starts[index % columns]
				for index, width in enumerate(widths)):
			return (columns, columns)
	return (1, 1)
