"""Tests for extract_odt_styles.py style extraction tool."""

# Standard Library
import os
import zipfile

# Pip Modules
import pytest
import yaml
import lxml.etree

# Local Repo Modules
import git_file_utils
import odt_utils
import extract_odt_styles

REPO_ROOT = git_file_utils.get_repo_root()
ARTIFACTS_DIR = os.path.join(REPO_ROOT, "ARTIFACTS")
HAS_ARTIFACTS = os.path.isdir(ARTIFACTS_DIR)
skip_no_artifacts = pytest.mark.skipif(
	not HAS_ARTIFACTS, reason="ARTIFACTS directory not available"
)
SAMPLE_ODT_2025 = "2025_genetics_final_exam2.odt"


#============================================
def create_minimal_odt(path: str) -> str:
	"""Build a tiny valid ODT file for testing.

	Args:
		path: Directory to create the ODT in.

	Returns:
		Path to the created ODT file.
	"""
	odt_path = os.path.join(path, "test_extract.odt")
	mimetype = b"application/vnd.oasis.opendocument.text"
	styles_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-styles'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		'>'
		'<office:styles>'
		'<style:style style:name="Standard" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
		'<style:style style:name="Bold" style:family="text">'
		'<style:text-properties fo:font-weight="bold"/>'
		'</style:style>'
		'</office:styles>'
		'<office:automatic-styles>'
		'<style:page-layout style:name="Mpm1">'
		'<style:page-layout-properties fo:page-width="8.5in" fo:page-height="11in"/>'
		'</style:page-layout>'
		'</office:automatic-styles>'
		'<office:master-styles>'
		'<style:master-page style:name="Standard" style:page-layout-name="Mpm1"/>'
		'</office:master-styles>'
		'</office:document-styles>'
	)
	content_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-content'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		'>'
		'<office:automatic-styles/>'
		'<office:body>'
		'<office:text>'
		'<text:p text:style-name="Standard">Hello world</text:p>'
		'</office:text>'
		'</office:body>'
		'</office:document-content>'
	)
	manifest_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<manifest:manifest'
		' xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
		'<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
		'<manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>'
		'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
		'</manifest:manifest>'
	)
	zf = zipfile.ZipFile(odt_path, 'w', zipfile.ZIP_DEFLATED)
	zf.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
	zf.writestr('styles.xml', styles_xml)
	zf.writestr('content.xml', content_xml)
	zf.writestr('META-INF/manifest.xml', manifest_xml)
	zf.close()
	return odt_path


#============================================
def create_variant_odt(path: str, filename: str, extra_style: bool) -> str:
	"""Build a variant ODT for comparison testing.

	Args:
		path: Directory to create the ODT in.
		filename: Name for the ODT file.
		extra_style: Whether to include an additional style.

	Returns:
		Path to the created ODT file.
	"""
	odt_path = os.path.join(path, filename)
	mimetype = b"application/vnd.oasis.opendocument.text"
	# build styles section with optional extra style
	extra = ''
	if extra_style:
		extra = (
			'<style:style style:name="Warning" style:family="paragraph">'
			'<style:paragraph-properties fo:background-color="#333333"/>'
			'</style:style>'
		)
	styles_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-styles'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		'>'
		'<office:styles>'
		'<style:style style:name="Standard" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
		+ extra +
		'</office:styles>'
		'<office:automatic-styles/>'
		'<office:master-styles/>'
		'</office:document-styles>'
	)
	content_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-content'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		'>'
		'<office:automatic-styles/>'
		'<office:body><office:text/></office:body>'
		'</office:document-content>'
	)
	manifest_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<manifest:manifest'
		' xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
		'<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
		'</manifest:manifest>'
	)
	zf = zipfile.ZipFile(odt_path, 'w', zipfile.ZIP_DEFLATED)
	zf.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
	zf.writestr('styles.xml', styles_xml)
	zf.writestr('content.xml', content_xml)
	zf.writestr('META-INF/manifest.xml', manifest_xml)
	zf.close()
	return odt_path


