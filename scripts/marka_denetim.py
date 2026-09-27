# -*- coding: utf-8 -*-
"""MARKA-REVIZE-01: Marka kimliği denetim araci.

Tarayan dosya tipleri: .py, .md, .json, .toml, .sql, .yaml, .yml
Raporlanan ihlaller:
    yasal_yazim: Huginn/Muninn/Odin yasak yazimlari (Huggin, Hugginn, Hugin,
                 Munin, Muginn, Odin, Odinn, Muginn, Munnin)
    kok_dizin: "kok dizindeki" ifadesi (kullanilmamali, docs/brand/ kastedilir)

Muafiyet (MARKA-REVIZE-01-BULGU, B-1/B-2):
    1) ATLANAN_DIZINLER  - arsiv/gecici/ajan calisma alanlari hic taranmaz
    2) MUAF_YOLLAR       - kokten glob; yasak listeyi TANIMLAYAN dosyalar
    3) MUAF_SENTINEL     - satirda 'marka-muaf' geciyorsa o satir atlanir

Kullanim:
    python scripts/marka_denetim.py              # tarama + rapor
    python scripts/marka_denetim.py --sayim      # sadece ozet

Cikis kodu: ihlal varsa 1, yoksa 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

YASAL_YAZIM = re.compile(
    r"Muginn|Hugin\b|Munin\b|Hugginn|Munnin|Odinn|Huggin\b",
    re.IGNORECASE,
)
ODIN_MISSPELLING = re.compile(r"Odın")  # exact: Turkc dotless i (U+0131)

KOK_DIZIN = re.compile(r"kok\s+dizindeki", re.IGNORECASE)

ATLANAN_DIZINLER = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".streamlit",
    "data",
    "venv",
    ".venv",
    "env",
    # B-2: eksik olan calisma alanlari / arsivler
    "_trash",
    "backups",
    ".kilo",
    ".agents",
    ".claude",
    ".continue",
    "workspace",
    "AI proje v1",
    # D-228 (2026-09-27): "data_worktree" muafiyeti kaldirildi — dizin silindi
    # (95 essiz dosya arsive tasindi). Muafiyet gerekcesi D-170'in "merge
    # bekliyor" notuydu; 6 gun bekleyen merge merge degildir. Geri dogarsa
    # tests/test_kok_izin_listesi.py::test_vault_icinde_paralel_veri_govdesi_yok
    # kirmizi yanar; burada tekrar muaf yazmak yasak.
}

# B-1: yasak listeyi TANIMLAYAN dosyalar kendi kurallarina takilmasin.
MUAF_YOLLAR: tuple[str, ...] = (
    "scripts/marka_denetim.py",       # yasak regex burada tanimli
    "docs/plans/*",                   # brifler yasak yazimlari ornekliyor
    "plans/*",
    "docs/ROO_ELESTIRI_NOTLARI.md",   # elestiri kayitlari ihlali alintiliyor
    "tests/test_i18n*.py",            # test regexleri yasak yazimi iceriyor
    "tests/test_marka*.py",
    "AGENT_SYNC.md",                  # otomatik uretilir (task_board'dan)
    "data/orchestrator/AGENT_SYNC.md",
)

MUAF_SENTINEL = "marka-muaf"

# B-1: "Yasak: Huggin, Hugin, ..." gibi kurali TANIMLAYAN satirlar ihlal degildir.
YASAK_BEYAN = re.compile(r"yasak|forbidden|misspell", re.IGNORECASE)

DOSYA_extensions = {".py", ".md", ".json", ".toml", ".sql", ".yaml", ".yml"}


def muaf_dosya(path: Path) -> bool:
    """Dosya MUAF_YOLLAR desenlerinden birine uyuyorsa True."""
    try:
        bagil = path.relative_to(KOK).as_posix()
    except ValueError:
        return False
    return any(Path(bagil).match(desen) for desen in MUAF_YOLLAR)


def taranabilir(path: Path) -> bool:
    """Dosya denetime girer mi? (uzanti + atlanan dizin + muaf yol)"""
    if not path.is_file() or path.suffix not in DOSYA_extensions:
        return False
    if any(part in ATLANAN_DIZINLER for part in path.parts):
        return False
    return not muaf_dosya(path)


def tarama_kapsami():
    """Kok dizindeki taranabilir dosyalari uretir."""
    for path in KOK.rglob("*"):
        if taranabilir(path):
            yield path


def tarama(
    dizin: Path | None = None,
) -> dict[str, list[str]]:
    """Marka ihlallerini taramak icin kullanilir.

    Dondurulan sozluk:
        yasal_yazim: [dosya_yolu: satir_no: metin]
        kok_dizin: [dosya_yolu: satir_no: metin]
    """
    root = dizin or KOK
    sonuc: dict[str, list[str]] = {"yasal_yazim": [], "kok_dizin": []}

    if root.is_file():
        _tarama_dosya(root, sonuc)
        return sonuc

    for path in root.rglob("*"):
        if not taranabilir(path):
            continue
        _tarama_dosya(path, sonuc)

    return sonuc


def _tarama_dosya(path: Path, sonuc: dict[str, list[str]]) -> None:
    try:
        icerik = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return

    for no, satir in enumerate(icerik.splitlines(), start=1):
        if MUAF_SENTINEL in satir:  # B-1: nokta atisi istisna
            continue
        if YASAK_BEYAN.search(satir):  # B-1: kural tanimi, ihlal degil
            continue
        for mac in YASAL_YAZIM.finditer(satir):
            sonuc["yasal_yazim"].append(
                f"{path}:{no}: '{mac.group()}' -> {satir.strip()[:120]}"
            )
        for mac in ODIN_MISSPELLING.finditer(satir):
            sonuc["yasal_yazim"].append(
                f"{path}:{no}: '{mac.group()}' -> {satir.strip()[:120]}"
            )
        for mac in KOK_DIZIN.finditer(satir):
            sonuc["kok_dizin"].append(
                f"{path}:{no}: {satir.strip()[:120]}"
            )


if __name__ == "__main__":
    sadece_sayim = "--sayim" in sys.argv
    sonuc = tarama()
    toplam = len(sonuc["yasal_yazim"]) + len(sonuc["kok_dizin"])

    if sadece_sayim:
        print(f"yasal_yazim: {len(sonuc['yasal_yazim'])} | kok_dizin: {len(sonuc['kok_dizin'])}")
        sys.exit(1 if toplam > 0 else 0)

    if sonuc["yasal_yazim"]:
        print("=== Yasal Yazim Ihlalleri ===")
        for m in sonuc["yasal_yazim"]:
            print(m)

    if sonuc["kok_dizin"]:
        print("=== Kok Dizindeki Ihlalleri ===")
        for m in sonuc["kok_dizin"]:
            print(m)

    if toplam == 0:
        print("Marka denetimi: temiz")
    else:
        print(f"\nToplam ihlal: {toplam}")

    sys.exit(1 if toplam > 0 else 0)
