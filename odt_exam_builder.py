#!/usr/bin/env python3
"""Generate a fully styled ODT exam document from structured YAML input.

Creates an ODT file with all named styles from docs/ODT_EXAM_STYLES.md
embedded, including page layouts, master pages, question formatting,
multiple choice layouts, tables, and embedded images.
"""

# Standard Library
import os
import copy
import zipfile
import argparse

# Pip Modules
import yaml
import lxml.etree

# Local Repo Modules
import odt_utils


# counter for automatic styles (tables, cells)
AUTO_STYLE_COUNTER = 0


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Generate a styled ODT exam document from YAML input"
	)
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help="Input YAML file with exam data"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', required=True,
		help="Output ODT file path"
	)
	args = parser.parse_args()
	return args


#============================================
def load_exam_data(yaml_path: str) -> dict:
	"""Load exam data from a YAML file.

	Args:
		yaml_path: Path to the YAML input file.

	Returns:
		Dict with exam structure data.
	"""
	with open(yaml_path, 'r') as f:
		data = yaml.safe_load(f)
	return data


#============================================
def next_auto_style_name() -> str:
	"""Generate a unique automatic style name.

	Returns:
		A unique name string like 'Auto1', 'Auto2', etc.
	"""
	global AUTO_STYLE_COUNTER
	AUTO_STYLE_COUNTER += 1
	name = f"Auto{AUTO_STYLE_COUNTER}"
	return name


