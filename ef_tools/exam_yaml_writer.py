"""Write exam YAML files with validator-friendly quoting.

PyYAML single-quotes strings that contain an apostrophe and escapes the
apostrophe as '' (valid YAML, but some lenient validators reject it). This
writer emits such strings double-quoted instead, so "Chargaff's" appears
literally. Strings without apostrophes keep PyYAML's default plain style.
"""

# PIP3 modules
import yaml


#============================================
def _str_representer(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
	"""Double-quote strings that contain an apostrophe."""
	if "'" in value:
		return dumper.represent_scalar("tag:yaml.org,2002:str", value, style='"')
	return dumper.represent_scalar("tag:yaml.org,2002:str", value)


class ExamYamlDumper(yaml.SafeDumper):
	"""SafeDumper with the apostrophe-aware string representer."""


ExamYamlDumper.add_representer(str, _str_representer)


#============================================
def write_exam_yaml(exam_dict: dict, output_file: str) -> None:
	"""Write exam_dict to output_file as ASCII YAML in insertion order."""
	with open(output_file, 'w', encoding='utf-8') as handle:
		yaml.dump(exam_dict, handle, Dumper=ExamYamlDumper, sort_keys=False, allow_unicode=False)
