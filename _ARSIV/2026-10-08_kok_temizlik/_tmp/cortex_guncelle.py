# -*- coding: utf-8 -*-
"""Cortex KALDIGIM YER'e yeni giris ekler (en uste, eski silinmez). D-219."""
from pathlib import Path

p = Path("Huginn Data Insights/ihsan_project_context.md")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

# satir 7 bos satir, satir 8 (index 7) eski en-yeni giris -> onun ONCESINE ekle
yeni = (
    "- **Konum (2026-10-10 14:20 — VERI-TOBB-HAVUZ-SEMA-01 TAMAMLANDI, teslime hazir, "
    "commit `9c52b43e` + sonraki):** Emrin 6 maddesi bitti: (1) gorev ihsan'a atandi, "
    "APIVOM iptal (PO karari, `apivom_vkn.py` SILINMEDI -- rakip istihbarati notu); "
    "(2) TEST-ODIN-HAKEM-ESIK-01 ONAY, TEST-ODIN-PROMPT-INJECTION GERI GONDER (3 somut madde); "
    "(3) onay kuyrugu bos, nobet_modu kuruldu; (4) Faz A canli olcum 132/1/5 (TOBB/yedek/huginu "
    "alan sayisi) + seed betigi; (5) DB insa: goc 0055-0059 + down + seed + mandal + 7 test + "
    "RLS 13 tablo, commit `9c52b43e`; (6) tam yedek `backups/supabase_20261010_122308.sql.gz` "
    "+ yerel kopya + geri yukleme testi (`restore_test` DB, firma/tobb_kart_ham/alan_sozlugu "
    "satir sayilari 10123/138/59 ile birebir eslesti). Brif kabul kriteri (Faz A-F) [x] tamam. "
    "Hub [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] 'Kapanan isler'e eklendi. Nihai rapor: "
    "`data/orchestrator/VERI-TOBB-HAVUZ-SEMA-01_rapor_2026-10-10_ihsan.md`. **SIMDI:** "
    "`gorev_kutusu.py teslim` + `nobet` calistir, degisen dosyalari commit et, PO'ya Turkce "
    "ozet rapor teslim et.\n\n"
)

lines.insert(7, yeni)
p.write_text("".join(lines), encoding="utf-8")
print("OK, yeni satir sayisi:", len(lines))
