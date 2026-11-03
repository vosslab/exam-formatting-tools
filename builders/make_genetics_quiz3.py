#!/usr/bin/env python3
"""Compose twenty linked questions from two biology-problems setup generators."""

# Standard Library
import sys
import json
import math
import pathlib
import argparse
import datetime
import itertools
import importlib

# Local Repo Modules
import ef_tools.bbq_parse
import ef_tools.bbq_tasks
import ef_tools.html_renderer
import ef_tools.exam_yaml_writer


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
def generate_setup(chi: object, mapping: object) -> dict:
	"""Draw each setup once; retain scientific data and the generators' own artwork."""
	# Match the statistic generator's nontrivial first/last-row arithmetic.
	for _ in range(100):
		observed = chi.create_observed_progeny(N=160, ratio='8:2:4:2')
		if min(observed) > 0 and abs(observed[0] - 90) > 2 and abs(observed[3] - 10) > 1:
			break
	else:
		raise ValueError('Could not draw a usable chi-square setup')
	expected = [90, 30, 30, 10]
	rows = [[label, exp, obs, '__', '__']
		for label, exp, obs in zip(chi.PEA_PHENOTYPES, expected, observed)]
	gene_map = mapping.GeneMappingClass(3, 1)
	gene_map.setup_question()
	distances = {''.join(sorted(gene_map.gene_order_str[i - 1]
		+ gene_map.gene_order_str[j - 1])): distance
		for (i, j), distance in gene_map.distances_dict.items()}
	setup = {
		'chi': {'observed': observed, 'expected': expected,
			'table_html': chi.render_table(chi.CALCULATION_HEADERS, rows,
				footer=(160, '__'))},
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
	if (setup['chi']['expected'] != [90, 30, 30, 10]
			or len(observed) != 4 or sum(observed) != 160
			or any(type(value) is not int or value <= 0 for value in observed)):
		raise ValueError('Chi-square setup must contain four positive counts totaling 160')
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
def item(stem: str, choices: list, correct: list, explanation: str) -> dict:
	"""Keep each subquestion and its key together while authoring."""
	if len(set(choices)) != len(choices) or not correct or not set(correct) < set(choices):
		raise ValueError(f'Ambiguous answer choices: {stem}')
	question = {'stem': stem, 'choices': choices, 'correct': correct,
		'explanation': explanation}
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
	terms = [(obs - exp) ** 2 / exp for obs, exp in zip(observed, expected)]
	statistic = sum(terms)
	p_value = chi.get_p_value(statistic, 3)
	questions = [item('What is the null hypothesis for this test?', [
		'The offspring fit a 9:3:3:1 phenotypic ratio.',
		'The offspring fit a 1:1:1:1 phenotypic ratio.',
		'The offspring differ significantly from a 9:3:3:1 ratio.',
		'The offspring all have the same phenotype.'],
		['The offspring fit a 9:3:3:1 phenotypic ratio.'],
		'H0: independent assortment gives 9:3:3:1 for YyRr x YyRr.')]
	for index, label in ((0, 'yellow, round'), (3, 'green, wrinkled')):
		obs, exp = observed[index], expected[index]
		choices = [f'({obs} - {exp})<sup>2</sup> / {exp} = {terms[index]:.3f}',
			f'({obs} - {exp})<sup>2</sup> / {obs} = {(obs - exp) ** 2 / obs:.3f}',
			f'({obs} - {exp}) / {exp} = {(obs - exp) / exp:.3f}',
			f'({obs} - {exp}) / {obs} = {(obs - exp) / obs:.3f}']
		questions.append(item(f'What is the chi-square contribution of the {label} row?',
			choices, [choices[0]], 'Square the deviation and divide by EXPECTED.'))
	# Wrong totals use observed denominators, unsquared deviations, or cancellation.
	questions.append(numeric_item('What is the total chi-square statistic?', [0,
		sum((o - e) ** 2 / o for o, e in zip(observed, expected)),
		sum(abs(o - e) / e for o, e in zip(observed, expected))], statistic,
		' + '.join(f'{term:.3f}' for term in terms) + f' = {statistic:.3f}.'))
	questions.append(item('How many degrees of freedom does this test have?',
		['1', '2', '3', '4', '159'], ['3'], 'Four classes minus one = 3.'))
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
	decisions = ['Reject H0; the deviation is statistically significant.',
		'Reject H0; the deviation is not statistically significant.',
		'Fail to reject H0; the deviation is statistically significant.',
		'Fail to reject H0; the deviation is not statistically significant.']
	questions.append(item('At &alpha; = 0.05, what can you conclude?', decisions,
		[decisions[0 if p_value < 0.05 else 3]],
		f'Compare {statistic:.3f} with {critical:.3f}; failure to reject would not prove H0.'))
	questions.append(item('What does the p-value describe?', [
		'The probability that H0 is true, given these offspring.',
		'The probability that H0 is false, given these offspring.',
		'The probability of this much deviation or more, assuming H0.',
		'The probability that the next offspring is a mutant.'],
		['The probability of this much deviation or more, assuming H0.'],
		'A p-value conditions on the null hypothesis; it is not P(H0 | data).'))
	questions.append(item('Under independent assortment, what is the probability that an '
		'offspring of this cross is <code>YyRr</code>?',
		['1/16', '1/8', '1/4', '9/16'], ['1/4'],
		'P(Yy) x P(Rr) = 1/2 x 1/2 = 1/4.'))
	return questions


#============================================
def mapping_items(data: dict) -> list:
	"""Derive every recombinant class and answer from one testcross."""
	letters, counts, parents = data['letters'], data['counts'], data['parents']
	total = sum(counts.values())
	pairs = sorted({tuple(sorted((genotype, ''.join('+' if allele != '+' else gene
		for gene, allele in zip(letters, genotype))))) for genotype in counts})
	labels = ['<code>' + ' '.join(a) + ' / ' + ' '.join(b) + '</code>' for a, b in pairs]
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
	distance_questions = []
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
		questions.append(item(f'Which TWO pairs are recombinant for genes {name[0]} '
			f'and {name[1]}? Choose two answers.', labels,
			[labels[pairs.index(pair)] for pair in recombinant_pairs], explanation))
		# Omit either reciprocal pair, or select another pair of loci.
		wrong = [100 * sum(counts[g] for g in pair) / total for pair in recombinant_pairs]
		wrong.extend(data['distances'].values())
		distance_questions.append(numeric_item(
			f'What is the observed recombination frequency between genes {name[0]} and {name[1]}?',
			wrong, frequency, explanation, suffix='%', precision=1))
	questions.extend(distance_questions)
	orders = sorted({min(''.join(order), ''.join(order)[::-1])
		for order in itertools.permutations(letters.upper())})
	order_choices = [' - '.join(order) for order in orders]
	correct_order = ' - '.join(min(data['order'].upper(), data['order'][::-1].upper()))
	questions.append(item('Which gene order fits the data? Either reading direction is equivalent.',
		order_choices, [correct_order], f'{data["order"][1].upper()} is the middle gene. '
		'Adjacent interval distances add; the outer-pair recombinant percentage can be smaller.'))
	dco_count = sum(counts[g] for g in dco)
	questions.append(numeric_item('How many double-crossover offspring were observed?',
		[counts[g] for g in dco] + [sum(counts[g] for g in pair)
		for pair in pairs if pair not in (dco, parent_pair)], dco_count,
		f'{counts[dco[0]]} + {counts[dco[1]]} = {dco_count}.', precision=0))
	return questions


#============================================
def write_quiz(setup: dict, output: pathlib.Path, date: str, chi: object) -> None:
	"""Use the existing BBQ parser, table capture, YAML writer, and answer-key formatter."""
	validate_setup(setup)
	parts = [chi_items(setup['chi'], chi), mapping_items(setup['mapping'])]
	critical_html = chi.make_chi_square_table(p_values=(0.5, 0.1, 0.05, 0.01))
	critical_html = '<table' + critical_html.split('<table', 1)[1]
	critical_html = critical_html.replace('Degrees of freedom', 'df')
	critical_html = critical_html.replace('<thead>',
		'<caption style="text-align: left;">Critical values: right-tail p</caption><thead>', 1)
	# Explicit composition keeps both source tables together at their shared print scale.
	group_start = '<div style="display: flex; align-items: flex-start; gap: 16px;">'
	phenotypes = setup['mapping']['phenotypes_html'].replace('max-width: 720px', 'max-width: 400px')
	introductions = [
		'<p>Questions 1-10 use this cross: <code>YyRr &times; YyRr</code>. '
		'Yellow (Y) and round (R) are completely dominant. Test independent assortment '
		'with &alpha; = 0.05. Use the table for your calculations.</p>'
		+ group_start + setup['chi']['table_html'] + critical_html + '</div>',
		'<p>Questions 11-20 use this three-point testcross. A female heterozygous for '
		'all three genes was crossed with a triple-recessive male. Lowercase alleles '
		'are recessive; + is wild type. The table shows the female gametes revealed '
		'by the offspring. Circle one answer unless instructed to choose two.</p>'
		+ group_start + phenotypes + setup['mapping']['table_html'] + '</div>',
	]
	output.parent.mkdir(parents=True, exist_ok=True)
	snapshot = output.with_name(output.stem + '_setup.json')
	# ASVS 1.5.2: snapshots contain JSON data, never pickled live generator objects.
	with snapshot.open('x') as handle:
		json.dump(setup, handle, indent=2)
	sections, records, explanations = [], [], []
	with ef_tools.html_renderer.HtmlRenderer() as renderer:
		for part_index, questions in enumerate(parts):
			section = {'chapter': ('Part 1: Chi-square and progeny' if part_index == 0
				else 'Part 2: Three-point testcross'), 'questions': []}
			for index, question in enumerate(questions):
				prefix = introductions[part_index] if index == 0 else ''
				kind = 'MA' if len(question['correct']) > 1 else 'MC'
				fields = [kind, prefix + '<p>' + question['stem'] + '</p>']
				for choice in question['choices']:
					fields.extend([choice, 'correct' if choice in question['correct'] else 'incorrect'])
				record = ef_tools.bbq_parse.parse_bbq_line('\t'.join(fields), math_renderer=renderer)
				ef_tools.bbq_parse.render_record_tables(record, renderer,
					str(output.parent / (output.stem + '_files')), f'q{len(records) + 1:02d}')
				section['questions'].append(record['question'])
				records.append(record)
				explanations.append(question['explanation'])
			sections.append(section)
	exam = {'title': 'Genetics Quiz 3', 'date': date, 'document_type': 'quiz',
		'total_points': 20, 'scoring_sections': 2, 'sections': sections}
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
			raise FileExistsError(f'Existing quiz artifact: {path}; choose a new output folder')
	chi, mapping = load_generators()
	setup = json.loads(pathlib.Path(args.input).read_text()) if args.input else generate_setup(chi, mapping)
	write_quiz(setup, output, args.date, chi)


if __name__ == '__main__':
	main()
