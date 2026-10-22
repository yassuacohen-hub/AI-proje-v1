# -*- coding: utf-8 -*-
"""Toplu durum olcumu -> _tmp/durum_olc.txt (terminal ciktisi filtrelenebiliyor)."""
import json
import subprocess
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent / "Huginn Data Insights"
CIKTI = Path(__file__).resolve().parent / "durum_olc.txt"
r: list[str] = []


def git(*a: str) -> str:
    p = subprocess.run(["git", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (p.stdout + p.stderr).strip()


msg = KOK / "data/orchestrator/chat/messages.jsonl"
satir = msg.read_text(encoding="utf-8-sig").splitlines()
r.append(f"messages.jsonl satir={len(satir)} bayt={msg.stat().st_size}")

kayit = {}
for dosya in ("agent_registry.json",):
    p = KOK / "data/orchestrator" / dosya
    r.append(f"{dosya} var={p.exists()}")
    if p.exists():
        t = p.read_text(encoding="utf-8-sig")
        r.append(f"  'nur' gecen yer sayisi={t.lower().count('nur')}")
        try:
            d = json.loads(t)
            anahtarlar = list(d.keys()) if isinstance(d, dict) else [type(d).__name__]
            r.append(f"  ust anahtarlar={anahtarlar[:15]}")
            ajanlar = d.get("agents", d) if isinstance(d, dict) else d
            if isinstance(ajanlar, dict):
                r.append(f"  ajan adlari={list(ajanlar.keys())}")
            elif isinstance(ajanlar, list):
                r.append(f"  ajan adlari={[a.get('id') or a.get('name') for a in ajanlar if isinstance(a, dict)]}")
        except ValueError as e:
            r.append(f"  json hata {e}")

tb = KOK / "data/orchestrator/task_board.json"
d = json.loads(tb.read_text(encoding="utf-8-sig"))
gorevler = d.get("tasks", d) if isinstance(d, dict) else d
if isinstance(gorevler, dict):
    gorevler = list(gorevler.values())
r.append(f"task_board gorev sayisi={len(gorevler)}")
for g in gorevler:
    if not isinstance(g, dict):
        continue
    tid = str(g.get("id") or g.get("task_id"))
    if any(k in tid for k in ("MUSTERI-PANEL", "MAIL-SAGLAYICI", "VERI-KAP")):
        r.append(f"  {tid} durum={g.get('durum') or g.get('status')} sahip={g.get('sahip') or g.get('owner')}")

r.append("--- son 12 commit ---")
r.append(git("log", "--oneline", "-12", "--format=%h %s"))
r.append("--- panel-tasarim hex ---")
r.append(git("status", "--short", "--", "data/orchestrator/chat")[:500] or "(chat temiz)")
CIKTI.write_text("\n".join(r) + "\n", encoding="utf-8")
print("tamam")
