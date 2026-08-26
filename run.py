#!/usr/bin/env python
"""
Sora AI (v2.0) - Root Launcher
"""
import sys
from pathlib import Path

# Add 'aegis' directory to sys.path
root_dir = Path(__file__).resolve().parent
aegis_dir = root_dir / "aegis"
if str(aegis_dir) not in sys.path:
    sys.path.insert(0, str(aegis_dir))

from aegis.main import main

if __name__ == "__main__":
    main()
