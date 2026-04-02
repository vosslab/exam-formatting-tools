"""Shared utility module for reading and writing ODT files using lxml and zipfile."""

# Standard Library
import re
import copy
import zipfile

# Pip Modules
import lxml.etree

# ODF namespace URI registry
# Maps short prefixes to full namespace URIs for use in XPath and element creation
ODF_NAMESPACES = {
	'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
	'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
	'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
	'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
	'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
	'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
	'svg': 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
	'xlink': 'http://www.w3.org/1999/xlink',
	'number': 'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0',
	'meta': 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
	'dc': 'http://purl.org/dc/elements/1.1/',
	'manifest': 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0',
	'loext': 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0',
}


#============================================
def qname(prefix: str, local: str) -> str:
	"""Return Clark notation {namespace_uri}local for lxml element/attribute access.

	Args:
		prefix: Short namespace prefix (e.g., 'style', 'fo', 'text').
		local: Local element or attribute name (e.g., 'style', 'font-size').

	Returns:
		Clark notation string like '{urn:oasis:...}font-size'.
	"""
	uri = ODF_NAMESPACES[prefix]
	clark = f"{{{uri}}}{local}"
	return clark


#============================================
def encode_style_name(name: str) -> str:
	"""Encode a human-readable style name to ODF internal format.

	LibreOffice encodes spaces and certain special characters in style names
	using _XX_ hex notation (e.g., space becomes _20_, underscore becomes _5f_).

	Args:
		name: Human-readable style name (e.g., 'Question Heading').

	Returns:
		ODF-encoded style name (e.g., 'Question_20_Heading').
	"""
	# encode space as _20_ (most common case)
	encoded = name.replace(' ', '_20_')
	return encoded


#============================================
def decode_style_name(name: str) -> str:
	"""Decode an ODF-encoded style name to human-readable format.

	Converts _XX_ hex patterns back to their character equivalents
	(e.g., _20_ becomes space, _5f_ becomes underscore).

	Args:
		name: ODF-encoded style name (e.g., 'Question_20_Heading').

	Returns:
		Human-readable style name (e.g., 'Question Heading').
	"""
	# replace _XX_ hex patterns with their character equivalents
	def hex_replace(match: re.Match) -> str:
		hex_val = match.group(1)
		char = chr(int(hex_val, 16))
		return char
	decoded = re.sub(r'_([0-9a-fA-F]{2})_', hex_replace, name)
	return decoded


#============================================
def read_odt(odt_path: str) -> dict:
	"""Open an ODT ZIP archive and parse its XML contents.

	Extracts styles.xml and content.xml as lxml element trees.
	All other entries are stored as raw bytes for round-trip preservation.

	Args:
		odt_path: Path to the ODT file.

	Returns:
		Dict with keys: styles_xml, content_xml, zip_path, other_entries, other_data.
	"""
	styles_xml = None
	content_xml = None
	other_entries = []
	other_data = {}
	# open the ODT as a ZIP archive
	zf = zipfile.ZipFile(odt_path, 'r')
	for info in zf.infolist():
		raw = zf.read(info.filename)
		if info.filename == 'styles.xml':
			styles_xml = lxml.etree.fromstring(raw)
		elif info.filename == 'content.xml':
			content_xml = lxml.etree.fromstring(raw)
		else:
			other_entries.append(info)
			other_data[info.filename] = raw
	zf.close()
	odt_data = {
		'styles_xml': styles_xml,
		'content_xml': content_xml,
		'zip_path': odt_path,
		'other_entries': other_entries,
		'other_data': other_data,
	}
	return odt_data


#============================================
def style_name(element: lxml.etree._Element) -> str:
	"""Return the style:name attribute value of an ODF style element.

	Args:
		element: An lxml Element with a style:name attribute.

	Returns:
		The style name string.
	"""
	name_attr = qname('style', 'name')
	name = element.get(name_attr)
	return name


#============================================
def style_family(element: lxml.etree._Element) -> str:
	"""Return the style:family attribute value of an ODF style element.

	Args:
		element: An lxml Element with a style:family attribute.

	Returns:
		The style family string (e.g., 'paragraph', 'text', 'table').
	"""
	family_attr = qname('style', 'family')
	family = element.get(family_attr)
	return family


