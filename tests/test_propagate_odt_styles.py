"""Tests for propagate_odt_styles.py style propagation tool."""

# Standard Library
import os
import zipfile

# Pip Modules
import pytest
import lxml.etree

# Local Repo Modules
import git_file_utils
import odt_utils
import propagate_odt_styles

REPO_ROOT = git_file_utils.get_repo_root()


#============================================
def build_odt(path: str, filename: str, style_names: list,
	page_layout_name: str, master_page_name: str) -> str:
	"""Build a test ODT with specified named styles.

	Args:
		path: Directory to create the ODT in.
		filename: Name for the ODT file.
		style_names: List of style names to include (all paragraph family).
		page_layout_name: Name for the page layout.
		master_page_name: Name for the master page.

	Returns:
		Path to the created ODT file.
	"""
	odt_path = os.path.join(path, filename)
	mimetype = b"application/vnd.oasis.opendocument.text"
	# build style elements
	style_elems = ''
	for name in style_names:
		style_elems += (
			f'<style:style style:name="{name}" style:family="paragraph">'
			f'<style:text-properties fo:font-size="11pt"/>'
			f'</style:style>'
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
		+ style_elems +
		'</office:styles>'
		'<office:automatic-styles>'
		f'<style:page-layout style:name="{page_layout_name}">'
		'<style:page-layout-properties fo:page-width="8.5in" fo:page-height="11in"'
		' fo:margin-top="0.6in" fo:margin-bottom="0.6in"/>'
		'</style:page-layout>'
		'</office:automatic-styles>'
		'<office:master-styles>'
		f'<style:master-page style:name="{master_page_name}"'
		f' style:page-layout-name="{page_layout_name}"/>'
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
		'<office:automatic-styles>'
		'<style:style style:name="AutoP1" style:family="paragraph">'
		'<style:text-properties fo:font-size="12pt"/>'
		'</style:style>'
		'</office:automatic-styles>'
		'<office:body>'
		'<office:text>'
		'<text:p text:style-name="Standard">Original content</text:p>'
		'</office:text>'
		'</office:body>'
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
def test_merge_adds_missing_style(tmp_path):
	"""Source style not in target should be added."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard", "Warning"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	source_data = odt_utils.read_odt(source_path)
	target_data = odt_utils.read_odt(target_path)
	summary = propagate_odt_styles.merge_named_styles(
		source_data['styles_xml'], target_data['styles_xml']
	)
	assert summary['added'] == 1
	# verify Warning style now exists in target
	result = odt_utils.get_style_by_name(target_data['styles_xml'], "Warning", "paragraph")
	assert result is not None


#============================================
def test_merge_replaces_existing_style(tmp_path):
	"""Source style with same name should replace target style."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	source_data = odt_utils.read_odt(source_path)
	target_data = odt_utils.read_odt(target_path)
	summary = propagate_odt_styles.merge_named_styles(
		source_data['styles_xml'], target_data['styles_xml']
	)
	assert summary['replaced'] == 1
	assert summary['added'] == 0


#============================================
def test_leaves_target_only_styles(tmp_path):
	"""Styles only in target should be left unchanged."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard", "CustomOnly"], "Mpm1", "Standard")
	source_data = odt_utils.read_odt(source_path)
	target_data = odt_utils.read_odt(target_path)
	propagate_odt_styles.merge_named_styles(
		source_data['styles_xml'], target_data['styles_xml']
	)
	# CustomOnly should still exist
	result = odt_utils.get_style_by_name(target_data['styles_xml'], "CustomOnly", "paragraph")
	assert result is not None


#============================================
def test_automatic_styles_untouched(tmp_path):
	"""Automatic styles in content.xml should not be modified by merge."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	target_data = odt_utils.read_odt(target_path)
	# get auto styles before merge
	auto_before = odt_utils.get_automatic_styles(target_data['content_xml'])
	auto_names_before = [odt_utils.style_name(s) for s in auto_before]
	# perform merge (only touches styles_xml, not content_xml)
	source_data = odt_utils.read_odt(source_path)
	propagate_odt_styles.merge_named_styles(
		source_data['styles_xml'], target_data['styles_xml']
	)
	# auto styles should be unchanged
	auto_after = odt_utils.get_automatic_styles(target_data['content_xml'])
	auto_names_after = [odt_utils.style_name(s) for s in auto_after]
	assert auto_names_before == auto_names_after


#============================================
def test_backup_file(tmp_path):
	"""Backup should create a .bak copy."""
	# create a test file
	test_file = os.path.join(str(tmp_path), "test.odt")
	with open(test_file, 'w') as f:
		f.write("test content")
	backup_path = propagate_odt_styles.backup_file(test_file)
	assert backup_path == test_file + '.bak'
	assert os.path.isfile(backup_path)
	# verify content matches
	with open(backup_path, 'r') as f:
		content = f.read()
	assert content == "test content"


#============================================
def test_dry_run_no_modification(tmp_path):
	"""Dry run should not modify the target file."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard", "Warning"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	# record target file content before propagation
	with open(target_path, 'rb') as f:
		original_bytes = f.read()
	summary = propagate_odt_styles.propagate(
		source_path, target_path,
		include_page_layout=False, dry_run=True
	)
	assert summary['dry_run'] is True
	# target should be unchanged on disk
	with open(target_path, 'rb') as f:
		after_bytes = f.read()
	assert original_bytes == after_bytes


#============================================
def test_page_layout_propagation(tmp_path):
	"""Page layout propagation should replace layouts by name."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	source_data = odt_utils.read_odt(source_path)
	target_data = odt_utils.read_odt(target_path)
	summary = propagate_odt_styles.merge_page_layouts(
		source_data['styles_xml'], target_data['styles_xml']
	)
	# Mpm1 should be replaced (exists in both)
	assert summary['layouts_replaced'] == 1
	assert summary['masters_replaced'] == 1


#============================================
def test_propagate_write_mode(tmp_path):
	"""Write mode should modify target and create backup."""
	source_path = build_odt(str(tmp_path), "source.odt",
		["Standard", "Warning"], "Mpm1", "Standard")
	target_path = build_odt(str(tmp_path), "target.odt",
		["Standard"], "Mpm1", "Standard")
	summary = propagate_odt_styles.propagate(
		source_path, target_path,
		include_page_layout=False, dry_run=False
	)
	assert summary['dry_run'] is False
	assert summary['added'] == 1
	# backup should exist
	assert os.path.isfile(target_path + '.bak')
	# re-read target and verify Warning was added
	target_data = odt_utils.read_odt(target_path)
	result = odt_utils.get_style_by_name(target_data['styles_xml'], "Warning", "paragraph")
	assert result is not None
