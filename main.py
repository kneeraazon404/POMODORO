"""POMODORO – entry point."""
from __future__ import annotations
import pathlib
from app.ui.app import Pomodoro


def _set_icon(win: Pomodoro) -> None:
    """Set window icon from assets/icon.png (requires Pillow)."""
    icon_path = pathlib.Path(__file__).parent / "assets" / "icon.png"
    if not icon_path.exists():
        return
    try:
        from PIL import Image, ImageTk  # type: ignore
        img = ImageTk.PhotoImage(Image.open(icon_path).resize((64, 64)))
        win.wm_iconphoto(True, img)
        win._icon_ref = img  # prevent GC
    except Exception:
        pass  # Pillow not installed – skip icon silently


def main() -> None:
    app = Pomodoro()
    _set_icon(app)
    app.run()


if __name__ == "__main__":
    main()
