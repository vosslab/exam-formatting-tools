#!/usr/bin/env python3
"""Empirical measurement tool for image-choice column sizing.

Generates noise PNG choice images, builds a one-question-per-col-count
exam DOCX through the production pipeline, converts each page to PNG via
LibreOffice + ImageMagick, and prints a per-cols table comparing each
rendered image's right edge to its target tab stop.

Use this whenever IMAGE_CHOICE_MAX_WIDTH_BY_COLS, layout_tab_stops,
choice_indent, or inline-image margin handling changes. The dead-space
column shows how close each image sits to the next tab stop, which is
the lever the user cares about.

Run with:
	source source_me.sh && python3 tools/measure_image_choices.py
"""

# Standard Library
import os
import sys
import shutil
import argparse
import subprocess

# PIP3 modules
import yaml
import numpy
import PIL.Image
import docx

# determine repo root from git so this tool runs from any CWD
REPO_ROOT = subprocess.check_output(
	['git', 'rev-parse', '--show-toplevel'], text=True).strip()
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

# local repo modules

import yaml_to_exam_docx
import ef_tools.style_loader

# OOXML drawing namespace; <wp:ext> carries image extent in EMU.
WP_DRAWING_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
EMU_PER_INCH = 914400.0


#============================================
def parse_args():
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Render image-choice rows for cols 2-5 and report dead space.")
	parser.add_argument('-o', '--output-dir', dest='output_dir',
		default='image_choice_measure',
		help="Directory for generated images, YAML, DOCX, PDF, PNG output.")
	parser.add_argument('-k', '--keep', dest='keep', action='store_true',
		help="Keep the output directory contents (do not clear before run).")
	return parser.parse_args()


#============================================
def make_noise_png(path: str, pixel_size: tuple) -> None:
	"""Write a square-ish noise PNG of the given pixel size to path."""
	# random RGB noise so each image is visually distinct
	width, height = pixel_size
	data = numpy.random.randint(0, 256, size=(height, width, 3), dtype=numpy.uint8)
	image = PIL.Image.fromarray(data, mode='RGB')
	image.save(path)


#============================================
def build_exam_yaml(image_paths_by_cols: dict) -> dict:
	"""Build the in-memory exam dict with one question per col count."""
	questions = []
	for num_cols in sorted(image_paths_by_cols):
		image_paths = image_paths_by_cols[num_cols]
		choices = [{'text': '', 'image': path} for path in image_paths]
		question = {
			'statement': f"Cols={num_cols}: identify the rightmost noise tile.",
			'choices': choices,
			'answer': 'A',
		}
		questions.append(question)
	exam = {
		'title': 'image_choice_measure',
		'sections': [
			{'heading': 'Image choice sizing test', 'questions': questions},
		],
	}
	return exam


#============================================
def render_docx_to_pngs(docx_path: str, output_dir: str) -> list:
	"""Convert docx -> pdf -> per-page PNGs; return list of png paths."""
	subprocess.run(
		['soffice', '--headless', '--convert-to', 'pdf',
			'--outdir', output_dir, docx_path],
		check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
	)
	pdf_path = os.path.join(output_dir,
		os.path.splitext(os.path.basename(docx_path))[0] + '.pdf')
	# magick splits multipage PDFs into <stem>-N.png
	png_stem = os.path.join(output_dir, 'page')
	subprocess.run(
		['magick', '-density', '150', pdf_path, png_stem + '.png'],
		check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
	)
	# collect produced pngs (single-page case has no -N suffix)
	pngs = sorted(
		path for path in os.listdir(output_dir)
		if path.startswith('page') and path.endswith('.png')
	)
	return [os.path.join(output_dir, name) for name in pngs]


#============================================
def measure_image_widths(docx_path: str) -> list:
	"""Return rendered image widths in inches, in document order."""
	# python-docx exposes inline pictures via the underlying XML; iterate
	# every <wp:inline> and read its <wp:extent cx=...> attribute
	document = docx.Document(docx_path)
	widths = []
	for paragraph in document.paragraphs:
		for inline in paragraph._p.iter('{%s}inline' % WP_DRAWING_NS):
			extent = inline.find('{%s}extent' % WP_DRAWING_NS)
			if extent is None:
				continue
			emu = int(extent.get('cx'))
			widths.append(emu / EMU_PER_INCH)
	return widths


#============================================
def load_tab_stops() -> dict:
	"""Read layout_tab_stops from the styles file; return {cols: [stops]}."""
	styles = ef_tools.style_loader.load_styles()
	return styles['layout_tab_stops']


