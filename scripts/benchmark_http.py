# -*- coding: utf-8 -*-
"""CL-02 — HTTP yuk testi yardimcisi (sahte motor + TestClient).

Kullanim:
    python scripts/benchmark_http.py --url /api/health --n 200 --c 8
    python scripts/benchmark_http.py --suite            # standart senaryo seti
    python scripts/benchmark_http.py --suite --json     # makine okunur cikti

Not: TestClient ASGI transport kullanir (ag yigini yok); sonuclar
goreceli karsilastirma icindir, uretim esigi degildir.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "src"))

import web_app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from web_app import app  # noqa: E402


class _Sonuc:
    def __init__(self, first=None, rows=None, scalar=None):
        self._first = first
        self._rows = list(rows) if rows else []
        self._scalar = scalar

    def first(self):
        return self._first

    def mappings(self):
        return self

    def all(self):
        return self._rows

    def scalar(self):
        return self._scalar


class _KilitliKuyruk:
    """Thread-guvenli sonsuz sahte-sonuc kaynagi."""

    def __init__(self, fabrika):
        self._fabrika = fabrika
        self._kilit = threading.Lock()
        self.executed = 0

    def sonuclari_yenile(self):
        with self._kilit:
            self._sonuclar = list(self._fabrika())

    def al(self):
        with self._kilit:
            self.executed += 1
            if not self._sonuclar:
                self._sonuclar = list(self._fabrika())
            return self._sonuclar.pop(0)


class _FakeConn:
    def __init__(self, kuyruk: _KilitliKuyruk):
        self._kuyruk = kuyruk

    def execute(self, stmt, *args, **kwargs):
        return self._kuyruk.al()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeEngine:
    def __init__(self, kuyruk: _KilitliKuyruk):
        self._kuyruk = kuyruk

    def connect(self):
        return _FakeConn(self._kuyruk)

    def begin(self):
        return _FakeConn(self._kuyruk)


def _fabrika_sec(url: str):
    if url.startswith("/api/companies/export"):
        return lambda: [_Sonuc(scalar=2), _Sonuc(rows=[
            {"legal_name": "FIRMA A", "data_quality_score": 70.0},
            {"legal_name": "FIRMA B", "data_quality_score": 55.0},
        ])]
    if url.startswith("/api/companies"):
        return lambda: [_Sonuc(scalar=2), _Sonuc(rows=[
            {"legal_name": "FIRMA A", "data_quality_score": 70.0},
            {"legal_name": "FIRMA B", "data_quality_score": 55.0},
        ])]
    if url.startswith("/api/kpi"):
        return lambda: [_Sonuc(first={"total": 10, "avg_score": 42.0})]
    if url.startswith("/api/intelligence/dashboard"):
        return lambda: [
            _Sonuc(rows=[{"signal_type": "growth", "cnt": 2}]),
            _Sonuc(rows=[{"cnt": 1}]),
            _Sonuc(rows=[]), _Sonuc(rows=[]),
            _Sonuc(rows=[]), _Sonuc(rows=[]), _Sonuc(rows=[]),
        ]
    return lambda: [_Sonuc()]


def _istatistik(sureler: list[float]) -> dict:
    s = sorted(sureler)
    n = len(s)
    return {
        "n": n,
        "min_ms": round(s[0] * 1000, 3),
        "p50_ms": round(s[n // 2] * 1000, 3),
        "p95_ms": round(s[int(n * 0.95) - 1] * 1000, 3) if n >= 20 else round(s[-1] * 1000, 3),
        "max_ms": round(s[-1] * 1000, 3),
        "ort_ms": round(sum(s) / n * 1000, 3),
    }


def kos(url: str, n: int = 100, c: int = 4) -> dict:
    kuyruk = _KilitliKuyruk(_fabrika_sec(url))
    kuyruk.sonuclari_yenile()
    web_app.get_engine = lambda: _FakeEngine(kuyruk)
    web_app.DASH_API_KEY = ""
    web_app._RATE_LIMIT.clear()
    sonuclar: list[float] = []
    hatalar = 0
    kilit = threading.Lock()

    def _tek() -> None:
        nonlocal hatalar
        with TestClient(app) as client:
            basla = time.perf_counter()
            r = client.get(url)
            gecen = time.perf_counter() - basla
        with kilit:
            if r.status_code == 200:
                sonuclar.append(gecen)
            else:
                hatalar += 1

    def _isci(kacar: int) -> None:
        for _ in range(kacar):
            _tek()

    dagilim = [n // c] * c
    for i in range(n % c):
        dagilim[i] += 1
    basla = time.perf_counter()
    threads = [threading.Thread(target=_isci, args=(k,)) for k in dagilim]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duvar = time.perf_counter() - basla
    ist = _istatistik(sonuclar) if sonuclar else {"n": 0}
    ist.update({
        "url": url,
        "es_zamanlilik": c,
        "duvar_suresi_sn": round(duvar, 3),
        "rps": round(len(sonuclar) / duvar, 1) if duvar else 0.0,
        "hata": hatalar,
    })
    return ist


STANDART_SUITE = [
    ("/api/health", 200, 8),
    ("/api/kpi", 100, 4),
    ("/api/companies?limit=20", 100, 4),
    ("/api/companies/export?format=csv&mask=1", 50, 2),
    ("/api/intelligence/dashboard", 50, 2),
]

ESIKLER_MS = {
    "/api/health": 50.0,
    "/api/kpi": 150.0,
    "/api/companies?limit=20": 200.0,
    "/api/companies/export?format=csv&mask=1": 500.0,
    "/api/intelligence/dashboard": 500.0,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="CL-02 HTTP benchmark")
    ap.add_argument("--url", default="/api/health")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--c", type=int, default=4)
    ap.add_argument("--suite", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    hedefler = STANDART_SUITE if a.suite else [(a.url, a.n, a.c)]
    rapor = [kos(u, n, c) for u, n, c in hedefler]
    kotu = []
    for r in rapor:
        esik = ESIKLER_MS.get(r["url"])
        durum = "OK"
        if esik and r.get("p50_ms", 0) > esik:
            durum = "ESIK-ASIMI"
            kotu.append(r["url"])
        r["esik_ms"] = esik
        r["durum"] = durum
        if r.get("hata"):
            kotu.append(f"{r['url']} (hata={r['hata']})")
    if a.json:
        print(json.dumps({"tarih": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "sonuclar": rapor},
                         ensure_ascii=False, indent=2))
    else:
        for r in rapor:
            print(f"{r['url']}: n={r['n']} p50={r.get('p50_ms')}ms "
                  f"p95={r.get('p95_ms')}ms rps={r['rps']} hata={r['hata']} "
                  f"esik={r.get('esik_ms')}ms [{r['durum']}]")
    return 1 if kotu else 0


if __name__ == "__main__":
    sys.exit(main())
