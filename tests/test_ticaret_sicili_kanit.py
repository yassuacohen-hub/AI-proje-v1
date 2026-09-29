# -*- coding: utf-8 -*-
"""Ticaret sicili kanıt katmanı testleri (D-270).

Veriler GERÇEK kayıtlardan alınmıştır (KAHİN ekran görüntüleri, 2026-09-29):
  MERSİS 00120320741000024 / Sicil 448217 / İlan 49136 / (21341515)

D-268: bu testler varsayımı değil ÖLÇÜLMÜŞ gerçeği korur. MERSİS'in
**17** haneli olduğu Webtekno'nun "16" iddiasına rağmen ölçülerek sabitlendi.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.services.ticaret_sicili_kanit import (  # noqa: E402
    ILAN_GOSTER_URL,
    KATMANLAR,
)

UNVAN = "AKANA MÜHENDİSLİK VE TİCARET ANONİM ŞİRKETİ BAŞKENT ORGANİZE ŞUBESİ"
MERSIS = "00120320741000024"
ADRES = "Malıköy Başkent OSB Mah. 16 Cad. Akana No: 9 Sincan / Ankara"


def _kanit(**ustune: object):
    """Gerçek kayda dayanan varsayılan kanıt."""
    from skills.services.ticaret_sicili_kanit import IlanKaniti

    veri = dict(
        ilan_sira_no="49136",
        icerik_no="21341515",
        mersis_no=MERSIS,
        ticaret_sicil_no="448217",
        ticaret_unvani=UNVAN,
        adres=ADRES,
        mudurluk="ANKARA",
        yayin_tarihi="21.08.2026",
        gazete_sayi="11649",
        gazete_sayfa="67",
        tescil_tarihi="20.08.2026",
        tescil_edilen_husus="Adres",
    )
    veri.update(ustune)
    return IlanKaniti(**veri)  # type: ignore[arg-type]


# ----------------------------------------------------------------------
# Bicim kurallari (D-268: 17 hane olculdu)
# ----------------------------------------------------------------------


def test_mersis_gercek_kayitta_gecerli():
    """ÖLÇÜLEN gerçek MERSİS 17 hanedir; 16 değil."""
    assert len(MERSIS) == 17
    assert _kanit().dogrula()["sonuc"] == "gecerli"


def test_mersis_16_hane_vkn_turetir():
    """SÖZLEŞE §3.4b: 16 haneli MERSIS ilk 10 hanesi VKN'dir (D-275)."""
    # Varsayılan kanıt 17 haneli (KAHİN'in okuma kayması); kanonik 16'yı dene.
    kanit = _kanit(mersis_no="0120320741000024")
    aci = next(
        b for b in kanit.dogrula()["bulgular"] if b["kod"] == "MERSIS_ACILIM"
    )
    assert "VKN=0120320741" in aci["mesaj"]


def test_mersis_vkn_dogrulandi():
    """Gecerli VKN turetilebilir."""
    kodlar = {b["kod"] for b in _kanit().dogrula()["bulgular"]}
    assert "MERSIS_VKN_DOGRULANDI" in kodlar


def test_mersis_17_hane_okuma_kaymasi_uyarisi():
    """KAHIN'in gercek kaydi 17 hane; kanonik 16 -> uyari (D-275)."""
    kanit = _kanit(mersis_no="00120320741000024")
    kodlar = {b["kod"] for b in kanit.dogrula()["bulgular"]}
    assert "MERSIS_17_HANE" in kodlar
    assert kanit.dogrula()["sonuc"] == "gecerli"


def test_mersis_17_hane_gecersiz_vkn_hata():
    """17 hane ama ilk 10 hane gecersiz VKN -> bicim hatasi (D-275).

    `9999999999` GIB saglamasindan GECMEZ (olculdu). `0123456789` gecerlidir;
    onu kullanmak testi yaniltirdi.
    """
    dogr = _kanit(mersis_no="09999999999000024").dogrula()
    assert dogr["sonuc"] == "supheli"
    assert "MERSIS_17_HANE" not in {b["kod"] for b in dogr["bulgular"]}


def test_mersis_16_hane_gecersiz_vkn_hata():
    """16 hane ama VKN saglamasi gecmiyor -> mersis_no ve vkn NULL (K-2)."""
    dogr = _kanit(mersis_no="9999999999999999").dogrula()
    assert "MERSIS_VKN_GECERSIZ" in {b["kod"] for b in dogr["bulgular"]}
    assert dogr["sonuc"] == "supheli"


