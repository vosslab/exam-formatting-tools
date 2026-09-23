"""Parse bptools bbq text lines into exam YAML questions plus answer records.

One bbq line is one tab-separated question:

	MC/MA  question  choice  Correct|Incorrect  choice  Correct|Incorrect ...
	MAT    question  prompt  match  prompt  match ...      (pairs in order)
	ORD    question  item  item  item ...                  (correct order)
	NUM / FIB / FIB_PLUS                                    (skipped: print-only)

MC/MA choices arrive pre-shuffled. MAT matches and ORD items arrive in answer
order, so this module shuffles the lettered list and records which letter
belongs to each prompt. ORD prints as a matching-style block whose prompts
are positions ("Position 1", "Position 2", ...).
"""

# Standard Library
import random

# local repo modules
import ef_tools.bbq_html
import ef_tools.question_utils


# bbq question types with no print form in exam YAML
SKIPPED_TYPES = ('NUM', 'FIB', 'FIB_PLUS')
# letter labels for choices, in the order the DOCX builder assigns them
LETTERS = 'ABCDEFGHIJKLMNOP'


#============================================
class UnprintableQuestion(ValueError):
	"""A well-formed bbq question that exam YAML cannot represent.

	Example: a matching prompt that is a drawing table. The Matching Prompt
	paragraph holds text only, so the generator is asked for another
	candidate instead of failing the run.
	"""


#============================================
def _clean_field(html: str) -> tuple:
	"""Reduce one bbq HTML field to exam text and its drawing tables."""
	remaining, tables = ef_tools.bbq_html.pull_tables(html)
	text = ef_tools.bbq_html.clean_inline_html(remaining)
	return text, tables


#============================================
def _clean_choice_fields(raw_choices: list) -> tuple:
	"""Clean a list of choice/match/item fields.

	Returns:
		(items, choice_tables): items are plain strings, or dicts with
		'text' and 'image' when the choice carried a drawing table;
		choice_tables maps choice index -> [table_html, ...].
	"""
	items = []
	choice_tables = {}
	for index, raw in enumerate(raw_choices):
		text, tables = _clean_field(raw)
		# a choice or prompt dict holds one image; several sibling tables in
		# one field have no exam YAML form
		if len(tables) > 1:
			raise UnprintableQuestion(f"field {index} holds {len(tables)} tables")
		if tables:
			items.append({'text': text, 'image': None})
			choice_tables[index] = tables
		else:
			items.append(text)
	return items, choice_tables


#============================================
def _is_correct(status: str) -> bool:
	"""bptools writes 'Correct'/'Incorrect'; older files use lowercase."""
	return status.strip().lower() == 'correct'


#============================================
def _parse_mc(parts: list) -> tuple:
	"""MC and MA: choices at even offsets, status markers at odd offsets."""
	choices, choice_tables = _clean_choice_fields(parts[2::2])
	statuses = parts[3::2]
	letters = [LETTERS[i] for i, status in enumerate(statuses) if _is_correct(status)]
	question = {'choices': choices}
	return question, letters, choice_tables, {}


#============================================
def _shuffled_matching(prompts: list, answers: list) -> tuple:
	"""Build prompts_list/choices_list with shuffled letters and the key.

	answers[i] is the correct option for prompts[i]. The returned letters
	give, for each prompt in order, the letter of its option after shuffling.
	"""
	order = random.sample(range(len(answers)), len(answers))
	choices_list = [answers[i] for i in order]
	letters = [LETTERS[order.index(i)] for i in range(len(answers))]
	question = {'prompts_list': prompts, 'choices_list': choices_list}
	return question, letters


#============================================
def _parse_mat(parts: list) -> tuple:
	"""MAT: prompt/match pairs in answer order."""
	prompts, prompt_tables = _clean_choice_fields(parts[2::2])
	matches, choice_tables = _clean_choice_fields(parts[3::2])
	question, letters = _shuffled_matching(prompts, matches)
	return question, letters, choice_tables, prompt_tables


#============================================
def _parse_ord(parts: list) -> tuple:
	"""ORD: items in correct order become position blanks plus shuffled items."""
	items, choice_tables = _clean_choice_fields(parts[2:])
	prompts = [f"Position {i + 1}" for i in range(len(items))]
	question, letters = _shuffled_matching(prompts, items)
	return question, letters, choice_tables, {}


#============================================
def parse_bbq_line(line: str) -> dict | None:
	"""Parse one bbq line.

	Args:
		line: Tab-separated bbq question line.

	Returns:
		None for blank lines and SKIPPED_TYPES. Otherwise a record:
		{'question': exam YAML dict, 'answer': {'code', 'type', 'letters'},
		'statement_tables': [html...], 'choice_tables': {index: [html...]}}.
	Drawing tables are returned as HTML; the caller renders them and may retain
	the source for the optional native DOCX table backend.

	Raises:
		UnprintableQuestion: the content has no exam YAML form (see class).
		ValueError: unknown question type.
	"""
	line = line.strip()
	if not line:
		return None
	parts = [part.strip() for part in line.split('\t')]
	question_type = parts[0].upper()
	if question_type in SKIPPED_TYPES:
		return None
	if question_type in ('MC', 'MA'):
		question, letters, choice_tables, prompt_tables = _parse_mc(parts)
	elif question_type == 'MAT':
		question, letters, choice_tables, prompt_tables = _parse_mat(parts)
	elif question_type == 'ORD':
		question, letters, choice_tables, prompt_tables = _parse_ord(parts)
	else:
		raise ValueError(f"unknown bbq question type: {question_type!r}")
	# statement: strip the CRC paragraph, pull tables, clean the rest
	code, statement_html = ef_tools.bbq_html.split_question_code(parts[1])
	statement = ef_tools.bbq_html.clean_statement_content(statement_html)
	question = {'statement': statement, **question}
	record = {
		'question': question,
		'answer': {'code': code, 'type': question_type, 'letters': letters},
		'choice_tables': choice_tables,
		'prompt_tables': prompt_tables,
	}
	return record


