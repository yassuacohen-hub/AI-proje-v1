# -*- coding: utf-8 -*-
"""OSINT Scraper Motoru — cekirdek orkestrator.

Kullanim:
    python -m company_master.engine.osint_engine status
    python -m company_master.engine.osint_engine check ostim-detail
    python -m company_master.engine.osint_engine run aso
    python -m company_master.engine.osint_engine pipeline ostim-detail
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .source_registry import SourceSpec, registry

ROOT = Path(__file__).resolve().parents[3]
STATE_FILE = ROOT / "data" / "osint_engine_state.json"
POST_SCRAPE = ROOT / "scripts" / "post_scrape_workflow.py"


# ---- durum yonetimi ----
def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _update_state(source_id: str, **fields) -> None:
    state = _load_state()
    entry = state.get(source_id, {})
    entry.update(fields)
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    state[source_id] = entry
    _save_state(state)


# ---- motor komutlari ----
def cmd_status() -> int:
    """Tum kaynaklarin ozeti + router politikalari."""
    from ..utils.scraping_permission_router import get_router

    state = _load_state()
    print("== OSINT Scraper Motoru — Kaynak Durumu ==")
    for sid, spec in registry().items():
        st = state.get(sid, {})
        durum = st.get("last_status", "bilinmiyor")
        bayt = (
            f"{spec.output_path.stat().st_size:,} bytes"
            if spec.output_path.exists()
            else "dosya yok"
        )
        print(
            f"  [{sid}] {spec.display_name}\n"
            f"      domain={spec.domain} | durum={durum} | cikti={bayt}\n"
            f"      enabled={spec.enabled} | pipeline={spec.pipeline} | {spec.note}"
        )
    print("\n== Router Politikalari ==")
    for d, info in get_router().status().items():
        print(f"  {d}: interval={info['min_interval']}s kvkk_safe={info['kvkk_safe']}")
    return 0


def cmd_check(source_id: str) -> int:
    """Kaynak icin izin kontrolu (robots.txt + KVKK + politika)."""
    from ..utils.scraping_permission_router import get_router

    spec = registry().get(source_id)
    if not spec:
        print(f"Bilinmeyen kaynak: {source_id}")
        return 1
    url = f"https://{spec.domain}/"
    dec = get_router().check(url)
    print(f"[{spec.source_id}] {url} -> allowed={dec.allowed} ({dec.reason})")
    return 0 if dec.allowed else 2


def cmd_run(source_id: str) -> int:
    """Kaynagi scraper'i ile calistir (detached degil; senkron)."""
    spec = registry().get(source_id)
    if not spec:
        print(f"Bilinmeyen kaynak: {source_id}")
        return 1
    if not spec.enabled:
        print(f"[{source_id}] kapali — {spec.note}")
        return 2

    _update_state(source_id, last_status="scraping",
                  started_at=datetime.now().isoformat(timespec="seconds"))
    try:
        if spec.scraper_cli:
            proc = subprocess.run(
                [sys.executable, str(spec.scraper_cli_path)],
                cwd=str(ROOT),
            )
            rc = proc.returncode
        elif spec.scraper_module:
            proc = subprocess.run(
                [
                    sys.executable, "-c",
                    f"import sys; sys.path.insert(0, {str(ROOT / 'src')!r}); "
                    f"import importlib; m = importlib.import_module({spec.scraper_module!r}); "
                    "m.run_full_scrape()",
                ],
                cwd=str(ROOT),
            )
            rc = proc.returncode
        else:
            print(f"[{source_id}] scraper tanimli degil")
            _update_state(source_id, last_status="scraper-yok")
            return 2
    except KeyboardInterrupt:
        _update_state(source_id, last_status="kesildi")
        return 130

    _update_state(
        source_id,
        last_status="tamamlandi" if rc == 0 else f"hata(rc={rc})",
        finished_at=datetime.now().isoformat(timespec="seconds"),
    )
    if rc == 0 and spec.pipeline:
        print(f"[{source_id}] scrape tamam — pipeline baslatiliyor")
        return cmd_pipeline(source_id)
    return rc


def cmd_pipeline(source_id: str) -> int:
    """Post-scrape pipeline: ingest -> VKN -> recalc -> KPI."""
    spec = registry().get(source_id)
    if not spec:
        print(f"Bilinmeyen kaynak: {source_id}")
        return 1
    _update_state(source_id, last_status="pipeline")
    proc = subprocess.run(
        [sys.executable, str(POST_SCRAPE)], cwd=str(ROOT)
    )
    _update_state(
        source_id,
        last_status="pipeline-ok" if proc.returncode == 0
        else f"pipeline-hata(rc={proc.returncode})",
    )
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="osint-engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    p_check = sub.add_parser("check")
    p_check.add_argument("source_id")
    p_run = sub.add_parser("run")
    p_run.add_argument("source_id")
    p_pipe = sub.add_parser("pipeline")
    p_pipe.add_argument("source_id")
    args = parser.parse_args(argv)

    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "check":
        return cmd_check(args.source_id)
    if args.cmd == "run":
        return cmd_run(args.source_id)
    if args.cmd == "pipeline":
        return cmd_pipeline(args.source_id)
    return 1


if __name__ == "__main__":
    sys.exit(main())