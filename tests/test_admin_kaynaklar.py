# -*- coding: utf-8 -*-
"""UI-ADMIN-KAYNAKLAR-SAYFA-34 + UI-ADMIN-CRAWL-TASI-35 — "Veri Kaynakları" testleri.

Kapsam (34, ≤10 test):
  - Bölüm/anchor tutarlılığı (ADMIN-UI-10)
  - Boş tablo → "Henüz kazıma yapılmadı" (D-249: veri yok ≠ 0)
  - Tek kaynak → rozet metni üretimi
  - `st.metric` kullanılmaz (ADMIN-KPI-KART-02 deseni)
  - SECTIONS kaydı (metrikler altında, sira=5)
  - Salt okuma: yazma yolu yok (KazimaYazici tek yazıcı kalır)

Kapsam (35, taşınan crawl kontrolü):
  - `_log_crawl_action` / `_crawl_is_enabled` / `CRAWL_STATUS_*` tek dosyada (D-211)
  - `webhook_monitor.py` içinde "Crawl Kontrolü" 0 satır (brif kabul kriteri)
  - Yönlendirme satırı `tab_getir("kaynaklar")` kullanır
  - Panel `Section(..., seviye=3)` ile, menü bölümüne girmeden çizilir
  - Başlat / iki adımlı onaylı durdur durum geçişleri
  - Yetki: admin_email yoksa butonlar devre dışı
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODUL = ROOT / "web_dashboard" / "tabs" / "admin_kaynaklar.py"

BOS_ROZETLERI = {"Henüz kazıma yapılmadı", "Sağlıklı", "Bozulma var", "Kritik"}


@pytest.fixture(scope="module")
def mod():
    from web_dashboard.tabs import admin_kaynaklar

    return admin_kaynaklar


def _ornek_kaynak(toplam: int = 10, basarili: int = 9) -> dict:
    return {
        "kaynak_id": "ostim.org.tr",
        "kaynak_adi": "ostim.org.tr",
        "toplam_cekis": toplam,
        "basarili_cekis": basarili,
        "son_cekis_zaman": "2026-10-03T21:50:41",
        "son_n_cekisler": [True] * 10,
    }


def test_bolum_kimlikleri_tekil(mod):
    """Dört bölüm, dört ayrı anchor kimliği."""
    kimlikler = [b.kimlik for b in mod.BOLUMLER]
    assert len(kimlikler) == 4
    assert len(set(kimlikler)) == 4


def test_tanimsiz_bolum_keyerror_verir(mod):
    with pytest.raises(KeyError):
        mod._bolum("olmayan-bolum")


def test_bos_tabloda_rozet_basarili_yazar(mod):
    """Üç tablo da boşsa "Henüz kazıma yapılmadı" — 0 başarısız değil (D-249)."""
    assert mod.ozet_metin([], [], []) == mod.BOS_ROZETI
    assert mod.BOS_ROZETI not in {"0", "0.0"}


def test_tek_kaynak_rozet_metni_uretilir(mod):
    """Tek kaynak → geçerli rozet metni (kabul kriteri)."""
    kartlar = mod.kaynak_saglik_kartlari([_ornek_kaynak()])
    assert len(kartlar) == 1
    rozet = mod.saglik_rozet_metni(kartlar[0].skor)
    assert rozet in BOS_ROZETLERI - {mod.BOS_ROZETI}


def test_ozet_metin_toplamlari_yazar(mod):
    metin = mod.ozet_metin([_ornek_kaynak(10, 9)], [{"hata": 1}], [{"sayfa_adedi": 3}])
    assert "1 kaynak" in metin
    assert "10 çekiş" in metin
    assert "9 başarılı" in metin
    assert "3 sayfa" in metin


def test_bos_liste_kart_dondurmez(mod):
    assert mod.kaynak_saglik_kartlari([]) == []


def test_cekis_yoksa_basari_orani_sifir(mod):
    """Veri yok → 0.0; bölme hatası üretmez."""
    assert mod.basari_orani(0, 0) == 0.0
    assert mod.basari_orani(4, 2) == 0.5


def test_st_metric_kullanilmaz(mod):
    """ADMIN-KPI-KART-02 deseni: sayfa `st.metric` çağırmaz."""
    kaynak = MODUL.read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    cagrilar = [
        satir
        for satir in ast.walk(agac)
        if isinstance(satir, ast.Call)
        and isinstance(satir.func, ast.Attribute)
        and satir.func.attr == "metric"
    ]
    assert cagrilar == [], f"admin_kaynaklar.py st.metric çağırıyor: {cagrilar}"


def test_salt_okuma_yazma_yolu_yok(mod):
    """0050 tablolarına INSERT/UPDATE/DELETE geçmemeli (KazimaYazici tek yazıcı)."""
    kaynak = MODUL.read_text(encoding="utf-8").lower()
    for yasak in ("insert into", "update scrape", "delete from", " truncate "):
        assert yasak not in kaynak, f"admin_kaynaklar.py yazma yolu içeriyor: {yasak}"


def test_sections_kaydi_dogru():
    """Metrikler (veri_kalite) altında, sira=5, admin rolü."""
    from web_dashboard.tabs import tab_getir

    t = tab_getir("kaynaklar")
    assert (t.url_path, t.ust, t.sira) == ("kaynaklar", "veri_kalite", 5)
    assert t.modul == "web_dashboard.tabs.admin_kaynaklar"
    assert t.fonksiyon == "render_kaynaklar_tab"
    assert t.min_rol == "admin"


# ---------------------------------------------------------------------------
# UI-ADMIN-CRAWL-TASI-35 — crawl kontrolü bu sayfaya TAŞINDI
# ---------------------------------------------------------------------------


def test_crawl_durum_sabitleri_tek_dosyada(mod):
    """D-211: `_log_crawl_action` / `_crawl_is_enabled` / `CRAWL_STATUS_` tek tanım."""
    tanimlar = []
    for yol in (ROOT / "web_dashboard").rglob("*.py"):
        metin = yol.read_text(encoding="utf-8")
        for istenen in ("def _log_crawl_action", "def _crawl_is_enabled",
                        "CRAWL_STATUS_BEKLEMEDE ="):
            if istenen in metin:
                tanimlar.append(f"{yol.name}:{istenen}")
    assert tanimlar == ["admin_kaynaklar.py:def _log_crawl_action",
                        "admin_kaynaklar.py:def _crawl_is_enabled",
                        "admin_kaynaklar.py:CRAWL_STATUS_BEKLEMEDE ="], tanimlar


def test_webhook_monitorde_crawl_kontrolu_kalmadi():
    """Brif kabul kriteri: webhook_monitor.py'de 'Crawl Kontrolü' 0 satır."""
    kaynak = (ROOT / "web_dashboard" / "tabs" / "webhook_monitor.py").read_text(
        encoding="utf-8")
    assert "Crawl Kontrol" not in kaynak
    assert "Crawl Başlat" not in kaynak


