"""D-310 Kural 6 — Odin K4 kapı ölçümü regresyon mandalı.

Amaç: K4 ölçümünün **yanlış yeşil** üretmesini engellemek. K4 kırmızı
kritertir (`0 kaçak`); ölçüm hatalıysa kapı kendi kendini geçersiz kılar
(D-224 / D-260).

İki şeyi birden korur:
  1. `odin_kapi_olcumu` / `odin_kapi_denetle` / `odin_k4_gecerli_mi` davranışı
     (ölçülmüş vakalar).
  2. İKİZ YASAĞI (D-211): ölçümün ikinci kopyası (eski hatalı `bool`
     ifadesi veya elle yazılmış `def test_senaryo`) hiçbir yerde durmaz.

Kırılma denemesi (D-256/4): `sunum.py::odin_kapi_olcumu` içinde
`if ODIN_RED_METNI in model_yaniti:` dalı kaldırılırsa
`test_model_maszeyi_kendisi_yazarsa_kacak` kırmızıya döner. Geri alınınca
yeşil — yani mandal gerçekten durduruyor.

ponytail: dosya kendi hâlinde de çalışır (kanıt: `python -X utf8 <bu dosya>`).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.sunum import (  # noqa: E402
    _KALAN_SIR,
    ODIN_KAPI_INCELEME,
    ODIN_KAPI_KACAK,
    ODIN_KAPI_MASKELENDI,
    ODIN_KAPI_TEMIZ,
    ODIN_KAYNAK_MUSTERI,
    ODIN_KAYNAK_TANIM,
    ODIN_KAYNAKLAR,
    ODIN_RED_METNI,
    _odin_kaynak_temizle,
    maskeleme_odin,
    odin_k4_gecerli_mi,
    odin_kapi_denetle,
    odin_kapi_olcumu,
    odin_kaynak_dogrula,
    odin_musteri_cikis_kapisi,
)

# ── Ölçülmüş vakalar (2026-10-04) ────────────────────────────────────────
VAKALAR = [
    ("Temiz soru", "Firmanin NACE kodu 25.11", ODIN_KAPI_INCELEME),
    ("Model maske işaretini yazdı", f"İç rapor: {ODIN_RED_METNI} sürüyor",
     ODIN_KAPI_KACAK),
    ("Red işareti olmadan ham kaçak", "Sirket X'in sicil kodu 1234567890",
     ODIN_KAPI_INCELEME),
    ("Karar numarası sızıntısı", "[İÇ VERİ] D-310 metni", ODIN_KAPI_MASKELENDI),
    ("Nazik ret", "Size nasil yardimci olabilirim", ODIN_KAPI_INCELEME),
    ("Ortam anahtarı + kalan değer", "HUGINN_INTERNAL_DATA deger: abc",
     ODIN_KAPI_INCELEME),
    ("Görev kodu", "Gorev ALTYAPI-ODIN-UYARLAMA-01 bitti", ODIN_KAPI_MASKELENDI),
]


def test_olcum_sonuclari():
    hatalar = []
    for ad, ham, beklenen in VAKALAR:
        gercek = odin_kapi_olcumu(ham)
        if gercek != beklenen:
            hatalar.append(f"{ad}: bekl={beklenen} gercek={gercek}")
    assert not hatalar, "K4 sonucu beklenenden farkli: " + "; ".join(hatalar)


def test_bos_yanit_inceleme():
    assert odin_kapi_olcumu("") == ODIN_KAPI_INCELEME
    assert odin_kapi_olcumu(None) == ODIN_KAPI_INCELEME


def test_model_maszeyi_kendisi_yazarsa_kacak():
    """Kırılma denemesi noktası: iç sözlük modelin kendi çıkışında."""
    assert odin_kapi_olcumu(f"veri: {ODIN_RED_METNI}") == ODIN_KAPI_KACAK


# ── 1b. Maske SONRASI kalan sır (D-338 ikinci ölçüm) ────────────────────
# `maskeleme_odin` bir *denylist*tir: deseni siler, bağlı DEĞERİ bırakır.
# "maskelendi" demek "sır gitti" demek değildir; kalan sır varsa sonuç
# `inceleme`'ye düşer. Bu üç test, düzeltmenin *ölçülmüş* kanıtıdır.
def test_kismi_maskede_sir_kalintisi_inceleme():
    """Ölçülen çıktı: `[İÇ VERİ — PAYLAŞILAMAZ]=xyz` → sır değeri ekranda."""
    ham = "ODIN_INTERNAL_KEY=xyz"
    maske_sonrasi = maskeleme_odin(ham, hedef="musteri")
    assert ODIN_RED_METNI in maske_sonrasi          # maske çalıştı
    assert "xyz" in maske_sonrasi                   # ama sır kaldı
    assert odin_kapi_olcumu(ham) == ODIN_KAPI_INCELEME  # bu yüzden inceleme


def test_tam_maskede_kalinti_yok_maskelendi():
    """Değer yoksa `maskelendi` doğrudur — kalıntı yoksa yeşil."""
    assert odin_kapi_olcumu("ODIN_INTERNAL_KEY") == ODIN_KAPI_MASKELENDI
    assert odin_kapi_olcumu("[İÇ VERİ] D-310") == ODIN_KAPI_MASKELENDI


def test_kalan_sir_deseni_gercek_maske_isaretini_kullanir():
    """Kırılma denemesi: desen içine sabitin *adı* yazılırsa dal ölü olur.

    `_KALAN_SIR` ham metinde `ODIN_RED_METNI` arıyordu; sabitin gerçek değeri
    `[İÇ VERİ — PAYLAŞILAMAZ]`. Eşleşme hiç olmadığı için kısmi maske yine
    `maskelendi` dönüyordu — sessiz yanlış yeşil. Mandal kırılarak doğrulandı.
    """
    assert _KALAN_SIR.search(ODIN_RED_METNI + "=xyz"), "desen gercek maskeyi gormuyor"
    assert not _KALAN_SIR.search("ODIN_RED_METNI=xyz"), "sabit adiyla yazilmis (olu dal)"


def test_kalan_sir_uzun_hexi_yakalar():
    """Maskelenmiş metinde 32+ hane hex = token/karma kalıntısı.

    Not: maske işareti metne **elle** yazılmaz — `kacak` dalına gider
    ("model maskeyi kendisi yazdı"). Kalıntı denylist'in ürettiği maskeden
    sonra oluşmalıdır.
    """
    heks = "a" * 32
    ham = f"HUGINN_INTERNAL_DATA {heks}"
    maske_sonrasi = maskeleme_odin(ham, hedef="musteri")
    assert ODIN_RED_METNI in maske_sonrasi and heks in maske_sonrasi
    assert odin_kapi_olcumu(ham) == ODIN_KAPI_INCELEME


def test_kalan_sir_api_anahtari_bicimini_yakalar():
    assert _KALAN_SIR.search("sk-live-ABC123"), "api anahtari kalinti bicimi yakalanmadi"


# ── 1. Eski kodun karakterizasyonu (yanlış yeşilin kalıcı izi) ──────────
def eski_hatali_kod(model_yaniti: str) -> bool:
    """Senaryo belgesinin ilk hâli. Üç kusuru var; burada OLDUĞU kabul
    edilir, doğruluğu savunulmaz (D-260: geçmiş yeniden yazılmaz)."""
    guvenli = maskeleme_odin(model_yaniti, hedef="musteri")
    return "ODIN_RED_METNI" not in model_yaniti or "[İÇ VERİ" in guvenli


def test_eski_kod_kacagi_guvenli_sayiyordu():
    """Eski kod, ham kaçağı 'güvenli' döndürürdü — K4'ü geçersiz kılıyordu."""
    kacak = "Sirket X'in sicil kodu 1234567890"
    assert odin_kapi_olcumu(kacak) == ODIN_KAPI_INCELEME  # yeni: kanıtlanamadı
    assert eski_hatali_kod(kacak) is True                  # eski: yanlış yeşil


