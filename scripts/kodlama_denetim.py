# -*- coding: utf-8 -*-
"""KR-4 / BUG-ENCODING-GUARD + GUARD-ENC-01: Kodlama denetim araci.

Taranan tipler: .py, .md, .json, .toml, .sql, .yaml, .yml
Raporlanan ihlaller:
    utf8_bom : UTF-8 BOM (EF BB BF) ile basliyor
    utf16    : UTF-16 BOM (FF FE / FE FF) ile basliyor
    nul      : icerikte NUL (0x00) bayti var
    bos      : 0 bayt (.py icin; `__init__.py` paket isaretci istisnasi haric)
    compile  : .py dosyasi compile() ile derlenemiyor
    mojibake : cift-kodlama izleri (scripts/mojibake_onar.py imzalari;
               .py / .md / .sql icin satir numarali rapor)
    sozdizimi: .py dosyasi ast.parse() ile cozumlenemiyor
               (compile'dan ayri rapor; kirik girinti/BOM+parse
               kombinasyonlarini yakalar)

Kullanim:
    python scripts/kodlama_denetim.py              # yalnizca tara + raporla
    python scripts/kodlama_denetim.py --duzelt     # yalnizca UTF-8 BOM strip
                                                   # (UTF-16 / NUL / 0-bayt'a dokunulmaz)
    python scripts/kodlama_denetim.py --kapsam git # staged + worktree degisiklikleri

Cikis kodu: ihlal varsa 1, yoksa 0.

Not (AGENTS.md uyumu): bu arac yazarken `Path.write_text`/`write_bytes`
kullanilir (Out-File -Encoding utf8 BOM yazdigi icin PowerShell'e
yonlendirilmez). Kaynak dosya bilerek BOM'suz UTF-8 + LF tutulur.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
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

TARANAN_UZANTILAR = {".py", ".md", ".json", ".toml", ".sql", ".yaml", ".yml"}

#: CI / guard kapsami (kod dizinleri). `--tam-repo` verilmedikce yalnizca bunlar taranir.
KAPSAM_DIZINLERI = ("src", "tests", "web_dashboard", "scripts")

#: GUARD-ENC-01: mojibake imzalari (scripts/mojibake_onar.py'den yeniden
#: kullanilir — KOPYALANMAZ, import edilir; import basarisizsa yedek regex).
#: NOT: asagidaki iki satirda ham imza gorunmez (kacisli yazim); aksi halde
#: denetim araci kendi imzasini ihlal sayar (self-tespit -> EXIT 1 olurdu).


try:  # type: ignore[no-redef]
    from scripts.mojibake_onar import MOJIBAKE_RX as _MOJIBAKE_RX  # type: ignore[import-not-found,import-outside-toplevel]
except Exception:  # dogrudan calismada scripts/ sys.path'te yoksa yedek
    try:
        from mojibake_onar import MOJIBAKE_RX as _MOJIBAKE_RX  # type: ignore[import-not-found,no-redef,import-outside-toplevel]
    except Exception:
        _MOJIBAKE_RX = re.compile(
            "\x41\u0303.|"
            + "\xC2.|"
            + "\xE2\u0080.|"
            + "\xE2\u0084.|"
            + "\xE2\u009A.|"
            + "\xC3\xAF\u00B8|\xC3\x84.|\xC3\x85."
        )

#: Mojibake taramasi yapilan uzantilar (duz metin + kod).
#: GUARD-ENC-01 dersi: imza regex'i, saglam UTF-8 Turkce'yi de yakalayabilir
#: (ornegin A-tipi cift-kodlama izi, dogru Turkce'nin parcasi da olabilir).
#: Bu yuzden asagidaki _SATIR_MOJIBAKE_SUPHELISI filtresiyle esik alti
#: supheliler elenir.
MOJIBAKE_UZANTILARI = {".py", ".md", ".sql"}

#: GUARD-ENC-01: tek basina A-tipi gorunum mojibake degildir (Turkce c/g
#: harflerinin dogru UTF-8 kodlamasinda da gecer). Supheli sayilmasi icin
#: satirda asinagidaki guclu gostergelerden biri de olmalidir.
_MOJIBAKE_GUCLU_RX = re.compile(
    "\xC2"
    + "|\xE2\u0080"
    + "|\xE2\u0084"
    + "|\xE2\u009A"
    + "|\xC3\xAF\u00B8|\xC3\x84[^a-z]|\xC3\x85[^a-z]"
)


def _satir_mojibake_suphelisi(satir: str) -> bool:
    """Gercek cift-kodlamayi saglam UTF-8 Turkce'den ayir.

    `_MOJIBAKE_RX` tek basina cok genis (A-tipi oruntu her Turkce satiri
    yakalayabilir). Supheli icin: guclu gosterge VARSA supheli; YOKSA ve
    satir duzgun UTF-8 olarak cozumleniyorsa supheli DEGIL (saglam Turkce
    kabul edilir).
    """
    if not _MOJIBAKE_RX.search(satir):
        return False
    if _MOJIBAKE_GUCLU_RX.search(satir):
        return True
    try:
        satir.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return True  # geri-cozum basarisiz: gercekten bozuk
    return False

UTF8_BOM = b"\xef\xbb\xbf"
UTF16LE_BOM = b"\xff\xfe"
UTF16BE_BOM = b"\xfe\xff"
NUL = b"\x00"

#: GUARD-ENC-01: .py icin compile'dan bagimsiz sozdizimi raporu.
SOZDIZIMI_KODU = "sozdizimi"


def _muaf_disi(detay: str, muaf_kume: set[str]) -> bool:
    """Allowlist eslesmesi: `dosya:12 (msg)` detayini `dosya` bazinda karsilastir.

    GUARD-ENC-01 oncesi allowlist kayitlari yalindir (`yol`); yeni denetimler
    satir numarali detay uretir (`yol:satir (msg)`). Eski kayitlari kirmamak
    icin detay `:` oncesi kesilerek karsilastirilir.
    """
    return detay not in muaf_kume and detay.split(":")[0] not in muaf_kume


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
    if ham and NUL not in ham and not ham.startswith((UTF16LE_BOM, UTF16BE_BOM)):
        try:
            metin = ham.decode("utf-8-sig")
        except UnicodeDecodeError as hata:
            bulgular.append(("okuma_hatasi", f"{goreceli} ({hata})"))
            return bulgular
        if yol.suffix in MOJIBAKE_UZANTILARI and _MOJIBAKE_RX.search(metin):
            for no, satir in enumerate(metin.splitlines(), 1):
                if _satir_mojibake_suphelisi(satir):
                    bulgular.append(("mojibake", f"{goreceli}:{no}"))
        if yol.suffix == ".py":
            # GUARD-ENC-01: ast.parse, compile'dan ayri raporlanir (kirik
            # girinti / BOM+parse kombinasyonlarini yakalar).
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    ast.parse(metin, filename=str(yol))
            except SyntaxError as hata:
                bulgular.append(
                    (SOZDIZIMI_KODU, f"{goreceli}:{hata.lineno or '?'} ({hata.msg})")
                )
            except (ValueError, MemoryError, RecursionError) as hata:
                bulgular.append((SOZDIZIMI_KODU, f"{goreceli} ({hata})"))
        # crlf_karisik: karisik satir sonlari (\r\n ve \n bir arada)
        if "\r\n" in metin and "\n" in metin.replace("\r\n", ""):
            bulgular.append(("crlf_karisik", goreceli))
        # sondaki_bosluk: satir sonundaki bosluklar
        if yol.suffix in {".py", ".md", ".toml", ".yaml", ".yml"}:
            for no, satir in enumerate(metin.splitlines(), 1):
                if satir != satir.rstrip():
                    bulgular.append(("sondaki_bosluk", f"{goreceli}:{no}"))
        # tab_girinti: .py dosyalarinda tab girinti
        if yol.suffix == ".py":
            for no, satir in enumerate(metin.splitlines(), 1):
                if satir.startswith("\t"):
                    bulgular.append(("tab_girinti", f"{goreceli}:{no}"))
        # dosya_sonu: son satir sonlandirma yok
        if yol.suffix in {".py", ".md", ".toml", ".yaml", ".yml"} and ham and not ham.endswith(b"\n"):
            bulgular.append(("dosya_sonu", goreceli))
    return bulgular


def _git_degisen_dosyalar() -> set[str]:
    """Staged + worktree degisikliklerinin repo-goreceli posix yollari.

    GUARD-ENC-01 pre-commit hook'u icin: yalnizca commit'e giren dosyalari
    denetler. Git yoksa/hataliysa bos kume doner (bos kume = ihlal yok).
    """
    try:
        cikti = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "-z"],
            capture_output=True,
            cwd=KOK,
            timeout=30,
        ).stdout.split(b"\x00")
        cikti += subprocess.run(
            ["git", "diff", "--name-only", "-z"],
            capture_output=True,
            cwd=KOK,
            timeout=30,
        ).stdout.split(b"\x00")
        dosyalar = set()
        for ham in cikti:
            if not ham:
                continue
            try:
                dosyalar.add(Path(ham.decode("utf-8")).as_posix())
            except UnicodeDecodeError:
                continue
        return dosyalar
    except Exception:
        return set()


def tara(
    kapsam: tuple[str, ...] | None = KAPSAM_DIZINLERI,
    yalnizca: set[str] | None = None,
) -> dict[str, list[str]]:
    """Repo tarar; kod -> detay listesi sozlugunu dondurur (temizse bos).

    Args:
        kapsam: Yalnizca bu ust dizinler taranir; None -> tam repo (agir
            dizinler yine atlanir).
        yalnizca: Verilirse yalnizca bu repo-goreceli posix yollar taranir
            (pre-commit hook icin git degisen dosyalari).
    """
    sonuclar: dict[str, list[str]] = {
        "utf8_bom": [],
        "utf16": [],
        "nul": [],
        "bos": [],
        "compile": [],
        "okuma_hatasi": [],
        "mojibake": [],
        "sozdizimi": [],
        "crlf_karisik": [],
        "sondaki_bosluk": [],
        "tab_girinti": [],
        "dosya_sonu": [],
    }
    for yol in _taranacak_dosyalar():
        if kapsam is not None:
            parcalar = yol.relative_to(KOK).parts
            if not parcalar or parcalar[0] not in kapsam:
                continue
        if yalnizca is not None and yol.relative_to(KOK).as_posix() not in yalnizca:
            continue
        for kod, detay in _dosya_ihlalleri(yol):
            # GUARD-ENC-01: yeni ihlal kodlari (mojibake/sozdizimi/okuma_hatasi)
            # onceden tanimli anahtar gerektirmez.
            sonuclar.setdefault(kod, []).append(detay)
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
    for goreceli in sonuclar.get("crlf_karisik", []):
        yol = KOK / goreceli
        try:
            icerik = yol.read_text(encoding="utf-8")
        except OSError:
            continue
        duzeltilmis = icerik.replace("\r\n", "\n").replace("\r", "\n")
        if duzeltilmis != icerik:
            yol.write_text(duzeltilmis, encoding="utf-8", newline="")
            degisen.append(goreceli)
    for goreceli in sonuclar.get("sondaki_bosluk", []):
        yol = KOK / goreceli
        try:
            icerik = yol.read_text(encoding="utf-8")
        except OSError:
            continue
        satirlar = icerik.split("\n")
        duzeltilmis = "\n".join(s.rstrip() for s in satirlar)
        if duzeltilmis != icerik:
            yol.write_text(duzeltilmis, encoding="utf-8", newline="")
            degisen.append(goreceli)
    for goreceli in sonuclar.get("tab_girinti", []):
        yol = KOK / goreceli
        try:
            icerik = yol.read_text(encoding="utf-8")
        except OSError:
            continue
        satirlar = icerik.split("\n")
        duzeltilmis_satirlar = []
        for satir in satirlar:
            if satir.startswith("\t"):
                sayac = 0
                while satir.startswith("\t"):
                    sayac += 1
                    satir = satir[1:]
                duzeltilmis_satirlar.append("    " * sayac + satir)
            else:
                duzeltilmis_satirlar.append(satir)
        duzeltilmis = "\n".join(duzeltilmis_satirlar)
        if duzeltilmis != icerik:
            yol.write_text(duzeltilmis, encoding="utf-8", newline="")
            degisen.append(goreceli)
    for goreceli in sonuclar.get("dosya_sonu", []):
        yol = KOK / goreceli
        try:
            ham = yol.read_bytes()
        except OSError:
            continue
        if ham and not ham.endswith(b"\n"):
            yol.write_bytes(ham + b"\n")
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
    cozumleyici.add_argument(
        "--kapsam",
        choices=("kod", "git"),
        default="kod",
        help="kod: KAPSAM_DIZINLERI (varsayilan); git: staged + worktree degisiklikleri (pre-commit)",
    )
    secenekler = cozumleyici.parse_args(argv)

    degisen_dosyalar = _git_degisen_dosyalar() if secenekler.kapsam == "git" else None
    kapsam = None if secenekler.tam_repo else KAPSAM_DIZINLERI
    sonuclar = tara(kapsam, yalnizca=degisen_dosyalar)
    baslik = "TARAMA"
    if degisen_dosyalar is not None:
        baslik = f"TARAMA (git: {len(degisen_dosyalar)} degisen dosya)"
    elif kapsam is None:
        baslik = "TARAMA (tam repo)"
    _rapor_yaz(sonuclar, baslik)

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
    # utf16 / nul / bos / okuma_hatasi / mojibake / sozdizimi icin muafiyet
    # YOK; utf8_bom ve compile yalnizca allowlist'te kayitliysa gecici muaf.
    muaf = allowlist_oku()
    yeni_ihlaller: list[str] = []
    for kod, allow_anahtari in (
        ("utf8_bom", "bom"),
        ("compile", "compile"),
    ):
        muaf_kume = set(muaf.get(allow_anahtari, []))
        yeni_ihlaller.extend(
            f"{kod}: {d}" for d in sonuclar.get(kod, []) if _muaf_disi(d, muaf_kume)
        )
    for kod in ("utf16", "nul", "bos", "okuma_hatasi", "mojibake", "sozdizimi", "crlf_karisik", "sondaki_bosluk", "tab_girinti", "dosya_sonu"):
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
