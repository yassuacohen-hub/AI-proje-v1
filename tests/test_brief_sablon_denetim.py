"""D-217 denetimi — her YENİ brif kanonik şablonun zorunlu bölümlerini taşır.

Kural: AGENTS.md "D-217 — Tek Brif + Brifte Ajan Chat Zorunlu".
Kanonik şablon tek dosya: plans/_brief_sablon.md (ikinci şablon = D-211 ihlali).

Ratchet (mandal) deseni: D-217 öncesi 113 brif eski formatta. Geriye dönük düzeltmek
değer üretmez — kapanmış işlerin brifi. Bunlar `_brief_baseline.txt`'te dondurulur.
Test iki şeyi garanti eder:
  1. Yeni brif (baseline'da olmayan) zorunlu bölümleri taşır.
  2. Baseline **büyümez** — listeye ekleme yapmak KAHİN kararı gerektirir.

Baseline'ı yenilemek için: python tests/test_brief_sablon_denetim.py --baseline-yaz
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
PLANS = KOK / "plans"
SABLON = PLANS / "_brief_sablon.md"
BASELINE = Path(__file__).resolve().parent / "_brief_baseline.txt"

# D-217 zorunlu bölümler. "## Adımlar" yerine "## Faz A" da kabul (toplu iş).
ZORUNLU = [
    "**Başlık:**",
    "**Öncelik:**",
    "**Hub:**",
    "## Neden",
    "## Doğrulanacak varsayım",
    "## Kabul kriteri",
    "## Ajan chat zorunlu",
    "## Teslim",
    "## Ilgili Nodlar",  # D-218 Obsidyen grafiği — linksiz doküman = grep maliyeti
]

# D-218: en az bu kadar wikilink. Linksiz doküman grafikten kopuk kalır,
# ajan onu bulmak için tüm repoyu tarar (token + süre maliyeti).
MIN_WIKILINK = 2


def _tum_brifler() -> list[Path]:
    return sorted(PLANS.glob("brief_*.md"))


def _baseline() -> set[str]:
    if not BASELINE.is_file():
        return set()
    return {
        s.strip()
        for s in BASELINE.read_text(encoding="utf-8").splitlines()
        if s.strip() and not s.startswith("#")
    }


def _eksikler(brif: Path) -> list[str]:
    metin = brif.read_text(encoding="utf-8")
    eksik = [b for b in ZORUNLU if b not in metin]
    if "## Adımlar" not in metin and "## Faz A" not in metin:
        eksik.append("## Adımlar|## Faz A")
    if "ajan_chat.py" not in metin:
        eksik.append("ajan_chat.py komut referansı")
    if metin.count("[[") < MIN_WIKILINK:
        eksik.append(f"en az {MIN_WIKILINK} Obsidyen wikilink [[...]] (D-218)")
    return eksik


def _yeni_brifler() -> list[Path]:
    eski = _baseline()
    return [p for p in _tum_brifler() if p.name not in eski]


def test_kanonik_sablon_tek():
    """İkiz şablon yasağı (D-211 · D-217)."""
    assert SABLON.is_file(), "plans/_brief_sablon.md yok"
    ikizler = sorted(
        {p.name for p in PLANS.glob("*TEMPLATE*")} | {p.name for p in PLANS.glob("*template*")}
    )
    assert not ikizler, f"ikiz şablon dosyası: {ikizler} — kanonik tek: _brief_sablon.md"


def test_sablon_zorunlu_bolumleri_tanimlar():
    """Şablonun kendisi zorunlu bölümleri içermeli, yoksa kural kağıt üstünde kalır."""
    eksik = _eksikler(SABLON)
    assert not eksik, f"_brief_sablon.md eksik bölüm: {eksik}"


def test_baseline_dosyasi_var():
    assert BASELINE.is_file(), (
        "tests/_brief_baseline.txt yok — "
        "python tests/test_brief_sablon_denetim.py --baseline-yaz ile üret"
    )


def test_baseline_buyumez():
    """Mandal: baseline yalnız küçülür. Yeni uyumsuz brif buraya eklenemez (D-217)."""
    eski = _baseline()
    mevcut = {p.name for p in _tum_brifler()}
    hayalet = sorted(eski - mevcut)
    assert not hayalet, (
        f"baseline'da olmayan dosya var (silinmiş): {hayalet} — baseline'ı yenile"
    )
    assert len(eski) <= 112, (
        f"baseline {len(eski)} kayda çıktı, üst sınır 112 (D-217). "
        "Yeni brif baseline'a eklenmez — şablona uydur."
    )


def test_yeni_brif_var_veya_hepsi_baseline():
    """Glob bozulmasına karşı duman testi."""
    assert _tum_brifler(), "plans/ altında hiç brief_*.md yok — glob bozuk"


@pytest.mark.parametrize("brif", _yeni_brifler(), ids=lambda p: p.name)
def test_yeni_brif_sablona_uyar(brif: Path):
    """D-217 sonrası yazılan her brif kanonik şablonun bölümlerini taşır."""
    eksik = _eksikler(brif)
    assert not eksik, (
        f"{brif.name} eksik bölüm (D-217): {eksik}\n"
        f"Şablon: plans/_brief_sablon.md — baseline'a EKLEME, şablona uydur."
    )


def _baseline_yaz() -> int:
    """Uyumsuz mevcut briflerin listesini dondurur."""
    uyumsuz = sorted(p.name for p in _tum_brifler() if _eksikler(p))
    BASELINE.write_text(
        "# D-217 baseline — bu brifler karar öncesi yazıldı, muaf.\n"
        "# YENİ SATIR EKLEMEK YASAK (test_baseline_buyumez). Şablona uy.\n"
        "# Yenile: python tests/test_brief_sablon_denetim.py --baseline-yaz\n"
        + "\n".join(uyumsuz)
        + "\n",
        encoding="utf-8",
    )
    return len(uyumsuz)


if __name__ == "__main__":
    if "--baseline-yaz" in sys.argv:
        n = _baseline_yaz()
        print(f"baseline yazildi: {n} uyumsuz brif donduruldu -> {BASELINE.name}")
        raise SystemExit(0)

    test_kanonik_sablon_tek()
    test_sablon_zorunlu_bolumleri_tanimlar()
    test_baseline_dosyasi_var()
    test_baseline_buyumez()
    test_yeni_brif_var_veya_hepsi_baseline()
    yeni = _yeni_brifler()
    for b in yeni:
        test_yeni_brif_sablona_uyar(b)
    print(f"OK — {len(yeni)} yeni brif denetlendi, {len(_baseline())} baseline muaf")
