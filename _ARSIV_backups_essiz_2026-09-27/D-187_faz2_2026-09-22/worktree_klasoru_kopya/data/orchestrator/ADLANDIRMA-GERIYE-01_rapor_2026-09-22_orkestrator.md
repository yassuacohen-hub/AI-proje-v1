# ADLANDIRMA-GERIYE-01 — D-55 geriye dönük adlandırma düzeltmesi

**Tarih:** 2026-09-22 · **Rol:** Orkestratör · **Öncelik:** P3 · **Durum:** done

## Ne yapıldı

D-55 demir kuralının (KAHİN kararı 2026-09-18) geriye dönük uygulaması yapıldı. `data/orchestrator/` altındaki rapor dosya adlarında geçen **ajan adları**, rol bazlı son eklerle değiştirildi.

Eşleme kaynağı iki bağımsız otorite ile doğrulandı:
- [`AGENTS.md`](../../AGENTS.md:403) satır 403-408 — ajan → kanonik ad → rol tablosu
- [`docs/ajanlar/ihsan.md`](../../docs/ajanlar/ihsan.md:166), [`utku.md`](../../docs/ajanlar/utku.md:146), [`yasu.md`](../../docs/ajanlar/yasu.md:172), [`salih.md`](../../docs/ajanlar/salih.md:178) — "Rol son eki" satırları

Uygulanan eşleme:

| Ajan adı (dosya adında) | Rol son eki |
|---|---|
| `roo`, `roo-code`, `ihsan` | `_orkestrator` |
| `kilo`, `kilo-code`, `utku` | `_uretim` |
| `cline`, `clinebot`, `yasin`, `yasu`, `merve`, `continue`, `salih` | `_denetim` |

Adım sırası: (1) kuru çalışma ile 33 dosyalık plan üretildi ve satır satır incelendi, (2) çakışma kapısı (`assert not yeni.exists()` + hedef ad tekilliği) geçildi, (3) fiziksel yeniden adlandırma, (4) `task_board.json` + `onay_kuyrugu.json` içindeki referanslar güncellendi (yazmadan önce `json.loads()` ile bütünlük doğrulaması), (5) kalan ajan adı sıfır self-check'i.

**Kapsam dışı tutulanlar** (D-55 kararının kendi metninde makine kimliği olarak istisna edilenler — [`docs/raporlar/roo_code/TAKIP.md`](../../docs/raporlar/roo_code/TAKIP.md:234) satır 234): `task_board.json` `sahip` alanı, CLI `--ajan` parametresi, `triggers/{ajan}.jsonl` dosyaları, `ajan_normalize()` fonksiyonu. Bunlara **dokunulmadı**.

## Değişen dosyalar

**Yeniden adlandırılan 33 rapor dosyası** (`data/orchestrator/`):

| Eski ad | Yeni ad |
|---|---|
| `ADMIN-AYAR-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `ADMIN-EXEC-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `ADMIN-HITAP-01_rapor_2026-09-18_roo.md` | `..._orkestrator.md` |
| `ADMIN-KOK-TEMIZLIK-01_rapor_2026-09-18_roo.md` | `..._orkestrator.md` |
| `ADMIN-KPI-KART-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `ADMIN-NAV-HAZIR-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `ADMIN-NAV-HAZIR-02_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `ADMIN-REFRESH-FIX-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `ADMIN-ROO-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `ADMIN-ROO-DENETIM-01_rapor_2026-09-18_roo.md` | `..._orkestrator.md` |
| `ADMIN-SEARCH-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `AGN-CREWAI-PILOT-01_rapor_2026-09-21_ihsan.md` | `..._orkestrator.md` |
| `AGN-STACK-01_rapor_roo.md` | `AGN-STACK-01_rapor_orkestrator.md` |
| `API-SPLIT-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `BRAND-KIMLIK-01_rapor_2026-09-16_cline.md` | `..._denetim.md` |
| `GIT-HIJYEN-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `HANDOFF-TEMIZ-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `KPI-HIST-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `MARKA-REVIZE-01_rapor_2026-09-17_cline.md` | `..._denetim.md` |
| `ORKESTRA-ONAY-KUYRUK-01_rapor_2026-09-21_yasu.md` | `..._denetim.md` |
| `RESEARCH-PONYTALE_rapor_2026-09-21_ihsan.md` | `..._orkestrator.md` |
| `REV-BATCH-01_rapor_2026-09-16_cline.md` | `..._denetim.md` |
| `REV-MVP-KD-01_rapor_20260915_cline.md` | `..._denetim.md` |
| `REVIEW-PO-BACK-06_rapor_20260915_cline.md` | `..._denetim.md` |
| `ROO-CONFIG-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `SEC-AUTH-01_asama_b_rapor_2026-09-17_cline.md` | `..._denetim.md` |
| `TEST-CI-01_rapor_2026-09-17_roo.md` | `..._orkestrator.md` |
| `TG-01_rapor_2026-09-18_kilo.md` | `..._uretim.md` |
| `UI-MIMARI-02_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `UTKU_UX_ZINCIR_DURUMU_RAPORU_2026-09-21.md` | `UX_ZINCIR_DURUMU_RAPORU_2026-09-21_uretim.md` |
| `VEC-TEST-01_rapor_2026-09-17_kilo.md` | `..._uretim.md` |
| `VERI-ARSIV-01_rapor_2026-09-21_utku.md` | `..._uretim.md` |
| `VERI-GRAPH-01_rapor_2026-09-21_utku.md` | `..._uretim.md` |