def test_kahin_hipotezi_dogrulandi():
    """KAHIN: bastaki 0 cikarilinca 16 hane -> DOGRULANDI (D-275)."""
    from skills.services.ticaret_sicili_kanit import MERSIS_VKN_IDDIASI

    assert MERSIS_VKN_IDDIASI["durum"].startswith("DOGRULANDI")


def test_sahis_isletmesinde_turetme_yapilmaz():
    """D-275: sahis isletmesinde TCKN 11 hane; MERSIS'ten turetme yapilmaz."""
    from skills.services.ticaret_sicili_kanit import MERSIS_VKN_IDDIASI

    assert "TURETILMEZ" in MERSIS_VKN_IDDIASI["sahis_isletmesi"]


def test_vkn_kontrol_tek_kaynaga_delegasyon():
    """K-1: vkn_kontrol() kendi algoritmasini YAZMAZ, tek kaynagi cagirir."""
    from skills.services.ticaret_sicili_kanit import vkn_kontrol

    sonuc = vkn_kontrol("0120320741")
    assert sonuc["gecerli"] is True
    assert sonuc["kaynak"] == "kimlik_no.vkn_gecerli"



def test_vkn_kontrol_bicim_hatasi():
    from skills.services.ticaret_sicili_kanit import vkn_kontrol

    assert vkn_kontrol("123")["gecerli"] is None
    assert vkn_kontrol("")["gecerli"] is None
    assert vkn_kontrol("abcdefghij")["gecerli"] is None


def test_mersis_bicim_hatasi_yakalanir():
    assert "MERSIS_BICIM" in {
        b["kod"] for b in _kanit(mersis_no="123").dogrula()["bulgular"]
    }


def test_mersis_bos_hata_verir():
    dogr = _kanit(mersis_no="").dogrula()
    assert dogr["sonuc"] == "supheli"
    assert "MERSIS_YOK" in {b["kod"] for b in dogr["bulgular"]}


# ----------------------------------------------------------------------
# Sirket tipi
# ----------------------------------------------------------------------


def test_sirket_tipi_sube_tespit_edilir():
    assert _kanit().dogrula()["turetilen"]["sirket_tipi"] == "sube"


def test_sirket_tipi_ana_sirket():
    kanit = _kanit(
        ticaret_unvani="AKANA MÜHENDİSLİK VE TİCARET ANONİM ŞİRKETİ",
        ticaret_sicil_no="79163",
    )
    assert kanit.dogrula()["turetilen"]["sirket_tipi"] == "as"


# ----------------------------------------------------------------------
# Zorunlu alanlar
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "alan", ["ticaret_sicil_no", "ticaret_unvani", "yayin_tarihi"]
)
def test_zorunlu_alan_bos_hata(alan: str):
    dogr = _kanit(**{alan: ""}).dogrula()
    assert dogr["sonuc"] == "supheli"
    assert f"ZORUNLU_{alan.upper()}" in {b["kod"] for b in dogr["bulgular"]}


# ----------------------------------------------------------------------
# Tarih sirasi
# ----------------------------------------------------------------------


def test_yayin_tescilden_once_hata():
    """Gazete yayını, tescilden önce olamaz."""
    dogr = _kanit(yayin_tarihi="01.01.2020", tescil_tarihi="20.08.2026").dogrula()
    assert dogr["sonuc"] == "supheli"
    assert "TARIH_SIRASI" in {b["kod"] for b in dogr["bulgular"]}


def test_tarih_bilinmiyorsa_atlanir():
    """D-268: bilinmeyen format UYDURULMAZ, kontrol atlanır."""
    assert _kanit(yayin_tarihi="belirsiz").dogrula()["sonuc"] == "gecerli"


# ----------------------------------------------------------------------
# Kanit anahtari ve kalicilik
# ----------------------------------------------------------------------


def test_kanit_anahtari_ucullu():
    assert _kanit().kanit_anahtari() == "49136-11649-67"




def test_kanit_kaydedilir_ve_geri_okunur(tmp_path: Path, monkeypatch):
    """Kanıt kendi verisiyle birlikte diske yazılır ve okunabilir."""
    import skills.services.ticaret_sicili_kanit as modul

    gecici = tmp_path / "kanit"
    monkeypatch.setattr(modul, "KANIT_DIZIN", gecici)

    sonuc = modul.kanit_kaydet(
        ilan_sira_no="49136",
        icerik_no="21341515",
        mersis_no=MERSIS,
        ticaret_sicil_no="448217",
        ticaret_unvani=UNVAN,
        adres=ADRES,
        mudurluk="ANKARA",
        yayin_tarihi="21.08.2026",
        gazete_sayi="11649",
        gazete_sayfa="67",
        tescil_tarihi="20.08.2026",
        tescil_edilen_husus="Adres",
    )
    assert sonuc["sonuc"] == "gecerli"

    dosya = gecici / "49136-11649-67.json"
    assert dosya.is_file()
    veri = json.loads(dosya.read_text(encoding="utf-8"))
    assert veri["mersis_no"] == MERSIS
    assert veri["dogrulama"]["sonuc"] == "gecerli"
    assert veri["alinma_zamani"]  # zaman damgasi dolu


