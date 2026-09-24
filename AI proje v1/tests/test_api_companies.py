# -*- coding: utf-8 -*-
"""Y9 — /api/companies entegrasyon testleri (gercek Supabase DB).

Birim seviyesindeki kural testleri icin: tests/test_kurallar.py
Calistirma: pytest tests/test_api_companies.py -v
Gereklilik: .env icinde DATABASE_URL (Supabase) + ag erisimi.
Not: .env'de DASH_API_KEY yoksa dev modu; auth testleri monkeypatch ile
key'i gecici olarak set eder ve sonda otomatik geri alir.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import web_app
from fastapi.testclient import TestClient
from web_app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _companies(client, **params):
    r = client.get("/api/companies", params=params)
    assert r.status_code == 200, r.text
    return r.json()


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ── Y7: KVKK PII maskeleme testleri ──
class TestKvkkMaskeUnit:
    """DB bagimsiz maskeleme fonksiyon testleri."""
    def test_mask_email(self):
        from web_app import _mask_email
        assert _mask_email("ahmet@gmail.com") == "ah***@gmail.com"
        assert _mask_email("info@akkor.com.tr") == "in***@akkor.com.tr"
        assert _mask_email("") == ""
        assert _mask_email(None) is None

    def test_mask_phone(self):
        from web_app import _mask_phone
        assert _mask_phone("905542287200") == "905***00"
        assert _mask_phone("0 312 555 44 33") == "031***33"
        assert _mask_phone("") == ""
        assert _mask_phone(None) is None

    def test_apply_kvkk_mask_both_fields(self):
        from web_app import apply_kvkk_mask
        row = {"primary_phone": "05061112233", "primary_email": "satis@firma.com", "legal_name": "X"}
        out = apply_kvkk_mask(row)
        assert out["primary_phone"] == "050***33"
        assert out["primary_email"] == "sa***@firma.com"
        assert out["legal_name"] == "X"  # unvan maskelemmez (PO karari)


class TestKvkkMaskeAPI:
    """?mask=1 istek bazli maskeleme (gercek DB)."""
    def test_mask_1_returns_masked(self, client):
        d = _companies(client, limit=200, mask=1)
        items = [i for i in d["items"] if i.get("primary_phone") or i.get("primary_email")]
        assert items, "test icin dolu tel/email'li kayit bulunamadi"
        for it in items:
            if it.get("primary_phone"):
                assert "***" in it["primary_phone"], it["primary_phone"]
            if it.get("primary_email"):
                assert "***" in it["primary_email"], it["primary_email"]

    def test_default_not_masked(self, client):
        d = _companies(client, limit=200)
        items = [i for i in d["items"] if i.get("primary_phone")]
        if items:  # veri varsa maske OLMAMALI
            assert all("***" not in i["primary_phone"] for i in items)

    def test_no_bireysel_email_in_db(self, client):
        """KVKK §3.1: DB'de bireysel e-posta (gmail/hotmail vs) OLMAMALI."""
        d = _companies(client, limit=200)
        bad = [i["primary_email"] for i in d["items"]
               if i.get("primary_email") and re.search(
                   r"(gmail|hotmail|yahoo|yandex|outlook|icloud)\.[a-z]{2,3}", i["primary_email"], re.I)]
        assert not bad, f"bireysel e-posta sizintisi: {bad[:3]}"


class TestNormalizeKurallariCanliVeri:
    """Kural 1+2+3 canli veri uzerinde invariant kontrolu."""

    def test_legal_name_tamamen_buyuk_harf(self, client):
        d = _companies(client, limit=20)
        for it in d["items"]:
            assert it["legal_name"], "legal_name bos olmamali"
            assert not re.search(r"[a-z]", it["legal_name"]), (
                f"Kucuk harf kaldi: {it['legal_name']!r}"
            )

    def test_ascii_kisaltma_kalintisi_yok(self, client):
        """Kural 2 regresyonu: cikti Turkce karakterli olmali (TIC./STI./MUH./MIM. yasak)."""
        d = _companies(client, limit=30)
        for it in d["items"]:
            legal = it["legal_name"]
            assert not re.search(r"\b(TIC|STI|MUH|MIM)\.", legal), (
                f"ASCII kisaltma kaldi: {legal!r}"
            )

    def test_trade_name_legal_kelimelerinden(self, client):
        """Kural 3: tabela ismi, unvandaki kelimelerin alt kumesi olmali."""

        def _words(s):
            return set(re.findall(r"[A-ZÇĞİÖŞÜ0-9&]+", s or ""))

        d = _companies(client, limit=20)
        for it in d["items"]:
            if it.get("trade_name"):
                eksik = _words(it["trade_name"]) - _words(it["legal_name"])
                assert not eksik, (
                    f"trade_name legal'de olmayan kelime: {it['trade_name']!r} / {it['legal_name']!r}"
                )


