"""
Desktop Assistant Runner
Simple launcher for the Desktop Assistant
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import main
from main import main

if __name__ == "__main__":
    # Run the assistant
    exit_code = main()
    sys.exit(exit_code)
