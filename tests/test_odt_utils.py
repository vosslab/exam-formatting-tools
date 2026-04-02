"""Tests for the odt_utils shared ODT utility module."""

# Standard Library
import os
import zipfile

# Pip Modules
import pytest
import lxml.etree

# Local Repo Modules
import git_file_utils
import odt_utils

REPO_ROOT = git_file_utils.get_repo_root()
ARTIFACTS_DIR = os.path.join(REPO_ROOT, "ARTIFACTS")
HAS_ARTIFACTS = os.path.isdir(ARTIFACTS_DIR)
skip_no_artifacts = pytest.mark.skipif(
	not HAS_ARTIFACTS, reason="ARTIFACTS directory not available"
)

# sample ODT filenames to look for in ARTIFACTS
SAMPLE_ODT_2025 = "2025_genetics_final_exam2.odt"
SAMPLE_ODT_2019 = "exam1-midtermA2-best_version.odt"


#============================================
def get_artifact_path(filename: str) -> str:
	"""Build full path to an artifact file.

	Args:
		filename: Name of the file in ARTIFACTS/.

	Returns:
		Full path string.
	"""
	path = os.path.join(ARTIFACTS_DIR, filename)
	return path


#============================================
def create_minimal_odt(path: str) -> str:
	"""Build a tiny valid ODT file for testing.

	Creates an ODT with mimetype, styles.xml, content.xml, and manifest.xml.

	Args:
		path: Directory to create the ODT in.

	Returns:
		Path to the created ODT file.
	"""
	odt_path = os.path.join(path, "test_minimal.odt")
	# mimetype content per ODF spec
	mimetype = b"application/vnd.oasis.opendocument.text"
	# minimal styles.xml with one named style
	styles_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-styles'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		' xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"'
		'>'
		'<office:styles>'
		'<style:style style:name="Standard" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
		'<style:style style:name="Question Heading" style:family="paragraph"'
		' style:parent-style-name="Standard">'
		'<style:text-properties fo:font-weight="bold" fo:font-style="italic"/>'
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
	# minimal content.xml with empty body
	content_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<office:document-content'
		' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
		' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		'>'
		'<office:automatic-styles>'
		'<style:style style:name="P1" style:family="paragraph">'
		'<style:text-properties fo:font-size="12pt"/>'
		'</style:style>'
		'</office:automatic-styles>'
		'<office:body>'
		'<office:text>'
		'<text:p text:style-name="Standard">Test content</text:p>'
		'</office:text>'
		'</office:body>'
		'</office:document-content>'
	)
	# minimal manifest.xml
	manifest_xml = (
		'<?xml version="1.0" encoding="UTF-8"?>'
		'<manifest:manifest'
		' xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">'
		'<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>'
		'<manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>'
		'<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
		'</manifest:manifest>'
	)
	# build the ODT ZIP
	zf = zipfile.ZipFile(odt_path, 'w', zipfile.ZIP_DEFLATED)
	zf.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
	zf.writestr('styles.xml', styles_xml)
	zf.writestr('content.xml', content_xml)
	zf.writestr('META-INF/manifest.xml', manifest_xml)
	zf.close()
	return odt_path


#============================================
# Pure logic tests (always run)
#============================================

def test_qname():
	"""Verify qname returns correct Clark notation."""
	result = odt_utils.qname('style', 'name')
	expected = '{urn:oasis:names:tc:opendocument:xmlns:style:1.0}name'
	assert result == expected
	# test another namespace
	result_fo = odt_utils.qname('fo', 'font-size')
	expected_fo = '{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}font-size'
	assert result_fo == expected_fo


#============================================
def test_encode_decode_style_name():
	"""Verify encode/decode round-trip for ODF style name encoding."""
	assert odt_utils.encode_style_name('Question Heading') == 'Question_20_Heading'
	assert odt_utils.decode_style_name('Question_20_Heading') == 'Question Heading'
	# underscore encoding: _5f_ for literal underscore
	assert odt_utils.decode_style_name('RTF_5f_Num_20_2') == 'RTF_Num 2'


#============================================
def test_odf_namespaces_complete():
	"""Verify all expected namespace prefixes are defined."""
	expected_prefixes = [
		'fo', 'style', 'text', 'table', 'draw', 'office',
		'svg', 'xlink', 'number', 'meta', 'dc', 'manifest', 'loext',
	]
	for prefix in expected_prefixes:
		assert prefix in odt_utils.ODF_NAMESPACES, f"Missing namespace prefix: {prefix}"


#============================================
def test_styles_equal_identical():
	"""Two identical style elements should compare equal."""
	xml_str = (
		'<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' style:name="Test" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
	)
	elem_a = lxml.etree.fromstring(xml_str)
	elem_b = lxml.etree.fromstring(xml_str)
	assert odt_utils.styles_equal(elem_a, elem_b) is True


#============================================
def test_styles_equal_different():
	"""Two different style elements should not compare equal."""
	xml_a = (
		'<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' style:name="Test" style:family="paragraph">'
		'<style:text-properties fo:font-size="11pt"/>'
		'</style:style>'
	)
	xml_b = (
		'<style:style xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
		' xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"'
		' style:name="Test" style:family="paragraph">'
		'<style:text-properties fo:font-size="14pt"/>'
		'</style:style>'
	)
	elem_a = lxml.etree.fromstring(xml_a)
	elem_b = lxml.etree.fromstring(xml_b)
	assert odt_utils.styles_equal(elem_a, elem_b) is False


