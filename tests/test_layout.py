"""Choice selection checks measured widths against real tab slots."""

import pytest

import ef_tools.layout
import ef_tools.style_loader


#============================================
@pytest.mark.parametrize('widths,expected', [
	([40] * 5, (5, 5)),
	([110] * 5, (3, 3)),
	([200] * 5, (1, 1)),
	([125] * 4, (2, 2)),
	([300] * 2, (1, 1)),
])
def test_measured_layout_retains_balanced_rows(widths: list, expected: tuple) -> None:
	"""Unsafe dense layouts fall back to balanced rows or a vertical stack."""
	styles = ef_tools.style_loader.for_paper_size(ef_tools.style_loader.load_styles(), 'letter')
	assert ef_tools.layout.auto_layout_for_choices(widths, styles) == expected


#============================================
def test_each_column_and_last_column_are_checked() -> None:
	"""The rightmost slot and each answer's actual position determine fit."""
	styles = ef_tools.style_loader.for_paper_size(ef_tools.style_loader.load_styles(), 'letter')
	styles['layout_tab_stops'][3] = [1.0, 6.0]
	assert ef_tools.layout.auto_layout_for_choices([50, 200, 80], styles) == (3, 3)
	assert ef_tools.layout.auto_layout_for_choices([200, 50, 80], styles) == (1, 1)
	assert ef_tools.layout.auto_layout_for_choices([50, 50, 100], styles) == (1, 1)


#============================================
def test_paper_width_and_gap_change_fit() -> None:
	"""A borderline Letter layout cannot silently overrun narrower A4 slots."""
	styles = ef_tools.style_loader.load_styles()
	letter = ef_tools.style_loader.for_paper_size(styles, 'letter')
	a4 = ef_tools.style_loader.for_paper_size(styles, 'a4')
	assert ef_tools.layout.auto_layout_for_choices([248, 248], letter) == (2, 2)
	assert ef_tools.layout.auto_layout_for_choices([248, 248], a4) == (1, 1)


#============================================
def test_choices_style_name_never_returns_choice() -> None:
	"""Every legal tab_style maps to a concrete Choices N style."""
	for tab_style in range(1, 6):
		assert ef_tools.layout.choices_style_name(tab_style) != 'Choice'
