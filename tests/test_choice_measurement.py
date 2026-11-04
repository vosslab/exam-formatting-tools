"""Measure the same text and formatting that the DOCX choice emitter uses."""

import ef_tools.choice_measurement
import ef_tools.style_loader
import yaml_to_exam_docx


#============================================
def test_complete_formatted_answer_measurement(monkeypatch: object) -> None:
	"""Labels, decoded entities, bold, italic, code, and small text reach measurement."""
	calls = []

	def measure(text: str, family: str, size: float,
			bold: bool = False, italic: bool = False) -> float:
		calls.append((text, family, size, bold, italic))
		return len(text) * size

	monkeypatch.setattr(ef_tools.choice_measurement, 'text_width', measure)
	styles = ef_tools.style_loader.load_styles()
	widths = ef_tools.choice_measurement.choice_widths([
		'<b>W&amp;</b><i>x</i><code>AT</code><small>tiny</small>'], styles, 'Condensed')
	assert widths == [122]
	assert calls[0] == ('(A) ', 'Condensed', 10, True, False)
	assert ('W&', 'Condensed', 10, True, False) in calls
	assert ('x', 'Condensed', 10, False, True) in calls
	assert ('AT', styles['fonts']['monospace'], 10, False, False) in calls
	assert ('tiny', 'Condensed', 8, False, False) in calls
	assert ef_tools.choice_measurement.choice_widths([
		'<span style="color: #ff0000;">abc</span>'], styles) == [70]


#============================================
def test_explicit_layout_bypasses_measurement() -> None:
	"""Instructor layout choices remain authoritative, including a vertical stack."""
	assert yaml_to_exam_docx.resolve_choice_layout({'layout': 1}, ['long answer'], {}) == (1, 1)


#============================================
def test_font_resolution_preserves_variable_instance(monkeypatch: object) -> None:
	"""Measuring the default variable face instead of its bold instance undercounts width."""
	calls = []

	def resolve(command: list, text: bool) -> str:
		calls.append(command)
		return '/installed/font.ttf\n393216'

	def open_font(path: str, size: int, index: int) -> tuple:
		return path, size, index

	monkeypatch.setattr(ef_tools.choice_measurement.subprocess, 'check_output', resolve)
	monkeypatch.setattr(ef_tools.choice_measurement.PIL.ImageFont, 'truetype', open_font)
	ef_tools.choice_measurement.load_font.cache_clear()
	font = ef_tools.choice_measurement.load_font('Example Face', True, False)
	assert font == ('/installed/font.ttf', 1000, 393216)
	assert calls[0][-1] == 'Example Face:weight=bold:slant=roman'
	ef_tools.choice_measurement.load_font.cache_clear()
