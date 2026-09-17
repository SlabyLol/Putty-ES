# Putty-ES installer for Windows (PowerShell)
Write-Host "========================================"
Write-Host "  Putty-ES Installer (Windows)"
Write-Host "========================================"

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

Write-Host "→ Upgrading pip…"
& $Python -m pip install --upgrade pip

Write-Host "→ Installing Putty-ES…"
if (Test-Path "pyproject.toml") {
    & $Python -m pip install -e ".[full]"
} else {
    & $Python -m pip install putty-es
}

Write-Host ""
Write-Host "✓ Installation complete"
Write-Host ""
Write-Host "  CLI:  putty-es --help"
Write-Host "  GUI:  putty-es --gui"
Write-Host "  ppi:  putty-es ppi build <package>"
Write-Host ""
