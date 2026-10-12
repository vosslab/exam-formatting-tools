set | grep -q '^BASH_VERSION=' || echo "use bash for your shell"
set | grep -q '^BASH_VERSION=' || exit 1

# Note: BASHRC unsets PYTHONPATH
source ~/.bashrc

# Set Python environment optimizations
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Must come after sourcing ~/.bashrc, which clears PYTHONPATH.
# The CLI scripts in converters/ import the repo-root ef_tools package.
REPO_ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -n "$REPO_ROOT_DIR" ]]; then
  export PYTHONPATH="$REPO_ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"
fi

