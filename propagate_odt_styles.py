#!/usr/bin/env python3
"""Apply styles from a source ODT to one or more target ODT files.

Reads named styles from a source ODT and replaces or merges them into
target ODT files, preserving target content. Supports dry-run mode
and optional page layout propagation.
"""

# Standard Library
import copy
import shutil
import argparse

# Pip Modules
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
		description="Propagate styles from a source ODT to target ODT files"
	)
	parser.add_argument(
		'-s', '--source', dest='source_file', required=True,
		help="Source ODT file to read styles from"
	)
	parser.add_argument(
		'-t', '--target', dest='target_files', nargs='+', required=True,
		help="Target ODT file(s) to apply styles to"
	)
	# dry-run boolean pair
	parser.add_argument(
		'-n', '--dry-run', dest='dry_run', action='store_true',
		help="Report what would change without modifying files"
	)
	parser.add_argument(
		'-w', '--write', dest='dry_run', action='store_false',
		help="Actually modify target files"
	)
	# page layout boolean pair
	parser.add_argument(
		'-p', '--include-page-layout', dest='include_page_layout', action='store_true',
		help="Also propagate page layouts and master pages"
	)
	parser.add_argument(
		'-P', '--no-page-layout', dest='include_page_layout', action='store_false',
		help="Do not propagate page layouts"
	)
	parser.set_defaults(dry_run=True, include_page_layout=False)
	args = parser.parse_args()
	return args


#============================================
def backup_file(target_path: str) -> str:
	"""Create a backup copy of the target file.

	Args:
		target_path: Path to the file to back up.

	Returns:
		Path to the backup file.
	"""
	backup_path = target_path + '.bak'
	shutil.copy2(target_path, backup_path)
	return backup_path


#============================================
def merge_named_styles(source_styles_root: lxml.etree._Element,
	target_styles_root: lxml.etree._Element) -> dict:
	"""Merge named styles from source into target styles.xml.

	For each named style in source office:styles:
	- If target has same name+family, replace the element
	- If target does not have it, append it
	- Automatic styles are never touched

	Args:
		source_styles_root: Root element of source styles.xml.
		target_styles_root: Root element of target styles.xml (modified in place).

	Returns:
		Summary dict with counts: replaced, added, skipped.
	"""
	source_styles = odt_utils.get_named_styles(source_styles_root)
	replaced = 0
	added = 0
	skipped = 0
	# find the office:styles container in target
	office_styles_tag = odt_utils.qname('office', 'styles')
	target_office_styles = target_styles_root.find(f".//{office_styles_tag}")
	if target_office_styles is None:
		skipped = len(source_styles)
		summary = {'replaced': replaced, 'added': added, 'skipped': skipped}
		return summary
	# build index of target styles by (name, family)
	target_styles = odt_utils.get_named_styles(target_styles_root)
	target_index = {}
	for elem in target_styles:
		name = odt_utils.style_name(elem)
		family = odt_utils.style_family(elem)
		target_index[(name, family)] = elem
	# merge each source style
	for source_elem in source_styles:
		name = odt_utils.style_name(source_elem)
		family = odt_utils.style_family(source_elem)
		key = (name, family)
		# deep copy source element for insertion
		new_elem = copy.deepcopy(source_elem)
		if key in target_index:
			# replace existing style
			old_elem = target_index[key]
			parent = old_elem.getparent()
			idx = list(parent).index(old_elem)
			parent.remove(old_elem)
			parent.insert(idx, new_elem)
			target_index[key] = new_elem
			replaced += 1
		else:
			# add new style
			target_office_styles.append(new_elem)
			target_index[key] = new_elem
			added += 1
	summary = {'replaced': replaced, 'added': added, 'skipped': skipped}
	return summary


