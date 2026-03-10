"""
app/ui/widgets/mini_timer.py – Floating, draggable, resizable timer overlay.

Features:
  • Always-on-top frameless window
  • Drag to move (left-click-drag)
  • Resize from bottom-right grip
  • Double-click to toggle fullscreen
  • Auto-scaling font
  • Coloured accent bar matching study / break mode
"""
from __future__ import annotations
import customtkinter as ctk
from app.config import PALETTE, font, font_bold


class MiniTimer:
    """Manages the floating mini-timer Toplevel window."""

    def __init__(self, parent: ctk.CTk, mode: str, on_click_restore) -> None:
        self._parent         = parent
        self._on_restore     = on_click_restore
        self._is_fullscreen  = False
        self._normal_geom    = ""
        self._dragged        = False
        self._drag_x = self._drag_y = 0
        self._rsz_w = self._rsz_h = 0
        self._rsz_ox = self._rsz_oy = 0

        self._build(mode)

    # ── Construction ──────────────────────────
    def _build(self, mode: str) -> None:
        color = PALETTE["study"] if mode == "Study" else PALETTE["brk"]
        bg    = PALETTE["bg_panel"]

        W, H  = 180, 76
        sw    = self._parent.winfo_screenwidth()
        sh    = self._parent.winfo_screenheight()
        x     = (sw - W) // 2
        y     = sh - H - 80

        self.win = ctk.CTkToplevel(self._parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.geometry(f"{W}x{H}+{x}+{y}")
        self.win.configure(fg_color=bg)
        self._normal_geom = self.win.geometry()

        # Top accent line
        ctk.CTkFrame(self.win, height=4, corner_radius=0, fg_color=color).pack(
            fill="x"
        )

        self.lbl = ctk.CTkLabel(
            self.win,
            text="00:00",
            font=font_bold(36),
            text_color=color,
            cursor="hand2",
        )
        self.lbl.pack(expand=True, fill="both")

        # Resize grip dot
        self._grip = ctk.CTkFrame(
            self.win,
            width=14, height=14,
            fg_color=PALETTE["text_muted"],
            cursor="bottom_right_corner",
            corner_radius=0,
        )
        self._grip.place(relx=1.0, rely=1.0, anchor="se")

        # ── Event bindings ────────────────────
        self.lbl.bind("<ButtonPress-1>",   self._on_press)
        self.lbl.bind("<B1-Motion>",       self._on_drag)
        self.lbl.bind("<ButtonRelease-1>", self._on_release)
        self.lbl.bind("<Double-Button-1>", self._toggle_fullscreen)
        self._grip.bind("<ButtonPress-1>", self._rsz_start)
        self._grip.bind("<B1-Motion>",     self._rsz_do)
        self.win.bind("<Configure>",       self._auto_scale_font)

    # ── Public API ────────────────────────────
    def update_text(self, text: str) -> None:
        if self.lbl.winfo_exists():
            self.lbl.configure(text=text)

    def exists(self) -> bool:
        try:
            return bool(self.win and self.win.winfo_exists())
        except Exception:
            return False

    def destroy(self) -> None:
        try:
            self.win.destroy()
        except Exception:
            pass

    # ── Drag ──────────────────────────────────
    def _on_press(self, event) -> None:
        self._drag_x  = event.x
        self._drag_y  = event.y
        self._dragged = False

    def _on_drag(self, event) -> None:
        nx = self.win.winfo_x() - self._drag_x + event.x
        ny = self.win.winfo_y() - self._drag_y + event.y
        self.win.geometry(f"+{nx}+{ny}")
        self._dragged = True

    def _on_release(self, event) -> None:
        if not self._dragged:
            self._on_restore()

    # ── Resize ────────────────────────────────
    def _rsz_start(self, event) -> None:
        self._rsz_w  = self.win.winfo_width()
        self._rsz_h  = self.win.winfo_height()
        self._rsz_ox = event.x_root
        self._rsz_oy = event.y_root

    def _rsz_do(self, event) -> None:
        nw = max(130, self._rsz_w + event.x_root - self._rsz_ox)
        nh = max(54,  self._rsz_h + event.y_root - self._rsz_oy)
        self.win.geometry(f"{nw}x{nh}")

    # ── Fullscreen ────────────────────────────
    def _toggle_fullscreen(self, event=None) -> None:
        self._is_fullscreen = not self._is_fullscreen
        if self._is_fullscreen:
            self._normal_geom = self.win.geometry()
            sw = self._parent.winfo_screenwidth()
            sh = self._parent.winfo_screenheight()
            self.win.geometry(f"{sw}x{sh}+0+0")
            self._grip.place_forget()
        else:
            self.win.geometry(self._normal_geom)
            self._grip.place(relx=1.0, rely=1.0, anchor="se")

    # ── Auto-scale font ───────────────────────
    def _auto_scale_font(self, event) -> None:
        if event.widget == self.win:
            sz = max(24, int(event.height * 0.52))
            self.lbl.configure(font=font_bold(sz))
