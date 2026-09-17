# ORCH-13 — Orkestrasyon sağlamlaştırma: S-05 / S-06 / D-35 (cline, P2)

Kaynak: `docs/ROO_ELESTIRI_NOTLARI.md` (D-35, O-03, S-06), `docs/ANTHROPIC_OIDC_KURAL.md` satır 112-113.

## Kapsam
1. **S-06 / D-35 hayalet onay:** `trigger.onay_bekleyenler()` panoda kaydı olmayan görevi (`tb.gorev_getir()` None) onay kuyruğuna ALMAZ; `gorev_kutusu.py bakim` böyle kayıtları temizler. Test: pano-dışı `teslim` → `onay_bekleyenler()` boş.
2. **Bilgi tetiği alma:** `tetik_al` panoda görev yoksa hata yerine `bilgi=True` ile `alindi` yapar (CLI `al --bilgi` bayrağı). Test ekle.
3. **S-05 şema doğrulama:** `pano_normalize` zorunlu alanları (`task_id,id,baslik,sahip,oncelik,durum`) eksikse tamamlar; eksik `id` → `task_id`. Test ekle.
4. **Bayatlama:** `bakim` 7 günden eski `bekliyor` tetikleri ve sahibi `done` olan kilitleri raporlar (silme yok, rapor). Test ekle.
5. Claude PR yorumu sonrası cline'ın yalnız "bulguları doğrula + brif kontrol listesi" yapması kuralını `docs/AJAN_DETAY.md` §7'ye tek madde olarak ekle.

## Sınırlar
- `oto_nobetci.py` sürekli modda çalışıyor; davranışını bozma (teslim→onay→zincir akışı testleri yeşil kalmalı: `tests/test_gorev_zinciri.py`).
- Commit ATMA.

## Teslim
- Rapor: `data/orchestrator/ORCH-13_rapor_<tarih>_cline.md`
- `python scripts/gorev_kutusu.py teslim --ajan cline --task-id ORCH-13`
