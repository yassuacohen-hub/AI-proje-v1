@echo off
python "Huginn Data Insights\scripts\gorev_kutusu.py" ekle --task-id YENI-PARSEL-KAYNAK-LISTESI-01 --baslik "[VERI] Yeni parsel kaynak listesi (veri çekmez)" --sahip yasu --oncelik P3 --dosyalar docs/raporlar/OSBUK-OSBLISTESI-01_veri_seti_2026-10-21.md --brief plans/brief_yasu_YENI-PARSEL-KAYNAK-LISTESI-01.md --talimat "Yeni parsel kaynak listesi çıkar, veri çekme" --mod code
