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
import os
import io
import random
import re

# PIP3 modules
import PIL.Image

# local repo modules
import ef_tools.bbq_html
import ef_tools.bbq_media
import ef_tools.svg_media
import ef_tools.question_utils
import ef_tools.compact


# bbq question types with no normal exam/quiz print form in exam YAML
SKIPPED_TYPES = ('NUM', 'FIB', 'FIB_PLUS')
# letter labels for choices, in the order the DOCX builder assigns them
LETTERS = 'ABCDEFGHIJKLMNOP'
HANDOUT_BLANK = '____________________'
_BOLD_HEADING_RE = re.compile(r'^<b>(.*?)</b>$', re.IGNORECASE)


#============================================
class UnprintableQuestion(ValueError):
	"""A well-formed bbq question that exam YAML cannot represent.

	Example: a matching prompt that is a drawing table. The Matching Prompt
	paragraph holds text only, so the generator is asked for another
	candidate instead of failing the run.
	"""


#============================================
def _clean_field(html: str, rendered_images: dict, field_name: str,
			math_renderer: object) -> tuple:
	"""Reduce one bbq field to text, tables, and standalone generated images."""
	image_refs = ef_tools.bbq_html.standalone_rendered_image_refs(html)
	remaining, tables = ef_tools.bbq_html.pull_tables(html)
	text = ef_tools.bbq_html.clean_inline_html(remaining)
	return text, tables, image_refs


#============================================
def _clean_choice_fields(raw_choices: list, rendered_images: dict,
			field_name: str, math_renderer: object) -> tuple:
	"""Clean a list of choice/match/item fields.

	Returns:
		(items, choice_tables): items are plain strings, or dicts with
		'text' and 'image' when the choice carried a drawing table;
		choice_tables maps choice index -> [table_html, ...].
	"""
	items = []
	choice_tables = {}
	for index, raw in enumerate(raw_choices):
		text, tables, image_refs = _clean_field(
			raw, rendered_images, f"{field_name} {index + 1}", math_renderer)
		# a choice or prompt dict holds one image; several sibling tables in
		# one field have no exam YAML form
		if len(tables) > 1:
			raise UnprintableQuestion(f"field {index} holds {len(tables)} tables")
		if len(image_refs) > 1:
			raise ValueError(
				f"{field_name} {index + 1} has {len(image_refs)} standalone "
				"molecule images; one image per choice is supported")
		if tables and image_refs:
			raise ValueError(
				f"{field_name} {index + 1} combines a table with a standalone "
				"molecule image")
		if tables:
			items.append({'text': text, 'image': None})
			choice_tables[index] = tables
		elif image_refs:
			items.append({'text': text, 'image': image_refs[0]})
		else:
			items.append(text)
	return items, choice_tables


#============================================
def _is_correct(status: str) -> bool:
	"""bptools writes 'Correct'/'Incorrect'; older files use lowercase."""
	return status.strip().lower() == 'correct'


#============================================
def _parse_mc(parts: list, rendered_images: dict, question_code: str,
			math_renderer: object) -> tuple:
	"""MC and MA: choices at even offsets, status markers at odd offsets."""
	choices, choice_tables = _clean_choice_fields(
		parts[2::2], rendered_images, f"question {question_code} choice",
		math_renderer)
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
def _parse_mat(parts: list, rendered_images: dict, question_code: str,
			math_renderer: object) -> tuple:
	"""MAT: prompt/match pairs in answer order."""
	prompts, prompt_tables = _clean_choice_fields(
		parts[2::2], rendered_images, f"question {question_code} prompt",
		math_renderer)
	matches, choice_tables = _clean_choice_fields(
		parts[3::2], rendered_images, f"question {question_code} choice",
		math_renderer)
	question, letters = _shuffled_matching(prompts, matches)
	return question, letters, choice_tables, prompt_tables


