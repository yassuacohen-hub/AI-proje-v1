#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix corrupted firmalar_vkn_ekli.jsonl - skip corrupt lines, keep valid ones."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "ostim" / "firmalar_vkn_ekli.jsonl"

if not INPUT.exists():
    print("File not found:", INPUT)
    exit(1)

with open(INPUT, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed = []
corrupt = 0
for i, line in enumerate(lines):
    if not line.strip():
        continue
    try:
        r = json.loads(line)
        fixed.append(json.dumps(r, ensure_ascii=False))
    except json.JSONDecodeError:
        corrupt += 1
        print(f"Corrupt line {i+1}: {line.strip()[:100]}...")
        # Try to extract partial JSON by finding the last valid field
        stripped = line.strip()
        # Try wrapping in a complete object if it was truncated from the beginning
        if stripped.startswith('"'):
            # The line is missing the opening bracket - try to reconstruct
            # Look for the pattern that indicates a truncated line
            pass

with open(INPUT, "w", encoding="utf-8") as f:
    for line in fixed:
        f.write(line + "\n")

vkn_count = sum(1 for r in (json.loads(l) for l in fixed) if r.get("vergi_no"))
print(f"Fixed: {len(fixed)} valid records, {corrupt} corrupt lines removed, {vkn_count} with VKN")
