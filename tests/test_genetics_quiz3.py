"""Protect the shared-setup answer calculations for future Quiz 3 versions."""

# Standard Library
import re
import math
import types

# PIP3 modules
import pytest

# Local Repo Modules
import builders.make_genetics_quiz3 as quiz


#============================================
@pytest.mark.parametrize('data,frequencies,order,dco', [
	({'letters': 'cem', 'order': 'ecm', 'parents': ['+++', 'cem'],
		'counts': {'cem': 1857, 'ce+': 157, 'c+m': 208, 'c++': 12,
			'+em': 10, '+e+': 210, '++m': 173, '+++': 1773},
		'distances': {'ce': 10, 'cm': 8, 'em': 17}},
		['10%', '8%', '17%'], 'E - C - M', '22'),
	({'letters': 'abc', 'order': 'acb', 'parents': ['++c', 'ab+'],
		'counts': {'+++': 4, '++c': 777, '+b+': 176, '+bc': 34,
			'a++': 36, 'a+c': 174, 'ab+': 793, 'abc': 6},
		'distances': {'ab': 21, 'ac': 18, 'bc': 4}},
		['21%', '18%', '4%'], 'A - C - B', '10'),
])
def test_mapping_keys_use_the_same_counts(data: dict, frequencies: list,
		order: str, dco: str) -> None:
	"""Cis/trans phases and a different middle gene give independently known keys."""
	colors = ('#935D00', '#007576', '#C80085')
	data['table_html'] = '<table><tr><td>wildtype</td>' + ''.join(
		f'<td><span style="color: {color};">+</span></td>' for color in colors)
	data['table_html'] += '<td>1</td></tr></table>'
	fills = ('#ffe4d9', '#c9f4f5', '#f3e3ff')
	mutant_row = '<tr><td>mutants</td>' + ''.join(
		f'<td style="background-color: {fill};">{letter}</td>'
		for letter, fill in zip(data['letters'], fills)) + '<td>1</td></tr>'
	data['table_html'] = data['table_html'].replace('</table>', mutant_row + '</table>')
	items = quiz.mapping_items(data)
	assert [item['correct'][0].rsplit(' = ', 1)[1] for item in items[5:8]] == frequencies
	for question in items[5:8]:
		for choice in question['choices']:
			calculation = re.fullmatch(
				r'<sup>\((\d+(?: \+ \d+)*)\)</sup>&frasl;<sub>(\d+)</sub> &times; 100 = (\d+)%', choice)
			assert calculation is not None
			terms, total, percentage = calculation.groups()
			assert sum(int(value) for value in terms.split(' + ')) * 100 == (
				int(total) * int(percentage))
	assert re.sub('<[^>]+>', '', items[8]['correct'][0]) == order[::-1]
	assert 'reading direction' not in items[8]['stem']
	assert sum(re.sub('<[^>]+>', '', choice).split(' - ')[1] == order.split(' - ')[1]
		for choice in items[8]['choices']) == 1
	for choice in items[0]['choices']:
		for letter, color, fill in zip(data['letters'], colors, fills):
			assert f'background-color: {fill};">{letter}</span>' in choice
			assert f'color: {color};">+</span>' in choice
	for letter in data['letters'].upper():
		assert quiz.gene_label(letter, data['letters'], colors) in items[8]['correct'][0]
	assert items[9]['correct'][0].rsplit(' = ', 1)[1] == dco
	for question in items[2:5]:
		assert len(question['correct']) == 2
		assert len(question['choices']) == 4
	assert len(items[8]['choices']) == 4


#============================================
@pytest.mark.parametrize('counts', [[157, 173], [10, 12]])
def test_fractional_recombination_distractors_are_not_rounded(counts: list) -> None:
	"""The former 7.5% and 0.5% distractors cannot masquerade as whole-number calculations."""
	with pytest.raises(ValueError, match='whole-number'):
		quiz.recombination_calculation(counts, 4400)


