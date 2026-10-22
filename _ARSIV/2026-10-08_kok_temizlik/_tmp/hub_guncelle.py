# -*- coding: utf-8 -*-
"""Hub TOBB satirini ve Kapanan isler tablosunu gunceller (B-14 kapisi)."""
from pathlib import Path

p = Path("Huginn Data Insights/hubs/VERI_KALITESI_HUB.md")
txt = p.read_text(encoding="utf-8")

eski = (
    "- [[Huginn Data Insights/plans/brief_ihsan_VERI-TOBB-HAVUZ-SEMA-01]] — "
    "**ONAY BEKLİYOR** (2026-10-10): havuz şeması 0055–0058, "
    "`tobb_kart_ham(tobb_yedek)`, `alan_sozlugu` 132+1+huginn, "
    "tek kapı `tobb_alan_haritasi.py`, 7 assert mandal"
)
yeni = (
    "- [[Huginn Data Insights/plans/brief_ihsan_VERI-TOBB-HAVUZ-SEMA-01]] — "
    "**TAMAMLANDI** (2026-10-10, commit `9c52b43e`): havuz şeması 0055–0058, "
    "`tobb_kart_ham(tobb_yedek)`, `alan_sozlugu` 132+1+huginn, "
    "tek kapı `tobb_alan_haritasi.py`, 7 assert mandal, RLS 13 tablo, "
    "yedek+geri yükleme testi doğrulandı"
)
assert eski in txt, "TOBB brif satiri bulunamadi"
txt = txt.replace(eski, yeni)

marker = "## Kapanan isler\n"
assert marker in txt, "Kapanan isler basligi bulunamadi"
yeni_satir = (
    "| VERI-TOBB-HAVUZ-SEMA-01 | TOBB Şirket Kartı havuz şeması uçtan uca kuruldu: "
    "goç 0055-0059 (`tobb_kart_ham`, `alan_sozlugu` 132 TOBB + 1 yedek + huginn bloğu), "
    "down migration + seed + tek-kapı eşleştirici [[Huginn Data Insights/src/company_master/etl/tobb_alan_haritasi]] "
    "(7 assert mandal), RLS 13 tablo, [[Huginn Data Insights/tests/test_tobb_alan_haritasi]] yeşil. "
    "Faz A canlı ölçüm: 132/1/5 (TOBB/yedek/huginn alan sayısı). Tam yedek "
    "`backups/supabase_20261010_122308.sql.gz` + yerel kopya + `restore_test` DB geri yükleme "
    "testi doğrulandı (firma/tobb_kart_ham/alan_sozlugu satır sayıları 10123/138/59 birebir eşleşti). "
    "Rapor: `data/orchestrator/VERI-TOBB-HAVUZ-SEMA-01_rapor_2026-10-10_ihsan.md` | 2026-10-10 |\n"
)
txt = txt.replace(marker, marker + yeni_satir, 1)
p.write_text(txt, encoding="utf-8")
print("OK")
