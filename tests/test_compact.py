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


#============================================
def test_compact_flows_recognized_phenotype_bullets_without_losing_markup() -> None:
	"""Phenotype support is one paragraph while gene labels retain their markup."""
	text = (
		'<b>Characteristics of Recessive Phenotypes</b>\n'
		'- <strong><span style="color: #112233;">Gene A</span></strong> is pale.\n'
		'- <strong><span style="color: #445566;">Gene B</span></strong> is round.\n'
		'<b>Question</b>\n- Keep this instruction as a list item.'
	)
	compact = ef_tools.compact.compact_text(text)
	phenotypes, question = compact.split('\n<b>Question: </b>')
	assert '<b>Characteristics of Recessive Phenotypes: </b>' in compact
	assert '\n' not in phenotypes
	assert '- <strong>' not in compact
	assert '<strong><span style="color: #112233;">Gene A</span></strong>' in compact
	assert '<strong><span style="color: #445566;">Gene B</span></strong>' in compact
	assert question == '- Keep this instruction as a list item.'


#============================================
def test_compact_does_not_flow_supporting_text_across_media_blocks() -> None:
	"""Each statement text block remains an independent render boundary."""
	statement = [
		{'text': '<b>Background</b>\n- First fact.'},
		{'image': 'table.png'},
		{'text': '<b>Background</b>\n- Second fact.'},
	]
	compact = ef_tools.compact.statement(statement, compact=True)
	assert compact[0]['text'].endswith('<small>First fact.</small>')
	assert compact[1] == {'image': 'table.png'}
	assert compact[2]['text'].endswith('<small>Second fact.</small>')


#============================================
def test_compact_keeps_bold_prompt_with_inline_answer_after_hints() -> None:
	"""A handout blank after a bold prompt ends, rather than joins, a hint section."""
	text = (
		'<b>Important Answer Guidelines</b>\nDo not print this.\n'
		'<b>Determine the distance</b> Answer: ____________________'
	)
	compact = ef_tools.compact.compact_text(text)
	assert 'Do not print this.' not in compact
	assert compact == '<b>Determine the distance</b> Answer: ____________________'
