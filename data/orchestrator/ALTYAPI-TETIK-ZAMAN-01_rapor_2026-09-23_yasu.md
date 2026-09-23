# ALTYAPI-TETIK-ZAMAN-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı (kod + test + gerçek koşu kanıtı + zamanlayıcı kuruldu)
- **Brif**: `plans/brief_yasu_ALTYAPI-TETIK-ZAMAN-01.md`

## 1. Kök neden (doğrulandı)

`scripts/tetik_senk.py` elle çalıştırılıyordu ve çıktısı hiçbir yere yazılmıyordu:
sonuç kayboluyor, sapma birikiyor, `pano_denetim.py` uyarı üretiyordu. Ayrıca
script yalnızca `bekliyor` durumundaki tetikleri kapatıyordu; kuyrukta **uçuşta**
kalan diğer açık durumlar (`alindi`, `teslim`, `zincir_bekleme`, `blocked`)
panoda iş bitse bile sonsuza kadar açık kalıyordu.

**Gerçek veride ölçüm (düzeltme öncesi):** 14 açık tetik → pano final:

| Tetik durumu | Pano durumu | Adet |
|---|---|---|
| `alindi` | done | 1 |
| `zincir_bekleme` | iptal | 3 |
| `zincir_bekleme` | archive | 1 |
| `blocked` | done | 2 |
| `blocked` | archive | 5 |
| `teslim` | done | 2 |

## 2. Yapılan değişiklikler

### `scripts/tetik_senk.py`
1. **`--gunluk` girişi:** koşu sonucu `data/orchestrator/tetik_senk_log.jsonl`
   satırına **append** edilir. Şema brifteki gibi sabit:
   `{"an": ISO-8601, "senk": N, "sapma": M}`.
   `senk = 0` olsa bile satır yazılır → her koşu iz bırakır (sıfır satır sessizliği yok).
2. **`sapma` sayacı + sessiz başarı yasağı:** `tetik_senk()` raporuna `sapma`
   eklendi. Düzeltilemeyen sapmalar sayılır:
   - pano okunamadı / `.jsonl` okunamadı / `.jsonl` yazılamadı,
   - **panoda karşılığı olmayan ve hâlâ açık** tetik (hayalet tetik).
3. **Çıkış kodu tablosu** (`cikis_kodu()`):
   `0` temiz · `1` okuma/yazma hatası · `2` düzeltilemeyen sapma ·
   `3` hiç tetik dosyası yok (yol/kurulum hatası) · `4` `--gunluk` istendi ama
   log satırı yazılamadı (0 satır etkilendi). Her `!= 0` kod için stderr'e **neden**
   yazılır.
4. **Açık durum kümesi genişletildi:** `ACIK_TETIK_DURUMLARI = (bekliyor, alindi,
   teslim, zincir_bekleme, blocked)`; pano final ise bunların hepsi `kapandi` yapılır.
