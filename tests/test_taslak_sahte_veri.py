# -*- coding: utf-8 -*-
"""K3-10c: Taslak modda sahte kutu üretilir ama ekranda 'SAHTE VERİ' yazar.

KAHİN kararı (2026-09-26): "UX yaparken sahte veri yazılır ama sahte olduğu
belirtilir." Bu test iki yönü de kilitler:
  1. Taslak KAPALI → boş hücre çizilmez (K3-10 kuralı).
  2. Taslak AÇIK  → hücre çizilir + "SAHTE VERİ" uyarısı basılır.
Ayrıca conic-gradient halkanın paketsiz ve yüzde kırpmalı olduğunu doğrular.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from web_dashboard.tabs import ana_kontrol as ak  # noqa: E402


def _yakala(monkeypatch):
    """st.columns/markdown/caption/info çağrılarını toplar."""
    kayit: dict[str, list] = {"caption": [], "info": [], "markdown": [], "kolon": []}

    class _Kolon:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _columns(n, **kw):
        kayit["kolon"].append(n if isinstance(n, int) else len(n))
        return [_Kolon() for _ in range(n if isinstance(n, int) else len(n))]

    monkeypatch.setattr(ak.st, "columns", _columns)
    monkeypatch.setattr(ak.st, "caption", lambda m, **k: kayit["caption"].append(m))
    monkeypatch.setattr(ak.st, "info", lambda m, **k: kayit["info"].append(m))
    monkeypatch.setattr(ak.st, "markdown", lambda m, **k: kayit["markdown"].append(m))
    monkeypatch.setattr(ak, "kpi_karti", lambda *a, **k: None)
    return kayit


ADAYLAR = [
    {"baslik": "Toplam Firma", "deger": 14000},
    {"baslik": "Aktif Kullanıcı", "deger": None},
    {"baslik": "Sinyal", "deger": 0},
]


def test_taslak_kapali_bos_hucre_cizilmez(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", False)
    ak._kart_izgara(ADAYLAR, "veri yok")
    assert kayit["kolon"] == [1], "Sadece gerçek veri kolonu açılmalı"
    assert any("2 metrik henüz veri üretmedi" in c for c in kayit["caption"])
    assert not any("SAHTE" in c for c in kayit["caption"])


def test_taslak_acik_sahte_kutu_isaretlenir(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", True)
    ak._kart_izgara(ADAYLAR, "veri yok")
    assert kayit["kolon"] == [3], "Taslakta 3 kutu da çizilir"
    uyari = [c for c in kayit["caption"] if "SAHTE VERİ" in c]
    assert uyari, "Sahte kutular ekranda işaretlenmeli"
    assert "Aktif Kullanıcı" in uyari[0] and "Sinyal" in uyari[0]


def test_taslak_kapali_tum_hucreler_bos_ise_info(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", False)
    ak._kart_izgara([{"baslik": "X", "deger": None}], "veri yok")
    assert kayit["info"] == ["veri yok"]
    assert kayit["kolon"] == []


def test_yuzde_halka_paketsiz_ve_kirpar():
    html = ak._yuzde_halka("Cache Hit", 42.4)
    assert "conic-gradient" in html and "<script" not in html
    assert "%42" in html
    assert "conic-gradient(#f97316 100.0%" in ak._yuzde_halka("X", 250)
    assert "conic-gradient(#f97316 0.0%" in ak._yuzde_halka("X", -5)
    # XSS: başlık kaçırılır
    assert "&lt;b&gt;" in ak._yuzde_halka("<b>", 10)


def test_halka_satiri_sahte_yuzdeyi_bildirir(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", True)
    ak._halka_satiri([("Cache Hit", 55.0), ("Veri Tamlığı", None)])
    assert kayit["kolon"] == [2]
    assert any("SAHTE VERİ" in c and "Veri Tamlığı" in c for c in kayit["caption"])


def test_hareket_satiri_yatay_bar_ve_sahte_etiket(monkeypatch):
    """K3-10f: yatay barlar paketsiz çizilir, sahte satır ekranda işaretlenir."""
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", True)
    ak._hareket_satiri([("Yeni Firma", 120, "musteri"), ("Giriş", None, "basari")])
    govde = "".join(kayit["markdown"])
    assert "linear-gradient(90deg" in govde and "<script" not in govde
    assert "120" in govde
    assert any("SAHTE VERİ" in c and "Giriş" in c for c in kayit["caption"])


def test_hareket_satiri_taslak_kapali_bos_dusurur(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", False)
    ak._hareket_satiri([("Yeni Firma", 120, "musteri"), ("Giriş", None, "basari")])
    assert not any("SAHTE" in c for c in kayit["caption"])
    assert "Giriş" not in "".join(kayit["markdown"])
    # Hiç veri yoksa tek bilgi satırı kalır, boş blok çizilmez.
    kayit2 = _yakala(monkeypatch)
    ak._hareket_satiri([("Giriş", None, "basari")])
    assert kayit2["markdown"] == [] and kayit2["caption"]


def test_veri_etiketi_ikon_ve_kelime_basar(monkeypatch):
    """VERI-ETIKET-01: gerçek → 🟢 GERÇEK VERİ, sahte → 🔴 SAHTE VERİ."""
    kayit = _yakala(monkeypatch)
    ak._veri_etiketi(["Toplam Firma"], ["Sinyal"])
    satir = kayit["caption"][0]
    assert "🟢 **GERÇEK VERİ**: Toplam Firma" in satir
    assert "🔴 **SAHTE VERİ**: Sinyal" in satir
    # Tek taraflı durumlar karşı etiketi basmaz.
    kayit2 = _yakala(monkeypatch)
    ak._veri_etiketi(["A"], [])
    assert "SAHTE" not in kayit2["caption"][0]
    kayit3 = _yakala(monkeypatch)
    ak._veri_etiketi([], ["B"])
    assert "GERÇEK" not in kayit3["caption"][0]
    # İki liste de boşsa satır hiç basılmaz.
    kayit4 = _yakala(monkeypatch)
    ak._veri_etiketi([], [])
    assert kayit4["caption"] == []


def test_kart_izgara_gercek_veriyi_de_etiketler(monkeypatch):
    kayit = _yakala(monkeypatch)
    monkeypatch.setattr(ak, "TASLAK", True)
    ak._kart_izgara(ADAYLAR, "veri yok")
    satir = "".join(kayit["caption"])
    assert "GERÇEK VERİ" in satir and "Toplam Firma" in satir


if __name__ == "__main__":  # elle koşum: python tests/test_taslak_sahte_veri.py
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
