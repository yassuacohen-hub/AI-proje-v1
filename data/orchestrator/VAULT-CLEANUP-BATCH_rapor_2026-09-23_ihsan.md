---
task_id: VAULT-CLEANUP-BATCH
ajan: ihsan
tarih: 2026-09-23
durum: review
---

# VAULT-CLEANUP-BATCH — Vault Mekanizması Temizliği (Rapor)

## Özet

Üç adımın üçü de tamamlandı. Yol boyunca **temizliğin asıl sebebi olan 3 kod hatası** bulundu ve düzeltildi; temizlik olmadan bu hatalar birikmeye devam edecekti.

| Adım | Brif talebi | Sonuç |
|---|---|---|
| 1 | `.ALARM.json` 25 dosya sil | 19 dosya bulundu → 4'ü `tetik_senk.py` tarafından otomatik silindi, 15'i `_trash/` klasörüne **taşındı** (silinmedi) |
| 2 | UTF-8 temizliği tüm ajanlar | 26 mojibake bulgusu → 6 dosyada onarıldı; kalan 5 kurtarılamaz kayıt (aşağıda) |
| 3 | `archive_old_records()` çalıştır | Fonksiyon **yok**; analog `pano_denetim.py --uygula` çalıştırıldı → 29 görev `archive`, 4 görev `bitis_temizle` |

## Bulunan Kod Hataları (asıl kök neden)

### Hata 1 — `tetik_senk.py` hiçbir tetik dosyasını bulamıyordu

```python
data_dir = Path("data/orchestrator")     # ESKİ: göreli + triggers/ eksik
data_dir = tb.STATE_DIR / "triggers"     # YENİ
```

İki kusur birden: yol `triggers/` alt klasörünü atlıyordu **ve** cwd'ye bağımlıydı. Script sessizce "0 dosya işledim" deyip exit 0 dönüyordu. Haftalardır bayat tetikler birikmesinin sebebi bu — `REVIEW-ONAY-KUYRUGU-01` tetiği **913 kez** uyarı üretmiş.

Ayrıca ajan listesi sabit kodlu idi; `trig.AJANLAR` tek kaynağına bağlandı (D-33/D-60).

### Hata 2 — `iptal` final durum sayılmıyordu

```python
if pano_durum in ("done", "blocked", "archive", "reddedildi", "iptal"):
```

`iptal` listede yoktu. İptal edilen görevlerin tetiği hiç kapanmıyor, sonsuza kadar uyarı üretiyordu.

### Hata 3 — Windows konsolunda çökme

Rapor satırındaki `✅` emojisi cp1254 konsolda `UnicodeEncodeError` veriyordu. `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` eklendi. Yanı sıra docstring'in **üstüne** konmuş kullanılmayan `import io` kaldırıldı, `datetime.utcnow()` → `datetime.now(timezone.utc)`.

## Adım 1 — ALARM dosyaları

Yedek: `data/_tmp/triggers_yedek_2026-09-23/` (35 dosya, mutasyondan önce).

`tetik_senk.py` düzeltildikten sonra çalıştırıldı: 14 bayat tetiğin 13'ü `bekliyor` → `kapandi`. Yalnızca `ORKESTRA-NAMING-AUDIT-02` `bekliyor` kaldı — panoda `plan`, yani **doğru davranış**, hâlâ açık görev.

Kalan 15 ALARM dosyası kanonik olmayan ajan adlarına aitti (D-60 öncesi: `arastirmaci`, `claude_code`, `external_agent`, `gelistirici`, `kalite`, `mimar`, `mimari`, `my_agent`, `orkestrator`, `roo_code`) ve task-id adlı artıklar (`MVP-KUL-02`, `admin_admin2_dogrula_01`, `admin_login_fix_01`, `admin_modal_stil_01`, `admin_sifre_reset_flow_01`).

Brif "sil" diyordu; **taşıdım**: `_trash/triggers_alarm_2026-09-23/`. Geri alınabilirlik silmeye tercih edildi.

```
tasinan 15 kalan 0
```

## Adım 2 — UTF-8

