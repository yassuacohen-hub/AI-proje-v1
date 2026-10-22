#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lokal + VDS 9Router kombo UYE listelerini karsilastir (salt-okunur).

C yolunun veri katmani: data/router/kombo_soylenti.json uretir.
"""
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KOK = Path("Huginn Data Insights")
C IKI = None  # placeholder
