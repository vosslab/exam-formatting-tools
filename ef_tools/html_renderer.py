"""Render HTML elements as SVG, using PNG for canvas drawings and SVG export failures."""

# Standard Library
import io
import html as html_module
import math
import os
import pathlib
import shutil
import subprocess
import tempfile
import warnings

# PIP3 modules
import PIL.Image
import PIL.ImageChops
import lxml.etree
import playwright.sync_api

# Local Repo Modules
import ef_tools.svg_media
import ef_tools.style_loader


CSS_PIXELS_PER_INCH = 96
PRINT_DPI = 600


#============================================
def _base_href(base_url: str) -> str:
	"""Return a URL suitable for an HTML base element."""
	if not base_url:
		return ''
	if '://' in base_url or base_url.startswith('data:'):
		return base_url
	path = pathlib.Path(base_url).expanduser().resolve()
	if path.is_file():
		path = path.parent
	base_href = path.as_uri()
	if not base_href.endswith('/'):
		base_href += '/'
	return base_href


#============================================
def _document_html(html: str, base_url: str) -> str:
	"""Wrap an HTML fragment with the assessment font and optional base URL."""
	styles = ef_tools.style_loader.load_styles()
	fonts = styles['fonts']
	base_href = _base_href(base_url)
	# ASVS 1.2.1: HTML-escape the source-controlled resource base before it
	# enters the wrapper document. The authored fragment intentionally remains
	# executable because its canvas scripts are the content being rendered.
	quoted_base = html_module.escape(base_href, quote=True)
	font_style = (
		'<style>'
		f'body {{ margin: 0; background: white; font-family: "{fonts["primary"]}", sans-serif; }}'
		f'table {{ font-family: "{fonts["primary"]}", sans-serif; }}'
		'table [style*="monospace" i], table code, table tt '
		f'{{ font-family: "{fonts["monospace"]}", monospace !important; }}'
		'</style>')
	document = (
		'<!doctype html><html><head>'
		f'<base href="{quoted_base}">{font_style}'
		f'</head><body>{html}</body></html>')
	return document


#============================================
def _flatten_on_white(image: PIL.Image.Image) -> PIL.Image.Image:
	"""Return image composited over white as RGB."""
	if image.mode == 'RGB':
		return image
	rgba = image.convert('RGBA')
	backdrop = PIL.Image.new('RGBA', rgba.size, (255, 255, 255, 255))
	flattened = PIL.Image.alpha_composite(backdrop, rgba).convert('RGB')
	return flattened


#============================================
def _crop_table(image: PIL.Image.Image, bleed_px: int) -> PIL.Image.Image:
	"""Trim a white table margin while retaining one CSS pixel of border bleed."""
	flattened = _flatten_on_white(image)
	white = PIL.Image.new('RGB', flattened.size, 'white')
	difference = PIL.ImageChops.difference(flattened, white)
	bbox = difference.getbbox()
	if bbox is None:
		return flattened
	left, top, right, bottom = bbox
	left = max(0, left - bleed_px)
	top = max(0, top - bleed_px)
	right = min(flattened.width, right + bleed_px)
	bottom = min(flattened.height, bottom + bleed_px)
	cropped = flattened.crop((left, top, right, bottom))
	return cropped


#============================================
def _stamp_png(png_bytes: bytes, dpi: float, crop_table: bool) -> bytes:
	"""Write accurate PNG density metadata, optionally cropping a table."""
	with PIL.Image.open(io.BytesIO(png_bytes)) as image:
		if crop_table:
			image = _crop_table(image, math.ceil(dpi / CSS_PIXELS_PER_INCH))
		else:
			image = image.copy()
		output = io.BytesIO()
		image.save(output, format='PNG', dpi=(dpi, dpi))
	stamped = output.getvalue()
	return stamped