#============================================
def create_exam_styles() -> lxml.etree._Element:
	"""Build the complete office:styles element with all exam styles.

	All style property values are from docs/ODT_EXAM_STYLES.md.

	Returns:
		An lxml Element for office:styles containing all named styles.
	"""
	office_styles = lxml.etree.Element(odt_utils.qname('office', 'styles'))
	# helper to create a style element
	def add_style(name: str, family: str, parent: str = None) -> lxml.etree._Element:
		"""Create and append a style:style element."""
		style = lxml.etree.SubElement(office_styles, odt_utils.qname('style', 'style'))
		style.set(odt_utils.qname('style', 'name'), name)
		style.set(odt_utils.qname('style', 'family'), family)
		if parent is not None:
			style.set(odt_utils.qname('style', 'parent-style-name'), parent)
		return style
	# Standard (base text style)
	std = add_style('Standard', 'paragraph')
	std_text = lxml.etree.SubElement(std, odt_utils.qname('style', 'text-properties'))
	std_text.set(odt_utils.qname('fo', 'font-family'), 'Liberation Sans')
	std_text.set(odt_utils.qname('fo', 'font-size'), '11pt')
	std_text.set(odt_utils.qname('style', 'font-pitch'), 'variable')
	std_para = lxml.etree.SubElement(std, odt_utils.qname('style', 'paragraph-properties'))
	std_para.set(odt_utils.qname('fo', 'line-height'), '110%')
	std_para.set(odt_utils.qname('fo', 'margin-bottom'), '0.05in')
	std_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	# Question Heading (encoded: spaces become _20_ in ODF style names)
	qh = add_style('Question_20_Heading', 'paragraph', 'Standard')
	qh_text = lxml.etree.SubElement(qh, odt_utils.qname('style', 'text-properties'))
	qh_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	qh_text.set(odt_utils.qname('fo', 'font-style'), 'italic')
	qh_text.set(odt_utils.qname('fo', 'font-size'), '11pt')
	qh_para = lxml.etree.SubElement(qh, odt_utils.qname('style', 'paragraph-properties'))
	qh_para.set(odt_utils.qname('fo', 'margin-left'), '0.2in')
	qh_para.set(odt_utils.qname('fo', 'text-indent'), '-0.2in')
	qh_para.set(odt_utils.qname('fo', 'margin-top'), '0.15in')
	qh_para.set(odt_utils.qname('fo', 'margin-bottom'), '0.02in')
	qh_para.set(odt_utils.qname('fo', 'keep-with-next'), 'always')
	# Question
	q = add_style('Question', 'paragraph', 'Question_20_Heading')
	q_text = lxml.etree.SubElement(q, odt_utils.qname('style', 'text-properties'))
	q_text.set(odt_utils.qname('fo', 'font-weight'), 'normal')
	q_text.set(odt_utils.qname('fo', 'font-style'), 'normal')
	q_para = lxml.etree.SubElement(q, odt_utils.qname('style', 'paragraph-properties'))
	q_para.set(odt_utils.qname('fo', 'line-height'), '125%')
	q_para.set(odt_utils.qname('fo', 'margin-left'), '0.2in')
	q_para.set(odt_utils.qname('fo', 'text-indent'), '-0.2in')
	q_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	q_para.set(odt_utils.qname('fo', 'margin-bottom'), '0.07in')
	q_para.set(odt_utils.qname('fo', 'orphans'), '2')
	q_para.set(odt_utils.qname('fo', 'widows'), '2')
	# add tab stops to Question style
	tab_stops = lxml.etree.SubElement(q_para, odt_utils.qname('style', 'tab-stops'))
	tab1 = lxml.etree.SubElement(tab_stops, odt_utils.qname('style', 'tab-stop'))
	tab1.set(odt_utils.qname('style', 'position'), '0.5in')
	tab2 = lxml.etree.SubElement(tab_stops, odt_utils.qname('style', 'tab-stop'))
	tab2.set(odt_utils.qname('style', 'position'), '3.5in')
	# Question Follow
	add_style('Question_20_Follow', 'paragraph', 'Standard')
	# Choices (base)
	ch = add_style('Choices', 'paragraph', 'Standard')
	ch_text = lxml.etree.SubElement(ch, odt_utils.qname('style', 'text-properties'))
	ch_text.set(odt_utils.qname('fo', 'font-size'), '10pt')
	ch_para = lxml.etree.SubElement(ch, odt_utils.qname('style', 'paragraph-properties'))
	ch_para.set(odt_utils.qname('fo', 'margin-left'), '0.15in')
	ch_para.set(odt_utils.qname('fo', 'text-indent'), '-0.05in')
	# Choices3 (2 columns = 2 tab stops)
	ch3 = add_style('Choices3', 'paragraph', 'Choices')
	ch3_para = lxml.etree.SubElement(ch3, odt_utils.qname('style', 'paragraph-properties'))
	ch3_tabs = lxml.etree.SubElement(ch3_para, odt_utils.qname('style', 'tab-stops'))
	ch3_t1 = lxml.etree.SubElement(ch3_tabs, odt_utils.qname('style', 'tab-stop'))
	ch3_t1.set(odt_utils.qname('style', 'position'), '2.33in')
	ch3_t2 = lxml.etree.SubElement(ch3_tabs, odt_utils.qname('style', 'tab-stop'))
	ch3_t2.set(odt_utils.qname('style', 'position'), '4.67in')
	# Choices4 (3 columns = 3 tab stops)
	ch4 = add_style('Choices4', 'paragraph', 'Choices')
	ch4_para = lxml.etree.SubElement(ch4, odt_utils.qname('style', 'paragraph-properties'))
	ch4_tabs = lxml.etree.SubElement(ch4_para, odt_utils.qname('style', 'tab-stops'))
	for pos in ['1.75in', '3.50in', '5.25in']:
		tab = lxml.etree.SubElement(ch4_tabs, odt_utils.qname('style', 'tab-stop'))
		tab.set(odt_utils.qname('style', 'position'), pos)
	# Choices5 (4 columns = 4 tab stops)
	ch5 = add_style('Choices5', 'paragraph', 'Choices')
	ch5_para = lxml.etree.SubElement(ch5, odt_utils.qname('style', 'paragraph-properties'))
	ch5_tabs = lxml.etree.SubElement(ch5_para, odt_utils.qname('style', 'tab-stops'))
	for pos in ['1.40in', '2.80in', '4.20in', '5.60in']:
		tab = lxml.etree.SubElement(ch5_tabs, odt_utils.qname('style', 'tab-stop'))
		tab.set(odt_utils.qname('style', 'position'), pos)
	# Warning
	warn = add_style('Warning', 'paragraph', 'Standard')
	warn_para = lxml.etree.SubElement(warn, odt_utils.qname('style', 'paragraph-properties'))
	warn_para.set(odt_utils.qname('fo', 'background-color'), '#333333')
	# Preformatted Text
	pre = add_style('Preformatted_20_Text', 'paragraph', 'Standard')
	pre_text = lxml.etree.SubElement(pre, odt_utils.qname('style', 'text-properties'))
	pre_text.set(odt_utils.qname('fo', 'font-family'), 'Courier New')
	pre_text.set(odt_utils.qname('fo', 'font-size'), '10pt')
	pre_text.set(odt_utils.qname('style', 'font-pitch'), 'fixed')
	pre_para = lxml.etree.SubElement(pre, odt_utils.qname('style', 'paragraph-properties'))
	pre_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	pre_para.set(odt_utils.qname('fo', 'margin-bottom'), '0in')
	# Table Contents
	tc = add_style('Table_20_Contents', 'paragraph', 'Standard')
	tc_para = lxml.etree.SubElement(tc, odt_utils.qname('style', 'paragraph-properties'))
	tc_para.set(odt_utils.qname('fo', 'line-height'), '90%')
	tc_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	tc_para.set(odt_utils.qname('fo', 'margin-bottom'), '0in')
	# Table Heading
	th = add_style('Table_20_Heading', 'paragraph', 'Standard')
	th_text = lxml.etree.SubElement(th, odt_utils.qname('style', 'text-properties'))
	th_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	th_para = lxml.etree.SubElement(th, odt_utils.qname('style', 'paragraph-properties'))
	th_para.set(odt_utils.qname('fo', 'text-align'), 'center')
	# Heading (base)
	hb = add_style('Heading', 'paragraph', 'Standard')
	hb_text = lxml.etree.SubElement(hb, odt_utils.qname('style', 'text-properties'))
	hb_text.set(odt_utils.qname('fo', 'font-family'), 'Liberation Sans')
	hb_text.set(odt_utils.qname('fo', 'font-size'), '14pt')
	hb_para = lxml.etree.SubElement(hb, odt_utils.qname('style', 'paragraph-properties'))
	hb_para.set(odt_utils.qname('fo', 'keep-with-next'), 'always')
	hb_para.set(odt_utils.qname('fo', 'margin-top'), '0.17in')
	hb_para.set(odt_utils.qname('fo', 'margin-bottom'), '0.08in')
	# Heading 1
	h1 = add_style('Heading_20_1', 'paragraph', 'Heading')
	h1_text = lxml.etree.SubElement(h1, odt_utils.qname('style', 'text-properties'))
	h1_text.set(odt_utils.qname('fo', 'font-size'), '115%')
	h1_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# Heading 2
	h2 = add_style('Heading_20_2', 'paragraph', 'Heading')
	h2_text = lxml.etree.SubElement(h2, odt_utils.qname('style', 'text-properties'))
	h2_text.set(odt_utils.qname('fo', 'font-size'), '14pt')
	h2_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	h2_text.set(odt_utils.qname('fo', 'font-style'), 'italic')
	# Heading 3
	h3 = add_style('Heading_20_3', 'paragraph', 'Heading')
	h3_text = lxml.etree.SubElement(h3, odt_utils.qname('style', 'text-properties'))
	h3_text.set(odt_utils.qname('fo', 'font-size'), '12pt')
	h3_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# Heading 4
	h4 = add_style('Heading_20_4', 'paragraph', 'Heading')
	h4_text = lxml.etree.SubElement(h4, odt_utils.qname('style', 'text-properties'))
	h4_text.set(odt_utils.qname('fo', 'font-size'), '11pt')
	h4_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	return office_styles


