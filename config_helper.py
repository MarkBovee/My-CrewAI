#!/usr/bin/env python3
"""
Convenience script to run configuration helper from project root
"""
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from instagram.helpers.config_helper import main

if __name__ == "__main__":
    main()