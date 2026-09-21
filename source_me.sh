set | grep -q '^BASH_VERSION=' || echo "use bash for your shell"
set | grep -q '^BASH_VERSION=' || exit 1

# Note: BASHRC unsets PYTHONPATH
source ~/.bashrc

# Set Python environment optimizations
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Sibling checkout of qti-package-maker supplies qti_package_maker.html_to_image
# (drawing-table detector + Playwright renderer) used by the bbq converters,
# and the bptools generator scripts import it as well.
QTI_PACKAGE_MAKER_DIR="$HOME/nsh/PROBLEMS/qti-package-maker"
if [[ -d "$QTI_PACKAGE_MAKER_DIR" ]]; then
  if [[ -z "${PYTHONPATH-}" ]]; then
    export PYTHONPATH="$QTI_PACKAGE_MAKER_DIR"
  else
    export PYTHONPATH="$QTI_PACKAGE_MAKER_DIR:$PYTHONPATH"
  fi
else
  echo "Warning: qti-package-maker not found at $QTI_PACKAGE_MAKER_DIR" >&2
fi