#============================================
def create_page_layouts() -> tuple:
	"""Build page layout and master page elements.

	Creates three page layouts (Mpm1/Standard, Mpm2/First Page, Mpm3/HTML)
	and three corresponding master pages.

	Returns:
		Tuple of (auto_styles_element, master_styles_element).
	"""
	auto_styles = lxml.etree.Element(odt_utils.qname('office', 'automatic-styles'))
	master_styles = lxml.etree.Element(odt_utils.qname('office', 'master-styles'))
	# Mpm1 - Standard body pages (0.6in margins)
	pl1 = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'page-layout'))
	pl1.set(odt_utils.qname('style', 'name'), 'Mpm1')
	pl1_props = lxml.etree.SubElement(pl1, odt_utils.qname('style', 'page-layout-properties'))
	pl1_props.set(odt_utils.qname('fo', 'page-width'), '8.5in')
	pl1_props.set(odt_utils.qname('fo', 'page-height'), '11in')
	pl1_props.set(odt_utils.qname('fo', 'margin-top'), '0.6in')
	pl1_props.set(odt_utils.qname('fo', 'margin-bottom'), '0.6in')
	pl1_props.set(odt_utils.qname('fo', 'margin-left'), '0.6in')
	pl1_props.set(odt_utils.qname('fo', 'margin-right'), '0.6in')
	pl1_props.set(odt_utils.qname('style', 'writing-mode'), 'lr-tb')
	# Mpm2 - First Page (0.5in top/bottom, 1.0in left/right)
	pl2 = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'page-layout'))
	pl2.set(odt_utils.qname('style', 'name'), 'Mpm2')
	pl2_props = lxml.etree.SubElement(pl2, odt_utils.qname('style', 'page-layout-properties'))
	pl2_props.set(odt_utils.qname('fo', 'page-width'), '8.5in')
	pl2_props.set(odt_utils.qname('fo', 'page-height'), '11in')
	pl2_props.set(odt_utils.qname('fo', 'margin-top'), '0.5in')
	pl2_props.set(odt_utils.qname('fo', 'margin-bottom'), '0.5in')
	pl2_props.set(odt_utils.qname('fo', 'margin-left'), '1.0in')
	pl2_props.set(odt_utils.qname('fo', 'margin-right'), '1.0in')
	pl2_props.set(odt_utils.qname('style', 'writing-mode'), 'lr-tb')
	# Mpm3 - HTML import
	pl3 = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'page-layout'))
	pl3.set(odt_utils.qname('style', 'name'), 'Mpm3')
	pl3_props = lxml.etree.SubElement(pl3, odt_utils.qname('style', 'page-layout-properties'))
	pl3_props.set(odt_utils.qname('fo', 'page-width'), '8.5in')
	pl3_props.set(odt_utils.qname('fo', 'page-height'), '11in')
	pl3_props.set(odt_utils.qname('fo', 'margin-top'), '0.39in')
	pl3_props.set(odt_utils.qname('fo', 'margin-bottom'), '0.39in')
	pl3_props.set(odt_utils.qname('fo', 'margin-left'), '0.79in')
	pl3_props.set(odt_utils.qname('fo', 'margin-right'), '0.39in')
	pl3_props.set(odt_utils.qname('style', 'writing-mode'), 'lr-tb')
	# Master pages
	mp_std = lxml.etree.SubElement(master_styles, odt_utils.qname('style', 'master-page'))
	mp_std.set(odt_utils.qname('style', 'name'), 'Standard')
	mp_std.set(odt_utils.qname('style', 'page-layout-name'), 'Mpm1')
	mp_first = lxml.etree.SubElement(master_styles, odt_utils.qname('style', 'master-page'))
	mp_first.set(odt_utils.qname('style', 'name'), 'First_20_Page')
	mp_first.set(odt_utils.qname('style', 'page-layout-name'), 'Mpm2')
	mp_first.set(odt_utils.qname('style', 'next-style-name'), 'Standard')
	mp_html = lxml.etree.SubElement(master_styles, odt_utils.qname('style', 'master-page'))
	mp_html.set(odt_utils.qname('style', 'name'), 'HTML')
	mp_html.set(odt_utils.qname('style', 'page-layout-name'), 'Mpm3')
	result = (auto_styles, master_styles)
	return result


