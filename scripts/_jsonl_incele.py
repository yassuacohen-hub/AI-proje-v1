# -*- coding: utf-8 -*-
"""JSONL ornek inceleme (Y2)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for osb in ("ivedik", "baskent"):
    lines = (ROOT / "data" / osb / "firmalar.jsonl").read_text(encoding="utf-8").splitlines()
    lines = [l for l in lines if l.strip()]
    rec = json.loads(lines[0])
    print("=" * 60)
    print(osb.upper(), "satir:", len(lines), "| alanlar:", sorted(rec.keys()))
    for i in (0, len(lines) // 2, -1):
        r = json.loads(lines[i])
        print(f"  [{i}] unvan={r.get('unvan')!r} tel={len(r.get('telefonlar') or [])} mail={len(r.get('emailler') or [])} web={bool(r.get('web_sitesi'))} adres={bool(r.get('adres'))} vkn={bool(r.get('vergi_no'))} sektor={r.get('sektor')!r}")
    # bos unvan / tekrar sayimi
    bos = sum(1 for l in lines if not (json.loads(l).get("unvan") or "").strip())
    print("  bos unvan:", bos)
