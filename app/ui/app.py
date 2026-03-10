"""
app/ui/app.py – Root application window for POMODORO.
"""
from __future__ import annotations
import customtkinter as ctk

import app.config as config
from app.config import PALETTE, font, font_bold
from app.database import Database
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.timer import TimerPage


class Pomodoro(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        ctk.set_appearance_mode(config.ctk_appearance())
        ctk.set_default_color_theme("blue")
        super().__init__()

        self.title("POMODORO")

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = int(sw * 0.70), int(sh * 0.80)
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.minsize(int(sw * 0.50), int(sh * 0.60))
        self.configure(fg_color=PALETTE["bg_deep"])

        self._db           = Database()
        self._current_page = "dashboard"
        self._build()

    # ── Build ─────────────────────────────────
    def _build(self) -> None:
        self._sidebar = ctk.CTkFrame(
            self, width=200, fg_color=PALETTE["bg_panel"], corner_radius=0
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._build_sidebar(self._sidebar)

        self._content = ctk.CTkFrame(
            self, fg_color=PALETTE["bg_deep"], corner_radius=0
        )
        self._content.pack(side="left", fill="both", expand=True)
        self._build_pages()

    def _build_pages(self) -> None:
        self._dash_page = DashboardPage(
            self._content,
            db=self._db,
            on_view_ledger=self._show_ledger,
            on_toggle_theme=self._toggle_theme,
        )
        self._timer_page = TimerPage(
            self._content,
            db=self._db,
            on_stats_changed=self._refresh_dash,
            on_toggle_theme=self._toggle_theme,
        )
        for page in (self._dash_page, self._timer_page):
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._show_page(self._current_page)
        self._dash_page.load_goals()
        self._dash_page.refresh_stats()
        self._timer_page.load_tasks()

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self, parent: ctk.CTkFrame) -> None:
        ctk.CTkLabel(parent, text="🍅", font=font(44)).pack(pady=(30, 2))

        self._appname_lbl = ctk.CTkLabel(
            parent, text="POMODORO",
            font=font_bold(18), text_color=PALETTE["text_primary"],
        )
        self._appname_lbl.pack(pady=(0, 32))

        self._divider = ctk.CTkFrame(
            parent, height=1, fg_color=PALETTE["bg_card2"], corner_radius=0
        )
        self._divider.pack(fill="x", padx=16, pady=(0, 16))

        self._nav_buttons: list[ctk.CTkButton] = []
        for label, key in [("📊  Dashboard", "dashboard"), ("⏱  Timer", "timer")]:
            btn = ctk.CTkButton(
                parent, text=label, height=44, corner_radius=12,
                fg_color="transparent",
                hover_color=PALETTE["sidebar_nav_hover"],
                text_color=PALETTE["text_secondary"],
                font=font(15), anchor="w",
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill="x", padx=12, pady=3)
            btn._page_key = key
            self._nav_buttons.append(btn)

        self._footer_lbl = ctk.CTkLabel(
            parent, text="v2.0",
            font=font(11), text_color=PALETTE["text_muted"],
        )
        self._footer_lbl.pack(side="bottom", pady=16)

    # ── Navigation ────────────────────────────
    def _show_page(self, key: str) -> None:
        self._current_page = key
        {"dashboard": self._dash_page, "timer": self._timer_page}[key].lift()
        for btn in self._nav_buttons:
            active = getattr(btn, "_page_key", None) == key
            btn.configure(
                fg_color=PALETTE["sidebar_nav_active"] if active else "transparent",
                text_color=PALETTE["text_primary"] if active else PALETTE["text_secondary"],
                font=font_bold(15) if active else font(15),
            )

    # ── Theme toggle ──────────────────────────
    def _toggle_theme(self) -> None:
        new_mode = "light" if config.current_theme() == "dark" else "dark"
        config.set_theme(new_mode)
        ctk.set_appearance_mode(config.ctk_appearance())

        self.configure(fg_color=PALETTE["bg_deep"])
        self._content.configure(fg_color=PALETTE["bg_deep"])
        self._sidebar.configure(fg_color=PALETTE["bg_panel"])
        self._appname_lbl.configure(text_color=PALETTE["text_primary"])
        self._divider.configure(fg_color=PALETTE["bg_card2"])
        self._footer_lbl.configure(text_color=PALETTE["text_muted"])

        self._dash_page.apply_theme()
        self._timer_page.apply_theme()
        self._show_page(self._current_page)

    # ── Callbacks ─────────────────────────────
    def _refresh_dash(self) -> None:
        self._dash_page.refresh_stats()

    def _show_ledger(self) -> None:
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = sw // 2, sh // 2
        x, y = (sw - w) // 2, (sh - h) // 2

        dlg = ctk.CTkToplevel(self)
        dlg.title("Ledger History")
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        dlg.resizable(False, False)
        dlg.configure(fg_color=PALETTE["bg_deep"])
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()

        # ── Header ──────────────────────────
        hdr = ctk.CTkFrame(dlg, height=60, fg_color=PALETTE["bg_panel"], corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="📅  Ledger History",
                     font=font_bold(20), text_color=PALETTE["text_primary"]
                     ).pack(side="left", padx=24, pady=14)

        # ── Date row ────────────────────────
        row = ctk.CTkFrame(dlg, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=(22, 10))

        ctk.CTkLabel(row, text="Date:", font=font(15),
                     text_color=PALETTE["text_secondary"]).pack(side="left", padx=(0, 10))

        date_var = ctk.StringVar(value=self._db.today)
        date_entry = ctk.CTkEntry(
            row, textvariable=date_var,
            width=180, height=38, corner_radius=10,
            fg_color=PALETTE["bg_input"], border_color=PALETTE["bg_card2"],
            text_color=PALETTE["text_bright"], font=font(15),
        )
        date_entry.pack(side="left", padx=(0, 12))

        # ── Result box ──────────────────────
        result_box = ctk.CTkTextbox(
            dlg, state="disabled",
            fg_color=PALETTE["bg_card"], border_color=PALETTE["bg_card2"],
            border_width=1, corner_radius=12,
            text_color=PALETTE["text_bright"], font=font(15),
            wrap="word",
        )
        result_box.pack(fill="both", expand=True, padx=28, pady=(0, 10))

        def _load():
            target = date_var.get().strip()
            result_box.configure(state="normal")
            result_box.delete("1.0", "end")
            row_data = self._db.get_ledger_for_date(target)
            if not row_data:
                result_box.insert("end", f"No data found for {target}.")
            else:
                tasks = self._db.get_tasks_for_date(target)
                tasks_str = "\n".join(f"  • {n}  [{s}]" for n, s in tasks) or "  No tasks."
                result_box.insert("end",
                    f"Date:       {target}\n"
                    f"Study time: {row_data['study_minutes']} min "
                    f"({round(row_data['study_minutes']/60, 2)} hrs)\n\n"
                    f"Tasks:\n{tasks_str}"
                )
            result_box.configure(state="disabled")

        ctk.CTkButton(
            row, text="Load", width=90, height=38, corner_radius=10,
            fg_color=PALETTE["accent"], hover_color=PALETTE["accent_hover"],
            font=font_bold(14), command=_load,
        ).pack(side="left")

        date_entry.bind("<Return>", lambda _e: _load())
        _load()  # pre-load today

        ctk.CTkButton(
            dlg, text="Close", width=110, height=38, corner_radius=10,
            fg_color=PALETTE["stop"], hover_color=PALETTE["stop_hover"],
            font=font_bold(13), command=dlg.destroy,
        ).pack(pady=(0, 18))


    # ── Lifecycle ─────────────────────────────
    def run(self) -> None:
        self.mainloop()
        self._db.close()
