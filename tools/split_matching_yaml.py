#!/usr/bin/env python3
"""Regenerate matching banks from a JSON partition map."""

# Standard Library
import argparse
import json
import pathlib

# PIP Modules
import yaml


OVERRIDE_FIELDS = {
	'items to match per question', 'key description', 'keys description',
	'value description', 'values description', 'dbsubject',
}


#============================================
def split_bank(bank: dict, splits: list) -> dict:
	"""Partition all terms once, retaining source fields unless explicitly overridden."""
	pairs = bank['matching pairs']
	outputs = {}
	assigned = set()
	if not splits:
		raise ValueError('The mapping must contain at least one split')
	for split in splits:
		unknown = set(split) - {'output', 'pairs', 'overrides'}
		if unknown:
			raise ValueError(f'Unknown split fields: {sorted(unknown)}')
		name = split['output']
		if pathlib.Path(name).name != name or pathlib.Path(name).suffix not in ('.yml', '.yaml'):
			raise ValueError(f'Output must be a YAML filename: {name}')
		if name in outputs:
			raise ValueError(f'Duplicate output filename: {name}')
		keys = split['pairs']
		if not isinstance(keys, list) or not keys or not all(isinstance(key, str) for key in keys):
			raise ValueError(f'{name}: pairs must be a nonempty list of term keys')
		if len(set(keys)) != len(keys) or assigned.intersection(keys):
			raise ValueError(f'{name}: a term appears more than once in the split mapping')
		unknown = set(keys) - set(pairs)
		if unknown:
			raise ValueError(f'{name}: unknown matching keys: {sorted(unknown)}')
		overrides = split.get('overrides', {})
		unknown = set(overrides) - OVERRIDE_FIELDS
		if unknown:
			raise ValueError(f'{name}: unsupported metadata overrides: {sorted(unknown)}')
		result = dict(bank)
		result['matching pairs'] = {key: pairs[key] for key in keys}
		result.update(overrides)
		count = result.get('items to match per question', 5)
		if type(count) is not int or not 1 <= count <= len(keys):
			raise ValueError(f'{name}: override items to match per question to fit {len(keys)} terms')
		for field, value in overrides.items():
			if field != 'items to match per question' and not isinstance(value, str):
				raise ValueError(f'{name}: {field} must be text')
		outputs[name] = result
		assigned.update(keys)
	missing = set(pairs) - assigned
	if missing:
		raise ValueError(f'Unassigned matching keys: {sorted(missing)}')
	return outputs


#============================================
def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-i', '--input', required=True, type=pathlib.Path, help='JSON split mapping')
	args = parser.parse_args()
	mapping_path = args.input.resolve()
	mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
	unknown = set(mapping) - {'source', 'source_revision', 'splits'}
	if unknown:
		raise ValueError(f'Unknown mapping fields: {sorted(unknown)}')
	source = (mapping_path.parent / mapping['source']).resolve()
	# ASVS 1.5.2: YAML input cannot construct arbitrary Python objects.
	bank = yaml.safe_load(source.read_text(encoding='utf-8'))
	outputs = split_bank(bank, mapping['splits'])
	output_dir = pathlib.Path('generated/matching_sets')
	header = '# Generated matching bank; edit the original YAML or JSON mapping, not this file.\n'
	header += f'# Split mapping: {mapping_path.name}\n'
	header += f'# Source relative to mapping: {mapping["source"]}\n'
	if 'source_revision' in mapping:
		header += f'# BPQ comparison baseline: {mapping["source_revision"]}\n'
	header += '# Regenerate from the mapping after updating the original.\n'
	output_dir.mkdir(parents=True, exist_ok=True)
	for name, result in outputs.items():
		content = header + yaml.safe_dump(result, sort_keys=False, allow_unicode=False, width=100)
		with (output_dir / name).open('w', encoding='utf-8') as handle:
			handle.write(content)
		print(f'Wrote {output_dir / name}')


if __name__ == '__main__':
	main()
