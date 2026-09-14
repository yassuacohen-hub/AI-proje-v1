# -*- coding: utf-8 -*-
"""CL-02 — Performans benchmark pytestleri (sahte motor; DB gerektirmez).

Kapsam:
- benchmark_http.main esik karsilastirmasi (standart suite esik alti).
- Tekil kritik uclar icin p50 tavan kontrolu.
- Raporu data/orchestrator/benchmark/ altina yazar (CL-02 kilidi: scripts/).

Calistirma: python -m pytest tests/test_benchmark.py -v
"""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

import benchmark_http

RAPOR_DIR = KOK / "data" / "orchestrator" / "benchmark"


def _suite_json() -> dict:
    buf = io.StringIO()
    eski = sys.argv
    sys.argv = ["benchmark_http.py", "--suite", "--json"]
    try:
        with redirect_stdout(buf):
            kod = benchmark_http.main()
    finally:
        sys.argv = eski
    assert kod == 0, "benchmark suite esik asimi/hata ile bitti"
    return json.loads(buf.getvalue())


class TestBenchmarkSuiteEsikler:
    def test_standart_suite_tum_esikler_altinda(self):
        veri = _suite_json()
        assert veri["sonuclar"], "suite sonucu bos"
        for r in veri["sonuclar"]:
            assert r["durum"] == "OK", f"{r['url']} esik asimi: {r}"
            assert r["hata"] == 0, f"{r['url']} hatali istek: {r['hata']}"

    @pytest.mark.parametrize("url,tavan_ms", [
        ("/api/health", 50.0),
        ("/api/kpi", 150.0),
        ("/api/companies?limit=20", 200.0),
    ])
    def test_kritik_uc_p50_tavan(self, url, tavan_ms):
        sonuc = benchmark_http.kos(url, 40, 2)
        assert sonuc["hata"] == 0
        assert sonuc["p50_ms"] < tavan_ms, f"{url} p50={sonuc['p50_ms']}ms >= {tavan_ms}ms"


class TestBenchmarkRapor:
    def test_rapor_dosyasi_yazilir(self, tmp_path=None):
        veri = _suite_json()
        RAPOR_DIR.mkdir(parents=True, exist_ok=True)
        yol = RAPOR_DIR / "CL-02_benchmark_raporu.json"
        yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")
        assert yol.exists()
        okunan = json.loads(yol.read_text(encoding="utf-8"))
        assert len(okunan["sonuclar"]) == 5
