# -*- coding: utf-8 -*-
"""`scrape_kayit` + `scrape_kosu` birim mandalı (D-310 katman 5).

NEDEN BU MANDAL VAR
    SCRAPE-002 tesliminde iki gerçek açık kaldı:
      1. Birim testi yoktu — dogrulama yalnizca canlı DB'de iki kosu idi.
         Canlı DB'ye yazan bir test, hata varken de "yesil" verebilir.
      2. Ilk yazim `scrape_errors`'a `source_name`/`source_url` yazdi; 0050
         semasinda o kolonlar YOK. Canlida reddedildi, duzeltildi.
         Ayni hatanin tekrar etmesi ancak bir mandalla engellenir.

KAPSAM DISI
    Bu mandal canli DB'ye BAGLANMAZ. `get_engine` sahte motorla degistirilir
    (ALTYAPI-TEST-HERMETIK-01). Idempotens kaniti canlida iki kosuyla
    alindi; buradaki test ayni SQL'in dogru kuruldugunu ve 0050 semasiyla
    uyumlu oldugunu korur.

ILGILI NODLAR
    [[D-310]] kazima merkezi kaydin servisidir
    [[D-261]] content_hash UNIQUE dedup
    [[D-243]] testin kirlettigi yeri olc
    [[src/company_master/etl/scrape_kayit]] 0050 tek yazma kapisi
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.etl import scrape_kayit as sk  # noqa: E402
from company_master.etl import scrape_kosu as sk_kosu  # noqa: E402


# ---------------------------------------------------------------- sahte motor


class _Sonuc:
    def __init__(self, deger):
        self._deger = deger

    def fetchone(self):
        return (self._deger,) if self._deger is not None else None

    def scalar(self):
        return self._deger


class _Yakalayici:
    """Cift sonuc dondurur: INSERT ... RETURNING olanlar icin `donen`."""

    def __init__(self, kayitlar, donen_serit=None):
        self.kayitlar = kayitlar
        self.donen = donen_serit or {}
        self.sira = 0

    def execute(self, ifade, params=None):
        sql = str(ifade)
        self.kayitlar.append((sql, params))
        hangi = "scrape_audit_log" if "scrape_audit_log" in sql else (
            "scrape_errors" if "scrape_errors" in sql else "scrape_pages"
        )
        self.sira += 1
        return _Sonuc(self.donen.get(hangi, self.sira))


class _Baglanti:
    def __init__(self, kayitlar, donen_serit):
        self._y = _Yakalayici(kayitlar, donen_serit)

    def __enter__(self):
        return self._y

    def __exit__(self, *a):
        return False


class _Motor:
    def __init__(self, donen_serit=None):
        self.kayitlar: list[tuple[str, dict]] = []
        self._donen = donen_serit or {}

    def begin(self):
        return _Baglanti(self.kayitlar, self._donen)

    def sql(self, tablo: str) -> str:
        return " ".join(s for s, _ in self.kayitlar if tablo in s)

    def params(self, tablo: str) -> dict:
        for s, p in self.kayitlar:
            if tablo in s:
                return p or {}
        return {}


@pytest.fixture()
def motor(monkeypatch):
    m = _Motor()
    monkeypatch.setattr(sk, "get_engine", lambda: m)
    return m


# ------------------------------------------------------------------- icerik hash


class TestIcerikHash:
    def test_ayni_icerik_ayni_hash(self):
        """D-261: ayni icerik -> ayni hash. UNIQUE kisiti ancak o zaman tutar."""
        assert sk.icerik_hash("<html>a</html>") == sk.icerik_hash("<html>a</html>")

    def test_farkli_icerik_farkli_hash(self):
        assert sk.icerik_hash("a") != sk.icerik_hash("b")

    def test_hash_zaman_damgasi_icermez(self):
        """Iki ayri anda üretilen hash ayni olmalı — degilse her kosuda yeni satir."""
        h1 = sk.icerik_hash("sabit")
        h2 = sk.icerik_hash("sabit")
        assert h1 == h2 and len(h1) == 64

    def test_str_ve_bytes_ayni_sonuc(self):
        assert sk.icerik_hash("abc") == sk.icerik_hash(b"abc")

    def test_url_hash_url_den_dogru_tureyor(self):
        import hashlib

        u = "https://ostim.org.tr/firmalar"
        assert sk.url_hash(u) == hashlib.sha256(u.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------- sayfa yazimi


class TestSayfaKaydet:
    def test_ilk_kayit_yazilir(self, motor):
        y = sk.KazimaYazici("ostim.org.tr")
        assert y.sayfa_kaydet("https://x/firmalar", "<html>a</html>") is True
        assert y.sonuc.yazilan_sayfa == 1 and y.sonuc.atlanan == 0

    def test_ikinci_kayit_atlanir(self, monkeypatch):
        """ON CONFLICT DO NOTHING -> RETURNING bos doner -> atlanan artar."""
        m = _Motor(donen_serit={"scrape_pages": None})
        monkeypatch.setattr(sk, "get_engine", lambda: m)
        y = sk.KazimaYazici("ostim.org.tr")
        assert y.sayfa_kaydet("https://x/firmalar", "<html>a</html>") is False
        assert y.sonuc.yazilan_sayfa == 0 and y.sonuc.atlanan == 1

    def test_conflict_kisiti_dogru_kolonlarda(self, motor):
        """D-261: UNIQUE(source_url, content_hash) — sayfa kimligi degil, icerik."""
        y = sk.KazimaYazici("ostim.org.tr")
        y.sayfa_kaydet("https://x/firmalar", "<html>a</html>")
        sql = motor.sql("ON CONFLICT")
        assert "ON CONFLICT (source_url, content_hash) DO NOTHING" in sql

    def test_hash_ve_len_parametrelere_girer(self, motor):
        y = sk.KazimaYazici("ostim.org.tr")
        ham = "<html>abc</html>"
        y.sayfa_kaydet("https://x/firmalar", ham)
        p = motor.params("scrape_pages")
        assert p["ch"] == sk.icerik_hash(ham)
        assert p["uh"] == sk.url_hash("https://x/firmalar")
        assert p["len"] == len(ham)

    def test_llm_used_false_ve_cost_sifir(self, motor):
        """0050 CHECK (cost_usd = 0); bu yol LLM-less (SKILL.md B-1)."""
        y = sk.KazimaYazici("ostim.org.tr")
        y.sayfa_kaydet("https://x/f", "<html>a</html>")
        sql = motor.sql("scrape_pages")
        assert "false, NULL, 0.00" in sql
        assert "llm_model" in sql


# ------------------------------------------------------------------- audit yazimi


class TestAuditKaydet:
    def test_audit_id_dondurulur(self, monkeypatch):
        """SCRAPE-002 borcu: audit_id dondurulmedigi icin hata kaydi FK'siz kaliyordu."""
        m = _Motor(donen_serit={"scrape_audit_log": 42})
        monkeypatch.setattr(sk, "get_engine", lambda: m)
        y = sk.KazimaYazici("ostim.org.tr")
        assert y.audit_kaydet("https://x/f") == 42
        assert y.sonuc.yazilan_audit == 1

    def test_kaynak_adi_audit_logda_tutulur(self, motor):
        y = sk.KazimaYazici("ivedik.org.tr", task_id="T-1")
        y.audit_kaydet("https://x/f")
        p = motor.params("scrape_audit_log")
        assert p["src"] == "ivedik.org.tr" and p["task"] == "T-1"

    def test_cost_sifir_llm_false(self, motor):
        y = sk.KazimaYazici("ostim.org.tr")
        y.audit_kaydet("https://x/f")
        assert "0.00" in motor.sql("scrape_audit_log")