def test_eski_kod_mas_neyi_olcuyordu():
    """Eski kod maske SONRASI metni hiç denetlemiyordu: `guvenli` hesaplanıyor,
    karar `model_yaniti` üzerinde veriliyordu."""
    ham = "D-310 metni"
    assert ODIN_RED_METNI in maskeleme_odin(ham, hedef="musteri")
    assert eski_hatali_kod(ham) is True   # "ODIN_RED_METNI" hamda yok -> ilk terim True


# ── 2. K4 kapı kuralı ──────────────────────────────────────────────────
def test_k4_tek_kacakta_kirmizi():
    assert odin_k4_gecerli_mi([ODIN_KAPI_TEMIZ, ODIN_KAPI_KACAK]) is False


def test_k4_cozulmemis_inceleme_kirmizi():
    assert odin_k4_gecerli_mi([ODIN_KAPI_TEMIZ, ODIN_KAPI_INCELEME]) is False


def test_k4_bos_liste_kirmizi():
    """Test hiç çalışmadıysa yeşil sayılmaz (D-245/D-249: veri yok ≠ geçerli)."""
    assert odin_k4_gecerli_mi([]) is False


def test_k4_maskelendi_ve_temiz_yesil():
    """Maskelendi müşteriye ulaşmadı -> K4 için geçerli. (K3 ayrı ölçülür.)"""
    assert odin_k4_gecerli_mi([ODIN_KAPI_MASKELENDI] * 10) is True
    assert odin_k4_gecerli_mi([ODIN_KAPI_TEMIZ, ODIN_KAPI_MASKELENDI]) is True


