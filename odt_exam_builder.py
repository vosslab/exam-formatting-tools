#!/usr/bin/env python3
"""Generate a fully styled ODT exam document from structured YAML input.

Creates an ODT file with all named styles from docs/ODT_EXAM_STYLES.md
embedded, including page layouts, master pages, question formatting,
multiple choice layouts, tables, and embedded images.
"""

# Standard Library
import os
import re
import html
import zipfile
import argparse

# Pip Modules
import yaml
import lxml.etree
import PIL.Image

# Local Repo Modules
import odt_utils
import exam_defaults


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
	# Question Heading
	qh = add_style('Question Heading', 'paragraph', 'Standard')
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
	q = add_style('Question', 'paragraph', 'Question Heading')
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
	add_style('Question Follow', 'paragraph', 'Standard')
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
	pre = add_style('Preformatted Text', 'paragraph', 'Standard')
	pre_text = lxml.etree.SubElement(pre, odt_utils.qname('style', 'text-properties'))
	pre_text.set(odt_utils.qname('fo', 'font-family'), 'Courier New')
	pre_text.set(odt_utils.qname('fo', 'font-size'), '10pt')
	pre_text.set(odt_utils.qname('style', 'font-pitch'), 'fixed')
	pre_para = lxml.etree.SubElement(pre, odt_utils.qname('style', 'paragraph-properties'))
	pre_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	pre_para.set(odt_utils.qname('fo', 'margin-bottom'), '0in')
	# Table Contents
	tc = add_style('Table Contents', 'paragraph', 'Standard')
	tc_para = lxml.etree.SubElement(tc, odt_utils.qname('style', 'paragraph-properties'))
	tc_para.set(odt_utils.qname('fo', 'line-height'), '90%')
	tc_para.set(odt_utils.qname('fo', 'margin-top'), '0in')
	tc_para.set(odt_utils.qname('fo', 'margin-bottom'), '0in')
	# Table Heading
	th = add_style('Table Heading', 'paragraph', 'Standard')
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
	h1 = add_style('Heading 1', 'paragraph', 'Heading')
	h1_text = lxml.etree.SubElement(h1, odt_utils.qname('style', 'text-properties'))
	h1_text.set(odt_utils.qname('fo', 'font-size'), '115%')
	h1_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# Heading 2
	h2 = add_style('Heading 2', 'paragraph', 'Heading')
	h2_text = lxml.etree.SubElement(h2, odt_utils.qname('style', 'text-properties'))
	h2_text.set(odt_utils.qname('fo', 'font-size'), '14pt')
	h2_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	h2_text.set(odt_utils.qname('fo', 'font-style'), 'italic')
	# Heading 3
	h3 = add_style('Heading 3', 'paragraph', 'Heading')
	h3_text = lxml.etree.SubElement(h3, odt_utils.qname('style', 'text-properties'))
	h3_text.set(odt_utils.qname('fo', 'font-size'), '12pt')
	h3_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# Heading 4
	h4 = add_style('Heading 4', 'paragraph', 'Heading')
	h4_text = lxml.etree.SubElement(h4, odt_utils.qname('style', 'text-properties'))
	h4_text.set(odt_utils.qname('fo', 'font-size'), '11pt')
	h4_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# Chapter Heading (14pt bold, dark purple #6600cc, Liberation Sans/Arial, keep-with-next)
	ch = add_style('Chapter Heading', 'paragraph', 'Standard')
	ch_text = lxml.etree.SubElement(ch, odt_utils.qname('style', 'text-properties'))
	ch_text.set(odt_utils.qname('fo', 'font-family'), 'Liberation Sans')
	ch_text.set(odt_utils.qname('fo', 'font-size'), '14pt')
	ch_text.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	ch_text.set(odt_utils.qname('fo', 'color'), '#6600cc')
	ch_para = lxml.etree.SubElement(ch, odt_utils.qname('style', 'paragraph-properties'))
	ch_para.set(odt_utils.qname('fo', 'keep-with-next'), 'always')
	ch_para.set(odt_utils.qname('fo', 'margin-top'), '0.15in')
	ch_para.set(odt_utils.qname('fo', 'margin-bottom'), '0.08in')
	# Header (for page headers on body pages)
	hdr = add_style('Header', 'paragraph', 'Standard')
	hdr_text = lxml.etree.SubElement(hdr, odt_utils.qname('style', 'text-properties'))
	hdr_text.set(odt_utils.qname('fo', 'font-size'), '9pt')
	hdr_para = lxml.etree.SubElement(hdr, odt_utils.qname('style', 'paragraph-properties'))
	hdr_tabs = lxml.etree.SubElement(hdr_para, odt_utils.qname('style', 'tab-stops'))
	# center tab at ~3.6in (middle of page with 0.6in margins on 8.5in page)
	center_tab = lxml.etree.SubElement(hdr_tabs, odt_utils.qname('style', 'tab-stop'))
	center_tab.set(odt_utils.qname('style', 'position'), '3.65in')
	center_tab.set(odt_utils.qname('style', 'type'), 'center')
	# right tab at ~7.3in (page width 8.5 - 0.6 margins = 7.3, minus some padding)
	right_tab = lxml.etree.SubElement(hdr_tabs, odt_utils.qname('style', 'tab-stop'))
	right_tab.set(odt_utils.qname('style', 'position'), '7.3in')
	right_tab.set(odt_utils.qname('style', 'type'), 'right')
	# Right Aligned (for name/score lines on title page)
	ra = add_style('Right Aligned', 'paragraph', 'Standard')
	ra_para = lxml.etree.SubElement(ra, odt_utils.qname('style', 'paragraph-properties'))
	ra_para.set(odt_utils.qname('fo', 'text-align'), 'end')
	return office_styles