**İçeriği değişen 2 dosya:**
- [`data/orchestrator/task_board.json`](task_board.json) — dosya adı referansları güncellendi + `ADLANDIRMA-GERIYE-01` kaydı `done`
- [`data/orchestrator/onay_kuyrugu.json`](onay_kuyrugu.json) — `ciktilar` alanlarındaki dosya adı referansları güncellendi

Toplam **32 referans** güncellendi.

**Geçici dosya:** `scripts/_adlandirma_geriye_01.py` — tek seferlik, çalıştırma sonrası silindi (D-86).

## Test sonuçları

Script içine gömülü assert tabanlı doğrulamalar (hepsi geçti, çıkış kodu 0):

| Kontrol | Sonuç |
|---|---|
| Çakışma kapısı — hiçbir hedef ad diskte mevcut değil | ✅ 33/33 |
| Plan içi hedef ad tekilliği | ✅ çakışma yok |
| `json.loads()` bütünlük doğrulaması (yazmadan önce, 2 dosya) | ✅ geçti |
| Self-check — kalan ajan adı sonekli rapor dosyası | ✅ **0** |
| Yeni adların diskte varlığı | ✅ 33/33 |
| `ADLANDIRMA-GERIYE-01` panoda bulundu ve `done` yazıldı | ✅ |

Kuru çalışma (`python scripts/_adlandirma_geriye_01.py`) önce çalıştırıldı, 33 satırlık plan gözle doğrulandı, ardından `uygula` argümanıyla uygulandı. Geri dönülemez toplu yeniden adlandırma için kuru çalışma kapısı zorunlu tutuldu.

## Bulgular

- 🟢 **Görev başlığındaki "55 dosya" sayısı bayat.** 2026-09-18 tarihli ilk tahmin. Gerçek durum: `data/orchestrator/` altında toplam **53** rapor dosyası var, bunların **33**'ünde ajan adı geçiyordu. Kalan 20 dosya zaten rol soneki kullanıyordu ya da sonek taşımıyordu. Kural ihlali tamamen kapandı.
- 🟡 **Görev kimliklerinde hâlâ ajan adı var:** `ADMIN-ROO-01`, `ADMIN-ROO-DENETIM-01`, `ROO-CONFIG-01`. D-55 görev kimliklerini de kapsıyor, ancak kimlik değiştirmek pano + `triggers/` + handoff zincirini etkileyen geniş bir patlama yarıçapına sahip. Bu, kardeş görev `BASLIK-GERIYE-01` deseninin kapsamı. Bu görevde bilerek yapılmadı.
- 🟡 **`docs/raporlar/roo_code/` dizin adı ajan adı taşıyor.** D-55 dizinleri de kapsıyor. Dizin yeniden adlandırma, içindeki `TAKIP.md`'ye yapılan çok sayıda referansı kırar; ayrı görev olarak ele alınmalı.
- 🟡 **Senkronizasyon riski:** Bu çalışma yalnızca `worktree klasoru/` altını değiştirdi. `Huginn Data Insights/data/orchestrator/` ve `Huginn Data Insights/data_worktree/orchestrator/` altında aynı raporların kopyaları bulunabilir; bunlar eski adlarıyla duruyor olabilir. Worktree birleştirmesi sırasında ikiz dosya oluşma ihtimali var.
- 🟢 **Kilit çakışması yok.** [`file_locks.json`](file_locks.json) içindeki iki rapor kilidi (`REVIEW-ONAY-KUYRUGU-01_rapor_2026-09-18_denetim.md`, `REVIEW-ONAY-KUYRUGU-02_rapor_2026-09-21.md`) zaten kurala uygun adlardı; yeniden adlandırma planında yer almadılar.
- 🔵 **Öneri — kuralı otomatik zorla.** `scripts/marka_denetim.py` deseninde küçük bir kontrol, `data/orchestrator/*.md` adlarında ajan adı arayıp CI'da kırmızı verebilir. Geriye dönük temizlik bir kez yapıldı; tekrar kirlenmemesi için makine kapısı gerekir. Aksi halde bu görev 3 ay sonra yeniden açılır.

## Eksik / erteleme

- Görev kimliklerindeki ajan adları (`ADMIN-ROO-*`, `ROO-CONFIG-01`) → `BASLIK-GERIYE-01` kapsamına bırakıldı.
- `docs/raporlar/roo_code/` dizin adı → ayrı görev gerektirir (referans kırılma riski).
- `Huginn Data Insights/` altındaki olası kopyaların senkronizasyonu → worktree birleştirme sırasında kontrol edilmeli.
- D-55 için CI koruma kontrolü (🔵 öneri) → görev açılmadı, ürün sahibi kararına bırakıldı.
