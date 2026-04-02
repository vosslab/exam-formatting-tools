"""Test ef_tools.style_loader module."""

import ef_tools.style_loader


#============================================
def test_load_styles_returns_dict():
	"""Test that load_styles successfully loads and returns a dict."""
	styles = ef_tools.style_loader.load_styles()
	assert isinstance(styles, dict)
