import sys
import os
from pathlib import Path

# Add workspace root and aegis directory to sys.path so pytest can discover aegis package
root_dir = Path(__file__).resolve().parent
aegis_dir = root_dir / "aegis"
for p in (str(root_dir), str(aegis_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

if sys.platform.startswith("linux") and not os.getenv("DISPLAY") and not os.getenv("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