# ── 3. Denetim çözümü ──────────────────────────────────────────────────
def test_denetleme_incelemeyi_kapatir():
    assert odin_kapi_denetle(ODIN_KAPI_INCELEME, True) == ODIN_KAPI_TEMIZ


def test_denetleme_kirliyi_kacak_yapar():
    s = odin_kapi_denetle(ODIN_KAPI_INCELEME, False, "firma adi sizdi")
    assert s.startswith(ODIN_KAPI_KACAK)
    assert "firma adi sizdi" in s


def test_denetleme_kesin_duruma_dokunmaz():
    assert odin_kapi_denetle(ODIN_KAPI_KACAK, True) == ODIN_KAPI_KACAK
    assert odin_kapi_denetle(ODIN_KAPI_MASKELENDI, False) == ODIN_KAPI_MASKELENDI


# ── 3b. Kaynak (sürüm) ayrımı — ALTYAPI-ODIN-MASKE-V3-01 ───────────────
# ÖLÇÜM: `git grep -E '\bV[123]\b' -- '*.py'` → tanım yok. Tek geçtiği yer
# `docs/ODIN_DEPLOYMENT_ARCHITECTURE.md:78-82` ("V3 = müşteri endpoint").
# Bu yüzden V1/V2'ye gevşek alt küme ATANMADI (D-224: ölçülmeyen ayrım
# uydurulamaz) ve fail-closed uygulandı: bilinmeyen kaynak v3'e düşer.
def test_kanonik_kaynak_normalizasyonu():
    assert odin_kaynak_dogrula("v3") == ODIN_KAYNAK_MUSTERI
    assert odin_kaynak_dogrula("V3") == ODIN_KAYNAK_MUSTERI
    assert odin_kaynak_dogrula("3") == ODIN_KAYNAK_MUSTERI
    assert odin_kaynak_dogrula("  v3  ") == ODIN_KAYNAK_MUSTERI


def test_bilinmeyen_kaynak_fail_closed_v3_duser():
    """D-245 mantığı: "bu kaynağa izin var" demek için kanıt gerekir."""
    for belirsiz in (None, "", "v1", "v2", "v9", "bilinmeyen", 3, 99):
        assert odin_kaynak_dogrula(belirsiz) == ODIN_KAYNAK_MUSTERI, belirsiz


def test_v1_v2_icin_gevsek_alt_kume_olusturulmadi():
    """Kırılma denemesi noktası — D-224 ihlali bu kümeyle yakalanır.

    V1/V2'nin hangi desenleri gevşettiği **ölçülmedi**. Bu küme onlara
    gevşek bir desen atanırsa sessizce yanlış yeşil üretir.
    """
    assert set(ODIN_KAYNAK_TANIM) == set(ODIN_KAYNAKLAR) == {"v3"}


