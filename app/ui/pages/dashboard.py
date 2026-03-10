"""
app/ui/pages/dashboard.py – Dashboard & Goals page with full CRUD goal cards.

• Goal item body text: 16 pt, text_bright (maximum contrast in both themes)
• apply_theme() rebuilds the whole page content so every widget picks up
  the new PALETTE values from config.
"""
from __future__ import annotations
import customtkinter as ctk
from app.config import PALETTE, font, font_bold
from app.database import Database


# ─────────────────────────────────────────────
# GOAL ITEM ROW
# ─────────────────────────────────────────────
class _GoalItemRow(ctk.CTkFrame):
    """One saved goal item: bullet + text + ✏ edit + ✕ delete."""

    def __init__(self, parent, item_id: int, content: str, tint: str,
                 on_save, on_delete) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self._item_id   = item_id
        self._on_save   = on_save
        self._on_delete = on_delete
        self._editing   = False
        self._tint      = tint
        self._build(content)

    def _build(self, content: str) -> None:
        self.columnconfigure(0, weight=1)

        # ── View row ──────────────────────────
        self._view = ctk.CTkFrame(self, fg_color="transparent")
        self._view.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._view.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self._view, text="•", font=font_bold(18),
            text_color=self._tint, width=20,
        ).grid(row=0, column=0, padx=(6, 6), pady=8, sticky="n")

        self._lbl = ctk.CTkLabel(
            self._view, text=content,
            font=font(16),                          # ← one size bigger
            text_color=PALETTE["text_bright"],      # ← maximum contrast
            anchor="w", justify="left", wraplength=340,
        )
        self._lbl.grid(row=0, column=1, sticky="ew", pady=8)

        # ── Action buttons ────────────────────
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e", padx=(0, 8))

        self._btn_edit = ctk.CTkButton(
            btns, text="📝", width=38, height=32, corner_radius=8,
            fg_color=PALETTE["bg_card2"], hover_color=PALETTE["accent"],
            text_color=PALETTE["text_secondary"], font=font(15),
            command=self._toggle_edit,
        )
        self._btn_edit.pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btns, text="🗑", width=38, height=32, corner_radius=8,
            fg_color=PALETTE["bg_card2"], hover_color=PALETTE["study"],
            text_color=PALETTE["text_secondary"], font=font(15),
            command=lambda: self._on_delete(self._item_id),
        ).pack(side="left")

        # ── Edit row (hidden until activated) ─
        self._edit_row = ctk.CTkFrame(self, fg_color="transparent")

        self._entry = ctk.CTkEntry(
            self._edit_row, height=36, corner_radius=8,
            fg_color=PALETTE["bg_input"],
            border_color=self._tint, border_width=1,
            text_color=PALETTE["text_bright"], font=font(15),
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(6, 8))
        self._entry.bind("<Return>", lambda _e: self._commit())
        self._entry.bind("<Escape>", lambda _e: self._cancel())

        ctk.CTkButton(
            self._edit_row, text="Save", width=64, height=36,
            corner_radius=8, fg_color=self._tint,
            hover_color=PALETTE["accent_hover"],
            text_color="#FFFFFF", font=font_bold(13),
            command=self._commit,
        ).pack(side="left", padx=(0, 6))

    def _toggle_edit(self) -> None:
        self._editing = not self._editing
        if self._editing:
            self._view.grid_remove()
            self._edit_row.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=4, pady=4)
            self._entry.delete(0, "end")
            self._entry.insert(0, self._lbl.cget("text"))
            self._entry.focus_set()
        else:
            self._cancel()

    def _commit(self) -> None:
        txt = self._entry.get().strip()
        if txt:
            self._lbl.configure(text=txt)
            self._on_save(self._item_id, txt)
        self._cancel()

    def _cancel(self) -> None:
        self._editing = False
        self._edit_row.grid_remove()
        self._view.grid()