# ------------------------------------------------------------------- hata yazimi


class TestHataKaydet:
    def test_scrape_errors_kaynak_kolonu_yok(self, motor):
        """0050'da source_name/source_url KOLONU YOK. Ilk yazim bunlari yazdi
        ve canli sema reddetti. Mandal bu regresyonu kapatir."""
        y = sk.KazimaYazici("ostim.org.tr")
        y.hata_kaydet(error_code="PermissionError", error_message="robots")
        sql = motor.sql("scrape_errors")
        assert "INSERT INTO scrape_errors (audit_id, page_id, error_code," in sql
        assert "source_name" not in sql and "source_url" not in sql

    def test_hata_kodu_ve_mesaj_kisaltilir(self, motor):
        """Kolon genislikleri 50 / 2000; tasarimi Python tarafinda kisaltiyoruz."""
        y = sk.KazimaYazici("ostim.org.tr")
        y.hata_kaydet(error_code="E" * 120, error_message="m" * 3000)
        p = motor.params("scrape_errors")
        assert len(p["kod"]) == 50 and len(p["msg"]) == 2000

    def test_retry_penceresi_yazilir(self, motor):
        y = sk.KazimaYazici("ostim.org.tr")
        y.hata_kaydet(error_code="X", error_message="y", retry_saat=6)
        assert motor.params("scrape_errors")["saat"] == 6
        assert sk.VARSAYILAN_RETRY_SAAT == 24

    def test_url_hata_kaydet_iki_kayit_yazar(self, motor):
        y = sk.KazimaYazici("baskentosb.org.tr")
        y.url_hata_kaydet("https://b/f", "PermissionError", "robots.txt Disallow")
        assert y.sonuc.yazilan_audit == 1 and y.sonuc.yazilan_hata == 1
        assert y.sonuc.hatali_url == ["https://b/f"]

    def test_url_hata_kaydet_audit_id_yi_hataya_baglar(self, monkeypatch):
        """Hata kaydi audit_id'siz olursa kaynak izi kopar; FK dolu olmali."""
        m = _Motor(donen_serit={"scrape_audit_log": 7})
        monkeypatch.setattr(sk, "get_engine", lambda: m)
        y = sk.KazimaYazici("baskentosb.org.tr")
        y.url_hata_kaydet("https://b/f", "PermissionError", "robots")
        assert m.params("scrape_errors")["aid"] == 7