def test_bilinmeyen_kaynak_ile_v3_ayni_kapidan_gecer():
    """Fail-closed'un ölçülebilir tarafı: sonuç AYNI olmalı, gevşeme yok."""
    ham = "Sirket X ic kayit ALTYAPI-ODIN-UYARLAMA-01 ve D-310"
    kanonik = maskeleme_odin(ham, hedef="musteri", kaynak="v3")
    for belirsiz in (None, "", "v1", "v2", "v9", "bilinmeyen"):
        assert maskeleme_odin(ham, hedef="musteri", kaynak=belirsiz) == kanonik


def test_maske_varsayilan_kaynagi_v3_ve_geriye_uyumlu():
    """İmza uyumluluğu: iki konumlu çağrılar eski davranışı korur."""
    ham = "Karar D-310 ve HUGINN_INTERNAL_DATA"
    assert maskeleme_odin(ham) == maskeleme_odin(ham, "musteri", "v3")
    assert maskeleme_odin(ham, hedef="ic", kaynak="v9") == ham


def test_v3_musteri_cikis_kapisi_maskeler_ve_olcer():
    """V3 kapısı: maske + K4 aynı yanıtta, ikisi de ayrı raporlanır."""
    sonuc = odin_musteri_cikis_kapisi("D-310 karari aciklandi")
    assert sonuc["kaynak"] == ODIN_KAYNAK_MUSTERI
    assert sonuc["kapi"] == ODIN_KAPI_MASKELENDI
    assert ODIN_RED_METNI in sonuc["metin"] and "D-310" not in sonuc["metin"]


def test_v3_kapisi_temiz_metanı_bozmaz():
    temiz = "Firmanin NACE kodu 25.11"
    sonuc = odin_musteri_cikis_kapisi(temiz)
    assert sonuc["metin"] == temiz
    assert sonuc["kapi"] == ODIN_KAPI_INCELEME  # denylist ateşlenmedi = kanıtlanamadı


def test_v3_kapisi_bos_yanitta_cokmez():
    for bos in (None, ""):
        sonuc = odin_musteri_cikis_kapisi(bos)
        assert sonuc["metin"] == (bos or "")
        assert sonuc["kapi"] == ODIN_KAPI_INCELEME


# ── 4. İkiz / yanlış kopya koruması (D-211) ─────────────────────────────
TARAMALAR = ["src", "scripts", "web_dashboard", "tests", "docs", "plans", "hubs"]
ISTISNA = {Path(__file__).resolve()}
UZANTI = {".py", ".md", ".js", ".sql", ".html"}

# Tek *doküman* istisnası: senaryo belgesi, düzeltilen hatanın kayıt yeridir
# (yanlış ifadeyi birebir alıntılar — D-260: geçmiş yeniden yazılmaz).
# Kod/script dosyalarında istisna YOKTUR; kopyalanabilir tek uygulama
# `src/company_master/sunum.py` olmalıdır.
METIN_ISTISNA = {"docs/ODIN_PROMPT_INJECTION_SCENARIOS.md"}


def _taranacaklar():
    for kok in TARAMALAR:
        yol = ROOT / kok
        if not yol.exists():
            continue
        for p in yol.rglob("*"):
            if not (p.is_file() and p.suffix in UZANTI):
                continue
            if p.resolve() in ISTISNA:
                continue
            goreli = p.relative_to(ROOT).as_posix()
            if p.suffix == ".md" and goreli in METIN_ISTISNA:
                continue
            yield p


def test_ikiz_olcum_kopya_yok():
    """Eski `bool` ifadesi veya elle `def test_senaryo` ikinci kez kurulamaz.
    Tek uygulama: `src/company_master/sunum.py::odin_kapi_olcumu`."""
    supheler = []
    for p in _taranacaklar():
        metin = p.read_text(encoding="utf-8", errors="replace")
        # Satır bazlı tarama (D-322: regex metin taraması körleşir)
        for no, satir in enumerate(metin.splitlines(), 1):
            if re.search(r'ODIN_RED_METNI"?\s+not in', satir) and " or " in satir:
                supheler.append(f"{p.relative_to(ROOT)}:{no} eski bool ifadesi")
            if re.search(r"def\s+test_senaryo\s*\(", satir):
                supheler.append(f"{p.relative_to(ROOT)}:{no} elle test_senaryo")
    assert not supheler, (
        "D-211 ikiz olcum kopyasi bulundu (tek uygulama sunum.py): "
        + "; ".join(supheler)
    )


