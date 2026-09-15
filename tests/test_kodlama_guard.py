# -*- coding: utf-8 -*-
"""KR-4 / BUG-ENCODING-GUARD: Kodlama ratchet guard testleri.

Iki katman:
  1) Scanner birim testleri (gecici dosyalarla - repoya dokunmaz)
  2) Ratchet guard: data/kodlama_allowlist.json disinda yeni UTF-8 BOM ->
     kirmizi; UTF-16 / NUL / 0-bayt .py icin allowlist YOK (her zaman kirmizi).

Kapsam dizinleri: src, tests, web_dashboard, scripts (agir veri klasorleri
taranmaz; tam repo taramasi: `python scripts/kodlama_denetim.py`).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
ARAC_YOLU = KOK / "scripts" / "kodlama_denetim.py"
ALLOWLIST_YOLU = KOK / "data" / "kodlama_allowlist.json"
KAPSAM_DIZINLERI = ("src", "tests", "web_dashboard", "scripts")


def _arac_yukle():
    spec = importlib.util.spec_from_file_location("kodlama_denetim", ARAC_YOLU)
    modul = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture(scope="module")
def denetim():
    return _arac_yukle()


# ------------------------------------------------------------------ birim testler


def test_utf8_bom_tespit(denetim, tmp_path: Path) -> None:
    hedef = tmp_path / "ornek.py"
    hedef.write_bytes(b"\xef\xbb\xbfprint('ok')\n")
    bulgular = denetim._dosya_ihlalleri(hedef, tmp_path)
    assert ("utf8_bom", "ornek.py") in bulgular
    assert not any(kod == "utf16" for kod, _ in bulgular)


def test_utf16_bom_tespit(denetim, tmp_path: Path) -> None:
    hedef = tmp_path / "u16.py"
    # utf-16-le codec'i BOM eklemez; BOM'u elle ekle (FF FE)
    hedef.write_bytes(b"\xff\xfe" + "# x\n".encode("utf-16-le"))
    bulgular = dict(denetim._dosya_ihlalleri(hedef, tmp_path))
    assert "utf16" in bulgular  # UTF-16 dosyada compile kategorisi atlanir


def test_nul_bayti_tespit(denetim, tmp_path: Path) -> None:
    hedef = tmp_path / "nul.py"
    hedef.write_bytes(b"print('a')\x00print('b')\n")
    assert "nul" in dict(denetim._dosya_ihlalleri(hedef, tmp_path))


def test_sifir_bayt_py_ihlal(denetim, tmp_path: Path) -> None:
    bos_modul = tmp_path / "bos.py"
    bos_modul.write_bytes(b"")
    assert ("bos", "bos.py") in denetim._dosya_ihlalleri(bos_modul, tmp_path)
    paket = tmp_path / "__init__.py"
    paket.write_bytes(b"")  # paket isaretcisi istisnasi
    assert not any(kod == "bos" for kod, _ in denetim._dosya_ihlalleri(paket, tmp_path))


def test_compile_hatasi_tespit(denetim, tmp_path: Path) -> None:
    hedef = tmp_path / "bozuk.py"
    hedef.write_bytes(b"def f(:\n")
    assert "compile" in dict(denetim._dosya_ihlalleri(hedef, tmp_path))


def test_tarama_tmp_kok(denetim, tmp_path: Path) -> None:
    """tara() mantigi: tmp kok altinda bilinen ihlali bulur, temizi atlamaz."""
    (tmp_path / "bomlu.py").write_bytes(b"\xef\xbb\xbfx = 1\n")
    (tmp_path / "temiz.py").write_bytes(b"x = 1\n")
    orijinal_kok = denetim.KOK
    try:
        denetim.KOK = tmp_path
        sonuclar = denetim.tara(None)  # kapsam siniri yok: tmp koku gez
    finally:
        denetim.KOK = orijinal_kok
    assert sonuclar.get("utf8_bom") == ["bomlu.py"]


def test_duzelt_yalnizca_bom_strip(denetim, tmp_path: Path, monkeypatch) -> None:
    """--duzelt: BOM'u kaldirir; icerige dokunmaz."""
    bomlu = tmp_path / "bomlu.py"
    bomlu.write_bytes(b"\xef\xbb\xbfx = 1\n")
    monkeypatch.setattr(denetim, "KOK", tmp_path)
    assert denetim.duzelt({"utf8_bom": ["bomlu.py"]}) == ["bomlu.py"]
    assert bomlu.read_bytes() == b"x = 1\n"


