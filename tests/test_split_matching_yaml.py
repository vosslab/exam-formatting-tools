"""Protect matching-bank partitioning and the original source YAML."""

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

SPEC = importlib.util.spec_from_file_location(
	'split_matching_yaml', pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'split_matching_yaml.py')
split_matching_yaml = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(split_matching_yaml)


def test_split_preserves_source_and_supports_metadata_overrides() -> None:
	bank = {
		'items to match per question': 1, 'key description': 'term',
		'keys description': 'terms', 'value description': 'definition',
		'values description': 'definitions', 'dbsubject': 'Biostatistics',
		'replacement_rules': {'alpha': '<b>&alpha;</b>'},
		'matching pairs': {'a': ['first', 'alternate'], 'b': ['second']},
	}
	original = copy.deepcopy(bank)
	splits = [
		{'output': 'a.yml', 'pairs': ['a']},
		{'output': 'b.yml', 'pairs': ['b'], 'overrides': {
			'key description': 'statistical term', 'keys description': 'statistical terms',
			'value description': 'explanation', 'values description': 'explanations',
			'dbsubject': 'Statistics', 'items to match per question': 1,
		}},
	]
	result = split_matching_yaml.split_bank(bank, splits)
	assert result['a.yml'] == {**bank, 'matching pairs': {'a': ['first', 'alternate']}}
	assert result['b.yml'] == {**bank, **splits[1]['overrides'], 'matching pairs': {'b': ['second']}}
	result['a.yml']['replacement_rules']['alpha'] = 'changed'
	assert result['b.yml']['replacement_rules'] == bank['replacement_rules']
	assert bank == original


@pytest.mark.parametrize('splits, message', [
	([{'output': 'a.yml', 'pairs': ['a', 'a']}], 'more than once'),
	([{'output': 'a.yml', 'pairs': ['a']}, {'output': 'b.yml', 'pairs': ['a']}], 'more than once'),
	([{'output': 'a.yml', 'pairs': ['missing']}], 'unknown matching keys'),
	([{'output': 'a.yml', 'pairs': ['a']}], 'Unassigned'),
	([{'output': '../a.yml', 'pairs': ['a', 'b']}], 'YAML filename'),
	([{'output': 'a.yml', 'pairs': ['a', 'b'], 'overrides': {'replacement_rules': {}}}], 'unsupported'),
	([{'output': 'a.yml', 'pairs': ['a', 'b'], 'overrides': {'items to match per question': 3}}], 'fit 2 terms'),
])
def test_invalid_partition_is_rejected(splits: list, message: str) -> None:
	bank = {'items to match per question': 1, 'matching pairs': {'a': ['A'], 'b': ['B']}}
	with pytest.raises(ValueError, match=message):
		split_matching_yaml.split_bank(bank, splits)


def test_cli_refreshes_generated_files(tmp_path, monkeypatch) -> None:
	(tmp_path / 'source.yml').write_text('items to match per question: 1\nmatching pairs:\n  a: [A]\n')
	mapping = tmp_path / 'split.json'
	mapping.write_text('{"source":"source.yml","splits":[{"output":"a.yml","pairs":["a"]}]}')
	monkeypatch.setattr(sys, 'argv', ['split_matching_yaml.py', '-i', str(mapping)])
	split_matching_yaml.main()
	assert yaml.safe_load((tmp_path / 'a.yml').read_text())['matching pairs'] == {'a': ['A']}
	(tmp_path / 'source.yml').write_text('items to match per question: 1\nmatching pairs:\n  a: [Polished]\n')
	split_matching_yaml.main()
	assert yaml.safe_load((tmp_path / 'a.yml').read_text())['matching pairs'] == {'a': ['Polished']}


def test_cli_refuses_to_overwrite_original(tmp_path, monkeypatch) -> None:
	source = tmp_path / 'source.yml'
	content = 'items to match per question: 1\nmatching pairs:\n  a: [A]\n'
	source.write_text(content)
	mapping = tmp_path / 'split.json'
	mapping.write_text('{"source":"source.yml","splits":[{"output":"source.yml","pairs":["a"]}]}')
	monkeypatch.setattr(sys, 'argv', ['split_matching_yaml.py', '-i', str(mapping)])
	with pytest.raises(ValueError, match='replace the original'):
		split_matching_yaml.main()
	assert source.read_text() == content
