# Rapor: ORKESTRA-STALE-TEMIZLIK-01
# Tarih: 2026-09-20
# Ajan: yasu

## Ne yapıldı
- Görev panosu dosyası (`data/orchestrator/task_board.json`) okundu, aktif/plan görevler belirlendi.
- Tüm ajan tetik kuyrukları (`data/orchestrator/triggers/*.jsonl`) tarandı; 24 saatten eski `alindi` durumlu kayıtlar arandı ancak orphan (teslim/done olmayan) kayıt bulunamadı.
- `data/orchestrator/decision_log.jsonl` dosyası okundu; UTF-8 geçersiz bayt (satır 86) bulundu ve raporlandı. Ayrıca duplicate karar girdileri ve bir kendine-yönelik rotasyon (kimden==kime) tespit edildi.
- `data/orchestrator/file_locks.json` dosyası okundu; görev panosunda `done` veya `iptal` durumundaki görevlere ait kilitler tespit edildi ve raporlandı.
- `python scripts/gorev_kutusu.py bakim` komutu çalıştırıldı; çıktı alınıp rapora eklendi.
- Test süiti çalıştırıldı; sonuçlar aşağıda raporlandı.

## Değişen dosyalar
- `data/_tmp/stale_audit.py` (geçici analiz scripti)
- `data/orchestrator/ORKESTRA-STALE-TEMIZLIK-01_rapor_2026-09-20_denetim.md` (bu rapor dosyası)

## Test sonuçları
- `python scripts/gorev_kutusu.py bakim` → `[BAKIM] uygulandi: dedupe: 0 | tetik esit: 0 | blokaj acilan: yok | blokaj kapanan: yok`
- `python -X utf8 -m pytest tests/ -q` → **1 failed, 3972 passed, 22 skipped** (47.35s). Tek failure: `tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db` — `sqlite3.OperationalError: no such table: job_postings`. Bu, mevcut bilinen DB şeması kaynaklı pre-existing failure'dır; yeni failure oluşmadı.

## Bulgular
- 🔴 **Kilitli dosyalar tamamlanmış görevlerde hâlâ kilitli**: `src/company_master/search/engine.py` (V10-HIJYEN-01, done), `tests/test_search_engine_where.py` (V10-HIJYEN-01, done), `src/company_master/search/fulltext.py` (V10-HIJYEN-02, done). Ortalama süre >2 gün; kilit bırakılmamış.
- 🟡 **Decision log UTF-8 bozulması**: `data/orchestrator/decision_log.jsonl` satır 86'da geçersiz bayt (0x87) tespit edildi; dosya bozuk, okuma hatası riski.
- 🟡 **Decision log duplicate kararlar**: 
  - `'orkestrator_rotasyonu'` x2 (satır 7 ve 12)
  - `'AI-CI-01: Anthropic x GitHub entegrasyonu'` x2 (muhtemelen yanlış kopyalama)
- 🔵 **Kendine yönelik orkestratör rotasyonu**: decision log satır 7: `{"action": "orkestrator_rotasyonu", "kimden": "cline", "kime": "cline", ...}`; KIMDEN ve KIME aynı, rol geçişi anlamı dimin.
- 🟢 **Bulgu defteri kontrolü**: `data/orchestrator/bulgu_defteri.md` içindeki tüm bulguların karar alanı dolu; işlenmemiş bulgu yok.

## Eksik / erteleme
- Kilitli dosyaların kilidi terk edilmesi gereklidir, ancak bu işlem kilit sahibi ajanı (roo) tarafından yapılmalıdır. Yasu kilidi terk edemez.
- Decision log dosyasının UTF-8 bozulması düzeltilmeli; ya da geri yüklenmeli veya temizlenmeli.
- Duplicate karar girdileri incelenip tekilleştirilmeli; karar geçmişi tutarlılığı için gerekli.
- Kendine yönelik rotasyon kaydının neden olması incelenmeli; olası yanlış veri girişi.
