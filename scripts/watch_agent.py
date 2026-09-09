#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Orkestratör — ajan izleme ağı (watch_agent v2).

Eski sistemdeki "herkes ne yapıyor" modelinin teknik ayağı:
  - Dosya değişiklik izleme (hash tabanlı, delta cache'li)
  - Kritik dosya seti (engine/, permission_router, entity_resolution vb.
    değişirse ACIL uyarı)
  - Ajan-edge haritası: her dosyanın hangi iç ajana ait olduğu
  - Log rotasyonu: watch_log.txt süresiz büyümesin

Kullanım:
    backup   -> data/watch/snapshot_baseline.json (ilk durum)
    diff     -> değişiklik raporu (delta cache ile)
    status   -> süreçler + scrape + görev panosu özeti
    watch    -> sürekli izleme (60 sn periyot)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = ROOT / "data" / "watch"
BASELINE = SNAP_DIR / "snapshot_baseline.json"
WATCH_LOG = SNAP_DIR / "watch_log.txt"
DELTA = SNAP_DIR / "watch_delta.json"

EXTENSIONS = {".py", ".md", ".json", ".jsonl", ".sql", ".bat", ".toml", ".txt", ".env"}
SKIP_DIRS = {".venv", "__pycache__", ".git", "node_modules", ".obsidian",
             ".pytest_cache", ".kilo", "backups", "logs", "watch", "test_reports"}
LOG_MAX_LINES = 4000  # rotasyon eşiği

# Kritik dosyalar: bu set değişirse ACIL uyarı (orkestratör müdahalesi gerekir)
KRITIK_DOSYALAR = frozenset({
    "src/company_master/engine/osint_engine.py",
    "src/company_master/engine/source_registry.py",
    "src/company_master/utils/scraping_permission_router.py",
    "src/company_master/etl/entity_resolution.py",
    "src/company_master/etl/nace_mapper.py",
    "src/company_master/etl/pipeline.py",
    "scripts/osint_engine.py",
    "scripts/post_scrape_workflow.py",
})


# Ajan-edge haritası: dizin/dosya -> sahip iç ajan (çakışma önleme rehberi)
def _dosyanin_ajani(rel: str) -> str | None:
    if rel.startswith("src/company_master/engine") or rel.startswith("src/company_master/utils"):
        return "web_kazima"
    if rel.startswith("src/company_master/etl") or rel.startswith("scripts/"):
        return "gelistirici"
    if rel.startswith("src/company_master/schema") or rel.startswith("src/company_master/db"):
        return "mimar"
    if rel.startswith("AI proje v1/V10/07_referanslar") or "meris_api" in rel:
        return "arastirmaci"
    if rel.startswith("tests/") or "kpi" in rel or "kalite" in rel.lower():
        return "kalite"
    if rel.startswith("AI proje v1/V10/08-Ajanlar") or rel.startswith("AI proje v1/V10/00-Home.md"):
        return "koordinator"
    return None


def _iter_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if Path(fn).suffix.lower() not in EXTENSIONS:
                continue
            p = Path(root) / fn
            rel = str(p.relative_to(ROOT))
            # Canlı scrape verisi izlenmez (dosya diff'te değerlendirilmez)
            if "firmalar_detayli.jsonl" in rel or ".scrape_state.json" in rel:
                continue
            try:
                digest = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            except OSError:
                continue
            yield rel, digest


def _file_map():
    return dict(_iter_files())


def _rotate_log() -> None:
    if WATCH_LOG.exists() and sum(1 for _ in WATCH_LOG.open(encoding="utf-8")) > LOG_MAX_LINES:
        lines = WATCH_LOG.read_text(encoding="utf-8").splitlines()
        WATCH_LOG.write_text("\n".join(lines[-LOG_MAX_LINES // 2:]) + "\n",
                             encoding="utf-8")


def _log(msg: str) -> None:
    satir = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(satir, flush=True)
    with WATCH_LOG.open("a", encoding="utf-8") as f:
        f.write(satir + "\n")
    _rotate_log()
# ---- komutlar ----
def cmd_backup() -> int:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": _file_map(),
    }
    BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if DELTA.exists():
        DELTA.unlink()
    print(f"Baseline kaydedildi: {len(data['files'])} dosya")
    return 0


def _delta_karsilastir() -> dict:
    """Baseline vs şimdi; dönüş: {tip: [rel,...]}, kritik değişim de ayrılır."""
    base = json.loads(BASELINE.read_text(encoding="utf-8"))["files"]
    now = _file_map()

    degisen = [rel for rel in base if now.get(rel) != base.get(rel)]
    yeni = [rel for rel in now if rel not in base]
    silinen = [rel for rel in base if rel not in now]
    kritik = [rel for rel in (degisen + yeni + silinen) if rel in KRITIK_DOSYALAR]

    return {
        "degisen": sorted(degisen),
        "yeni": sorted(yeni),
        "silinen": sorted(silinen),
        "kritik": sorted(kritik),
        "rapor_tarihi": datetime.now().isoformat(timespec="seconds"),
    }


def cmd_diff() -> int:
    if not BASELINE.exists():
        print("Baseline yok — once: python watch_agent.py backup")
        return 2
    d = _delta_karsilastir()
    toplam = len(d["degisen"]) + len(d["yeni"]) + len(d["silinen"])
    print(f"Degisen: {len(d['degisen'])} | Yeni: {len(d['yeni'])} | Silinen: {len(d['silinen'])}")
    for rel in (d["degisen"] + d["yeni"] + d["silinen"])[:60]:
        tip = "M" if rel in d["degisen"] else ("A" if rel in d["yeni"] else "D")
        ajan = _dosyanin_ajani(rel)
        e = f" [{ajan}]" if ajan else ""
        print(f"  [{tip}] {rel}{e}")
    if d["kritik"]:
        print("\n!! KRITIK DOSYA DEGISTI !!")
        for rel in d["kritik"]:
            print(f"   >>> {rel}")
    DELTA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if toplam else 0


def cmd_status() -> int:
    print("== Surecler ==")
    out = subprocess.run(
        ["powershell", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" "
         "| Select-Object ProcessId, CreationDate, CommandLine"],
        capture_output=True, text=True,
    )
    print(out.stdout.strip() if out.stdout.strip() else "(python sureci yok)")

    state = ROOT / "data" / "ostim" / ".scrape_state.json"
    if state.exists():
        print("\n== Scrape Durumu ==")
        print(state.read_text(encoding="utf-8"))

    board = ROOT / "data" / "orchestrator" / "task_board.json"
    if board.exists():
        try:
            gorevler = json.loads(board.read_text(encoding="utf-8"))
            aktif = [g for g in gorevler if g["durum"] not in ("done",)]
            print(f"\n== Görev Panosu: {len(aktif)} aktif görev ==")
            for g in aktif:
                print(f"  [{g['durum']}] {g['task_id']} -> {g['sahip']} | {g['baslik'][:45]}")
        except json.JSONDecodeError:
            print("\n(görev panosu okunamadı)")
    return 0


def cmd_watch(dakika: int = 1440) -> int:
    """Her 60 sn'de diff; yeni degisiklikleri loglar, kritik degisimi aninda uyarir."""
    if not BASELINE.exists():
        print("Baseline yok — once: python watch_agent.py backup")
        return 2
    seen: set[str] = set()
    son_sync = 0.0
    bitis = time.time() + dakika * 60
    while time.time() < bitis:
        d = _delta_karsilastir()
        toplam = d["degisen"] + d["yeni"] + d["silinen"]
        for rel in toplam:
            tip = "M" if rel in d["degisen"] else ("A" if rel in d["yeni"] else "D")
            anahtar = f"{tip}:{rel}"
            if anahtar not in seen:
                ajan = _dosyanin_ajani(rel)
                a = f" [{ajan}]" if ajan else ""
                _log(f"[{tip}]{a} {rel}")
                seen.add(anahtar)
        if d["kritik"]:
            _log("!!! KRITIK DOSYA DEGISTI: " + ", ".join(d["kritik"]))
        # K4: Her 5 dk'da AGENT_SYNC.md'yi guncelle
        if time.time() - son_sync > 300:
            try:
                from company_master.orchestrator import task_board as _tb
                _tb.agent_sync_yaz()
                son_sync = time.time()
            except Exception:
                pass  # watch_agent basarisiz olmasin
        time.sleep(60)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "diff"
    if cmd == "backup":
        sys.exit(cmd_backup())
    if cmd == "diff":
        sys.exit(cmd_diff())
    if cmd == "status":
        sys.exit(cmd_status())
    if cmd == "watch":
        dakika = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
        sys.exit(cmd_watch(dakika))
    print(__doc__)
    sys.exit(1)