# ------------------------------------------------------------------- router kapisi


class TestRouterKapisi:
    def test_izin_var_routeri_kullanir(self, monkeypatch):
        """SKILL.md'nin get_router(domain)/can_fetch() cagrisi YANLIS; olculmus
        API parametresiz get_router() -> check(url) -> Decision."""
        class _R:
            def check(self, url):
                return type("D", (), {"allowed": True, "reason": "ok"})()

        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: _R())
        assert sk.KazimaYazici.izin_var("https://x/f") == (True, "ok")

    def test_izin_yok_reddedilir(self, monkeypatch):
        class _R:
            def check(self, url):
                return type("D", (), {"allowed": False, "reason": "robots.txt Disallow"})()

        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: _R())
        assert sk.KazimaYazici.izin_var("https://x/f") == (False, "robots.txt Disallow")

    def test_rate_limit_domain_bekler(self, monkeypatch):
        class _R:
            def rate_limit(self, domain):
                return 1.5

        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: _R())
        assert sk.KazimaYazici.rate_limit_bekle("https://www.ivedikosb.org.tr/f") == 1.5


# ------------------------------------------------------------------- kosu iskeleti


class TestKosu:
    def _kaynak(self, **kw):
        d = dict(
            ad="ostim.org.tr",
            url="https://ostim.org.tr/firmalar",
            robots_url="https://ostim.org.tr/robots.txt",
        )
        d.update(kw)
        return sk_kosu.Kaynak(**d)

    def _router(self, izin=True):
        class _R:
            def check(self, url):
                return type("D", (), {
                    "allowed": izin, "reason": "" if izin else "robots.txt Disallow",
                })()

            def rate_limit(self, domain):
                return 0.0

        return _R()

    def _resp(self, metin="<html><title>Firmalar</title></html>"):
        class _Resp:
            text = metin

            def raise_for_status(self):
                return None

        return _Resp()

    def test_izin_yoksa_fetch_hic_yapilmaz(self, monkeypatch, motor):
        monkeypatch.setattr(
            sk, "get_engine", lambda: motor
        )
        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: self._router(izin=False))

        def _patlama(*a, **k):
            raise AssertionError("izin yokken fetch yapilmamali")

        monkeypatch.setattr(sk_kosu.requests, "get", _patlama)
        sonuc = sk_kosu.kosu(self._kaynak())
        assert sonuc["izin"] is False and sonuc["hata"] == 1 and sonuc["yazilan"] == 0
        assert motor.params("scrape_errors")["kod"] == "PermissionError"

    def test_basarili_kosu_audit_ve_sayfa_yazar(self, monkeypatch, motor):
        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: self._router())
        monkeypatch.setattr(
            sk_kosu.requests, "get", lambda *a, **k: self._resp()
        )
        sonuc = sk_kosu.kosu(self._kaynak())
        assert sonuc["izin"] is True and sonuc["hata"] == 0
        assert sonuc["yazilan"] == 1 and sonuc["atlanan"] == 0
        assert motor.sql("scrape_audit_log") and motor.sql("scrape_pages")

    def test_ayni_icerik_ikinci_kosuda_atlanir(self, monkeypatch):
        """Idempotensin kayit katmani tarafi: ayni icerik -> atlanan=1."""
        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: self._router())
        monkeypatch.setattr(sk_kosu.requests, "get", lambda *a, **k: self._resp())
        m1 = _Motor()
        monkeypatch.setattr(sk, "get_engine", lambda: m1)
        a = sk_kosu.kosu(self._kaynak())
        m2 = _Motor(donen_serit={"scrape_pages": None})
        monkeypatch.setattr(sk, "get_engine", lambda: m2)
        b = sk_kosu.kosu(self._kaynak())
        assert (a["yazilan"], a["atlanan"]) == (1, 0)
        assert (b["yazilan"], b["atlanan"]) == (0, 1)

    def test_fetch_hatasi_hata_kaydina_duser(self, monkeypatch, motor):
        import company_master.utils.scraping_permission_router as r
        import requests as rq

        monkeypatch.setattr(r, "get_router", lambda: self._router())

        def _patla(*a, **k):
            raise rq.ConnectionError("baglanti yok")

        monkeypatch.setattr(sk_kosu.requests, "get", _patla)
        sonuc = sk_kosu.kosu(self._kaynak())
        assert sonuc["hata"] == 1 and sonuc["yazilan"] == 0
        assert motor.params("scrape_errors")["kod"] == "ConnectionError"

    def test_ayiklayici_kirilirsa_kayit_yine_yazilir(self, monkeypatch, motor):
        """Kirik ayiklayici kosuyu oldurmemeli; varsayilana dusulur (D-245)."""
        import company_master.utils.scraping_permission_router as r

        monkeypatch.setattr(r, "get_router", lambda: self._router())
        html = '<div class="col-lg-4 mb-3"></div>'
        monkeypatch.setattr(sk_kosu.requests, "get", lambda *a, **k: self._resp(html))

        def _bozuk(soup):
            raise ValueError("beklenmeyen")

        sonuc = sk_kosu.kosu(self._kaynak(ayikla=_bozuk))
        assert sonuc["hata"] == 0 and sonuc["yazilan"] == 1
        assert "ayiklayici_hata" in sonuc["alanlar"]