# ─────────────────────────────────────────────
# GOAL CARD
# ─────────────────────────────────────────────
class _GoalCard(ctk.CTkFrame):
    """Card for one goal type with a full CRUD item list."""

    def __init__(self, parent, goal_type: str, tint: str, db: Database) -> None:
        super().__init__(
            parent,
            fg_color=PALETTE["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=PALETTE["bg_card2"],
        )
        self._type  = goal_type
        self._tint  = tint
        self._db    = db
        self._build()
        self._load()

    def _build(self) -> None:
        # Left accent bar
        ctk.CTkFrame(self, width=6, corner_radius=0,
                      fg_color=self._tint).pack(side="left", fill="y")

        self._inner = ctk.CTkFrame(self, fg_color="transparent")
        self._inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        # Header
        hdr = ctk.CTkFrame(self._inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 8))

        badge = ctk.CTkFrame(hdr, fg_color=self._tint, corner_radius=6)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=f"  {self._type.upper()}  ",
                     font=font_bold(11), text_color="#FFFFFF").pack(padx=4, pady=3)

        self._title_lbl = ctk.CTkLabel(
            hdr, text=" Goals", font=font_bold(18),
            text_color=PALETTE["text_primary"],
        )
        self._title_lbl.pack(side="left")

        # Items container (content-height driven)
        self._items_frame = ctk.CTkFrame(self._inner, fg_color="transparent")
        self._items_frame.pack(fill="x", pady=(0, 8))
        self._items_frame.columnconfigure(0, weight=1)

        # Add row
        add_row = ctk.CTkFrame(self._inner, fg_color="transparent")
        add_row.pack(fill="x")

        self._add_entry = ctk.CTkEntry(
            add_row,
            placeholder_text=f"Add a {self._type.lower()} goal …",
            height=36, corner_radius=9,
            fg_color=PALETTE["bg_input"],
            border_color=PALETTE["bg_card2"], border_width=1,
            text_color=PALETTE["text_bright"],
            placeholder_text_color=PALETTE["text_muted"],
            font=font(14),
        )
        self._add_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._add_entry.bind("<Return>", lambda _e: self._add_item())

        ctk.CTkButton(
            add_row, text="＋", width=36, height=36, corner_radius=9,
            fg_color=self._tint, hover_color=PALETTE["accent_hover"],
            text_color="#FFFFFF", font=font_bold(16),
            command=self._add_item,
        ).pack(side="left")

    def _load(self) -> None:
        for w in self._items_frame.winfo_children():
            w.destroy()

        rows = self._db.get_goal_items(self._type)
        if not rows:
            ctk.CTkLabel(
                self._items_frame,
                text="No goals yet — add one below",
                font=font(14), text_color=PALETTE["text_muted"],
            ).grid(row=0, column=0, sticky="w", padx=8, pady=6)
            return

        for idx, (item_id, content) in enumerate(rows):
            if idx > 0:
                ctk.CTkFrame(self._items_frame, height=1,
                              fg_color=PALETTE["bg_card2"],
                              corner_radius=0).grid(
                    row=idx * 2 - 1, column=0, sticky="ew", padx=8
                )
            _GoalItemRow(
                self._items_frame,
                item_id=item_id, content=content, tint=self._tint,
                on_save=self._save_item, on_delete=self._delete_item,
            ).grid(row=idx * 2, column=0, sticky="ew")

    def _add_item(self) -> None:
        txt = self._add_entry.get().strip()
        if txt:
            self._db.add_goal_item(self._type, txt)
            self._add_entry.delete(0, "end")
            self._load()

    def _save_item(self, item_id: int, content: str) -> None:
        self._db.update_goal_item(item_id, content)

    def _delete_item(self, item_id: int) -> None:
        self._db.delete_goal_item(item_id)
        self._load()

    def apply_theme(self) -> None:
        """Reconfigure all explicitly-colored widgets with current PALETTE."""
        self.configure(
            fg_color=PALETTE["bg_card"],
            border_color=PALETTE["bg_card2"],
        )
        self._title_lbl.configure(text_color=PALETTE["text_primary"])
        self._add_entry.configure(
            fg_color=PALETTE["bg_input"],
            border_color=PALETTE["bg_card2"],
            text_color=PALETTE["text_bright"],
            placeholder_text_color=PALETTE["text_muted"],
        )
        self._load()   # recreates item rows with fresh palette colours


# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────
class DashboardPage(ctk.CTkFrame):
    GOALS = ["Yearly", "Quarterly", "Monthly", "Weekly"]

    def __init__(self, parent, db: Database, on_view_ledger, on_toggle_theme) -> None:
        super().__init__(parent, fg_color=PALETTE["bg_deep"], corner_radius=0)
        self._db             = db
        self._on_ledger      = on_view_ledger
        self._on_toggle_theme = on_toggle_theme
        self._cards: list[_GoalCard] = []
        self._build()

    # ── Build ─────────────────────────────────
    def _build(self) -> None:
        self._build_header()
        self._build_stats_bar()
        self._build_goals_section()

    def _build_header(self) -> None:
        self._hdr = ctk.CTkFrame(self, height=72,
                                  fg_color=PALETTE["bg_panel"], corner_radius=0)
        self._hdr.pack(fill="x")
        self._hdr.pack_propagate(False)

        self._hdr_lbl = ctk.CTkLabel(
            self._hdr, text="Dashboard",
            font=font_bold(24), text_color=PALETTE["text_primary"],
        )
        self._hdr_lbl.pack(side="left", padx=30, pady=18)

        # Ledger far-right, theme icon just inside it
        self._ledger_btn = ctk.CTkButton(
            self._hdr, text="📅  Ledger",
            width=130, height=38, corner_radius=10,
            fg_color=PALETTE["stop"], hover_color=PALETTE["stop_hover"],
            font=font_bold(13), command=self._on_ledger,
        )
        self._ledger_btn.pack(side="right", padx=(0, 14), pady=18)

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
        self._theme_btn.pack(side="right", padx=(0, 6), pady=18)

    def _build_stats_bar(self) -> None:
        self._stats_bar = ctk.CTkFrame(self, height=58,
                                        fg_color=PALETTE["bg_card"], corner_radius=0)
        self._stats_bar.pack(fill="x")
        self._stats_bar.pack_propagate(False)

        self._stats_var = ctk.StringVar(value="Loading …")
        self._stats_lbl = ctk.CTkLabel(
            self._stats_bar, textvariable=self._stats_var,
            font=font(14), text_color=PALETTE["text_secondary"],
        )
        self._stats_lbl.pack(expand=True)

    def _build_goals_section(self) -> None:
        tints = PALETTE["goal_tints"]

        self._section_lbl = ctk.CTkLabel(
            self, text="🎯  High-Level Goals",
            font=font_bold(20), text_color=PALETTE["text_primary"],
        )
        self._section_lbl.pack(anchor="w", padx=28, pady=(20, 8))

        self._scroller = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=PALETTE["accent"], corner_radius=0,
        )
        self._scroller.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        self._cards.clear()
        for i, goal in enumerate(self.GOALS):
            card = _GoalCard(self._scroller, goal_type=goal,
                              tint=tints[i], db=self._db)
            card.pack(fill="x", pady=10, padx=4)
            self._cards.append(card)

    # ── Public API ────────────────────────────
    def refresh_stats(self) -> None:
        mins        = self._db.get_study_minutes()
        hrs         = round(mins / 60, 2)
        total, done = self._db.count_tasks()
        self._stats_var.set(
            f"📅  {self._db.today}"
            f"     ⏱  Study: {hrs} hrs ({mins} min)"
            f"     ✅  Tasks: {done} / {total}"
        )

    def load_goals(self) -> None:
        pass  # cards auto-load on construction

    def apply_theme(self) -> None:
        self.configure(fg_color=PALETTE["bg_deep"])
        self._hdr.configure(fg_color=PALETTE["bg_panel"])
        self._hdr_lbl.configure(text_color=PALETTE["text_primary"])
        self._theme_btn.configure(
            text=PALETTE["theme_icon"],
            fg_color=PALETTE["bg_card2"],
            hover_color=PALETTE["sidebar_nav_hover"],
            text_color=PALETTE["text_primary"],
        )
        self._ledger_btn.configure(
            fg_color=PALETTE["stop"], hover_color=PALETTE["stop_hover"]
        )
        self._stats_bar.configure(fg_color=PALETTE["bg_card"])
        self._stats_lbl.configure(text_color=PALETTE["text_secondary"])
        self._section_lbl.configure(text_color=PALETTE["text_primary"])
        self._scroller.configure(scrollbar_button_color=PALETTE["accent"])
        for card in self._cards:
            card.apply_theme()