#============================================
@pytest.mark.parametrize('observed,expected,statistic,p_range,decision', [
	([71, 25, 48, 16], [90, 30, 30, 10], 19.244444444444444,
		'p < 0.01', 'Reject the null hypothesis (H0); significant deviation.'),
	([143, 61, 48, 20], [153, 51, 51, 17], 3.3202614379084965,
		'0.10 &le; p < 0.50', 'Fail to reject the null hypothesis (H0); no significant deviation.'),
])
def test_chi_square_key_and_progeny_probability(observed: list, expected: list,
		statistic: float, p_range: str, decision: str) -> None:
	"""The total uses expected denominators and the p-value is a right-tail probability."""
	def right_tail(value: float, df: int) -> float:
		assert df == 3
		assert math.isclose(value, statistic)
		x = math.sqrt(value / 2)
		return math.erfc(x) + 2 * x * math.exp(-x * x) / math.sqrt(math.pi)

	chi = types.SimpleNamespace(get_p_value=right_tail,
		get_critical_value=lambda alpha, df: [3.841459, 5.991465, 7.814728, 9.487729][df - 1])
	items = quiz.chi_items({'observed': observed, 'expected': expected}, chi)
	assert items[3]['correct'][0].rsplit(' &asymp; ', 1)[1] == f'{statistic:.3f}'
	assert all(' + ' in choice and ' &asymp; ' in choice for choice in items[3]['choices'])
	assert len(items[1]['choices']) == len(items[2]['choices']) == len(items[3]['choices']) == 5
	expected_paths = [
		[(o - e) / o for o, e in zip(observed, expected)],
		[(o - e) / e for o, e in zip(observed, expected)],
		[(e - o) / o for o, e in zip(observed, expected)],
		[(o - e) ** 2 / o for o, e in zip(observed, expected)],
		[(o - e) ** 2 / e for o, e in zip(observed, expected)],
	]
	for path_index, total_choice in enumerate(items[3]['choices']):
		total_choice = total_choice.replace('&ndash;', '-')
		contributions, total = total_choice.split(' &asymp; ')
		values = [value.strip('()') for value in contributions.split(' + ')]
		assert values == [f'{value:.3f}' for value in expected_paths[path_index]]
		assert items[1]['choices'][path_index].replace('&ndash;', '-').endswith(' = ' + values[0])
		assert items[2]['choices'][path_index].replace('&ndash;', '-').endswith(' = ' + values[3])
		assert math.isclose(sum(float(value) for value in values), float(total), abs_tol=0.0021)
	assert '|' not in str(items[1:4])
	assert items[1]['choices'][1].startswith(f'({observed[0]} &ndash; {expected[0]})')
	assert items[1]['choices'][2].startswith(f'({expected[0]} &ndash; {observed[0]})')
	assert all('-' not in choice for question in items[1:4] for choice in question['choices'])
	assert items[4]['correct'] == ['3']
	assert items[4]['choices'][-1] == str(sum(observed) - 1)
	assert items[5]['correct'] == ['7.81']
	assert items[6]['correct'] == [p_range]
	assert [re.sub('<[^>]+>', '', value) for value in items[7]['correct']] == [decision]
	assert 'level of significance (&alpha;)' in items[5]['stem']
	assert 'color: #8601af;' in items[5]['stem']
	assert 'color: #0247fe;' in items[7]['correct'][0]
	assert items[9]['correct'] == ['1/2 &times; 1/2 = 1/4']


#============================================
def test_chi_setup_uses_drawn_total(monkeypatch: pytest.MonkeyPatch) -> None:
	"""A new sample size reaches the sampler, expected counts, and printed footer."""
	monkeypatch.setattr(quiz.random, 'randint', lambda low, high: 17)

	def sample(N: int, ratio: str) -> list:
		assert N == 272
		assert ratio == '9:3:3:1'
		return [143, 61, 48, 20]

	def render(headers: list, rows: list, footer: tuple) -> str:
		assert footer == (272, '__')
		assert [row[1] for row in rows] == [153, 51, 51, 17]
		assert [row[2] for row in rows] == [143, 61, 48, 20]
		return '<table>setup</table>'

	chi = types.SimpleNamespace(create_observed_progeny=sample, render_table=render,
		PEA_PHENOTYPES=['YR', 'Yrr', 'yyR', 'yyrr'], CALCULATION_HEADERS=[])
	setup = quiz.generate_chi_setup(chi)
	assert setup['expected'] == [153, 51, 51, 17]
	assert sum(setup['observed']) == sum(setup['expected']) == 272
