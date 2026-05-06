"""Render RDKit HTML5 canvas widgets to PNG.

Cleaned Blackboard HTML exports embed molecular structures as a
`<canvas class="cleaned-statement-media" id="canvas_NNN">` paired with an
inline `<script>` that calls `initRDKitModule()` and binds a SMILES string
to `let smiles="..."`. The canvas-and-script pair lives somewhere inside
the same `takeQuestionDiv`, but the script is not necessarily a direct
sibling of the canvas (it is often inside a separate `<td>`). Helpers
here extract the SMILES literal from the script text and re-render the
molecule to a PNG via RDKit, without executing any JavaScript.
"""

# Standard Library
import os
import re

# Pip Modules
import rdkit.Chem
import rdkit.Chem.Draw


# Match `smiles="..."` where the character before `smiles` is not a word
# character and not a double-quote. This rejects dict-style accesses
# such as `mdetails["smiles"]=` while accepting `let smiles="..."` and
# the comment-decorated `let/* ... */smiles="..."` shape Blackboard emits.
SMILES_RE = re.compile(r'(?<![\w"])smiles\s*=\s*"([^"]+)"')


#============================================
def extract_smiles_from_rdkit_script(script_element) -> str | None:
	"""Return the SMILES literal bound in an RDKit canvas script.

	Args:
		script_element: lxml `<script>` element from a cleaned HTML export.

	Returns:
		The SMILES string captured from `let smiles="..."`, or None when the
		script does not call `initRDKitModule` (so unrelated page scripts
		are silently ignored).

	Raises:
		ValueError: when an RDKit script is recognized but no
			`smiles="..."` literal is present, so the failure is visible
			rather than silently dropping the widget.
	"""
	text = script_element.text or ""
	# Only RDKit canvas scripts are eligible.
	if "initRDKitModule" not in text:
		return None
	match = SMILES_RE.search(text)
	if match is None:
		raise ValueError(
			"RDKit script does not contain an extractable 'smiles=\"...\"' literal"
		)
	smiles = match.group(1)
	return smiles


#============================================
def render_smiles_to_png(
	smiles: str, out_dir: str, *, basename: str, size: tuple[int, int] = (480, 480)
) -> str:
	"""Render a SMILES string to a PNG file under out_dir.

	The filename is `<basename>.png`. Reruns with the same basename
	overwrite the file, which is fine because the molecule is determined
	by the SMILES and exam exports stay stable across runs.

	Args:
		smiles: Canonical SMILES string.
		out_dir: Directory to write the PNG into. Created if missing.
		basename: Filename stem (without extension), e.g. `rdkit_canvas_3071`.
		size: (width, height) in pixels for the rendered image.

	Returns:
		Absolute path to the written PNG file.

	Raises:
		ValueError: when RDKit cannot parse the SMILES.
	"""
	mol = rdkit.Chem.MolFromSmiles(smiles)
	if mol is None:
		raise ValueError(f"RDKit could not parse SMILES: {smiles!r}")
	os.makedirs(out_dir, exist_ok=True)
	out_path = os.path.abspath(os.path.join(out_dir, f"{basename}.png"))
	rdkit.Chem.Draw.MolToFile(mol, out_path, size=size)
	return out_path