# ------------------------------------------------------------------- varsayilan ayikla


class TestVarsayilanAyikla:
    def test_osb_list_card_sinifi_once_denir(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<div class="osb-list-card"></div>', "html.parser")
        a = sk_kosu._varsayilan_ayikla(soup)
        assert a["kart_tipi"] == "osb-list-card" and a["kart_sayisi"] == 1

    def test_col_lg4_yapisi_dusulur(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup('<div class="col-lg-4 mb-3"></div><div class="col-lg-4 mb-3"></div>',
                             "html.parser")
        a = sk_kosu._varsayilan_ayikla(soup)
        assert a["kart_tipi"] == "col-lg-4.mb-3" and a["kart_sayisi"] == 2

    def test_kart_yoksa_sayi_sifir_ve_tip_none(self):
        """D-245: doluluk gecerlilik degil; kart yoksa 0 yazilir, uydurulmaz."""
        from bs4 import BeautifulSoup

        a = sk_kosu._varsayilan_ayikla(BeautifulSoup("<html></html>", "html.parser"))
        assert a["kart_sayisi"] == 0 and a["kart_tipi"] is None

    def test_baslik_okunur(self):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><title>Firmalar</title></html>", "html.parser")
        assert sk_kosu._varsayilan_ayikla(soup)["baslik"] == "Firmalar"


# ------------------------------------------------------------------- kaynak dosyalari


class TestKapsamSiniri:
    """D-235: kayit katmani kanonik kaziyiciyi TIKAMAZ."""

    def test_kanonik_kaziyicilara_dokunulmaz(self):
        kanonik = ROOT / "src" / "company_master" / "etl" / "scrapers"
        for ad in ("ostim_scraper.py", "ivedik_scraper.py", "baskent_scraper.py"):
            p = kanonik / ad
            if p.exists():
                assert "scrape_kayit" not in p.read_text(encoding="utf-8")

    def test_kayit_katmani_firma_ckarimi_yapmaz(self):
        """D-211: bu katman yalniz kanit yazar; INSERT yalniz 0050 tablosuna."""
        kaynak = (ROOT / "src" / "company_master" / "etl" / "scrape_kayit.py").read_text(
            encoding="utf-8"
        )
        assert "INSERT INTO companies" not in kaynak
        hedefler = set(re.findall(r"INSERT INTO (\w+)", kaynak))
        assert hedefler == {"scrape_pages", "scrape_audit_log", "scrape_errors"}


# ------------------------------------------------------------------- yan etki denetimi


class TestYanEtkiYok:
    def test_liste_dosyalarina_yazmaz(self):
        """ALTYAPI-TEST-HERMETIK-01: kosu yalniz DB'ye yazar, diske degil."""
        kaynak = (ROOT / "src" / "company_master" / "etl" / "scrape_kosu.py").read_text(
            encoding="utf-8"
        )
        assert "open(" not in kaynak
        assert "write_text" not in kaynak and "to_csv" not in kaynak

    def test_sonuc_ozeti_okunabilir(self):
        y = sk.KazimaSonuc(yazilan_sayfa=1, yazilan_audit=1, yazilan_hata=0, atlanan=0)
        ozet = y.ozet()
        assert "sayfa +1" in ozet and "audit +1" in ozet and "hata +0" in ozet


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
