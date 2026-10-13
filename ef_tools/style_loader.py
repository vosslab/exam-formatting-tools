"""Load exam style definitions from YAML.

Reads assessment_styles/exam_styles.yaml and returns a plain dict. All values
are plain numbers (pt for sizes, inches for spacing/page). The builder
applies Pt() or Inches() wrappers as appropriate.
"""

# Standard Library
import os
import copy
import subprocess

# Pip Modules
import yaml


#============================================
def for_paper_size(styles: dict, paper_size: str) -> dict:
	"""Adapt Letter-based horizontal positions without changing fonts or drawing scale."""
	dimensions = {'letter': (8.5, 11.0), 'a4': (210 / 25.4, 297 / 25.4)}
	if paper_size not in dimensions:
		raise ValueError(f'Unsupported paper size: {paper_size}')
	adapted = copy.deepcopy(styles)
	page = adapted['page']
	width, height = dimensions[paper_size]
	page['width'] = width
	page['height'] = height
	if paper_size == 'letter':
		return adapted
	base_width = 8.5 - 2 * page['margin']
	usable_width = width - 2 * page['margin']
	ratio = usable_width / base_width
	page['header_center_tab'] = usable_width / 2
	page['header_right_tab'] = usable_width
	# Keep the name/score block's width by moving its left edge with the right margin.
	page['heading_block_tab'] += usable_width - base_width
	indent = adapted['spacing']['choice_indent']
	for columns, stops in adapted['layout_tab_stops'].items():
		adapted['layout_tab_stops'][columns] = [indent + (stop - indent) * ratio for stop in stops]
	adapted['matching_prompt_tab_stops'] = [
		stop * ratio for stop in adapted['matching_prompt_tab_stops']]
	return adapted


#============================================
def _get_repo_root() -> str:
	"""Get the repository root directory.

	Returns:
		Absolute path to the repository root.
	"""
	result = subprocess.check_output(
		["git", "rev-parse", "--show-toplevel"],
		text=True,
	).strip()
	return result


#============================================
def load_styles(yaml_path: str = None) -> dict:
	"""Load exam style definitions from a YAML file.

	If yaml_path is None, loads assessment_styles/exam_styles.yaml relative to
	the repository root.

	Args:
		yaml_path: Optional explicit path to the YAML file.

	Returns:
		Dict of style definitions.
	"""
	if yaml_path is None:
		repo_root = _get_repo_root()
		yaml_path = os.path.join(repo_root, 'assessment_styles', 'exam_styles.yaml')
	with open(yaml_path, 'r') as f:
		styles = yaml.safe_load(f)
	return styles
