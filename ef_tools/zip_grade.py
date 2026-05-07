"""ZipGrade compatibility classification for exam YAML.

ZipGrade 100-question bubble forms support exactly five lettered options
per row (A-E) for up to 100 numbered rows. This module classifies each
exam question as OK, FIXABLE, or ERROR and provides:

	- Severity enum: OK / FIXABLE / ERROR
	- Issue dataclass for one violation
	- LineTrackingLoader: yaml.SafeLoader subclass attaching '__line__'
	  (1-based) to every constructed mapping
	- validate(exam_data) -> list[Issue]
	- filter_exam(exam_data) -> tuple[dict, list[Issue]]
	- format_report(issues, source_path=None) -> str

Both downstream consumers (the validate_zipgrade_yaml.py linter and the
--zip-grade flag on yaml_to_exam_docx.py) call into this module so rules
cannot drift between them.
"""

# Standard Library
import copy
import enum
import dataclasses

# PIP3 modules
import yaml


# ZipGrade form constants
MAX_CHOICES = 5
MIN_CHOICES = 2
FIXABLE_CHOICES = 6
MAX_TOTAL_ROWS = 100

# preview length for statement excerpts in reports
STATEMENT_PREVIEW_LEN = 60


#============================================
class Severity(enum.Enum):
	"""ZipGrade compatibility severity tiers."""
	OK = 'OK'
	FIXABLE = 'FIXABLE'
	ERROR = 'ERROR'


#============================================
@dataclasses.dataclass
class Issue:
	"""A single ZipGrade compatibility issue.

	Attributes:
		severity: OK, FIXABLE, or ERROR.
		line_number: 1-based YAML source line of the offending question
			mapping (None when the loader did not track lines, or for
			whole-exam issues like total-rows-overflow).
		question_number: First numbered row of the question (None for
			whole-exam issues).
		span: Number of rows the question consumes (1 for MC,
			len(prompts_list) for matching).
		rule: Short rule identifier; useful for tests.
		message: Human-readable description of the violation.
		statement_excerpt: First STATEMENT_PREVIEW_LEN chars of the
			question statement (empty for whole-exam issues).
	"""
	severity: Severity
	line_number: int = None
	question_number: int = None
	span: int = 1
	rule: str = ''
	message: str = ''
	statement_excerpt: str = ''

	#--------------------------------------------
	def label(self) -> str:
		"""Format the Q-number hint, e.g. 'Q12' or 'Q23-26'.

		Returns empty string for whole-exam issues without a question
		number. Q-labels are secondary hints in reports; line numbers are
		the stable identifier.
		"""
		if self.question_number is None:
			return ''
		if self.span > 1:
			end = self.question_number + self.span - 1
			label_text = f"Q{self.question_number}-{end}"
		else:
			label_text = f"Q{self.question_number}"
		return label_text


#============================================
class LineTrackingLoader(yaml.SafeLoader):
	"""SafeLoader subclass that tags every mapping with its source line.

	After loading, each dict carries '__line__' (1-based source-file line
	of the mapping's first key). The linter uses this to anchor reports to
	the YAML file. The filter strips '__line__' from the output.
	"""

	#--------------------------------------------
	def construct_mapping(self, node, deep=False):
		mapping = super().construct_mapping(node, deep=deep)
		# node.start_mark.line is 0-based; humans want 1-based
		mapping['__line__'] = node.start_mark.line + 1
		return mapping


#============================================
def _statement_excerpt(question: dict) -> str:
	"""Return up to STATEMENT_PREVIEW_LEN chars of the question statement."""
	statement = question.get('statement', '')
	if not isinstance(statement, str):
		return ''
	# collapse whitespace so YAML newlines don't break the preview
	cleaned = ' '.join(statement.split())
	if len(cleaned) <= STATEMENT_PREVIEW_LEN:
		return cleaned
	preview = cleaned[:STATEMENT_PREVIEW_LEN] + '...'
	return preview


#============================================
def _question_span(question: dict) -> int:
	"""Number of numbered rows consumed by the question.

	Mirrors the question_span logic in yaml_to_exam_docx.py:193-194 so the
	row-budget check matches what the DOCX builder will actually emit.
	"""
	prompts_list = question.get('prompts_list', None)
	if prompts_list:
		return max(1, len(prompts_list))
	return 1


