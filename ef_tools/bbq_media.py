"""Capture BBQ visuals in their complete question context before text parsing."""

# Standard Library
import pathlib
import urllib.parse
import urllib.request

# PIP3 modules
import lxml.html

# Local Repo Modules
import ef_tools.bbq_html
import ef_tools.style_loader


#============================================
def prepare_fields(parts: list, renderer: object, image_store: dict,
			base_url: str, label: str) -> list:
	"""Render outer drawings together, retaining source tables for native DOCX.

	Statement and choice scripts share a browser document, just as they do in
	BP's authored question. Temporary references let the parser preserve order
	and the matching answer shuffle before media paths are assigned.
	"""
	roots = [ef_tools.bbq_html._parse(field) for field in parts[1:]]
	targets = {}
	elements = []
	width = ef_tools.style_loader.load_styles()['page']['image_max_width']
	for root in roots:
		for element in root.xpath('.//table | .//math | .//canvas'):
			if element.xpath('ancestor::table | ancestor::math | ancestor::canvas'):
				continue
			key = str(len(elements) + 1)
			element.set('data-ef-capture', key)
			selector = f'[data-ef-capture="{key}"]'
			targets[selector] = None if element.tag == 'table' else width
			elements.append((element, key, selector))
	if targets:
		if renderer is None:
			raise ValueError(f'{label}: HTML visuals require an image renderer')
		document = ''.join(ef_tools.bbq_html.outer_html(root) for root in roots)
		captures = renderer.render(document, targets, base_url=base_url, label=label)
		for element, key, selector in elements:
			image_store[key] = captures[selector]
			element.attrib.pop('data-ef-capture')
			if element.tag == 'table':
				element.set('data-ef-image', key)
			else:
				image = lxml.html.Element('img')
				image.set('src', ef_tools.bbq_html.RENDERED_IMAGE_PREFIX + key)
				image.tail = element.tail
				element.getparent().replace(element, image)
	for root in roots:
		# Existing images outside captured tables are embedded without a screenshot.
		for image in root.xpath('.//img[not(ancestor::table)]'):
			source = image.get('src', '')
			if ef_tools.bbq_html.is_rendered_image_ref(source):
				continue
			if not source:
				raise ValueError(f'{label}: image has no source')
			base = base_url or pathlib.Path.cwd().as_uri() + '/'
			url = urllib.parse.urljoin(base, source)
			# Trusted authored exam HTML intentionally loads local files and data URLs
			# as well as web images. This local importer is not a remote-input service.
			with urllib.request.urlopen(url, timeout=30) as response:  # nosec B310
				data = response.read()
			key = str(len(image_store) + 1)
			image_store[key] = data
			image.set('src', ef_tools.bbq_html.RENDERED_IMAGE_PREFIX + key)
		# Scripts/styles have already served the browser. Keep any following prose.
		for node in root.xpath('.//script | .//style | .//link'):
			node.drop_tree()
	result = [parts[0]] + [ef_tools.bbq_html._serialize(root) for root in roots]
	return result


#============================================
def clean_table_source(table_html: str) -> str:
	"""Remove the transient media lookup from the table saved in exam YAML."""
	root = ef_tools.bbq_html._parse(table_html)
	for table in root.xpath('.//table'):
		table.attrib.pop('data-ef-image', None)
	result = ef_tools.bbq_html._serialize(root)
	return result
