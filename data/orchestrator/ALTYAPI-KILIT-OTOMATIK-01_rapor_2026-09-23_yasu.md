# ALTYAPI-KILIT-OTOMATIK-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı

## Bulgu: İşin Yarısı Zaten Kodda

Brief hazırlandığında kod incelenmiş ama implementasyonun büyük kısmı
zaten `src/company_master/orchestrator/task_board.py` içinde mevcut bulunmuş
(muhtemelen roo'nun ORCH-05/05b çalışması):

| Brief Maddesi | Durum |
|---|---|
| 1. `lock_birak_gorev(task_id)` — tek yazım, dosya listesi döner | ✅ Zaten var (satır ~545) |
| 2. `gorev_guncelle()` done dalında otomatik çağrı + hata yutma | ✅ Zaten var (ORCH-05: done/blocked'da kilitler düşüyor; hata pano yazımını çökertmiyor) |
| 3. `stale_kilitler(saat=24)` — sadece listeler, silmez | ✅ Zaten var (satır ~558; bozuk tarih atlanıyor, yaş saat sıralı) |
| 4. Self-lock guard (`file_locks.json` / `task_board.json` kilitlenemez) | ❌ **Eksikti → bu görevde eklendi** |
| 5. `tests/test_task_board_kilit.py` | ⚠️ Dosya vardı (7 test), **2 test eklendi** (self-lock + done-hata-yutma) |

## Yapılan Değişiklikler

1. **`_lock_alan()` self-lock guard** (`src/company_master/orchestrator/task_board.py`):
   - Dosya adı `file_locks.json` veya `task_board.json` ise kilit koymadan sessizce döner.
   - İsim-bazlı kontrol (resolve değil) — test monkeypatch'leriyle uyumlu, Windows path davranışından bağımsız.
   - `lock_birak()` imzası değiştirilmedi (brief kuralı).

2. **`tests/test_task_board_kilit.py`** — 2 yeni test:
   - `test_altyapi_kendi_dosyasini_kilitlenemez`: altyapı kendi dosyasını kilitleyemez (sessiz geçilir)
   - `test_gorev_guncelle_done_kilit_hatasi_loglar_gecer`: kilit bırakma patlarsa bile gorev `done` olur

## Test Sonucu

```
tests/test_task_board_kilit.py — 9/9 PASSED (1.13s)
```

## Not

- `stale_kilitler()` otomatik SİLME yapmıyor (brief md.3 uyarısına uygun);
  silme kararı orkestratörde kalıyor. ALTYAPI-KILIT-TEMIZLE-01'deki manuel
  temizlik artık `stale_kilitler(24)` ile önceden görülebilir.
- Kilit düşüşü mevcut `gorev_guncelle(done/blocked)` dalında çalışıyor —
  P1 sorunu ("kilitler done olunca düşmüyor") zaten ORCH-05 ile kapanmış;
  bu görev eksik parçayı (self-lock guard + test güvencesi) tamamladı.
