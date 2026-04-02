#!/usr/bin/env python3
"""Extract named styles from ODT files to YAML or template ODT.

Reads one or more ODT files and extracts named styles to YAML
(human-readable catalog) or a content-free template ODT (styles only).
Also supports comparison mode to diff styles between two ODT files.
"""

# Standard Library
import copy
import argparse

# Pip Modules
import yaml
import lxml.etree

# Local Repo Modules
import odt_utils


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns:
		Parsed argument namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Extract named styles from ODT files to YAML or template ODT"
	)
	# input/output
	parser.add_argument(
		'-i', '--input', dest='input_file', required=True,
		help="Input ODT file path"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file', required=True,
		help="Output file path (YAML or ODT)"
	)
	# mode flags
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument(
		'-t', '--template', dest='template_mode', action='store_true',
		help="Output as content-free template ODT instead of YAML"
	)
	mode_group.add_argument(
		'-c', '--compare', dest='compare_file', type=str, default=None,
		help="Second ODT file to compare styles against"
	)
	# filter
	parser.add_argument(
		'-f', '--family', dest='style_family', type=str, default=None,
		help="Filter by style family (paragraph, text, table, table-cell, page-layout)"
	)
	args = parser.parse_args()
	return args


#============================================
def element_attribs_to_dict(element: lxml.etree._Element) -> dict:
	"""Convert an element's attributes to a dict with prefixed names.

	Replaces full namespace URIs with short prefixes for readability.

	Args:
		element: An lxml Element.

	Returns:
		Dict mapping prefixed attribute names to values.
	"""
	# build reverse namespace lookup
	reverse_ns = {}
	for prefix, uri in odt_utils.ODF_NAMESPACES.items():
		reverse_ns[uri] = prefix
	result = {}
	for attr_clark, value in element.attrib.items():
		# parse Clark notation {uri}local
		if attr_clark.startswith('{'):
			close_brace = attr_clark.index('}')
			uri = attr_clark[1:close_brace]
			local = attr_clark[close_brace + 1:]
			prefix = reverse_ns.get(uri, uri)
			key = f"{prefix}:{local}"
		else:
			key = attr_clark
		result[key] = value
	# decode ODF-encoded style names for human readability in YAML output
	for name_key in ('style:name', 'style:parent-style-name', 'style:next-style-name',
		'style:page-layout-name'):
		if name_key in result:
			result[name_key] = odt_utils.decode_style_name(result[name_key])
	return result


#============================================
def style_element_to_dict(element: lxml.etree._Element) -> dict:
	"""Convert a style element and its children to a plain dict for YAML output.

	Recursively walks child elements and converts attributes.
	Namespace URIs are replaced with short prefixes.

	Args:
		element: An lxml style element (style:style or similar).

	Returns:
		Dict representation of the style with attributes and child elements.
	"""
	result = element_attribs_to_dict(element)
	# process child elements
	for child in element:
		# get the tag with prefix
		tag = child.tag
		if tag.startswith('{'):
			close_brace = tag.index('}')
			uri = tag[1:close_brace]
			local = tag[close_brace + 1:]
			# build reverse namespace lookup
			reverse_ns = {}
			for prefix, ns_uri in odt_utils.ODF_NAMESPACES.items():
				reverse_ns[ns_uri] = prefix
			prefix = reverse_ns.get(uri, uri)
			tag_name = f"{prefix}:{local}"
		else:
			tag_name = tag
		# recurse into children
		child_dict = style_element_to_dict(child)
		result[tag_name] = child_dict
	return result


#============================================
def extract_styles(odt_data: dict, family_filter: str) -> dict:
	"""Extract named styles, page layouts, and master pages from ODT data.

	Groups styles by family. Applies optional family filter.

	Args:
		odt_data: Dict from odt_utils.read_odt().
		family_filter: Style family to filter by, or None for all.

	Returns:
		Dict with keys 'styles' (grouped by family), 'page_layouts', 'master_pages'.
	"""
	# extract named styles
	named_styles = odt_utils.get_named_styles(odt_data['styles_xml'])
	# group by family
	styles_by_family = {}
	for elem in named_styles:
		family = odt_utils.style_family(elem)
		if family_filter is not None and family != family_filter:
			continue
		if family not in styles_by_family:
			styles_by_family[family] = []
		style_dict = style_element_to_dict(elem)
		styles_by_family[family].append(style_dict)
	# extract page layouts
	page_layouts = []
	if family_filter is None or family_filter == 'page-layout':
		raw_layouts = odt_utils.get_page_layouts(odt_data['styles_xml'])
		for elem in raw_layouts:
			page_layouts.append(style_element_to_dict(elem))
	# extract master pages
	master_pages = []
	if family_filter is None or family_filter == 'master-page':
		raw_masters = odt_utils.get_master_pages(odt_data['styles_xml'])
		for elem in raw_masters:
			master_pages.append(element_attribs_to_dict(elem))
	result = {
		'styles': styles_by_family,
		'page_layouts': page_layouts,
		'master_pages': master_pages,
	}
	return result


