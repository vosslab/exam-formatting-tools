#!/usr/bin/env python3
"""Compose a multipart quiz and progeny question from two generated setups."""

# Standard Library
import sys
import re
import json
import math
import random
import pathlib
import argparse
import datetime
import itertools
import importlib

# PIP3 Modules
import lxml.html

# Local Repo Modules
import ef_tools.bbq_parse
import ef_tools.bbq_tasks
import ef_tools.html_renderer
import ef_tools.exam_yaml_writer
import ef_tools.text_utils

# Match chi-square_terms.yml terminology and semantic colors.
STATISTICAL_TERMS = {
	'null hypothesis': ('null hypothesis (H<sub>0</sub>)', '#0247fe'),
	'&alpha;': ('level of significance (&alpha;)', '#8601af'),
	'chi-square statistic': ('chi-square statistic (&chi;<sup>2</sup>)', '#935d00'),
	'critical value': ('critical value', '#4424D6'),
	'p-value': ('p-value', '#C21460'),
	'degrees of freedom': ('degrees of freedom', '#687f19'),
}


#============================================
def statistical_terms(text: str) -> str:
	"""Keep statistical symbols named and consistently colored in quiz prose."""
	def replace(match: re.Match) -> str:
		label, color = STATISTICAL_TERMS[match.group()]
		return f'<span style="color: {color};">{label}</span>'

	return re.sub('|'.join(re.escape(term) for term in STATISTICAL_TERMS), replace, text)

#============================================
def gene_label(letter: str, letters: str, colors: tuple) -> str:
	"""Match gene identity across the clue, genotypes, and gene-order choices."""
	color = colors[letters.index(letter.lower())]
	return f'<span style="color: {color};">{letter}</span>'


#============================================
def mapping_colors(data: dict) -> tuple:
	"""Read the generated palette from the three wild-type allele cells."""
	root = lxml.html.fromstring(data['table_html'])
	for row in root.xpath('.//tr'):
		cells = row.xpath('./td')
		if len(cells) == 5 and all(cell.text_content().strip() == '+' for cell in cells[1:4]):
			colors = []
			for cell in cells[1:4]:
				style = cell.xpath('.//span/@style')[0]
				color = next(value.strip() for name, value in
					(declaration.split(':', 1) for declaration in style.split(';') if ':' in declaration)
					if name.strip() == 'color')
				colors.append(color)
			return tuple(colors)
	raise ValueError('Generated mapping table is missing its wild-type palette row')


#============================================
def load_generators() -> tuple:
	"""Use the same sibling paths as the task importer, without changing those repos."""
	settings = ef_tools.bbq_tasks.load_settings('bbq_settings.yml')
	paths = ef_tools.bbq_tasks.resolve_alias_map(settings['paths'])
	for path in ef_tools.bbq_tasks.build_pythonpath(settings).split(':'):
		if path not in sys.path:
			sys.path.append(path)
	root = pathlib.Path(paths['bp_root'])
	sys.path.extend([str(root / 'chi_square'),
		str(root / 'inheritance-problems' / 'gene_mapping')])
	modules = (importlib.import_module('chisquarelib'),
		importlib.import_module('gene_map_class_lib'))
	return modules


