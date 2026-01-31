"""Entry point for running neuromorpho_analyzer as a module.

Usage:
    python -m neuromorpho_analyzer          # Launch GUI
    python -m neuromorpho_analyzer gui      # Launch GUI
    python -m neuromorpho_analyzer import   # Import data
    python -m neuromorpho_analyzer --help   # Show help
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
