"""VERI-TSG-ESLEME-CASE-01 kapanış kaydını hub'a ekler (idempotent).

Satır metni kanonik kayıttır; kayıt zaten varsa hiçbir şey yazılmaz
(D-243: "var" demek için diske bakılır, varsayılmaz).
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HUB = Path("hubs/OSINT_VERI_TOPLAMA_HUB.md")

SATIR = (
    "| VERI-TSG-ESLEME-CASE-01 | **Varsayim olculdu ve yanlis bulundu; canli tablo "
    "geri dolduruldu.** Brif'in `306/326 NULL` iddiasinin gercek sebebi eslesme "
    "baskarisizligi degil, **306 kanit dosyasinin `il_turu` alaninin bos olmasi**; "
    "bu kayitlarda etiketlenecek metin yok. Eski katlama turkce harfleri "
    "(`ı ş ğ ü ö ç`) sessizce yutuyordu: `Artirimı`->`ARTRM`, `Sube Acilis`->`SUBE ACLS`. "
    "`_TR_ASCII` harf eslemeleri duzeltildi, `ILAN_TURU_ESLEME` **olculmus 17 tam "
    "`il_turu` degeriyle** tanimlandi. Kanitta etiketlenen 13 -> **20** (+7). "
    "**Ikinci katman (D-261: kod yazildi != kosturuldu):** eski esleme canli "
    "`company_events` tablosuna yazilmisti; `tsg_yazici` `source_guid`'i mevcut "
    "sayip atladigi icin (407/407) yeniden kosmak **hicbir sey duzeltmezdi**. "
    "Olcum: **19 satiri** duzeltilecek, yedek `yedekler/company_events_esleme_20261002.jsonl` "
    "(19 satir) alindi, sonra uygulandi: `event_type IS NULL` **404 -> 387**. "
    "Bos `il_turu` kayitlari dogru olarak NULL kaldi. Idempotency kaniti: ikinci kosu "
    "**0 yazilacak**. Zincir kaniti: 326 kanit dosyasi -> 0 hata. Test "
    "**75 passed** (5 yeni mandal: geri dosyasi degeri gozlemez, prova yazmaz). "
    "Kanit dosyalari: `scripts/tsg_esleme_geri_doldurma_olcumu.py`, "
    "`scripts/tsg_esleme_geri_doldur.py`, `scripts/tsg_esleme_mandal_kirma_denemesi.py`. | "
    "2026-10-02 |"
)


def main() -> int:
    if not HUB.exists():
        print(f"HATA: hub yok: {HUB}")
        return 1

    metin = HUB.read_text(encoding="utf-8")
    if "VERI-TSG-ESLEME-CASE-01" in metin:
        print("Zaten kayitli - hicbir sey yazilmadi (idempotent)")
        return 0

    satir = SATIR + "\n"
    if not satir.endswith("|\n"):
        satir = SATIR + " |\n"

    satirlar = metin.splitlines(keepends=True)
    # Kapanış tablosunun **son satırını** bul ("Kapanan işler" başlığından
    # sonraki tablo bloğunun sonu). Kayıt dosyanın başına değil, tabloya girer —
    # dosyanın tepesine yazmak tabloyu koparır.
    bas = next(
        (i for i, s in enumerate(satirlar) if s.strip().startswith("## Kapanan")),
        None,
    )
    if bas is None:
        print("HATA: '## Kapanan ...' bolumu bulunamadi")
        return 1

    son = bas
    for i in range(bas + 1, len(satirlar)):
        if satirlar[i].startswith("## "):
            break
        if satirlar[i].startswith("|"):
            son = i

    if not satirlar[son].rstrip().endswith("|"):
        print(f"HATA: son tablo satiri beklenmedik: {satirlar[son]!r}")
        return 1

    satirlar.insert(son + 1, satir)
    HUB.write_text("".join(satirlar), encoding="utf-8")
    print(f"Kapanis kaydi eklendi: {HUB} (tablo sonu, satir {son + 1})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