#============================================
def _parse_ord(parts: list, rendered_images: dict, question_code: str,
			math_renderer: object) -> tuple:
	"""ORD: items in correct order become position blanks plus shuffled items."""
	items, choice_tables = _clean_choice_fields(
		parts[2:], rendered_images, f"question {question_code} choice",
		math_renderer)
	prompts = [f"Position {i + 1}" for i in range(len(items))]
	question, letters = _shuffled_matching(prompts, items)
	return question, letters, choice_tables, {}


#============================================
def _parse_handout_blank(parts: list, question_type: str) -> tuple:
	"""Return the key payload for a non-choice handout item."""
	if question_type == 'NUM':
		if len(parts) < 3:
			raise ValueError('NUM question is missing its answer')
		answer = parts[2]
		question = {}
		return question, answer
	if question_type == 'FIB':
		answers = [part for part in parts[2:] if part]
		if not answers:
			raise ValueError('FIB question is missing its answer')
		question = {}
		return question, ' / '.join(answers)
	groups = []
	index = 2
	while index < len(parts):
		name = parts[index]
		index += 1
		answers = []
		while index < len(parts) and parts[index] not in ('', '<div></div>'):
			answers.append(parts[index])
			index += 1
		if index < len(parts) and parts[index] in ('', '<div></div>'):
			index += 1
		if not name or not answers:
			raise ValueError('FIB_PLUS has a malformed blank group')
		groups.append((name, answers))
	if not groups:
		raise ValueError('FIB_PLUS question is missing blank groups')
	answer = '; '.join(f"{name}={' / '.join(answers)}" for name, answers in groups)
	question = {}
	return question, answer


#============================================
def _heading_text(line: str) -> str:
	"""Return a normalized standalone bold heading, or an empty string."""
	match = _BOLD_HEADING_RE.fullmatch(line.strip())
	if match is None:
		return ''
	return re.sub(r'<[^>]+>', '', match.group(1)).strip().rstrip(':').lower()


#============================================
def _append_handout_blank(statement: list) -> None:
	"""Append one paper blank to the final non-hint prompt line.

	NUM and FIB BBQ records provide answers separately and reserve no prompt
	placeholder syntax. The exact printed blank is the only recognized existing
	blank, so authored underscore-like text is never guessed at or rewritten.
	"""
	if any(HANDOUT_BLANK in block.get('text', '') for block in statement):
		return
	section_heading = ''
	candidate = None
	for block in statement:
		if 'text' not in block:
			continue
		for line_index, line in enumerate(block['text'].split('\n')):
			heading = _heading_text(line)
			if heading:
				section_heading = heading
				if heading not in ef_tools.compact.HINT_HEADINGS:
					# Some NUM/FIB authors make the final prompt a bold line.
					# Keeping it as the candidate puts the blank after </b>.
					candidate = (block, line_index)
				continue
			if line.strip() and section_heading not in ef_tools.compact.HINT_HEADINGS:
				candidate = (block, line_index)
	if candidate is None:
		raise ValueError('NUM/FIB handout question has no prose prompt for its answer blank')
	block, line_index = candidate
	lines = block['text'].split('\n')
	lines[line_index] += f' Answer: {HANDOUT_BLANK}'
	block['text'] = '\n'.join(lines)


