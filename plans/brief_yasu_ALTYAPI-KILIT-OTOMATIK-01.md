# ALTYAPI-KILIT-OTOMATIK-01 — Kilit otomatik birakmayi yaz

## Gorev Ozeti
Senin `ALTYAPI-KILIT-TEMIZLE-01` raporunun bulgularini koda cevirir. Stale kilit
elle temizlenmeye devam ederse ayni is her hafta tekrar eder; kok neden
kilitlerin gorev bitince dusmemesidir.

## Mevcut Durum
- `src/company_master/orchestrator/task_board.py` — `_lock_alan()` kilit koyar,
  `lock_birak(dosya, sahip)` tek dosya birakir. Gorev `done` olunca **toplu
  birakma yok**.
- `file_locks.json` su an `{}` (senin temizligin sonrasi) — yani temiz zeminde
  calisiyorsun, regresyon riski dusuk.
- Yas bilgisi kayitta zaten var: `"kilitlendi": <ISO>`.

## Is Maddeleri
1. `task_board.py` icine `lock_birak_gorev(task_id: str) -> list[str]` ekle:
   `file_locks.json` icinde `task_id` esleşen tum kayitlari siler, silinen dosya
   yollarini doner. Tek yazma (`_write_json`) ile, dongu icinde yazma yok.
2. Gorev `done` durumuna gecerken cagir. Baglama noktasi `gorev_guncelle()`
   icinde `durum == "done"` daligi — kilit birakma **hata firlatmayacak**,
   basarisizlik gorev kapanisini dusurmesin (logla, gec).
3. Yasa dayali stale tespiti: `stale_kilitler(saat: int = 24) -> list[dict]`
   — `kilitlendi` alani `saat`ten eskiyse listeler. **Sadece listeler, silmez.**
   Otomatik silme bu gorevde YOK (sessiz veri kaybi riski); silme karari
   orkestratorde kalir.
4. Kendi kendini kilitleme antipattern'i: `_lock_alan()` icinde dosya yolu
   `file_locks.json` veya `task_board.json` ise kilit koyma, sessiz gec —
   orkestrasyon altyapisinin kendisi kilitlenemez.
5. Test: `tests/test_task_board_kilit.py`
   - kilit koy → `lock_birak_gorev()` → dosya listesi doner, `file_locks.json` bos
   - iki farkli task'in kiliti varken sadece hedef task'inki dusuyor
   - `stale_kilitler(24)` taze kiliti dondurmuyor, 25 saatlik kiliti donduruyor
   - `file_locks.json` kendi kendine kilitlenemiyor

## Dosyalar
- `src/company_master/orchestrator/task_board.py`
- `tests/test_task_board_kilit.py` (yeni)

## Kurallar
- D-55 adlandirma, D-184 wikilink koprusu, D-86 cmd.exe.
- Var olan `lock_birak()` imzasi **degismeyecek** (cagiranlar kirilmasin).

## Teslim
```
python scripts/gorev_kutusu.py teslim --task-id ALTYAPI-KILIT-OTOMATIK-01 --ajan yasu --ozet "<ozet>" --cikti data/orchestrator/ALTYAPI-KILIT-OTOMATIK-01_rapor_2026-09-23_yasu.md
```

## Sure Tahmini
3s

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
