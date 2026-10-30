"""Paper-output compaction that preserves the authored YAML."""

# Standard Library
import re


HINT_HEADINGS = {
	'hints', 'step-by-step instructions', 'important answer guidelines',
}
SMALL_HEADINGS = {
	'background', 'background information', 'characteristics of recessive phenotypes',
}
_HEADING_RE = re.compile(r'^<b>(.*?)</b>$', re.IGNORECASE)


#============================================
def _heading_text(line: str) -> str:
	"""Return a normalized bold-line heading, or an empty string."""
	match = _HEADING_RE.fullmatch(line.strip())
	if match is None:
		return ''
	text = re.sub(r'<[^>]+>', '', match.group(1)).strip().rstrip(':').lower()
	return text


#============================================
def compact_text(text: str) -> str:
	"""Remove recognized hints and mark recognized supporting text small."""
	lines = [line for line in text.split('\n') if line.strip()]
	result = []
	mode = ''
	for line in lines:
		heading = _heading_text(line)
		if heading:
			if heading in HINT_HEADINGS:
				mode = 'drop'
				continue
			mode = 'small' if heading in SMALL_HEADINGS else ''
			result.append(line)
			continue
		if 'in this problem, you will use unordered tetrads' in line.lower():
			result.append(f'<small>{line}</small>')
			continue
		if mode == 'drop':
			continue
		if mode == 'small' and '<span style=' not in line.lower():
			result.append(f'<small>{line}</small>')
		else:
			result.append(line)
	joined = []
	for line in result:
		if joined and _heading_text(joined[-1]) and not _heading_text(line):
			joined[-1] = joined[-1].rstrip()[:-4] + ': </b>' + line
		else:
			joined.append(line)
	return '\n'.join(joined)


#============================================
def statement(statement: list, compact: bool) -> list:
	"""Return render-time text compaction without changing source YAML."""
	if not compact or not isinstance(statement, list):
		return statement
	blocks = []
	for block in statement:
		if 'text' in block:
			blocks.append({'text': compact_text(block['text'])})
		else:
			blocks.append(block)
	return blocks