#============================================
def parse_bbq_line(line: str, math_renderer: object = None, base_url: str = '',
		handout: bool = False) -> dict | None:
	"""Parse one bbq line.

	Args:
		line: Tab-separated bbq question line.
		math_renderer: Shared HTML renderer used for all question visuals.
		base_url: Source file URL for relative resources.

	Returns:
		None for blank lines and SKIPPED_TYPES. Otherwise a record:
		{'question': exam YAML dict, 'answer': {'code', 'type', 'letters'},
		'rendered_images': opaque image references used until media files are saved,
		plus the parsed question and its table sources.
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
	if question_type in SKIPPED_TYPES and not handout:
		return None
	code, statement_html = ef_tools.bbq_html.split_question_code(parts[1])
	question_code = code or "without question code"
	ef_tools.bbq_html.validate_authored_question_html(
		parts[1:], f'question {question_code}')
	rendered_images = {}
	if math_renderer is not None or '<img' in line:
		parts = ef_tools.bbq_media.prepare_fields(
			parts, math_renderer, rendered_images, base_url, f'question {question_code}')
		code, statement_html = ef_tools.bbq_html.split_question_code(parts[1])
	if question_type in ('MC', 'MA'):
		question, letters, choice_tables, prompt_tables = _parse_mc(
			parts, rendered_images, question_code, math_renderer)
	elif question_type == 'MAT':
		question, letters, choice_tables, prompt_tables = _parse_mat(
			parts, rendered_images, question_code, math_renderer)
	elif question_type == 'ORD':
		question, letters, choice_tables, prompt_tables = _parse_ord(
			parts, rendered_images, question_code, math_renderer)
	elif question_type in SKIPPED_TYPES and handout:
		question, answer_text = _parse_handout_blank(parts, question_type)
		letters = []
		choice_tables = {}
		prompt_tables = {}
	else:
		raise ValueError(f"unknown bbq question type: {question_type!r}")
	statement = ef_tools.bbq_html.clean_statement_content(statement_html)
	if question_type == 'FIB_PLUS' and handout:
		for block in statement:
			if 'text' in block:
				block['text'] = re.sub(r'\[[^]]+\]', '____________________', block['text'])
	elif question_type in ('NUM', 'FIB') and handout:
		_append_handout_blank(statement)
	# Keep the original BBQ kind in the printable YAML question. Renderers can
	# then apply an explicitly type-scoped paper treatment without inferring a
	# question kind from its prose.
	question = {'statement': statement, 'question_type': question_type, **question}
	record = {
		'question': question,
		'answer': {'code': code, 'type': question_type, 'letters': letters,
			'answer_text': answer_text if question_type in SKIPPED_TYPES else ''},
		'choice_tables': choice_tables,
		'prompt_tables': prompt_tables,
		'rendered_images': rendered_images,
	}
	return record


#============================================
def attach_table_images(record: dict, statement_paths: list, choice_paths: dict,
		prompt_paths: dict = None) -> None:
	"""Fill image paths into a parsed record's question, in place.

	Args:
		record: Output of parse_bbq_line.
		statement_paths: Image paths for record['statement_tables'], in order.
		choice_paths: index -> [image path] for record['choice_tables'].
		prompt_paths: index -> [image path] for record['prompt_tables']
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
		block['html_table'] = ef_tools.bbq_media.clean_table_source(block['html_table'])
	# choice_paths is keyed by the original bbq choice index; for shuffled
	# matching lists the answer letters recover the printed position
	for index, paths in choice_paths.items():
		if len(paths) != 1:
			raise ValueError(f"choice {index} has {len(paths)} tables; one image per choice")
		target = _choice_dict_for_index(record, index)
		target['image'] = paths[0]
		target['html_table'] = ef_tools.bbq_media.clean_table_source(
			record['choice_tables'][index][0])
	for index, paths in (prompt_paths or {}).items():
		if len(paths) != 1:
			raise ValueError(f"prompt {index} has {len(paths)} tables; one image per prompt")
		question['prompts_list'][index]['image'] = paths[0]
		question['prompts_list'][index]['html_table'] = ef_tools.bbq_media.clean_table_source(
			record['prompt_tables'][index][0])


#============================================
def has_tables(record: dict) -> bool:
	"""Return whether a parsed record carries any drawing table."""
	statement = record['question']['statement']
	found = bool(any('html_table' in block for block in statement)
		or record['choice_tables'] or record['prompt_tables'])
	return found


#============================================
def has_rendered_images(record: dict) -> bool:
	"""Return whether the parsed record contains generated image bytes."""
	found = bool(record['rendered_images'])
	return found


