# -*- coding: utf-8 -*-
"""D-288 — TSG pipeline zincir testi (DB bağımsız).

Kanıt dosyaları -> ilan_turu_normalize_et -> olay_esle -> event_type/direction
-> company_events şeması uyumu zincirini doğrular. Veritabanına bağlanmaz.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.company_master.etl.tsg_yazici import (
    ilan_turu_normalize_et,
    kanit_dosyalarini_oku,
    olay_esle,
    _source_guid_olustur,
    TsgYaziciSonuc,
)


def test_kanit_dosyalari_okunur():
    """data/kanit/ altındaki tüm JSON'lar okunabilmeli."""
    dosyalar = kanit_dosyalarini_oku()
    assert len(dosyalar) > 0, "Kanıt dosyası bulunamadı"
    for d in dosyalar:
        assert "_dosya_adi" in d


def test_ilan_turu_normalize():
    """Büyük harf + boşluk normalize."""
    assert ilan_turu_normalize_et("  LİMİTED ŞİRKET (KURULUŞ)  ") == "LİMİTED ŞİRKET (KURULUŞ)"
    assert ilan_turu_normalize_et(None) is None
    assert ilan_turu_normalize_et("") is None


def test_olay_esle_tum_kanitlar_eslesin():
    """Tüm kanıt dosyalarındaki il_turu, olay_esle ile eşleşmeli."""
    dosyalar = kanit_dosyalarini_oku()
    eslesmeyen = []
    for d in dosyalar:
        tur = ilan_turu_normalize_et(d.get("il_turu"))
        if not tur:
            continue
        et, dirn = olay_esle(tur)
        if et is None:
            eslesmeyen.append(tur)
    assert not eslesmeyen, f"Eşleşmeyen il_turu: {eslesmeyen}"


def test_olay_esle_bos():
    """Boş/None girdi None, 'unknown' döner."""
    et, dirn = olay_esle(None)
    assert et is None
    assert dirn == "unknown"
    et, dirn = olay_esle("")
    assert et is None
    assert dirn == "unknown"


# ---------------------------------------------------------------------------
# VERI-TSG-ESLEME-CASE-01 — ASCII katlama Türkçe harfi yutmamalı (D-256/4)
#
# Neden ayrı mandal: yukarıdaki `test_olay_esle_tum_kanitlar_eslesin`
# kanıt dosyalarını okur, ama bu dosyalar `il_turu`'yu **ASCII saklıyor**.
# Gerçek TSG verisi **Türkçe** gelir. Bu yüzden katlama hatası o mandalı
# geçiyordu: ölçülen 4 sermaye artırımı kaydı `unknown` dönüyordu.
# ---------------------------------------------------------------------------

#: Katlamada yutulması yasak Türkçe harflerin ASCII karşılığı.
#: `str.encode("ascii", "ignore")` Unicode katmanında bunları **sessizce
#: düşürür**; karşılık tablosu olmadan `"Artırımı"` -> `"ARTRM"` olur.
TR_ASCII_CIFILERI = {
    "ı": "I", "ş": "S", "ğ": "G", "ü": "U", "ö": "O", "ç": "C",
}


def test_ascii_katlama_turkce_harfi_yutmaz():
    """`_asciiye()` Türkçe harfleri karşılıklarına çevirmeli, düşürmemeli.

    Ölçülen hata (2026-10-02): eski katlama `"Artırımı" -> "ARTRM"` ve
    `"Şube Açılış" -> "SUBE ACLS"` üretiyordu; `ILAN_TURU_ESLEME`
    anahtarları (`SERMAYE ARTIRIMI`, `SUBE ACILIS`) elle ASCII yazıldığı
    için katlama yolu onları **hiç üretemiyordu**.
    """
    from skills.services.ticaret_sicili_kanit import _asciiye

    assert _asciiye("Artırımı") == "ARTIRIMI"
    assert _asciiye("Şube Açılış") == "SUBE ACILIS"
    assert _asciiye("Değişiklik") == "DEGISIKLIK"
    assert _asciiye("Yönetim Kurulu") == "YONETIM KURULU"
    assert _asciiye("Konkordato") == "KONKORDATO"
    assert _asciiye("Tür Değişikliği") == "TUR DEGISIKLIGI"
    assert _asciiye("İptal") == "IPTAL"
    assert _asciiye("Taşfiye") == "TASFIYE"


def test_ascii_katlama_harf_sayisini_korur():
    """Katlama harf **sayısını** korur — yutmaz, silmez.

    Uzunluk ölçüsü seçildi çünkü "yutma" tanımı zaten uzunluktur: eski
    katlamada `"Artırımı"` (8) -> `"ARTRM"` (5) idi. Sözlük anahtarları
    zaten ASCII olduğu için katlanmış hâlleri **özdeş** olmalıdır.
    """
    from skills.services.ticaret_sicili_kanit import ILAN_TURU_ESLEME, _asciiye

    for metin in ("Artırımı", "Şube Açılış", "İptal", "Taşfiye", "Yönetim Kurulu"):
        kat = _asciiye(metin)
        assert len(kat) == len(metin), f"harf yutuldu: {metin!r} -> {kat!r}"

    bozulan = [k for k in ILAN_TURU_ESLEME if _asciiye(k) != k]
    assert not bozulan, f"Katlanmış anahtar özdeş değil (sözlük zaten ASCII): {bozulan}"


