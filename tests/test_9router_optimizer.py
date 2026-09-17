# -*- coding: utf-8 -*-
"""9R-05 — 9router_optimizer.py birim testleri.

Kapsam (plan §7 / Adım G):
  - Secret maskeleme (_maskele / _maskele_rek)
  - Sağlık taraması parse (saglik_taramasi, null-safety dahil)
  - DB yedekleme + retention 7 (db_yedekle)
  - Combo RR istatistiği (provider-bazlı latency/maliyet)
  - Skorlama (provider-bazlı, testStatus=error cezası, ölçülmemiş nötr 75)
  - Anomali tespiti (YUKSEK/ORTA öncelik)
  - Telegram sentinel (tekrar engelleme)
  - Çıktılar (json_cikti / markdown_rapor)

Gerçek 9router DB'sine ve ağa dokunmaz; tmp_path + monkeypatch ile izole.
"""
from __future__ import annotations

import importlib
import json
import sqlite3
import sys
import types
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

# "9router_optimizer" bir identifier olmadığı için importlib ile yüklenir.
opt = importlib.import_module("9router_optimizer")


# ---------------------------------------------------------------- Yardımcılar
def _provider_ekle(
    con: sqlite3.Connection,
    provider: str,
    isActive: int = 1,
    data: dict | None = None,
    name: str = "",
    authType: str = "apiKey",
    priority: int = 1,
) -> None:
    con.execute(
        "INSERT INTO providerConnections "
        "(provider, authType, name, priority, isActive, data, updatedAt) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            provider,
            authType,
            name,
            priority,
            isActive,
            json.dumps(data) if data is not None else None,
            "2026-09-12T00:00:00",
        ),
    )


def _request_ekle(
    con: sqlite3.Connection,
    provider: str,
    status: str,
    latency_total: int,
    model: str = "m",
    ts: str = "2026-09-12T00:00:00",
) -> None:
    data = json.dumps(
        {
            "latency": {"ttft": 100, "total": latency_total},
            "tokens": {"prompt_tokens": 10, "completion_tokens": 5},
        }
    )
    con.execute(
        "INSERT INTO requestDetails (timestamp, provider, model, status, data) "
        "VALUES (?,?,?,?,?)",
        (ts, provider, model, status, data),
    )


def _usage_ekle(
    con: sqlite3.Connection,
    provider: str,
    cost: float,
    endpoint: str = "/v1/chat/completions",
    status: str = "success",
) -> None:
    con.execute(
        "INSERT INTO usageHistory "
        "(timestamp, provider, model, endpoint, status, cost, promptTokens, completionTokens) "
        "VALUES (?,?,?,?,?,?,?,?)",
        ("2026-09-12T00:00:00", provider, "m", endpoint, status, cost, 10, 5),
    )


@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    """9router şemasının test kopyası (providerConnections/requestDetails/usageHistory/settings)."""
    db = tmp_path / "data.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE providerConnections (
            provider TEXT, authType TEXT, name TEXT, priority INTEGER,
            isActive INTEGER, data TEXT, updatedAt TEXT
        );
        CREATE TABLE requestDetails (
            timestamp TEXT, provider TEXT, model TEXT, status TEXT, data TEXT
        );
        CREATE TABLE usageHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, provider TEXT, model TEXT, endpoint TEXT,
            status TEXT, cost REAL, promptTokens INTEGER, completionTokens INTEGER
        );
        CREATE TABLE settings (data TEXT);
        """
    )
    con.commit()
    yield db
    con.close()


def _p(
    provider: str,
    isActive: int = 1,
    backoff: int = 0,
    locks: int = 0,
    error: str | None = None,
    test: str = "ok",
) -> dict:
    """skorla()/anomali_tespit() için minimal provider dict'i."""
    return {
        "provider": provider,
        "name": provider,
        "isActive": isActive,
        "durum": {
            "backoffLevel": backoff,
            "modelLockSayisi": locks,
            "errorCode": error,
            "testStatus": test,
        },
    }


