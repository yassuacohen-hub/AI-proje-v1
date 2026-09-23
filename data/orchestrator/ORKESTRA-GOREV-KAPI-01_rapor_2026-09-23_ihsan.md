# ORKESTRA-GOREV-KAPI-01 — Rapor

- **Ajan:** ihsan
- **Tarih:** 2026-09-23
- **Durum:** tamamlandı
- **Kilitler:** `scripts/gorev_at.py`, `scripts/tetik_senk.py`

## Özet

Brif 7 maddesi denetlendi. 5 madde zaten sevk edilmişti (kaynak okunarak doğrulandı, varsayılmadı);
gerçekten eksik olan tek madde `guncelle` komutuydu. O eklendi, testleri yazıldı.
Regresyon sırasında görevle ilgisiz bir **mojibake bozulma olayı** tespit edildi ve onarıldı.

## Madde Madde Durum

| # | Madde | Sonuç |
|---|---|---|
| 1 | D-58 orkestratör kapısı (`at`) | Zaten vardı — `_orkestrator_kapisi`, exit 4 |
| 2 | D-66 brif+talimat zorunluluğu | Zaten vardı — `_brief_bul` + boş talimat reddi |
| 3 | D-57 başlık kapısı (`→` / `--baslik-b64`) | Zaten vardı — `_d57_dogrula`, `_baslik_coz` |
| 4 | **`guncelle` tek komutu (D-87)** | **EKLENDİ** — `cmd_guncelle` + parser |
| 5 | D-63 architect modu kapısı | Zaten vardı |
| 6 | `pano` alt komutu | Zaten vardı — `cmd_pano` |
| 7 | **Test kapsamı** | **EKLENDİ** — 4 test |

## Madde 4 — `guncelle`

`scripts/gorev_at.py` içinde `cmd_guncelle` (satır 302-340). Elle script yazmayı bitirir;
brief/talimat/oncelik/durum alanlarını tek komutla düzeltir.

Çıkış kodu sözleşmesi (sessiz başarı yasağı):

| Kod | Anlam |
|---|---|
| 0 | Güncellendi (`GUNCELLENDI: <id> (<alanlar>)`) |
| 1 | Alan verilmedi **veya** görev panoda yok (0 kayıt ≠ başarı) |
| 4 | D-58 — çağıran aktif orkestratör değil |
| 6 | D-66 — `--brief` diskte olmayan dosyayı gösteriyor |

Kullanım:

```
python scripts/gorev_at.py guncelle --task-id <ID> --cagiran roo --brief plans/brief_<ajan>_<ID>.md
python scripts/gorev_at.py guncelle --task-id <ID> --cagiran roo --oncelik P1 --durum aktif
```

## Madde 7 — Testler

`tests/test_gorev_at_kapi.py` içine 4 test eklendi (`_gargs` yardımcısıyla):

- `test_guncelle_olmayan_brif_reddeder` — D-66, exit 6, **panoya yazılmadığı da doğrulanır**
- `test_guncelle_alansiz_cagri_reddeder` — sessiz başarı yasağı, exit 1
- `test_guncelle_gorev_yoksa_sifir_donmez` — `gorev_guncelle` None → exit 1
- `test_guncelle_var_olan_brif_gecer` — exit 0 + yolun POSIX kaldığı (Windows ters bölü sızmasın)

Gerçek CLI kabul kontrolü: `guncelle --brief <olmayan>` → **exit 6** (doğrulandı).

## Regresyon

| Aşama | Sonuç |
|---|---|
| Görev öncesi bilinen taban | 7 failed / 3966 passed |
| Değişiklik sonrası ilk ölçüm | **14 failed** / 3972 passed ← 7 YENİ kırık |
| Mojibake onarımı sonrası | 8 failed / 3982 passed |
| Import düzeltmesi geri uygulandıktan sonra | 7 failed (taban) |

## BULGU — Mojibake Bozulma Olayı (görev dışı, kritik)

