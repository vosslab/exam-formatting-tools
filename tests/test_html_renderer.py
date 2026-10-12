"""Protect source-resolution reporting and canvas PNG selection."""

import io
import unittest.mock

import PIL.Image
import pytest

import ef_tools.html_renderer


@pytest.mark.parametrize('pixels,expected_issue', [(256, True), (1200, False)])
def test_source_resolution_uses_printed_size(pixels: int, expected_issue: bool) -> None:
	"""Raster content is acceptable when its actual pixels meet placement DPI."""
	page = unittest.mock.Mock()
	page.locator.return_value.count.return_value = 1
	page.locator.return_value.nth.return_value.evaluate.return_value = {
		'kind': 'canvas', 'cssWidth': 256, 'cssHeight': 256,
		'backingWidth': pixels, 'backingHeight': pixels,
	}
	renderer = ef_tools.html_renderer.HtmlRenderer()
	issues = renderer._source_resolution_issues(page, {'#drawing': 2},
		{'#drawing': {'width': 256, 'height': 256}})
	assert ('#drawing' in issues) == expected_issue


@pytest.mark.parametrize('source_recovers', [True, False])
def test_canvas_uses_png_without_replacing_mixed_svg(source_recovers: bool) -> None:
	"""Fallback is per target and reports source detail still missing after recapture."""
	renderer = ef_tools.html_renderer.HtmlRenderer()
	page = unittest.mock.Mock()
	png = io.BytesIO()
	PIL.Image.new('RGB', (1408, 1408), 'white').save(png, format='PNG')
	page.locator.return_value.screenshot.return_value = png.getvalue()
	page.locator.return_value.evaluate.return_value = False
	measurements = {key: {'width': 256, 'height': 256} for key in ('#table', '#drawing')}
	issues = {key: 'canvas source dimensions below print requirement'
		for key in ('#table', '#drawing')}
	svg = b'<svg xmlns="http://www.w3.org/2000/svg"/>'
	with unittest.mock.patch.object(renderer, '_load_page', return_value=(unittest.mock.Mock(), page)), \
		unittest.mock.patch.object(renderer, '_wait_for_canvases'), \
		unittest.mock.patch.object(renderer, '_target_measurements', return_value=measurements), \
		unittest.mock.patch.object(renderer, '_source_resolution_issues',
			side_effect=[issues, {} if source_recovers else {'#drawing': issues['#drawing']}]), \
		unittest.mock.patch.object(renderer, '_canvas_only', side_effect=[False, True]), \
		unittest.mock.patch.object(renderer, '_capture_svg', return_value=svg), \
		pytest.warns(UserWarning) as messages:
		result = renderer.render('<html/>', {'#table': 2, '#drawing': 2})
	assert result['#table'] == svg
	with PIL.Image.open(io.BytesIO(result['#drawing'])) as image:
		assert image.format == 'PNG'
		assert image.width / 2 >= ef_tools.html_renderer.PRINT_DPI
	assert any('SVG retains limited source detail' in str(item.message) for item in messages)
	assert any('PNG source remains below print quality' in str(item.message)
		for item in messages) == (not source_recovers)
