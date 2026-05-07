"""CLI helpers for root scripts: extension validation and default outputs."""

# Standard Library
import os


#============================================
def require_extensions(path: str, allowed: tuple, role: str) -> None:
	"""Validate that path has one of the allowed extensions.

	Raises ValueError on mismatch so a wrong-format input fails loudly
	at startup instead of producing a near-empty or malformed output.

	Args:
		path: File path to check.
		allowed: Tuple of allowed extensions, lowercase, including the dot
			(for example ('.yml', '.yaml')).
		role: Human-readable role for the error message ('input' or 'output').
	"""
	ext = os.path.splitext(path)[1].lower()
	if ext not in allowed:
		raise ValueError(
			f"{role} file {path!r} has extension {ext!r}; "
			f"expected one of {allowed}"
		)


#============================================
def default_output_path(input_path: str, new_ext: str) -> str:
	"""Derive an output path from an input path by swapping its extension.

	The output is just the basename + new extension, so it lands in the
	current working directory rather than alongside the input file. This
	avoids accidentally overwriting source files when the script is run
	from a different directory.

	Args:
		input_path: Path to the input file.
		new_ext: Target extension including the leading dot (for example
			'.docx' or '.yml').

	Returns:
		Basename of input_path with its extension replaced by new_ext.
	"""
	stem = os.path.splitext(os.path.basename(input_path))[0]
	output_path = stem + new_ext
	return output_path
