"""Build shared DOCX styles, rich text, tables, and page headers.

Formatting values come from the styles dict loaded from
styles/exam_styles.yaml rather than being hardcoded.
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
def set_font_with_fallback(style: object, primary: str, fallback: str) -> None:
	"""Set font name on a style with a fallback font via XML.

	python-docx only supports a single font name. This sets the primary
	font and adds the fallback as hAnsi/cs font for cross-platform
	compatibility.

	Args:
		style: A python-docx paragraph or character style.
		primary: Primary font name (e.g., 'Atkinson Hyperlegible Next').
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
def set_run_font_from_style(run: object, source_style: object) -> None:
	"""Copy a style's font family settings onto a run directly."""
	source_rpr = source_style.element.get_or_add_rPr()
	source_rfonts = source_rpr.find(docx.oxml.ns.qn('w:rFonts'))
	if source_rfonts is None:
		return
	run_rpr = run._element.get_or_add_rPr()
	run_rfonts = run_rpr.find(docx.oxml.ns.qn('w:rFonts'))
	if run_rfonts is None:
		run_rfonts = docx.oxml.OxmlElement('w:rFonts')
		run_rpr.insert(0, run_rfonts)
	# Inline code here is Latin text; leave non-Latin font slots inherited.
	for attribute in ('ascii', 'hAnsi'):
		qname = docx.oxml.ns.qn(f'w:{attribute}')
		value = source_rfonts.get(qname)
		if value is not None:
			run_rfonts.set(qname, value)


