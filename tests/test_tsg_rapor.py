# -*- coding: utf-8 -*-
"""TSG-06 rapor şablonu mandalları (D-306)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from skills.services import ticaret_sicili_kanit as tsk
from skills.services.tsg_rapor import (
    kalici_adres,
    kanit_anahtari,
    kisi_maskele,
    olumsuz_ilanlar,
    posta_govdesi,
    rapor_konusu,
    rapor_uret,
    son_teyit,
    zaman_cizelgesi,
)

KANIT_A = {
    "ilan_sira_no": "12",
    "icerik_no": "345",
    "gazete_sayi": "11200",
    "gazete_sayfa": "7",
    "yayin_tarihi": "15.03.2026",
    "il_turu": "Adres Degisikligi",
    "alinma_zamani": "2026-09-01T10:00:00+00:00",
}
KANIT_B = {
    "ilan_sira_no": "13",
    "icerik_no": "346",
    "gazete_sayi": "11300",
    "gazete_sayfa": "2",
    "yayin_tarihi": "01.06.2026",
    "il_turu": "Tasfiye",
    "guid": "ABC-123",
    "alinma_zamani": "2026-09-20T10:00:00+00:00",
}


# --- maskeleme --------------------------------------------------------


@pytest.mark.parametrize(
    "girdi,beklenen",
    [
        ("Ahmet Yilmaz", "A*** Y***"),
        ("  Ayse  ", "A***"),
        ("", "bilinmiyor"),
        ("   ", "bilinmiyor"),
        (None, "bilinmiyor"),
    ],
)
def test_kisi_maskele(girdi, beklenen):
    assert kisi_maskele(girdi) == beklenen


def test_maske_ad_uzunlugunu_sizdirmaz():
    """Kisa ve uzun ad ayni uzunlukta maske uretir."""
    assert kisi_maskele("Ali") == kisi_maskele("Abdurrahman")


# --- kanit referansi --------------------------------------------------


def test_kanit_anahtari_dogrulamadan_okur():
    kanit = {**KANIT_A, "dogrulama": {"turetilen": {"anahtar": "ONCEDEN-VAR"}}}
    assert kanit_anahtari(kanit) == "ONCEDEN-VAR"


def test_kanit_anahtari_tek_kapidan_uretilir():
    """Dogrulanmamis kanit da anahtar alir; bicim IlanKaniti ile ayni (K-1)."""
    beklenen = tsk.IlanKaniti(
        ilan_sira_no="12", icerik_no="345",
        gazete_sayi="11200", gazete_sayfa="7",
    ).kanit_anahtari()
    assert kanit_anahtari(KANIT_A) == beklenen == "12-11200-7"


def test_kalici_adres_guid_yoksa_yok():
    assert kalici_adres(KANIT_A) is None
    assert kalici_adres(KANIT_B) == tsk.ILAN_GOSTER_URL.format(guid="ABC-123")


# --- son teyit --------------------------------------------------------


def test_son_teyit_en_yeniyi_alir():
    assert son_teyit([KANIT_A, KANIT_B]) == "2026-09-20T10:00:00+00:00"


def test_son_teyit_kanit_yoksa_tarih_uydurmaz():
    """Bugunun tarihi yazilmaz (D-268)."""
    assert son_teyit([]) == "bilinmiyor"


# --- zaman cizelgesi --------------------------------------------------


def test_cizelge_tarihe_gore_sirali():
    cizelge = zaman_cizelgesi([KANIT_B, KANIT_A])
    assert [s["tarih"] for s in cizelge] == ["2026-03-15", "2026-06-01"]


def test_cozulemeyen_tarih_dusmez_sona_gider():
    bozuk = {**KANIT_A, "yayin_tarihi": "bilinmez", "tescil_tarihi": ""}
    cizelge = zaman_cizelgesi([bozuk, KANIT_B])
    assert len(cizelge) == 2
    assert cizelge[-1]["tarih"] is None
    assert cizelge[-1]["tarih_ham"] == "bilinmez"


def test_eslesmeyen_ilan_turu_unknown():
    assert zaman_cizelgesi([KANIT_A])[0]["yon"] == "unknown"


# --- olumsuz ilan -----------------------------------------------------


def test_esleme_disi_etiket_olculemez():
    """Sozluk TSG-04 ile dolu (D-307); sozlukte olmayan etiket hala 'olculemez' doner (D-216)."""
    assert "Adres Degisikligi" not in tsk.ILAN_TURU_ESLEME
    assert "Tasfiye" not in tsk.ILAN_TURU_ESLEME
    sonuc = olumsuz_ilanlar([KANIT_A, KANIT_B])
    assert sonuc["olculebilir"] is False
    assert len(sonuc["etiketsiz"]) == 2
    assert not sonuc["satirlar"]


def test_esleme_dolunca_negatif_ayiklanir(monkeypatch):
    monkeypatch.setitem(tsk.ILAN_TURU_ESLEME, "Tasfiye", ("liquidation", "negative"))
    monkeypatch.setitem(tsk.ILAN_TURU_ESLEME, "Adres Degisikligi", ("move", "stable"))
    sonuc = olumsuz_ilanlar([KANIT_A, KANIT_B])
    assert sonuc["olculebilir"] is True
    assert [s["ilan_turu"] for s in sonuc["satirlar"]] == ["Tasfiye"]


# --- rapor ------------------------------------------------------------


SIMDI = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


def test_rapor_zorunlu_bolumleri_icerir():
    metin = rapor_uret(
        "ORNEK AS", [KANIT_A, KANIT_B],
        kapsam={"ticaretsicil.gov.tr": "tarandi"},
        kisiler=["Ahmet Yilmaz"],
        uretim_zamani=SIMDI,
    )
    for baslik in ("# Ticaret Sicili Raporu", "## Zaman cizelgesi",
                   "## Olumsuz ilanlar", "## Kapsam (son 1 gun)",
                   "## Kisiler (maskeli)"):
        assert baslik in metin
    assert "Son teyit:** 2026-09-20T10:00:00+00:00" in metin
    assert "A*** Y***" in metin
    assert "Ahmet" not in metin, "acik kisi adi rapora sizdi"
    assert tsk.ILAN_GOSTER_URL.format(guid="ABC-123") in metin


def test_kapsam_verilmezse_tam_kapsam_iddiasi_edilmez():
    metin = rapor_uret("ORNEK AS", [KANIT_A], uretim_zamani=SIMDI)
    assert "OLCULMEDI" in metin


def test_kanitsiz_rapor_patlamaz():
    metin = rapor_uret("", [], uretim_zamani=SIMDI)
    assert "bilinmiyor" in metin
    assert "(kayit yok)" in metin


def test_posta_govdesi_html_kacisi_yapar():
    """Kanit metnindeki `<` HTML'e ham gecmez."""
    govde = posta_govdesi("unvan: <script>x</script> & co")
    assert "<script>" not in govde
    assert "&lt;script&gt;" in govde
    assert govde.startswith("<pre>") and govde.endswith("</pre>")


def test_posta_konusu_tek_yerden():
    assert rapor_konusu("ORNEK AS") == "Ticaret Sicili Raporu: ORNEK AS"
    assert rapor_konusu("") == "Ticaret Sicili Raporu: bilinmiyor"