def test_olay_esle_turkce_girdi_eslesir():
    """Kanıt dosyalarındaki **ölçülmüş** her `il_turu`, Türkçe harfli
    karşılığıyla da eşleşebilmeli.

    Bu, sözlük ile katlamanın **aynı** normalizasyonu paylaştığını kanıtlar.
    Anahtarlar elle ASCII yazıldığı için bu yol önceden sessizce başarısızdı.

    **Neden kanıt dosyalarından:** uydurma örnek "Sermaye Artırımı" gibi
    gerçek veride **olmayan** bir ilan türüne işaret eder ve ölçülmeden
    karar yazmış oluruz (D-224). Kaynak metinler gerçekten kanıttır.
    """
    from skills.services.ticaret_sicili_kanit import olay_esle

    dosyalar = kanit_dosyalarini_oku()
    turler = {
        d["il_turu"] for d in dosyalar if (d.get("il_turu") or "").strip()
    }
    assert turler, "kanıt dosyalarında il_turu bulunamadı — mandal boşa geçmesin"

    # ASCII -> Türkçe harf karşılığı (sözlük anahtarları ASCII yazılmıştır).
    # I->ı, S->ş, G->ğ, U->ü, C->ç (O/Ö çifti kasıtlı: `O` -> `ö` de geçerli).
    geri = str.maketrans("ISGUCO", "ışğüçö")

    eslesmeyen = [
        t for t in sorted(turler)
        if olay_esle(t)[0] is None or olay_esle(t.translate(geri))[0] is None
    ]
    assert not eslesmeyen, f"Türkçe karşılığıyla eşleşmedi: {eslesmeyen}"

    # En az biri gerçekten Türkçe harf içermeli; yoksa mandal hiçbir şey
    # ölçmüyor demektir (sessizce geçen mandal = olmayan mandal, D-256).
    turkce = [t for t in turler if t.translate(geri) != t]
    assert turkce, "kanıt il_turu değerlerinin hepsi ASCII — mandal işlevsiz kalır"


def test_source_guid_benzersiz():
    """Her kanıt için source_guid benzersiz olmalı."""
    dosyalar = kanit_dosyalarini_oku()
    guidler = set()
    for d in dosyalar:
        guid = _source_guid_olustur(d)
        assert guid not in guidler, f"Duplicate source_guid: {guid}"
        guidler.add(guid)
    assert len(guidler) == len(dosyalar)


def test_pipeline_sonuc_sinifi():
    """TsgYaziciSonuc varsayılan değerleri doğru."""
    s = TsgYaziciSonuc()
    assert s.islenen == 0
    assert s.eklenen == 0
    assert s.guncellenen == 0
    assert s.atlanan == 0
    assert s.hatalar == []


def test_pipeline_get_engine_kullanimi():
    """get_engine() database gate kullanılmıyor (import + kaynak kontrolü)."""
    import inspect
    modul = sys.modules["src.company_master.etl.tsg_yazici"]
    kaynak = inspect.getsource(modul)
    assert "get_engine" in kaynak, "get_engine import edilmemiş"
    assert "_veritabani_baglantisi" not in kaynak, "Eski _veritabani_baglantisi kalıyor"


# --- Geri doldurma araci (D-261: "kod yazildi" ile "kosturuldu" ayridir) ---


def test_geri_doldurma_yedekteki_degeri_gozlemez():
    """Hedef deger **kanittan** yeniden hesaplanir; yedekteki `event_type_yeni`
    guvenilmez.

    Yedek "ne degisecek" bilgisini tasir; "ne olmali" bilgisi tek kapidan
    (`olay_esle`) gelir. Yedek ikinci bir gercek olsaydi (D-211), kirilan bir
    geri dosyasi tabloya **yanlis degeri** yazardi — hem de "dogrulandi"
    mesajiyla.
    """
    import importlib.util
    from pathlib import Path

    kok = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "_tsg_geri_doldurma", kok / "scripts" / "tsg_esleme_geri_doldur.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Yedek bilerek **yanlis** bir "yeni deger" vaat ediyor.
    yedek = [{
        "source_guid": "test-1",
        "event_type_yeni": "YANLIS_DEGER",
        "event_type_onceki": None,
        "il_turu": "ŞUBE AÇILIŞ",
    }]
    out = mod.kanittan_hesapla(yedek)
    assert len(out) == 1
    assert out[0]["event_type"] != "YANLIS_DEGER", (
        "geri doldurma yedekteki degeri kabul etti — kanit kapisi atlandi"
    )
    assert out[0]["event_type"] == "sube_acilisi"
    assert out[0]["direction"] == "positive"


def test_geri_doldurma_prova_yazmaz():
    """`--dene` kipi yazmaz; varsayilan kip prova (D-243).

    Kaynak metin denetimi: geri dosyasinda yazma yolu `--yaz` sartina
    baglanmis olmali; `--dene` dalinda `backup_path=None` basilmali.
    """
    import importlib.util
    from pathlib import Path

    kok = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "_tsg_geri_doldurma2", kok / "scripts" / "tsg_esleme_geri_doldur.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    kaynak = Path(kok / "scripts" / "tsg_esleme_geri_doldur.py").read_text(
        encoding="utf-8"
    )

    assert "backup_path=None" in kaynak, "prova backup_path=None bildirmiyor"
    assert "if not args.yaz:" in kaynak, "prova yazma oncesi erken donus yok"
    # Yazma tek transaction icinde; satir sayisi denetimi kalsin.
    assert "RuntimeError" in kaynak, " satir sayisi denetimi yok (D-243)"
