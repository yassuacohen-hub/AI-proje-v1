#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-scrape workflow: ingest detail data, extract VKN from footers, recalculate quality.

Her adim alt process olarak calisir (import izolasyonu + ayri DB baglantisi).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

STEPS: list[tuple[str, str]] = [
    ("Adim 1: Detay verilerini DB'ye yaz", "ingest_ostim_detail.py"),
    ("Adim 2: Web footer'dan VKN cikar", "footer_vkn_extractor.py"),
    ("Adim 3: Kalite skorlarini yeniden hesapla", "recalculate_quality_scores.py"),
    ("Adim 4: KPI raporu uret", "generate_kpi_report.py"),
    # Job Intelligence adımları (mevcut pipeline SONUNDA calisir):
    ("Adim 5: Is ilanlarini DB'ye yaz", "ingest_job_postings.py"),
    ("Adim 6: Is ilani sinyallerini analiz et", "analyze_job_signals.py"),
    ("Adim 7: Istihbarat skorlarini hesapla", "recalc_intelligence_scores.py"),
]


def run_step(baslik: str, script: str) -> int:
    print(f"\n=== {baslik} ===")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        print(f"HATA: {script} rc={proc.returncode}")
    return proc.returncode


def run_vkn_validation() -> int:
    """VKN dogrulama ve duplicate filtreleme adimi.

    Hatalar bastirilmiyor; pipeline'in basarisiz donmesini sagliyor.
    Config'deki post_scrape ve quality_gate ayarlari kullaniliyor.
    """
    # Load config
    sys.path.insert(0, str(ROOT / "src"))
    from company_master.engine.quality_gate import load_quality_config

    cfg = load_quality_config()
    ps_cfg = cfg.get("post_scrape", {}) if cfg else {}
    if not ps_cfg.get("validate_vkn", True):
        print("[SKIP] VKN validation disabled in config")
        return 0

    input_path = ROOT / "data" / "ostim" / "firmalar_detayli.jsonl"
    output_path = ROOT / "data" / "ostim" / "firmalar_detayli_validated.jsonl"
    dedup = ps_cfg.get("dedup", True)
    dedup_fields = ps_cfg.get("dedup_fields", ["legal_name", "trade_name", "tax_number", "vergi_no"])
    min_score = cfg.get("quality_gate", {}).get("min_score", 30) if cfg else 30

    cmd = [
        sys.executable,
        str(SCRIPTS / "validate_vkn_duplicate.py"),
        str(input_path),
        str(output_path),
    ]
    if dedup:
        cmd.append("--dedup")
        cmd.extend(["--dedup-fields", ",".join(dedup_fields)])

    spam_filter = ps_cfg.get("spam_filter", {}) or {}
    if spam_filter.get("enabled", True):
        cmd.append("--spam-filter")
        cmd.extend(["--max-records-per-domain", str(spam_filter.get("max_records_per_domain", 500))])
        cmd.extend(["--max-records-per-nace", str(spam_filter.get("max_records_per_nace", 10000))])

    cmd.extend(["--min-score", str(min_score)])

    print("\n=== Adim 0: VKN Doğrulama ve Duplicate Filtreleme ===")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Dedup: {dedup}")
    print(f"  Fields: {dedup_fields}")

    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    if proc.returncode != 0:
        print(f"HATA: validate_vkn_duplicate.py rc={proc.returncode}")
    return proc.returncode


def main() -> int:
    # VKN validation ve duplicate filtreleme (pipelenin basinda)
    rc = run_vkn_validation()
    if rc != 0:
        return rc

    # Quality Gate adimi (pipelenin basinda)
    from company_master.engine.quality_gate import load_quality_config
    cfg = load_quality_config()
    qg_cfg = cfg.get("quality_gate", {}) if cfg else {}
    min_score = qg_cfg.get("min_score", 30.0)

    from company_master.engine.source_registry import registry
    from company_master.engine.quality_gate import QualityGate

    for sid, spec in registry().items():
        if not spec.enabled or not spec.output_path.exists():
            continue
        print(f"\n=== Quality Gate: {sid} ===")
        gate = QualityGate(min_score=min_score)
        output_path = spec.output_path.with_name(spec.output_path.stem + "_filtered.jsonl")
        try:
            report = gate.run(spec.output_path, output_path)
            print(report.summary())
        except Exception as exc:
            print(f"HATA: Quality Gate basarisiz: {exc}")
            return 1

    for baslik, script in STEPS:
        rc = run_step(baslik, script)
        if rc != 0:
            return rc
    print("\n=== Tum adimlar tamamlandi ===")
    # P0-2: Board'daki gorevi done isaretle
    try:
        import sys as _sys
        from pathlib import Path as _Path
        _sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
        from company_master.orchestrator import task_board as _tb
        _tb.gorev_guncelle("P0-2", durum="done", **{"not": "Otomatik tetiklendi"})
        _tb.handoff_yaz("P0-2", "Scrape pipeline tamamlandi", "P0-3 kalite kontrol")
    except Exception as exc:
        print(f"[UYARI] Gorev panosu guncellemesi basarisiz: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
