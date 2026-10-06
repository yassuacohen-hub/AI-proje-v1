"""API istek loglama yardimcisi (ALTYAPI-API-ANALYTICS-LOGLAMA-01).

`api_analytics` tablosuna per-request log yazar.
"""
from __future__ import annotations

import time
from typing import Optional

from company_master.db.connection import get_engine
from sqlalchemy import text


def log_api_request(
    endpoint: str,
    method: str = "GET",
    status: int = 200,
    sure_ms: int = 0,
    kullanici: Optional[str] = None,
    hata_mesaji: Optional[str] = None,
) -> None:
    """
    API istegini `api_analytics` tablosuna yazar.

    Args:
        endpoint: Istek edilen endpoint (orn. "/api/companies")
        method: HTTP metodu (GET, POST, PUT, DELETE)
        status: HTTP status kodu
        sure_ms: Yanit suresi (milisaniye)
        kullanici: Ajan/kullanici adi (opsiyonel)
        hata_mesaji: Hata mesaji (4xx/5xx icin, opsiyonel)
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO api_analytics (endpoint, method, status, sure_ms, username, hata_mesaji)
                    VALUES (:endpoint, :method, :status, :sure_ms, :kullanici, :hata_mesaji)
                    """
                ),
                {
                    "endpoint": endpoint,
                    "method": method,
                    "status": status,
                    "sure_ms": sure_ms,
                    "kullanici": kullanici,
                    "hata_mesaji": hata_mesaji,
                },
            )
            conn.commit()
    except Exception as exc:
        # Loglama hatasi uygulamanin akisini bloklamamali
        # Sadece console'a yaz (gercek loglama icin structlog/print kullanilabilir)
        print(f"[api_logger] Yazim hatasi: {exc}")


def log_api_timed(endpoint: str, method: str = "GET", kullanici: Optional[str] = None):
    """
    Context manager olarak kullanilip otomatik sure/status loglar.

    Ornek:
        with log_api_timed("/api/companies", "GET", "utku"):
            # islem yap
            pass  # cikista otomatik loglanir
    """
    class _Timer:
        def __init__(self, ep: str, meth: str, usr: Optional[str]):
            self.endpoint = ep
            self.method = meth
            self.kullanici = usr
            self.baslangic = 0
            self.status = 200
            self.hata_mesaji = None

        def __enter__(self):
            self.baslangic = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            sure_ms = int((time.perf_counter() - self.baslangic) * 1000)
            if exc_type is not None:
                self.status = 500
                self.hata_mesaji = str(exc_val)
            log_api_request(
                endpoint=self.endpoint,
                method=self.method,
                status=self.status,
                sure_ms=sure_ms,
                kullanici=self.kullanici,
                hata_mesaji=self.hata_mesaji,
            )
            return False  # exception'i gecir

    return _Timer(endpoint, method, kullanici)


if __name__ == "__main__":
    # Manuel test
    log_api_request("/api/test", "GET", 200, 42, "test_user", None)
    with log_api_timed("/api/test-timed", "POST", "test_user"):
        time.sleep(0.05)
    print("Test loglari yazildi.")