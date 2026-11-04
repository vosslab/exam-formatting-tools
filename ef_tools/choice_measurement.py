"""Measure formatted choice text using the installed DOCX font faces."""

# Standard Library
import functools
import subprocess

# Pip Modules
import PIL.ImageFont

# Local Repo Modules
import ef_tools.text_utils


#============================================
@functools.lru_cache(maxsize=128)
def load_font(family: str, bold: bool, italic: bool) -> object:
	"""Resolve a fontconfig face, including a variable font's named instance."""
	weight = 'bold' if bold else 'regular'
	slant = 'italic' if italic else 'roman'
	# Pass authored names as one argument; never interpolate them into a shell.
	result = subprocess.check_output([
		'fc-match', '-f', '%{file}\n%{index}',
		f'{family}:weight={weight}:slant={slant}'], text=True).splitlines()
	font = PIL.ImageFont.truetype(result[0], size=1000, index=int(result[1]))
	return font


#============================================
def text_width(text: str, family: str, size: float,
		bold: bool = False, italic: bool = False) -> float:
	"""Return width in points, including italic ink extending beyond its advance."""
	font = load_font(family, bold, italic)
	left, _top, right, _bottom = font.getbbox(text)
	width = max(font.getlength(text), right - min(0, left)) * size / 1000
	return width


#============================================
def choice_widths(choices: list, styles: dict, font_family: str = None) -> list:
	"""Measure each bold label plus its rendered rich-text runs, in points."""
	family = font_family or styles['fonts']['primary']
	size = styles['sizes']['choice']
	widths = []
	for index, choice in enumerate(choices):
		width = text_width(f'({chr(ord("A") + index)}) ', family, size, bold=True)
		text = choice.get('text', '') if isinstance(choice, dict) else choice
		decoded = ef_tools.text_utils.decode_html_entities(text)
		for segment, tags in ef_tools.text_utils.parse_rich_text(decoded):
			if segment == '\n':
				continue
			segment = segment.replace('\n', ' ')
			face = styles['fonts']['monospace'] if 'code' in tags else family
			run_size = 8 if 'small' in tags else size
			# Full-size sub/superscripts are a conservative bound on Writer's reduced glyphs.
			width += text_width(segment, face, run_size, 'b' in tags, 'i' in tags)
		widths.append(width)
	return widths
