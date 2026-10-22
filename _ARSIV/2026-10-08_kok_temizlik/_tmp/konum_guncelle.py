# -*- coding: utf-8 -*-
"""D-219 KALDIĞIM YER girişi ekle — tek seferlik, muhafazalı.

apply_diff 6+ kez boşluk (whitespace) uyuşmazlığıyla patladı; write_to_file ise
read_file'ın 2000 karakter kırpması nedeniyle satır 19/24 kuyruğunu yok ederdi.
Bu betik dosyanın geri kalanına DOKUNMAZ; yalnız satır 7-8 (iki boş satır)
sonrasına yeni Konum girişini ekler.

Kullanım: python ..\\_tmp\\konum_guncelle.py  (her yerden koşabilir, yol absolute)
"""
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent  # workspace kökü
DOSYA = KOK / "Huginn Data Insights" / "ihsan_project_context.md"

ETIKET = "2026-10-10 20:00"

YENI = (
    "- **Konum (2026-10-10 20:00 — VERI-TOBB-HAVUZ-SEMA-01 TESLİM (review, `baad4849`) — "
    "Faz A→F BİTTİ; rapor verildi; KENDİ KARARI: yeni oturum watchdog turuyla başlar, onay beklenmez):** "
    "Faz A canlı ölçümünün öğrettikleri: 132/132 TOBB alanı `alan_sozlugu.sira_no` 1–132 birebir sırada, "
    "1 ham kaynak, seed bekleyen 5 sözlük (8 tablo 0 satır). İnşa edilenler: göçler 0055–0059 "
    "(havuz, sözlük seed, `company_persons`, `companies` TOBB kolonları, adres/hukuk/gazete) + "
    "tek kapı `etl/tobb_alan_haritasi.py` + mandallar + 7 test + RLS 13 tablo; tam yedek → `restore_test` "
    "10123/138/59 eşleşti. **TOBB eşleşme = TAM** (D-357 ikiz kopya): `tobb_kart_ham.tobb` TOBB'un kendi "
    "alan adlarıyla aynen + `tobb_yedek` 133 + 134+ `blok='huginn'`. **Kalan tek TOBB/DB işi**: 7 sözlük "
    "tablosunun (`nevi_grup`, `nevi_grubu_kodu`, `tsm_listesi`, `sehir_listesi`, `temsil_gorevi`, "
    "`temsil_yetki_sekli`, `temsil_turu`) seed verisi — `VERI-TOBB-SIRKETKARTI-MANTIK-01` brifine Adım "
    "olarak eklendi (yasu, kuyruk); `ALTYAPI-TOBB-SABIT-IP-01` bağımsız (yasu, kuyruk). Yeni görev "
    "açılmadı (D-217 tek brif); `docs/BORC_DEFTERI.md` yazılmadı — yeni borç yok, kalan iş panoda görev "
    "olarak duruyor (D-272); `docs/SSOT_ILERLEME_MATRISI.md` yazılmadı — elle yazım yasak, yalnız "
    "`scripts/ssot_ilerleme.py` ölçer (D-326/D-197). PO başlangıç-prompt şablonu raporda sunuldu. "
    "**ŞİMDİ (kendi kararım, PO guidance 2026-10-10):** yeni oturum watchdog turuyla başlar: "
    "(1) `python scripts/ajan_chat.py ozet --durum acik` (oturumun İLK komutu, kalıcı öz-eleştiri kuralı), "
    "(2) `python scripts/gorev_kutusu.py nobet --ajan ihsan`, (3) `VERI-TOBB-HAVUZ-SEMA-01` review "
    "kuyruğunda — PO kabul bekler; kritik blokaj yoksa `## Yapılacaklar` ilk açık madde."
)


def main() -> int:
    metin = DOSYA.read_text(encoding="utf-8")
    satirlar = metin.splitlines(keepends=True)
    if ETIKET in metin:
        print("SKIP: giris zaten var, ikinci kez eklenmedi")
        return 0
    # muhafazalı bekçiler (ölçmeden yazma — D-260)
    assert satirlar[3].startswith("## KALDIĞIM YER"), "satir 4 beklenmeyen"
    assert satirlar[5].startswith("> D-219:"), "satir 6 beklenmeyen"
    assert satirlar[6].strip() == "" and satirlar[7].strip() == "", "satir 7-8 bos degil"
    assert satirlar[8].lstrip().startswith("- **Konum (2026-10-10 06:45"), "satir 9 beklenmeyen"
    satirlar[6:8] = ["\n", YENI + "\n", "\n"]
    DOSYA.write_text("".join(satirlar), encoding="utf-8")
    yeni_sayim = len("".join(satirlar).splitlines())
    print(f"OK satir_sonrasi={yeni_sayim} (tavan 400)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
