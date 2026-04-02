#!/usr/bin/env python3
"""Generate a styled DOCX exam document from structured YAML input.

Uses python-docx to create a Word document with exam styles, auto-numbering,
bold choice prefixes, images, tables, and page headers. Reads the YAML exam
format (see docs/YAML_EXAM_FORMAT.md) and styles from styles/exam_styles.yaml.
"""

# Standard Library
import os
import argparse

# Pip Modules
import yaml
import docx
import docx.shared
import docx.enum.text
import docx.enum.style
import docx.oxml.ns
import docx.oxml

# Local Repo Modules
import ef_tools.layout
import ef_tools.text_utils
import ef_tools.style_loader
import ef_tools.exam_defaults
import ef_tools.question_utils


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Generate a styled DOCX exam document from YAML input"
	)
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help="Input YAML file with exam data"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', required=True,
		help="Output DOCX file path (must not already exist)"
	)
	args = parser.parse_args()
	return args


#============================================
def _set_font_with_fallback(style, primary: str, fallback: str) -> None:
	"""Set font name on a style with a fallback font via XML.

	python-docx only supports a single font name. This sets the primary
	font and adds the fallback as hAnsi/cs font for cross-platform
	compatibility (Liberation Sans on Linux, Arial on Windows/Mac).

	Args:
		style: A python-docx paragraph or character style.
		primary: Primary font name (e.g., 'Liberation Sans').
		fallback: Fallback font name (e.g., 'Arial').
	"""
	style.font.name = primary
	# set the fallback font on the underlying XML for non-ascii/hAnsi
	rpr = style.element.get_or_add_rPr()
	rfonts_tag = docx.oxml.ns.qn('w:rFonts')
	rfonts = rpr.find(rfonts_tag)
	if rfonts is None:
		rfonts = docx.oxml.OxmlElement('w:rFonts')
		rpr.insert(0, rfonts)
	rfonts.set(docx.oxml.ns.qn('w:ascii'), primary)
	rfonts.set(docx.oxml.ns.qn('w:hAnsi'), fallback)
	rfonts.set(docx.oxml.ns.qn('w:cs'), fallback)


#============================================
def _parse_hex_color(hex_str: str) -> docx.shared.RGBColor:
	"""Parse a hex color string like '#6600CC' into an RGBColor.

	Args:
		hex_str: Color string with leading '#'.

	Returns:
		RGBColor object.
	"""
	hex_str = hex_str.lstrip('#')
	r = int(hex_str[0:2], 16)
	g = int(hex_str[2:4], 16)
	b = int(hex_str[4:6], 16)
	color = docx.shared.RGBColor(r, g, b)
	return color