def _saglik_ornek(providerlar: list[dict]) -> dict:
    return {
        "toplam": len(providerlar),
        "aktif": sum(1 for p in providerlar if p["isActive"] == 1),
        "inaktif": sum(1 for p in providerlar if p["isActive"] == 0),
        "sorunlu_sayisi": 0,
        "sorunlu": [],
        "providerlar": providerlar,
    }


def _combo_ornek() -> dict:
    """Provider-bazlı ölçümlü combo istatistiği (openai hızlı+ucuz, xai pahalı)."""
    return {
        "requestDetails": {
            "kayit_sayisi": 2,
            "provider_dagilimi": {"openai": 1, "xai": 1},
            "status_dagilimi": {"success": 2},
            "ortalama_latency_ms": 1500.0,
            "provider_latency_ort": {"openai": 1000.0, "xai": 2000.0},
            "provider_status": {
                "openai": {"success": 1, "error": 0},
                "xai": {"success": 1, "error": 0},
            },
        },
        "usageHistory": {
            "kayit_sayisi": 2,
            "endpoint_dagilimi": {"/v1/chat/completions": 2},
            "toplam_maliyet_usd": 0.01,
            "provider_maliyet_toplam": {"openai": 0.001, "xai": 0.009},
            "provider_maliyet_ort": {"openai": 0.001, "xai": 0.009},
            "provider_cagri_sayisi": {"openai": 1, "xai": 1},
        },
        "settings": {
            "comboStrategy": "round-robin",
            "comboStickyRoundRobinLimit": 3,
            "enableObservability": True,
        },
    }


# ---------------------------------------------------------------- Secret maskeleme
class TestSecretMaskeleme:
    def test_uzun_deger_ilk_son_4(self) -> None:
        assert opt._maskele("sk-1234567890abcdef") == "sk-1...cdef"

    def test_kisa_deger_tamamen_maskelenir(self) -> None:
        assert opt._maskele("kisa") == "****"

    def test_dict_icinde_secret_anahtar_maskelenir(self) -> None:
        sonuc = opt._maskele_rek(
            {"apiKey": "sk-1234567890abcdef", "name": "OpenAI"}
        )
        assert sonuc["apiKey"] == "sk-1...cdef"
        assert sonuc["name"] == "OpenAI"

    def test_list_icinde_recursive(self) -> None:
        sonuc = opt._maskele_rek([{"token": "abc123456789"}])
        assert sonuc[0]["token"] == "abc1...6789"


# ---------------------------------------------------------------- Sağlık taraması
class TestSaglikTaramasi:
    def test_saglikli_provider_sorunlu_degil(self, test_db: Path) -> None:
        con = sqlite3.connect(test_db)
        _provider_ekle(con, "openai", data={"testStatus": "ok", "backoffLevel": 0})
        con.commit()
        con.close()

        sonuc = opt.saglik_taramasi(test_db)
        assert sonuc["toplam"] == 1
        assert sonuc["aktif"] == 1
        assert sonuc["sorunlu_sayisi"] == 0

    def test_backoff_esik_ve_locks(self, test_db: Path) -> None:
        """modelLock_* anahtarları ayrı ayrı sayılır (gerçek DB'de 112 lock = 112 anahtar)."""
        con = sqlite3.connect(test_db)
        # 12 ayrı modelLock_* anahtarı → kilit_sayisi = 12 (> 10 eşiği)
        locks = {f"modelLock_model_{i}": 1 for i in range(12)}
        _provider_ekle(
            con,
            "api-airforce",
            data={"backoffLevel": 14, **locks},
        )
        con.commit()
        con.close()

        sonuc = opt.saglik_taramasi(test_db)
        assert sonuc["sorunlu_sayisi"] == 1
        sorunlar = sonuc["sorunlu"][0]["sorunlar"]
        assert "backoff=14" in sorunlar
        assert "locks=12" in sorunlar

    def test_error_code_ve_teststatus(self, test_db: Path) -> None:
        con = sqlite3.connect(test_db)
        _provider_ekle(
            con,
            "bazaarlink",
            data={"errorCode": 429, "testStatus": "error"},
        )
        con.commit()
        con.close()

        sonuc = opt.saglik_taramasi(test_db)
        sorunlar = sonuc["sorunlu"][0]["sorunlar"]
        assert "error=429" in sorunlar
        assert "testStatus=error" in sorunlar

    def test_null_backoff_cokmez(self, test_db: Path) -> None:
        """JSON'da backoffLevel: null → None; or 0 ile null-safety."""
        con = sqlite3.connect(test_db)
        _provider_ekle(con, "openai", data={"backoffLevel": None, "errorCode": None})
        con.commit()
        con.close()

        sonuc = opt.saglik_taramasi(test_db)
        assert sonuc["sorunlu_sayisi"] == 0

    def test_bozuk_json_ham_fallback(self, test_db: Path) -> None:
        con = sqlite3.connect(test_db)
        con.execute(
            "INSERT INTO providerConnections "
            "(provider, authType, name, priority, isActive, data, updatedAt) "
            "VALUES (?,?,?,?,?,?,?)",
            ("bozuk", "apiKey", "", 1, 1, "{bozuk-json", "2026-09-12T00:00:00"),
        )
        con.commit()
        con.close()

        sonuc = opt.saglik_taramasi(test_db)
        assert sonuc["toplam"] == 1
        assert sonuc["providerlar"][0]["data_maskeli"]["HAM"].startswith("{bozuk")


