#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Task board'u guncelle ve harici ajanlara bildirim gonder."""
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-3: ASO ingest - devam ediyor
tb.gorev_guncelle("P1-3", durum="aktif", **{"not": "ASO ingest devam ediyor. 450/785 kayit islendi, 0 hata. DB toplam: 8637 firma."})
tb.handoff_yaz("P1-3", "ASO ingest devam ediyor (450/785)", "ASO ingest tamamlaninca kalite recalc yapilacak")

# P1-4: Multi-OSB merger - plan
tb.gorev_guncelle("P1-4", durum="plan", **{"not": "Plan dosyasi hazir, kodlamaya hazir."})
tb.handoff_yaz("P1-4", "Multi-OSB merger plani hazir", "Kodlama baslayacak")

# P1-5: NACE eksikleri - plan
tb.gorev_guncelle("P1-5", durum="plan", **{"not": "1266 firma NACE eksik. Araştırma gerekli."})
tb.handoff_yaz("P1-5", "NACE eksikleri araştırılıyor", "1266 firma için sektör eşleştirme")

# P1-6: Telegram bot - plan
tb.gorev_guncelle("P1-6", durum="plan", **{"not": "Systemd unit hazir, servis olarak kurulmadi."})
tb.handoff_yaz("P1-6", "Telegram bot plan fazinda", "Servis kurulumu gerekiyor")

# P2-1: MERSIS API - plan
tb.gorev_guncelle("P2-1", durum="plan", **{"not": "API basvurusu takibi devam ediyor."})
tb.handoff_yaz("P2-1", "MERSIS API takibi devam ediyor", "API entegrasyonu bekliyor")

# P2-2: State dashboard - done (yukarida olusturduk)
tb.gorev_guncelle("P2-2", durum="done", **{"not": "Streamlit dashboard app.py ile olusturuldu. Port 8501'de calisiyor."})
tb.handoff_yaz("P2-2", "Streamlit dashboard tamamlandi", "Gorsel arayuz hazir")

# P2-3: Zamanlanmıi scrape - plan
tb.gorev_guncelle("P2-3", durum="plan", **{"not": "Gunluk refresh icin cron/systemd timer planlanacak."})
tb.handoff_yaz("P2-3", "Zamanlanmis scrape planlanacak", "Cron kurulumu")

# P2-4: Entity resolution - plan
tb.gorev_guncelle("P2-4", durum="plan", **{"not": "Rapidfuzz threshold optimizasyonu yapilacak."})
tb.handoff_yaz("P2-4", "Entity resolution threshold optimizasyonu", "Threshold ayarlanacak")

# P2-5: Iç ajan oto atama - plan
tb.gorev_guncelle("P2-5", durum="plan", **{"not": "oto_atama.py ile task_board -> state.json senkronizasyonu."})
tb.handoff_yaz("P2-5", "İç ajan otomatik görev atama", "Oto_atama.py kodlanacak")

# AGENT_SYNC guncelle
tb.agent_sync_yaz()
print("Task board guncellendi!")
