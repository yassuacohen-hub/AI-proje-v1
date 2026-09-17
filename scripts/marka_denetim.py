# -*- coding: utf-8 -*-
"""MARKA-REVIZE-01: Marka kimliği denetim araci.

Tarayan dosya tipleri: .py, .md, .json, .toml, .sql, .yaml, .yml
Raporlanan ihlaller:
    yasal_yazim: Huginn/Muninn/Odin yasak yazimlari (Huggin, Hugginn, Hugin,
                 Munin, Muginn, Odin, Odinn, Muginn, Munnin)
    kok_dizin: "kok dizindeki" ifadesi (kullanilmamali, docs/brand/ kastedilir)

Kullanim:
    python scripts/marka_denetim.py              # tarama + rapor

Cikis kodu: ihlal varsa 1, yoksa 0.
"""
from __future__ import annotations

import ast
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
}

DOSYA_extensions = {".py", ".md", ".json", ".toml", ".sql", ".yaml", ".yml"}


def tarama_kapsami() -> list[Path]:
    """Kok dizindeki tum dosyalari dondurur (ATLANAN_DIZINLER disi)."""
    for path in KOK.rglob("*"):
        if path.is_file() and path.suffix in DOSYA_extensions:
            if any(part in ATLANAN_DIZINLER for part in path.parts):
                continue
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
        if not path.is_file() or path.suffix not in DOSYA_extensions:
            continue
        if any(part in ATLANAN_DIZINLER for part in path.parts):
            continue
        _tarama_dosya(path, sonuc)

    return sonuc


def _tarama_dosya(path: Path, sonuc: dict[str, list[str]]) -> None:
    try:
        icerik = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return

    for no, satir in enumerate(icerik.splitlines(), start=1):
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
    sonuc = tarama()
    toplam = len(sonuc["yasal_yazim"]) + len(sonuc["kok_dizin"])

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