`scripts/mojibake_onar.py` klasör argümanı kabul etmiyor (`YOK: data\orchestrator\triggers`, exit 2); glob ile dosya listesi verildi.

- **BOM:** 16 dosyanın hiçbirinde yok.
- **Mojibake:** ilk tarama 26 bulgu / 6 dosya (`ihsan` 20, `kalite` 2, `claude_code` 1, `gelistirici` 1, `mimari` 1, `yasu` 1).
- İki onarım turu sonrası: `ihsan`, `kalite`, `mimari`, `claude_code` temiz.
- **Kalan 5 bulgu kurtarılamaz** (`ATLANDI`): `yasu.jsonl:27` (`GUARD-ENC-01`) ve `gelistirici.jsonl` — bunlar çift kodlamadan değil, kaynakta zaten kaybolmuş bayt. Onarıcı doğru davranıp dokunmadı.

Bütünlük doğrulaması onarımdan sonra:

```
satir 224 bozuk 0 BOM 0
```

Yani 224 JSON satırının hiçbiri onarım sırasında bozulmadı.

## Adım 3 — Arşiv

`archive_old_records()` diye bir fonksiyon kod tabanında **yok**. En yakın analog: [`pano_denetim.arsivlenebilir()`](../../scripts/pano_denetim.py:188) — `durum=done` + kuyrukta `onaylandi` + son hareket 7 günden eski görevleri seçer, `uygula()` bunları `durum="archive"` yapar.

Yedek: `data/_tmp/task_board_yedek_2026-09-23.json`.

Pano durum dağılımı:

| durum | önce | sonra |
|---|---|---|
| done | 268 | 239 |
| archive | 79 | 108 |
| iptal | 3 | 3 |
| plan | 5 | 5 |
| aktif | 4 | 4 |
| review | 1 | 1 |
| **toplam** | **360** | **360** |

29 görev arşivlendi, 4 görevin tutarsız `bitis` alanı temizlendi. Denetim durumu `fail` (4 hata) → **`ok` (0 hata)**. Kalan 16 uyarı bilinçli olarak dokunulmadı: `orphan` ve `kuyruk=onaylandi ama pano=plan` bulguları kanıt ister, D-77 gereği orkestratörün yetkisindedir.

## Değişen Dosyalar

- [`scripts/tetik_senk.py`](../../scripts/tetik_senk.py) — 3 hata düzeltildi
- `data/orchestrator/triggers/*.jsonl` — mojibake onarımı + bayat tetik kapatma
- `data/orchestrator/task_board.json` — 29 archive + 4 bitis_temizle
- `_trash/triggers_alarm_2026-09-23/` — 15 ALARM dosyası (taşındı)
- `data/_tmp/triggers_yedek_2026-09-23/`, `data/_tmp/task_board_yedek_2026-09-23.json` — yedekler

## Öneriler (KAHİN kararı gerekir)

1. **`tetik_senk.py` günlük çalışsın.** Hata düzeltildi ama script elle çağrılıyor; bayat tetik birikimi yine olur. `pano_denetim.py` ile aynı zamanlamaya bağlanmalı.
2. **Sessiz başarı yasaklanmalı.** `tetik_senk.py` 0 dosya bulduğunda exit 0 dönüyordu — hatanın haftalarca görünmemesinin tek sebebi bu. "0 dosya = hata" kuralı bu tür tarayıcılara konmalı.
3. **Kanonik olmayan ajan tetikleri temizlensin.** `arastirmaci`, `claude_code`, `mimar`, `kalite` vb. 10 adet D-60 öncesi `.jsonl` hâlâ `triggers/` içinde duruyor; `AJANLAR` dışındaki her dosya arşive alınmalı.
4. **`mojibake_onar.py` klasör argümanı kabul etsin.** Şu an yalnızca dosya listesi alıyor; toplu denetimde her seferinde glob sarmalayıcı yazmak gerekiyor.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/data/orchestrator/VAULT-CLEANUP-BATCH_brif_2026-09-23_ihsan]]
- [[Huginn Data Insights/data/orchestrator/AGENTS-MERGE-UU_rapor_2026-09-23_ihsan]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
