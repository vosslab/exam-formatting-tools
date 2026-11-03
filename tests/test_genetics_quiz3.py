"""Protect the shared-setup answer calculations for future Quiz 3 versions."""

# Standard Library
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
		['10.0%', '8.0%', '17.0%'], 'E - C - M', '22'),
	({'letters': 'abc', 'order': 'acb', 'parents': ['++c', 'ab+'],
		'counts': {'+++': 4, '++c': 427, '+b+': 114, '+bc': 18,
			'a++': 23, 'a+c': 102, 'ab+': 557, 'abc': 5},
		'distances': {'ab': 20.56, 'ac': 18, 'bc': 4}},
		['20.6%', '18.0%', '4.0%'], 'A - C - B', '9'),
])
def test_mapping_keys_use_the_same_counts(data: dict, frequencies: list,
		order: str, dco: str) -> None:
	"""Cis/trans phases and a different middle gene give independently known keys."""
	items = quiz.mapping_items(data)
	assert [item['correct'] for item in items[5:8]] == [[value] for value in frequencies]
	assert items[8]['correct'] == [order]
	assert items[9]['correct'] == [dco]
	for question in items[2:5]:
		assert len(question['correct']) == 2
		assert len(question['choices']) == 4
	assert len(items[8]['choices']) == 3


#============================================
def test_chi_square_key_and_progeny_probability() -> None:
	"""The total uses expected denominators and the p-value is a right-tail probability."""
	def right_tail(statistic: float, df: int) -> float:
		assert df == 3
		assert math.isclose(statistic, 19.244444444444444)
		x = math.sqrt(statistic / 2)
		return math.erfc(x) + 2 * x * math.exp(-x * x) / math.sqrt(math.pi)

	chi = types.SimpleNamespace(get_p_value=right_tail,
		get_critical_value=lambda alpha, df: [3.841459, 5.991465, 7.814728, 9.487729][df - 1])
	items = quiz.chi_items({'observed': [71, 25, 48, 16], 'expected': [90, 30, 30, 10]}, chi)
	assert items[3]['correct'] == ['19.244']
	assert items[4]['correct'] == ['3']
	assert items[5]['correct'] == ['7.81']
	assert items[6]['correct'] == ['p < 0.01']
	assert items[7]['correct'] == ['Reject H0; the deviation is statistically significant.']
	assert items[9]['correct'] == ['1/4']
