"""Operations for the ordered statement blocks in exam YAML."""


#============================================
def text_block(text: str) -> dict:
	"""Create one statement text block."""
	return {'text': text}


#============================================
def append_text(statement: list, text: str) -> None:
	"""Append text, joining it to the previous text block when possible."""
	if not text:
		return
	if statement and 'text' in statement[-1]:
		statement[-1]['text'] += text
	else:
		statement.append(text_block(text))


#============================================
def text_content(statement: list) -> str:
	"""Return statement prose in block order, omitting drawings and tables."""
	content = '\n'.join(block['text'] for block in statement if 'text' in block)
	return content


#============================================
def validate(statement: list) -> None:
	"""Reject statement blocks that do not match the canonical YAML schema."""
	if not isinstance(statement, list):
		raise TypeError("Question 'statement' must be an ordered list of content blocks")
	if not statement:
		raise ValueError("Question 'statement' must contain at least one content block")
	for index, block in enumerate(statement):
		if not isinstance(block, dict):
			raise TypeError(f"Statement block {index} must be a mapping")
		keys = set(block)
		if keys == {'text'} and isinstance(block['text'], str) and block['text'].strip():
			continue
		if keys in ({'image'}, {'image', 'html_table'}):
			if not isinstance(block['image'], str) or not block['image'].strip():
				raise ValueError(f"Statement block {index} image must be a non-empty path string")
			if 'html_table' in block and not isinstance(block['html_table'], str):
				raise TypeError(f"Statement block {index} html_table must be a string")
			continue
		if keys == {'table'}:
			table = block['table']
			if not isinstance(table, dict) or set(table) != {'columns', 'rows'}:
				raise ValueError(
					f"Statement block {index} table must contain only columns and rows")
			columns = table['columns']
			rows = table['rows']
			if (not isinstance(columns, list) or not columns
					or not all(isinstance(column, str) for column in columns)):
				raise ValueError(
					f"Statement block {index} table columns must be a non-empty list of strings")
			if (not isinstance(rows, list)
					or any(not isinstance(row, list) or len(row) != len(columns)
						or not all(isinstance(cell, str) for cell in row)
						for row in rows)):
				raise ValueError(
					f"Statement block {index} table rows must match the column count")
			continue
		raise ValueError(f"Statement block {index} has invalid fields: {sorted(keys)}")