#============================================
class HtmlRenderer:
	"""Capture selected HTML elements with Chromium at their printed resolution.

	The renderer intentionally accepts valid browser HTML as-is. It captures
	visual content that DOCX cannot represent; it does not repair MathML or
	interpret JavaScript drawing data.
	"""

	#============================================
	def __init__(self) -> None:
		"""Initialize an unopened renderer."""
		self._playwright = None
		self._browser = None

	#============================================
	def __enter__(self) -> 'HtmlRenderer':
		"""Return the renderer; Chromium starts only when rendering begins."""
		return self

	#============================================
	def __exit__(self, exc_type: object, exc_value: object,
			exc_traceback: object) -> None:
		"""Close the browser and Playwright process."""
		if self._browser is not None:
			self._browser.close()
			self._browser = None
		if self._playwright is not None:
			self._playwright.stop()
			self._playwright = None

	#============================================
	def _browser_instance(self) -> playwright.sync_api.Browser:
		"""Start and return the single Chromium browser for this renderer."""
		if self._playwright is None:
			self._playwright = playwright.sync_api.sync_playwright().start()
		if self._browser is None:
			self._browser = self._playwright.chromium.launch()
		return self._browser

	#============================================
	def _new_page(self, scale: int) -> tuple:
		"""Create a page using one integer device scale factor."""
		browser = self._browser_instance()
		context = browser.new_context(device_scale_factor=scale)
		page = context.new_page()
		return context, page

	#============================================
	def _load_page(self, html: str, base_url: str, scale: int,
			label: str) -> tuple:
		"""Load one complete authored document and collect browser failures."""
		context, page = self._new_page(scale)
		script_errors = []
		resource_errors = []
		page.on('pageerror', lambda error: script_errors.append(str(error)))
		page.on('requestfailed', lambda request: resource_errors.append(
			f'{request.url}: {request.failure}'))
		page.on('response', lambda response: resource_errors.append(
			f'{response.url}: HTTP {response.status}') if response.status >= 400 else None)
		document = _document_html(html, base_url)
		file_descriptor, page_path = tempfile.mkstemp(suffix='.html', prefix='ef_tools_render_')
		with os.fdopen(file_descriptor, 'w', encoding='utf-8') as handle:
			handle.write(document)
		loaded = False
		try:
			# ASVS 1.2.3: authored scripts run only in this fresh, disposable
			# browser context. Rendering valid question HTML requires that behavior.
			page.goto(pathlib.Path(page_path).as_uri(), wait_until='load')
			page.evaluate('() => document.fonts.ready')
			if script_errors or resource_errors:
				details = '; '.join(script_errors + resource_errors)
				raise ValueError(f'{label}: browser could not render authored HTML: {details}')
			try:
				page.wait_for_function(
					'() => Array.from(document.images).every((image) => '
					'image.complete && image.naturalWidth > 0)')
			except playwright.sync_api.TimeoutError as exc:
				missing = page.evaluate(
					'() => Array.from(document.images).filter(image => '
					'!image.complete || !image.naturalWidth).map(image => image.src)')
				raise ValueError(
					f'{label}: image resource did not load: {missing}') from exc
			loaded = True
		finally:
			os.unlink(page_path)
			if not loaded:
				context.close()
		if script_errors or resource_errors:
			context.close()
			details = '; '.join(script_errors + resource_errors)
			raise ValueError(f'{label}: browser could not render authored HTML: {details}')
		return context, page

	#============================================
	def _target_measurements(self, page: playwright.sync_api.Page,
			targets: dict[str, float | None], label: str) -> dict[str, dict]:
		"""Measure target CSS widths and verify every requested selector exists."""
		measurements = {}
		for selector, width_inches in targets.items():
			locator = page.locator(selector)
			if locator.count() != 1:
				raise ValueError(
					f'{label}: selector {selector!r} matched {locator.count()} elements; expected 1')
			box = locator.bounding_box()
			if box is None or box['width'] <= 0 or box['height'] <= 0:
				raise ValueError(f'{label}: selector {selector!r} has no visible dimensions')
			measurements[selector] = box
		return measurements

	#============================================
	def _printed_width_inches(self, selector: str, target_width: float | None,
			measurements: dict[str, dict]) -> float:
		"""Return target placement width from a caller value or table style rule."""
		if target_width is not None:
			if target_width <= 0:
				raise ValueError(f'{selector}: intended printed width must be positive')
			return target_width
		styles = ef_tools.style_loader.load_styles()
		width_inches = measurements[selector]['width'] / CSS_PIXELS_PER_INCH
		printed_width = width_inches * styles['page']['table_image_scale']
		return printed_width

	#============================================
	def _capture_scales(self, targets: dict[str, float | None],
			measurements: dict[str, dict]) -> dict[int, dict[str, float | None]]:
		"""Group targets by the smallest scale that meets their print DPI."""
		groups = {}
		for selector, target_width in targets.items():
			printed_width = self._printed_width_inches(selector, target_width, measurements)
			css_width = measurements[selector]['width']
			scale = math.ceil(PRINT_DPI * printed_width / css_width)
			groups.setdefault(scale, {})[selector] = target_width
		return groups

	#============================================
	def _wait_for_canvases(self, page: playwright.sync_api.Page,
			targets: dict, label: str) -> None:
		"""Wait until captured 2D canvases contain a visible pixel."""
		predicate = '''(selectors) => selectors.flatMap((selector) =>
			Array.from(document.querySelectorAll(selector)).flatMap((element) =>
				element.matches('canvas') ? [element] : Array.from(element.querySelectorAll('canvas')))
		).every((canvas) => {
			const context = canvas.getContext('2d');
			if (!context) return true;
			const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
			for (let index = 3; index < pixels.length; index += 4) {
				if (pixels[index] !== 0) return true;
			}
			return false;
		})'''
		try:
			page.wait_for_function(predicate, arg=list(targets))
		except playwright.sync_api.TimeoutError as exc:
			raise ValueError(
				f'{label}: JavaScript canvas did not draw before the browser timeout') from exc

	#============================================
	def _canvas_only(self, page: playwright.sync_api.Page, selector: str) -> bool:
		"""Use PNG for canvas drawings; keep surrounding text and tables vector."""
		return page.locator(selector).evaluate('''(element) => {
			if (element.tagName === 'CANVAS') return true;
			const copy = element.cloneNode(true);
			copy.querySelectorAll('script, style').forEach(node => node.remove());
			return !!copy.querySelector('canvas') && !copy.textContent.trim()
				&& !copy.matches('table, svg, math') && !copy.querySelector('table, svg, math');
		}''')

	#============================================
	def _source_resolution_issues(self, page: playwright.sync_api.Page,
			targets: dict[str, float | None], measurements: dict[str, dict]) -> dict[str, str]:
		"""Return per-target reasons raster source pixels cannot meet print DPI."""
		issues = {}
		for selector, target_width in targets.items():
			printed_width = self._printed_width_inches(selector, target_width, measurements)
			assets = page.locator(f'{selector}:is(canvas, img), {selector} canvas, {selector} img')
			for index in range(assets.count()):
				asset = assets.nth(index)
				asset_data = asset.evaluate('''(element) => ({
					kind: element.tagName.toLowerCase(),
					cssWidth: element.getBoundingClientRect().width,
					cssHeight: element.getBoundingClientRect().height,
					backingWidth: element.tagName === 'CANVAS' ? element.width : element.naturalWidth,
					backingHeight: element.tagName === 'CANVAS' ? element.height : element.naturalHeight,
				})''')
				minimum_width = math.ceil(
					printed_width * asset_data['cssWidth'] / measurements[selector]['width'] * PRINT_DPI)
				minimum_height = math.ceil(
					printed_width * asset_data['cssHeight'] / measurements[selector]['width'] * PRINT_DPI)
				if (asset_data['backingWidth'] < minimum_width
						or asset_data['backingHeight'] < minimum_height):
					issues[selector] = (
						f'{asset_data["kind"]} source dimensions '
						f'{asset_data["backingWidth"]}x{asset_data["backingHeight"]}px are below the '
						f'{minimum_width}x{minimum_height}px needed for {PRINT_DPI} DPI at print size')
		return issues

	#============================================
	def render(self, html: str, targets: dict[str, float | None],
			base_url: str = '', label: str = 'HTML') -> dict[str, bytes]:
		"""Capture each selector at its intended printed resolution.

		Args:
			html: Complete browser-compatible question fragment.
			targets: CSS selectors mapped to intended printed widths in inches.
				A None width uses the shared table-image scale.
			base_url: Source path or URL used to resolve relative resources.
			label: Context included in actionable rendering failures.

		Returns:
			SVG or fallback PNG bytes indexed by the requested selector.
		"""
		if not targets:
			return {}
		measurement_context, measurement_page = self._load_page(html, base_url, 1, label)
		rendered = {}
		try:
			self._wait_for_canvases(measurement_page, targets, label)
			measurements = self._target_measurements(measurement_page, targets, label)
			quality_issues = self._source_resolution_issues(measurement_page, targets, measurements)
			for selector in targets:
				try:
					if self._canvas_only(measurement_page, selector):
						continue
					if selector in quality_issues:
						warnings.warn(
							f'{label}: {selector}: SVG retains limited source detail: '
							f'{quality_issues[selector]}', stacklevel=2)
					rendered[selector] = self._capture_svg(measurement_page, selector, measurements[selector])
				except (OSError, ValueError, subprocess.SubprocessError,
						playwright.sync_api.Error, lxml.etree.XMLSyntaxError) as exc:
					warnings.warn(f'{label}: {selector}: SVG rejected; using PNG: {exc}', stacklevel=2)
			fallback_targets = {key: value for key, value in targets.items() if key not in rendered}
			capture_groups = self._capture_scales(fallback_targets, measurements)
		finally:
			measurement_context.close()
		for capture_scale, group_targets in capture_groups.items():
			capture_context, capture_page = self._load_page(
				html, base_url, capture_scale, label)
			try:
				self._wait_for_canvases(capture_page, group_targets, label)
				quality_issues = self._source_resolution_issues(
					capture_page, group_targets, measurements)
				for selector, reason in quality_issues.items():
					warnings.warn(
						f'{label}: {selector}: PNG source remains below print quality: {reason}; '
						'increased screenshot density does not restore source detail', stacklevel=2)
				dpi = CSS_PIXELS_PER_INCH * capture_scale
				for selector in group_targets:
					locator = capture_page.locator(selector)
					png_bytes = locator.screenshot(type='png')
					crop_table = locator.evaluate('(element) => element.tagName === "TABLE"')
					rendered[selector] = _stamp_png(png_bytes, dpi, crop_table)
			finally:
				capture_context.close()
		return rendered

	#============================================
	def _capture_svg(self, page: playwright.sync_api.Page, selector: str, box: dict) -> bytes:
		"""Print one live element without detaching its canvas or inherited styles."""
		converter = shutil.which('pdftocairo')
		if converter is None:
			raise OSError('pdftocairo is unavailable; install Poppler for SVG output')
		locator = page.locator(selector)
		width = math.ceil(box['width'])
		height = math.ceil(box['height'])
		locator.evaluate('(element) => element.setAttribute("data-ef-vector-target", "")')
		# Hidden siblings still affect print shrink-to-fit. Clip the page box
		# while fixing the target's measured size, without detaching live canvases.
		style = page.add_style_tag(content=(
			f'html, body {{ width:{width}px !important; height:{height}px !important;'
			'overflow:hidden !important; min-width:0 !important; margin:0 !important; }'
			'* { visibility:hidden !important; -webkit-print-color-adjust:exact !important; }'
			'[data-ef-vector-target], [data-ef-vector-target] * { visibility:visible !important; }'
			'[data-ef-vector-target] { position:fixed !important; left:0 !important;'
			'top:0 !important; margin:0 !important; box-sizing:border-box !important;'
			f'width:{box["width"]}px !important; height:{box["height"]}px !important; }}'
			f'@page {{ size:{width}px {height}px; margin:0; }}'))
		try:
			page.emulate_media(media='screen')
			with tempfile.TemporaryDirectory(prefix='ef_tools_vector_') as directory:
				pdf_path = pathlib.Path(directory) / 'capture.pdf'
				svg_path = pathlib.Path(directory) / 'capture.svg'
				page.pdf(path=str(pdf_path), prefer_css_page_size=True,
					print_background=True, page_ranges='1')
				# ASVS 1.2.5: authored content never enters a shell command.
				subprocess.run([converter, '-svg', str(pdf_path), str(svg_path)],
					check=True, capture_output=True, timeout=30)
				root = ef_tools.svg_media.svg_root(svg_path.read_bytes())
				# PDF paper sizes are rounded; keep the measured CSS dimensions
				# and clip that rounding instead of changing the drawing's scale.
				root.set('width', f'{width}px')
				root.set('height', f'{height}px')
				root.set('viewBox', f'0 0 {width * 0.75} {height * 0.75}')
				result = lxml.etree.tostring(root, xml_declaration=True, encoding='UTF-8')
		finally:
			style.evaluate('(element) => element.remove()')
			locator.evaluate('(element) => element.removeAttribute("data-ef-vector-target")')
		return result