#============================================
def set_character_style_border(style: object, width_pt: float,
		padding_pt: float) -> None:
	"""Set a rectangular border around text using a character style."""
	rpr = style.element.get_or_add_rPr()
	border = docx.oxml.OxmlElement('w:bdr')
	border.set(docx.oxml.ns.qn('w:val'), 'single')
	border.set(docx.oxml.ns.qn('w:sz'), str(int(round(width_pt * 8))))
	border.set(docx.oxml.ns.qn('w:space'), str(int(round(padding_pt))))
	border.set(docx.oxml.ns.qn('w:color'), '000000')
	rpr.append(border)


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

	Reads font, size, color, spacing, border, and style_flags values from
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
	borders = styles['borders']

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
	if flags['question_italic']:
		qh.font.italic = True
	qh.font.size = docx.shared.Pt(sizes['question'])
	qh.paragraph_format.left_indent = docx.shared.Inches(spacing['question_indent'])
	qh.paragraph_format.first_line_indent = docx.shared.Inches(spacing['question_hanging'])
	qh.paragraph_format.space_before = docx.shared.Inches(spacing['question_heading_space_before'])
	qh.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qh.paragraph_format.keep_with_next = True

	# Question Follow inherits Question Heading and removes the leading
	# space, keeping all question text visually consistent.
	qf = doc.styles.add_style('Question Follow', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	qf.base_style = qh
	qf.paragraph_format.space_before = docx.shared.Pt(0)
	qf.paragraph_format.space_after = docx.shared.Inches(spacing['question_space_after'])
	qf.paragraph_format.keep_with_next = True

	# A temporary style carries the configured monospace font; rich-text runs
	# copy its settings directly, then the style is removed before saving.
	code_style = doc.styles.add_style(
		'Exam Code', docx.enum.style.WD_STYLE_TYPE.CHARACTER)
	set_font_with_fallback(
		code_style, fonts['docx_monospace_face'],
		fonts['docx_monospace_face'])

	# The question label stays a text run while the character style supplies
	# its outline independently of the question paragraph's regular weight.
	question_number_style = doc.styles.add_style(
		'Question Number', docx.enum.style.WD_STYLE_TYPE.CHARACTER)
	set_font_with_fallback(
		question_number_style, fonts['primary'], fonts['fallback'])
	question_number_style.font.bold = False
	question_number_style.font.italic = False
	set_character_style_border(
		question_number_style,
		borders['question_label_width_pt'],
		borders['question_label_padding_pt'],
	)

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
	choice_base.paragraph_format.space_before = docx.shared.Pt(
		spacing['choice_space_before_pt'])
	choice_base.paragraph_format.space_after = docx.shared.Pt(spacing['normal_space_after_pt'])
	choice_base.paragraph_format.keep_with_next = False

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

	# Matching Prompt: numbered fill-in lines for matching questions.
	# Mirrors the legacy ARTIFACTS/2019_exam2-final.docx "Question" style
	# (verified via LibreOffice style dialog). Two tab stops let prompts
	# render in a two-column layout: "___ 1. text<tab>___ 2. text".
	matching_prompt = doc.styles.add_style(
		'Matching Prompt', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
	matching_prompt.base_style = qh
	matching_prompt.font.bold = False
	matching_prompt.paragraph_format.left_indent = docx.shared.Inches(spacing['matching_prompt_indent'])
	matching_prompt.paragraph_format.first_line_indent = docx.shared.Inches(spacing['matching_prompt_hanging'])
	matching_prompt.paragraph_format.space_before = docx.shared.Inches(spacing['matching_prompt_space_before'])
	matching_prompt.paragraph_format.space_after = docx.shared.Pt(0)
	matching_prompt.paragraph_format.line_spacing = spacing['matching_prompt_line_spacing']
	matching_prompt.paragraph_format.keep_with_next = False
	for pos in styles['matching_prompt_tab_stops']:
		matching_prompt.paragraph_format.tab_stops.add_tab_stop(docx.shared.Inches(pos))

	# Choices 2 through 5: inherit from Choice, with tab stops on the style
	# load tab stops from YAML if available, else use layout module defaults
	tab_stops_config = styles.get('layout_tab_stops', ef_tools.layout.CHOICES_TAB_STOPS)
	for n in range(2, 6):
		style = doc.styles.add_style(f'Choices {n}', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
		style.base_style = choice_base
		style.paragraph_format.keep_with_next = False
		# add tab stops so switching styles in Word preserves column alignment
		stops = tab_stops_config.get(n, tab_stops_config.get(str(n), []))
		for pos in stops:
			style.paragraph_format.tab_stops.add_tab_stop(docx.shared.Inches(pos))


#============================================
def add_page_number_field(paragraph: object) -> None:
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
def setup_header(doc: docx.Document, section: object, date_str: str, styles: dict) -> None:
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
def add_rich_text_runs(para: object, text: str,
		font_family: str = None) -> None:
	"""Add styled runs to a paragraph, parsing inline HTML tags.

	Handles <sub>, <sup>, <b>, <strong>, <i>, <em>, <code>, and <tt>
	tags by creating separate runs with appropriate font properties.
	HTML entities are decoded first, then rich text tags are parsed.

	Font size, bold, and italic come from the paragraph style and markup. A
	code tag sets the configured monospace face; upright code resets the slant
	only when the paragraph itself is not italic, avoiding LibreOffice carrying
	an earlier italic code face into later upright runs.

	Args:
		para: The paragraph to add runs to.
		text: Text that may contain HTML entities and inline tags.
		font_family: Optional face override for non-code runs.
	"""
	# decode HTML entities first, then parse rich text tags
	decoded = ef_tools.text_utils.decode_html_entities(text)
	segments = ef_tools.text_utils.parse_rich_text(decoded)
	for segment_text, tags in segments:
		# drop hard-break segments and collapse stray newlines to spaces;
		# paragraph-level splitting belongs to add_rich_text_paragraphs
		if segment_text == "\n":
			continue
		flat_text = segment_text.replace("\n", " ")
		if not flat_text:
			continue
		run = para.add_run(flat_text)
		if font_family and 'code' not in tags:
			run.font.name = font_family
		if 'code' in tags:
			code_style = para.part.styles['Exam Code']
			set_run_font_from_style(run, code_style)
			if 'i' not in tags:
				style = para.style
				inherited_italic = False
				while style is not None:
					if style.font.italic is not None:
						inherited_italic = style.font.italic
						break
					style = style.base_style
				if not inherited_italic:
					run.font.italic = False
		# only set run-level overrides for rich text tags
		if 'b' in tags:
			run.font.bold = True
		if 'i' in tags:
			run.font.italic = True
		if 'sub' in tags:
			run.font.subscript = True
		if 'sup' in tags:
			run.font.superscript = True
		for tag in tags:
			if tag.startswith('color:'):
				run.font.color.rgb = parse_hex_color(tag.split(':', 1)[1])


#============================================
def remove_temporary_code_style(doc: docx.Document) -> None:
	"""Remove the temporary font settings donor before writing the DOCX."""
	code_style = doc.styles['Exam Code']
	doc.styles.element.remove(code_style.element)


#============================================
def add_rich_text_paragraphs(doc: object, style_name: str, text: str,
		prefix: str = '', boxed_prefix: bool = False) -> object:
	"""Split text on hard breaks (\\n and <br>) into separate paragraphs.

	Each piece becomes its own paragraph styled with style_name. The
	optional prefix is added to the first paragraph only. When boxed_prefix
	is true, the trimmed prefix uses the Question Number character style and
	any trailing separator remains outside the border.
	An empty input still emits one paragraph (carrying just the prefix)
	so callers can rely on at least one paragraph being created.

	Returns the last paragraph created.
	"""
	pieces = ef_tools.text_utils.split_on_hard_breaks(text)
	# keep only pieces with visible content; preserve at least one slot
	pieces = [piece for piece in pieces if piece.strip()]
	if not pieces:
		pieces = ['']
	last_para = None
	for index, piece in enumerate(pieces):
		current_style_name = style_name
		if index > 0 and style_name == 'Question Heading':
			current_style_name = 'Question Follow'
		para = doc.add_paragraph()
		para.style = doc.styles[current_style_name]
		if index == 0 and prefix:
			if boxed_prefix:
				label_text = prefix.rstrip()
				separator = prefix[len(label_text):]
				label_run = para.add_run(label_text)
				label_run.style = 'Question Number'
				if separator:
					para.add_run(separator)
			else:
				para.add_run(prefix)
		add_rich_text_runs(para, piece)
		last_para = para
	return last_para


#============================================
def _add_boilerplate_run(para: object, text: str, font_size_pt: float) -> None:
	"""Add one first-page boilerplate run at body size.

	The title paragraph carries the Heading 1 style, so a run added to it
	inherits 18pt bold. The name and score lines sit on those same lines but
	are body text, so each run overrides size and weight explicitly.
	"""
	run = para.add_run(text)
	run.font.size = docx.shared.Pt(font_size_pt)
	run.bold = False
	run.italic = False


#============================================
def add_first_page_heading(doc: docx.Document, title: str, name_line: str,
		score_line: str, styles: dict) -> None:
	"""Write the first-page title and the name/score block beside it.

	The title sits flush left and the boilerplate block starts at a single tab
	stop partway across the page, so the two share a line instead of stacking
	three centered lines with an empty left column and an empty right half.

	Args:
		doc: The Document to write into.
		title: Exam title text, may carry inline markup.
		name_line: The student name rule.
		score_line: The per-section score rule.
		styles: Loaded style definitions.
	"""
	block_tab = styles['page']['heading_block_tab']
	body_size = styles['sizes']['normal']
	# Heading 1 rather than add_heading so the custom font overrides Word's
	# built-in theme font.
	title_para = doc.add_paragraph()
	title_para.style = doc.styles['Heading 1']
	add_rich_text_runs(title_para, title)
	title_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(block_tab), docx.enum.text.WD_TAB_ALIGNMENT.LEFT)
	_add_boilerplate_run(title_para, "\t" + name_line, body_size)
	# The score line continues the same block, so it hugs the line above it.
	score_para = doc.add_paragraph()
	score_para.paragraph_format.tab_stops.add_tab_stop(
		docx.shared.Inches(block_tab), docx.enum.text.WD_TAB_ALIGNMENT.LEFT)
	score_para.paragraph_format.space_before = docx.shared.Pt(0)
	_add_boilerplate_run(score_para, "\t" + score_line, body_size)


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
