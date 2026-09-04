"Compatibility export for the established Sora dark HUD stylesheet."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[2] / 'aegis'
if str(_AEGIS) not in sys.path: sys.path.insert(0, str(_AEGIS))
from aegis.UI.styles import MAIN_STYLE
__all__ = ['MAIN_STYLE']
