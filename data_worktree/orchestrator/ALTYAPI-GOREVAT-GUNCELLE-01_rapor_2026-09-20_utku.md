# ALTYAPI-GOREVAT-GUNCELLE-01 Rapor — 2026-09-20

## Görev
- **Task ID:** ALTYAPI-GOREVAT-GUNCELLE-01
- **Ajan:** utku
- **Durum:** TAMAMLANDI → TESLİM
- **Öncelik:** P2
- **Brif:** Teslim komutundaki talimat (gorev kutusu bak)

## Yapılan İş
1. **`scripts/gorev_at.py`** — `guncelle` subkomutu eklendi
   - `--task-id` (required), `--talimat`, `--durum`, `--sahip` parametreleri
   - `cmd_guncelle()` fonksiyonu: `tb.gorev_guncelle()` wrapper
   - D-57/D-33 doğrulama: `sahip` normalize, `durum` GOREV_DURUMLARI kontrolü
   - Boş talimat → `-` default; boş sahip → `-` default
   - Güncellemeden önce mevcut değer okunur, before→after gösterilir

2. **`src/company_master/orchestrator/trigger.py`** — D-66 guard düzeltmesi
   - `tetik_ekle()`'ye `zorunlu_brif: bool = False` parametresi eklendi
   - Varsayılan False → pytest devam eder (PYTEST_CURRENT_TEST bypass korunur)
   - `zorunlu_brif=True` → D-66 guard her zaman devreye girer (pytest altında dahil)
   - D-66 testleri artık guard'ı doğrulayabilir

3. **`tests/test_d66_brif_guard.py`** — D-66 testleri güncellendi
   - 3 test (`test_bos_talimat_hata_firlatir`, `test_bosluk_talimat_hata_firlatir`, `test_olmayan_brif_hata_firlatir`) artık `zorunlu_brif=True` ile çağrılıyor

## Değişen Dosyalar
- `scripts/gorev_at.py` — `cmd_guncelle` + `guncelle` subparser
- `src/company_master/orchestrator/trigger.py` — `zorunlu_brif` parametresi + D-66 guard
- `tests/test_d66_brif_guard.py` — `zorunlu_brif=True` eklendi (3 test)

## Test Sonuçları
```
# D-66 + trigger + CLI testleri:
tests/test_d66_brif_guard.py  5 PASSED
tests/test_gorev_trigger.py   PASSED
tests/test_gorev_kutusu_cli.py PASSED
Toplam: 36 passed

# Full suite regression:
4 failed, 3923 passed, 22 skipped, 127 warnings in 73.55s
```

### Bilinen Test Failure'ları (ALTYAPI-GOREVAT-GUNCELLE-01 Dışı — Önceden Var)
1. `test_find_root_finds_env` — .env konfigürasyonu (pre-existing)
2. `test_sekme_rehgeri_metinleri_utf8_ve_yapili` — encoding (pre-existing)
3. `test_auth_modal_icerik_fonksiyonu` — app.py "Şifremi unuttum" eksik (pre-existing)
4. `test_render_webhook_monitor_tab_renders_metrics` — st.metric çağrısı eksik (pre-existing)

**ALTYAPI-GOREVAT-GUNCELLE-01 çalışması BU failure'lara neden olmamıştır.**

## Kodlama Denetim
- `python scripts/kodlama_denetim.py --tam-repo` — `gorev_at.py`, `trigger.py`, `test_d66_brif_guard.py` listede yok (temiz)

## Wireframe/Uyum
- D-57: `guncelle` komutu başlık doğrulaması yapmaz (güncelleme işlemi olduğu için)
- D-66: `zorunlu_brif` parametresiyle D-66 guard test edilebilir

## Bulgular

🟢 **Tamam:** `guncelle` subkomutu eklendi — CLI'dan talimat/durum/sahip güncellenebilir
🟢 **Tamam:** D-66 guard `zorunlu_brif` parametresiyle test edilebilir hale getirildi
🟢 **Tamam:** `sahip` normalizasyonu ve `durum` validasyonu `guncelle` komutunda çalışıyor
🔵 **Öneri:** Diğer `gorev_at.py` alt komutları (`at`, `abrakadabra`) da `zorunlu_brif` parametresi eklemesi önerilir (konsistans için)
🔵 **Öneri:** `cmd_at` içinde D-66 guard da aynı `zorunlu_brif=False` default'u ile çalışmalı; prod ortamında boş talimat engellenir
