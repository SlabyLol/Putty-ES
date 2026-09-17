#!/usr/bin/env bash
# Putty-ES installer for Linux / macOS
set -euo pipefail

echo "========================================"
echo "  Putty-ES Installer"
echo "========================================"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: python3 not found"
  exit 1
fi

echo "→ Upgrading pip…"
"$PYTHON" -m pip install --upgrade pip

echo "→ Installing Putty-ES…"
if [ -f "pyproject.toml" ]; then
  "$PYTHON" -m pip install -e ".[full]"
else
  "$PYTHON" -m pip install putty-es
fi

echo ""
echo "✓ Installation complete"
echo ""
echo "  CLI:  putty-es --help"
echo "  GUI:  putty-es --gui"
echo "  ppi:  putty-es ppi build <package>"
echo ""
