"""
Main Putty-ES GUI application.
Modern dark-themed interface with Server Management + ppiRuler.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    CTK_AVAILABLE = True
except ImportError:
    import tkinter as ctk
    from tkinter import filedialog, messagebox, ttk
    CTK_AVAILABLE = False

from putty_es import __version__
from putty_es.gui.splash import SplashScreen


def _set_appearance() -> None:
    if CTK_AVAILABLE:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")


class PuttyESApp:
    """Main application window."""

    def __init__(self) -> None:
        _set_appearance()
        self.root = ctk.CTk() if CTK_AVAILABLE else ctk.Tk()
        self.root.title(f"Putty-ES v{__version__}")
        self.root.geometry("980x640")
        self.root.minsize(820, 560)

        # Center
        self.root.update_idletasks()
        w, h = 980, 640
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    def _build_ui(self) -> None:
        # ── Top bar ──────────────────────────────────────
        top = ctk.CTkFrame(self.root, height=56, corner_radius=0, fg_color="#161b22")
        top.pack(fill="x")
        top.pack_propagate(False)

        title = ctk.CTkLabel(
            top,
            text="  Putty-ES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#58a6ff",
        )
        title.pack(side="left", padx=12, pady=12)

        subtitle = ctk.CTkLabel(
            top,
            text=f"v{__version__}  ·  Elite Server Setup + ppiRuler",
            font=ctk.CTkFont(size=12),
            text_color="#8b949e",
        )
        subtitle.pack(side="left", padx=4, pady=12)

        # ── Tabview ──────────────────────────────────────
        self.tabs = ctk.CTkTabview(self.root, fg_color="#0d1117")
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_server = self.tabs.add("Server Management")
        self.tab_ppi = self.tabs.add("ppiRuler")
        self.tab_about = self.tabs.add("About")

        self._build_server_tab()
        self._build_ppi_tab()
        self._build_about_tab()

        # Status bar
        self.status = ctk.CTkLabel(
            self.root,
            text=" Ready",
            font=ctk.CTkFont(size=11),
            text_color="#8b949e",
            anchor="w",
        )
        self.status.pack(fill="x", padx=12, pady=(0, 8))

    # ── Server Management Tab ─────────────────────────────

    def _build_server_tab(self) -> None:
        frame = self.tab_server

        # Config file row
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=(12, 6))

        ctk.CTkLabel(row, text="Config file:", width=90, anchor="w").pack(side="left")
        self.config_entry = ctk.CTkEntry(row, placeholder_text="path/to/config.yaml")
        self.config_entry.pack(side="left", fill="x", expand=True, padx=6)

        ctk.CTkButton(row, text="Browse…", width=90, command=self._browse_config).pack(side="left")

        # Options
        opts = ctk.CTkFrame(frame, fg_color="transparent")
        opts.pack(fill="x", padx=8, pady=6)

        self.dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts, text="Dry-run (simulate only)", variable=self.dry_run_var).pack(side="left", padx=4)

        self.verbose_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opts, text="Verbose", variable=self.verbose_var).pack(side="left", padx=12)

        # Buttons
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=8)

        ctk.CTkButton(
            btn_row, text="Apply Configuration", width=160,
            fg_color="#238636", hover_color="#2ea043",
            command=self._apply_config,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="Init Example Config", width=150,
            command=self._init_config,
        ).pack(side="left", padx=4)

        # Log / output area
        ctk.CTkLabel(frame, text="Output", anchor="w").pack(fill="x", padx=12, pady=(12, 2))
        self.server_log = ctk.CTkTextbox(frame, height=280, font=ctk.CTkFont(family="Consolas", size=12))
        self.server_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.server_log.insert("end", "Ready. Select a configuration file and click Apply.\n")

    def _browse_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Putty-ES config",
            filetypes=[("YAML / TOML", "*.yaml *.yml *.toml"), ("All files", "*.*")],
        )
        if path:
            self.config_entry.delete(0, "end")
            self.config_entry.insert(0, path)

    def _init_config(self) -> None:
        from putty_es.cli import init as cli_init
        # Simple local init
        target = Path("putty-es.yaml")
        if target.exists():
            messagebox.showinfo("Info", "putty-es.yaml already exists.")
            return
        example = """name: my-server-fleet
hosts:
  - name: web-01
    hostname: 192.168.1.10
    user: root
    port: 22
modules:
  - name: packages
    packages: [curl, git, htop]
