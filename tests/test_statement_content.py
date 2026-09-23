"""Tests for the ordered statement block contract."""

import pytest

import ef_tools.statement_content


#============================================
@pytest.mark.parametrize('statement', [
	[],
	[{'text': '  '}],
	[{'image': ' '}],
	[{'table': {}}],
	[{'table': {'columns': ['Path'], 'rows': [['too', 'many']]}}],
	[{'text': 'prose', 'image': 'figure.png'}],
])
def test_statement_validation_rejects_unrenderable_blocks(statement: list) -> None:
	"""Malformed or empty blocks fail at the schema boundary."""
	with pytest.raises(ValueError):
		ef_tools.statement_content.validate(statement)


#============================================
def test_statement_validation_accepts_a_complete_data_table() -> None:
	"""Structured tables match the DOCX renderer's columns-and-rows input."""
	ef_tools.statement_content.validate([{
		'table': {'columns': ['Step'], 'rows': [['Product']]}}])
