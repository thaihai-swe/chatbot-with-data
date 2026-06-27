#!/usr/bin/env python3
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
_PARENT = str(_SCRIPT_DIR.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from core.template_engine import main

if __name__ == "__main__":
    main()
