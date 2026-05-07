"""Tests for ef_tools.zip_grade ZipGrade compatibility validator.

Locks the severity matrix from docs/USAGE.md and the plan's section 7,
and the contracts on filter_exam, LineTrackingLoader, and format_report:

	- Line numbers are the primary identifier in reports.
	- FIXABLE and ERROR are both non-OK; filter_exam drops both.
	- filter_exam deep-copies and strips '__line__' markers.
"""

# Standard Library
import textwrap

# PIP3 modules
import yaml

# Local Repo Modules
import ef_tools.zip_grade


#============================================
def _exam_with_question(question: dict) -> dict:
	"""Wrap a single question in a minimal exam structure."""
	exam = {
		'title': 'Test',
		'date': '2026-05-07',
		'sections': [
			{'questions': [question]},
		],
	}
	return exam


#============================================
# Severity matrix tests (one per row of plan section 7)
#============================================
def test_severity_mc_five_choices_is_ok():
	"""5-choice MC fits A-E exactly; classified OK so no Issue emitted."""
	exam = _exam_with_question({
		'statement': 'Pick one.',
		'choices': ['a', 'b', 'c', 'd', 'e'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert issues == []


#============================================
def test_severity_mc_two_choices_is_ok():
	"""2-choice MC is the lower OK boundary."""
	exam = _exam_with_question({
		'statement': 'Pick one.',
		'choices': ['yes', 'no'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert issues == []


#============================================
def test_severity_mc_six_choices_is_fixable():
	"""6-choice MC is FIXABLE: one distractor over A-E, but tooling
	cannot pick which to remove (no answer key in this YAML schema)."""
	exam = _exam_with_question({
		'statement': 'Pick one.',
		'choices': ['a', 'b', 'c', 'd', 'e', 'f'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.FIXABLE
	assert issues[0].rule == 'mc_choices_count'


#============================================
def test_severity_mc_seven_choices_is_error():
	"""7+ choice MC is ERROR: not realistically reducible without rewrite."""
	exam = _exam_with_question({
		'statement': 'Pick one.',
		'choices': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'mc_choices_too_many'


#============================================
def test_severity_mc_one_choice_is_error():
	"""<2 choices is ERROR: not bubbleable."""
	exam = _exam_with_question({
		'statement': 'Pick one.',
		'choices': ['only'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'mc_choices_too_few'


#============================================
def test_severity_matching_five_choices_is_ok():
	"""Matching with 5 choices_list items is OK regardless of prompts_list size."""
	exam = _exam_with_question({
		'statement': 'Match.',
		'prompts_list': ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'],
		'choices_list': ['c1', 'c2', 'c3', 'c4', 'c5'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert issues == []


#============================================
def test_severity_matching_six_choices_is_fixable():
	"""Matching with 6 choices_list items is FIXABLE."""
	exam = _exam_with_question({
		'statement': 'Match.',
		'prompts_list': ['p1', 'p2'],
		'choices_list': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.FIXABLE
	assert issues[0].rule == 'matching_choices_count'


#============================================
def test_severity_matching_one_choice_is_error():
	"""Matching with <2 choices_list items is ERROR: not bubbleable."""
	exam = _exam_with_question({
		'statement': 'Match.',
		'prompts_list': ['p1', 'p2'],
		'choices_list': ['only'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'matching_choices_too_few'


#============================================
def test_severity_matching_seven_choices_is_error():
	"""Matching with 7+ choices_list items is ERROR."""
	exam = _exam_with_question({
		'statement': 'Match.',
		'prompts_list': ['p1', 'p2'],
		'choices_list': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'],
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'matching_choices_too_many'


#============================================
def test_severity_no_choices_no_prompts_is_error():
	"""Bare statement with no answer surface is ERROR (fill-in/hotspot)."""
	exam = _exam_with_question({
		'statement': 'Calculate the equilibrium constant.',
	})
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'no_answers'


#============================================
def test_severity_total_rows_overflow_is_error():
	"""Whole-exam row total >100 emits one ERROR with no question_number."""
	# 101 single-MC questions
	questions = [
		{'statement': f'Q{i}', 'choices': ['a', 'b', 'c', 'd']}
		for i in range(101)
	]
	exam = {
		'title': 'Big',
		'date': '2026-05-07',
		'sections': [{'questions': questions}],
	}
	issues = ef_tools.zip_grade.validate(exam)
	# all questions OK individually; only the whole-exam issue
	assert len(issues) == 1
	assert issues[0].severity is ef_tools.zip_grade.Severity.ERROR
	assert issues[0].rule == 'total_rows'
	assert issues[0].question_number is None
	assert issues[0].line_number is None


#============================================
# filter_exam contract tests
#============================================
def test_filter_drops_error_and_fixable_keeps_ok():
	"""filter_exam drops both severities; preserves OK questions."""
	exam = {
		'title': 'Mixed',
		'date': '2026-05-07',
		'sections': [
			{'questions': [
				{'statement': 'OK1', 'choices': ['a', 'b', 'c']},
				{'statement': 'FIX', 'choices': ['a', 'b', 'c', 'd', 'e', 'f']},
				{'statement': 'ERR', 'choices': ['a', 'b', 'c', 'd', 'e', 'f', 'g']},
				{'statement': 'OK2', 'choices': ['x', 'y']},
			]},
		],
	}
	filtered, issues = ef_tools.zip_grade.filter_exam(exam)
	kept = filtered['sections'][0]['questions']
	assert len(kept) == 2
	assert kept[0]['statement'] == 'OK1'
	assert kept[1]['statement'] == 'OK2'
	# two non-OK issues reported
	assert len(issues) == 2


#============================================
def test_filter_strips_line_markers_recursively():
	"""filter_exam removes every '__line__' key it copies in."""
	yaml_text = textwrap.dedent('''
		title: Test
		date: 2026-05-07
		sections:
		  - questions:
		      - statement: Pick one
		        choices:
		          - a
		          - b
		          - c
		''').strip()
	# LineTrackingLoader extends yaml.SafeLoader, so this is safe
	exam = yaml.load(yaml_text, Loader=ef_tools.zip_grade.LineTrackingLoader)  # nosec B506
	# loader injected at least one __line__
	assert '__line__' in exam
	filtered, _ = ef_tools.zip_grade.filter_exam(exam)
	# walk filtered and confirm no __line__ anywhere
	def _has_line_marker(node):
		if isinstance(node, dict):
			if '__line__' in node:
				return True
			return any(_has_line_marker(v) for v in node.values())
		if isinstance(node, list):
			return any(_has_line_marker(item) for item in node)
		return False
	assert not _has_line_marker(filtered)


#============================================
def test_filter_preserves_section_structure():
	"""Empty sections are kept after all questions are dropped."""
	exam = {
		'title': 'AllBad',
		'date': '2026-05-07',
		'sections': [
			{'heading': 'Section A', 'questions': [
				{'statement': 'BAD', 'choices': ['a']},
			]},
			{'heading': 'Section B', 'questions': [
				{'statement': 'OK', 'choices': ['a', 'b']},
			]},
		],
	}
	filtered, _ = ef_tools.zip_grade.filter_exam(exam)
	# both sections still present, even though section A is empty
	assert len(filtered['sections']) == 2
	assert filtered['sections'][0]['questions'] == []
	assert len(filtered['sections'][1]['questions']) == 1


#============================================
def test_filter_skips_inline_chapter_pseudo_questions():
	"""Inline chapter dicts (chapter without statement) are kept and not classified."""
	exam = {
		'title': 'Chapters',
		'date': '2026-05-07',
		'sections': [
			{'questions': [
				{'chapter': 'Chapter 1'},
				{'statement': 'OK', 'choices': ['a', 'b']},
			]},
		],
	}
	filtered, issues = ef_tools.zip_grade.filter_exam(exam)
	# inline chapter retained alongside the OK question
	assert len(filtered['sections'][0]['questions']) == 2
	assert filtered['sections'][0]['questions'][0] == {'chapter': 'Chapter 1'}
	assert issues == []


#============================================
# LineTrackingLoader and format_report tests
#============================================
def test_line_tracking_loader_attaches_line_numbers():
	"""LineTrackingLoader injects a 1-based __line__ on every mapping."""
	yaml_text = textwrap.dedent('''
		title: Test
		date: 2026-05-07
		sections:
		  - questions:
		      - statement: Pick one
		        choices:
		          - a
		          - b
		''').strip()
	# LineTrackingLoader extends yaml.SafeLoader, so this is safe
	exam = yaml.load(yaml_text, Loader=ef_tools.zip_grade.LineTrackingLoader)  # nosec B506
	# the question dict starts on a known line in the source; we only
	# care that __line__ is present and positive, not the exact value
	# (asserting on a specific line number would be fragile to fixture
	# reformatting)
	question = exam['sections'][0]['questions'][0]
	assert '__line__' in question
	assert question['__line__'] is not None
	assert question['__line__'] > 0


#============================================
def test_validate_uses_line_numbers_from_loader():
	"""validate() reads __line__ from each question into Issue.line_number."""
	yaml_text = textwrap.dedent('''
		title: Test
		date: 2026-05-07
		sections:
		  - questions:
		      - statement: Bad question
		        choices:
		          - only
		''').strip()
	# LineTrackingLoader extends yaml.SafeLoader, so this is safe
	exam = yaml.load(yaml_text, Loader=ef_tools.zip_grade.LineTrackingLoader)  # nosec B506
	issues = ef_tools.zip_grade.validate(exam)
	assert len(issues) == 1
	# only assert presence and positivity, not a specific line number,
	# so the test does not break when the fixture is reformatted
	assert issues[0].line_number is not None
	assert issues[0].line_number > 0


#============================================
def test_format_report_uses_path_line_prefix():
	"""format_report puts <path>:<line> at the start when source_path is given."""
	issue = ef_tools.zip_grade.Issue(
		severity=ef_tools.zip_grade.Severity.FIXABLE,
		line_number=142,
		question_number=12,
		span=1,
		rule='mc_choices_count',
		message='6 choices (ZipGrade supports A-E only)',
		statement_excerpt='Which of the following...',
	)
	report = ef_tools.zip_grade.format_report([issue], source_path='exam.yml')
	first_line = report.splitlines()[0]
	assert first_line.startswith('exam.yml:142')
	assert '[FIXABLE]' in first_line
	assert '(Q12)' in first_line


#============================================
def test_format_report_falls_back_to_line_only():
	"""When source_path is None, prefix becomes '(line N)' so output stays line-anchored."""
	issue = ef_tools.zip_grade.Issue(
		severity=ef_tools.zip_grade.Severity.ERROR,
		line_number=200,
		question_number=17,
		span=1,
		rule='no_answers',
		message='no choices and no prompts_list',
	)
	report = ef_tools.zip_grade.format_report([issue], source_path=None)
	assert report.startswith('(line 200)')
	assert '[ERROR]' in report
	assert '(Q17)' in report


#============================================
def test_format_report_whole_exam_issue_has_no_q_label():
	"""Whole-exam issues render without a (Qn) hint."""
	issue = ef_tools.zip_grade.Issue(
		severity=ef_tools.zip_grade.Severity.ERROR,
		line_number=None,
		question_number=None,
		span=4,
		rule='total_rows',
		message='104 numbered rows total (max 100 for ZipGrade form)',
	)
	report = ef_tools.zip_grade.format_report([issue])
	# no '(Q' Q-label hint
	assert '(Q' not in report
	assert '[ERROR]' in report
	assert 'total' in report


#============================================
def test_format_report_empty_when_no_issues():
	"""Clean exam returns empty string."""
	report = ef_tools.zip_grade.format_report([])
	assert report == ''