#============================================
def _classify_question(question: dict) -> tuple:
	"""Classify a single question per the severity matrix.

	Returns (Severity, rule_id, message). For OK questions, rule_id and
	message are empty strings.
	"""
	choices = question.get('choices', None)
	prompts_list = question.get('prompts_list', None)
	choices_list = question.get('choices_list', None)
	# bubble-able question must have either MC choices or matching options
	has_mc = choices is not None and len(choices) > 0
	has_match = (prompts_list is not None and len(prompts_list) > 0
		and choices_list is not None and len(choices_list) > 0)
	if not has_mc and not has_match:
		return (Severity.ERROR, 'no_answers',
			"no choices and no prompts_list (not bubbleable on ZipGrade)")
	# matching takes precedence: prompts_list drives the bubbled rows, so
	# the constraint applies to choices_list
	if has_match:
		count = len(choices_list)
		if count < MIN_CHOICES:
			message = (f"{count} lettered choices_list items "
				f"(need at least {MIN_CHOICES} for ZipGrade)")
			return (Severity.ERROR, 'matching_choices_too_few', message)
		if count == FIXABLE_CHOICES:
			message = (f"{count} lettered choices_list items "
				f"(ZipGrade supports A-E only; remove one to fit)")
			return (Severity.FIXABLE, 'matching_choices_count', message)
		if count > MAX_CHOICES:
			message = (f"{count} lettered choices_list items "
				f"(ZipGrade supports A-E only; rewrite required)")
			return (Severity.ERROR, 'matching_choices_too_many', message)
		return (Severity.OK, '', '')
	# MC path
	count = len(choices)
	if count < MIN_CHOICES:
		message = (f"{count} choices "
			f"(need at least {MIN_CHOICES} for ZipGrade)")
		return (Severity.ERROR, 'mc_choices_too_few', message)
	if count == FIXABLE_CHOICES:
		message = (f"{count} choices "
			f"(ZipGrade supports A-E only; remove one distractor to fit)")
		return (Severity.FIXABLE, 'mc_choices_count', message)
	if count > MAX_CHOICES:
		message = (f"{count} choices "
			f"(ZipGrade supports A-E only; rewrite required)")
		return (Severity.ERROR, 'mc_choices_too_many', message)
	return (Severity.OK, '', '')


#============================================
def _iter_questions(exam_data: dict):
	"""Yield (section_index, question_index, question) for real questions.

	Skips inline-chapter pseudo-questions (a dict with 'chapter' but no
	'statement'), matching the skip rule in yaml_to_exam_docx.py:169-175.
	"""
	sections = exam_data.get('sections', [])
	for section_index, section_data in enumerate(sections):
		questions = section_data.get('questions', [])
		for question_index, question in enumerate(questions):
			# inline chapter heading is not a real question
			if 'chapter' in question and 'statement' not in question:
				continue
			yield section_index, question_index, question


#============================================
def validate(exam_data: dict) -> list:
	"""Return a list of Issue objects for every ZipGrade violation.

	Walks the exam, assigns running question numbers exactly the way
	yaml_to_exam_docx.build_document does (including matching span and
	the optional 'number' override), runs the per-question classifier,
	then performs the whole-exam total-rows check.

	OK questions produce no Issue. FIXABLE and ERROR questions each
	produce one Issue. Whole-exam total-rows-overflow produces one ERROR
	Issue with line_number=None and question_number=None.

	Args:
		exam_data: Parsed exam YAML (dict).

	Returns:
		List of Issue objects. Empty list means the exam is fully
		ZipGrade-compatible (no FIXABLE, no ERROR, row total <= 100).
	"""
	issues = []
	question_counter = 1
	total_rows = 0
	for _, _, question in _iter_questions(exam_data):
		# explicit number override mirrors builder behavior
		if 'number' in question:
			question_counter = question['number']
		span = _question_span(question)
		severity, rule_id, message = _classify_question(question)
		if severity is not Severity.OK:
			issue = Issue(
				severity=severity,
				line_number=question.get('__line__', None),
				question_number=question_counter,
				span=span,
				rule=rule_id,
				message=message,
				statement_excerpt=_statement_excerpt(question),
			)
			issues.append(issue)
		total_rows += span
		question_counter += span
	# whole-exam row budget
	if total_rows > MAX_TOTAL_ROWS:
		overflow_message = (f"{total_rows} numbered rows total "
			f"(max {MAX_TOTAL_ROWS} for ZipGrade form)")
		issue = Issue(
			severity=Severity.ERROR,
			line_number=None,
			question_number=None,
			span=total_rows - MAX_TOTAL_ROWS,
			rule='total_rows',
			message=overflow_message,
			statement_excerpt='',
		)
		issues.append(issue)
	return issues


