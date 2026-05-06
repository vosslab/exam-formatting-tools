"""Test SMILES extraction and PNG rendering helpers in ef_tools.rdkit_render."""

# Standard Library
import os

# Pip Modules
import lxml.html
import pytest

# Local Repo Modules
import ef_tools.rdkit_render


# Adenine SMILES as it appears in the cleaned 2A export.
ADENINE_SMILES = "C1=NC2=NC=NC(=C2N1)N"
# Charged dipeptide SMILES with brackets and stereochemistry markers.
DIPEPTIDE_SMILES = (
	"[NH3+][C@@H](CCCC[NH3+])(C(=O)N[C@@H](Cc1ccccc1)(C(=O)[O-]))"
)


#============================================
def _build_rdkit_script(smiles: str):
	"""Return a parsed <script> element shaped like the cleaned export."""
	body = (
		"\n         /* */initRDKitModule().then(function(instance){"
		"RDKitModule=instance;/*</span> */let/* */"
		f"smiles=\"{smiles}\";let/*"
		"</span>*/mol=RDKitModule.get_mol(smiles);});\n        "
	)
	wrapper = lxml.html.fromstring(f"<div><script>{body}</script></div>")
	script = wrapper.xpath(".//script")[0]
	return script


#============================================
def test_extract_smiles_from_rdkit_script_returns_adenine():
	"""SMILES literal is recovered verbatim from the inline RDKit script."""
	script = _build_rdkit_script(ADENINE_SMILES)
	result = ef_tools.rdkit_render.extract_smiles_from_rdkit_script(script)
	assert result == ADENINE_SMILES


#============================================
def test_extract_smiles_preserves_charged_brackets_and_stereochemistry():
	"""Bracketed atoms and @@ chirality markers survive extraction unchanged."""
	script = _build_rdkit_script(DIPEPTIDE_SMILES)
	result = ef_tools.rdkit_render.extract_smiles_from_rdkit_script(script)
	assert result == DIPEPTIDE_SMILES


#============================================
def test_extract_smiles_returns_none_for_non_rdkit_script():
	"""Scripts that do not call initRDKitModule are ignored, not parsed."""
	wrapper = lxml.html.fromstring(
		"<div><script>console.log('hello'); var smiles=\"ignored\";</script></div>"
	)
	script = wrapper.xpath(".//script")[0]
	result = ef_tools.rdkit_render.extract_smiles_from_rdkit_script(script)
	assert result is None


#============================================
def test_extract_smiles_raises_when_rdkit_script_lacks_literal():
	"""An RDKit script with no smiles=\"...\" assignment fails loudly."""
	wrapper = lxml.html.fromstring(
		"<div><script>initRDKitModule().then(function(i){RDKitModule=i;});</script></div>"
	)
	script = wrapper.xpath(".//script")[0]
	with pytest.raises(ValueError):
		ef_tools.rdkit_render.extract_smiles_from_rdkit_script(script)


#============================================
def test_render_smiles_to_png_writes_nonempty_png(tmp_path):
	"""Rendering produces a PNG file under the requested directory."""
	out_dir = tmp_path / "rdkit"
	path = ef_tools.rdkit_render.render_smiles_to_png(
		ADENINE_SMILES, str(out_dir), basename="rdkit_canvas_42"
	)
	assert path.endswith("rdkit_canvas_42.png")
	assert os.path.isfile(path)
	# PNG magic bytes survive compression and version bumps.
	with open(path, "rb") as handle:
		header = handle.read(8)
	assert header.startswith(b"\x89PNG")
	# Re-rendering with the same basename targets the same file path so
	# repeated runs of the converter overwrite cleanly.
	repeat = ef_tools.rdkit_render.render_smiles_to_png(
		ADENINE_SMILES, str(out_dir), basename="rdkit_canvas_42"
	)
	assert repeat == path


#============================================
def test_render_smiles_to_png_rejects_invalid_smiles(tmp_path):
	"""Invalid SMILES strings raise rather than producing a placeholder PNG."""
	with pytest.raises(ValueError):
		ef_tools.rdkit_render.render_smiles_to_png(
			"not-a-molecule", str(tmp_path), basename="rdkit_bad"
		)