#============================================
def get_named_styles(styles_root: lxml.etree._Element) -> list:
	"""Get all named style elements from the office:styles section.

	Args:
		styles_root: Root element of styles.xml.

	Returns:
		List of style:style elements from office:styles.
	"""
	xpath = f".//{qname('office', 'styles')}/{qname('style', 'style')}"
	styles = styles_root.findall(xpath)
	return styles


#============================================
def get_automatic_styles(content_root: lxml.etree._Element) -> list:
	"""Get all automatic style elements from content.xml.

	Args:
		content_root: Root element of content.xml.

	Returns:
		List of style:style elements from office:automatic-styles.
	"""
	xpath = f".//{qname('office', 'automatic-styles')}/{qname('style', 'style')}"
	styles = content_root.findall(xpath)
	return styles


#============================================
def get_page_layouts(styles_root: lxml.etree._Element) -> list:
	"""Get all page layout elements from styles.xml.

	Page layouts define page dimensions, margins, and orientation.

	Args:
		styles_root: Root element of styles.xml.

	Returns:
		List of style:page-layout elements.
	"""
	xpath = f".//{qname('style', 'page-layout')}"
	layouts = styles_root.findall(xpath)
	return layouts


#============================================
def get_master_pages(styles_root: lxml.etree._Element) -> list:
	"""Get all master page elements from styles.xml.

	Master pages link page layouts to named page styles used in the document body.

	Args:
		styles_root: Root element of styles.xml.

	Returns:
		List of style:master-page elements.
	"""
	xpath = f".//{qname('office', 'master-styles')}/{qname('style', 'master-page')}"
	pages = styles_root.findall(xpath)
	return pages


#============================================
def get_style_by_name(styles_root: lxml.etree._Element, name: str, family: str) -> lxml.etree._Element:
	"""Find a specific named style by name and family.

	Tries both the given name and its encoded/decoded form so callers
	can pass either human-readable or ODF-encoded names.

	Args:
		styles_root: Root element of styles.xml.
		name: The style:name value to match (human-readable or ODF-encoded).
		family: The style:family value to match (e.g., 'paragraph').

	Returns:
		The matching style:style element, or None if not found.
	"""
	# build set of candidate names to match
	candidates = {name, encode_style_name(name), decode_style_name(name)}
	named_styles = get_named_styles(styles_root)
	for elem in named_styles:
		elem_name = style_name(elem)
		elem_family = style_family(elem)
		if elem_name in candidates and elem_family == family:
			return elem
	return None


#============================================
def write_odt(odt_data: dict, output_path: str) -> None:
	"""Write an ODT data dict back to a valid ODT ZIP archive.

	The mimetype entry is written first and uncompressed (ZIP_STORED)
	as required by the ODF specification.

	Args:
		odt_data: Dict from read_odt() with styles_xml, content_xml, other_entries, other_data.
		output_path: Path for the output ODT file.
	"""
	zf = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
	# mimetype must be first entry and stored uncompressed per ODF spec
	if 'mimetype' in odt_data['other_data']:
		zf.writestr('mimetype', odt_data['other_data']['mimetype'], compress_type=zipfile.ZIP_STORED)
	# serialize the XML trees back to bytes
	styles_bytes = lxml.etree.tostring(
		odt_data['styles_xml'], xml_declaration=True, encoding='UTF-8'
	)
	content_bytes = lxml.etree.tostring(
		odt_data['content_xml'], xml_declaration=True, encoding='UTF-8'
	)
	# write styles.xml and content.xml
	zf.writestr('styles.xml', styles_bytes)
	zf.writestr('content.xml', content_bytes)
	# write all other entries (skip mimetype since already written)
	for info in odt_data['other_entries']:
		if info.filename == 'mimetype':
			continue
		raw = odt_data['other_data'][info.filename]
		zf.writestr(info, raw)
	zf.close()


#============================================
def styles_equal(elem_a: lxml.etree._Element, elem_b: lxml.etree._Element) -> bool:
	"""Compare two style elements for equality using canonical serialization.

	Uses C14N2 canonical form to normalize attribute ordering and namespaces.

	Args:
		elem_a: First style element.
		elem_b: Second style element.

	Returns:
		True if the elements are semantically equal.
	"""
	# deep copy to avoid modifying originals during serialization
	a_copy = copy.deepcopy(elem_a)
	b_copy = copy.deepcopy(elem_b)
	bytes_a = lxml.etree.tostring(a_copy, method='c14n2')
	bytes_b = lxml.etree.tostring(b_copy, method='c14n2')
	equal = (bytes_a == bytes_b)
	return equal