#============================================
def create_page_layouts(date_str: str = "") -> tuple:
	"""Build page layout and master page elements.

	Creates three page layouts (Mpm1/Standard, Mpm2/First Page, Mpm3/HTML)
	and three corresponding master pages. The Standard master page includes
	a header with page numbers, date, and student name line.

	Args:
		date_str: Date string to embed in the header of body pages.

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
	# Mpm2 - First Page (same 0.6in margins as body pages, no header)
	pl2 = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'page-layout'))
	pl2.set(odt_utils.qname('style', 'name'), 'Mpm2')
	pl2_props = lxml.etree.SubElement(pl2, odt_utils.qname('style', 'page-layout-properties'))
	pl2_props.set(odt_utils.qname('fo', 'page-width'), '8.5in')
	pl2_props.set(odt_utils.qname('fo', 'page-height'), '11in')
	pl2_props.set(odt_utils.qname('fo', 'margin-top'), '0.6in')
	pl2_props.set(odt_utils.qname('fo', 'margin-bottom'), '0.6in')
	pl2_props.set(odt_utils.qname('fo', 'margin-left'), '0.6in')
	pl2_props.set(odt_utils.qname('fo', 'margin-right'), '0.6in')
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
	# add header to Standard master page
	hdr_std = lxml.etree.SubElement(mp_std, odt_utils.qname('style', 'header'))
	hdr_std_para = lxml.etree.SubElement(hdr_std, odt_utils.qname('text', 'p'))
	hdr_std_para.set(odt_utils.qname('text', 'style-name'), 'Header')
	# "Page X of Y"
	hdr_std_para.text = "Page "
	page_num = lxml.etree.SubElement(hdr_std_para, odt_utils.qname('text', 'page-number'))
	page_num.set(odt_utils.qname('text', 'select-page'), 'current')
	page_num.text = "1"
	page_num.tail = " of "
	page_count = lxml.etree.SubElement(hdr_std_para, odt_utils.qname('text', 'page-count'))
	page_count.text = "1"
	page_count.tail = None
	# tab to center position (for date)
	tab1 = lxml.etree.SubElement(hdr_std_para, odt_utils.qname('text', 'tab'))
	tab1.tail = date_str
	# tab to right position (for student name line)
	tab2 = lxml.etree.SubElement(hdr_std_para, odt_utils.qname('text', 'tab'))
	if date_str:
		tab2.tail = "First Name:_____________________________"
	else:
		tab2.tail = "First Name:_____________________________"
	# add header style properties to page layout Mpm1
	hdr_style = lxml.etree.SubElement(pl1, odt_utils.qname('style', 'header-style'))
	hdr_style_props = lxml.etree.SubElement(hdr_style, odt_utils.qname('style', 'header-footer-properties'))
	hdr_style_props.set(odt_utils.qname('fo', 'min-height'), '0in')
	hdr_style_props.set(odt_utils.qname('fo', 'margin-bottom'), '0.2in')
	# First Page master
	mp_first = lxml.etree.SubElement(master_styles, odt_utils.qname('style', 'master-page'))
	mp_first.set(odt_utils.qname('style', 'name'), 'First Page')
	mp_first.set(odt_utils.qname('style', 'page-layout-name'), 'Mpm2')
	mp_first.set(odt_utils.qname('style', 'next-style-name'), 'Standard')
	# add empty header to First Page master
	hdr_first = lxml.etree.SubElement(mp_first, odt_utils.qname('style', 'header'))
	hdr_first_para = lxml.etree.SubElement(hdr_first, odt_utils.qname('text', 'p'))
	hdr_first_para.set(odt_utils.qname('text', 'style-name'), 'Header')
	# HTML master page
	mp_html = lxml.etree.SubElement(master_styles, odt_utils.qname('style', 'master-page'))
	mp_html.set(odt_utils.qname('style', 'name'), 'HTML')
	mp_html.set(odt_utils.qname('style', 'page-layout-name'), 'Mpm3')
	result = (auto_styles, master_styles)
	return result


#============================================
def decode_html_entities(text: str) -> str:
	"""Decode HTML entities to Unicode characters for ODT output.

	YAML files use ASCII HTML entities (e.g., &Delta;, &alpha;) for
	special characters. This converts them to Unicode for rendering.

	Args:
		text: Text that may contain HTML entities.

	Returns:
		Text with entities decoded to Unicode.
	"""
	decoded = html.unescape(text)
	return decoded


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
	# decode HTML entities from YAML ASCII to Unicode for ODT
	para.text = decode_html_entities(text)
	return para


#============================================
def auto_layout_for_choices(choices: list) -> int:
	"""Determine appropriate Choices layout based on choice count and text length.

	Approximate character limits per column (10pt Liberation Sans + bold "(A) " prefix):
	- Choices5: ~12 chars per choice text (column width ~1.40in)
	- Choices4: ~16 chars per choice text (column width ~1.75in)
	- Choices3: ~22 chars per choice text (column width ~2.33in)
	- Choices4 with 2 items: uses 4 % 2 == 0 property for even spacing

	Args:
		choices: List of choice text strings.

	Returns:
		Layout integer (3, 4, or 5).
	"""
	# approximate max chars per column for each layout at 10pt Liberation Sans
	# column widths: Choices5=1.40in, Choices4=1.75in, Choices3=2.33in
	# empirically measured with bold "(A) " prefix included
	MAX_CHARS_5 = 18
	MAX_CHARS_4 = 24
	MAX_CHARS_3 = 31
	count = len(choices)
	if count < 1:
		return 5
	max_len = max(len(c) for c in choices)
	# 2 choices: use Choices4 since 4 % 2 == 0 gives even spacing
	# each item spans 2 columns (~50 chars per choice)
	MAX_CHARS_2 = 50
	if count == 2:
		if max_len <= MAX_CHARS_2:
			return 4
		# very long 2-item choices: use Choices3 for more space
		return 3
	# 3 choices: use Choices3 if they fit, otherwise Choices4 with overflow
	if count == 3:
		if max_len <= MAX_CHARS_3:
			return 3
		return 4
	# 4 choices: use Choices4 if they fit, otherwise Choices3 with overflow
	if count == 4:
		if max_len <= MAX_CHARS_4:
			return 4
		return 3
	# 5+ choices: pick best fit from tightest to widest
	if max_len <= MAX_CHARS_5:
		return 5
	if max_len <= MAX_CHARS_4:
		return 4
	# long choices need Choices3 with overflow rows
	return 3


#============================================
def create_choices_paragraph(choices: list, layout: int,
	auto_styles: lxml.etree._Element = None) -> lxml.etree._Element:
	"""Build a tab-separated choices paragraph with bold letter prefixes.

	Uses Choices3 (layout 3), Choices4 (layout 4), or Choices5 (layout 5)
	style names based on the layout parameter. Generates bold **(A) (B) (C)**
	letter prefixes automatically.

	Args:
		choices: List of plain choice text strings (without letter prefixes).
		layout: Number of choices per row (3, 4, or 5).
		auto_styles: Optional automatic-styles element for bold style creation.

	Returns:
		An lxml Element for text:p with tab-separated choices and bold prefixes.
	"""
	style = f"Choices{layout}"
	para = lxml.etree.Element(odt_utils.qname('text', 'p'))
	para.set(odt_utils.qname('text', 'style-name'), style)
	# items per row based on layout
	# Choices3 = 3 per row (2 tabs), Choices4 = 4 per row (3 tabs), Choices5 = 5 per row (4 tabs)
	items_per_row = layout
	tab_tag = odt_utils.qname('text', 'tab')
	span_tag = odt_utils.qname('text', 'span')
	# ensure AutoBold style exists if auto_styles provided
	bold_style_name = 'AutoBold'
	if auto_styles is not None:
		# check if AutoBold exists
		bold_exists = False
		for style_elem in auto_styles.findall(odt_utils.qname('style', 'style')):
			if style_elem.get(odt_utils.qname('style', 'name')) == 'AutoBold':
				bold_exists = True
				break
		# create AutoBold if not found
		if not bold_exists:
			bold_style = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'style'))
			bold_style.set(odt_utils.qname('style', 'name'), 'AutoBold')
			bold_style.set(odt_utils.qname('style', 'family'), 'text')
			text_props = lxml.etree.SubElement(bold_style, odt_utils.qname('style', 'text-properties'))
			text_props.set(odt_utils.qname('fo', 'font-weight'), 'bold')
	# build choices with bold letter prefixes and tabs
	for i, choice_text in enumerate(choices):
		letter = chr(ord('A') + i)
		# insert line break before new rows (after first row)
		if i > 0 and i % items_per_row == 0:
			lxml.etree.SubElement(para, odt_utils.qname('text', 'line-break'))
		# add tab before this choice (except first in row)
		if i > 0 and i % items_per_row > 0:
			lxml.etree.SubElement(para, tab_tag)
		# add bold letter prefix as span
		span = lxml.etree.SubElement(para, span_tag)
		span.set(odt_utils.qname('text', 'style-name'), bold_style_name)
		span.text = f"({letter}) "
		span.tail = decode_html_entities(choice_text)
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
	para = create_paragraph(text, 'Table Contents')
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
		para.set(odt_utils.qname('text', 'style-name'), 'Table Heading')
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
	# get actual image dimensions and preserve aspect ratio
	img = PIL.Image.open(image_path)
	pixel_width, pixel_height = img.size
	# scale to fit within max_width while preserving aspect ratio
	max_width_in = 5.0
	aspect_ratio = pixel_height / pixel_width
	display_width = min(max_width_in, pixel_width / 96.0)
	display_height = display_width * aspect_ratio
	# create draw:frame
	frame = lxml.etree.Element(odt_utils.qname('draw', 'frame'))
	frame.set(odt_utils.qname('draw', 'name'), image_name)
	frame.set(odt_utils.qname('text', 'anchor-type'), 'as-char')
	frame.set(odt_utils.qname('svg', 'width'), f"{display_width:.2f}in")
	frame.set(odt_utils.qname('svg', 'height'), f"{display_height:.2f}in")
	# create draw:image inside frame
	image = lxml.etree.SubElement(frame, odt_utils.qname('draw', 'image'))
	image.set(odt_utils.qname('xlink', 'href'), odt_image_path)
	image.set(odt_utils.qname('xlink', 'type'), 'simple')
	image.set(odt_utils.qname('xlink', 'show'), 'embed')
	image.set(odt_utils.qname('xlink', 'actuate'), 'onLoad')
	return frame


#============================================
def select_question_style(prev_element: str) -> str:
	"""Select appropriate question paragraph style based on previous element.

	"Question Heading" is used for questions in normal sequential flow
	(after other questions or choices).

	"Question Follow" is used for questions immediately after a non-question
	element (image, table, or chapter heading).

	Args:
		prev_element: Type of the previous element ('question', 'choices',
			'chapter', 'table', or 'image').

	Returns:
		Style name: 'Question Heading' or 'Question Follow'.
	"""
	if prev_element in ('question', 'choices'):
		return 'Question Heading'
	else:
		# prev_element is 'chapter', 'table', or 'image'
		return 'Question Follow'


#============================================
def count_total_questions(sections: list) -> int:
	"""Count total number of questions across all sections.

	Args:
		sections: List of section dicts from exam data.

	Returns:
		Total count of questions.
	"""
	total = 0
	for section in sections:
		questions = section.get('questions', [])
		total += len(questions)
	return total


#============================================
def build_document_body(exam_data: dict,
	auto_styles: lxml.etree._Element,
	other_data: dict) -> lxml.etree._Element:
	"""Build the office:body > office:text element tree from exam data.

	Processes new YAML format with auto-numbering and auto-layout.
	Auto-selects "Question Heading" or "Question Follow" style based on
	what element precedes the question.

	Args:
		exam_data: Dict from YAML input with exam structure.
		auto_styles: The automatic-styles element for cell/table styles.
		other_data: Dict for storing embedded image data.

	Returns:
		An lxml Element for office:body.
	"""
	body = lxml.etree.Element(odt_utils.qname('office', 'body'))
	text = lxml.etree.SubElement(body, odt_utils.qname('office', 'text'))
	# exam title (first page uses First Page master for no header)
	title = exam_data.get('title', 'Exam')
	# create automatic style that references First Page master
	title_auto_name = next_auto_style_name()
	title_auto = lxml.etree.SubElement(auto_styles, odt_utils.qname('style', 'style'))
	title_auto.set(odt_utils.qname('style', 'name'), title_auto_name)
	title_auto.set(odt_utils.qname('style', 'family'), 'paragraph')
	title_auto.set(odt_utils.qname('style', 'parent-style-name'), 'Heading 1')
	title_auto.set(odt_utils.qname('style', 'master-page-name'), 'First Page')
	title_para = create_paragraph(title, title_auto_name)
	text.append(title_para)
	# calculate total points
	total_points = exam_data.get('total_points', None)
	if total_points is None:
		sections = exam_data.get('sections', [])
		total_points = count_total_questions(sections)
	# scoring sections (number of blanks in score line)
	num_sections = exam_data.get('scoring_sections', exam_defaults.DEFAULT_SCORING_SECTIONS)
	# name line shifted right with tab (matching ARTIFACTS pattern)
	name_line = exam_data.get('student_line', exam_defaults.DEFAULT_NAME_LINE)
	name_para = lxml.etree.Element(odt_utils.qname('text', 'p'))
	name_para.set(odt_utils.qname('text', 'style-name'), 'Question')
	# use tab to shift text to right side of page
	tab_elem = lxml.etree.SubElement(name_para, odt_utils.qname('text', 'tab'))
	tab_elem.tail = name_line
	text.append(name_para)
	# score line shifted right with tab
	score_line = exam_defaults.format_score_line(total_points, num_sections)
	score_para = lxml.etree.Element(odt_utils.qname('text', 'p'))
	score_para.set(odt_utils.qname('text', 'style-name'), 'Question')
	tab_elem2 = lxml.etree.SubElement(score_para, odt_utils.qname('text', 'tab'))
	tab_elem2.tail = score_line
	text.append(score_para)
	# sections
	sections = exam_data.get('sections', [])
	question_counter = 1  # auto-numbering counter
	# track previous element type for question style selection
	prev_element = 'chapter'  # start of section counts as chapter heading
	for section in sections:
		# section heading: 'heading' for major sections (Heading 2), 'chapter' for chapters (level 3)
		heading = section.get('heading', '')
		if heading:
			heading_para = create_paragraph(heading, 'Heading 2')
			text.append(heading_para)
			prev_element = 'chapter'
		chapter = section.get('chapter', '')
		if chapter:
			chapter_para = create_paragraph(chapter, 'Chapter Heading')
			text.append(chapter_para)
			prev_element = 'chapter'
		# questions
		questions = section.get('questions', [])
		for question in questions:
			# get explicit number if provided, otherwise use counter
			if 'number' in question:
				question_counter = question['number']
			question_number = question_counter
			# build question statement with number prefix
			statement = question.get('statement', '')
			if statement:
				# strip any existing number prefix (e.g., "22) " or "22. ")
				stripped = re.sub(r'^\d+[).]\s*', '', statement)
				# prepend number: "##. statement text"
				q_text_with_num = f"{question_number}. {stripped}"
				# select question style based on previous element
				question_style = select_question_style(prev_element)
				qh_para = create_paragraph(q_text_with_num, question_style)
				text.append(qh_para)
				prev_element = 'question'
			# choices
			choices = question.get('choices', None)
			if choices is not None and len(choices) > 0:
				# auto-determine layout if not specified
				layout = question.get('layout', None)
				if layout is None:
					layout = auto_layout_for_choices(choices)
				choices_para = create_choices_paragraph(choices, layout, auto_styles)
				text.append(choices_para)
				prev_element = 'choices'
			# table
			table_data = question.get('table', None)
			if table_data is not None:
				columns = table_data['columns']
				rows = table_data['rows']
				table_elem = create_table(columns, rows, auto_styles)
				text.append(table_elem)
				prev_element = 'table'
			# image
			image_path = question.get('image', None)
			if image_path is not None and os.path.isfile(image_path):
				frame = embed_image(image_path, other_data)
				# wrap frame in a paragraph
				img_para = lxml.etree.Element(odt_utils.qname('text', 'p'))
				img_para.set(odt_utils.qname('text', 'style-name'), 'Standard')
				img_para.append(frame)
				text.append(img_para)
				prev_element = 'image'
			# increment counter for next question
			question_counter += 1
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
	date_str = exam_data.get('date', '')
	auto_styles_elem, master_styles_elem = create_page_layouts(date_str)
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