#============================================
def setup_styles(doc: docx.Document, styles: dict) -> None:
	"""Create all named exam styles in the document.

	Reads font, size, color, and spacing values from the styles dict
	(loaded from styles/exam_styles.yaml).

	Args:
		doc: The Document to add styles to.
		styles: Style definitions dict from YAML.
	"""
	fonts = styles['fonts']
	sizes = styles['sizes']
	colors = styles['colors']
	spacing = styles['spacing']

	# modify the built-in Normal style as our base
	normal = doc.styles['Normal']
	normal.font.size = docx.shared.Pt(sizes['normal'])
	normal.paragraph_format.space_after = docx.shared.Pt(spacing['normal_space_after_pt'])
	normal.paragraph_format.space_before = docx.shared.Pt(0)
	normal.paragraph_format.line_spacing = spacing['normal_line_spacing']
	_set_font_with_fallback(normal, fonts['primary'], fonts['fallback'])

	# customize built-in Heading 1: bold, keep-with-next
	h1 = doc.styles['Heading 1']
	h1.font.size = docx.shared.Pt(sizes['heading_1'])
	h1.font.bold = True
	h1.font.italic = False
	h1.font.color.rgb = docx.shared.RGBColor(0x00, 0x00, 0x00)
	h1.paragraph_format.space_before = docx.shared.Inches(spacing['heading_space_before'])
	h1.paragraph_format.space_after = docx.shared.Inches(spacing['heading_space_after'])
	h1.paragraph_format.keep_with_next = True
	_set_font_with_fallback(h1, fonts['primary'], fonts['fallback'])

	# Question Heading: bold italic, hanging indent, keep-with-next
	qh = doc.styles.add_style('Question Heading', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	qh.base_style = normal
	qh.font.bold = True
	qh.font.italic = True
	qh.font.size = docx.shared.Pt(sizes['question'])
	qh.paragraph_format.left_indent = docx.shared.Inches(spacing['question_indent'])
	qh.paragraph_format.first_line_indent = docx.shared.Inches(spacing['question_hanging'])
	qh.paragraph_format.space_before = docx.shared.Inches(spacing['question_heading_space_before'])
	qh.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qh.paragraph_format.keep_with_next = True

	# Question Follow: same as Question Heading but no space above
	qf = doc.styles.add_style('Question Follow', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	qf.base_style = normal
	qf.font.bold = True
	qf.font.italic = True
	qf.font.size = docx.shared.Pt(sizes['question'])
	qf.paragraph_format.left_indent = docx.shared.Inches(spacing['question_indent'])
	qf.paragraph_format.first_line_indent = docx.shared.Inches(spacing['question_hanging'])
	qf.paragraph_format.space_before = docx.shared.Pt(0)
	qf.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qf.paragraph_format.keep_with_next = True

	# Chapter Heading: bold, dark purple, keep-with-next
	ch = doc.styles.add_style('Chapter Heading', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	ch.base_style = normal
	ch.font.size = docx.shared.Pt(sizes['chapter_heading'])
	_set_font_with_fallback(ch, fonts['primary'], fonts['fallback'])
	ch.font.bold = True
	ch.font.color.rgb = _parse_hex_color(colors['chapter_heading'])
	ch.paragraph_format.space_before = docx.shared.Pt(spacing['chapter_space_before_pt'])
	ch.paragraph_format.space_after = docx.shared.Pt(spacing['chapter_space_after_pt'])
	ch.paragraph_format.keep_with_next = True

	# Heading 2: bold italic, for major section labels
	h2 = doc.styles.add_style('Exam Heading 2', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	h2.base_style = normal
	h2.font.size = docx.shared.Pt(sizes['heading_2'])
	_set_font_with_fallback(h2, fonts['primary'], fonts['fallback'])
	h2.font.bold = True
	h2.font.italic = True
	h2.paragraph_format.space_before = docx.shared.Pt(spacing['chapter_space_before_pt'])
	h2.paragraph_format.space_after = docx.shared.Pt(spacing['chapter_space_after_pt'])
	h2.paragraph_format.keep_with_next = True

	# Choice: base style for all choice layouts
	choice_base = doc.styles.add_style('Choice', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	choice_base.base_style = normal
	choice_base.font.size = docx.shared.Pt(sizes['choice'])
	choice_base.paragraph_format.left_indent = docx.shared.Inches(spacing['choice_indent'])
	choice_first_line = spacing['choice_first_line_indent']
	if choice_first_line != 0:
		choice_base.paragraph_format.first_line_indent = docx.shared.Inches(choice_first_line)
	choice_base.paragraph_format.space_before = docx.shared.Pt(0)
	choice_base.paragraph_format.space_after = docx.shared.Pt(spacing['normal_space_after_pt'])

	# Choices 2 through 5: inherit from Choice, tab stops set per-paragraph
	for n in range(2, 6):
		style = doc.styles.add_style(f'Choices {n}', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
		style.base_style = choice_base


#============================================
def add_page_number_field(paragraph) -> None:
	"""Add 'Page X of Y' field codes to a paragraph using raw XML.

	python-docx does not have native page number field support,
	so we insert the Word XML field elements directly.

	Args:
		paragraph: The paragraph to add page numbers to.
	"""
	# "Page " text
	run_page = paragraph.add_run("Page ")
	run_page.font.size = docx.shared.Pt(9)
	# PAGE field
	run1 = paragraph.add_run()
	run1.font.size = docx.shared.Pt(9)
	fld_simple_page = docx.oxml.OxmlElement('w:fldSimple')
	fld_simple_page.set(docx.oxml.ns.qn('w:instr'), ' PAGE ')
	run1._element.addnext(fld_simple_page)
	# " of " text
	run_of = paragraph.add_run(" of ")
	run_of.font.size = docx.shared.Pt(9)
	# NUMPAGES field
	run2 = paragraph.add_run()
	run2.font.size = docx.shared.Pt(9)
	fld_simple_total = docx.oxml.OxmlElement('w:fldSimple')
	fld_simple_total.set(docx.oxml.ns.qn('w:instr'), ' NUMPAGES ')
	run2._element.addnext(fld_simple_total)


#============================================
def setup_header(section, date_str: str, styles: dict) -> None:
	"""Configure page header on body pages with page number, date, and name.

	Sets up different first page header (empty) and body page header with
	'Page X of Y | date | First Name:___' layout using tab stops.

	Args:
		section: The document section to configure.
		date_str: Date string to display in header center.
		styles: Style definitions dict from YAML.
	"""
	page = styles['page']
	header_size = styles['sizes']['header']

	# enable different first page header (empty on page 1)
	section.different_first_page_header_footer = True

	# body page header: "Page X of Y [tab] date [tab] First Name:___"
	header = section.header
	header.is_linked_to_previous = False
	header_para = header.paragraphs[0]
	# add tab stops from YAML: center and right
	header_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(page['header_center_tab']), docx.enum.text.WD_TAB_ALIGNMENT.CENTER
	)
	header_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(page['header_right_tab']), docx.enum.text.WD_TAB_ALIGNMENT.RIGHT
	)
	# add page number fields
	add_page_number_field(header_para)
	# tab to center, add date
	run_tab1 = header_para.add_run("\t")
	run_tab1.font.size = docx.shared.Pt(header_size)
	if date_str:
		run_date = header_para.add_run(date_str)
		run_date.font.size = docx.shared.Pt(header_size)
	# tab to right, add name line
	run_tab2 = header_para.add_run("\t")
	run_tab2.font.size = docx.shared.Pt(header_size)
	run_name = header_para.add_run("First Name:_____________________________")
	run_name.font.size = docx.shared.Pt(header_size)

	# first page header is empty (just clear it)
	first_header = section.first_page_header
	# clear any default content
	for p in first_header.paragraphs:
		p.text = ""


#============================================
def add_rich_text_runs(para, text: str, font_size: float = None,
	base_bold: bool = False, base_italic: bool = False) -> None:
	"""Add styled runs to a paragraph, parsing inline HTML tags.

	Handles <sub>, <sup>, <b>, <strong>, <i>, <em> tags by creating
	separate runs with appropriate font properties. HTML entities are
	decoded first, then rich text tags are parsed.

	Args:
		para: The paragraph to add runs to.
		text: Text that may contain HTML entities and inline tags.
		font_size: Optional font size in points for all runs.
		base_bold: Whether the base text should be bold.
		base_italic: Whether the base text should be italic.
	"""
	# decode HTML entities first, then parse rich text tags
	decoded = ef_tools.text_utils.decode_html_entities(text)
	segments = ef_tools.text_utils.parse_rich_text(decoded)
	for segment_text, tags in segments:
		run = para.add_run(segment_text)
		if font_size is not None:
			run.font.size = docx.shared.Pt(font_size)
		# apply base formatting
		if base_bold or 'b' in tags:
			run.font.bold = True
		if base_italic or 'i' in tags:
			run.font.italic = True
		# apply sub/superscript
		if 'sub' in tags:
			run.font.subscript = True
		if 'sup' in tags:
			run.font.superscript = True


#============================================
def add_choices_paragraph(doc: docx.Document, choices: list,
	tab_style: int, items_per_row: int) -> None:
	"""Add a tab-separated choices paragraph with bold letter prefixes.

	Creates a paragraph with (A) (B) (C) format, using tab characters
	to align columns. The tab_style selects tab stop positions (3, 4, 5)
	and items_per_row controls how many choices per line.

	Args:
		doc: The Document to add the paragraph to.
		choices: List of choice text strings (no letter prefixes).
		tab_style: Tab stop layout (3, 4, or 5) from CHOICES_TAB_STOPS.
		items_per_row: Number of choices per line (may differ from tab_style).
	"""
	para = doc.add_paragraph()
	# select the appropriate style for this layout
	style_name = ef_tools.layout.CHOICES_STYLE_NAME[tab_style]
	para.style = doc.styles[style_name]
	# set tab stops for the chosen layout
	tab_positions = ef_tools.layout.CHOICES_TAB_STOPS[tab_style]
	for pos in tab_positions:
		para.paragraph_format.tab_stops.add_tab_stop(docx.shared.Inches(pos))
	# vertical stack: one choice per line, no tabs
	if items_per_row <= 1:
		for i, choice_text in enumerate(choices):
			if i > 0:
				run_br = para.add_run()
				run_br.add_break()
			letter = chr(ord('A') + i)
			bold_run = para.add_run(f"({letter}) ")
			bold_run.bold = True
			bold_run.font.size = docx.shared.Pt(10)
			# choice text with rich text support
			add_rich_text_runs(para, choice_text, font_size=10)
		return
	# multi-column layout
	for i, choice_text in enumerate(choices):
		letter = chr(ord('A') + i)
		# line break before new rows (after first row)
		if i > 0 and i % items_per_row == 0:
			run_br = para.add_run()
			run_br.add_break()
		# tab before this choice (except first in each row)
		if i > 0 and i % items_per_row != 0:
			para.add_run("\t")
		# bold letter prefix
		bold_run = para.add_run(f"({letter}) ")
		bold_run.bold = True
		bold_run.font.size = docx.shared.Pt(10)
		# choice text with rich text support
		add_rich_text_runs(para, choice_text, font_size=10)


#============================================
def add_table(doc: docx.Document, columns: list, rows: list,
	header_bg: str = 'F2F2F2') -> None:
	"""Add a table with a styled header row.

	The header row uses bold centered text with a light gray background.

	Args:
		doc: The Document to add the table to.
		columns: List of column header strings.
		rows: List of row data (each row is a list of cell strings).
		header_bg: Hex color for header background (no '#' prefix).
	"""
	num_rows = len(rows) + 1
	num_cols = len(columns)
	table = doc.add_table(rows=num_rows, cols=num_cols)
	table.style = 'Table Grid'
	# header row
	for ci, col_text in enumerate(columns):
		cell = table.rows[0].cells[ci]
		# use rich text for header cells (bold base)
		cell_para = cell.paragraphs[0]
		add_rich_text_runs(cell_para, col_text, base_bold=True)
		cell_para.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER
		# light gray background via XML shading
		shading = docx.oxml.OxmlElement('w:shd')
		shading.set(docx.oxml.ns.qn('w:fill'), header_bg)
		shading.set(docx.oxml.ns.qn('w:val'), 'clear')
		cell._element.get_or_add_tcPr().append(shading)
	# data rows
	for ri, row_data in enumerate(rows):
		for ci, cell_text in enumerate(row_data):
			cell_para = table.rows[ri + 1].cells[ci].paragraphs[0]
			add_rich_text_runs(cell_para, cell_text)


#============================================
def build_document(exam_data: dict, output_path: str) -> None:
	"""Build a complete DOCX exam document from YAML data.

	Creates all styles, page layout, headers, and body content.
	Refuses to overwrite an existing file.

	Args:
		exam_data: Dict from YAML input with exam structure.
		output_path: Path for the output DOCX file.
	"""
	# enforce .docx extension
	if not output_path.endswith('.docx'):
		raise ValueError(f"Output file must have .docx extension, got: {output_path}")
	# safety check: never overwrite existing files
	if os.path.exists(output_path):
		raise FileExistsError(f"Output file already exists: {output_path}")

	doc = docx.Document()

	# load style definitions from YAML
	styles = ef_tools.style_loader.load_styles()

	# setup styles from YAML definitions
	setup_styles(doc, styles)

	# page layout: margins from YAML
	page_margin = styles['page']['margin']
	section = doc.sections[0]
	section.top_margin = docx.shared.Inches(page_margin)
	section.bottom_margin = docx.shared.Inches(page_margin)
	section.left_margin = docx.shared.Inches(page_margin)
	section.right_margin = docx.shared.Inches(page_margin)

	# setup page header (empty on first page, name/date on body pages)
	date_str = exam_data.get('date', '')
	setup_header(section, date_str, styles)

	# --- first page boilerplate ---
	boilerplate_tab = styles['page']['boilerplate_tab']

	# exam title
	title = exam_data.get('title', 'Exam')
	title_para = doc.add_heading(ef_tools.text_utils.decode_html_entities(title), level=1)
	title_para.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER

	# name line shifted right with tab
	name_line = exam_data.get('student_line', ef_tools.exam_defaults.DEFAULT_NAME_LINE)
	name_para = doc.add_paragraph()
	name_para.add_run("\t" + name_line)
	name_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(boilerplate_tab), docx.enum.text.WD_TAB_ALIGNMENT.LEFT
	)

	# score line shifted right with tab
	sections = exam_data.get('sections', [])
	total_points = exam_data.get('total_points', None)
	if total_points is None:
		total_points = ef_tools.question_utils.count_total_questions(sections)
	num_sections = exam_data.get('scoring_sections', ef_tools.exam_defaults.DEFAULT_SCORING_SECTIONS)
	score_line = ef_tools.exam_defaults.format_score_line(total_points, num_sections)
	score_para = doc.add_paragraph()
	score_para.add_run("\t" + score_line)
	score_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(boilerplate_tab), docx.enum.text.WD_TAB_ALIGNMENT.LEFT
	)

	# --- sections and questions ---
	question_counter = 1
	prev_element = 'chapter'
	for section_data in sections:
		# major section heading (Heading 2 level)
		heading = section_data.get('heading', '')
		if heading:
			para = doc.add_paragraph()
			para.style = doc.styles['Exam Heading 2']
			add_rich_text_runs(para, heading, base_bold=True, base_italic=True)
			prev_element = 'chapter'
		# chapter heading (purple, level 3)
		chapter = section_data.get('chapter', '')
		if chapter:
			para = doc.add_paragraph()
			para.style = doc.styles['Chapter Heading']
			add_rich_text_runs(para, chapter, base_bold=True)
			prev_element = 'chapter'
		# questions
		questions = section_data.get('questions', [])
		for question in questions:
			# get explicit number if provided, otherwise use counter
			if 'number' in question:
				question_counter = question['number']
			question_number = question_counter
			# build question statement with number prefix
			statement = question.get('statement', '')
			if statement:
				# strip existing number prefix and add our own
				stripped = ef_tools.text_utils.strip_number_prefix(statement)
				# select style based on previous element
				style_name = ef_tools.question_utils.select_question_style(prev_element)
				para = doc.add_paragraph()
				para.style = doc.styles[style_name]
				# add number prefix as bold-italic run
				num_run = para.add_run(f"{question_number}. ")
				num_run.bold = True
				num_run.italic = True
				# add statement text with rich text support
				add_rich_text_runs(para, stripped, base_bold=True, base_italic=True)
				prev_element = 'question'
			# image (before choices, after question text)
			image_path = question.get('image', None)
			if image_path is not None and os.path.isfile(image_path):
				# add image with auto aspect ratio, max 5in wide
				doc.add_picture(image_path, width=docx.shared.Inches(5))
				prev_element = 'image'
			# table
			table_data = question.get('table', None)
			if table_data is not None:
				columns = table_data['columns']
				rows = table_data['rows']
				# pass table header background color from styles
				table_bg = styles['colors']['table_header_bg'].lstrip('#')
				add_table(doc, columns, rows, header_bg=table_bg)
				prev_element = 'table'
			# choices
			choices = question.get('choices', None)
			if choices is not None and len(choices) > 0:
				layout_override = question.get('layout', None)
				if layout_override is not None:
					# explicit override: tab_style = items_per_row = layout value
					tab_style = layout_override
					items_per_row = layout_override
				else:
					# auto-determine layout
					tab_style, items_per_row = ef_tools.layout.auto_layout_for_choices(choices)
				add_choices_paragraph(doc, choices, tab_style, items_per_row)
				prev_element = 'choices'
			# increment question counter
			question_counter += 1

	# save document
	doc.save(output_path)


#============================================
def main():
	"""Main entry point for DOCX exam builder."""
	args = parse_args()
	# load YAML
	with open(args.input_file, 'r') as f:
		exam_data = yaml.safe_load(f)
	# build document
	build_document(exam_data, args.output_file)
	print(f"Exam DOCX written to {args.output_file}")


#============================================
if __name__ == '__main__':
	main()