#============================================
def create_paragraph(text: str, style_name: str) -> lxml.etree._Element:
	"""Build a text:p element with the given text and style.

	Args:
		text: The text content of the paragraph.
		style_name: The style name to apply.

	Returns:
		An lxml Element for text:p.
	"""
	para = lxml.etree.Element(odt_utils.qname('text', 'p'))
	para.set(odt_utils.qname('text', 'style-name'), style_name)
	para.text = text
	return para


#============================================
def create_choices_paragraph(items: list, layout: int) -> lxml.etree._Element:
	"""Build a tab-separated choices paragraph.

	Uses Choices3 (layout 3), Choices4 (layout 4), or Choices5 (layout 5)
	style names based on the layout parameter.

	Args:
		items: List of choice text strings.
		layout: Number of choices per row (3, 4, or 5).

	Returns:
		An lxml Element for text:p with tab-separated choices.
	"""
	style = f"Choices{layout}"
	para = lxml.etree.Element(odt_utils.qname('text', 'p'))
	para.set(odt_utils.qname('text', 'style-name'), style)
	# items per row based on layout
	# Choices3 = 3 per row (2 tabs), Choices4 = 4 per row (3 tabs), Choices5 = 5 per row (4 tabs)
	items_per_row = layout
	tab_tag = odt_utils.qname('text', 'tab')
	row_items = []
	for i, item in enumerate(items):
		row_items.append(item)
		# if row is full or last item, flush the row
		if len(row_items) == items_per_row or i == len(items) - 1:
			# add this row of items
			if i >= items_per_row:
				# need a line break before new row
				line_break = lxml.etree.SubElement(para, odt_utils.qname('text', 'line-break'))
				line_break.tail = row_items[0]
			else:
				# first row
				if len(para) == 0:
					para.text = row_items[0]
				else:
					# should not happen for first row
					para.text = row_items[0]
			# add tabs between items in this row
			for j in range(1, len(row_items)):
				tab_elem = lxml.etree.SubElement(para, tab_tag)
				tab_elem.tail = row_items[j]
			row_items = []
	return para


