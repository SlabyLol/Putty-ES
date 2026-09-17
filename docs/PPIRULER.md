# ppiRuler – Python Package Implementor Ruler

ppiRuler downloads any package from PyPI and turns it into a **fully offline** distribution.

## CLI

```bash
putty-es ppi build requests
putty-es ppi build rich --version 13.7.1 -t exe -t html -t ini -o ./offline-rich
putty-es ppi info
```

## Targets

| Target   | Output                                      |
|----------|---------------------------------------------|
| `exe` / `windows` | Windows launcher or PyInstaller EXE + sources |
| `linux`  | Linux shell launcher or binary + sources    |
| `html`   | Beautiful status / documentation page       |
| `ini`    | Configuration `.ini` files                  |
| `dll`    | Notes / stubs for native extensions         |

## Output layout

```
ppi_output/
├── windows/
├── linux/
├── html/index.html
├── config/*.ini
└── manifest.json
```

Everything is self-contained – no network calls to package indexes at runtime.
