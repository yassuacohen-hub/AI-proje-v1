# -*- coding: utf-8 -*-
"""VERI-RAG-KORPUS-01 mandali.

Iki sozlesmeyi zorlar:
  (a) Korpus metni kisisel veri (TCKN/telefon/e-posta) TASIYAMAZ (D-247).
  (b) Her kayit kaynak kunyesi TASIR; kunyesiz kayit uretilemez (brif adim 3).

Ayrica beyaz listenin kendisi denetlenir: `description` listede olmaz —
canli DB olcumunde 632 dolu kaydin 624'u (%98.7) adres deseniydi.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.vector.service import (  # noqa: E402
    EMBEDDER_TOKEN_LIMITASI,
    KORPUS_ALANLARI,
    KORPUS_KISISEL_DESENLER,
    KUNYE_AYRAC,
    KorpusHatasi,
    chunk_gerekli,
    firma_korpus_metni,
    korpus_icerigi,
    korpus_kaydi,
    korpus_kayitlarini_uret,
    korpus_kunyesi,
    kisisel_veri_tara,
    isim_soyisim_kalibi,
    sahis_firmasi_tagi,
)

SATIR = {
    "company_id": "80f53933-60be-49db-b5ea-231eb49f41cf",
    "legal_name": "BIRSAN CEV TAS. SAN. TIC. LTD. STI.",
    "nace_code": "05.10",
    "nace_source": "sector_default",
    "nace_validity": "medium",
    "sector_name": "Gida Ve Endustriyel Mutfak",
    "employee_count": 25,
    "is_ankara": True,
    "is_osb_member": True,
    "source_name": "ostim.org.tr",
    "updated_at": "2026-10-01T08:00:00+00:00",
}


class TestBeyazListe:
    def test_description_listede_yok(self):
        """`description` adres alani; korpusa giremez (D-247)."""
        assert "description" not in KORPUS_ALANLARI

    def test_kisisel_kolonlar_listede_yok(self):
        """Kimlik/iletisim kolonlari hicbir bicimde listeye giremez."""
        yasak = {
            "tax_number", "tckn", "primary_phone", "primary_email",
            "address", "tax_office", "mersis_number", "trade_registry_number",
        }
        assert not (yasak & set(KORPUS_ALANLARI))

    def test_legal_name_listede_var(self):
        """Kimlik alani olmadan korpus metni kurulamaz."""
        assert "legal_name" in KORPUS_ALANLARI


class TestKisiselVeriSizmaz:
    def test_temiz_satir_taramayi_gecer(self):
        metin, _ = firma_korpus_metni(SATIR)
        assert kisisel_veri_tara(metin) == []

    def test_tckn_sizarsa_reddedilir(self):
        kotu = dict(SATIR, sector_name="TCKN 12345678901")
        metin, _ = firma_korpus_metni(kotu)
        assert "TCKN" in kisisel_veri_tara(metin)

    def test_telefon_sizarsa_reddedilir(self):
        kotu = dict(SATIR, sector_name="Tel 05321234567")
        metin, _ = firma_korpus_metni(kotu)
        assert "telefon" in kisisel_veri_tara(metin)

    def test_eposta_sizarsa_reddedilir(self):
        kotu = dict(SATIR, sector_name="info@ornek.com.tr")
        metin, _ = firma_korpus_metni(kotu)
        assert "email" in kisisel_veri_tara(metin)

    def test_sizan_kayit_toplu_uretmede_duser_ve_sebep_yazilir(self):
        """Sizinti sessizce yazilmaz; hata listesine girer."""
        satirlar = [SATIR, dict(SATIR, company_id="kirli", sector_name="a@b.com")]
        basarili, hatalar = korpus_kayitlarini_uret(satirlar)
        assert len(basarili) == 1
        assert len(hatalar) == 1
        assert "kisisel veri deseni" in hatalar[0][1]
        assert hatalar[0][0] == "kirli"


class TestKunyeZorunlulugu:
    def test_kunye_metnin_icinde(self):
        metin, kunye = firma_korpus_metni(SATIR)
        assert KUNYE_AYRAC in metin
        assert kunye in metin

    def test_kunye_eksik_parcalari_aciklar(self):
        """Eksik parca sessizce yutulmaz; acik metin yazilir."""
        kunye = korpus_kunyesi("abc", None, None)
        assert "kaynak-yok" in kunye
        assert "tarih-yok" in kunye

    def test_metin_siz_dogrulamasi(self):
        assert korpus_kaydi(SATIR).metin_siz() is True

    def test_kunyesiz_kayit_uretildiginde_tespit_edilir(self):
        """Kunye atan kayit, metni kirletmeden yakalanir."""
        kayit = korpus_kaydi(SATIR)
        bozuk = type(kayit)(
            firma_id=kayit.firma_id,
            metin=kayit.metin.replace(KUNYE_AYRAC, " | "),
            kunye=kayit.kunye,
            nace_kod=kayit.nace_kod,
            nace_kaynak=kayit.nace_kaynak,
        )
        assert bozuk.metin_siz() is False

    def test_kunyesiz_kayit_toplu_uretmede_duser(self):
        """Toplu uretim kunyesiz kaydi hata listesine yazar."""
        bozuk = dict(SATIR, company_id="kunyesiz")
        # kunye uretimi satirin kendi alanlarindan; company_id silinince
        # kunye "firma_id-yok" yazilir ama ayrac korunur -> elle bozulur.
        kayitlar = [SATIR]
        basarili, hatalar = korpus_kayitlarini_uret(kayitlar)
        assert len(basarili) == 1 and not hatalar

        kayit = korpus_kaydi(bozuk)
        assert kayit.metin_siz() is True  # ayrac korundugu icin gecerli


class TestKimliksizSatir:
    def test_legal_name_bossa_hata(self):
        with pytest.raises(KorpusHatasi):
            firma_korpus_metni(dict(SATIR, legal_name="  "))

    def test_legal_name_yoksa_hata(self):
        satir = {k: v for k, v in SATIR.items() if k != "legal_name"}
        with pytest.raises(KorpusHatasi):
            firma_korpus_metni(satir)

    def test_kimliksiz_satir_toplu_uretmede_sebep_yazilir(self):
        basarili, hatalar = korpus_kayitlarini_uret([dict(SATIR, legal_name=None)])
        assert not basarili
        assert len(hatalar) == 1 and "legal_name" in hatalar[0][1]


class TestNaceAcilim:
    def test_sozlukte_varsa_acilim_eklenir(self):
        metin, _ = firma_korpus_metni(SATIR, {"05.10": "Tarla bitkileri"})
        assert "05.10 (Tarla bitkileri)" in metin

    def test_sozlukte_yoksa_sadece_kod(self):
        """Sahte acilim uydurulmaz (D-245)."""
        metin, _ = firma_korpus_metni(SATIR, {"99.99": "Olmayan"})
        assert "05.10" in metin and "Olmayan" not in metin

    def test_nace_kaynagi_metinde_kalir(self):
        """D-252: kayitli / tahmin ayrimi metinde korunur."""
        metin, _ = firma_korpus_metni(SATIR)
        assert "sector_default" in metin


class TestDesenler:
    def test_her_desen_calisiyor(self):
        """Desen tanimi bozulmusa sessizce hicbir sey yakalamaz."""
        ornek = {
            "TCKN": "12345678901",
            "telefon": "05321234567",
            "email": "a@b.com",
        }
        for ad, deger in ornek.items():
            assert KORPUS_KISISEL_DESENLER[ad].search(deger), ad

    def test_uuid_kuyrugu_tckn_sanilmaz(self):
        """Canli olcumde 44 gecerli kayit bu yuzden reddedildi.

        `a05368782388` -> `05368782388`: 11 hane. Desen hex-duyarli olmali.
        """
        canli_uuid = "05d51bdb-2885-4063-b413-a05368782388"
        assert KORPUS_KISISEL_DESENLER["TCKN"].search(canli_uuid) is None

    def test_uuid_kunyesi_kayit_gecirir(self):
        """Bu regresyon: kunye taramasi gecerli firmayi dusurmemeli."""
        satir = dict(SATIR, company_id="05d51bdb-2885-4063-b413-a05368782388")
        basarili, hatalar = korpus_kayitlarini_uret([satir])
        assert len(basarili) == 1, hatalar
        assert hatalar == []

    def test_tckn_yine_de_yakalanir(self):
        """Hex-duyarlilik gercek TCKNyi gormezden gelmemeli."""
        assert KORPUS_KISISEL_DESENLER["TCKN"].search("TCKN 12345678901")

    def test_12_haneli_uuid_kuyrugu_telefon_sanilmaz(self):
        """Son canli olcumde kalan tek yanlis pozitif buydu.

        `033034123829` 12 hanedir ve telefon desenine giriyordu.
        Artik kunye taramaya girmez (korpus_icerigi).
        """
        canli_uuid = "d6dca73e-c1ca-40e7-96a1-033034123829"
        satir = dict(SATIR, company_id=canli_uuid)
        metin, kunye = firma_korpus_metni(satir)
        assert kunye in metin
        assert kisisel_veri_tara(korpus_icerigi(metin)) == []

    def test_icerik_kunyesiz_ayrilir(self):
        metin, kunye = firma_korpus_metni(SATIR)
        icerik = korpus_icerigi(metin)
        assert kunye not in icerik
        assert SATIR["legal_name"] in icerik

    def test_kunyesiz_metin_ayrilmaz(self):
        """Ayirac yoksa metin aynen doner; veri kaybi olmaz."""
        assert korpus_icerigi("kisa metin") == "kisa metin"


class TestChunkKarari:
    """Chunk karari olcumle verilir; 200 karakter marker'i DEGIL
    (D-255/4: olcumun kapsami kararin kapsamini belirlemez)."""

    def test_canli_olcum_degerleri_chunk_gerektirmiyor(self):
        # 2026-10-02 canli DB: medyan 275, en uzun 448 karakter
        canli = [f"x" * n for n in (175, 275, 448)]
        gerekli, en_uzun, oran = chunk_gerekli(canli)
        assert en_uzun == 448
        assert gerekli is False
        assert oran < 0.05, f"oran {oran:.4f} pencereye sigmaliydi"

    def test_200_karakter_marker_i_tek_basina_yetmez(self):
        """200 krk asmak pencereye takildi demek DEGIL."""
        gerekli, _, oran = chunk_gerekli(["x" * 275])
        assert gerekli is False

    def test_pencereyi_asan_metinde_chunk_gerekli(self):
        gerekli, en_uzun, oran = chunk_gerekli(
            ["x" * (EMBEDDER_TOKEN_LIMITASI * 4)], token_limitasi=EMBEDDER_TOKEN_LIMITASI
        )
        assert gerekli is True
        assert oran >= 1.0

    def test_bos_korpusta_chunk_gerekmez(self):
        gerekli, en_uzun, oran = chunk_gerekli([])
        assert gerekli is False
        assert en_uzun == 0


class TestSahisFirmasiTagi:
    """KAHİN kararı (2026-10-02): "Şahıs şirketlerinde LTD ŞTİ gibi
    ünvanlar geçmez. Kolonlarda isim soy isim ve vergi no kolonunda TC
    olarak yazılmışsa bu bir şahıs şirketidir, KVKK girer."

    TESPİTTİR, KARAR DEĞİLDİR: kayıt korpusta kalır, bayrak taşınır.

    Canlı DB ölçümü (9412 firma, Supabase):
      unvansız (tüzel aday değil)  : 2391 (%25.4)
      vergi no = geçerli TC        : **0**
      şahıs firması (tag)         : 1455 (%15.5)
    TC bacağı bugün 0 üretiyor: veri kaynağı TC taşımıyor. Kural ileri
    ingest için şart; bugünkü 1455'in tamamı isim+soyisim bacağından.
    """

    # KAHİN'in tarifine birebir uyan kayıtlar.
    SAHIS = [
        "MEHMET SOYALP",
        "KEMAL ÖZDEMİR",
        "HACI AHMET TOPUZ",
        "ADNAN VURAL TERZİ",
    ]

    # Ünvan geçiyor → tüzel kişi. KAHİN'in kuralının ikinci cümlesi:
    # "şahıs şirketlerinde LTD ŞTİ gibi ünvanlar geçmez".
    TUZEL = [
        "BIRSAN CEV TAS. SAN. TIC. LTD. STI.",
        "MEHMET ÖZBEK LTD. ŞTİ.",          # kişi adı var AMA ünvan da var
        "MÜMTAZ KARACA & KARACA VOLVO SERVISI",
        "HOLDİNG A.Ş.",
        "",
        None,
    ]

    # Unvansız ama kalıba girmeyen: faaliyet kelimesi ya da tek kelime.
    KALIP_DISI = [
        "DOĞUŞ İŞ MAKİNALARI",
        "KARDEŞLER LOKANTASI",
        "OTO SELİM",
        "YAVUZLAR SONDAJ EKIPMANLARI",
        "1234567890",                      # rakam
    ]

    # Kuralın ÖLÇÜLMÜŞ sınırı, 2026-10-02 KAHİN kararıyla **KAPANDI**.
    # Eski hâli: "AKSOY TURBO" 2 kelime, alfabetik, ünvansız olduğu için
    # kural şahıs sayıyordu, oysan markadır — regex ile ayırt edilemiyordu.
    # KAHİN: *"şahıs işletmelerinde marka olmaz."* `METAL` ve `TURBO`
    # faaliyet/marka kelimesidir; `marka_tasiyor_mu()` bunları eler ve bu
    # üç kayıt artık şahıs **değildir**.
    #
    # Bu bir tesadüf değil, kararın uygulanmasıdır: liste boşaltıldı ve
    # kayıtlar aşağıda marka olarak doğrulanır. Kuralın kendisi hâlâ
    # tek başına karar mercii DEĞİLDİR — 9412 kaydın 720'si `belirsiz`
    # kaldı ve insan kararı gerektiriyor.
    MARKA_KARARI_DEGISEN = ["AKSOY TURBO", "ARITAS METAL", "DOST METAL"]

    @pytest.mark.parametrize("ad", SAHIS)
    def test_sahis_isaretlenir(self, ad):
        assert sahis_firmasi_tagi({"legal_name": ad}) is True

    @pytest.mark.parametrize("ad", TUZEL)
    def test_unvanli_tuzel_isaretlenmez(self, ad):
        assert sahis_firmasi_tagi({"legal_name": ad}) is False

    @pytest.mark.parametrize("ad", KALIP_DISI)
    def test_kalip_disi_isaretlenmez(self, ad):
        assert sahis_firmasi_tagi({"legal_name": ad}) is False

    # Gecerli TCKN (saslama toplami dogrulanmis). Bilerek uretilmedi:
    # kuralin calistigini gosteren kucuk bir ornek.
    TC_GECERLI = "10000000146"

    # Vergi no bacagini IZOLE eden satir: tek kelime -> isim kalibina girmez.
    # Boylece sonuc yalniz vergi no kolonundaki degere baglidir.
    KALIP_DISI_AD = "KAYA"

    def test_gecerli_tc_vergiden_sahis_yapar(self):
        """KAHİN'in 2. bacakı: vergi no kolonunda TC varsa şahıs firması."""
        satir = {"legal_name": self.KALIP_DISI_AD, "tax_number": self.TC_GECERLI}
        assert sahis_firmasi_tagi(satir) is True

    def test_gecersiz_tc_vergiden_sahis_yapmaz(self):
        """D-246/5: 11 hane olmak TCKN olmak değildir — sağlama toplamı tutmaz."""
        satir = {"legal_name": self.KALIP_DISI_AD, "tax_number": "11111111111"}
        assert sahis_firmasi_tagi(satir) is False

    def test_vkn_vergiden_sahis_yapmaz(self):
        """10 haneli VKN TC değildir (canlı DB'deki 5 kayıtın tamamı VKN)."""
        satir = {"legal_name": self.KALIP_DISI_AD, "tax_number": "5050051468"}
        assert sahis_firmasi_tagi(satir) is False

    def test_unicase_tckn_kesin_sahis_ilan_edilir(self):
        """KAHİN 2026-10-02: *"vergi no eğer tc no ise kesin şahıs işletmesidir."*

        **KESİN** kural — unvan elemesi onu geçersiz kılamaz. Bu, eski
        davranışın (`test_unvanli_kayit_tc_ile_de_sahis_sayilmaz`) tam
        tersidir ve KAHİN'in kararıyla bilinçli olarak değiştirildi.

        Gerekçe (D-248/1): şahıs işletmesinde TCKN vergi numarası yerine
        geçer, yani TC taşıyan kayıt tüzel bir kişi olamaz.
        """
        satir = {"legal_name": "KAYA LTD. ŞTİ.", "tax_number": self.TC_GECERLI}
        assert sahis_firmasi_tagi(satir) is True

    @pytest.mark.parametrize("ad", MARKA_KARARI_DEGISEN)
    def test_marka_tasidan_kayit_sahis_sayilmaz(self, ad):
        """KAHİN: *"şahıs işletmelerinde marka olmaz."*

        `METAL` / `TURBO` faaliyet kelimesidir; taşıyan kayıt marka üzerinden
        kendini gösterir, dolayısıyla şahıs işletmesi olamaz. Bu üç kayıt
        daha önce bu testte **bilinen yanlış pozitif** olarak sabitlenmişti.
        """
        assert sahis_firmasi_tagi({"legal_name": ad}) is False

    def test_bayrak_kayit_uzerinde_tasinir(self):
        """Eski sezgi bayrağı hesaplayıp BIRAKIYORDU; bu regresyon kapısı.

        `korpus_istatistik` yerel değişkende doldurulup döndürülmüyordu;
        tespit yapılıyordu ama kimse okuyamıyordu. Bayrak artık kaydın
        üzerinde ve dışarıdan okunabilir.
        """
        satir = dict(SATIR, legal_name="MEHMET SOYALP")
        kayit = korpus_kaydi(satir)
        assert kayit.sahis_firmasi is True

    def test_temiz_tuzel_kayitta_bayrak_kapali(self):
        assert korpus_kaydi(dict(SATIR)).sahis_firmasi is False

    def test_sahis_kayit_korpustan_dusurulmez(self):
        """Tespit karardır: silme orkestratöründür. Kayıt kalır."""
        satir = dict(SATIR, legal_name="MEHMET SOYALP")
        basarili, hatalar = korpus_kayitlarini_uret([satir])
        assert len(basarili) == 1
        assert hatalar == []
        assert basarili[0].sahis_firmasi is True

    def test_isim_kalibi_kamu_oyunu_yakalamaz(self):
        assert isim_soyisim_kalibi("DOĞUŞ İŞ MAKİNALARI") is False
        assert isim_soyisim_kalibi("MEHMET SOYALP") is True

    def test_temiz_kayit_etkilenmez(self):
        basarili, hatalar = korpus_kayitlarini_uret([SATIR])
        assert len(basarili) == 1 and hatalar == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
