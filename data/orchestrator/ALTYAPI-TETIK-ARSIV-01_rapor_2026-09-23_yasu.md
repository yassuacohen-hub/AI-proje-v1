# ALTYAPI-TETIK-ARSIV-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı (silme yok, sadece taşıma)

## 1. Taşınanlar → `data/orchestrator/triggers/_arsiv_2026-09-23/`

Kanonik ajanlar (kaynak: `trigger.AJANLAR` = ihsan, utku, salih, yasu) dışındaki
11 dosya arşive taşındı. Taşıma öncesi her dosyada açık kayıt (`bekliyor`/`alindi`)
taraması yapıldı:

| Dosya | İçerik Durumu | Karar |
|---|---|---|
| claude_code.jsonl (907B) | açık kayıt yok | ✅ taşındı |
| external_agent.jsonl (594B) | açık kayıt yok | ✅ taşındı |
| gelistirici.jsonl (900B) | açık kayıt yok | ✅ taşındı |
| kalite.jsonl (890B) | açık kayıt yok | ✅ taşındı |
| mimari.jsonl (904B) | açık kayıt yok | ✅ taşındı |
| MVP-KUL-02.jsonl (987B) | açık kayıt yok | ✅ taşındı |
| research_ponytale_caveman.jsonl (310B) | açık kayıt yok | ✅ taşındı |
| arastirmaci.jsonl (0B) | boş | ✅ taşındı |
| copilot.jsonl (0B) | boş | ✅ taşındı |
| cursor_grok.jsonl (0B) | boş | ✅ taşındı |
| web_kazima.jsonl (0B) | boş | ✅ taşındı |

## 2. Taşınmayan (açık kayıt taşıyor)

| Dosya | Açık Kayıt | Gerekçe |
|---|---|---|
| **mimar.jsonl** (1191B) | satır 4: `DASH-UX-02a` — **bekliyor** | Yarım kalmış iş sessizce gömülmedi. Not: DASH-UX-02a görevi pano sahipliğiyle ihsan/utku'ya ait; bu tetik yanlış ajana (mimar) düşmüş eski kayıt. Temizlik kararı orkestratörde (D-77): ya sil ya doğru ajana aktar. |

## 3. Kalanlar (kanonik, değişmedi)

`ihsan.jsonl`, `utku.jsonl`, `salih.jsonl`, `yasu.jsonl`

## 4. Pano Denetimi

`python scripts/pano_denetim.py` → `status=ok hata=0 uyari=11` — taşımadan
önceki uyarı setiyle aynı; **yeni uyari çıkmadı**. (Mevcut 11 uyarı önceden
bilinen stuck/kuyruk/orphan kayıtları, bu görevin kapsamı dışında.)

## 5. Ek Bulgu: data_worktree Kopyaları (karar orkestratörde — işlem YOK)

`data_worktree/orchestrator/` altında pano kopyası mevcut; **silme/taşıma yapılmadı** (D-172):

- `data_worktree/orchestrator/triggers/` — aynı ALARM/jsonl setinin tam kopyası
- `data_worktree/orchestrator/` içinde 9 `.jsonl` + görev brif/rapor kopyaları
  (ADMIN-UX-LOGOUT-01, ALTYAPI-FORM-SETUP-03, ALTYAPI-PROXY-CONFIG-02,
  ALTYAPI-WEB-MONITOR-01 brif/raporları her iki ağaçta da var)
- `data_worktree/orchestrator/TG-01_rapor_2026-09-18_kilo.md` = `data/orchestrator/` kopyası

**Risk**: iki doğruluk kaynağı. `trigger.py`/`task_board.py` `data/orchestrator/`
(ROOT bazlı) kullanıyor; worktree kopyası pasif görünüyor ama denetim
araçları (vault tarama, mojibake) ikisini de geziyor. Öneri: worktree
kopyasının statüsü orkestratörce netleştirilsin (arşiv mi, aktif mi).

## Araç

- Taşıma scripti: `scripts/_tetik_arsiv_tasi.py` (açık-kayıt korumalı, silme yok)
