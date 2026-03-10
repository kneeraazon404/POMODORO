"""
app/ui/pages/timer.py – Pomodoro timer page + task list.
"""
from __future__ import annotations
import customtkinter as ctk
from app.config import PALETTE, font, font_bold
from app.database import Database
from app.ui.widgets.mini_timer import MiniTimer


class TimerPage(ctk.CTkFrame):
    """Page 2 – Pomodoro timer and daily task list."""

    def __init__(self, parent, db: Database, on_stats_changed, on_toggle_theme) -> None:
        super().__init__(parent, fg_color=PALETTE["bg_deep"], corner_radius=0)
        self._db              = db
        self._on_stats        = on_stats_changed
        self._on_toggle_theme = on_toggle_theme

        # Timer state
        self._is_running      = False
        self._time_left       = 0
        self._current_mode    = "Study"
        self._session_minutes = 25
        self._mini: MiniTimer | None = None

        self._build()

    # ── Build ─────────────────────────────────
    def _build(self) -> None:
        self._build_header()
        self._build_timer_card()
        self._build_task_section()

    def _build_header(self) -> None:
        self._hdr = ctk.CTkFrame(self, height=72, fg_color=PALETTE["bg_panel"],
                            corner_radius=0)
        self._hdr.pack(fill="x")
        self._hdr.pack_propagate(False)
        self._hdr_lbl = ctk.CTkLabel(
            self._hdr,
            text="Pomodoro Timer",
            font=font_bold(24),
            text_color=PALETTE["text_primary"],
        )
        self._hdr_lbl.pack(side="left", padx=30, pady=18)

        # Theme icon – top-right of header
        self._theme_btn = ctk.CTkButton(
            self._hdr,
            text=PALETTE["theme_icon"],
            width=40, height=38, corner_radius=10,
            fg_color=PALETTE["bg_card2"],
            hover_color=PALETTE["sidebar_nav_hover"],
            text_color=PALETTE["text_primary"],
            font=font(20),
            command=self._on_toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=22, pady=18)

    def _build_timer_card(self) -> None:
        self._timer_card = ctk.CTkFrame(
            self,
            fg_color=PALETTE["bg_card"],
            corner_radius=20,
            border_width=1,
            border_color=PALETTE["bg_card2"],
        )
        self._timer_card.pack(fill="x", padx=26, pady=22)
        card = self._timer_card

        # Mode badge
        self._mode_lbl = ctk.CTkLabel(
            card,
            text="IDLE",
            font=font_bold(13),
            text_color=PALETTE["text_muted"],
        )
        self._mode_lbl.pack(pady=(22, 2))

        # Giant clock
        self._lbl_timer = ctk.CTkLabel(
            card,
            text="25:00",
            font=font_bold(90),
            text_color=PALETTE["timer_idle"],
        )
        self._lbl_timer.pack()

        # Duration pickers
        pickers = ctk.CTkFrame(card, fg_color="transparent")
        pickers.pack(pady=(6, 0))

        for col, (label, values, default, attr) in enumerate([
            ("Study (min)", ["15","25","30","45","50","60","90","120"], "25", "opt_study"),
            ("Break (min)", ["5","10","15","20","30"], "5", "opt_break"),
        ]):
            ctk.CTkLabel(
                pickers, text=label, font=font(13),
                text_color=PALETTE["text_secondary"],
            ).grid(row=0, column=col * 2, padx=(24, 6), pady=4)
            opt = ctk.CTkOptionMenu(
                pickers,
                values=values, width=82, height=34, corner_radius=8,
                fg_color=PALETTE["bg_input"],
                button_color=PALETTE["accent"],
                button_hover_color=PALETTE["accent_hover"],
                dropdown_fg_color=PALETTE["bg_card2"],
                text_color=PALETTE["text_primary"],
                font=font(14),
            )
            opt.set(default)
            opt.grid(row=0, column=col * 2 + 1, padx=(0, 20), pady=4)
            setattr(self, attr, opt)

        # Action buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(18, 26))

        W, H = 154, 46
        for col, (txt, clr, hov, cmd) in enumerate([
            ("▶  Study",  PALETTE["study"], PALETTE["study_hover"], lambda: self._start("Study")),
            ("☕  Break",  PALETTE["brk"],   PALETTE["brk_hover"],   lambda: self._start("Break")),
            ("■  Stop",   PALETTE["stop"],  PALETTE["stop_hover"],  self._stop),
        ]):
            ctk.CTkButton(
                btn_row, text=txt, width=W, height=H, corner_radius=12,
                fg_color=clr, hover_color=hov, font=font_bold(15),
                command=cmd,
            ).grid(row=0, column=col, padx=10)

    def _build_task_section(self) -> None:
        # ── Header row ────────────────────────
        th = ctk.CTkFrame(self, fg_color="transparent")
        th.pack(fill="x", padx=26, pady=(4, 4))

        ctk.CTkLabel(
            th,
            text="📋  Today's Tasks",
            font=font_bold(18),
            text_color=PALETTE["text_primary"],
        ).pack(side="left")

        # ── Input row ─────────────────────────
        ir = ctk.CTkFrame(self, fg_color="transparent")
        ir.pack(fill="x", padx=26, pady=(0, 8))

        self._task_entry = ctk.CTkEntry(
            ir,
            placeholder_text="Add a new task and press Enter …",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["bg_input"],
            border_color=PALETTE["bg_card2"],
            border_width=1,
            text_color=PALETTE["text_primary"],
            placeholder_text_color=PALETTE["text_muted"],
            font=font(15),
        )
        self._task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._task_entry.bind("<Return>", lambda _e: self._add_task())

        ctk.CTkButton(
            ir,
            text="＋  Add",
            width=106, height=42, corner_radius=10,
            fg_color=PALETTE["accent"], hover_color=PALETTE["accent_hover"],
            font=font_bold(14),
            command=self._add_task,
        ).pack(side="left")

        # ── Scrollable task list ───────────────
        self._tasks_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=PALETTE["bg_card"],
            corner_radius=14,
            border_width=1,
            border_color=PALETTE["bg_card2"],
            scrollbar_button_color=PALETTE["accent"],
        )
        self._tasks_frame.pack(fill="both", expand=True, padx=26, pady=(0, 22))

    # ── Theme support ─────────────────────────
    def apply_theme(self) -> None:
        """Reconfigure all explicitly-colored widgets with current PALETTE."""
        self.configure(fg_color=PALETTE["bg_deep"])
        self._hdr.configure(fg_color=PALETTE["bg_panel"])
        self._hdr_lbl.configure(text_color=PALETTE["text_primary"])
        self._theme_btn.configure(
            text=PALETTE["theme_icon"],
            fg_color=PALETTE["bg_card2"],
            hover_color=PALETTE["sidebar_nav_hover"],
            text_color=PALETTE["text_primary"],
        )
        self._timer_card.configure(
            fg_color=PALETTE["bg_card"], border_color=PALETTE["bg_card2"]
        )
        self._mode_lbl.configure(text_color=PALETTE["text_muted"])
        if not self._is_running:
            self._lbl_timer.configure(text_color=PALETTE["timer_idle"])
        self._task_entry.configure(
            fg_color=PALETTE["bg_input"],
            border_color=PALETTE["bg_card2"],
            text_color=PALETTE["text_primary"],
            placeholder_text_color=PALETTE["text_muted"],
        )
        self._tasks_frame.configure(
            fg_color=PALETTE["bg_card"],
            border_color=PALETTE["bg_card2"],
            scrollbar_button_color=PALETTE["accent"],
        )
        self.load_tasks()

    # ── Tasks ─────────────────────────────────
    def load_tasks(self) -> None:
        for w in self._tasks_frame.winfo_children():
            w.destroy()

        rows = self._db.get_tasks()
        if not rows:
            ctk.CTkLabel(
                self._tasks_frame,
                text="No tasks yet — add one above!",
                font=font(14),
                text_color=PALETTE["text_muted"],
            ).pack(pady=22)
            return

        for task_id, name, status in rows:
            done = status == "completed"
            row_f = ctk.CTkFrame(
                self._tasks_frame,
                fg_color=PALETTE["bg_card2"] if done else PALETTE["bg_panel"],
                corner_radius=10,
            )
            row_f.pack(fill="x", padx=10, pady=4)

            cb = ctk.CTkCheckBox(
                row_f,
                text=name,
                font=font(14),
                text_color=PALETTE["text_muted"] if done else PALETTE["text_primary"],
                fg_color=PALETTE["accent"],
                hover_color=PALETTE["accent_hover"],
                checkmark_color="#FFFFFF",
                corner_radius=6,
                border_width=2,
                command=lambda t=task_id: self._complete_task(t),
            )
            cb.pack(anchor="w", padx=14, pady=10)
            if done:
                cb.select()
                cb.configure(state="disabled")

    def _add_task(self) -> None:
        name = self._task_entry.get().strip()
        if name:
            self._db.add_task(name)
            self._task_entry.delete(0, "end")
            self.load_tasks()
            self._on_stats()

    def _complete_task(self, task_id: int) -> None:
        self._db.complete_task(task_id)
        self.load_tasks()
        self._on_stats()

    # ── Timer ─────────────────────────────────
    def _start(self, mode: str) -> None:
        if self._is_running:
            return
        self._current_mode    = mode
        self._session_minutes = (
            int(self.opt_study.get()) if mode == "Study"
            else int(self.opt_break.get())
        )
        self._time_left  = self._session_minutes * 60
        self._is_running = True

        color = PALETTE["study"] if mode == "Study" else PALETTE["brk"]
        self._lbl_timer.configure(text_color=color)
        self._mode_lbl.configure(
            text="🔥  STUDY SESSION" if mode == "Study" else "☕  BREAK TIME",
            text_color=color,
        )
        self._create_mini(mode)
        self._tick()

    def _stop(self) -> None:
        self._is_running = False
        self._lbl_timer.configure(
            text=f"{int(self.opt_study.get()):02d}:00",
            text_color=PALETTE["timer_idle"],
        )
        self._mode_lbl.configure(text="IDLE", text_color=PALETTE["text_muted"])
        self._destroy_mini()

    def _tick(self) -> None:
        if self._is_running and self._time_left > 0:
            m, s     = divmod(self._time_left, 60)
            txt      = f"{m:02d}:{s:02d}"
            self._lbl_timer.configure(text=txt)
            if self._mini and self._mini.exists():
                self._mini.update_text(txt)
            self._time_left -= 1
            self.after(1000, self._tick)

        elif self._time_left == 0 and self._is_running:
            self._is_running = False
            self._destroy_mini()

            if self._current_mode == "Study":
                self._db.add_study_minutes(self._session_minutes)
                self._on_stats()

            self._restore_main()
            self._start("Break" if self._current_mode == "Study" else "Study")

    def _create_mini(self, mode: str) -> None:
        self._destroy_mini()
        self._mini = MiniTimer(
            self.winfo_toplevel(), mode=mode,
            on_click_restore=self._restore_main,
        )

    def _destroy_mini(self) -> None:
        if self._mini:
            self._mini.destroy()
            self._mini = None

    def _restore_main(self) -> None:
        win = self.winfo_toplevel()
        win.deiconify()
        win.lift()
        win.focus_force()
        win.attributes("-topmost", True)
        win.attributes("-topmost", False)