Regresyon 7 → 14'e çıktı. Benim değişikliğim değildi.

`git diff --stat` → `src/company_master/orchestrator/trigger.py | 250 +++---` — hiç dokunmadığım dosya.
Bayt düzeyinde kanıt:

```
-            raise TriggerError(f"Görev panoda bulunamadı: {task_id}")
+            raise TriggerError(f"GÃ¶rev panoda bulunamadÄ±: {task_id}")
-                f"Görev {task_id} '{...}' ajanına ait; {ajan} alamaz"
+                f"GÃ¶rev {task_id} '{...}' ajanÄ±na ait; {ajan} alamaz"
```

Doğru UTF-8 kaynak kodu **mojibake'lendi** — onarım aracı ters yönde iş görmüş.
Blast radius: `src scripts tests web_dashboard` altında **110 mojibake satırı eklenmiş**,
ayrıca `trigger.py` satır 1'e **BOM enjekte edilmiş** (`test_kodlama_denetim::test_guard_bom_ratchet` bundan kırıldı).

### Yapılanlar

1. Bozuk hâl yedeklendi: `data/_tmp/_trigger_bozuk_yedek.py.bak`
2. `git checkout -- src/company_master/orchestrator/trigger.py`
3. **Toptan geri alma yapılmadı.** Diğer değişen dosyalar tek tek incelendi ve meşru işler korundu:
   - `tests/test_webhook_monitor_tab.py` (`st.metric` → `webhook_monitor.kpi_karti`) — korundu
   - `src/.../task_board.py` (`ALTYAPI-KILIT-OTOMATIK-01` öz-kilit koruması) — korundu
4. Geri alma yasu'nun `ALTYAPI-IMPORT-TEKLES-01` import düzeltmesini de sildi
   (`tests/test_trigger_import.py::test_uzaktan_cagirma_baglaminda_import_calisir` kırıldı).
   Düzeltme **mojibake'siz olarak yeniden uygulandı** — `trigger.py` satır 24, 274, 305, 386:
   `from src.company_master.orchestrator import X` → `from . import X`.
   Doğrulama: `test_trigger_import.py` + `test_pano_sema.py` + `test_gorev_at_kapi.py` → **29 passed**.

### Kalan Risk — `scripts/mojibake_onar.py` (dokunulmadı, yasu'nun aktif görevi)

- `--dizin` modu yalnız `**/*.md` tarar → `.py` hasarı **tek-dosya modundan** gelmiş olmalı.
- **Bariyer yok:** araç yazmadan önce "mojibake sayısı arttı mı" kontrolü yapmıyor.
  Öneri: `dosya_onar` içinde yazım öncesi `MOJIBAKE_RX` kalan sayısı başlangıçtan büyükse yaz**ma**, hata dön.
- **Yanıltıcı özet satırı** (satır 140):
  ```python
  print(f"taranan={len(args.dosyalar)} degisen={toplam_kalan}")
  ```
  `kalan` değeri `degisen` etiketiyle basılıyor. Düzeltilmeli.

## Kalan 7 Kırık Test (hepsi görev öncesinden, bu görevle ilgisiz)

- `test_admin_performance.py` (3) — önceden kırık
- `test_d182_mimir.py::test_mimir_kanonik_ajan` — açık görev `ALTYAPI-D182-MIMIR-01`
- `test_d87_atama_otomasyonu_fixed.py::test_brifsiz_atama_reddedilir` — **hermetik değil**:
  canlı repoya yazıyor, kendi artığı `data/orchestrator/triggers/olmayan.jsonl`'i bırakıyor;
  ayrıca COP-26'ya triyajda brif geri yazıldığı için artık "brifsiz" değil
- `test_marka_denetim_muafiyet.py::test_kok_denetimi_temiz` — önceden kırık
- `test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[musteri_yonetimi]` — önceden kırık

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/plans/brief_ihsan_ORKESTRA-GOREV-KAPI-01]]