#============================================
def generate_chi_setup(chi: object) -> dict:
	"""Vary the sample size using the dihybrid hypothesis generator's count range."""
	total = random.randint(10, 20) * 16
	expected = [total * weight // 16 for weight in (9, 3, 3, 1)]
	# Nonzero deviations keep the worked-calculation distractors distinct.
	for _ in range(100):
		observed = chi.create_observed_progeny(N=total, ratio='9:3:3:1')
		if min(observed) > 0 and all(abs(observed[i] - expected[i]) > 1 for i in (0, 3)):
			break
	else:
		raise ValueError('Could not draw a usable chi-square setup')
	rows = [[label, exp, obs, '__', '__']
		for label, exp, obs in zip(chi.PEA_PHENOTYPES, expected, observed)]
	setup = {'observed': observed, 'expected': expected,
		'table_html': chi.render_table(chi.CALCULATION_HEADERS, rows, footer=(total, '__'))}
	return setup


#============================================
def generate_setup(chi: object, mapping: object) -> dict:
	"""Draw each setup once; retain scientific data and the generators' own artwork."""
	chi_setup = generate_chi_setup(chi)
	gene_map = mapping.GeneMappingClass(3, 1)
	gene_map.setup_question()
	distances = {''.join(sorted(gene_map.gene_order_str[i - 1]
		+ gene_map.gene_order_str[j - 1])): distance
		for (i, j), distance in gene_map.distances_dict.items()}
	setup = {
		'chi': chi_setup,
		'mapping': {'letters': gene_map.gene_letters_str,
			'order': gene_map.gene_order_str,
			'counts': gene_map.genotype_counts,
			'parents': list(gene_map.parental_genotypes_tuple),
			'distances': distances,
			'phenotypes_html': gene_map.get_phenotype_info(),
			'table_html': gene_map.get_progeny_html_table()},
	}
	return setup


#============================================
def validate_setup(setup: dict) -> None:
	"""Reject inconsistent scientific inputs before composing any answers."""
	# ASVS 2.2.1/2.2.3: validate the snapshot's values and related totals.
	observed = setup['chi']['observed']
	if len(observed) != 4 or any(type(value) is not int or value <= 0 for value in observed):
		raise ValueError('Chi-square setup must contain four positive integer counts')
	total = sum(observed)
	expected = setup['chi']['expected']
	if len(expected) != 4 or any(
			not isinstance(exp, (int, float)) or exp < 5
			or not math.isclose(exp, total * weight / 16)
			for exp, weight in zip(expected, (9, 3, 3, 1))):
		raise ValueError('Expected counts must follow 9:3:3:1 for the observed total and be >= 5')
	data = setup['mapping']
	letters = data['letters']
	if (len(letters) != 3 or not letters.isascii() or not letters.islower()
			or not letters.isalpha() or len(set(letters)) != 3
			or sorted(data['order']) != sorted(letters)):
		raise ValueError('Mapping requires three distinct lowercase gene letters')
	genotypes = {''.join(alleles) for alleles in itertools.product(
		*((letter, '+') for letter in letters))}
	if set(data['counts']) != genotypes or any(
			type(value) is not int or value <= 0 for value in data['counts'].values()):
		raise ValueError('Mapping requires all eight positive progeny classes')
	parents = data['parents']
	if (len(parents) != 2 or any(parent not in genotypes for parent in parents)
			or any(a == b for a, b in zip(*parents))
			or set(sorted(data['counts'], key=data['counts'].get)[-2:]) != set(parents)):
		raise ValueError('Parental classes must be reciprocal and most frequent')
	for owner, fields in ((setup['chi'], ('table_html',)),
			(data, ('table_html', 'phenotypes_html'))):
		if any(not isinstance(owner[field], str) or '<table' not in owner[field]
				for field in fields):
			raise ValueError('Setup is missing the generator table markup')


#============================================
def item(stem: str, choices: list, correct: list, explanation: str,
		layout: int | None = None) -> dict:
	"""Keep each subquestion and its key together while authoring."""
	if len(set(choices)) != len(choices) or not correct or not set(correct) < set(choices):
		raise ValueError(f'Ambiguous answer choices: {stem}')
	question = {'stem': stem, 'choices': choices, 'correct': correct,
		'explanation': explanation}
	if layout is not None:
		question['layout'] = layout
	return question


#============================================
def numeric_item(stem: str, values: list, correct: float, explanation: str,
		suffix: str = '', precision: int = 3) -> dict:
	"""Sort and deduplicate computed distractors at the displayed precision."""
	choices = [f'{value:.{precision}f}{suffix}'
		for value in sorted({round(value, precision) for value in values + [correct]})]
	question = item(stem, choices, [f'{correct:.{precision}f}{suffix}'], explanation)
	return question


#============================================
def chi_items(data: dict, chi: object) -> list:
	"""Follow the historical null -> calculation -> inference progression."""
	observed, expected = data['observed'], data['expected']
	# Each path supplies all row choices and its matching total, in the same A-E order.
	paths = []
	for squared, denominator, reverse in ((False, 'observed', False), (False, 'expected', False),
			(False, 'observed', True), (True, 'observed', False), (True, 'expected', False)):
		values, calculations = [], []
		for obs, exp in zip(observed, expected):
			first, second = (exp, obs) if reverse else (obs, exp)
			value = (first - second) ** 2 if squared else first - second
			expression = f'({first} - {second})' + ('<sup>2</sup>' if squared else '')
			divisor = exp if denominator == 'expected' else obs
			value /= divisor
			expression += f' / {divisor}'
			values.append(value)
			calculations.append(f'{expression} = {value:.3f}'.replace('-', '&ndash;'))
		paths.append((values, calculations))
	terms = paths[-1][0]
	statistic = sum(terms)
	p_value = chi.get_p_value(statistic, 3)
	questions = [item('What is the null hypothesis for this test?', [
		'The offspring fit a 9:3:3:1 phenotypic ratio.',
		'The offspring fit a 1:1:1:1 phenotypic ratio.',
		'The offspring differ significantly from a 9:3:3:1 ratio.',
		'The offspring all have the same phenotype.'],
		['The offspring fit a 9:3:3:1 phenotypic ratio.'],
		'The null hypothesis: independent assortment gives 9:3:3:1 for YyRr x YyRr.')]
	for index, label in ((0, 'yellow, round'), (3, 'green, wrinkled')):
		choices = [calculations[index] for values, calculations in paths]
		questions.append(item(f'What is the chi-square contribution of the {label} row?',
			choices, [choices[-1]], 'Square the deviation and divide by EXPECTED.', layout=1))
	total_choices = [' + '.join(f'({value:.3f})' if value < 0 else f'{value:.3f}' for value in values)
		+ f' &asymp; {sum(values):.3f}' for values, calculations in paths]
	total_choices = [choice.replace('-', '&ndash;') for choice in total_choices]
	questions.append(item('Which sum gives the total chi-square statistic?',
		total_choices, [total_choices[-1]],
		' + '.join(f'{term:.3f}' for term in terms)
		+ f' approximately {statistic:.3f} (displayed row contributions are rounded).', layout=1))
	questions.append(item('How many degrees of freedom does this test have?',
		['1', '2', '3', '4', str(sum(observed) - 1)], ['3'], 'Four classes minus one = 3.'))
	critical = chi.get_critical_value(0.05, 3)
	questions.append(numeric_item('At &alpha; = 0.05, what is the critical value?',
		[chi.get_critical_value(0.05, df) for df in (1, 2, 3, 4)], critical,
		'Use the df = 3 row and the right-tail p = 0.05 column.', precision=2))
	upper_bounds = [0.01, 0.05, 0.1, 0.5, 1.0]
	ranges = ['p < 0.01', '0.01 &le; p < 0.05', '0.05 &le; p < 0.10',
		'0.10 &le; p < 0.50', '0.50 &le; p &le; 1.00']
	answer = next(label for bound, label in zip(upper_bounds, ranges) if p_value < bound)
	questions.append(item('Which range contains the p-value?', ranges, [answer],
		f'Right-tail p = {p_value:.6g} for chi-square = {statistic:.6g}, df = 3.'))
	decisions = ['Reject the null hypothesis; significant deviation.',
		'Reject the null hypothesis; no significant deviation.',
		'Fail to reject the null hypothesis; significant deviation.',
		'Fail to reject the null hypothesis; no significant deviation.']
	questions.append(item('At &alpha; = 0.05, what can you conclude?', decisions,
		[decisions[0 if p_value < 0.05 else 3]],
		f'Compare {statistic:.3f} with {critical:.3f}; failure to reject would not prove the null hypothesis.'))
	questions.append(item('What does the p-value describe?', [
		'The chance the null hypothesis is true, given these offspring.',
		'The chance the null hypothesis is false, given these offspring.',
		'The chance of this or more deviation under the null hypothesis.',
		'The chance of a mutation in the next offspring.'],
		['The chance of this or more deviation under the null hypothesis.'],
		'A p-value assumes the null hypothesis; it is not the probability that the null hypothesis is true.'))
	questions.append(item('Under independent assortment, what is the probability that an '
		'offspring of this cross is <code>YyRr</code>?',
		['1/4 &times; 1/4 = 1/16', '1/2 &times; 1/4 = 1/8',
			'1/2 &times; 1/2 = 1/4', '3/4 &times; 3/4 = 9/16'],
		['1/2 &times; 1/2 = 1/4'],
		'P(Yy) x P(Rr) = 1/2 x 1/2 = 1/4.'))
	for question in questions:
		for field in ('stem', 'explanation'):
			question[field] = statistical_terms(question[field])
		for field in ('choices', 'correct'):
			question[field] = [statistical_terms(value) for value in question[field]]
	return questions


#============================================
def recombination_calculation(values: list, total: int) -> str:
	"""Show the count selection and evaluated percentage without a calculator."""
	frequency = 100 * sum(values) / total
	if not math.isclose(frequency, round(frequency)):
		raise ValueError('Quiz 3 mapping setups must give whole-number recombination frequencies')
	numerator = ' + '.join(str(value) for value in values)
	choice = f'<sup>({numerator})</sup>&frasl;<sub>{total}</sub> &times; 100 = {frequency:.0f}%'
	return choice


#============================================
def mapping_items(data: dict) -> list:
	"""Derive every recombinant class and answer from one testcross."""
	letters, counts, parents = data['letters'], data['counts'], data['parents']
	colors = mapping_colors(data)
	root = lxml.html.fromstring(data['table_html'])
	fills = {}
	for row in root.xpath('.//tr'):
		for cell in row.xpath('./td')[1:4]:
			allele = cell.text_content().strip()
			if allele in letters:
				fills[allele] = ef_tools.text_utils.text_color_from_style(
					cell.get('style', ''), 'background-color')
	if set(fills) != set(letters) or not all(fills.values()):
		raise ValueError('Generated mapping table is missing recessive allele backgrounds')
	total = sum(counts.values())
	pairs = sorted({tuple(sorted((genotype, ''.join('+' if allele != '+' else gene
		for gene, allele in zip(letters, genotype))))) for genotype in counts})
	labels = []
	for pair in pairs:
		genotypes = [' '.join((f'<span style="color: {color};">+</span>' if allele == '+'
			else f'<span style="color: #000000; background-color: {fills[allele]};">{allele}</span>')
			for allele, color in zip(genotype, colors)) for genotype in pair]
		labels.append('<code>' + ' / '.join(genotypes) + '</code>')
	parent_pair = tuple(sorted(parents))
	middle = letters.index(data['order'][1])
	dco = tuple(sorted(parent[:middle] + ('+' if parent[middle] != '+' else letters[middle])
		+ parent[middle + 1:] for parent in parents))
	if set(dco) != set(sorted(counts, key=counts.get)[:2]):
		raise ValueError('Double crossover classes must be the least frequent')
	questions = [item('Which pair represents the parental types?', labels,
		[labels[pairs.index(parent_pair)]], 'The two most frequent classes are parental.'),
		item('Which pair represents the double crossovers?', labels,
		[labels[pairs.index(dco)]], 'The two least frequent classes are double crossovers.')]
	recombinant_counts = {}
	explanations = {}
	for i, j in itertools.combinations(range(3), 2):
		name = (letters[i] + letters[j]).upper()
		parental_combinations = {parent[i] + parent[j] for parent in parents}
		recombinants = [g for g in counts if g[i] + g[j] not in parental_combinations]
		recombinant_pairs = [pair for pair in pairs if set(pair) <= set(recombinants)]
		numerator = sum(counts[g] for g in recombinants)
		frequency = 100 * numerator / total
		if not math.isclose(frequency, data['distances'][name.lower()]):
			raise ValueError(f'{name} counts disagree with generator distance')
		explanation = ' + '.join(str(counts[g]) for g in sorted(recombinants))
		explanation += f' = {numerator}; {numerator}/{total} x 100 = {frequency:g}%.'
		questions.append(item(f'Which TWO pairs are recombinant for genes {gene_label(name[0], letters, colors)} '
			f'and {gene_label(name[1], letters, colors)}? Choose two answers.', labels,
			[labels[pairs.index(pair)] for pair in recombinant_pairs], explanation))
		recombinant_counts[name.lower()] = [counts[g] for g in sorted(recombinants)]
		explanations[name.lower()] = explanation
	adjacent_pairs = [''.join(sorted(data['order'][i:i + 2])) for i in (0, 1)]
	# Error: add adjacent intervals to obtain the outer-pair recombinant percentage.
	span_counts = recombinant_counts[adjacent_pairs[0]] + recombinant_counts[adjacent_pairs[1]]
	for name, values in recombinant_counts.items():
		choice_by_sum = {sum(option): recombination_calculation(option, total)
			for option in list(recombinant_counts.values()) + [span_counts]}
		correct = recombination_calculation(values, total)
		choice_by_sum[sum(values)] = correct
		questions.append(item(f'Which calculation gives the recombination frequency between '
			f'genes {gene_label(name[0].upper(), letters, colors)} and '
			f'{gene_label(name[1].upper(), letters, colors)}?',
			[choice_by_sum[value] for value in sorted(choice_by_sum)], [correct],
			explanations[name], layout=1))
	orders = sorted({min(''.join(order), ''.join(order)[::-1])
		for order in itertools.permutations(letters.upper())})
	canonical_correct = min(data['order'].upper(), data['order'][::-1].upper())
	wrong_orders = [order for order in orders if order != canonical_correct]
	# Include reversed orientations without offering two equivalent correct choices.
	orders = sorted(wrong_orders + [wrong_orders[0][::-1], canonical_correct[::-1]])
	order_choices = [' - '.join(gene_label(letter, letters, colors) for letter in order) for order in orders]
	correct_order = ' - '.join(gene_label(letter, letters, colors)
		for letter in canonical_correct[::-1])
	questions.append(item('Which gene order fits the data?',
		order_choices, [correct_order], f'{data["order"][1].upper()} is the middle gene. '
		'Adjacent interval distances add; the outer-pair recombinant percentage can be smaller.'))
	dco_count = sum(counts[g] for g in dco)
	count_choices = {counts[g]: str(counts[g]) for g in dco}
	for pair in pairs:
		if pair != parent_pair:
			count_choices[sum(counts[g] for g in pair)] = (
				f'{counts[pair[0]]} + {counts[pair[1]]} = {sum(counts[g] for g in pair)}')
	questions.append(item('How many double-crossover offspring were observed?',
		[count_choices[value] for value in sorted(count_choices)], [count_choices[dco_count]],
		f'{counts[dco[0]]} + {counts[dco[1]]} = {dco_count}.'))
	return questions


#============================================
def write_quiz(setup: dict, output: pathlib.Path, date: str, chi: object) -> None:
	"""Use the existing BBQ parser, table capture, YAML writer, and answer-key formatter."""
	validate_setup(setup)
	parts = [chi_items(setup['chi'], chi), mapping_items(setup['mapping']), [item(
		'For the <code>YyRr &times; YyRr</code> cross in Part 1, what is the probability '
		'of a yellow, round offspring under independent assortment?',
		['1/4 &times; 1/4 = 1/16', '1/2 &times; 1/2 = 1/4',
			'3/4 &times; 1/2 = 3/8', '3/4 &times; 3/4 = 9/16'],
		['3/4 &times; 3/4 = 9/16'], 'P(Y-) x P(R-) = 3/4 x 3/4 = 9/16.')]]
	critical_html = chi.make_chi_square_table(p_values=(0.5, 0.1, 0.05, 0.01))
	critical_html = '<table' + critical_html.split('<table', 1)[1]
	critical_html = critical_html.replace('Degrees of freedom', 'df')
	critical_html = critical_html.replace('<thead>',
		'<caption style="text-align: left;">Critical values: right-tail p</caption><thead>', 1)
	# Explicit composition keeps both source tables together at their shared print scale.
	group_start = '<div style="display: inline-flex; align-items: flex-start; gap: 16px;">'
	phenotypes = setup['mapping']['phenotypes_html'].replace('max-width: 720px', 'max-width: 400px')
	phenotypes = '<table' + phenotypes.split('<table', 1)[1]
	introductions = [
		'<p>Cross: <code>YyRr &times; YyRr</code>. '
		'Yellow (Y) and round (R) are completely dominant. Test independent assortment '
		'with &alpha; = 0.05. Use the table for your calculations.</p>'
		+ group_start + setup['chi']['table_html'] + critical_html + '</div>',
		'<p>A female heterozygous for '
		'all three genes was crossed with a triple-recessive male. Lowercase alleles '
		'are recessive; + is wild type. The table shows the female gametes revealed '
		'by the offspring. Circle one answer unless instructed to choose two.</p>'
		+ group_start + phenotypes + setup['mapping']['table_html'] + '</div>',
		'',
	]
	introductions[0] = statistical_terms(introductions[0])
	output.parent.mkdir(parents=True, exist_ok=True)
	snapshot = output.with_name(output.stem + '_setup.json')
	# ASVS 1.5.2: snapshots contain JSON data, never pickled live generator objects.
	with snapshot.open('x') as handle:
		json.dump(setup, handle, indent=2)
	sections, records, explanations = [], [], []
	with ef_tools.html_renderer.HtmlRenderer() as renderer:
		for part_index, questions in enumerate(parts):
			section = {'chapter': ('Questions 1-10: Chi-square and progeny',
				'Questions 11-20: Three-point testcross', 'Progeny probability')[part_index],
				'questions': []}
			for index, question in enumerate(questions):
				prefix = introductions[part_index] if index == 0 else ''
				kind = 'MA' if len(question['correct']) > 1 else 'MC'
				fields = [kind, prefix + '<p>' + question['stem'] + '</p>']
				for choice in question['choices']:
					fields.extend([choice, 'correct' if choice in question['correct'] else 'incorrect'])
				record = ef_tools.bbq_parse.parse_bbq_line('\t'.join(fields), math_renderer=renderer)
				if 'layout' in question:
					record['question']['layout'] = question['layout']
				ef_tools.bbq_parse.render_record_tables(record, renderer,
					str(output.parent / (output.stem + '_files')), f'q{len(records) + 1:02d}')
				if prefix:
					section['setup'] = record['question']['statement'][:-1]
					record['question']['statement'] = record['question']['statement'][-1:]
				section['questions'].append(record['question'])
				records.append(record)
				explanations.append(question['explanation'])
			sections.append(section)
	exam = {'title': 'Genetics Quiz 3', 'date': date, 'document_type': 'quiz',
		'total_points': 21, 'scoring_sections': 3, 'sections': sections}
	ef_tools.exam_yaml_writer.write_exam_yaml(exam, str(output))
	key = ef_tools.bbq_parse.format_answer_key([r['question'] for r in records],
		[r['answer'] for r in records], ['Genetics Quiz 3'] * len(records))
	key += '\nOne point per question. Questions 13-15 require both correct selections.\n\n'
	key += '\n'.join(f'{index}. {text}' for index, text in enumerate(explanations, 1)) + '\n'
	output.with_name(output.stem + '-key.txt').write_text(key)
	print(f'Quiz YAML, setup snapshot, and answer key written beside {output}')


#============================================
def main() -> None:
	"""Generate a fresh version or compose from a saved scientific setup."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-o', '--output', dest='output', required=True,
		help='New exam YAML path; existing artifacts are preserved.')
	parser.add_argument('-i', '--input', dest='input',
		help='Optional saved setup JSON; omit to draw two new setups.')
	parser.add_argument('-d', '--date', dest='date', default=datetime.date.today().isoformat())
	args = parser.parse_args()
	datetime.date.fromisoformat(args.date)
	output = pathlib.Path(args.output)
	if output.suffix not in ('.yaml', '.yml'):
		raise ValueError('Output must be .yaml or .yml')
	for path in (output, output.with_name(output.stem + '_setup.json'),
			output.with_name(output.stem + '-key.txt'),
			output.parent / (output.stem + '_files')):
		if path.exists():
			raise FileExistsError(f'Existing quiz artifact: {path}; choose a new output filename')
	chi, mapping = load_generators()
	setup = json.loads(pathlib.Path(args.input).read_text()) if args.input else generate_setup(chi, mapping)
	write_quiz(setup, output, args.date, chi)


if __name__ == '__main__':
	main()