#============================================
def test_style_element_to_dict():
	"""Verify style_element_to_dict converts element attributes and children."""
	xml_str = (
		'<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' style:name="Test" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
	)
	elem = lxml.etree.fromstring(xml_str)
	result = extract_odt_styles.style_element_to_dict(elem)
	assert result['style:name'] == 'Test'
	assert result['style:family'] == 'paragraph'
	# child element should be present as nested dict
	assert 'style:text-properties' in result
	assert result['style:text-properties']['fo:font-size'] == '11pt'


#============================================
def test_extract_styles_from_minimal_odt(tmp_path):
	"""Extract styles from minimal ODT and verify structure."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	result = extract_odt_styles.extract_styles(odt_data, None)
	# should have styles grouped by family
	assert 'styles' in result
	assert 'page_layouts' in result
	assert 'master_pages' in result
	# paragraph family should have Standard style
	assert 'paragraph' in result['styles']
	para_names = [s['style:name'] for s in result['styles']['paragraph']]
	assert 'Standard' in para_names
	# text family should have Bold style
	assert 'text' in result['styles']


#============================================
def test_extract_styles_with_family_filter(tmp_path):
	"""Verify family filter restricts output."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	# filter to text family only
	result = extract_odt_styles.extract_styles(odt_data, 'text')
	assert 'text' in result['styles']
	# paragraph family should not be present
	assert 'paragraph' not in result['styles']


#============================================
def test_compare_styles_identical(tmp_path):
	"""Comparing identical styles should yield no diffs."""
	odt_path_a = create_variant_odt(str(tmp_path), "a.odt", extra_style=False)
	odt_path_b = create_variant_odt(str(tmp_path), "b.odt", extra_style=False)
	odt_a = odt_utils.read_odt(odt_path_a)
	odt_b = odt_utils.read_odt(odt_path_b)
	styles_a = extract_odt_styles.extract_styles(odt_a, None)
	styles_b = extract_odt_styles.extract_styles(odt_b, None)
	diff = extract_odt_styles.compare_styles(styles_a, styles_b)
	assert len(diff['added']) == 0
	assert len(diff['removed']) == 0
	assert len(diff['changed']) == 0


#============================================
def test_compare_styles_different(tmp_path):
	"""Comparing ODTs with different styles should find diffs."""
	# a has only Standard, b has Standard + Warning
	odt_path_a = create_variant_odt(str(tmp_path), "a.odt", extra_style=False)
	odt_path_b = create_variant_odt(str(tmp_path), "b.odt", extra_style=True)
	odt_a = odt_utils.read_odt(odt_path_a)
	odt_b = odt_utils.read_odt(odt_path_b)
	styles_a = extract_odt_styles.extract_styles(odt_a, None)
	styles_b = extract_odt_styles.extract_styles(odt_b, None)
	diff = extract_odt_styles.compare_styles(styles_a, styles_b)
	# Warning style is in B but not A
	added_names = [d['name'] for d in diff['added']]
	assert 'Warning' in added_names
	assert len(diff['removed']) == 0


#============================================
def test_write_template_odt(tmp_path):
	"""Template ODT should have empty body but preserve styles."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	output_path = os.path.join(str(tmp_path), "template.odt")
	extract_odt_styles.write_template_odt(odt_data, output_path)
	# read back the template
	template_data = odt_utils.read_odt(output_path)
	# styles should still be present
	styles = odt_utils.get_named_styles(template_data['styles_xml'])
	assert len(styles) > 0
	# body text should be empty
	text_tag = odt_utils.qname('office', 'text')
	body_tag = odt_utils.qname('office', 'body')
	body = template_data['content_xml'].find(f".//{body_tag}")
	text_elem = body.find(text_tag)
	# text element should have no children
	assert len(list(text_elem)) == 0


#============================================
@skip_no_artifacts
def test_extract_real_exam():
	"""Extract styles from real artifact and verify known names present."""
	odt_path = os.path.join(ARTIFACTS_DIR, SAMPLE_ODT_2025)
	if not os.path.isfile(odt_path):
		pytest.skip(f"Artifact file not found: {SAMPLE_ODT_2025}")
	odt_data = odt_utils.read_odt(odt_path)
	result = extract_odt_styles.extract_styles(odt_data, None)
	# check for known style names from docs/ODT_EXAM_STYLES.md
	assert 'paragraph' in result['styles']
	para_names = [s['style:name'] for s in result['styles']['paragraph']]
	assert 'Standard' in para_names