#============================================
def create_table_cell(text: str, background_color: str,
	auto_styles: lxml.etree._Element) -> lxml.etree._Element:
	"""Build a table:table-cell element with text and optional background color.

	Creates an automatic style for the cell if a background color is specified.

	Args:
		text: Cell text content.
		background_color: Hex color string (e.g., '#f2f2f2') or None.
		auto_styles: The automatic-styles element to add cell styles to.

	Returns:
		An lxml Element for table:table-cell.
	"""
	cell = lxml.etree.Element(odt_utils.qname('table', 'table-cell'))
	cell.set(odt_utils.qname('office', 'value-type'), 'string')
	# create automatic style for cell if background color specified
	if background_color is not None:
		auto_name = next_auto_style_name()
		cell_style = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'style'))
		cell_style.set(odt_utils.qname('style', 'name'), auto_name)
		cell_style.set(odt_utils.qname('style', 'family'), 'table-cell')
		cell_props = lxml.etree.SubElement(cell_style, odt_utils.qname('style', 'table-cell-properties'))
		cell_props.set(odt_utils.qname('fo', 'background-color'), background_color)
		cell_props.set(odt_utils.qname('fo', 'padding'), '0.0194in')
		cell.set(odt_utils.qname('table', 'style-name'), auto_name)
	# add text paragraph inside cell
	para = create_paragraph(text, 'Table_20_Contents')
	cell.append(para)
	return cell


