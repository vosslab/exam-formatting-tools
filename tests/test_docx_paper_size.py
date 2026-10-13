"""Paper switching must preserve typography and respect the printable width."""

import docx
import pytest

import yaml_to_exam_docx
import ef_tools.style_loader


@pytest.mark.parametrize('paper_size,width,height', [
	('letter', 8.5, 11.0), ('a4', 210 / 25.4, 297 / 25.4),
])
def test_document_paper_size(tmp_path: object, paper_size: str,
		width: float, height: float) -> None:
	"""A paper change sets real page geometry while retaining the authored theme."""
	data = {'title': 'Exam', 'sections': []}
	path = tmp_path / f'{paper_size}.docx'
	yaml_to_exam_docx.build_document(data, str(path), paper_size=paper_size)
	document = docx.Document(path)
	section = document.sections[0]
	assert section.page_width.inches == pytest.approx(width, abs=0.001)
	assert section.page_height.inches == pytest.approx(height, abs=0.001)
	usable = section.page_width - section.left_margin - section.right_margin
	tabs = document.styles['Header'].paragraph_format.tab_stops
	assert tabs[-1].position == pytest.approx(usable, abs=1000)
	styles = ef_tools.style_loader.load_styles()
	assert document.styles['Normal'].font.size.pt == styles['sizes']['normal']
	assert document.styles['Normal'].font.name == styles['fonts']['primary']
	assert 'width' not in styles['page']
