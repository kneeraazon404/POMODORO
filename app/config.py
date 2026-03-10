"""
app/config.py – Design tokens, palette, and cross-platform font resolver.

Two themes (dark / light) with carefully tuned contrast ratios.
Use set_theme("dark"|"light") to swap at runtime – the module-level
PALETTE dict is updated in-place so all subsequent widget reads get the
new values automatically.

Platform font families:
  macOS   → SF Pro Display  → Helvetica Neue
  Windows → Segoe UI        → Arial
  Linux   → Noto Sans       → Liberation Sans → DejaVu Sans → Ubuntu
"""
from __future__ import annotations
import platform

# ──────────────────────────────────────────────
# PALETTES
# ──────────────────────────────────────────────
_DARK: dict = {
    # Backgrounds
    "bg_deep":    "#0B0D13",
    "bg_panel":   "#10131C",
    "bg_card":    "#181C28",
    "bg_card2":   "#1C2033",
    "bg_input":   "#171A25",

    # Accent / Action
    "accent":        "#6C63FF",
    "accent_hover":  "#5750D9",
    "study":         "#FF6B6B",
    "study_hover":   "#D9534F",
    "brk":           "#43C6AC",
    "brk_hover":     "#2DA89B",
    "stop":          "#4E5575",
    "stop_hover":    "#363C58",

    # Text
    "text_primary":   "#ECEEF5",   # headers, labels – near white on dark
    "text_bright":    "#FFFFFF",   # goal item body / max contrast
    "text_secondary": "#A0A8C0",   # stats, hints – readable on dark bg
    "text_muted":     "#6E7698",   # placeholders – visible but subdued

    # Timer
    "timer_idle":  "#6C63FF",
    "timer_study": "#FF6B6B",
    "timer_break": "#43C6AC",

    # Goal card tints (Yearly / Quarterly / Monthly / Weekly)
    "goal_tints": ["#6C63FF", "#FF6B6B", "#43C6AC", "#F7B731"],

    # Sidebar nav
    "sidebar_nav_active": "#6C63FF",
    "sidebar_nav_hover":  "#1C2033",

    # Theme toggle icon
    "theme_icon": "☀️",   # shown in dark mode = click to go light
}

_LIGHT: dict = {
    # Backgrounds
    "bg_deep":    "#F0F3FB",
    "bg_panel":   "#E6EAF7",
    "bg_card":    "#FFFFFF",
    "bg_card2":   "#EBEFFa",
    "bg_input":   "#F5F7FF",

    # Accent / Action
    "accent":        "#5A52D5",
    "accent_hover":  "#4840B8",
    "study":         "#D94F4F",
    "study_hover":   "#B83838",
    "brk":           "#2A9E87",
    "brk_hover":     "#1E8067",
    "stop":          "#7B83A8",
    "stop_hover":    "#626A8C",

    # Text
    "text_primary":   "#1A1D35",   # near-black on light bg
    "text_bright":    "#0D0F1A",   # goal item body / max contrast
    "text_secondary": "#3D4470",   # stats, secondary – readable on white/light card
    "text_muted":     "#6B7299",   # placeholders – visible but subdued

    # Timer
    "timer_idle":  "#5A52D5",
    "timer_study": "#D94F4F",
    "timer_break": "#2A9E87",

    # Goal card tints
    "goal_tints": ["#5A52D5", "#D94F4F", "#2A9E87", "#C47B00"],

    # Sidebar nav
    "sidebar_nav_active": "#5A52D5",
    "sidebar_nav_hover":  "#DDE3F5",

    # Theme toggle icon
    "theme_icon": "🌙",   # shown in light mode = click to go dark
}

# ──────────────────────────────────────────────
# ACTIVE PALETTE  (mutable dict – updated in-place on toggle)
# ──────────────────────────────────────────────
PALETTE: dict = dict(_DARK)
_current_theme: str = "dark"


def set_theme(mode: str) -> None:
    """Swap PALETTE in-place to 'dark' or 'light'."""
    global _current_theme
    _current_theme = mode
    src = _DARK if mode == "dark" else _LIGHT
    PALETTE.clear()
    PALETTE.update(src)


def current_theme() -> str:
    return _current_theme


def ctk_appearance() -> str:
    """Return the CustomTkinter appearance mode string."""
    return "Dark" if _current_theme == "dark" else "Light"


# ──────────────────────────────────────────────
# FONT RESOLVER
# ──────────────────────────────────────────────
_PLATFORM = platform.system()

_FONT_FAMILIES: dict[str, list[str]] = {
    "Darwin":  ["SF Pro Display", "Helvetica Neue", "Arial"],
    "Windows": ["Segoe UI", "Arial", "Tahoma"],
    "Linux":   ["Noto Sans", "Liberation Sans", "DejaVu Sans", "Ubuntu", "Arial"],
}


def font(size: int = 14, weight: str = "normal") -> tuple[str, int, str]:
    families = _FONT_FAMILIES.get(_PLATFORM, _FONT_FAMILIES["Linux"])
    return (families[0], size, weight)


def font_bold(size: int = 14) -> tuple[str, int, str]:
    return font(size, "bold")