def test_webhook_monitor_veri_kaynaklarina_link_verir():
    """Webhook ekranı artık yönlendirme satırı basar; kanonik adresi `tab_getir` verir."""
    kaynak = (ROOT / "web_dashboard" / "tabs" / "webhook_monitor.py").read_text(
        encoding="utf-8")
    assert 'tab_getir("kaynaklar")' in kaynak
    assert "st.link_button(" in kaynak


def test_crawl_kontrolu_son_calismalardan_once_cizilir(mod):
    """Crawl paneli, brief gereği 'Son Çalışmalar' bölümünün üstünde."""
    kaynak = MODUL.read_text(encoding="utf-8")
    i_crawl = kaynak.index("_render_crawl_kontrolu()\n")
    i_son = kaynak.index("_render_son_calismalar(calismalar)")
    assert i_crawl < i_son


def test_crawl_kontrolu_seviye3_alt_baslik_ile_cizilir(mod, monkeypatch):
    """`Section(..., seviye=3)` kullanılır; ana bölüm listesine girmez (D-213 menü tekliği)."""
    from unittest.mock import MagicMock

    cizilen = []

    def _sahte(*a, **k):
        t = MagicMock()
        t.render.side_effect = lambda: cizilen.append((k.get("kimlik"), k.get("seviye")))
        return t

    monkeypatch.setattr(mod, "Section", _sahte)
    monkeypatch.setattr(mod.st, "caption", MagicMock())
    monkeypatch.setattr(mod.st, "checkbox", MagicMock())
    monkeypatch.setattr(mod.st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(mod.st, "columns", lambda *a, **k: [MagicMock(), MagicMock(), MagicMock()])

    mod._render_crawl_kontrolu()

    assert ("crawl-kontrolu", 3) in cizilen
    assert "crawl-kontrolu" not in [b.kimlik for b in mod.BOLUMLER]


def test_crawl_durumu_ve_yetki_korumasi(mod, monkeypatch):
    """Yetkisizde butonlar devre dışı; admin_email yoksa salt okuma."""
    from unittest.mock import MagicMock

    monkeypatch.setattr(mod, "Section", lambda *a, **k: MagicMock())
    monkeypatch.setattr(mod.st, "caption", MagicMock())
    seen = {}

    def _cb(label, **k):
        seen["checkbox"] = k
        return False

    def _btn(label, **k):
        seen.setdefault("buttons", []).append((label, k.get("disabled")))
        return False

    monkeypatch.setattr(mod.st, "checkbox", _cb)
    monkeypatch.setattr(mod.st, "button", _btn)
    monkeypatch.setattr(mod.st, "columns", lambda *a, **k: [MagicMock(), MagicMock(), MagicMock()])

    # admin_email yok -> yetkisiz
    monkeypatch.setitem(mod.st.session_state, "admin_email", "")
    monkeypatch.setitem(mod.st.session_state, "crawl_status", mod.CRAWL_STATUS_BEKLEMEDE)
    mod._render_crawl_kontrolu()
    assert seen["checkbox"]["disabled"] is True
    assert seen["buttons"][0][1] is True, seen["buttons"]

    # admin -> butonlar açık
    seen.clear()
    monkeypatch.setitem(mod.st.session_state, "admin_email", "ihsan@local")
    mod._render_crawl_kontrolu()
    assert seen["buttons"][0][1] is False, seen["buttons"]


def test_crawl_baslat_durdur_durum_gecisleri(mod, monkeypatch):
    """Başlat -> CALISIYOR, iki adımlı onaylı durdur -> DURDURULDU."""
    from unittest.mock import MagicMock

    monkeypatch.setattr(mod, "Section", lambda *a, **k: MagicMock())
    monkeypatch.setattr(mod.st, "caption", MagicMock())
    monkeypatch.setattr(mod.st, "checkbox", MagicMock())
    monkeypatch.setattr(mod.st, "success", MagicMock())
    monkeypatch.setattr(mod.st, "rerun", MagicMock())
    monkeypatch.setitem(mod.st.session_state, "admin_email", "ihsan@local")

    def _columns(*a, **k):
        n = a[0] if a else 3
        if isinstance(n, (list, tuple)):
            n = len(n)
        return [MagicMock() for _ in range(n)]

    monkeypatch.setattr(mod.st, "columns", _columns)

    # 1) BASLAT
    monkeypatch.setitem(mod.st.session_state, "crawl_status", mod.CRAWL_STATUS_BEKLEMEDE)
    monkeypatch.setattr(mod.st, "button",
                        lambda label, **k: label == "▶️ Crawl Başlat")
    mod._render_crawl_kontrolu()
    assert mod.st.session_state["crawl_status"] == mod.CRAWL_STATUS_CALISIYOR

    # 2) DURDUR (ilk tik -> onay iste)
    monkeypatch.setattr(mod.st, "button",
                        lambda label, **k: label == "⏹️ Crawl Durdur")
    mod._render_crawl_kontrolu()
    assert mod.st.session_state["crawl_stop_confirm"] is True

    # 3) DURDUR (onay -> durduruldu)
    monkeypatch.setattr(mod.st, "button",
                        lambda label, **k: label == "✅ Evet, Durdur")
    mod._render_crawl_kontrolu()
    assert mod.st.session_state["crawl_status"] == mod.CRAWL_STATUS_DURDURULDU
    assert mod.st.session_state["crawl_stop_confirm"] is False


def test_crawl_durum_ikonlari_dort_durumu_kapsar(mod):
    assert set(mod.CRAWL_DURUM_IKONLARI) == {
        mod.CRAWL_STATUS_BEKLEMEDE, mod.CRAWL_STATUS_CALISIYOR,
        mod.CRAWL_STATUS_BASARISIZ, mod.CRAWL_STATUS_DURDURULDU,
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
