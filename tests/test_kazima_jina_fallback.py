# -*- coding: utf-8 -*-
"""SCRAPE-003: 9Router Jina-Reader fallback.

Kritik kural: Jina bir VEKIL sunucudur. **Izin reddi varsa denenmez**;
aksi halde vekil reddedilmis sayfayi getirirdi.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

spec = importlib.util.spec_from_file_location(
    "kazima_jina", KOK / "scripts" / "kazima_jina_fallback.py")
kj = importlib.util.module_from_spec(spec)
sys.modules["kazima_jina"] = kj
spec.loader.exec_module(kj)


class _Yanit:
    def __init__(self, veri=None, hata=False):
        self._veri = veri
        self._hata = hata
        self.text = "<html><title>Test</title>" \
                    "<div class='osb-list-card'>a</div>" \
                    "<div class='osb-list-card'>b</div></html>"
        self.status_code = 200

    def raise_for_status(self):
        if self._hata:
            import requests
            raise requests.HTTPError("403")

    def json(self):
        if not isinstance(self._veri, dict):
            raise ValueError("json yok")
        return self._veri


def test_dogrudan_basarili_jina_cagrilmaz(monkeypatch):
    """Dogrudan yoldan icerik geldiyse vekil denenmez."""
    cagrildi = []
    monkeypatch.setattr(kj.requests, "get",
                        lambda *a, **k: _Yanit())
    monkeypatch.setattr(kj, "jina_cek",
                        lambda *a, **k: cagrildi.append(1) or ("", ""))
    s = kj.cek("https://x.test")
    assert s["yol"] == "dogrudan"
    assert cagrildi == []


def test_dogrudan_basarisiz_jina_devreye_girer(monkeypatch):
    """Asil davranis: dogrudan kirilirsa Jina-Reader devreye girer."""
    import requests

    def _patla(*a, **k):
        raise requests.ConnectionError("DNS")

    monkeypatch.setattr(kj.requests, "get", _patla)
    monkeypatch.setattr(kj, "jina_cek", lambda *a, **k: ("# icerik", ""))
    s = kj.cek("https://x.test")
    assert s["yol"] == "jina-fallback"
    assert s["metin"] == "# icerik"
    assert s["hata"] == "ConnectionError"


def test_iki_yol_da_basarisiz_hata_donuyor(monkeypatch):
    import requests

    def _patla(*a, **k):
        raise requests.ConnectionError("DNS")

    monkeypatch.setattr(kj.requests, "get", _patla)
    monkeypatch.setattr(kj, "jina_cek", lambda *a, **k: ("", "HTTPError"))
    s = kj.cek("https://x.test")
    assert s["metin"] == ""
    assert s["yol"] == ""
    assert "ConnectionError" in s["hata"] and "HTTPError" in s["hata"]


def test_izin_reddi_vekil_denemez(monkeypatch):
    """EN KRITIK: izin yoksa Jina HIC denenmez (vekil korumasi)."""
    cagrildi = []
    monkeypatch.setattr(kj, "jina_cek",
                        lambda *a, **k: cagrildi.append(1) or ("# icerik", ""))

    class _Yazici:
        def url_hata_kaydet(self, *a, **k):
            pass

    import company_master.etl.scrape_kayit as sk
    eski = sk.KazimaYazici.izin_var
    sk.KazimaYazici.izin_var = staticmethod(lambda u: (False, "Disallow"))
    try:
        s = kj.hedef_isle("https://x.test", _Yazici(), kuru=True)
    finally:
        sk.KazimaYazici.izin_var = eski
    assert s["hata"] == 1
    assert "izin yok" in s["neden"]
    assert cagrildi == [], "izin reddinde vekil denenmemeliydi"


def test_jina_url_yoksa_anlasilir_hata(monkeypatch):
    monkeypatch.setenv("NINEROUTER_URL", "")
    monkeypatch.setattr(kj, "_env_oku", lambda ad: "")
    assert kj.jina_cek("https://x.test") == ("", "NINEROUTER_URL_YOK")


def test_env_okuma_anahtari_basmaz():
    """Anahtar degeri hicbir cikti/loga girmez (D-288)."""
    kaynak = (KOK / "scripts" / "kazima_jina_fallback.py").read_text(
        encoding="utf-8")
    assert "print(NINEROUTER_KEY" not in kaynak
    assert "print(_env_oku(\"NINEROUTER_KEY\")" not in kaynak


def test_olcule_yapi_bilinmiyorsa_acik_yazar():
    """D-245: '0 kart' ile 'yapi bilinmiyor' ayni degildir."""
    a = kj._olcule("<html><head><title>x</title></head><body></body></html>")
    assert a["kart_tipi"] is None
    assert a["kart_sayisi"] == 0
    assert a["baslik"] == "x"


def test_olcule_kart_sayar():
    a = kj._olcule("<html><title>t</title>"
                   "<div class='osb-list-card'>1</div>"
                   "<div class='osb-list-card'>2</div></html>")
    assert a["kart_tipi"] == "osb-list-card"
    assert a["kart_sayisi"] == 2


def test_kuru_mod_hicbir_sey_yazmaz(monkeypatch):
    yazilan = []
    monkeypatch.setattr(kj, "cek", lambda *a, **k: {
        "yol": "dogrudan", "metin": "<html></html>", "hata": ""})
    import company_master.etl.scrape_kayit as sk
    eski = sk.KazimaYazici.izin_var
    sk.KazimaYazici.izin_var = staticmethod(lambda u: (True, ""))
    try:
        s = kj.hedef_isle("https://x.test", type("Y", (), {
            "url_hata_kaydet": lambda *a, **k: yazilan.append(1)})(), kuru=True)
    finally:
        sk.KazimaYazici.izin_var = eski
    assert s["yazilan"] == 0
    assert yazilan == []