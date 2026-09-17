# Putty-ES GUI

## Launch

```bash
putty-es --gui
putty-es gui
putty-es-gui
```

## Startup animation

On every start a borderless splash screen appears with:

- Putty-ES title
- Progress bar
- Status steps (Loading core → … → Welcome)

After the animation the main window opens.

## Tabs

1. **Server Management** – select config, dry-run, apply, live log
2. **ppiRuler** – package name, version, targets, build offline package
3. **About** – version and project info

## Requirements

`customtkinter` is a hard dependency and is installed with the package.
