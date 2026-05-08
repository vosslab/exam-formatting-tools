# Exclude both end-to-end tiers from pytest collection. tests/playwright/
# holds browser-driven tests (Playwright), and tests/e2e/ holds heavier
# shell/Python whole-system runners. Both run outside pytest -- see
# docs/PLAYWRIGHT_USAGE.md and docs/E2E_TESTS.md.
collect_ignore = ["e2e", "playwright"]

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
