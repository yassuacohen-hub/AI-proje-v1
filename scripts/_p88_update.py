# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
ROOT = Path('C:/Projeler/Huginn Data Insights')
sys.path.insert(0, str(ROOT / 'src'))
from company_master.orchestrator import task_board as tb
now = '2026-09-09T20:40:00'
tb.gorev_guncelle('P8-8', durum='done', bitis=now, **{
    'not': 'Kurumsal rapor ve medya entegrasyonu tasari tamamlandi. KAP, Resmi Gazete, haber kaynaklari, sosyal medya sinyalleri ile ilan verisi zenginlestirme stratejisi: data/orchestrator/p88_result.json'
})
tb.handoff_yaz('P8-8', 'Kurumsal rapor ve medya entegrasyonu tasari tamamlandi', 'P8-9/medya_pipeline', 'Medya entegrasyonu MVP once P8-9 gorulmeli')
tb.agent_sync_yaz()
print('P8-8 kapatildi')
