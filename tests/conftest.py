"""Make scripts/ importable as plain modules (the repo is scripts, not a package)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

REPO = Path(__file__).resolve().parent.parent
