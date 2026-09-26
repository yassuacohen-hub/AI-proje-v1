"""D-220 doküman sıkılaştırma kapısı.

Politika yazı olarak kalmasın: yeni ihlal girişini kapıda durdurur.
Mevcut ihlaller mandal (ratchet) ile dondurulur — sayı yalnız küçülür.

Tek başına da koşar:  python tests/test_dokuman_politikasi.py
"""

from __future__ import annotations

import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent

# D-220 Kural 2 — arama kapsamı dışı. Üçüncü parti skill, worktree kopyası, yedek.
GURULTU = (
    ".git",
    ".agents",
    ".kilo",
    ".claude",
    ".pytest_cache",
    "data_worktree",
    "backups",
    "node_modules",
    "archive",
    "data\\skills",
    "data/skills",
    "_ARSIV",
    "worktree klasoru",
)

# D-220 Kural 4 — git geçmişi bu işi yapar, dosya adı yapmaz.
YASAK_AD = re.compile(
    r"(_|-)(eski|yeni|kopya|copy|final|old|new|draft|backup|v\d+)(\.|_|-|$)", re.I
)

# D-220 Kural 3 — tür başına TEK şablon. Liste kapalı; yeni satır KAHİN kararı ister.
KANONIK_SABLONLAR = {
    "plans/_brief_sablon.md",  # görev brifi (D-217)
    "_ajan_context_sablon.md",  # ajan oturum hafızası (D-219)
    "chat_brief_template.md",  # telegram/chat mesajı
    "completion_report_template.md",  # tamamlama raporu
    "docs/VAULT_AUTOMATION_TEMPLATE.md",
    "AI proje v1/V10/templates/ADR-template.md",
    "AI proje v1/V10/templates/Bug-template.md",
    "AI proje v1/V10/templates/Spec-template.md",
    "AI proje v1/V10/03_mimari/brifler/00_sablon.md",  # mimari öneri brifi ≠ görev brifi
}

# D-220 Kural 1 — her türün tek yaşam yeri.
KANONIK_YOLLAR = (
    "AGENTS.md",
    "plans/_brief_sablon.md",
    "_ajan_context_sablon.md",
    "ihsan_project_context.md",
)


def _kanonik_md() -> list[Path]:
    return [
        p
        for p in KOK.rglob("*.md")
        if not any(g in str(p) for g in GURULTU)
    ]


def _bagil(p: Path) -> str:
    return p.relative_to(KOK).as_posix()


def test_kural1_kanonik_yollar_mevcut() -> None:
    eksik = [y for y in KANONIK_YOLLAR if not (KOK / y).is_file()]
    assert not eksik, f"D-220 Kural 1: kanonik yol kayıp -> {eksik}"


def test_kural3_sablon_tekligi() -> None:
    bulunan = {
        _bagil(p) for p in _kanonik_md() if re.search(r"(sablon|template)", p.stem, re.I)
    }
    yeni = bulunan - KANONIK_SABLONLAR
    assert not yeni, (
        "D-220 Kural 3: kayıtsız şablon açılmış -> "
        f"{sorted(yeni)}\nŞablon yetersizse mevcudu düzelt; yenisi KAHİN kararı ister (D-211)."
    )


def test_kural4_yasak_ad_kalibi_artmiyor() -> None:
    ihlal = sorted(_bagil(p) for p in _kanonik_md() if YASAK_AD.search(p.stem))
    # Mandal: D-220 anında 15 ihlal vardı. Geriye dönük düzeltmek değer üretmez;
    # yeni ihlal girişi kapıda durur. Sayı yalnız küçülür.
    assert len(ihlal) <= 15, (
        f"D-220 Kural 4: yasak ad kalıbı {len(ihlal)} dosyada, üst sınır 15.\n"
        f"Yeni ihlal: _eski/_yeni/_kopya/_final/_v2 yasak — git geçmişi bu işi yapar.\n"
        + "\n".join(ihlal)
    )


def test_d219_ajan_context_dosyalari() -> None:
    """Her ajanın hafıza dosyası: §KALDIĞIM YER + wikilink + 200 satır tavanı."""
    ajanlar = ("ihsan", "utku", "yasu", "salih")
    for a in ajanlar:
        p = KOK / f"{a}_project_context.md"
        assert p.is_file(), f"D-219: {p.name} yok — her ajanın hafıza dosyası zorunlu"
        t = p.read_text(encoding="utf-8")
        assert "## KALDIĞIM YER" in t, f"D-219: {p.name} §KALDIĞIM YER bloğu yok"
        assert "## Ilgili Nodlar" in t, f"D-218: {p.name} §Ilgili Nodlar yok"
        assert t.count("[[") >= 2, f"D-218: {p.name} en az 2 wikilink ister"
        satir = len(t.splitlines())
        assert satir <= 200, (
            f"D-219: {p.name} {satir} satır, tavan 200. "
            "Eski oturum bloklarını archive/<ajan>_context_<YYYYMM>.md'ye taşı."
        )


def test_gurultu_orani_raporlanabilir() -> None:
    """Gürültü oranı ölçülebilir kalsın; politika sayı üzerinden tartışılır."""
    tum = len(list(KOK.rglob("*.md")))
    kanonik = len(_kanonik_md())
    assert kanonik > 0 and kanonik <= tum
    assert kanonik < tum, "gürültü filtresi hiçbir şeyi dışlamıyor — GURULTU listesi bozuk"


if __name__ == "__main__":
    tum = len(list(KOK.rglob("*.md")))
    kanonik = _kanonik_md()
    ihlal = sorted(_bagil(p) for p in kanonik if YASAK_AD.search(p.stem))
    print(f"toplam md      : {tum}")
    print(f"kanonik md     : {len(kanonik)}  (gürültü {tum - len(kanonik)})")
    print(f"yasak ad ihlali: {len(ihlal)} / üst sınır 15")
    for y in ihlal:
        print("  -", y)
    test_kural1_kanonik_yollar_mevcut()
    test_kural3_sablon_tekligi()
    test_kural4_yasak_ad_kalibi_artmiyor()
    test_d219_ajan_context_dosyalari()
    test_gurultu_orani_raporlanabilir()
    print("D-220 kapisi: OK")
