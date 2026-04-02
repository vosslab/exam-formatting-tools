"""Tests for odt_exam_builder.py ODT exam generation tool."""

# Standard Library
import os

# Pip Modules
import lxml.etree

# Local Repo Modules
import git_file_utils
import odt_utils
import odt_exam_builder

REPO_ROOT = git_file_utils.get_repo_root()


#============================================
def make_sample_exam_data() -> dict:
	"""Build a minimal exam data dict for testing.

	Returns:
		Dict matching the expected YAML input format.
	"""
	data = {
		'title': 'Test Exam',
		'date': '2025-12-01',
		'student_line': 'Name: ________  Score: ____/50',
		'sections': [
			{
				'chapter': 'Chapter 1 -- Basics',
				'questions': [
					{
						'statement': 'What is DNA?',
						'choices': ['protein', 'lipid', 'nucleic acid', 'carbohydrate'],
						'layout': 4,
					},
					{
						'statement': 'Matching question',
						'table': {
							'columns': ['Term', 'Definition'],
							'rows': [
								['Gene', 'Unit of heredity'],
								['Allele', 'Variant of a gene'],
							],
						},
					},
				],
			},
		],
	}
	return data


#============================================
def test_select_question_style():
	"""Auto-selection should choose correct style based on previous element."""
	# After question or choices: use Question Heading
	assert odt_exam_builder.select_question_style('question') == 'Question Heading'
	assert odt_exam_builder.select_question_style('choices') == 'Question Heading'
	# After chapter, table, or image: use Question Follow
	assert odt_exam_builder.select_question_style('chapter') == 'Question Follow'
	assert odt_exam_builder.select_question_style('table') == 'Question Follow'
	assert odt_exam_builder.select_question_style('image') == 'Question Follow'


#============================================
def test_auto_layout_for_choices():
	"""Auto-layout should select correct style based on count and length."""
	# 2 choices -> Choices4
	assert odt_exam_builder.auto_layout_for_choices(['a', 'b']) == 4
	# 3 choices -> Choices3
	assert odt_exam_builder.auto_layout_for_choices(['a', 'b', 'c']) == 3
	# 4 choices -> Choices4
	assert odt_exam_builder.auto_layout_for_choices(['a', 'b', 'c', 'd']) == 4
	# 5 short choices -> Choices5
	short_5 = ['a', 'b', 'c', 'd', 'e']
	assert odt_exam_builder.auto_layout_for_choices(short_5) == 5
	# 5 medium choices (<=24 chars) -> Choices4
	med_5 = ['abcdefghijklmnopqrstuvwx', 'short', 'tiny', 'ok', 'end']
	assert odt_exam_builder.auto_layout_for_choices(med_5) == 4
	# 5 long choices (>24 chars) -> Choices3
	long_5 = ['abcdefghijklmnopqrstuvwxy', 'short', 'tiny', 'ok', 'end']
	assert odt_exam_builder.auto_layout_for_choices(long_5) == 3


#============================================
def test_create_choices_paragraph():
	"""Choices paragraph should use correct style and tab count per layout."""
	tab_tag = odt_utils.qname('text', 'tab')
	# Choices4: 4 items produce 3 tabs
	para4 = odt_exam_builder.create_choices_paragraph(['a', 'b', 'c', 'd'], 4)
	assert para4.get(odt_utils.qname('text', 'style-name')) == 'Choices4'
	assert len(para4.findall(tab_tag)) == 3
	# verify bold letter prefixes are present
	span_tag = odt_utils.qname('text', 'span')
	spans = para4.findall(span_tag)
	assert len(spans) == 4, f"Expected 4 bold letter spans, got {len(spans)}"
	# check that spans contain bold style name
	for span in spans:
		assert span.get(odt_utils.qname('text', 'style-name')) == 'AutoBold'


#============================================
def test_create_table():
	"""Verify table header row uses Table Heading style."""
	auto_styles = lxml.etree.Element(odt_utils.qname('office', 'automatic-styles'))
	table = odt_exam_builder.create_table(['A', 'B'], [['1', '2']], auto_styles)
	# header row cells should use Table_20_Heading style
	first_row = table.findall(odt_utils.qname('table', 'table-row'))[0]
	first_cell = first_row.find(odt_utils.qname('table', 'table-cell'))
	para = first_cell.find(odt_utils.qname('text', 'p'))
	assert para.get(odt_utils.qname('text', 'style-name')) == 'Table Heading'