#============================================
def render_record_tables(record: dict, renderer: object, media_dir: str, stem: str) -> None:
	"""Save generated images, capture tables, and attach image paths in place.

	Args:
		record: Output of parse_bbq_line.
		renderer: Shared native HTML renderer.
		media_dir: `<yaml_dir>/<stem>_files` directory for captured images.
		stem: Filename stem for this question (its CRC code).
	"""
	image_store = record['rendered_images']
	saved_images = {}
	yaml_dir = os.path.dirname(os.path.abspath(media_dir))
	safe_stem = ''.join(
		character if character.isalnum() or character in '_-' else '_'
		for character in stem)
	for block_index, block in enumerate(record['question']['statement'], start=1):
		image_ref = block.get('image')
		if isinstance(image_ref, str) and ef_tools.bbq_html.is_rendered_image_ref(image_ref):
			basename = _rendered_image_basename(
				safe_stem, 'statement', block_index, image_ref)
			block['image'] = _save_rendered_image(
				image_ref, image_store, media_dir, yaml_dir, basename, saved_images)
	for field_name in ('choices', 'choices_list', 'prompts_list'):
		for index, item in enumerate(record['question'].get(field_name, []), start=1):
			if not isinstance(item, dict):
				continue
			image_ref = item.get('image')
			if isinstance(image_ref, str) and ef_tools.bbq_html.is_rendered_image_ref(image_ref):
				basename = _rendered_image_basename(
					safe_stem, field_name, index, image_ref)
				item['image'] = _save_rendered_image(
					image_ref, image_store, media_dir, yaml_dir, basename,
					saved_images)
	statement_table_html = [
		block['html_table'] for block in record['question']['statement']
		if 'html_table' in block]
	statement_paths = ef_tools.bbq_html.write_table_images(
		statement_table_html, renderer, media_dir, stem, image_store)
	choice_paths = {}
	for index, tables in record['choice_tables'].items():
		choice_paths[index] = ef_tools.bbq_html.write_table_images(
			tables, renderer, media_dir, f"{stem}_choice{index}", image_store)
	prompt_paths = {}
	for index, tables in record['prompt_tables'].items():
		prompt_paths[index] = ef_tools.bbq_html.write_table_images(
			tables, renderer, media_dir, f"{stem}_prompt{index}", image_store)
	attach_table_images(record, statement_paths, choice_paths, prompt_paths)
	record.pop('rendered_images', None)


#============================================
def _rendered_image_basename(stem: str, field_name: str, index: int,
			image_ref: str) -> str:
	"""Build an asset name that identifies generated equations and canvases."""
	basename = f"{stem}_{field_name}_{index}_image.png"
	return basename


#============================================
def _save_rendered_image(image_ref: str, image_store: dict, media_dir: str,
			yaml_dir: str, filename: str, saved_images: dict) -> str:
	"""Write one standalone generated image and return its YAML path."""
	key = image_ref[len(ef_tools.bbq_html.RENDERED_IMAGE_PREFIX):]
	if key in saved_images:
		return saved_images[key]
	if key not in image_store:
		raise ValueError(f"question refers to missing rendered image {key!r}")
	os.makedirs(media_dir, exist_ok=True)
	if ef_tools.svg_media.is_svg(image_store[key]):
		extension = 'svg'
	else:
		with PIL.Image.open(io.BytesIO(image_store[key])) as image:
			extension = image.format.lower()
	filename = os.path.splitext(filename)[0] + '.' + extension
	path = os.path.join(media_dir, filename)
	with open(path, 'wb') as handle:
		handle.write(image_store[key])
	relative_path = os.path.relpath(path, yaml_dir)
	saved_images[key] = relative_path
	return relative_path


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
		if answer['type'] in SKIPPED_TYPES:
			label = f"{number}. {answer['answer_text']}"
		elif span > 1:
			pairs = ' '.join(f"{number + i}={letter}" for i, letter in enumerate(letters))
			label = f"Q{number}-{number + span - 1}. {pairs}"
		else:
			label = f"{number}. {','.join(letters)}"
		lines.append(f"{label}   {answer['code']}   {source}")
		number += span
	key_text = '\n'.join(lines) + '\n'
	return key_text