#============================================
def merge_page_layouts(source_root: lxml.etree._Element,
	target_root: lxml.etree._Element) -> dict:
	"""Merge page layouts and master pages from source into target.

	Replaces matching elements by name, adds missing ones.

	Args:
		source_root: Root element of source styles.xml.
		target_root: Root element of target styles.xml (modified in place).

	Returns:
		Summary dict with counts of layouts and master pages replaced/added.
	"""
	layouts_replaced = 0
	layouts_added = 0
	masters_replaced = 0
	masters_added = 0
	style_name_attr = odt_utils.qname('style', 'name')
	# merge page layouts
	source_layouts = odt_utils.get_page_layouts(source_root)
	target_layouts = odt_utils.get_page_layouts(target_root)
	# build index of target layouts by name
	target_layout_index = {}
	for elem in target_layouts:
		name = elem.get(style_name_attr)
		target_layout_index[name] = elem
	# find automatic-styles container in target for page layouts
	auto_styles_tag = odt_utils.qname('office', 'automatic-styles')
	target_auto_styles = target_root.find(f".//{auto_styles_tag}")
	for source_elem in source_layouts:
		name = source_elem.get(style_name_attr)
		new_elem = copy.deepcopy(source_elem)
		if name in target_layout_index:
			old_elem = target_layout_index[name]
			parent = old_elem.getparent()
			idx = list(parent).index(old_elem)
			parent.remove(old_elem)
			parent.insert(idx, new_elem)
			layouts_replaced += 1
		elif target_auto_styles is not None:
			target_auto_styles.append(new_elem)
			layouts_added += 1
	# merge master pages
	source_masters = odt_utils.get_master_pages(source_root)
	target_masters = odt_utils.get_master_pages(target_root)
	target_master_index = {}
	for elem in target_masters:
		name = elem.get(style_name_attr)
		target_master_index[name] = elem
	# find master-styles container in target
	master_styles_tag = odt_utils.qname('office', 'master-styles')
	target_master_styles = target_root.find(f".//{master_styles_tag}")
	for source_elem in source_masters:
		name = source_elem.get(style_name_attr)
		new_elem = copy.deepcopy(source_elem)
		if name in target_master_index:
			old_elem = target_master_index[name]
			parent = old_elem.getparent()
			idx = list(parent).index(old_elem)
			parent.remove(old_elem)
			parent.insert(idx, new_elem)
			masters_replaced += 1
		elif target_master_styles is not None:
			target_master_styles.append(new_elem)
			masters_added += 1
	summary = {
		'layouts_replaced': layouts_replaced,
		'layouts_added': layouts_added,
		'masters_replaced': masters_replaced,
		'masters_added': masters_added,
	}
	return summary


#============================================
def propagate(source_path: str, target_path: str,
	include_page_layout: bool, dry_run: bool) -> dict:
	"""Propagate styles from source ODT to a single target ODT.

	Args:
		source_path: Path to source ODT file.
		target_path: Path to target ODT file.
		include_page_layout: Whether to also propagate page layouts and master pages.
		dry_run: If True, report changes without modifying the target file.

	Returns:
		Summary dict with merge results.
	"""
	source_data = odt_utils.read_odt(source_path)
	target_data = odt_utils.read_odt(target_path)
	# merge named styles
	style_summary = merge_named_styles(
		source_data['styles_xml'], target_data['styles_xml']
	)
	# optionally merge page layouts
	layout_summary = {}
	if include_page_layout:
		layout_summary = merge_page_layouts(
			source_data['styles_xml'], target_data['styles_xml']
		)
	# write or just report
	if not dry_run:
		# backup before writing
		backup_path = backup_file(target_path)
		print(f"  Backup: {backup_path}")
		odt_utils.write_odt(target_data, target_path)
	summary = {}
	summary.update(style_summary)
	summary.update(layout_summary)
	summary['dry_run'] = dry_run
	return summary


#============================================
def main():
	"""Main entry point for style propagation."""
	args = parse_args()
	print(f"Source: {args.source_file}")
	if args.dry_run:
		print("Mode: dry-run (no files will be modified)")
	else:
		print("Mode: write (files will be modified)")
	for target_path in args.target_files:
		print(f"\nTarget: {target_path}")
		summary = propagate(
			args.source_file, target_path,
			args.include_page_layout, args.dry_run
		)
		print(f"  Styles replaced: {summary.get('replaced', 0)}")
		print(f"  Styles added: {summary.get('added', 0)}")
		if args.include_page_layout:
			print(f"  Layouts replaced: {summary.get('layouts_replaced', 0)}")
			print(f"  Layouts added: {summary.get('layouts_added', 0)}")
			print(f"  Master pages replaced: {summary.get('masters_replaced', 0)}")
			print(f"  Master pages added: {summary.get('masters_added', 0)}")


#============================================
if __name__ == '__main__':
	main()
