"""Pytest configuration: ensure repo root is on sys.path for local imports."""

import sys
import subprocess

# add repo root to sys.path so tests can import local modules
_repo_root = subprocess.check_output(
	["git", "rev-parse", "--show-toplevel"],
	text=True,
).strip()
if _repo_root not in sys.path:
	sys.path.insert(0, _repo_root)
