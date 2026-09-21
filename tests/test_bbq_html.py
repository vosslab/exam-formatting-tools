"""Tests for ef_tools.bbq_html: bptools HTML -> exam YAML text and PNG tables."""

# Standard Library
import os

# PIP3 modules
import pytest

# local repo modules
import ef_tools.bbq_html


# real bptools chargaff statement (trimmed) with CRC paragraph and color spans
CHARGAFF_HTML = (
	"<p>c555_9c1d</p> <p>According to Chargaff's rules, consider a sample where "
	"<strong><span style='color: #004d00;'>46% is adenine</span></strong>.</p>"
	"<p>What are the percentages of the other three bases?</p>"
)

DRAWING_TABLE = (
	"<table><tr><td style='border: 1px solid gray;' bgcolor='#E0E0E0'>Mother</td></tr>"
	"<tr><td bgcolor='#6495ED'></td></tr></table>"
)
PLAIN_TABLE = "<table><tr><td>Mother</td></tr><tr><td>Child</td></tr></table>"


class FakeRenderer:
	"""Stand-in for TableRenderer that returns fixed PNG bytes."""

	def render_table_png(self, table_html: str) -> bytes:
		return b'PNG' + table_html.encode('ascii')[:4]


#============================================
def test_split_question_code_removes_leading_code_paragraph():
	code, rest = ef_tools.bbq_html.split_question_code(CHARGAFF_HTML)
	assert code == 'c555_9c1d'
	assert 'c555_9c1d' not in rest and 'adenine' in rest


#============================================
def test_split_question_code_without_code_returns_html_unchanged():
	code, rest = ef_tools.bbq_html.split_question_code('<p>Plain question</p>')
	assert code == ''
	assert rest == '<p>Plain question</p>'


#============================================
def test_clean_inline_html_drops_spans_keeps_bold_and_splits_paragraphs():
	_, rest = ef_tools.bbq_html.split_question_code(CHARGAFF_HTML)
	cleaned = ef_tools.bbq_html.clean_inline_html(rest)
	lines = cleaned.split('\n')
	assert len(lines) == 2
	assert '<strong>46% is adenine</strong>' in lines[0]
	assert 'span' not in cleaned


#============================================
def test_clean_inline_html_h6_becomes_bold_line_and_entities_stay_escaped():
	cleaned = ef_tools.bbq_html.clean_inline_html(
		'<h6>Background</h6><p>A &mdash; B</p>')
	assert cleaned.split('\n')[0] == '<b>Background</b>'
	assert '&#8212;' in cleaned


#============================================
def test_clean_inline_html_drops_html_comments():
	cleaned = ef_tools.bbq_html.clean_inline_html("<p>5'-ACGT-3'<!-- helper --> end</p>")
	assert cleaned == "5'-ACGT-3' end"


#============================================
def test_clean_inline_html_rejects_unknown_tag():
	with pytest.raises(ValueError, match='blink'):
		ef_tools.bbq_html.clean_inline_html('<p>x <blink>y</blink></p>')


#============================================
def test_pull_tables_extracts_drawing_tables_in_order():
	html = f"<p>Who?</p>{DRAWING_TABLE}<p>Gel B</p>{DRAWING_TABLE.replace('Mother', 'Child')}"
	remaining, tables = ef_tools.bbq_html.pull_tables(html)
	assert len(tables) == 2
	assert 'Mother' in tables[0] and 'Child' in tables[1]
	assert '<table' not in remaining
	assert ef_tools.bbq_html.clean_inline_html(remaining) == 'Who?\nGel B'


#============================================
def test_pull_tables_takes_tables_without_cell_styles_too():
	remaining, tables = ef_tools.bbq_html.pull_tables(f"<p>x</p>{PLAIN_TABLE}")
	assert len(tables) == 1 and 'Mother' in tables[0]
	assert '<table' not in remaining


#============================================
def test_pull_tables_keeps_nested_tables_inside_their_parent():
	nested = f"<table><tr><td>{PLAIN_TABLE}</td><td>{PLAIN_TABLE}</td></tr></table>"
	_, tables = ef_tools.bbq_html.pull_tables(f"<p>{nested}</p>")
	assert len(tables) == 1
	assert tables[0].count('<table') == 3


#============================================
def test_pull_tables_flattens_single_row_sequence_strip_to_text():
	cell = "<td style='font-family: monospace;'>"
	strip = (f"<table><tr>{cell}5&prime;&ndash;</td>{cell}&nbsp;<span style='color: #004d00;'>A</span>&nbsp;</td>"
		f"{cell}&nbsp;N&nbsp;</td>{cell}&ndash;3&prime;</td></tr></table>")
	remaining, tables = ef_tools.bbq_html.pull_tables(f"Site: {strip} end")
	assert tables == []
	assert ef_tools.bbq_html.clean_inline_html(remaining) == 'Site: 5&#8242;&#8211;AN&#8211;3&#8242; end'


#============================================
def test_clean_inline_html_headings_and_hr():
	cleaned = ef_tools.bbq_html.clean_inline_html('<h4>Hint</h4><p>a</p><hr/><p>b</p>')
	assert cleaned == '<b>Hint</b>\na\nb'


#============================================
def test_write_table_pngs_writes_files_and_returns_yaml_relative_paths(tmp_path):
	media_dir = tmp_path / 'quiz_files'
	paths = ef_tools.bbq_html.write_table_pngs(
		[DRAWING_TABLE, DRAWING_TABLE], FakeRenderer(), str(media_dir), 'ab12_cd34')
	assert paths == [
		os.path.join('quiz_files', 'ab12_cd34_table_1.png'),
		os.path.join('quiz_files', 'ab12_cd34_table_2.png'),
	]
	for path in paths:
		assert (tmp_path / path).stat().st_size > 0