"""
        target.write_text(example, encoding="utf-8")
        self.config_entry.delete(0, "end")
        self.config_entry.insert(0, str(target.resolve()))
        self._log_server(f"Created {target.resolve()}\n")
        self.status.configure(text=" Example configuration created")

    def _apply_config(self) -> None:
        path = self.config_entry.get().strip()
        if not path:
            messagebox.showwarning("Missing", "Please select a configuration file.")
            return

        def worker() -> None:
            self.status.configure(text=" Applying configuration…")
            self._log_server(f"\n>>> Applying {path}\n")
            try:
                from putty_es.core.config import load_config
                from putty_es.core.executor import Executor

                config = load_config(path)
                self._log_server(f"Loaded fleet: {config.name}\n")
                executor = Executor(
                    dry_run=self.dry_run_var.get(),
                    verbose=self.verbose_var.get(),
                )
                for host in config.hosts:
                    self._log_server(f"  → Host {host.name} ({host.hostname})\n")
                    try:
                        executor.apply_modules(host, config.modules)
                        self._log_server(f"  ✓ {host.name} done\n")
                    except Exception as e:
                        self._log_server(f"  ✗ {host.name}: {e}\n")
                self._log_server("\nAll done.\n")
                self.status.configure(text=" Configuration applied")
            except Exception as e:
                self._log_server(f"Error: {e}\n")
                self.status.configure(text=" Error")

        threading.Thread(target=worker, daemon=True).start()

    def _log_server(self, text: str) -> None:
        self.server_log.insert("end", text)
        self.server_log.see("end")

    # ── ppiRuler Tab ──────────────────────────────────────

    def _build_ppi_tab(self) -> None:
        frame = self.tab_ppi

        # Package input
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(12, 6))

        ctk.CTkLabel(row1, text="Package:", width=90, anchor="w").pack(side="left")
        self.pkg_entry = ctk.CTkEntry(row1, placeholder_text="e.g. requests  or  rich==13.7.1")
        self.pkg_entry.pack(side="left", fill="x", expand=True, padx=6)

        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(row2, text="Version:", width=90, anchor="w").pack(side="left")
        self.ver_entry = ctk.CTkEntry(row2, placeholder_text="optional (latest if empty)", width=160)
        self.ver_entry.pack(side="left", padx=6)

        ctk.CTkLabel(row2, text="Output:", width=60, anchor="w").pack(side="left", padx=(16, 0))
        self.out_entry = ctk.CTkEntry(row2, placeholder_text="./ppi_output")
        self.out_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.out_entry.insert(0, "./ppi_output")

        # Targets
        targets_frame = ctk.CTkFrame(frame, fg_color="transparent")
        targets_frame.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(targets_frame, text="Targets:").pack(side="left", padx=(0, 8))

        self.t_exe = ctk.BooleanVar(value=True)
        self.t_linux = ctk.BooleanVar(value=True)
        self.t_html = ctk.BooleanVar(value=True)
        self.t_ini = ctk.BooleanVar(value=True)
        self.t_dll = ctk.BooleanVar(value=False)

        for text, var in [
            ("Windows / EXE", self.t_exe),
            ("Linux", self.t_linux),
            ("HTML", self.t_html),
            ("INI", self.t_ini),
            ("DLL notes", self.t_dll),
        ]:
            ctk.CTkCheckBox(targets_frame, text=text, variable=var).pack(side="left", padx=6)

        # Build button
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=10)

        ctk.CTkButton(
            btn_row,
            text="Build Offline Package",
            width=180,
            fg_color="#1f6feb",
            hover_color="#388bfd",
            command=self._run_ppi,
        ).pack(side="left", padx=4)

        # Log
        ctk.CTkLabel(frame, text="ppiRuler Output", anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        self.ppi_log = ctk.CTkTextbox(frame, height=260, font=ctk.CTkFont(family="Consolas", size=12))
        self.ppi_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.ppi_log.insert("end", "Enter a package name and click Build Offline Package.\n")

    def _run_ppi(self) -> None:
        package = self.pkg_entry.get().strip()
        if not package:
            messagebox.showwarning("Missing", "Please enter a package name.")
            return

        version = self.ver_entry.get().strip() or None
        output = self.out_entry.get().strip() or "./ppi_output"

        targets = []
        if self.t_exe.get():
            targets.append("exe")
        if self.t_linux.get():
            targets.append("linux")
        if self.t_html.get():
            targets.append("html")
        if self.t_ini.get():
            targets.append("ini")
        if self.t_dll.get():
            targets.append("dll")

        if not targets:
            messagebox.showwarning("Targets", "Select at least one target.")
            return

        def worker() -> None:
            self.status.configure(text=f" ppiRuler building {package}…")
            self._log_ppi(f"\n>>> Building offline package for {package}\n")
            try:
                from putty_es.ppi_ruler.core import PPIRuler

                ruler = PPIRuler(
                    package=package,
                    version=version,
                    output_dir=output,
                    targets=targets,
                )
                # No terminal animation in GUI mode
                result = ruler.run(animated=False)
                self._log_ppi(f"✓ Finished. Output: {result}\n")
                self.status.configure(text=f" ppiRuler finished → {result}")
                messagebox.showinfo("Success", f"Offline package created in:\n{result}")
            except Exception as e:
                self._log_ppi(f"Error: {e}\n")
                self.status.configure(text=" ppiRuler error")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _log_ppi(self, text: str) -> None:
        self.ppi_log.insert("end", text)
        self.ppi_log.see("end")

    # ── About Tab ─────────────────────────────────────────

    def _build_about_tab(self) -> None:
        frame = self.tab_about

        about_text = f"""
Putty-ES  v{__version__}

Elite Server Setup & Management Tool
+ ppiRuler (Python Package Implementor Ruler)

Open Source · MIT License
DarkFox Co. / SlabyLol

Features:
  • Modular server provisioning over SSH
  • Configuration-driven (YAML / TOML)
  • Smart modules (packages, pypi, docker, firewall, …)
  • ppiRuler – turn any PyPI package into offline artifacts
  • Clean animated startup
  • Modern dark GUI

GitHub: https://github.com/SlabyLol/Putty-ES
"""
        label = ctk.CTkLabel(
            frame,
            text=about_text.strip(),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            justify="left",
            anchor="nw",
        )
        label.pack(fill="both", expand=True, padx=24, pady=24)

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    """Entry point: show animated splash, then main window."""

    def start_main() -> None:
        app = PuttyESApp()
        app.run()

    splash = SplashScreen(on_complete=start_main)
    splash.show()
