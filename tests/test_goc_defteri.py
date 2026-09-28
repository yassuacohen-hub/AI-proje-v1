# -*- coding: utf-8 -*-
"""Goc defteri mandali (GOC-DEFTER-01, D-251/3).

Defter semanin tek anlaticisidir. Bu mandal defterin yalan soylemesini
yakalar. Framework yok; dogrudan calisir:

    python tests/test_goc_defteri.py
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.quality_recalc import tavan_raporu  # noqa: E402
from scripts.goc_defteri import degerlendir, goc_izleri, sema_durumu  # noqa: E402


def test_defter_semayla_uyusuyor():
    izler = goc_izleri()
    with get_engine().connect() as conn:
        sema = sema_durumu(conn)
        defter = {
            r[0] for r in conn.execute(text("SELECT filename FROM schema_migrations"))
        }
    sonuc = degerlendir(izler, sema)

    # 1) Diskteki her goc defterde olmali (D-251/3).
    yazilmamis = sorted(set(izler) - defter)
    assert not yazilmamis, f"Deftere yazilmamis goc: {yazilmamis}"

    # 2) Defterdeki her kayit diskte olmali; hayalet kayit defteri yalanci yapar.
    hayalet = sorted(defter - set(izler))
    assert not hayalet, f"Diskte karsiligi olmayan defter kaydi: {hayalet}"

    # 3) Defterde yazan ama semada izi eksik goc = uygulanmamis sayilir.
    eksik = {d: e for d, (durum, e) in sonuc.items() if durum == "EKSIK"}
    assert not eksik, f"Defterde yazili ama semada izi yok: {eksik}"

    # 4) Sayilar esit (gorevin acik mandali).
    assert len(izler) == len(defter), f"{len(izler)} goc != {len(defter)} kayit"

    # 5) D-267: "IZSIZ" = arac dogrulayamadi demektir; bir dosya icin dogruysa
    #    dosyada "veri-gocu:" ile YAZILI olmalidir. Yazisiz IZSIZ kalan her goc
    #    bugun yanlis alarm, yarin gercek alarmi gizleyen gurultudur.
    izsiz = sorted(d for d, (durum, _) in sonuc.items() if durum == "IZSIZ")
    assert not izsiz, f"Sebebi yazilmamis izsiz goc (veri-gocu: ekle): {izsiz}"


# D-251/1 kapsamindaki bilinen borc. SEMA-IKIZ-01 (goc 0027) ile besinin
# besi de kapandi; liste BOS. Mandalin isi bu listeyi KUCULTMEK degil,
# BUYUMESINI engellemek. Buraya yeni ad eklemek bilincli bir borc kaydidir.
BILINEN_DIL_BORCU: set[str] = set()

# Kolon adi "_" ile parcalanir, her parca bu koklerle karsilastirilir.
# Parca bazli olmasinin sebebi: govde icinde arama yanlis alarm uretir
# ("fea-tur-es", "contr-adi-ction" Ingilizce'dir).
TURKCE_KOKLER = (
    "adres", "vergi", "sicil", "kimlik", "puan", "surum", "sayi", "tarih",
    "durum", "parsel", "site", "unvan", "ilce", "sehir", "firma", "musteri",
    "kullanici", "yetki", "ayar", "tamlik", "aktif", "gecerli", "kaynak",
)


def _turkce_mi(kolon: str) -> bool:
    if any(c in "çğıöşüÇĞİÖŞÜ" for c in kolon):
        return True
    return any(
        parca.startswith(kok)
        for parca in kolon.lower().split("_")
        for kok in TURKCE_KOKLER
    )


def test_sema_dili_ingilizce():
    """D-251/1: kolon adlarinda Turkce kelime/karakter olmaz."""
    with get_engine().connect() as conn:
        kolonlar = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT DISTINCT column_name FROM information_schema.columns "
                    "WHERE table_schema='public'"
                )
            )
        }
    supheli = {k for k in kolonlar if k not in BILINEN_DIL_BORCU and _turkce_mi(k)}
    assert not supheli, f"Yeni Turkce kolon adi (D-251/1): {sorted(supheli)}"

    # Mandal kendi kendini de denetler: ayirt edici mi?
    assert _turkce_mi("vergi_dairesi"), "Turkce ad yakalanmiyor"
    assert not _turkce_mi("features"), "Ingilizce ad yanlis alarm veriyor"
    assert not _turkce_mi("contradiction_penalty"), "Ingilizce ad yanlis alarm"

    # Kapanan borc listede kalmasin (liste bayatlamasin).
    bayat = BILINEN_DIL_BORCU - kolonlar
    assert not bayat, f"Borc listesinde olmayan kolon var, silinmeli: {sorted(bayat)}"


def test_sicil_semada_duruyor():
    """D-267 (GOC 0035): sicil degeri ham arsivde degil, semada okunabilir mi?

    Sayilarin kaynagi tek tek olculmustur, uydurulmamistir:
      619 = raw_payload->>'ticaretSicilNo' tasiyan 620 kaydin firmaya bagli olani
             (1 kayit hicbir firmaya bagli degil), hepsi sicil_dogrula()'dan gecti
       25 = bu 619'un icinde sicil DAIRESI de tasiyan firma sayisi. D-250 puan
             icin no VE daire'yi birlikte ister; puan alan bu 25'tir.
    Sayi degisirse once olcum yenilenmeli, test degil.
    """
    with get_engine().connect() as conn:
        n = dict(
            conn.execute(
                text(
                    "SELECT count(trade_registry_number) no, "
                    "count(trade_registry_office) daire FROM companies"
                )
            ).mappings().one()
        )
    assert n["no"] == 619, f"sicil no dolu firma {n['no']}, beklenen 619 (goc 0035)"
    assert n["daire"] == 25, f"sicil dairesi dolu firma {n['daire']}, beklenen 25"

    # Tavan bu 25 sayesinde acilir: "kilitli" = SIFIR firma puan aliyor demek.
    # 25 > 0 oldugu icin trade_registry_number artik kilitli degil (D-258).
    r = tavan_raporu()
    assert "trade_registry_number" not in r["kilitli"], (
        f"sicil hala kilitli gorunuyor: {r['kilitli']}"
    )
    assert r["tavan"] == 7.5, f"tavan {r['tavan']}, beklenen 7.5 (D-267)"


if __name__ == "__main__":
    test_defter_semayla_uyusuyor()
    test_sema_dili_ingilizce()
    test_sicil_semada_duruyor()
    print("MANDAL GECTI.")