def test_allowlist_okuma_ve_yazma(denetim, tmp_path: Path, monkeypatch) -> None:
    allowlist = tmp_path / "kodlama_allowlist.json"
    monkeypatch.setattr(denetim, "ALLOWLIST_YOLU", allowlist)
    assert denetim.allowlist_oku() == {"bom": [], "compile": []}  # dosya yok
    denetim.allowlist_yaz({"bom": ["a.py", "b.py", "a.py"], "compile": ["c.py"]})
    assert json.loads(allowlist.read_text(encoding="utf-8")) == {
        "bom": ["a.py", "b.py"],
        "compile": ["c.py"],
    }
    assert denetim.allowlist_oku() == {"bom": ["a.py", "b.py"], "compile": ["c.py"]}


def test_cikis_kodu_ihlalda_bir(denetim, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(denetim, "KOK", tmp_path)
    assert denetim.main(["--tam-repo"]) == 0  # tmp bos: temiz
    (tmp_path / "bomlu.md").write_bytes(b"\xef\xbb\xbf# baslik\n")
    assert denetim.main(["--tam-repo"]) == 1  # ihlal: cikis kodu 1


# ------------------------------------------------------------------ ratchet guard


def _kapsam_bulgulari(denetim) -> dict[str, list[str]]:
    """Kapsam dizinlerindeki ihlalleri toplar (.py/.md/.json/.toml/.sql)."""
    sonuclar: dict[str, list[str]] = {}
    for dizin in KAPSAM_DIZINLERI:
        kok_dizin = KOK / dizin
        if not kok_dizin.is_dir():
            continue
        for uzanti in ("*.py", "*.md", "*.json", "*.toml", "*.sql"):
            for yol in sorted(kok_dizin.rglob(uzanti)):
                for kod, detay in denetim._dosya_ihlalleri(yol, KOK):
                    if yol.name == "__init__.py" and kod == "bos":
                        continue  # meşru paket işaretçisi
                    sonuclar.setdefault(kod, []).append(detay)
    return sonuclar


def test_guard_utf16_nul_sifir_bayt_her_zaman_kirmizi(denetim) -> None:
    """UTF-16 / NUL / 0-bayt icin allowlist yok: her zaman kirmizi."""
    bulgular = _kapsam_bulgulari(denetim)
    kotu = bulgular.get("utf16", []) + bulgular.get("nul", []) + bulgular.get("bos", [])
    assert kotu == [], (
        "UTF-16 / NUL / 0-bayt dosyalari bulundu (allowlist kabul etmez): "
        + ", ".join(kotu)
    )


def test_guard_compile_ratchet(denetim) -> None:
    """Derlenemeyen .py: src/tests/web_dashboard'da her zaman kirmizi;
    scripts/ altindakiler yalnizca allowlist['compile'] ile muaf (ratchet)."""
    bulgular = _kapsam_bulgulari(denetim)
    derleme = bulgular.get("compile", [])
    muaf = set()
    if ALLOWLIST_YOLU.is_file():
        muaf = set(json.loads(ALLOWLIST_YOLU.read_text(encoding="utf-8")).get("compile", []))
    kirmizi = [d for d in derleme if d.split("/")[0] != "scripts" or d not in muaf]
    assert kirmizi == [], "Derlenemeyen .py dosyalari (ratchet ihlali): " + ", ".join(kirmizi)


def test_guard_bom_ratchet(denetim) -> None:
    """Allowlist disinda UTF-8 BOM -> kirmizi (ratchet: liste asagi gitmeli)."""
    mevcut_bom = _kapsam_bulgulari(denetim).get("utf8_bom", [])
    allowlist: list[str] = []
    if ALLOWLIST_YOLU.is_file():
        veri = json.loads(ALLOWLIST_YOLU.read_text(encoding="utf-8"))
        allowlist = sorted(veri.get("bom", []))
    disinda = sorted(set(mevcut_bom) - set(allowlist))
    assert disinda == [], (
        "Allowlist disinda UTF-8 BOM'lu dosyalar bulundu (ratchet ihlali): "
        + ", ".join(disinda)
    )
    gereksiz = sorted(set(allowlist) - set(mevcut_bom))
    assert gereksiz == [], (
        "Allowlist'te artik BOM'lu olmayan dosya var (ratchet asagi guncelle): "
        + ", ".join(gereksiz)
    )