5. **Zamanlayıcı bağlaması** (yeni bağımlılık yok, mevcut `gorev_nobetci.py` deseni):
   - `kur --saat SS:DD` → `scripts/tetik_senk.bat` + `scripts/tetik_senk.vbs`
     (gizli pencere: `WScript.Shell.Run ..., 0, False`) üretir; `schtasks /SC DAILY`
     ile **HuginnData-TetikSenk** görevini kurar.
   - `durum` → schtasks kaydı + son 5 log satırı.
   - `kaldir` → görevi siler (tek komutla geri al).
   - **Geriye uyum:** `tetik_senk.py` ve `tetik_senk.py --gunluk` çağrıları
     bozulmadı (argümansız/flag'li çağrı otomatik `senkron` alt komutuna yönlenir);
     rapor anahtar adları (`basarili`, `hata`, `bulunan_dosya`) korundu →
     `tests/test_sessiz_basari.py` etkilenmedi.

### `tests/test_tetik_senk_log.py` (yeni)
Brifin istediği 2 test + 2 koruma testi = **4 test**:

| Test | Ne kanıtlıyor |
|---|---|
| `test_gunluk_log_satiri_yazilir_ve_json_okunur` | log satırı yazılıyor, JSON olarak okunuyor, şema `{an, senk, sapma}` |
| `test_duzeltilemeyen_sapmada_exit_sifir_degil` | hayalet açık tetik → `sapma=1`, `basarili=0`, exit **2** |
| `test_senk_artisi_loga_yansir` | panoda final + açık tetik → `senk=1`, tetik `kapandi` |
| `test_log_yazilamazsa_sifir_donmez` | log yazılamazsa (0 satır etkilendi) exit **4** |

## 3. Kanıt (gerçek koşu)

### 3.1 İlk koşu — 14 sapma düzeltildi
```
python -X utf8 scripts/tetik_senk.py --gunluk
Sonuç: 14 düzeltme | sapma: 0 | hata: 0 | taranan dosya: 4      (exit=0)
```
Kapatılanlar:
- **ihsan (7):** AGN-CREWAI-PILOT-01 (alindi), ADMIN-UX-MENUTREE-01,
  ADMIN-UX-PROFILMENU-01, DASH-UX-02a (zincir_bekleme), ADMIN-UX-AYARLAR-SAYFA-01,
  DASH-UX-02b, BRIF-03 (blocked)
- **utku (7):** GUARD-ENC-02, SEC-BANDIT-01, FMT-01 (blocked), DOC-SIRKET-MASTER-01,
  ALTYAPI-PANO-ENCODING-FIX-01 (teslim), ADMIN-UX-MENUTREE-01 (zincir_bekleme),
  DASH-UX-02b (blocked)

### 3.2 İkinci koşu — idempotent (kanıt: sapma kalmadı)
```
Sonuç: 0 düzeltme | sapma: 0 | hata: 0 | taranan dosya: 4        (exit=0)
```

### 3.3 Günlük log (gerçek dosya)
`data/orchestrator/tetik_senk_log.jsonl` — 4 koşu, 4 satır (manuel 2 + bat 2):
```jsonl
{"an": "2026-09-23T10:02:36.998434+00:00", "senk": 14, "sapma": 0}
{"an": "2026-09-23T10:02:41.865183+00:00", "senk": 0, "sapma": 0}
{"an": "2026-09-23T10:03:03.072768+00:00", "senk": 0, "sapma": 0}
{"an": "2026-09-23T10:03:11.680388+00:00", "senk": 0, "sapma": 0}
```

### 3.4 Zamanlayıcı (kuruldu + sorgulandı)
```
schtasks /Query /TN HuginnData-TetikSenk /fo LIST
TaskName:      \HuginnData-TetikSenk
Next Run Time: 24.09.2026 08:30:00
Status:        Ready
```
`cmd /c scripts\tetik_senk.bat` → exit 0 (zamanlayıcının çağıracağı yol uçtan uca
denendi; bat 2 log satırı daha yazdı).

### 3.5 Testler
```
pytest tests/test_tetik_senk_log.py tests/test_sessiz_basari.py -q  ->  8 passed
```

## 4. Bilinen/Not edilen davranışlar (karar GEREKMEZ, bilgi)

- **ALARM temizliği:** script, tetik dosyası bulunan her ajanın `*.ALARM.json`
  dosyasını sıfırlar (mevcut davranış, bu görev değiştirmedi). Yani nöbetçi
  uyarı sayaçları her günlük koşuda sıfırlanır. Bu kasıtlıdır ("nöbetçi
  sayaçları artık gerekli değil") ancak uyarı sayacı kanıtı tarihsel olarak
  tutulacaksa ayrı bir arşiv mekanizması gerekir — **ayrı görev önerisi**.
- **Bayat tetikler silinmez:** panoda karşılığı olmayan ama *kapalı* durumdaki
  19 kayıt (ihsan 16, utku 3 — hepsi `done`/`iptal`) temizlik kapsamı dışında
  bırakıldı; yalnızca **açık** olanlar `sapma` sayılır. (Arşivleme
  ALTYAPI-TETIK-ARSIV-01'in alanı.)
- **Yedek:** koşu öncesi `data/orchestrator/triggers/` klasörünün tamamı
  `%TEMP%\tetik_triggers_yedek_20260923\` altına kopyalandı (tetik dosyaları
  git'te izlenmiyor).
- `data/orchestrator/tetik_senk_cikti.log` yeni çalışma zamanı logu
  (bat çıktısı); konsol kod sayfası nedeniyle emoji/aksansız karakterler bu log
  dosyasında bozuk görünebilir — veri (JSONL) UTF-8 ve temiz.

## 5. Geri alma

```powershell
python -X utf8 scripts/tetik_senk.py kaldir          # zamanlayıcıyı sil
# istenirse: Remove-Item scripts\tetik_senk.bat, scripts\tetik_senk.vbs
# tetik kuyruğu: %TEMP%\tetik_triggers_yedek_20260923\ klasöründen geri kopyala
```

## Araçlar

- `scripts/tetik_senk.py` — senkron + `--gunluk` + `kur`/`durum`/`kaldir`
- `tests/test_tetik_senk_log.py` — 4 test
- `scripts/tetik_senk.bat` / `scripts/tetik_senk.vbs` — zamanlayıcı sarmalayıcıları
  (üretilen dosyalar)
