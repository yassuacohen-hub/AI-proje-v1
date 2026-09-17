# -*- coding: utf-8 -*-
"""Add the research task trigger."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.orchestrator import trigger

# Add trigger for roo to research ponytail vs caveman
result = trigger.tetik_ekle(
    "RESEARCH-PONYTALE",
    "roo",
    "Ponytail vs Caveman derinlemesine arastirma: ikisini karsilastir, en iyi secenegi ve calisma sistemini optimize et. Teslim: data/orchestrator/RESEARCH-PONYTALE_rapor.md"
)
print(f"Trigger added: {result}")
