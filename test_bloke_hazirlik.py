# -*- coding: utf-8 -*-
"""
TEST-BLOKE-FAKTOR-ARASTIRMA-01 — Test Hazırlık Scripti
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEVAM_EDEN_GOREVLER = ["API-14", "API-16", "UI-20", "API-21", "UI-22"]

print("TEST-BLOKE-FAKTOR-ARASTIRMA-01 research takibi aktif")
print(f"Devam eden görevler: {DEVAM_EDEN_GOREVLER}")