def test_kanit_listele_sayar(tmp_path: Path, monkeypatch):
    import skills.services.ticaret_sicili_kanit as modul

    gecici = tmp_path / "kanit"
    gecici.mkdir()
    (gecici / "a.json").write_text(
        json.dumps(
            {
                "ticaret_sicil_no": "448217",
                "ticaret_unvani": UNVAN,
                "dogrulama": {
                    "sonuc": "gecerli",
                    "turetilen": {"sirket_tipi": "sube"},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(modul, "KANIT_DIZIN", gecici)
    sonuc = modul.kanit_listele()
    assert sonuc["kayit"] == 1
    assert sonuc["liste"][0]["sirket_tipi"] == "sube"


def test_bozuk_json_dokunmadan_isaretlenir(tmp_path: Path, monkeypatch):
    """Okunamayan kanıt listede `okunamadi` olarak görünür, patlamaz."""
    import skills.services.ticaret_sicili_kanit as modul

    gecici = tmp_path / "kanit"
    gecici.mkdir()
    (gecici / "bozuk.json").write_text("{bozuk", encoding="utf-8")
    monkeypatch.setattr(modul, "KANIT_DIZIN", gecici)
    sonuc = modul.kanit_listele()
    assert sonuc["kayit"] == 1
    assert sonuc["liste"][0]["sonuc"] == "okunamadi"


def test_supheli_kanit_silinmez(tmp_path: Path, monkeypatch):
    """D-216: hatalı kanıt da kayıttır — silinmez, işaretlenir."""
    import skills.services.ticaret_sicili_kanit as modul

    gecici = tmp_path / "kanit"
    monkeypatch.setattr(modul, "KANIT_DIZIN", gecici)
    modul.kanit_kaydet(
        ilan_sira_no="1", icerik_no="1", mersis_no="123",
        ticaret_sicil_no="79163", yayin_tarihi="01.01.2020",
    )
    dosya = gecici / "1-E-E.json"
    assert dosya.is_file()
    veri = json.loads(dosya.read_text(encoding="utf-8"))
    assert veri["dogrulama"]["sonuc"] == "supheli"


def test_kanit_anahtari_eksik_alanla_calisir():
    """Sayı/sayfa yoksa anahtar `E` ile üretilir, ÇÖKMEZ (D-216/D-271).

    `?` Windows dosya adında geçersizdir; OSError fırlatır.
    """
    assert _kanit(gazete_sayi="", gazete_sayfa="").kanit_anahtari() == (
        "49136-E-E"
    )


def test_kanit_anahtari_gecersiz_karakter_ayiklanir():
    """Dosya adına karışabilecek karakterler temizlenir."""
    assert "/" not in _kanit(ilan_sira_no="4/91").kanit_anahtari()


# ----------------------------------------------------------------------
# D-272: Grup / nokta analizi (fabrika, sube, bayi)
# ----------------------------------------------------------------------

#: KAHİN'in 2. ekran görüntüsündeki GERÇEK tablo (6 satır).
GERCEK_TABLO = [
    {"sicil_no": "448217", "unvan": "AKANA ... BASKENT ORGANIZE SUBESI",
     "il_turu": "SUBE (ADRES DEGISIKLIGI)"},
    {"sicil_no": "546008", "unvan": "AKANA ... ARGE SUBESI",
     "il_turu": "SUBE ACILIS"},
    {"sicil_no": "518675", "unvan": "AKANA ... SINCAN SUBESI",
     "il_turu": "SUBE (YONETIM - TEMSIL)"},
    {"sicil_no": "448217", "unvan": "AKANA ... BASKENT ORGANIZE SUBESI",
     "il_turu": "SUBE (YONETIM - TEMSIL)"},
    {"sicil_no": "79163", "unvan": "AKANA MUHENDISLIK VE TICARET ANONIM SIRKETI",
     "il_turu": "ANONIM SIRKET (YONETIM - TEMSIL VE DIGER)"},
    {"sicil_no": "79163", "unvan": "AKANA MUHENDISLIK VE TICARET ANONIM SIRKETI",
     "il_turu": "DENETCI"},
]


def test_grup_nokta_sayisi_gercek_tablo():
    """6 gerçek kayıttan grup genişliği ölçülür."""
    k = _kanit()
    g = k.grup_olustur("AKANA MUHENDISLIK VE TICARET ANONIM SIRKETI", GERCEK_TABLO)
    assert g["nokta_sayisi"] == 6


def test_grup_ana_kayit_sube_degil():
    """Ana sicil no, ŞUBESİ olmayan kayıttan gelir (79163)."""
    k = _kanit()
    g = k.grup_olustur("AKANA MUHENDISLIK VE TICARET ANONIM SIRKETI", GERCEK_TABLO)
    assert g["ana_sicil_no"] == "79163"


def test_il_turu_dagilimi_hesaplanir():
    k = _kanit()
    g = k.grup_olustur("AKANA", GERCEK_TABLO)
    dag = g["il_turu_dagilimi"]
    assert dag["SUBE (YONETIM - TEMSIL)"] == 2
    assert dag["DENETCI"] == 1
    assert sum(dag.values()) == 6


def test_yeni_acilis_buyume_sinyali():
    """Şube açılışı = büyüme sinyali."""
    k = _kanit()
    k.grup_olustur("AKANA", GERCEK_TABLO)
    a = k.genislik_analizi()
    assert a["yeni_acilan"] == 1
    assert a["sinyal"] == "buyume"


def test_adres_degisikligi_tasinma_sinyali():
    k = _kanit()
    k.grup_olustur("AKANA", [
        {"sicil_no": "1", "unvan": "X SUBESI", "il_turu": "SUBE (ADRES DEGISIKLIGI)"},
    ])
    a = k.genislik_analizi()
    assert a["adres_degisikligi"] == 1
    assert a["sinyal"] == "tasinma"


def test_bos_kayit_durgun_sinyali():
    k = _kanit()
    k.grup_olustur("AKANA", [])
    assert k.genislik_analizi()["sinyal"] == "durgun"


def test_bos_liste_cokmez():
    """D-216: kayıt yoksa çökmez, 0 döner."""
    k = _kanit()
    g = k.grup_olustur("YOK", [])
    assert g["nokta_sayisi"] == 0
    assert g["il_turu_dagilimi"] == {}


# ----------------------------------------------------------------------
# D-273: Katman / erişim (ucretsiz vs ucretli)
# ----------------------------------------------------------------------


def test_katman0_varsayilan_ve_bedava():
    """D-273: varsayılan katman 0, maliyet sıfır."""
    k = _kanit()
    kapsam = k.kanit_kapsami()
    assert kapsam["katman"] == 0
    assert kapsam["maliyet"] == "0"
    assert kapsam["katman_adi"] == "ucretsiz-uyelik"


def test_katman0_kanit_yeterli():
    """Gerçek kayıt ücretsiz katmanda kanıt üretmeye yeterli."""
    k = _kanit(il_turu="SUBE (ADRES DEGISIKLIGI)", delil_belgeler="X")
    kapsam = k.kanit_kapsami()
    assert kapsam["kanit_yeterli"] is True


def test_katman1_ucretli_onerilmez():
    """D-273: ücretli katman kodda ÖNERİLMEZ olarak işaretli."""
    assert KATMANLAR[1]["durum"] == "ONERILMEZ"


def test_katman1_fiyati_olculmemis():
    """D-268: fiyat UYDURULMAZ; 'çok pahalı' ölçülmedi olarak kalır."""
    assert KATMANLAR[1]["maliyet"] == "OLCULMEDI/COK_PAHALI"


def test_katman1_guid_ile_kalici_adres():
    """Ücretli katmanın kalıcı adresi `goster.php?Guid=`."""
    k = _kanit(guid="4fb204d4-8b72-11e9-a292-54e0589", katman=1)
    adres = k.kanit_kapsami()["kalici_adres"]
    assert adres is not None
    assert "goster.php?Guid=4fb204d4" in adres


def test_katman0_guid_yok():
    """Ücretsiz katmanda `guid` boş kalır, adres üretilmez."""
    assert _kanit().kanit_kapsami()["kalici_adres"] is None


def test_eksik_alanlar_bildirilir():
    """Kanıtta hangi alan eksikse açıkça listelenir."""
    kapsam = _kanit().kanit_kapsami()
    assert "delil_belgeler" in kapsam["eksik_alanlar"]


def test_ilan_goster_url_sablonu():
    """Kalıcı adres şablonu kaynakta birebir geçer."""
    assert "{guid}" in ILAN_GOSTER_URL
    assert "goster.php" in ILAN_GOSTER_URL




def test_kanit_eksik_alanlari_bildirir():
    assert "delil_belgeler" in _kanit(delil_belgeler=None)._doluluk()["bos"]