# ---------------------------------------------------------------- DB yedekleme + retention
class TestDbYedekle:
    def test_retention_7_eski_yedekler_silinir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_db: Path
    ) -> None:
        yedek_dir = tmp_path / "yedekler"
        yedek_dir.mkdir()
        monkeypatch.setattr(opt, "YEDEK_DIR", yedek_dir)

        # 10 eski yedek + 1 yeni = 11; retention 7 → 4'ü silinir, 7 kalır
        for i in range(10):
            (yedek_dir / f"9router_20260901_{i:02d}.sqlite").write_bytes(b"x")

        sonuc = opt.db_yedekle(test_db, keep=7)

        kalan = sorted(yedek_dir.glob("9router_*.sqlite"))
        assert len(kalan) == 7
        assert len(sonuc["silinen_yedekler"]) == 4
        assert sonuc["boyut_mb"] >= 0

    def test_yeni_yedek_gercek_sqlite(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, test_db: Path
    ) -> None:
        yedek_dir = tmp_path / "yedekler"
        monkeypatch.setattr(opt, "YEDEK_DIR", yedek_dir)

        sonuc = opt.db_yedekle(test_db, keep=7)
        yeni = Path(sonuc["yedek_alindi"])
        assert yeni.exists()

        con = sqlite3.connect(yeni)
        tablolar = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )]
        con.close()
        assert "providerConnections" in tablolar


# ---------------------------------------------------------------- Combo RR istatistiği
class TestComboIstatistik:
    def test_provider_bazli_latency_ve_maliyet(self, test_db: Path) -> None:
        con = sqlite3.connect(test_db)
        _request_ekle(con, "openai", "success", 1000)
        _request_ekle(con, "openai", "success", 3000)
        _request_ekle(con, "xai", "error", 2000)
        _usage_ekle(con, "openai", 0.001)
        _usage_ekle(con, "openai", 0.003)
        _usage_ekle(con, "xai", 0.009)
        con.commit()
        con.close()

        sonuc = opt.combo_rr_istatistik(test_db, limit=500)

        rd = sonuc["requestDetails"]
        assert rd["kayit_sayisi"] == 3
        assert rd["provider_latency_ort"]["openai"] == 2000.0  # (1000+3000)/2
        assert rd["provider_latency_ort"]["xai"] == 2000.0
        assert rd["status_dagilimi"]["error"] == 1

        uh = sonuc["usageHistory"]
        assert uh["provider_maliyet_ort"]["openai"] == 0.002  # (0.001+0.003)/2
        assert uh["provider_maliyet_ort"]["xai"] == 0.009
        assert uh["provider_cagri_sayisi"]["openai"] == 2
        assert uh["toplam_maliyet_usd"] == 0.013

    def test_settings_okunur(self, test_db: Path) -> None:
        con = sqlite3.connect(test_db)
        con.execute(
            "INSERT INTO settings (data) VALUES (?)",
            (
                json.dumps(
                    {
                        "comboStrategy": "round-robin",
                        "comboStickyRoundRobinLimit": 3,
                        "enableObservability": True,
                    }
                ),
            ),
        )
        con.commit()
        con.close()

        sonuc = opt.combo_rr_istatistik(test_db)
        assert sonuc["settings"]["comboStrategy"] == "round-robin"
        assert sonuc["settings"]["comboStickyRoundRobinLimit"] == 3

    def test_bos_db_cokmez(self, test_db: Path) -> None:
        sonuc = opt.combo_rr_istatistik(test_db)
        assert sonuc["requestDetails"]["kayit_sayisi"] == 0
        assert sonuc["requestDetails"]["ortalama_latency_ms"] == 0
        assert sonuc["usageHistory"]["toplam_maliyet_usd"] == 0.0