class TestTurkceArama:
    """Y3: ASCII sorgu Turkce veriyle eslesmeli (tr_normalize fallback)."""

    def test_ascii_sorgu_turkce_veriyi_bulur(self, client):
        """Arama coklu alandadir (email/telefon dahil); legal'de DOĞAN gecen
        en az bir sonuc donmeli + toplam tutarli olmali."""
        d = _companies(client, limit=10, search="dogan")
        assert d["total"] > 0
        assert any(
            re.search(r"DO[ĞG]AN", it["legal_name"]) for it in d["items"]
        ), "legal_name'de DOĞAN gecen hic sonuc yok"

    def test_turkce_sorgu_calisir(self, client):
        d = _companies(client, limit=5, search="doğan")
        assert d["total"] > 0
        for it in d["items"]:
            assert re.search(r"DO[ĞG]AN", it["legal_name"]), it["legal_name"]

    def test_turkce_karakter_sorgu_sozluk_kisaltmasini_bulur(self, client):
        d = _companies(client, limit=5, search="ŞTİ")
        assert d["total"] > 500  # LTD. ŞTİ. cok yaygin

    def test_bilinen_firma_arama(self, client):
        d = _companies(client, limit=5, search="radikal")
        assert d["total"] >= 1
        for it in d["items"]:
            assert "RADIKAL" in it["legal_name"]


class TestCokluKaynak:
    """Y1: sources=a,b -> UNION; source= geriye donuk uyum."""

    def test_source_ve_sources_ayni_sonuc(self, client):
        t_source = _companies(client, limit=1, source="ostim.org.tr")["total"]
        t_sources = _companies(client, limit=1, sources="ostim.org.tr")["total"]
        assert t_source == t_sources
        assert t_source > 1000

    def test_iki_kaynak_toplami_tum_firmalara_esit(self, client):
        kaynaklar = client.get("/api/sources").json()
        assert len(kaynaklar) >= 2
        toplamlar = []
        for s in kaynaklar[:2]:
            t = _companies(client, limit=1, sources=s["source_name"])["total"]
            toplamlar.append(t)
        iki_kaynak = _companies(
            client, limit=1, sources=",".join(s["source_name"] for s in kaynaklar[:2])
        )["total"]
        assert iki_kaynak == sum(toplamlar)  # firma tek kaynaga bagli: ayrismasiz UNION
        # Tum kaynaklar ayri ayri toplanirsa genel toplama esit olmali (kesisim yok)
        tum_kaynak_toplam = sum(
            _companies(client, limit=1, sources=s["source_name"])["total"]
            for s in kaynaklar
        )
        hepsi = _companies(client, limit=1)["total"]
        assert tum_kaynak_toplam == hepsi


class TestPagination:
    """Y5: limit/offset + data_quality_score DESC siralama."""

    def test_limit_offset_calisir(self, client):
        s1 = _companies(client, limit=5, offset=0)
        s2 = _companies(client, limit=5, offset=5)
        assert len(s1["items"]) == 5
        assert s1["total"] == s2["total"]
        id1 = [i["legal_name"] for i in s1["items"]]
        id2 = [i["legal_name"] for i in s2["items"]]
        assert id1 != id2, "offset sayfalari ayni geldi"

    def test_limit_clamp_500(self, client):
        d = _companies(client, limit=10000)
        assert len(d["items"]) <= web_app.MAX_COMPANIES_LIMIT

    def test_kalite_skoruna_gore_azalan_siralama(self, client):
        d = _companies(client, limit=20)
        skorlar = [i["data_quality_score"] for i in d["items"] if i["data_quality_score"] is not None]
        assert skorlar == sorted(skorlar, reverse=True)


class TestNaceFiltre:
    def test_nace_onek_filtresi(self, client):
        # En yaygin sektoru dinamik sec (veri degisse de test kirilmasin)
        dist = client.get("/api/nace-distribution", params={"limit": 1}).json()
        assert dist, "nace-distribution bos"
        on_ek = (dist[0].get("nace_code") or "")[:2]
        assert on_ek, f"nace_code yok: {dist[0]}"

        d = _companies(client, limit=10, nace=on_ek)
        assert d["total"] > 0
        for it in d["items"]:
            assert (it.get("nace_code") or "").startswith(on_ek), it["nace_code"]
        hepsi = _companies(client, limit=1)["total"]
        assert d["total"] < hepsi


class TestApiKeyAuth:
    """Y6: DASH_API_KEY set iken koruma; monkeypatch ile gecici."""

    def test_key_olmayinca_401(self, client, monkeypatch):
        monkeypatch.setattr(web_app, "DASH_API_KEY", "test-key-123")
        r = client.get("/api/companies", params={"limit": 1})
        assert r.status_code == 401

    def test_yanlis_key_401(self, client, monkeypatch):
        monkeypatch.setattr(web_app, "DASH_API_KEY", "test-key-123")
        r = client.get("/api/companies", params={"limit": 1}, headers={"X-API-Key": "yanlis"})
        assert r.status_code == 401

    def test_dogru_key_header_ile_200(self, client, monkeypatch):
        monkeypatch.setattr(web_app, "DASH_API_KEY", "test-key-123")
        r = client.get("/api/companies", params={"limit": 1}, headers={"X-API-Key": "test-key-123"})
        assert r.status_code == 200

    def test_dogru_key_query_ile_200(self, client, monkeypatch):
        monkeypatch.setattr(web_app, "DASH_API_KEY", "test-key-123")
        r = client.get("/api/companies", params={"limit": 1, "api_key": "test-key-123"})
        assert r.status_code == 200


class TestRateLimit:
    """Y6: dakikada istek siniri (in-memory, IP basina)."""

    def test_limit_asilinca_429(self, client, monkeypatch):
        monkeypatch.setattr(web_app, "_RATE_LIMIT_MAX", 2)
        web_app._RATE_LIMIT.clear()
        try:
            kodlar = [
                client.get("/api/companies", params={"limit": 1}).status_code
                for _ in range(3)
            ]
            assert kodlar[:2] == [200, 200]
            assert kodlar[2] == 429
        finally:
            web_app._RATE_LIMIT.clear()

