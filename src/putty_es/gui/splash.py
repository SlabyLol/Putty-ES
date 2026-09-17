"""
Animated splash / startup screen for Putty-ES GUI.
Clean, modern, professional animation on program start.
"""

from __future__ import annotations

import time
import threading
from typing import Callable, Optional

try:
    import customtkinter as ctk
except ImportError:
    import tkinter as ctk  # type: ignore

from putty_es import __version__


class SplashScreen:
    """Animated startup splash window."""

    def __init__(self, on_complete: Optional[Callable] = None) -> None:
        self.on_complete = on_complete
        self.root = ctk.CTk() if hasattr(ctk, "CTk") else ctk.Tk()
        self.root.title("Putty-ES")
        self.root.geometry("520x320")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # borderless

        # Center on screen
        self.root.update_idletasks()
        w, h = 520, 320
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Dark background
        try:
            self.root.configure(fg_color="#0d1117")
        except Exception:
            self.root.configure(bg="#0d1117")

        self._build_ui()
        self._progress = 0.0

    def _build_ui(self) -> None:
        # Main frame
        frame = ctk.CTkFrame(self.root, fg_color="#0d1117", corner_radius=0)
        frame.pack(fill="both", expand=True)

        # Logo / Title
        self.title_label = ctk.CTkLabel(
            frame,
            text="Putty-ES",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color="#58a6ff",
        )
        self.title_label.pack(pady=(60, 4))

        self.subtitle = ctk.CTkLabel(
            frame,
            text="Elite Server Setup & Management",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#8b949e",
        )
        self.subtitle.pack(pady=(0, 8))

        self.version_label = ctk.CTkLabel(
            frame,
            text=f"v{__version__}  ·  ppiRuler included",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#484f58",
        )
        self.version_label.pack(pady=(0, 30))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            frame,
            width=320,
            height=6,
            progress_color="#58a6ff",
            fg_color="#21262d",
            corner_radius=3,
        )
        self.progress.pack(pady=(10, 8))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            frame,
            text="Starting…",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8b949e",
        )
        self.status_label.pack(pady=(4, 0))

        # Footer
        footer = ctk.CTkLabel(
            frame,
            text="DarkFox Co.  ·  Open Source",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#30363d",
        )
        footer.pack(side="bottom", pady=16)

    def _animate(self) -> None:
        steps = [
            (0.15, "Loading core…"),
            (0.30, "Initializing modules…"),
            (0.45, "Preparing ppiRuler…"),
            (0.60, "Loading configuration…"),
            (0.75, "Building interface…"),
            (0.90, "Almost ready…"),
            (1.00, "Welcome"),
        ]

        for value, text in steps:
            self._progress = value
            try:
                self.progress.set(value)
                self.status_label.configure(text=text)
                self.root.update()
            except Exception:
                break
            time.sleep(0.28)

        time.sleep(0.35)
        self._close()

    def _close(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass
        if self.on_complete:
            self.on_complete()

    def show(self) -> None:
        """Show splash and run animation in a thread."""
        t = threading.Thread(target=self._animate, daemon=True)
        t.start()
        self.root.mainloop()