#============================================
def test_create_exam_styles():
	"""Verify all expected style names are present."""
	styles = odt_exam_builder.create_exam_styles()
	style_tag = odt_utils.qname('style', 'style')
	name_attr = odt_utils.qname('style', 'name')
	# collect all style names
	style_names = []
	for elem in styles.findall(style_tag):
		style_names.append(elem.get(name_attr))
	expected_names = [
		'Standard', 'Question Heading', 'Question', 'Question Follow',
		'Choices', 'Choices3', 'Choices4', 'Choices5',
		'Warning', 'Preformatted Text', 'Table Contents', 'Table Heading',
		'Heading', 'Heading 1', 'Heading 2', 'Heading 3', 'Heading 4',
		'Chapter Heading',
	]
	for name in expected_names:
		assert name in style_names, f"Missing style: {name}"


#============================================
def test_create_page_layouts():
	"""Verify page layouts include expected names."""
	auto_styles, master_styles = odt_exam_builder.create_page_layouts()
	layout_tag = odt_utils.qname('style', 'page-layout')
	layout_names = [l.get(odt_utils.qname('style', 'name')) for l in auto_styles.findall(layout_tag)]
	assert 'Mpm1' in layout_names
	assert 'Mpm2' in layout_names
	# master pages
	master_tag = odt_utils.qname('style', 'master-page')
	master_names = [m.get(odt_utils.qname('style', 'name')) for m in master_styles.findall(master_tag)]
	assert 'Standard' in master_names
	assert 'First Page' in master_names


#============================================
def test_assemble_minimal_exam(tmp_path):
	"""Build exam from minimal data and verify output is readable."""
	data = make_sample_exam_data()
	output_path = os.path.join(str(tmp_path), "exam_output.odt")
	odt_exam_builder.assemble_odt(data, output_path)
	# verify the file exists
	assert os.path.isfile(output_path)
	# verify it can be read back
	odt_data = odt_utils.read_odt(output_path)
	assert odt_data['styles_xml'] is not None
	assert odt_data['content_xml'] is not None
	# verify named styles are in the output
	named_styles = odt_utils.get_named_styles(odt_data['styles_xml'])
	names = [odt_utils.style_name(s) for s in named_styles]
	assert 'Standard' in names
	assert 'Question Heading' in names
	assert 'Choices4' in names
	# verify body has content
	body_tag = odt_utils.qname('office', 'body')
	text_tag = odt_utils.qname('office', 'text')
	body = odt_data['content_xml'].find(f".//{body_tag}")
	text = body.find(text_tag)
	# should have paragraphs and a table
	assert len(list(text)) > 0


#============================================
def test_question_style_selection_in_document(tmp_path):
	"""Verify auto-selection: first question uses Question Follow after chapter."""
	data = {
		'title': 'Test Auto-Selection',
		'date': '2025-12-01',
		'student_line': 'Name: ________',
		'sections': [
			{
				'chapter': 'Chapter 1 -- Introduction',
				'questions': [
					{
						'statement': 'First question after chapter',
						'choices': ['a', 'b', 'c', 'd'],
						'layout': 4,
					},
					{
						'statement': 'Second question after choices',
						'choices': ['x', 'y', 'z'],
						'layout': 3,
					},
				],
			},
		],
	}
	output_path = os.path.join(str(tmp_path), "test_selection.odt")
	odt_exam_builder.assemble_odt(data, output_path)
	# read back and check question styles
	odt_data = odt_utils.read_odt(output_path)
	body_tag = odt_utils.qname('office', 'body')
	text_tag = odt_utils.qname('office', 'text')
	body = odt_data['content_xml'].find(f".//{body_tag}")
	text = body.find(text_tag)
	# find all paragraphs with style attributes
	paras = text.findall(odt_utils.qname('text', 'p'))
	# collect styles: should have Heading1, Standard, Chapter Heading, then questions
	styles_found = []
	for para in paras:
		style = para.get(odt_utils.qname('text', 'style-name'))
		if style:
			styles_found.append(style)
	# verify first question uses Question Follow (after Chapter Heading)
	assert 'Chapter Heading' in styles_found
	chapter_idx = styles_found.index('Chapter Heading')
	# first question after chapter should be Question Follow
	assert chapter_idx + 1 < len(styles_found)
	assert styles_found[chapter_idx + 1] == 'Question Follow'
	# second question should be Question Heading (after choices)
	choice_style_before_q2 = None
	for i in range(chapter_idx + 1, len(styles_found)):
		if styles_found[i].startswith('Choices'):
			choice_style_before_q2 = i
			break
	if choice_style_before_q2 is not None:
		assert choice_style_before_q2 + 1 < len(styles_found)
		assert styles_found[choice_style_before_q2 + 1] == 'Question Heading'
