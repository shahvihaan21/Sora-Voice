"Compatibility export for the existing PyQt HUD."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[2] / 'aegis'
if str(_AEGIS) not in sys.path: sys.path.insert(0, str(_AEGIS))
from aegis.UI.main_window import MainWindow
__all__ = ['MainWindow']
