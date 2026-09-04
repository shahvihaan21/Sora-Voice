"Compatibility export for the established waveform visualizer."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[3] / 'aegis'
if str(_AEGIS) not in sys.path: sys.path.insert(0, str(_AEGIS))
from aegis.UI.widgets.visualizer import AudioVisualizer, VisualizerMode
__all__ = ['AudioVisualizer', 'VisualizerMode']
