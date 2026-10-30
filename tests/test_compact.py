"""Contracts for compact paper-output prose handling."""

import ef_tools.compact


#============================================
def test_compact_removes_recognized_hints_and_shrinks_supporting_text() -> None:
	"""Known headings drive compaction; ordinary prose remains available."""
	text = (
		'<b>Background Information</b>\nUseful setup.\n'
		'<b>Step-by-Step Instructions</b>\nDo this first.\n'
		'<b>Question</b>\nSolve the problem.'
	)
	compact = ef_tools.compact.compact_text(text)
	assert '<small>Useful setup.</small>' in compact
	assert 'Do this first.' not in compact
	assert '<b>Question: </b>Solve the problem.' in compact


#============================================
def test_compact_keeps_colored_background_at_normal_size() -> None:
	"""Colored runs carry instructional meaning and remain readable."""
	text = '<b>Background</b>\n<span style="color: #112233;">Gene A</span> matters.'
	compact = ef_tools.compact.compact_text(text)
	assert '<small>' not in compact