# ---------------------------------------------------------------- Skorlama
class TestSkorla:
    def test_saglikli_hizli_ucuz_en_iyi(self) -> None:
        saglik = _saglik_ornek([_p("openai"), _p("xai")])
        skorlar = opt.skorla(saglik, _combo_ornek())

        by_name = {s["provider"]: s for s in skorlar}
        # openai: sağlık=100, hız=100 (1000ms), maliyet=100 (0.2x referans) → 100
        assert by_name["openai"]["toplam"] == 100.0
        # xai: sağlık=100, hız=100 (2000ms), maliyet=50 (1.8x referans) → 87.5
        assert by_name["xai"]["toplam"] == 87.5
        assert skorlar[0]["provider"] == "openai"

    def test_teststatus_error_cezasi(self) -> None:
        saglik = _saglik_ornek([_p("bazaarlink", test="error")])
        skorlar = opt.skorla(saglik, _combo_ornek())

        s = skorlar[0]
        assert s["saglik"] == 60  # 100 - 40
        assert s["toplam"] == 67.5  # 60*0.5 + 75*0.25 + 75*0.25

    def test_olculmemis_provider_nort_75(self) -> None:
        """Verisi olmayan provider 100 değil nötr 75 almalı (yanıltıcı 'en iyi' olmamalı)."""
        saglik = _saglik_ornek([_p("olculmemis")])
        skorlar = opt.skorla(saglik, _combo_ornek())

        s = skorlar[0]
        assert s["hiz"] == 75
        assert s["maliyet"] == 75
        assert s["latency_ms"] is None
        assert s["maliyet_ort_usd"] is None

    def test_inaktif_provider_sifir_saglik(self) -> None:
        saglik = _saglik_ornek([_p("kapali", isActive=0)])
        skorlar = opt.skorla(saglik, _combo_ornek())

        s = skorlar[0]
        assert s["saglik"] == 0
        assert s["toplam"] == 37.5  # 0*0.5 + 75*0.25 + 75*0.25

    def test_siralama_azalan(self) -> None:
        saglik = _saglik_ornek(
            [
                _p("openai"),
                _p("xai"),
                _p("bazaarlink", test="error"),
                _p("kapali", isActive=0),
            ]
        )
        skorlar = opt.skorla(saglik, _combo_ornek())
        toplamlar = [s["toplam"] for s in skorlar]
        assert toplamlar == sorted(toplamlar, reverse=True)


