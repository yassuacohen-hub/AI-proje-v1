# UI-D57-BASLIK-DUZELT-01 — Brif

| Alan | Değer |
|------|-------|
| **Task ID** | UI-D57-BASLIK-DUZELT-01 |
| **Başlık** | `[ORKESTRA] D-57 başlık ihlallerini düzelt → data/orchestrator/task_board.json (2s)` |
| **Sahip** | Üretim/Hacim UTKU |
| **Öncelik** | P1 |
| **Süre** | 2s |
| **Kaynak** | `ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md` (YASU denetimi) |

## Amaç
YASU'nun brif kalite denetimi 11/12 görevde D-57 başlık standardı ihlali buldu. Bu görev ihlalleri `task_board.json` içinde düzeltir.

## D-57 Standardı (hatırlatma)
```
[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)
```
- **ALAN** (7 kanonik): `UI` · `API` · `VERI` · `TEST` · `DOC` · `ALTYAPI` · `ORKESTRA`
- **FİİL** (8 kanonik): `yaz` · `düzelt` · `taşı` · `sil` · `denetle` · `ölç` · `belgele` · `araştır`
- **ÇIKTI**: tek dosya yolu veya tek komut
- **SÜRE**: `30d` · `1s` · `2s` · `4s`
- Ok işareti **Unicode `→`** olmalı (ASCII `->` değil)

## İş Maddeleri

### 1. Süre eksik olan 8 görev — SÜRE ekle
Aşağıdaki görevlerin başlığına `(SÜRE)` son eki ekle. Süre tahmini iş kapsamına göre:

| task_id | Mevcut başlık sorunu | Önerilen SÜRE |
|---------|---------------------|---------------|
| `ALTYAPI-FORM-SETUP-03` | SÜRE eksik | `(2s)` |
| `ALTYAPI-PROXY-CONFIG-02` | SÜRE eksik | `(1s)` |
| `ALTYAPI-SQLITE-INIT` | SÜRE eksik | `(1s)` |
| `ALTYAPI-WEB-MONITOR-01` | SÜRE eksik | `(2s)` |
| `DOC-V10-AUDIT-01` | SÜRE eksik | `(2s)` |
| `ORKESTRA-BRIEF-KALITE-01` | SÜRE eksik | `(1s)` |

### 2. FİİL yanlış olan 2 görev — kanonik FİİL'e çevir
| task_id | Mevcut | Düzeltilmiş |
|---------|--------|-------------|
| `ALTYAPI-BENCHMARK-02` | "Performans ölçümü" (isim öbeği) | `Performansı ölç` |
| `ALTYAPI-BILGI-TABANI-03` | "Runbook ve uyum denetimi" (isim öbeği) | `Runbook belgele` |

### 3. Tam ihlal — 1 görev
| task_id | Sorun | Düzeltilmiş başlık |
|---------|-------|-------------------|
| `ADMIN-UX-LOGOUT-01` | `[ALAN]`, FİİL, `→`, ÇIKTI, SÜRE hepsi eksik | `[UI] Çıkış akışını düzelt → web_dashboard/tabs/admin_auth.py (1s)` |

## Nasıl Yapılır
`scripts/gorev_at.py guncelle` komutu ile her görevin başlığını güncelle:
```
python -X utf8 scripts/gorev_at.py guncelle --task-id <ID> --baslik "<yeni başlık>"
```

Ya da toplu düzeltme için geçici script yaz (`data/_tmp/` altına), çalıştır, sil.

## Kabul Kriterleri
- [ ] 11 görevin başlığı D-57 kalıbına uygun
- [ ] Ok işareti Unicode `→` (ASCII `->` yok)
- [ ] ALAN ön eki `task_id` ön eki ile aynı
- [ ] `python -X utf8 scripts/kodlama_denetim.py` temiz
- [ ] Rapor yazıldı: `data/orchestrator/UI-D57-BASLIK-DUZELT-01_rapor_2026-09-20_uretim.md`

## Çıktı
`data/orchestrator/task_board.json` (11 görev başlığı düzeltilmiş)

## Notlar
- **D-57 geriye dönük muafiyet** var (`BASLIK-GERIYE-01`), ancak bu 11 görev **yeni** (2026-09-20) olduğundan muafiyete girmez.
- Başlık değişimi görev kimliğini (`task_id`) **değiştirmez** — sadece `baslik` alanı güncellenir.