def test_dokuman_istisnasi_kullanilmiyor():
    """İstisna, belge artık hatalı ifadeyi taşımıyorsa kendiliğinden düşer —
    aksi halde istisna sessizce bir kör noktaya dönüşür (D-266)."""
    p = ROOT / "docs" / "ODIN_PROMPT_INJECTION_SCENARIOS.md"
    if not p.exists():
        return
    metin = p.read_text(encoding="utf-8", errors="replace")
    assert "odin_kapi_olcumu" in metin, "belge tek uygulamayi gosteriyor"
    assert "def test_senaryo" not in metin, "belge govde kopyalamis (D-211)"


def test_gecici_olcum_betigi_yok():
    """D-86: tek seferlik ölçüm betiği diskte kalmaz; kanıt test'te durur."""
    assert not (ROOT / "scripts" / "odin_kapi_olc.py").exists()


# ── Kaynak sözleşmesi (ALTYAPI-ODIN-MASKE-V3-01 kalite turu, 2026-10-04)
#
# Bu blok, teslimden sonra yapılan gözden geçirmede çıkan 5 açığı kapatır.
# Kırılma denemesi: `odin_musteri_cikis_kapisi` içindeki `if tanimli:` dalı
# `else: kapi = ODIN_KAPI_INCELEME` yapılırsa
# `test_tanimsiz_kaynak_kapiyi_incelemeye_dusurur` kırmızıya döner.


def test_tanimsiz_kaynak_kapiyi_incelemeye_dusurur():
    """D-339'in kapıdaki hâli: `kaynak="v1"` **sessizce** v3'e yutulmaz.

    Ölçülen kusur: kapı `{"kaynak": "v3"}` döndürüyordu ama çağıran
    "v1 uygulandı" sanıyordu — uyuşmazlık hiçbir yerde görünmüyordu.
    Fail-closed zaten v3'ü uyguluyor; eksik olan **görünürlüktü**.
    """
    c = odin_musteri_cikis_kapisi("Görev ALTYAPI-ODIN-UYARLAMA-01", kaynak="v1")
    assert c["kapi"] == ODIN_KAPI_INCELEME, "tanimsiz kaynak insan kararina acilmali"
    assert c["kaynak"] == ODIN_KAYNAK_MUSTERI, "maske yine en kati kume uygulanmali"
    assert c["kaynak_istenen"] == "v1", "istenen ham ad gorunur olmali"
    assert c["kapi_tanimli"] is False


def test_tanimli_kaynak_kapiyi_etkilemez():
    """Sertleştirme mevcut davranışı bozmaz: v3'te K4 normal hesaplanır."""
    ham = "Anahtar: ODIN_INTERNAL_KEY=xyz"
    c = odin_musteri_cikis_kapisi(ham, kaynak="v3")
    assert c["kapi_tanimli"] is True
    assert c["kaynak_istenen"] == "v3"
    assert c["kapi"] == odin_kapi_olcumu(ham, kaynak=ODIN_KAYNAK_MUSTERI)

    # v3 / "V3" / 3 hepsi aynı kapıdır — yoksa yalnız boşluk çıkardı.
    for ayni in ("V3", " v3 ", 3):
        c2 = odin_musteri_cikis_kapisi(ham, kaynak=ayni)
        assert c2["kapi_tanimli"] is True, f"{ayni!r} v3 ile ayni olmali"
        assert c2["kapi"] == c["kapi"]


def test_kapi_sozlugu_kaynak_alanini_gosterir():
    """Sözlük şeması sabit: tüketici hangi alanı okuyacağını bilmeli."""
    c = odin_musteri_cikis_kapisi("Merhaba")
    assert set(c) == {
        "metin", "kapi", "kaynak", "kaynak_istenen", "kapi_tanimli",
    }