# ---------------------------------------------------------------- Anomali tespiti
class TestAnomaliTespit:
    def test_coklu_neden_yuksek_oncelik(self) -> None:
        saglik = _saglik_ornek([_p("api-airforce", backoff=14, error="402")])
        anomaliler = opt.anomali_tespit(saglik, _combo_ornek())

        assert len(anomaliler) == 1
        assert anomaliler[0]["oncelik"] == "YUKSEK"
        assert len(anomaliler[0]["nedenler"]) == 2

    def test_tek_neden_orta_oncelik(self) -> None:
        saglik = _saglik_ornek([_p("kiro", locks=44)])
        anomaliler = opt.anomali_tespit(saglik, _combo_ornek())

        assert len(anomaliler) == 1
        assert anomaliler[0]["oncelik"] == "ORTA"

    def test_temiz_provider_anomali_yok(self) -> None:
        saglik = _saglik_ornek([_p("openai")])
        anomaliler = opt.anomali_tespit(saglik, _combo_ornek())
        assert anomaliler == []


# ---------------------------------------------------------------- Telegram sentinel
class TestTelegramSentinel:
    @pytest.fixture(autouse=True)
    def _sahte_telegram(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """send_telegram_message'ı sahte modülle değiştir, sentinel'i tmp_path'e yönlendir."""
        sahte = types.ModuleType("src.company_master.utils.telegram_bot")
        gonderilen: list[str] = []
        sahte.send_telegram_message = lambda mesaj: gonderilen.append(mesaj)
        monkeypatch.setitem(
            sys.modules, "src.company_master.utils.telegram_bot", sahte
        )
        monkeypatch.setattr(opt, "SON_UYARILAR", tmp_path / "son_uyarilar.json")
        yield gonderilen

    def test_ilk_bildirim_gonderilir(self, _sahte_telegram: list[str]) -> None:
        anomaliler = [
            {"provider": "xai", "name": "xAI", "nedenler": ["errorCode=403"], "oncelik": "YUKSEK"}
        ]
        opt.telegram_bildir(anomaliler)
        assert len(_sahte_telegram) == 1
        assert "xai" in _sahte_telegram[0]

    def test_ayni_anomali_1_saat_icinde_tekrar_gonderilmez(
        self, _sahte_telegram: list[str]
    ) -> None:
        anomaliler = [
            {"provider": "xai", "name": "xAI", "nedenler": ["errorCode=403"], "oncelik": "YUKSEK"}
        ]
        opt.telegram_bildir(anomaliler)
        opt.telegram_bildir(anomaliler)
        assert len(_sahte_telegram) == 1  # sentinel tekrarı engelledi

    def test_farkli_anomali_gonderilir(self, _sahte_telegram: list[str]) -> None:
        opt.telegram_bildir(
            [{"provider": "xai", "name": "xAI", "nedenler": ["errorCode=403"], "oncelik": "YUKSEK"}]
        )
        opt.telegram_bildir(
            [{"provider": "kiro", "name": "Kiro", "nedenler": ["locks=44"], "oncelik": "ORTA"}]
        )
        assert len(_sahte_telegram) == 2

    def test_bos_anomali_gonderilmez(self, _sahte_telegram: list[str]) -> None:
        opt.telegram_bildir([])
        assert _sahte_telegram == []


# ---------------------------------------------------------------- Çıktılar
class TestCikti:
    def test_json_cikti_anahtarlari(self) -> None:
        saglik = _saglik_ornek([_p("openai")])
        skorlar = opt.skorla(saglik, _combo_ornek())
        anomaliler = opt.anomali_tespit(saglik, _combo_ornek())

        cikti = opt.json_cikti(saglik, skorlar, anomaliler, _combo_ornek())
        assert set(cikti.keys()) == {
            "timestamp", "saglik", "skorlar", "anomaliler", "combo_istatistik"
        }
        assert cikti["skorlar"][0]["provider"] == "openai"

    def test_markdown_rapor_baslik_ve_provider(self) -> None:
        saglik = _saglik_ornek([_p("openai")])
        skorlar = opt.skorla(saglik, _combo_ornek())
        anomaliler = opt.anomali_tespit(saglik, _combo_ornek())

        rapor = opt.markdown_rapor(saglik, skorlar, anomaliler, _combo_ornek())
        assert rapor.startswith("# 9R-05 Optimizasyon Raporu")
        assert "openai" in rapor
        assert "## 1. Sağlık Taraması" in rapor
