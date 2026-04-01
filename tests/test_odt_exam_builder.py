"""Tests for odt_exam_builder.py ODT exam generation tool."""

# Standard Library
import os

# Pip Modules
import pytest
import yaml
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
				'heading': 'Chapter 1 -- Basics',
				'questions': [
					{
						'number': 1,
						'heading': '1. What is DNA?',
						'text': 'Select the best answer.',
						'choices': {
							'layout': 4,
							'items': ['protein', 'lipid', 'nucleic acid', 'carbohydrate'],
						},
					},
					{
						'number': 2,
						'heading': '2. Matching',
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
def test_create_choices_paragraph():
	"""Choices paragraph should use correct style and tab count per layout."""
	tab_tag = odt_utils.qname('text', 'tab')
	# Choices4: 4 items produce 3 tabs
	para4 = odt_exam_builder.create_choices_paragraph(['a', 'b', 'c', 'd'], 4)
	assert para4.get(odt_utils.qname('text', 'style-name')) == 'Choices4'
	assert len(para4.findall(tab_tag)) == 3


#============================================
def test_create_table():
	"""Verify table header row uses Table Heading style."""
	auto_styles = lxml.etree.Element(odt_utils.qname('office', 'automatic-styles'))
	table = odt_exam_builder.create_table(['A', 'B'], [['1', '2']], auto_styles)
	# header row cells should use Table_20_Heading style
	first_row = table.findall(odt_utils.qname('table', 'table-row'))[0]
	first_cell = first_row.find(odt_utils.qname('table', 'table-cell'))
	para = first_cell.find(odt_utils.qname('text', 'p'))
	assert para.get(odt_utils.qname('text', 'style-name')) == 'Table_20_Heading'


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
		'Standard', 'Question_20_Heading', 'Question', 'Question_20_Follow',
		'Choices', 'Choices3', 'Choices4', 'Choices5',
		'Warning', 'Preformatted_20_Text', 'Table_20_Contents', 'Table_20_Heading',
		'Heading', 'Heading_20_1', 'Heading_20_2', 'Heading_20_3', 'Heading_20_4',
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
	assert 'First_20_Page' in master_names


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
	assert 'Question_20_Heading' in names
	assert 'Choices4' in names
	# verify body has content
	body_tag = odt_utils.qname('office', 'body')
	text_tag = odt_utils.qname('office', 'text')
	body = odt_data['content_xml'].find(f".//{body_tag}")
	text = body.find(text_tag)
	# should have paragraphs and a table
	assert len(list(text)) > 0