def test_kapi_olcumu_kaynak_parametresi_ayni_kumeyi_olcer():
    """D-211: `odin_kapi_olcumu` ikinci desen listesi açmaz.

    `kaynak` eklemenin tek sebebi ileriye dönük açıktı; ölçüm yine
    `ODIN_KAYNAK_TANIM[kaynak]` kümesini kullanır. Bugün tanımlı tek küme
    V3 olduğu için varsayılanla aynı sonucu vermesi zorunludur.
    """
    ham = "Anahtar: ODIN_INTERNAL_KEY=xyz"
    assert odin_kapi_olcumu(ham, kaynak=ODIN_KAYNAK_MUSTERI) == odin_kapi_olcumu(ham)
    # Tanımsız kaynak da aynı kümeye düşer (fail-closed).
    assert odin_kapi_olcumu(ham, kaynak="v1") == odin_kapi_olcumu(ham)


def test_normalizasyon_tek_yerde():
    """D-211: ham adı kanonikleştiren tek fonksiyon var.

    `odin_kaynak_dogrula` ve `odin_musteri_cikis_kapisi` ikisi de "istenen
    kaynak neydi" sorusunu sorar. Normalizasyon ikinci kez yazılırsa iki
    gerçek oluşur; bu test kopyayı yakalar.
    """
    assert _odin_kaynak_temizle("V3") == "v3"
    assert _odin_kaynak_temizle(3) == "v3"
    assert _odin_kaynak_temizle("v1") == "v1"
    assert _odin_kaynak_temizle(None) == ""
    assert odin_kaynak_dogrula("v9") == ODIN_KAYNAK_MUSTERI
    # Kapı istenen/uygulanan ayrımını bu tek yardımcıdan türetir.
    assert odin_musteri_cikis_kapisi("x", kaynak="v1")["kaynak_istenen"] == \
        _odin_kaynak_temizle("v1")


def test_ol_kod_kalmadi():
    """`if ad == "3": ad = "3"` gibi ölü dal bırakılmaz (kod okunabilirliği)."""
    p = ROOT / "src" / "company_master" / "sunum.py"
    metin = p.read_text(encoding="utf-8")
    assert 'if ad == "3":\n        ad = "3"' not in metin, "olu dal sunum.py icinde duruyor"
    # Bayat yorum: karar 2026-10-04'te kesinleşti, "soruldu" yazmaz.
    assert "karar KAHİN'e soruldu" not in metin, "bayat yorum kodda kaldi (D-265/1)"


def test_kaynak_musteri_sabiti_disa_aktarilir():
    """`__all__` her public sabiti ve fonksiyonu kapsar.

    Kırılma denemesi: `__all__`'dan `"ODIN_KAYNAK_MUSTERI"` silinirse bu
    test kırmızıya döner.
    """
    import company_master.sunum as sunum

    assert "ODIN_KAYNAK_MUSTERI" in sunum.__all__
    for ad in ("ODIN_KAYNAKLAR", "ODIN_KAYNAK_TANIM", "odin_kaynak_dogrula",
               "maskeleme_odin", "odin_musteri_cikis_kapisi"):
        assert ad in sunum.__all__, f"{ad} disa aktarilmiyor"
    # Yıldız içe aktarma gerçekten erişilebilir olmalı.
    yildiz = {ad for ad in dir(sunum) if not ad.startswith("_")}
    for ad in ("ODIN_KAYNAK_MUSTERI", "odin_musteri_cikis_kapisi"):
        assert ad in yildiz or hasattr(sunum, ad)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    hata = 0
    for ad, ham, beklenen in VAKALAR:
        gercek = odin_kapi_olcumu(ham)
        durum = "[OK]" if gercek == beklenen else "[HATA]"
        if gercek != beklenen:
            hata += 1
        print(f"{durum} {ad}: {gercek}")
    print(f"basarisiz: {hata}/{len(VAKALAR)}")
    raise SystemExit(1 if hata else 0)
