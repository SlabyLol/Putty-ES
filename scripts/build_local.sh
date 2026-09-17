#!/usr/bin/env bash
# Local build of wheels + optional PyInstaller binary
set -euo pipefail

echo "→ Building sdist + wheel…"
python -m pip install --upgrade build wheel
python -m build

echo "→ Building standalone executable (optional)…"
if python -c "import PyInstaller" 2>/dev/null; then
  pyinstaller --onefile --name putty-es --paths src src/putty_es/cli.py || true
  echo "Binary (if successful): dist/putty-es"
else
  echo "PyInstaller not installed – skipping binary build"
  echo "  pip install pyinstaller"
fi

echo "Done. Artifacts in dist/"
