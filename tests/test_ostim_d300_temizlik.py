"""D-300 regresyon testleri — telefon ve cok-bloklu adres temizligi.

Neden bu dosya var:
  D-300 duzeltmeleri ONCEDEN yalniz elle komut satirinda dogrulandi,
  hicbir teste yazilmamisti. Yanlis bir duzeltmenin geri gelmesi
  kimse tarafindan yakalanamazdi. Burada her duzeltme KILITLENIR.

Kritik kural (KAHIN uyarisi): 12+ haneli telefon ASLA ilk 10 haneye
kirpilmaz. Kirpmak bastaki `0`'yi dusurur ve GECERSIZ bir numara
uretir. Uretmek, kirp BIRAKMAKTAN kotudur.

Ayrica iki yazim tuzagi testle korunur:
  1. "Sube" kelimesi Turkce KUCUK s ile baslar; buyuk S yazilirsa
     desen HIC eslesmez ve temizlik sessizce calismaz.
  2. `m.start() > 0` sarti yanlisti - ilk etiket metnin basinda
     oldugunda hicbir sey kesilmezdi.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
_MOD = KOK / "scripts" / "ostim_mukerrer_coz.py"

if not _MOD.is_file():
    pytest.skip(f"modul yok: {_MOD}", allow_module_level=True)

_spec = importlib.util.spec_from_file_location("ostim_mukerrer_coz", _MOD)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["ostim_mukerrer_coz"] = _mod
_spec.loader.exec_module(_mod)

telefonlari_temizle = _mod.telefonlari_temizle
adresi_temizle = _mod.adresi_temizle


# ---------------------------------------------------------------- TELEFON

class TestTelefonGecerlilik:
    """Gecerli numaralara DOKUNULMAZ (KAHIN yazim kurali)."""

    @pytest.mark.parametrize("ham", [
        "0312 385 40 00",
        "0312-385-40-00",
        "(0312) 385 40 00",
        "3123854000",
        "03123854000",
        "0532 123 45 67",
        "05321234567",
        "5321234567",
        "+90 312 385 40 00",
        "0090 532 123 45 67",
    ])
    def test_gecerli_numara_korunur(self, ham):
        sonuc = telefonlari_temizle([ham])
        assert sonuc, f"gecerli numara SILINDI: {ham}"
        for n in sonuc:
            rakam = n.replace(" ", "")
            assert 10 <= len(rakam) <= 11, f"gecersiz uzunluk: {ham} -> {n}"
            assert rakam.isdigit(), f"rakam disi kaldi: {ham} -> {n}"

    def test_sabit_hat_alan_kodu_sonrasi_bosluk(self):
        """KAHIN: '0312 den sonrasini bosluk birak - alan kodu, sonra 7 hane'."""
        sonuc = telefonlari_temizle(["03123854000"])
        assert sonuc == ["0312 3854000"], f"sabit bicim yanlis: {sonuc}"

    def test_cep_alan_kodusuz(self):
        """KAHIN: 'cep 05 ile baslar, alan kodu olmaz'."""
        sonuc = telefonlari_temizle(["05321234567"])
        assert sonuc == ["05321234567"], f"cep bicim yanlis: {sonuc}"
        assert " " not in sonuc[0], "cep numarasinda bolum olmamali"

    def test_bastaki_sifir_eklenir(self):
        """KAHIN: '0 yoksa ekle' - alan kodu 0312 / cep 0532 olur."""
        assert telefonlari_temizle(["3123854000"]) == ["0312 3854000"]
        assert telefonlari_temizle(["5321234567"]) == ["05321234567"]

    def test_ulke_kodu_silinir(self):
        """KAHIN: '9 varsa sil 9 - ulke kodu gerek yok'."""
        assert telefonlari_temizle(["903123854000"]) == ["0312 3854000"]
        assert telefonlari_temizle(["+903123854000"]) == ["0312 3854000"]
        assert telefonlari_temizle(["00905321234567"]) == ["05321234567"]
        for ham in ("903123854000", "+903123854000", "00905321234567"):
            for n in telefonlari_temizle([ham]):
                assert "90" not in n.replace(" ", "")[:2], \
                    f"ulke kodu kaldi: {ham} -> {n}"


class TestTelefonKirpmaYasagi:
    """KAHIN uyarisinin kaydi: kirpma gecersiz numara uretir."""

    def test_12_hane_kirpILMAZ_birakilir(self):
        """12 hane belirsizse ATILIR, ilk 10 haneye kirpILMAZ."""
        # Eski (hatali) davranis: '903123852424' -> '3123852424'
        # Bu bir numara DEGIL; bastaki 0 kaybolmus iki numaranin yarisi.
        ham = "903123852424"
        sonuc = telefonlari_temizle([ham])
        assert sonuc != ["3123852424"], (
            "12 haneli deger ilk 10 haneye kirpildi - bu gecersiz "
            "numara uretir (bastaki 0 duser)")
        if sonuc:
            assert sonuc[0].startswith("0"), (
                f"Turk numarasi 0 ile baslamali: {sonuc[0]}")

    def test_ayrilamayan_cok_uzun_birakilir(self):
        """13+ hanede agirlikla iki numara birlestmis; kirpma riskli."""
        for ham in ("123456789012", "111111111111111"):
            sonuc = telefonlari_temizle([ham])
            for n in sonuc:
                assert 10 <= len(n.replace(" ", "")) <= 11, (
                    f"{ham} -> {n}: uydurma/kirp numara uretildi")

    def test_ulke_kodu_ayiklandiktan_sonra_0_korunur(self):
        """90 + 10 hane ayriklanirken bastaki 0 geri konur."""
        sonuc = telefonlari_temizle(["903123854000"])
        assert sonuc, "ayrilabilir numara atilmis olmamali"
        assert sonuc[0].startswith("0"), f"bastaki 0 duser: {sonuc[0]}"
        assert not sonuc[0].startswith("90"), f"ulke kodu kaldi: {sonuc[0]}"

    def test_kirpma_yerine_dusurme_tercih_edilir(self):
        for ham in ("903123854000", "053212345678", "031238540001"):
            sonuc = telefonlari_temizle([ham])
            for n in sonuc:
                assert 10 <= len(n.replace(" ", "")) <= 11, f"{ham} -> {n}"


class TestTelefonGirdiCesitleri:
    @pytest.mark.parametrize("bos", [[], None, [""], ["  "], ["abc"]])
    def test_bos_ve_gecersiz_girdi_cekis_vermez(self, bos):
        assert telefonlari_temizle(bos) == []

    def test_tekrar_edenler_tekillestirilir(self):
        assert telefonlari_temizle(
            ["03123854000", "0312 385 40 00", "3123854000"]) == ["0312 3854000"]

    def test_coklu_numara_korunur(self):
        sonuc = telefonlari_temizle(["03123854000", "05321234567"])
        assert len(sonuc) == 2, f"numara kayboldu: {sonuc}"



# ----------------------------------------------------------------- ADRES

class TestAdresCokBlok:
    """Sayfa blogu sizmis adreslerden TEK gercek adres secilir."""

    def test_merkez_sube_ilk_blok_alinir(self):
        ham = ("Merkez: 100. Yil Bulvari 1230-1 Sokak No:4 Ostim - Ankara "
               "Sube: 100. Yil Bulv 1231-1 Sokak No:2P-5")
        sonuc = adresi_temizle(ham)
        assert sonuc is not None, "adres tamamen kayboldu"
        assert "1230" in sonuc, f"ilk blok alinmadi: {sonuc}"
        assert "1231" not in sonuc, f"sube blogu kirpilmadi: {sonuc}"

    def test_fabrika_lojistik_ilk_blok_alinir(self):
        ham = ("Fabrika: Ivedik OSB 1436 Sok. No:6 Ostim Ankara "
               "Lojistik adresi: Ostim Centre Uzay Cagi Cad. No: 112/16")
        sonuc = adresi_temizle(ham)
        assert sonuc is not None
        assert "1436" in sonuc, f"fabrika blogu alinmadi: {sonuc}"
        assert "112" not in sonuc, f"lojistik blogu kirpilmadi: {sonuc}"

    def test_ilk_etiket_bastayken_de_kesilir(self):
        """m.start() > 0 tuzagi: ilk etiket basinda olunca da kirpilmali."""
        ham = "Fabrika: 1000 Cadde No:5 Sube: 2000 Cadde No:7"
        sonuc = adresi_temizle(ham)
        assert sonuc == "1000 Cadde No:5", f"beklenmeyen: {sonuc}"

    def test_arka_arkaya_etiketler(self):
        """Iki etiket arka arkaya gelirse ikincisi de islenir."""
        ham = "Merkez: Fabrika: Ivedik OSB 1436 Sok No:6 Sube: 2. Cadde 15"
        sonuc = adresi_temizle(ham)
        assert sonuc is not None, "adres kaybolmamali"
        assert "1436" in sonuc, f"ilk gercek adres alinmadi: {sonuc}"
        assert "Cadde 15" not in sonuc, f"sube blogu kaldi: {sonuc}"

    @pytest.mark.parametrize("etiket", [
        "Merkez", "Sube", "Şube", "sube", "ŞÜBE",
        "Fabrika", "Tel", "Telefon", "Lojistik adresi",
    ])
    def test_etiket_varyantlari_eslesir(self, etiket):
        """Turkce kodu sorunu: her yazim eslesmeli (D-300 tuzagi 1)."""
        ham = f"{etiket}: 1000 Cadde No:5 Sube: 2000 Cadde No:7"
        sonuc = adresi_temizle(ham)
        assert sonuc is not None, f"etiket taninmadi: {etiket}"
        assert "2000" not in sonuc, f"{etiket} sonrasi kirpilmadi"

    def test_telefon_blogu_kirpilir(self):
        ham = "1000 Cadde No:5 Ostim Tel: 0312 385 40 00"
        sonuc = adresi_temizle(ham)
        assert sonuc is not None
        assert "0312" not in sonuc, f"telefon blogu kirpilmadi: {sonuc}"


class TestAdresNormalizasyon:
    @pytest.mark.parametrize("ham", [
        "AH EVRAN CAD. 63",
        "1229. CADDE (ESKI 43) 25 G",
        "1167. CADDE (ESKİ 212) 4 3",
        "OSTIM ANKARA 1234 CADDE 5",
    ])
    def test_gercek_adres_korunur(self, ham):
        sonuc = adresi_temizle(ham)
        assert sonuc == " ".join(ham.split()), f"degisti: {ham} -> {sonuc}"

    @pytest.mark.parametrize("bos", [None, "", "   ", "Merkez:", "Sube:"])
    def test_adres_deger_severiler_reddedilir(self, bos):
        """Rakam veya minimum uzunluk yoksa reddedilir."""
        assert adresi_temizle(bos) is None


# ------------------------------------------------- ASIL DIZI DOGRULAMASI

class TestDizinButunlugu:
    """Cikti dosyasi D-300 kurallarina uymali (canli, fixture degil)."""

    @pytest.fixture(scope="class")
    def temiz(self):
        yol = KOK / "data" / "ostim" / "OSTIM_TEMIZ.jsonl"
        if not yol.is_file():
            pytest.skip("OSTIM_TEMIZ.jsonl yok")
        import json
        return [json.loads(x) for x in
                yol.read_text(encoding="utf-8").splitlines() if x.strip()]

    def test_hicbir_telefon_10_11_hane(self, temiz):
        kotu = []
        for s in temiz:
            for t in s.get("telefonlar") or []:
                if not (10 <= len(str(t)) <= 11):
                    kotu.append(t)
        assert not kotu, f"{len(kotu)} gecersiz telefon: {kotu[:5]}"

    def test_hicbir_adres_etiket_tasiMiYor(self, temiz):
        kotu = [s.get("adres") for s in temiz
                if s.get("adres") and _mod._ADRES_BLOGU.search(s["adres"])]
        assert not kotu, f"{len(kotu)} kirli adres: {kotu[:3]}"

    def test_hicbir_adres_cok_uzun(self, temiz):
        kotu = [s.get("adres") for s in temiz
                if s.get("adres") and len(s["adres"]) > 120]
        assert not kotu, f"{len(kotu)} adres 120 karakterden uzun: {kotu[:3]}"


# ------------------------------------------------ KIRPMA YASAGI (KAHIN)

def test_kirpma_uretecegi_kadar_tercih_edilir():
    """KAHIN kurali: kirp BIRAKILIR, yanlis numara URETILMEZ."""
    for n in telefonlari_temizle(["123456789012"]):
        assert len(n) in (10, 11)
        assert n != "1234567890", "belirsiz deger kirpildi"


    def test_cok_uzun_adres_kesilir(self):
        uzun = "1200. CADDE NO:5 " + "OSTIM ANKARA YENIMAHALLE " * 6
        sonuc = adresi_temizle(uzun)
        if sonuc:
            assert len(sonuc) <= 120, f"cok uzun kaldi: {len(sonuc)}"

    def test_coklu_bosluk_tekillestirilir(self):
        assert adresi_temizle("AH   EVRAN  CAD.  63") == "AH EVRAN CAD. 63"
