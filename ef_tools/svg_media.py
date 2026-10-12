"""Dimensions and direct DOCX insertion for Chromium/Poppler SVG captures."""

# Standard Library
import pathlib

# PIP3 modules
import lxml.etree
import docx.opc.part
import docx.opc.constants
import docx.oxml.shape
import docx.shared


SVG_NAMESPACE = 'http://www.w3.org/2000/svg'


#============================================
def is_svg(data: bytes) -> bool:
	"""Distinguish generated SVG XML from the renderer's PNG fallback."""
	stripped = data.lstrip()
	return stripped.startswith((b'<?xml', b'<svg'))


#============================================
def svg_root(data: bytes) -> object:
	"""Read our generated SVG without resolving external XML entities."""
	# ASVS 1.5.1: SVG parsing does not load DTDs or resolve external entities.
	parser = lxml.etree.XMLParser(resolve_entities=False, no_network=True)
	root = lxml.etree.fromstring(data, parser)
	if root.tag != f'{{{SVG_NAMESPACE}}}svg':
		raise ValueError('Expected an SVG capture')
	return root


#============================================
def pixel_size(image_path: str) -> tuple:
	"""Return the CSS-pixel dimensions recorded by our SVG renderer."""
	root = svg_root(pathlib.Path(image_path).read_bytes())
	dimensions = []
	for name in ('width', 'height'):
		value = root.attrib[name]
		if not value.endswith('px'):
			raise ValueError(f'{image_path}: generated SVG {name} must use px')
		dimensions.append(float(value[:-2]))
	return tuple(dimensions)


#============================================
def add_picture(run: object, image_path: str, **kwargs: object) -> object:
	"""Embed a generated SVG directly; LibreOffice preserves its vectors."""
	width, height = pixel_size(image_path)
	cx = kwargs.get('width')
	cy = kwargs.get('height')
	if cx is None and cy is None:
		cx = docx.shared.Inches(width / 96)
	if cx is None:
		cx = round(cy * width / height)
	if cy is None:
		cy = round(cx * height / width)
	package = run.part.package
	part = docx.opc.part.Part(package.next_partname('/word/media/image%d.svg'),
		'image/svg+xml', pathlib.Path(image_path).read_bytes(), package)
	relation = run.part.relate_to(part, docx.opc.constants.RELATIONSHIP_TYPE.IMAGE)
	inline = docx.oxml.shape.CT_Inline.new_pic_inline(
		run.part.next_id, relation, pathlib.Path(image_path).name, cx, cy)
	run._r.add_drawing(inline)
	return inline
