# Proje Denetimi — 2026-09-09 (Koordinatör Ajan)

Bağlantılar: [[00-Home]] · [[project_state]] · [[TODO]] · `AGENTS.md` · `AGENT_SYNC.md`

> Kaynak görev: `data/orchestrator/task_board.json` → `DENET-*` görevleri.
> Bu belge, çalışma alanının genel sağlık denetimi sonucunda bulunan eksik/hata/riskleri ve yapılan/planlanan düzeltmeleri **tüm ajanların** görebileceği tek noktada toplar.

## Yapılan Düzeltmeler (Tamamlandı)

| # | Bulgu | Düzeltme | Etkilenen Dosyalar |
|---|-------|----------|---------------------|
| DENET-2 | Birden fazla dosyada Türkçe karakter bozulması (mojibake, cp1254/utf-8 karışımı) | Bozuk bayt dizileri UTF-8'e düzeltildi | `AGENTS.md`, `AGENT_SYNC.md`, `CHANGELOG.md`, `AI proje v1/V10/project_state.md` |
| DENET-3 | `AGENTS.md` içinde "VPN Kullanım Kuralı" ve "Ajan Kılavuzu" bölümleri iki kez tekrarlanmış, biri bozuk kodlamalı | Tekilleştirildi; ayrıca **"Görev Panosu ve Dosya Kilidi" bölümü eklendi** (bkz. aşağıda) | `AGENTS.md` |

## Yeni Kural: Görev Panosu + Dosya Kilidi Zorunluluğu

`src/company_master/orchestrator/task_board.py` içinde zaten canlı bir görev panosu + dosya kilidi (file lock) mekanizması mevcuttu ama `AGENTS.md`'de zorunlu kural olarak tanımlı değildi. Artık **tüm ajanlar için zorunlu**:

- İşe başlamadan önce `data/orchestrator/task_board.json` / `gorev_panosu.md` ve `data/orchestrator/file_locks.json` kontrol edilir.
- Görev, `gorev_ekle(task_id, baslik, sahip, dosyalar=[...])` ile açılır — bu, verilen dosyaları otomatik kilitler.
- Kilitli bir dosyaya başka sahip erişmeye çalışırsa `PermissionError` alır (çakışma otomatik engellenir).
- İş bitince `gorev_guncelle(..., durum="done")` + `lock_birak(...)` çağrılır.
- Detay: `.\Huginn Data Insights\AGENTS.md` → "Görev Panosu ve Dosya Kilidi (Çakışma Önleme) — ZORUNLU" bölümü.

## Açık Bulgular / Kararlar (2026-09-09 düzeltme sonrası)

| # | Bulgu | Aksiyon | Durum |
|---|-------|---------|-------|
| DENET-1 | Proje kökünde **git deposu yok** | `git init` + ilk commit (kullanıcı onayı ile) | blocked (onay bekliyor) |
| DENET-4 | Geçici/deneme dosyaları (`check_payload_diag*.py`, `_tmp*.py`, `_probe*.py`, `_test*.py`, `temp_match_stats.py`, `--help`, `.canvas`/`.md` boş dosyalar) | `cop_kutusu_2026_09_09/DENET_arsiv_2026_09_09/scripts_gecici/` altına taşındı; 35MB `ingest_ostim_detail.log` → `.gz` (0.65MB) | done |
| DENET-5 | `c:\Projeler\Huginin Data Insights` (yazım hatalı) klasörü | İçinde yalnızca **1 bayt** `scripts` dosyası vardı; gerçek veri yok → klasör kaldırıldı | done |
| DENET-6 | `project_state.md` / `_iso.md` / `_utf8.md` — 3 kopya | `project_state.md` **tek kaynak** ilan edildi (UTF-8 doğru); `_iso`/`_utf8` mojibake kopyaları arşive taşındı | done |
| DENET-7 | Kökte `company_master.db` (2.5MB), `test.db` (2.64MB) SQLite; asıl DB Supabase | Eski yerel kopyalar (8313 kayıt, 09/02-09/07) → arşive taşındı; `backups/company_master_pre_dedup_*.db` yedeği yerinde bırakıldı; `data/ankara_osb.db` (0B) arşivlendi | done |

## Zaten Bilinen / Panoda Takip Edilen Riskler (Tekrar Not)

- **KVKK / VKN-e-posta görünürlüğü** — görev `Y7` (arastirmaci, plan) zaten panoda; bu denetim yalnızca teyit eder, yeni görev açılmadı.
- **Kaynak çeşitliliği / iş ilanı / çalışan sayısı metrikleri hâlâ 0 puan** — `project_state.md` "Sonraki Adımlar" bölümünde zaten kayıtlı.

## Not

Tüm `DENET-*` görevlerinin güncel durumu için `data/orchestrator/gorev_panosu.md` veya `AGENT_SYNC.md` → "Aktif İşler" tablosuna bakın.
