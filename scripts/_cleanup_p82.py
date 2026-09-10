#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clean up temporary check scripts."""
from pathlib import Path
import os

scripts_dir = Path(__file__).resolve().parent
for f in scripts_dir.glob("_p82_*.py"):
    f.unlink()
    print(f"Deleted: {f}")
