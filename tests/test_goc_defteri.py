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
    return len(izler)


# D-251/1 kapsamindaki bilinen borc. SEMA-IKIZ-01 ve IP-ADRESI isleriyle
# kapatilacak. Mandalin isi bu listeyi KUCULTMEK degil, BUYUMESINI engellemek.
BILINEN_DIL_BORCU = {
    "adres",        # -> address      (SEMA-IKIZ-01, 5797 dolu)
    "osb_parsel",   # -> osb_parcel   (SEMA-IKIZ-01)
    "vergi_no",     # -> tax_number   (SEMA-IKIZ-01, 761 dolu, ikiz)
    "web_sitesi",   # -> website_domain (SEMA-IKIZ-01, 5049 dolu, ikiz)
    "ip_adresi",    # -> ip_address   (GOC-DEFTER-01 olcumunde bulundu)
}

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
    return len(BILINEN_DIL_BORCU)


if __name__ == "__main__":
    n = test_defter_semayla_uyusuyor()
    b = test_sema_dili_ingilizce()
    print(f"MANDAL GECTI: {n} goc = {n} defter kaydi; {b} bilinen dil borcu.")
