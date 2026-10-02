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
    # Sanal ortam: pip install ettigin her paket kendi .md sablonlarini
    # getirir (huggingface_hub/templates/modelcard_template.md gibi).
    # Bunlar proje sablonu DEGIL; listeye girmeyince Kural 3 yanlis alarm
    # verir ve asil sablon ihlalini gizler (D-220: gurultu gercek alarmi gizlemez).
    ".venv",
    ".venv_test",
    "site-packages",
    "__pycache__",
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


# D-271 — borç başlığı fiil taşımaz. Segment bazlı: "UC" gibi kısa belirteçler
# kelime içinde kaybolmasın diye kimlik "-" ile bölünür, parça karşılaştırılır.
# D-272: kimlik SOLDAN bağlanır. `\b` tireyi sınır saydığı için eski kalıp
# `ALTYAPI-VERI-GORUNURLUK-01` içinden olmayan bir `VERI-GORUNURLUK-01`
# kimliği uyduruyordu — D-270'in aynası, mandalın kendi kör noktası.
BORC_KIMLIK = re.compile(r"(?<![A-Z0-9-])(?:BORC|VERI)-[A-Z0-9-]+-\d{2}\b")
FIIL = {"DUSUR", "DOGRULAMA", "DEDUP", "TEMIZ", "BAG", "SOZLUK", "BETIK"}
SAYI = {"IKI", "UC", "IKIZ", "TEK"}


def _borc_kimlikleri() -> set[str]:
    t = (KOK / "AGENTS.md").read_text(encoding="utf-8")
    return set(BORC_KIMLIK.findall(t))


def _fiilli_sayili() -> tuple[list[str], list[str]]:
    fiilli, sayili = [], []
    for k in sorted(_borc_kimlikleri()):
        parca = set(k.split("-"))
        if parca & FIIL:
            fiilli.append(k)
        if parca & SAYI:
            sayili.append(k)
    return fiilli, sayili


def test_d272_borc_defteri_eksiksiz() -> None:
    """D-272: AGENTS.md'de adı geçen her borç kimliği defterde yazılı olmalı.

    Mandalın yönü tek: AGENTS.md → defter. Tersi (defterde olup AGENTS.md'de
    olmayan) kontrol edilmez, çünkü kapanan borcun D-kaydı silinmez; defter
    AGENTS.md'nin üst kümesi olamaz ama alt kümesi de olmamalı.

    D-270 dersi uygulandı: kimlikler defterde **sabit dize** olarak durur,
    parçadan kurulmaz; iki tarafta aynı BORC_KIMLIK regexi tarar.
    """
    defter = KOK / "docs" / "BORC_DEFTERI.md"
    assert defter.exists(), f"borç defteri yok: {defter}"
    yazili = set(BORC_KIMLIK.findall(defter.read_text(encoding="utf-8")))
    eksik = sorted(_borc_kimlikleri() - yazili)
    assert not eksik, (
        f"AGENTS.md'de adı geçip docs/BORC_DEFTERI.md'de olmayan {len(eksik)} kimlik: "
        f"{eksik}. Borç kapatan/açan D-kaydı aynı turda defteri de güncellemeli."
    )


def test_d271_borc_adinda_fiil_artmiyor() -> None:
    """D-271: borç başlığı ölçülen sapmayı söyler, yapılacak fiili değil.

    Mandal: D-271 anında 8 fiilli + 4 sayılı kimlik vardı. Geriye dönük
    yeniden adlandırma 30+ karar girdisini ve git geçmişini kırar, kazancı
    yok (D-221/1 mantığı). Yeni kimlik kapıda durur; sayı yalnız küçülür.

    Tavan neden 4, 3 değil: bu mandal ilk koşuşta D-271 girdisinin kendisini
    yakaladı. Girdi "`BORC-DEFTER-IKI-SEMA-01` defterde yok" diyordu; bunu
    yazmak kimliği deftere soktu. Dördüncü sayılı kimlik iptal edilmiş bir
    kimliktir — sayıyı mandala uydurmak yerine tavan gerçeğe çekildi.
    """
    fiilli, sayili = _fiilli_sayili()
    assert len(fiilli) <= 8, (
        f"D-271/1: fiil taşıyan borç kimliği {len(fiilli)}, üst sınır 8.\n"
        "Yeni borç adında fiil yasak — yalnız ölçülen sapma yazılır.\n"
        "'nace_name doldur' DEĞİL -> 'nace_name 52/8289 dolu, değerler isim değil'.\n"
        + "\n".join(fiilli)
    )
    assert len(sayili) <= 4, (
        f"D-271/2: sayı sayan borç kimliği {len(sayili)}, üst sınır 4.\n"
        "Ad sayıyı dondurur, ölçüm değiştirir (D-265: 'iki defter' üç çıktı).\n"
        + "\n".join(sayili)
    )


TAVAN = 400          # D-219 Ek (2026-10-02): 200 -> 400
OZ_BOLUM = "\u00a7\u00d6z-ele\u015ftiri"   # kalici ogrenme blogu, tavana dahil DEGIL


def test_d320_ajan_context_dosyalari() -> None:
    """Her ajanin hafiza dosyasi: KALDIĞIM YER + wikilink + 400 satir tavani.

    D-320 DUZELTMESI: onceki test 200 satir ve Oz-eleştiri'yi tavana sayiyordu.
    Iki yanlis vardi:
      1) Tavan 2026-10-02'de Uretim Sahibi karariyla 400'e cikarildi (D-219 Ek).
      2) §Öz-eleştiri KALICI ve tavana DAHIL DEGIL; ajanin ogrendigi ders
         arsiv rotasyonuyla silinmez. Yanlis olcum, ajani dogru davranisindan
         dolayi cezalandirir (ölçüm yaniltmaz, D-260).
    """
    ajanlar = ("ihsan", "utku", "yasu", "salih")
    for a in ajanlar:
        p = KOK / f"{a}_project_context.md"
        assert p.is_file(), f"D-219: {p.name} yok — her ajanin hafiza dosyasi zorunlu"
        t = p.read_text(encoding="utf-8")
        assert "## KALDIĞIM YER" in t, f"D-219: {p.name} §KALDIĞIM YER blogu yok"
        assert "## Ilgili Nodlar" in t, f"D-218: {p.name} §Ilgili Nodlar yok"
        assert t.count("[[") >= 2, f"D-218: {p.name} en az 2 wikilink ister"

        sat = t.splitlines()
        bas = next((i for i, l in enumerate(sat) if OZ_BOLUM in l), len(sat))
        sayilan = bas                     # tavana sayilan kisim
        assert sayilan <= TAVAN, (
            f"D-320: {p.name} {sayilan} satir, tavan {TAVAN} "
            f"(Oz-eleştiri bolumu {len(sat) - bas} satir haric).\n"
            "Eski oturum bloklarini archive/<ajan>_context_<YYYYMM>.md'ye tasi."
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
    fiilli, sayili = _fiilli_sayili()
    print(f"borç kimliği   : {len(_borc_kimlikleri())}")
    print(f"  fiilli       : {len(fiilli)} / üst sınır 8  {fiilli}")
    print(f"  sayılı       : {len(sayili)} / üst sınır 4  {sayili}")
    test_kural1_kanonik_yollar_mevcut()
    test_kural3_sablon_tekligi()
    test_kural4_yasak_ad_kalibi_artmiyor()
    test_d271_borc_adinda_fiil_artmiyor()
    test_d219_ajan_context_dosyalari()
    test_gurultu_orani_raporlanabilir()
    print("D-220 kapisi: OK")
