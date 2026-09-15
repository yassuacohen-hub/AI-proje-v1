# -*- coding: utf-8 -*-
"""KR-4 / BUG-ENCODING-GUARD: Kodlama denetim araci (BOM / NUL / 0-bayt / UTF-16).

Taranan tipler: .py, .md, .json, .toml, .sql
Raporlanan ihlaller:
    utf8_bom : UTF-8 BOM (EF BB BF) ile basliyor
    utf16    : UTF-16 BOM (FF FE / FE FF) ile basliyor
    nul      : icerikte NUL (0x00) bayti var
    bos      : 0 bayt (.py icin; `__init__.py` paket isaretci istisnasi haric)
    compile  : .py dosyasi compile() ile derlenemiyor

Kullanim:
    python scripts/kodlama_denetim.py              # yalnizca tara + raporla
    python scripts/kodlama_denetim.py --duzelt     # yalnizca UTF-8 BOM strip
                                                   # (UTF-16 / NUL / 0-bayt'a dokunulmaz)

Cikis kodu: ihlal varsa 1, yoksa 0.

Not (AGENTS.md uyumu): bu arac yazarken `Path.write_text`/`write_bytes`
kullanilir (Out-File -Encoding utf8 BOM yazdigi icin PowerShell'e
yonlendirilmez). Kaynak dosya bilerek BOM'suz UTF-8 + LF tutulur.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
ALLOWLIST_YOLU = KOK / "data" / "kodlama_allowlist.json"

# Taranmayacak agir / ilgisiz dizinler (buyuk veri, cikti ve arac klasorleri)
ATLANAN_DIZINLER = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    "data",
    "workspace",
    "test_reports",
    ".agents",
    ".kilo",
    "backups",
    "dist",
    "build",
    "htmlcov",
}

TARANAN_UZANTILAR = {".py", ".md", ".json", ".toml", ".sql"}

#: CI / guard kapsami (kod dizinleri). `--tam-repo` verilmedikce yalnizca bunlar taranir.
KAPSAM_DIZINLERI = ("src", "tests", "web_dashboard", "scripts")

UTF8_BOM = b"\xef\xbb\xbf"
UTF16LE_BOM = b"\xff\xfe"
UTF16BE_BOM = b"\xfe\xff"
NUL = b"\x00"


def allowlist_oku() -> dict[str, list[str]]:
    """data/kodlama_allowlist.json -> {'bom': [...], 'compile': [...]} dondurur.

    Ratchet sozlesmesi:
        bom     : bilinen UTF-8 BOM'lu dosyalar (gecici muafiyet; zamanla bosalmali)
        compile : bilinen derlenemeyen .py dosyalari (gecici muafiyet)
    """
    bos: dict[str, list[str]] = {"bom": [], "compile": []}
    if not ALLOWLIST_YOLU.is_file():
        return bos
    try:
        veri = json.loads(ALLOWLIST_YOLU.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return bos
    if not isinstance(veri, dict):
        return bos
    return {
        "bom": sorted(str(k) for k in veri.get("bom", [])),
        "compile": sorted(str(k) for k in veri.get("compile", [])),
    }


def allowlist_yaz(veri: dict[str, list[str]]) -> None:
    """Allowlist'i yazar ('bom' + 'compile' anahtarlari; ust dizin garanti edilir)."""
    ALLOWLIST_YOLU.parent.mkdir(parents=True, exist_ok=True)
    icerik = json.dumps(
        {
            "bom": sorted(set(veri.get("bom", []))),
            "compile": sorted(set(veri.get("compile", []))),
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    ALLOWLIST_YOLU.write_text(icerik, encoding="utf-8", newline="\n")


def _taranacak_dosyalar() -> list[Path]:
    """Repo kokunden taranan uzantili dosyalari toplar (agir dizinler budanir)."""
    import os

    dosyalar: list[Path] = []
    kok_str = str(KOK)
    for kok_dizin, dizinler, dosya_adlari in os.walk(kok_str):
        # dizin seviyesinde buda: agir/irrelevant klasorlere hic inme
        dizinler[:] = sorted(d for d in dizinler if d not in ATLANAN_DIZINLER)
        for dosya_adi in dosya_adlari:
            yol = Path(kok_dizin) / dosya_adi
            if yol.suffix.lower() not in TARANAN_UZANTILAR:
                continue
            dosyalar.append(yol)
    return sorted(dosyalar)


def _dosya_ihlalleri(yol: Path, kok: Path | None = None) -> list[tuple[str, str]]:
    """Tek dosyanin ihlal kayitlarini [(kod, detay), ...] dondurur.

    Args:
        yol: Denetlenecek dosya.
        kok: Goreceli yol hesabi icin kok (varsayilan repo koku; tmp_path
            tabanli birim testler icin override edilir).
    """
    kok = kok or KOK
    try:
        goreceli = yol.relative_to(kok).as_posix()
    except ValueError:
        goreceli = yol.as_posix()
    try:
        ham = yol.read_bytes()
    except OSError as hata:
        return [("okuma_hatasi", f"{goreceli} ({hata})")]

    bulgular: list[tuple[str, str]] = []
    if ham.startswith((UTF16LE_BOM, UTF16BE_BOM)):
        bulgular.append(("utf16", goreceli))
    if NUL in ham:
        bulgular.append(("nul", goreceli))
    if ham.startswith(UTF8_BOM):
        bulgular.append(("utf8_bom", goreceli))
    if not ham and not (yol.suffix == ".py" and yol.name == "__init__.py"):
        # 0 bayt: .py icin `__init__.py` (paket isaretcisi) istisnasi disinda ihlal
        bulgular.append(("bos", goreceli))
    if yol.suffix == ".py" and ham and NUL not in ham and not ham.startswith(UTF16LE_BOM):
        try:
            with warnings.catch_warnings():
                # eski scriptlerdeki gecersiz escape dizileri (SyntaxWarning) gurultu;
                # yalnizca gerçek SyntaxError ihlaldir
                warnings.simplefilter("ignore")
                compile(ham.decode("utf-8-sig"), str(yol), "exec")
        except (SyntaxError, ValueError, UnicodeDecodeError) as hata:
            bulgular.append(("compile", f"{goreceli} ({hata})"))
    return bulgular


def tara(kapsam: tuple[str, ...] | None = KAPSAM_DIZINLERI) -> dict[str, list[str]]:
    """Repo tarar; kod -> detay listesi sozlugunu dondurur (temizse bos).

    Args:
        kapsam: Yalnizca bu ust dizinler taranir; None -> tam repo (agir
            dizinler yine atlanir).
    """
    sonuclar: dict[str, list[str]] = {
        "utf8_bom": [],
        "utf16": [],
        "nul": [],
        "bos": [],
        "compile": [],
        "okuma_hatasi": [],
    }
    for yol in _taranacak_dosyalar():
        if kapsam is not None:
            parcalar = yol.relative_to(KOK).parts
            if not parcalar or parcalar[0] not in kapsam:
                continue
        for kod, detay in _dosya_ihlalleri(yol):
            sonuclar[kod].append(detay)
    return {k: sorted(v) for k, v in sonuclar.items() if v}


def duzelt(sonuclar: dict[str, list[str]]) -> list[str]:
    """Yalnizca UTF-8 BOM'u strip eder (UTF-16 / NUL / 0-bayt'a dokunulmaz).

    Returns:
        Degistirilen dosyalarin goreceli yollari.
    """
    degisen: list[str] = []
    for goreceli in sonuclar.get("utf8_bom", []):
        yol = KOK / goreceli
        try:
            ham = yol.read_bytes()
        except OSError:
            continue
        if ham.startswith(UTF8_BOM):
            yol.write_bytes(ham[len(UTF8_BOM) :])
            degisen.append(goreceli)
    return sorted(degisen)


def _rapor_yaz(sonuclar: dict[str, list[str]], baslik: str) -> None:
    print(f"== {baslik} ==")
    if not sonuclar:
        print("  temiz: kodlama ihlali yok")
        return
    for kod in sorted(sonuclar):
        print(f"  {kod} ({len(sonuclar[kod])}):")
        for detay in sonuclar[kod]:
            print(f"    - {detay}")


def main(argv: list[str] | None = None) -> int:
    cozumleyici = argparse.ArgumentParser(description="Kodlama denetimi (KR-4)")
    cozumleyici.add_argument(
        "--duzelt",
        action="store_true",
        help="Kapsam dizinlerindeki UTF-8 BOM'u strip et (diger ihlallere dokunulmaz)",
    )
    cozumleyici.add_argument(
        "--allowlist-guncelle",
        action="store_true",
        help="Mevcut utf8_bom bulgularini allowlist'e yaz (ratchet baslangici)",
    )
    cozumleyici.add_argument(
        "--tam-repo",
        action="store_true",
        help="Kod dizinleriyle sinirli kalma; tum repoyu tara (rapor amacli)",
    )
    secenekler = cozumleyici.parse_args(argv)

    kapsam = None if secenekler.tam_repo else KAPSAM_DIZINLERI
    sonuclar = tara(kapsam)
    _rapor_yaz(sonuclar, "TARAMA" if kapsam else "TARAMA (tam repo)")

    if secenekler.allowlist_guncelle:
        mevcut = allowlist_oku()
        allowlist_yaz(
            {
                "bom": sorted(set(mevcut["bom"]) | set(sonuclar.get("utf8_bom", []))),
                "compile": sorted(
                    set(mevcut["compile"]) | set(sonuclar.get("compile", []))
                ),
            }
        )
        print(f"allowlist guncellendi: {ALLOWLIST_YOLU.relative_to(KOK)}")

    if secenekler.duzelt:
        # Kapsam disina (kullanici belgeleri, .sql vb.) BOM strip uygulanmaz
        duzeltilecek = {
            kod: [d for d in liste if d.split("/")[0] in KAPSAM_DIZINLERI]
            for kod, liste in sonuclar.items()
        }
        degisen = duzelt(duzeltilecek)
        print(f"--duzelt: {len(degisen)} dosyadan UTF-8 BOM strip edildi")
        sonuclar = tara(kapsam)
        _rapor_yaz(sonuclar, "YENIDEN TARAMA")

    # Cikis kodu: allowlist disindaki ihlaller (ratchet sozlesmesi).
    # utf16 / nul / bos / okuma_hatasi icin muafiyet YOK; utf8_bom ve compile
    # yalnizca allowlist'te kayitliysa gecici olarak muaf sayilir.
    muaf = allowlist_oku()
    yeni_ihlaller: list[str] = []
    for kod, allow_anahtari in (
        ("utf8_bom", "bom"),
        ("compile", "compile"),
    ):
        muaf_kume = set(muaf.get(allow_anahtari, []))
        yeni_ihlaller.extend(
            f"{kod}: {d}" for d in sonuclar.get(kod, []) if d not in muaf_kume
        )
    for kod in ("utf16", "nul", "bos", "okuma_hatasi"):
        yeni_ihlaller.extend(f"{kod}: {d}" for d in sonuclar.get(kod, []))
    if yeni_ihlaller:
        print(f"ALLOWLIST DISI IHlAL ({len(yeni_ihlaller)}):")
        for satir in yeni_ihlaller:
            print(f"  - {satir}")
        return 1
    print("allowlist disi ihlal yok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
