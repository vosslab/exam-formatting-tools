"""Load exam style definitions from YAML.

Reads styles/exam_styles.yaml and returns a plain dict. All values
are plain numbers (pt for sizes, inches for spacing/page). The builder
applies Pt() or Inches() wrappers as appropriate.
"""

# Standard Library
import os
import subprocess

# Pip Modules
import yaml


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

	If yaml_path is None, loads styles/exam_styles.yaml relative to
	the repository root.

	Args:
		yaml_path: Optional explicit path to the YAML file.

	Returns:
		Dict of style definitions.
	"""
	if yaml_path is None:
		repo_root = _get_repo_root()
		yaml_path = os.path.join(repo_root, 'styles', 'exam_styles.yaml')
	with open(yaml_path, 'r') as f:
		styles = yaml.safe_load(f)
	return styles