#============================================
def load_choice_indent() -> float:
	"""Read choice_indent in inches from the styles file."""
	styles = ef_tools.style_loader.load_styles()
	return styles['spacing']['choice_indent']


#============================================
def build_summary(image_widths_by_cols: dict, tab_stops: dict,
	choice_indent: float, prefix_width_estimate: float = 0.25) -> str:
	"""Build a printable table comparing rendered widths to tab gaps.

	prefix_width_estimate: rough width of the bold "(A)" run preceding
	each image; used only to estimate dead space, not enforced.
	"""
	lines = []
	header = (
		f"{'cols':>4}  {'col_gap':>8}  {'img_w':>7}  "
		f"{'prefix':>7}  {'cursor':>7}  {'next_stop':>9}  {'dead':>6}"
	)
	lines.append(header)
	lines.append('-' * len(header))
	for num_cols in sorted(image_widths_by_cols):
		widths = image_widths_by_cols[num_cols]
		stops = tab_stops[num_cols]
		# inter-column gap for cols 1..N-1 is uniform; build a list of
		# starting x positions for each column: choice_indent, then each
		# tab stop in turn (last column has no following stop)
		column_starts = [choice_indent] + list(stops)
		for col_index, image_width in enumerate(widths):
			start_x = column_starts[col_index]
			# cursor advances: prefix run + image; OOXML inline margins are
			# zeroed in production, so image consumes exactly image_width
			cursor_x = start_x + prefix_width_estimate + image_width
			if col_index < len(stops):
				next_stop = stops[col_index]
				dead = next_stop - cursor_x
				next_stop_str = f"{next_stop:.3f}"
			else:
				# last column: no next stop, dead space is to right page edge
				next_stop = None
				dead = float('nan')
				next_stop_str = '   --   '
			gap_inches = (column_starts[col_index + 1] - start_x
				if col_index + 1 < len(column_starts) else float('nan'))
			gap_str = f"{gap_inches:.3f}" if gap_inches == gap_inches else '  --  '
			dead_str = f"{dead:+.3f}" if dead == dead else '  --  '
			tag = f"{num_cols}c[{col_index}]"
			line = (
				f"{tag:>4}  {gap_str:>8}  {image_width:.3f}  "
				f"{prefix_width_estimate:7.3f}  {cursor_x:7.3f}  "
				f"{next_stop_str:>9}  {dead_str:>6}"
			)
			lines.append(line)
	return '\n'.join(lines)


#============================================
def main():
	"""Generate noise images, render docx, report dead space per column."""
	args = parse_args()
	output_dir = args.output_dir
	# clear or create output directory
	if os.path.isdir(output_dir) and not args.keep:
		shutil.rmtree(output_dir)
	os.makedirs(output_dir, exist_ok=True)
	# generate noise images: one set per col count, square 300x300 px
	image_paths_by_cols = {}
	for num_cols in (2, 3, 4, 5):
		paths = []
		for index in range(num_cols):
			path = os.path.join(output_dir, f"noise_{num_cols}c_{index}.png")
			# 2:1 aspect roughly matches real chemistry/curve choices and
			# keeps the rendered width binding (not the max-height clamp)
			make_noise_png(path, (600, 300))
			paths.append(path)
		image_paths_by_cols[num_cols] = paths
	# write exam yaml (kept on disk for inspection)
	exam_data = build_exam_yaml(image_paths_by_cols)
	yaml_path = os.path.join(output_dir, 'measure.yaml')
	with open(yaml_path, 'w', encoding='utf-8') as handle:
		yaml.safe_dump(exam_data, handle, sort_keys=False)
	# build docx through the production pipeline
	docx_path = os.path.join(output_dir, 'measure.docx')
	yaml_to_exam_docx.build_document(exam_data, docx_path)
	# render to inspectable PNG pages
	png_paths = render_docx_to_pngs(docx_path, output_dir)
	# measure rendered image widths and group by col count, in order
	all_widths = measure_image_widths(docx_path)
	image_widths_by_cols = {}
	cursor = 0
	for num_cols in (2, 3, 4, 5):
		image_widths_by_cols[num_cols] = all_widths[cursor:cursor + num_cols]
		cursor += num_cols
	# print summary table
	tab_stops = load_tab_stops()
	choice_indent = load_choice_indent()
	summary = build_summary(image_widths_by_cols, tab_stops, choice_indent)
	print(summary)
	print('')
	print(f"docx: {docx_path}")
	print(f"yaml: {yaml_path}")
	for png_path in png_paths:
		print(f"page: {png_path}")


if __name__ == '__main__':
	main()