#============================================
def compare_styles(styles_a: dict, styles_b: dict) -> dict:
	"""Compare extracted styles from two ODT files.

	Args:
		styles_a: Styles dict from first ODT (via extract_styles).
		styles_b: Styles dict from second ODT (via extract_styles).

	Returns:
		Dict with keys 'added', 'removed', 'changed' listing style differences.
	"""
	added = []
	removed = []
	changed = []
	# get all style names from both sides
	names_a = {}
	for family, style_list in styles_a['styles'].items():
		for s in style_list:
			name = s.get('style:name', 'unknown')
			names_a[(name, family)] = s
	names_b = {}
	for family, style_list in styles_b['styles'].items():
		for s in style_list:
			name = s.get('style:name', 'unknown')
			names_b[(name, family)] = s
	# find added (in B but not in A)
	for key in names_b:
		if key not in names_a:
			added.append({'name': key[0], 'family': key[1]})
	# find removed (in A but not in B)
	for key in names_a:
		if key not in names_b:
			removed.append({'name': key[0], 'family': key[1]})
	# find changed (in both but different)
	for key in names_a:
		if key in names_b and names_a[key] != names_b[key]:
			changed.append({
				'name': key[0],
				'family': key[1],
				'old': names_a[key],
				'new': names_b[key],
			})
	result = {
		'added': added,
		'removed': removed,
		'changed': changed,
	}
	return result


#============================================
def write_template_odt(odt_data: dict, output_path: str) -> None:
	"""Write a content-free template ODT that preserves all styles.

	Clears the office:body/office:text content while keeping
	all named styles, page layouts, and master pages.

	Args:
		odt_data: Dict from odt_utils.read_odt().
		output_path: Path for the output template ODT.
	"""
	# deep copy to avoid modifying original data
	template_data = copy.deepcopy(odt_data)
	# find office:body > office:text and clear its children
	body_tag = odt_utils.qname('office', 'body')
	text_tag = odt_utils.qname('office', 'text')
	content_root = template_data['content_xml']
	body = content_root.find(f".//{body_tag}")
	if body is not None:
		text_elem = body.find(text_tag)
		if text_elem is not None:
			# remove all children from text element
			for child in list(text_elem):
				text_elem.remove(child)
	odt_utils.write_odt(template_data, output_path)


#============================================
def main():
	"""Main entry point for style extraction."""
	args = parse_args()
	# read input ODT
	odt_data = odt_utils.read_odt(args.input_file)
	if args.compare_file is not None:
		# comparison mode: diff styles between two ODT files
		odt_data_b = odt_utils.read_odt(args.compare_file)
		styles_a = extract_styles(odt_data, args.style_family)
		styles_b = extract_styles(odt_data_b, args.style_family)
		diff = compare_styles(styles_a, styles_b)
		# write diff to YAML
		with open(args.output_file, 'w') as f:
			yaml.dump(diff, f, default_flow_style=False, sort_keys=False)
		print(f"Style comparison written to {args.output_file}")
		# print summary
		print(f"  Added: {len(diff['added'])}")
		print(f"  Removed: {len(diff['removed'])}")
		print(f"  Changed: {len(diff['changed'])}")
	elif args.template_mode:
		# template mode: write content-free ODT with styles preserved
		write_template_odt(odt_data, args.output_file)
		print(f"Template ODT written to {args.output_file}")
	else:
		# default: extract styles to YAML
		styles = extract_styles(odt_data, args.style_family)
		with open(args.output_file, 'w') as f:
			yaml.dump(styles, f, default_flow_style=False, sort_keys=False)
		print(f"Styles written to {args.output_file}")


#============================================
if __name__ == '__main__':
	main()