#============================================
def create_table(columns: list, rows: list,
	auto_styles: lxml.etree._Element) -> lxml.etree._Element:
	"""Build a table:table element with header row and data rows.

	The header row uses a light gray (#f2f2f2) background.

	Args:
		columns: List of column header strings.
		rows: List of row data (each row is a list of cell strings).
		auto_styles: The automatic-styles element for cell styles.

	Returns:
		An lxml Element for table:table.
	"""
	table_name = next_auto_style_name()
	table = lxml.etree.Element(odt_utils.qname('table', 'table'))
	table.set(odt_utils.qname('table', 'name'), table_name)
	# add column definitions
	for _col in columns:
		col_elem = lxml.etree.SubElement(table, odt_utils.qname('table', 'table-column'))
		col_elem.set(odt_utils.qname('table', 'number-columns-repeated'), '1')
	# header row with gray background
	header_row = lxml.etree.SubElement(table, odt_utils.qname('table', 'table-row'))
	for col_text in columns:
		cell = create_table_cell(col_text, '#f2f2f2', auto_styles)
		# use Table Heading style for header text
		para = cell.find(odt_utils.qname('text', 'p'))
		para.set(odt_utils.qname('text', 'style-name'), 'Table_20_Heading')
		header_row.append(cell)
	# data rows
	for row_data in rows:
		row = lxml.etree.SubElement(table, odt_utils.qname('table', 'table-row'))
		for cell_text in row_data:
			cell = create_table_cell(cell_text, None, auto_styles)
			row.append(cell)
	return table


#============================================
def embed_image(image_path: str, odt_other_data: dict) -> lxml.etree._Element:
	"""Add an image to the ODT and return a draw:frame element.

	Reads the image file and stores it in the Pictures/ directory
	within the ODT archive.

	Args:
		image_path: Path to the image file on disk.
		odt_other_data: The other_data dict to add image bytes to.

	Returns:
		An lxml Element for draw:frame containing draw:image.
	"""
	# determine the image filename
	image_name = os.path.basename(image_path)
	odt_image_path = f"Pictures/{image_name}"
	# read image bytes
	with open(image_path, 'rb') as f:
		image_bytes = f.read()
	odt_other_data[odt_image_path] = image_bytes
	# create draw:frame
	frame = lxml.etree.Element(odt_utils.qname('draw', 'frame'))
	frame.set(odt_utils.qname('draw', 'name'), image_name)
	frame.set(odt_utils.qname('text', 'anchor-type'), 'as-char')
	frame.set(odt_utils.qname('svg', 'width'), '4in')
	frame.set(odt_utils.qname('svg', 'height'), '3in')
	# create draw:image inside frame
	image = lxml.etree.SubElement(frame, odt_utils.qname('draw', 'image'))
	image.set(odt_utils.qname('xlink', 'href'), odt_image_path)
	image.set(odt_utils.qname('xlink', 'type'), 'simple')
	image.set(odt_utils.qname('xlink', 'show'), 'embed')
	image.set(odt_utils.qname('xlink', 'actuate'), 'onLoad')
	return frame


#============================================
def build_document_body(exam_data: dict,
	auto_styles: lxml.etree._Element,
	other_data: dict) -> lxml.etree._Element:
	"""Build the office:body > office:text element tree from exam data.

	Args:
		exam_data: Dict from YAML input with exam structure.
		auto_styles: The automatic-styles element for cell/table styles.
		other_data: Dict for storing embedded image data.

	Returns:
		An lxml Element for office:body.
	"""
	body = lxml.etree.Element(odt_utils.qname('office', 'body'))
	text = lxml.etree.SubElement(body, odt_utils.qname('office', 'text'))
	# exam title
	title = exam_data.get('title', 'Exam')
	title_para = create_paragraph(title, 'Heading_20_1')
	text.append(title_para)
	# date line
	date_str = exam_data.get('date', '')
	if date_str:
		date_para = create_paragraph(date_str, 'Standard')
		text.append(date_para)
	# student info line
	student_line = exam_data.get('student_line', '')
	if student_line:
		student_para = create_paragraph(student_line, 'Standard')
		text.append(student_para)
	# sections
	sections = exam_data.get('sections', [])
	for section in sections:
		# section heading
		heading = section.get('heading', '')
		if heading:
			heading_para = create_paragraph(heading, 'Heading_20_4')
			text.append(heading_para)
		# questions
		questions = section.get('questions', [])
		for question in questions:
			# question heading
			q_heading = question.get('heading', '')
			if q_heading:
				qh_para = create_paragraph(q_heading, 'Question_20_Heading')
				text.append(qh_para)
			# question text
			q_text = question.get('text', '')
			if q_text:
				qt_para = create_paragraph(q_text, 'Question')
				text.append(qt_para)
			# choices
			choices = question.get('choices', None)
			if choices is not None:
				layout = choices.get('layout', 4)
				items = choices.get('items', [])
				if items:
					choices_para = create_choices_paragraph(items, layout)
					text.append(choices_para)
			# table
			table_data = question.get('table', None)
			if table_data is not None:
				columns = table_data['columns']
				rows = table_data['rows']
				table_elem = create_table(columns, rows, auto_styles)
				text.append(table_elem)
			# image
			image_path = question.get('image', None)
			if image_path is not None and os.path.isfile(image_path):
				frame = embed_image(image_path, other_data)
				# wrap frame in a paragraph
				img_para = lxml.etree.Element(odt_utils.qname('text', 'p'))
				img_para.set(odt_utils.qname('text', 'style-name'), 'Standard')
				img_para.append(frame)
				text.append(img_para)
	return body