#============================================
def attach_table_images(record: dict, statement_paths: list, choice_paths: dict,
		prompt_paths: dict = None) -> None:
	"""Fill image paths into a parsed record's question, in place.

	Args:
		record: Output of parse_bbq_line.
		statement_paths: PNG paths for record['statement_tables'], in order.
		choice_paths: index -> [PNG path] for record['choice_tables'].
		prompt_paths: index -> [PNG path] for record['prompt_tables']
			(matching prompts keep their order, so the index is the
			printed position).

	Raises:
		ValueError: a choice or prompt carries more than one table; exam
			YAML choice and prompt dicts hold a single image.
	"""
	question = record['question']
	table_blocks = [block for block in question['statement'] if 'html_table' in block]
	if len(table_blocks) != len(statement_paths):
		raise ValueError(
			f"statement has {len(table_blocks)} table blocks but {len(statement_paths)} rendered images")
	for block, path in zip(table_blocks, statement_paths):
		block['image'] = path
	# choice_paths is keyed by the original bbq choice index; for shuffled
	# matching lists the answer letters recover the printed position
	for index, paths in choice_paths.items():
		if len(paths) != 1:
			raise ValueError(f"choice {index} has {len(paths)} tables; one image per choice")
		target = _choice_dict_for_index(record, index)
		target['image'] = paths[0]
		target['html_table'] = record['choice_tables'][index][0]
	for index, paths in (prompt_paths or {}).items():
		if len(paths) != 1:
			raise ValueError(f"prompt {index} has {len(paths)} tables; one image per prompt")
		question['prompts_list'][index]['image'] = paths[0]
		question['prompts_list'][index]['html_table'] = record['prompt_tables'][index][0]


#============================================
def has_tables(record: dict) -> bool:
	"""Return whether a parsed record carries any drawing table."""
	statement = record['question']['statement']
	found = bool(any('html_table' in block for block in statement)
		or record['choice_tables'] or record['prompt_tables'])
	return found


#============================================
def render_record_tables(record: dict, renderer: object, media_dir: str, stem: str) -> None:
	"""Rasterize every table in a record and attach the PNG paths in place.

	Args:
		record: Output of parse_bbq_line.
		renderer: TableRenderer (or a fake with render_table_png).
		media_dir: `<yaml_dir>/<stem>_files` directory for the PNGs.
		stem: Filename stem for this question (its CRC code).
	"""
	statement_table_html = [
		block['html_table'] for block in record['question']['statement']
		if 'html_table' in block]
	statement_paths = ef_tools.bbq_html.write_table_pngs(
		statement_table_html, renderer, media_dir, stem)
	choice_paths = {}
	for index, tables in record['choice_tables'].items():
		choice_paths[index] = ef_tools.bbq_html.write_table_pngs(
			tables, renderer, media_dir, f"{stem}_choice{index}")
	prompt_paths = {}
	for index, tables in record['prompt_tables'].items():
		prompt_paths[index] = ef_tools.bbq_html.write_table_pngs(
			tables, renderer, media_dir, f"{stem}_prompt{index}")
	attach_table_images(record, statement_paths, choice_paths, prompt_paths)


#============================================
def _choice_dict_for_index(record: dict, index: int) -> dict:
	"""Find the choice dict that came from original bbq choice index."""
	question = record['question']
	if 'choices' in question:
		return question['choices'][index]
	# shuffled matching lists: the dict object identity survived the shuffle,
	# so locate it by matching the original order through the answer letters
	letters = record['answer']['letters']
	position = LETTERS.index(letters[index])
	return question['choices_list'][position]


#============================================
def format_answer_key(questions: list, answers: list, sources: list) -> str:
	"""Format the answer key, one line per printed question block.

	Numbering advances by question_utils.question_span so a matching block
	that the DOCX prints as "Q5-8." is keyed "Q5-8. 5=C 6=A 7=D 8=B".

	Args:
		questions: exam YAML question dicts in print order.
		answers: matching answer dicts ({'code', 'type', 'letters'}).
		sources: matching source labels (generator script names).

	Returns:
		Key text ending with a newline.
	"""
	lines = []
	number = 1
	for question, answer, source in zip(questions, answers, sources):
		span = ef_tools.question_utils.question_span(question)
		letters = answer['letters']
		if span > 1:
			pairs = ' '.join(f"{number + i}={letter}" for i, letter in enumerate(letters))
			label = f"Q{number}-{number + span - 1}. {pairs}"
		else:
			label = f"{number}. {','.join(letters)}"
		lines.append(f"{label}   {answer['code']}   {source}")
		number += span
	key_text = '\n'.join(lines) + '\n'
	return key_text
