"""DOCX rendering helpers for exam document building.

Provides style setup, rich text rendering, choice layout, table building,
and page header configuration. All formatting values come from the styles
dict (loaded from styles/exam_styles.yaml) rather than being hardcoded.
"""

# Standard Library
import datetime

# Pip Modules
import docx
import docx.shared
import docx.enum.text
import docx.enum.style
import docx.oxml.ns
import docx.oxml

# Local Repo Modules
import ef_tools.layout
import ef_tools.text_utils


#============================================
def set_font_with_fallback(style, primary: str, fallback: str) -> None:
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
	# remove theme font attributes that override explicit font names
	# (built-in styles like Heading 1 use asciiTheme/hAnsiTheme for Calibri)
	for theme_attr in ('w:asciiTheme', 'w:hAnsiTheme', 'w:csTheme', 'w:eastAsiaTheme'):
		qname = docx.oxml.ns.qn(theme_attr)
		if rfonts.get(qname) is not None:
			del rfonts.attrib[qname]
	rfonts.set(docx.oxml.ns.qn('w:ascii'), primary)
	rfonts.set(docx.oxml.ns.qn('w:hAnsi'), fallback)
	rfonts.set(docx.oxml.ns.qn('w:cs'), fallback)


#============================================
def parse_hex_color(hex_str: str) -> docx.shared.RGBColor:
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

	Reads font, size, color, spacing, and style_flags values from
	the styles dict (loaded from styles/exam_styles.yaml).

	Args:
		doc: The Document to add styles to.
		styles: Style definitions dict from YAML.
	"""
	fonts = styles['fonts']
	sizes = styles['sizes']
	colors = styles['colors']
	spacing = styles['spacing']
	flags = styles['style_flags']

	# modify the built-in Normal style as our base
	normal = doc.styles['Normal']
	normal.font.size = docx.shared.Pt(sizes['normal'])
	normal.paragraph_format.space_after = docx.shared.Pt(spacing['normal_space_after_pt'])
	normal.paragraph_format.space_before = docx.shared.Pt(0)
	normal.paragraph_format.line_spacing = spacing['normal_line_spacing']
	set_font_with_fallback(normal, fonts['primary'], fonts['fallback'])

	# customize built-in Heading 1
	h1 = doc.styles['Heading 1']
	h1.font.size = docx.shared.Pt(sizes['heading_1'])
	h1.font.bold = flags['heading_1_bold']
	h1.font.italic = flags['heading_1_italic']
	h1.font.color.rgb = parse_hex_color(colors['heading_1'])
	h1.paragraph_format.space_before = docx.shared.Inches(spacing['heading_space_before'])
	h1.paragraph_format.space_after = docx.shared.Inches(spacing['heading_space_after'])
	h1.paragraph_format.keep_with_next = True
	if flags['heading_1_centered']:
		h1.paragraph_format.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER
	set_font_with_fallback(h1, fonts['primary'], fonts['fallback'])

	# Question Heading: hanging indent, keep-with-next
	qh = doc.styles.add_style('Question Heading', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	qh.base_style = normal
	qh.font.bold = flags['question_bold']
	qh.font.italic = flags['question_italic']
	qh.font.size = docx.shared.Pt(sizes['question'])
	qh.paragraph_format.left_indent = docx.shared.Inches(spacing['question_indent'])
	qh.paragraph_format.first_line_indent = docx.shared.Inches(spacing['question_hanging'])
	qh.paragraph_format.space_before = docx.shared.Inches(spacing['question_heading_space_before'])
	qh.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qh.paragraph_format.keep_with_next = True

	# Question Follow: same as Question Heading but no space above
	qf = doc.styles.add_style('Question Follow', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	qf.base_style = normal
	qf.font.bold = flags['question_bold']
	qf.font.italic = flags['question_italic']
	qf.font.size = docx.shared.Pt(sizes['question'])
	qf.paragraph_format.left_indent = docx.shared.Inches(spacing['question_indent'])
	qf.paragraph_format.first_line_indent = docx.shared.Inches(spacing['question_hanging'])
	qf.paragraph_format.space_before = docx.shared.Pt(0)
	qf.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qf.paragraph_format.keep_with_next = True

	# Chapter Heading: colored, keep-with-next
	ch = doc.styles.add_style('Chapter Heading', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	ch.base_style = normal
	ch.font.size = docx.shared.Pt(sizes['chapter_heading'])
	set_font_with_fallback(ch, fonts['primary'], fonts['fallback'])
	ch.font.bold = flags['chapter_heading_bold']
	ch.font.color.rgb = parse_hex_color(colors['chapter_heading'])
	ch.paragraph_format.space_before = docx.shared.Pt(spacing['chapter_space_before_pt'])
	ch.paragraph_format.space_after = docx.shared.Pt(spacing['chapter_space_after_pt'])
	ch.paragraph_format.keep_with_next = True

	# Heading 2: for major section labels
	h2 = doc.styles.add_style('Exam Heading 2', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	h2.base_style = normal
	h2.font.size = docx.shared.Pt(sizes['heading_2'])
	set_font_with_fallback(h2, fonts['primary'], fonts['fallback'])
	h2.font.bold = flags['heading_2_bold']
	h2.font.italic = flags['heading_2_italic']
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

	# Header: small font for page headers with center and right tab stops
	# modify the built-in Header style (not add_style)
	hdr = doc.styles['Header']
	hdr.font.size = docx.shared.Pt(sizes['header'])
	# use header-specific fonts if defined, otherwise fall back to primary
	header_primary = fonts.get('header_primary', fonts['primary'])
	header_fallback = fonts.get('header_fallback', fonts['fallback'])
	set_font_with_fallback(hdr, header_primary, header_fallback)
	# small gap below header before content
	hdr.paragraph_format.space_after = docx.shared.Pt(spacing['header_space_after_pt'])
	# clear any pre-existing tab stops from the built-in Header style
	hdr.paragraph_format.tab_stops.clear_all()
	# left-aligned page number, center date, right-aligned name
	hdr.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(styles['page']['header_center_tab']),
		docx.enum.text.WD_TAB_ALIGNMENT.CENTER
	)
	hdr.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(styles['page']['header_right_tab']),
		docx.enum.text.WD_TAB_ALIGNMENT.RIGHT
	)

	# Choices 2 through 5: inherit from Choice, with tab stops on the style
	# load tab stops from YAML if available, else use layout module defaults
	tab_stops_config = styles.get('layout_tab_stops', ef_tools.layout.CHOICES_TAB_STOPS)
	for n in range(2, 6):
		style = doc.styles.add_style(f'Choices {n}', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
		style.base_style = choice_base
		# add tab stops so switching styles in Word preserves column alignment
		stops = tab_stops_config.get(n, tab_stops_config.get(str(n), []))
		for pos in stops:
			style.paragraph_format.tab_stops.add_tab_stop(docx.shared.Inches(pos))


#============================================
def add_page_number_field(paragraph) -> None:
	"""Add 'Page X of Y' field codes to a paragraph using raw XML.

	python-docx does not have native page number field support,
	so we insert the Word XML field elements directly.

	Args:
		paragraph: The paragraph to add page numbers to.
	"""
	# "Page " text (font size inherited from paragraph style)
	paragraph.add_run("Page ")
	# PAGE field
	run1 = paragraph.add_run()
	fld_simple_page = docx.oxml.OxmlElement('w:fldSimple')
	fld_simple_page.set(docx.oxml.ns.qn('w:instr'), ' PAGE ')
	run1._element.addnext(fld_simple_page)
	# " of " text
	paragraph.add_run(" of ")
	# NUMPAGES field
	run2 = paragraph.add_run()
	fld_simple_total = docx.oxml.OxmlElement('w:fldSimple')
	fld_simple_total.set(docx.oxml.ns.qn('w:instr'), ' NUMPAGES ')
	run2._element.addnext(fld_simple_total)


#============================================
def format_date_human(date_str: str) -> str:
	"""Convert an ISO date string to human-readable format.

	Converts '2026-04-02' to 'April 2, 2026'. If parsing fails,
	returns the original string unchanged.

	Args:
		date_str: Date string in ISO format (YYYY-MM-DD).

	Returns:
		Human-readable date string like 'April 2, 2026'.
	"""
	# parse ISO date and format with full month name, no zero-padded day
	dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
	# %-d gives non-padded day on Unix/macOS
	formatted = dt.strftime('%B %-d, %Y')
	return formatted

assert format_date_human('2026-04-02') == 'April 2, 2026'
assert format_date_human('2025-12-25') == 'December 25, 2025'
assert format_date_human('2026-01-01') == 'January 1, 2026'


#============================================
def setup_header(doc: docx.Document, section, date_str: str, styles: dict) -> None:
	"""Configure page header on body pages with page number, date, and name.

	Sets up different first page header (empty) and body page header with
	'Page X of Y | date | First Name:___' layout. Font size and tab stops
	come from the Header style.

	Args:
		doc: The Document (needed to access Header style).
		section: The document section to configure.
		date_str: Date string to display in header center.
		styles: Style definitions dict from YAML.
	"""
	# enable different first page header (empty on page 1)
	section.different_first_page_header_footer = True
	# fix header distance so top margin is consistent on all pages
	header_distance = styles['page']['header_distance']
	section.header_distance = docx.shared.Inches(header_distance)

	# body page header: "Page X of Y [tab] date [tab] First Name:___"
	header = section.header
	header.is_linked_to_previous = False
	header_para = header.paragraphs[0]
	# apply Header style (font size and tab stops defined on style)
	header_para.style = doc.styles['Header']
	# add page number fields (left-aligned by default)
	add_page_number_field(header_para)
	# tab to center, add human-readable date
	header_para.add_run("\t")
	if date_str:
		# convert ISO date (2026-04-02) to human-readable (April 2, 2026)
		formatted_date = format_date_human(date_str)
		header_para.add_run(formatted_date)
	# tab to right, add name line
	header_para.add_run("\t")
	header_para.add_run("First Name:_____________________________")

	# first page header is empty (just clear it)
	first_header = section.first_page_header
	# clear any default content
	for p in first_header.paragraphs:
		p.text = ""


#============================================
def add_rich_text_runs(para, text: str) -> None:
	"""Add styled runs to a paragraph, parsing inline HTML tags.

	Handles <sub>, <sup>, <b>, <strong>, <i>, <em> tags by creating
	separate runs with appropriate font properties. HTML entities are
	decoded first, then rich text tags are parsed.

	Font size, base bold, and base italic come from the paragraph style.
	Only rich text tags add run-level overrides.

	Args:
		para: The paragraph to add runs to.
		text: Text that may contain HTML entities and inline tags.
	"""
	# decode HTML entities first, then parse rich text tags
	decoded = ef_tools.text_utils.decode_html_entities(text)
	segments = ef_tools.text_utils.parse_rich_text(decoded)
	for segment_text, tags in segments:
		if segment_text == "\n":
			run = para.add_run()
			run.add_break()
			continue
		text_parts = segment_text.split("\n")
		for index, text_part in enumerate(text_parts):
			if index > 0:
				break_run = para.add_run()
				break_run.add_break()
			if not text_part:
				continue
			run = para.add_run(text_part)
			# only set run-level overrides for rich text tags
			if 'b' in tags:
				run.font.bold = True
			if 'i' in tags:
				run.font.italic = True
			if 'sub' in tags:
				run.font.subscript = True
			if 'sup' in tags:
				run.font.superscript = True


#============================================
def add_choice_content(para, choice, image_width: float = None) -> None:
	"""Add text and optional image content for one choice."""
	choice_text = ef_tools.layout.choice_text(choice)
	if choice_text:
		add_rich_text_runs(para, choice_text)
	image_path = ef_tools.layout.choice_image(choice)
	if image_path:
		if choice_text:
			para.add_run().add_break()
		run = para.add_run()
		if image_width is None:
			run.add_picture(image_path)
		else:
			run.add_picture(image_path, width=docx.shared.Inches(image_width))


#============================================
def add_image_choices_tabbed(doc: docx.Document, choices: list,
	image_width: float, page_width: float) -> None:
	"""Add image-based choices in a horizontal layout using tab stops.

	Builds a single paragraph with explicit tab stops at evenly spaced
	column positions. The first line holds bold letter prefixes and any
	caption text, the second line holds inline images. No docx tables
	are created.

	Args:
		doc: The Document to add the paragraph to.
		choices: List of structured choice dicts with text and/or image keys.
		image_width: Maximum image width in inches.
		page_width: Usable page width in inches (page width minus margins).
	"""
	para = doc.add_paragraph()
	para.style = doc.styles['Choice']
	# evenly spaced tab stops, one per column boundary
	num_cols = len(choices)
	col_width = page_width / num_cols
	for col_index in range(1, num_cols):
		para.paragraph_format.tab_stops.add_tab_stop(
			docx.shared.Inches(col_width * col_index),
			docx.enum.text.WD_TAB_ALIGNMENT.LEFT,
		)
	# letter row: (A) caption_a <tab> (B) caption_b <tab> ...
	for index, choice in enumerate(choices):
		if index > 0:
			para.add_run("\t")
		letter = chr(ord('A') + index)
		prefix = para.add_run(f"({letter}) ")
		prefix.bold = True
		choice_text = ef_tools.layout.choice_text(choice)
		if choice_text:
			add_rich_text_runs(para, choice_text)
	# line break, then image row aligned to the same tab stops
	para.add_run().add_break()
	for index, choice in enumerate(choices):
		if index > 0:
			para.add_run("\t")
		image_path = ef_tools.layout.choice_image(choice)
		if image_path:
			image_run = para.add_run()
			image_run.add_picture(image_path, width=docx.shared.Inches(image_width))


#============================================
def add_choices_paragraph(doc: docx.Document, choices: list,
	tab_style: int, items_per_row: int, image_width: float = None) -> None:
	"""Add a tab-separated choices paragraph with bold letter prefixes.

	Creates a paragraph with (A) (B) (C) format, using tab characters
	to align columns. The tab_style selects tab stop positions (3, 4, 5)
	and items_per_row controls how many choices per line.

	Args:
		doc: The Document to add the paragraph to.
		choices: List of choice text strings or dicts with text/image keys.
		tab_style: Tab stop layout (3, 4, or 5) from CHOICES_TAB_STOPS.
		items_per_row: Number of choices per line (may differ from tab_style).
	"""
	para = doc.add_paragraph()
	# select the appropriate style (tab stops are defined on the style)
	style_name = ef_tools.layout.CHOICES_STYLE_NAME[tab_style]
	para.style = doc.styles[style_name]
	has_images = any(ef_tools.layout.choice_image(choice) for choice in choices)
	if has_images:
		items_per_row = 1
		tab_style = 1
		para.style = doc.styles['Choice']
	# vertical stack: one choice per line, no tabs
	if items_per_row <= 1:
		for i, choice in enumerate(choices):
			if i > 0:
				run_br = para.add_run()
				run_br.add_break()
			letter = chr(ord('A') + i)
			# bold letter prefix (only run-level override needed)
			bold_run = para.add_run(f"({letter}) ")
			bold_run.bold = True
			# choice content inherits font size from style
			add_choice_content(para, choice, image_width=image_width)
		return
	# multi-column layout
	for i, choice in enumerate(choices):
		letter = chr(ord('A') + i)
		# line break before new rows (after first row)
		if i > 0 and i % items_per_row == 0:
			run_br = para.add_run()
			run_br.add_break()
		# tab before this choice (except first in each row)
		if i > 0 and i % items_per_row != 0:
			para.add_run("\t")
		# bold letter prefix (only run-level override needed)
		bold_run = para.add_run(f"({letter}) ")
		bold_run.bold = True
		# choice content inherits font size from style
		add_choice_content(para, choice, image_width=image_width)


#============================================
def add_table(doc: docx.Document, columns: list, rows: list,
	header_bg: str = 'F2F2F2', center_header: bool = True) -> None:
	"""Add a table with a styled header row.

	The header row uses bold text with a background color.

	Args:
		doc: The Document to add the table to.
		columns: List of column header strings.
		rows: List of row data (each row is a list of cell strings).
		header_bg: Hex color for header background (no '#' prefix).
		center_header: Whether to center-align header cells.
	"""
	num_rows = len(rows) + 1
	num_cols = len(columns)
	table = doc.add_table(rows=num_rows, cols=num_cols)
	table.style = 'Table Grid'
	# header row
	for ci, col_text in enumerate(columns):
		cell = table.rows[0].cells[ci]
		cell_para = cell.paragraphs[0]
		# add header text with rich text support (decodes HTML entities)
		add_rich_text_runs(cell_para, col_text)
		# set bold on all runs in the header cell
		for run in cell_para.runs:
			run.font.bold = True
		if center_header:
			cell_para.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER
		# background color via XML shading
		shading = docx.oxml.OxmlElement('w:shd')
		shading.set(docx.oxml.ns.qn('w:fill'), header_bg)
		shading.set(docx.oxml.ns.qn('w:val'), 'clear')
		cell._element.get_or_add_tcPr().append(shading)
	# data rows
	for ri, row_data in enumerate(rows):
		for ci, cell_text in enumerate(row_data):
			cell_para = table.rows[ri + 1].cells[ci].paragraphs[0]
			add_rich_text_runs(cell_para, cell_text)
