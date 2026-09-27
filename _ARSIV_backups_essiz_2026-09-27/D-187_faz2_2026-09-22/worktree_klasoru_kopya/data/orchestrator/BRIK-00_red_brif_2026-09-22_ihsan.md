# BRIK-00 RED KARARI — Orkestratör (ihsan) Bilgilendirme Brifi

> Tarih: 2026-09-22 · Kaynak: kontrolör yasu (kullanıcı kararı) · İlgili: D-68

## Karar
`BRIK-00` teslimi **reddedildi** ve düzeltme uygulandı:

| Alan | Eski | Yeni |
|---|---|---|
| `onay_kuyrugu.json` | `onaylandi` (onaylayan: ihsan) | **`reddedildi`** — onaylayan: yasu (kontrolör) |
| `task_board.json` | `done` | **`archive`** (geçerli durum makinesi değeri; panoda BRIK-00 görev kaydı hiç yoktu, bu kayıt hatalıydı) |

## Gerekçe
- `task_board.json` içinde BRIK-00 görev kaydı **yoktu** (BRIK araması: 0 sonuç).
- Teslimde kanıt/çıktı dosyası bildirilmemişti (`ciktilar: []`).
- D-68 tutarlılık ihlali: pano kaydı olmadan onay/done geçersizdir.

## Orkestratörden İstenen
1. **Kök neden:** BRIK-00 pano kaydı yokken kuyruğa nasıl teslim edildi/ondan önce nasıl `onaylandi` işaretlendi — `trigger.py` / `gorev_kutusu.py` akışında pano-doğrulama boşluğu varsa koruma görevi aç (örn. `ORKESTRA-KUYRUK-GUARD-01`: `teslim_et` çağrısında pano kaydı zorunlu olsun).
2. **Kuyruk hijyeni:** 169 kayıtlık kuyrukta benzer "panoda olmayan ama onaylandi/done" satırları var mı kontrol et; varsa aynı düzeltmeyle `reddedildi`/`archive`'a çek.
3. **Karar defteri:** Bu red kararını `decision_log.jsonl`'ye kaydet (gerekçe yukarıda).

## Kanıt
- Düzeltme betiği: `scripts/brik00_red_duzelt.py` (çalıştırıldı: "kuyruk guncellendi", "pano guncellendi")
- Denetim raporu: `data/orchestrator/ORKESTRA-ONAY-KUYRUK-01_rapor_2026-09-21_yasu.md`