#============================================
def assemble_odt(exam_data: dict, output_path: str) -> None:
	"""Assemble a complete ODT document and write to file.

	Creates all styles, page layouts, and body content,
	then writes the ODT via odt_utils.write_odt().

	Args:
		exam_data: Dict from YAML input with exam structure.
		output_path: Path for the output ODT file.
	"""
	# reset auto style counter
	global AUTO_STYLE_COUNTER
	AUTO_STYLE_COUNTER = 0
	# build the styles.xml tree
	nsmap = {}
	for prefix, uri in odt_utils.ODF_NAMESPACES.items():
		nsmap[prefix] = uri
	styles_root = lxml.etree.Element(
		odt_utils.qname('office', 'document-styles'), nsmap=nsmap
	)
	# add named styles
	office_styles = create_exam_styles()
	styles_root.append(office_styles)
	# add page layouts and master pages
	auto_styles_elem, master_styles_elem = create_page_layouts()
	styles_root.append(auto_styles_elem)
	styles_root.append(master_styles_elem)
	# build the content.xml tree
	content_root = lxml.etree.Element(
		odt_utils.qname('office', 'document-content'), nsmap=nsmap
	)
	# automatic styles for content (tables, cells)
	content_auto_styles = lxml.etree.SubElement(
		content_root, odt_utils.qname('office', 'automatic-styles')
	)
	# prepare other_data for embedded images
	other_data = {}
	# build body
	body = build_document_body(exam_data, content_auto_styles, other_data)
	content_root.append(body)
	# build manifest
	manifest_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<manifest:manifest'
		' xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
		'<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
		'<manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>'
		'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
		'</manifest:manifest>'
	)
	# build mimetype
	mimetype = b"application/vnd.oasis.opendocument.text"
	# assemble other_entries and other_data
	other_entries = []
	# add mimetype
	mime_info = zipfile.ZipInfo('mimetype')
	other_entries.append(mime_info)
	other_data['mimetype'] = mimetype
	# add manifest
	manifest_info = zipfile.ZipInfo('META-INF/manifest.xml')
	other_entries.append(manifest_info)
	other_data['META-INF/manifest.xml'] = manifest_xml.encode('utf-8')
	# add image entries
	for img_path, img_bytes in list(other_data.items()):
		if img_path.startswith('Pictures/'):
			img_info = zipfile.ZipInfo(img_path)
			other_entries.append(img_info)
	# build the odt_data dict for write_odt
	odt_data = {
		'styles_xml': styles_root,
		'content_xml': content_root,
		'zip_path': output_path,
		'other_entries': other_entries,
		'other_data': other_data,
	}
	odt_utils.write_odt(odt_data, output_path)


#============================================
def main():
	"""Main entry point for ODT exam builder."""
	args = parse_args()
	exam_data = load_exam_data(args.input_file)
	assemble_odt(exam_data, args.output_file)
	print(f"Exam ODT written to {args.output_file}")


#============================================
if __name__ == '__main__':
	main()
