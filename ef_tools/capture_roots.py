"""Select authored visual roots for browser capture."""


#============================================
def _has_ancestor(element: object, ancestors: list) -> bool:
	"""Return whether element is nested inside one of ancestors."""
	return any(parent is ancestor for parent in element.iterancestors()
		for ancestor in ancestors)


#============================================
def _inline_display(element: object) -> str:
	"""Return the element's inline display value, if explicitly declared."""
	display = ''
	for declaration in element.get('style', '').split(';'):
		name, separator, value = declaration.partition(':')
		if separator and name.strip().lower() == 'display':
			display = value.strip().lower()
	return display


#============================================
def select_capture_roots(root: object, visual_nodes: list) -> list:
	"""Replace multi-table flex groups with one root in authored document order.

	``visual_nodes`` is already limited to one statement or choice boundary by
	the caller. Only exact inline ``display: flex`` and ``display: inline-flex``
	declarations establish a group; stylesheet classes and computed layout are
	intentionally outside the import contract.
	"""
	outer_tables = [
		node for node in visual_nodes
		if node.tag == 'table' and not node.xpath('ancestor::table')]
	groups = []
	for element in root.iter():
		if _inline_display(element) not in ('flex', 'inline-flex'):
			continue
		member_tables = [
			table for table in outer_tables if _has_ancestor(table, [element])]
		if len(member_tables) >= 2 and not _has_ancestor(element, groups):
			groups.append(element)
	roots = []
	for element in root.iter():
		if any(element is group for group in groups):
			roots.append(element)
			continue
		if not any(element is node for node in visual_nodes):
			continue
		if element.tag == 'table' and element.xpath('ancestor::table'):
			continue
		if _has_ancestor(element, groups):
			continue
		if element.xpath('ancestor::table | ancestor::math | ancestor::canvas'):
			continue
		roots.append(element)
	return roots
