# VERI-SEMA-DOGRULA-02 — Eksik Tablolar Kod Taraması

**Ölçen:** ihsan (orkestratör devralma, D-58) · **Ajan:** yasu
**Tarih:** 2026-10-01 · **Kurallar:** D-222 · D-238 · D-260

## Sonuç

İki tablo da **şemada var ve kodda okunuyor**; hiçbir yerde yazılmıyor (INSERT yok).
SEMA-DENETIM-01'in "kodda var şemada yok" iddiası **doğrulanmadı** — canlı ölçümde ikisi de mevcut.

## entity_matches

| Dosya | Satır | İşlem | Koşul |
|---|---|---|---|
| [`threshold_optimizer.py`](../src/company_master/entity_resolution/threshold_optimizer.py:31) | 31 | SELECT COUNT(*) | `match_type = 'fuzzy'` |
| [`threshold_optimizer.py`](../src/company_master/entity_resolution/threshold_optimizer.py:44) | 44 | SELECT COUNT(*) | `match_type = 'fuzzy'` |

- Referans sayısı: **1 dosya, 2 sorgu**
- INSERT/UPDATE/DELETE: **yok**
- Okunan sütunlar: `match_type`, `similarity_score`, `created_at`
- Beklenen sütunlar: `match_id`, `company_id`, `source_id`, `match_type`, `similarity_score`, `created_at`

## api_usage_daily

| Dosya | Satır | İşlem | Not |
|---|---|---|---|
| [`admin_kpi.py`](../web_dashboard/tabs/admin_kpi.py:108) | 108 | `tablo_var_mi()` varlık kontrolü | UI-ADMIN-SAHTE-KPI-01: tablo yoksa 0 değil **rozet** gösterir |
| [`admin_kpi.py`](../web_dashboard/tabs/admin_kpi.py:115) | 115 | `SELECT SUM(request_count)` | toplam istek |
| [`admin_kpi.py`](../web_dashboard/tabs/admin_kpi.py:313) | 313 | `SELECT date, SUM(request_count) GROUP BY` | son 30 gün trendi |

- Referans sayısı: **1 dosya, 3 sorgu**
- INSERT/UPDATE/DELETE: **yok** → tablo **asla dolmaz**, panel kalıcı olarak boş gösterir
- Okunan sütunlar: `request_count`, `date`, `tier`
- Beklenen sütunlar: `date`, `tier`, `request_count`, `endpoint`

## Bulgu — açık borç

**Her iki tablonun da yazıcısı yok (D-236 deseni: tüketicisi olan ama üreticisi olmayan yapı).**
`admin_kpi.py:108` zaten doğru davranıyor — tablo yoksa sıfır uydurmuyor, rozet basıyor (D-249).
Ama tablo **var ve boş** olduğunda aynı koruma çalışmaz: `SUM` → `COALESCE(...,0)` → panel "0 istek" der, bu bir yalandır.

| Borç | Önerilen sahip | Tahmin |
|---|---|---|
| `api_usage_daily` yazıcısı (API istek sayacı) | utku | 0.5 gün |
| `entity_matches` yazıcısı (eşleştirme kaydı) | utku | 0.5 gün |
| `admin_kpi.py` boş-tablo rozeti (tablo var + 0 satır) | yasu | 1 saat |

## Kabul kriteri

- [x] entity_matches tüm referanslar bulundu (dosya + satır)
- [x] api_usage_daily tüm referanslar bulundu
- [x] Beklenen sütun listesi yazıldı
- [x] Rapor dosyası oluşturuldu (bu dosya)

## Öz-eleştiri

Brif, migrasyon dosyası olarak `0021_missing_tables.sql`'i işaret ediyordu; ölçüm tabloların **zaten var** olduğunu gösterdi. Brifi ölçmeden yazmışım — "eksik tablo" varsayımı canlı veritabanında doğrulanmamıştı (D-238 ihlali, benim hatam).

## Ilgili Nodlar

- [[AGENTS]]
- [[hubs/VERI_KALITESI_HUB]]