#============================================
def _strip_line_markers(node) -> None:
	"""Recursively delete '__line__' keys added by LineTrackingLoader."""
	if isinstance(node, dict):
		# pop the marker if present
		if '__line__' in node:
			del node['__line__']
		# recurse into values
		for value in node.values():
			_strip_line_markers(value)
	elif isinstance(node, list):
		for item in node:
			_strip_line_markers(item)


#============================================
def filter_exam(exam_data: dict) -> tuple:
	"""Return (filtered_exam, issues): exam with non-OK questions removed.

	Drops both ERROR and FIXABLE questions per the contract -- a 6-choice
	question is not safe to truncate automatically, so it is excluded
	unless the YAML is edited by hand. Sections are preserved (even if
	their questions list ends up empty); inline-chapter pseudo-questions
	are kept. The whole-exam total-rows-overflow issue is reported but
	NOT auto-trimmed -- the DOCX flag treats post-filter overflow as a
	WARNING and still builds, while the linter treats it as ERROR.

	Args:
		exam_data: Parsed exam YAML (dict).

	Returns:
		Tuple of (new exam dict, list[Issue]). The original dict is not
		modified. The returned dict has all '__line__' keys stripped.
	"""
	# run validate once to get the issue list
	issues = validate(exam_data)
	# determine which (section, question) tuples to drop by re-walking
	# with the same numbering so we can match issues to indices
	drop_set = set()
	question_counter = 1
	for section_index, question_index, question in _iter_questions(exam_data):
		if 'number' in question:
			question_counter = question['number']
		span = _question_span(question)
		severity, _, _ = _classify_question(question)
		if severity is not Severity.OK:
			drop_set.add((section_index, question_index))
		question_counter += span
	# deep-copy so the original exam_data is untouched
	filtered = copy.deepcopy(exam_data)
	sections = filtered.get('sections', [])
	for section_index, section_data in enumerate(sections):
		questions = section_data.get('questions', [])
		kept = []
		for question_index, question in enumerate(questions):
			if (section_index, question_index) in drop_set:
				continue
			kept.append(question)
		section_data['questions'] = kept
	# strip __line__ keys recursively from the filtered output
	_strip_line_markers(filtered)
	return filtered, issues


#============================================
def filtered_total_rows(filtered_exam: dict) -> int:
	"""Count total numbered rows in a filtered exam.

	Used by the DOCX flag to detect post-filter overflow (>100 rows still
	remaining after dropping non-OK questions).
	"""
	total = 0
	for _, _, question in _iter_questions(filtered_exam):
		total += _question_span(question)
	return total


#============================================
def format_report(issues: list, source_path: str = None) -> str:
	"""Format the issue list as a multi-line line-anchored report.

	Per-question issues render as:

		<source_path>:<line> [SEVERITY] (Qlabel) <message>
		                                "<statement excerpt>"

	When source_path is None, the prefix becomes '(line N)' so the report
	stays line-anchored. Whole-exam issues (no line number, no question
	number) render as a single '[SEVERITY] <message>' line.

	Issues are emitted in the order produced by validate(): per-question
	issues first (in document order), then any whole-exam issues at the
	bottom.

	Args:
		issues: List from validate().
		source_path: Optional source file path for the prefix.

	Returns:
		Multi-line report string. Empty string when issues is empty.
	"""
	if not issues:
		return ''
	lines_out = []
	for issue in issues:
		# whole-exam issues have no question_number
		if issue.question_number is None:
			lines_out.append(f"[{issue.severity.value}] {issue.message}")
			continue
		# per-question issue: build line-anchored prefix
		if issue.line_number is not None:
			if source_path is not None:
				prefix = f"{source_path}:{issue.line_number}"
			else:
				prefix = f"(line {issue.line_number})"
		else:
			# loader did not track lines; fall back to source_path or empty
			if source_path is not None:
				prefix = source_path
			else:
				prefix = '(no line)'
		label = issue.label()
		head = f"{prefix} [{issue.severity.value}] ({label}) {issue.message}"
		lines_out.append(head)
		if issue.statement_excerpt:
			# indent the excerpt under the head line for readability
			lines_out.append(f'    "{issue.statement_excerpt}"')
	report = '\n'.join(lines_out)
	return report