#============================================
def test_read_write_minimal_odt(tmp_path):
	"""Read a minimal ODT and verify the returned dict structure."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	# verify dict keys
	assert 'styles_xml' in odt_data
	assert 'content_xml' in odt_data
	assert 'zip_path' in odt_data
	assert 'other_entries' in odt_data
	assert 'other_data' in odt_data
	# verify XML roots are elements
	assert odt_data['styles_xml'] is not None
	assert odt_data['content_xml'] is not None
	# verify other entries include mimetype and manifest
	other_names = [e.filename for e in odt_data['other_entries']]
	assert 'mimetype' in other_names
	assert 'META-INF/manifest.xml' in other_names


#============================================
def test_round_trip_odt(tmp_path):
	"""Read then write an ODT and verify the output is still valid."""
	odt_path = create_minimal_odt(str(tmp_path))
	# read the original
	odt_data = odt_utils.read_odt(odt_path)
	# write to a new file
	output_path = os.path.join(str(tmp_path), "round_trip.odt")
	odt_utils.write_odt(odt_data, output_path)
	# read the round-tripped file
	odt_data2 = odt_utils.read_odt(output_path)
	# verify styles are preserved
	original_styles = odt_utils.get_named_styles(odt_data['styles_xml'])
	round_trip_styles = odt_utils.get_named_styles(odt_data2['styles_xml'])
	assert len(original_styles) == len(round_trip_styles)
	# verify style names match
	original_names = sorted([odt_utils.style_name(s) for s in original_styles])
	round_trip_names = sorted([odt_utils.style_name(s) for s in round_trip_styles])
	assert original_names == round_trip_names


#============================================
def test_mimetype_first(tmp_path):
	"""Verify mimetype is the first entry in written ODT and uses ZIP_STORED."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	output_path = os.path.join(str(tmp_path), "mimetype_check.odt")
	odt_utils.write_odt(odt_data, output_path)
	# check the ZIP structure
	zf = zipfile.ZipFile(output_path, 'r')
	first_entry = zf.infolist()[0]
	assert first_entry.filename == 'mimetype'
	assert first_entry.compress_type == zipfile.ZIP_STORED
	zf.close()


#============================================
def test_get_named_styles_minimal(tmp_path):
	"""Verify get_named_styles returns styles from minimal ODT."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	styles = odt_utils.get_named_styles(odt_data['styles_xml'])
	# minimal ODT has Standard and Question Heading styles
	assert len(styles) == 2
	names = [odt_utils.style_name(s) for s in styles]
	assert "Standard" in names
	assert "Question Heading" in names


#============================================
def test_get_style_by_name_human_readable(tmp_path):
	"""Verify get_style_by_name finds encoded style with human-readable name."""
	odt_path = create_minimal_odt(str(tmp_path))
	odt_data = odt_utils.read_odt(odt_path)
	# style is stored with plain spaces
	result = odt_utils.get_style_by_name(odt_data['styles_xml'], "Question Heading", "paragraph")
	assert result is not None
	assert odt_utils.style_name(result) == "Question Heading"
	# nonexistent style returns None
	result = odt_utils.get_style_by_name(odt_data['styles_xml'], "Nonexistent", "paragraph")
	assert result is None


#============================================
# Artifact-dependent tests (skip if ARTIFACTS/ missing)
#============================================

@skip_no_artifacts
def test_read_real_odt():
	"""Read a real artifact ODT and verify dict structure."""
	odt_path = get_artifact_path(SAMPLE_ODT_2025)
	if not os.path.isfile(odt_path):
		pytest.skip(f"Artifact file not found: {SAMPLE_ODT_2025}")
	odt_data = odt_utils.read_odt(odt_path)
	assert odt_data['styles_xml'] is not None
	assert odt_data['content_xml'] is not None
	assert len(odt_data['other_entries']) > 0


#============================================
@skip_no_artifacts
def test_get_named_styles_real():
	"""Verify named styles are found in real artifact ODT."""
	odt_path = get_artifact_path(SAMPLE_ODT_2025)
	if not os.path.isfile(odt_path):
		pytest.skip(f"Artifact file not found: {SAMPLE_ODT_2025}")
	odt_data = odt_utils.read_odt(odt_path)
	styles = odt_utils.get_named_styles(odt_data['styles_xml'])
	assert len(styles) > 0
	# check for known style names from docs/ODT_EXAM_STYLES.md
	names = [odt_utils.style_name(s) for s in styles]
	assert "Standard" in names


#============================================
@skip_no_artifacts
def test_get_page_layouts_real():
	"""Verify page layouts are found in real artifact ODT."""
	odt_path = get_artifact_path(SAMPLE_ODT_2025)
	if not os.path.isfile(odt_path):
		pytest.skip(f"Artifact file not found: {SAMPLE_ODT_2025}")
	odt_data = odt_utils.read_odt(odt_path)
	layouts = odt_utils.get_page_layouts(odt_data['styles_xml'])
	assert len(layouts) > 0


#============================================
@skip_no_artifacts
def test_get_master_pages_real():
	"""Verify master pages are found in real artifact ODT."""
	odt_path = get_artifact_path(SAMPLE_ODT_2025)
	if not os.path.isfile(odt_path):
		pytest.skip(f"Artifact file not found: {SAMPLE_ODT_2025}")
	odt_data = odt_utils.read_odt(odt_path)
	pages = odt_utils.get_master_pages(odt_data['styles_xml'])
	assert len(pages) > 0
