# VERI-TSG-ESLEME-CASE-01 — Teslim Raporu

**Rol:** uretim · **Tarih:** 2026-10-02

## Ne yapıldı

1. **Varsayım ölçüldü ve yanlış bulundu.** Brif'in `306/326 NULL çünkü eşleşme başarısız`
   iddiasının gerçek sebebi eşleşme hatası değil: 306 kanıt dosyasının `il_turu`
   alanı **boş**. Etiketlenecek metin yok.
2. **Türkçe katlama düzeltildi.** `_asciiye()` Türkçe harfleri (`ı ş ğ ü ö ç`)
   yutuyordu. Kanıt: `Artırımı` -> `ARTRM`, `Şube Açılış` -> `SUBE ACLS`.
   `_TR_ASCII` harf eşlemeleri eklendi; `ILAN_TURU_ESLEME` ölçülmüş **17 tam
   `il_turu` değeri** ile tanımlandı. Kanıtta etiketlenen kayıt **13 -> 20** (+7).
3. **Canlı tablo geri dolduruldu (D-261).** Eşleme düzeltmesi yalnız koda girdi;
   `company_events` kayıtları eski eşlemeyle yazılmıştı. `tsg_yazici`
   `source_guid`'i mevcut sayıp atladığı için (**407 kayıt / 407'si zaten
   mevcut** — canlı Supabase'ten ölçüldü, kanıt dosyası sayısı değil) yeniden
   koşmak hiçbir şeyi düzeltmezdi. **19 satır** ölçüldü, yedek alındı, uygulandı.
   Sonrasında `event_type` boşluğu **404 → 387**, etiketli kayıt **13 → 20**.
4. **Kanıt zinciri ölçüldü:** 326 kanıt dosyası -> **0 hata**.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `skills/services/ticaret_sicili_kanit.py` | `_TR_ASCII` Türkçe harf eşlemeleri; `ILAN_TURU_ESLEME` ölçülmüş 17 değer |
| `tests/test_tsg_zincir.py` | Türkçe katlama, ölçülmüş veri, geri doldurma mandalları (10 -> 15 test) |
| `scripts/tsg_esleme_geri_doldurma_olcumu.py` | Yeni — düzeltilecek satır ölçümü (salt okuma) |
| `scripts/tsg_esleme_geri_doldur.py` | Yeni — `--dene` / `--yaz`; yedek kanıttan yeniden hesaplama (D-243/D-244) |
| `scripts/tsg_esleme_mandal_kirma_denemesi.py` | Yeni — mandalı gerçek dosya değişikliğiyle kırma kanıtı |
| `scripts/tsg_kapanis_kaydi.py` | Yeni — idempotent hub kayıt yazıcı |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | Kapanış kaydı eklendi |

## Test sonuçları

| Ölçüm | Sonuç |
|---|---|
| TSG hedefli süit (`test_tsg_zincir` + `test_ticaret_sicili_kanit` + `test_tsg_rapor`) | **75 passed** |
| Karar numarası + tetik–pano mandalı | **19 passed** |
| Kodlama denetimi | temiz |
| Zincir kanıtı (kanit -> yazici -> company_events) | 326 dosya, **0 hata** |
| Kanıttan etiketlenen kayıt | 13 -> **20** |
| Canlı `company_events` | 407 satır |
| `event_type IS NULL` | 404 -> **387** |
| Düzeltilen satır | **19** |
| Yedek kanıt | `yedekler/company_events_esleme_20261002.jsonl` (19 satır) |
| İdempotency (ikinci koşu) | **0 yazılacak** |

### Bilinen test failure'ları (D-55 teslim madde 2 — zorunlu açıklama)

Tam süit ölçüldü: **18 failed / 4957 passed / 12 skipped** (197 sn).
Bu teslimin kapsamındaki **hiçbir** hata teslim gerekçesi değildir; sahiplik
kovaları `scripts/tam_suit_kova_olcumu.py` ile ayrıştırıldı ve kaynak
dosya:test adı ölçüldü (D-224 — teşhis tahmin değil):

| Kova | Adet | Sahiplik |
|---|---:|---|
| Bu teslimin sahipliği (TSG) | **0** | — |
| `brief_sablon_denetim` (5 SEMA brifi) | 5 | salih / yasu |
| `pano` / `gorev_kutusu` / `kok_politikasi` / `naming_audit` / `dusurulen_kolon` / `dokuman_politikasi` / `kodlama_denetim` | 10 | Orkestratör |
| `tests/vector/test_embedder.py` | 1 | `ALTYAPI-RAG-EMBEDDER-01` (yasu) |
| **Toplam** | **18** | |

Bu teslimden **önce** iki kırmızı bu ajanın alanındaydı ve **kapatıldı**:
`rag_korpus_olcum.py` BOM'lu (kırpıldı), `brief_utku_VERI-TSG-ESLEME-CASE-01.md`
başlığı Türkçe `İ` ile yazılmıştı (ASCII'ye çevrildi, D-218).
RAG teslimi sonrası hedefli genişletilmiş süit: **221 passed, 5 failed** —
5'in tamamı `brief_salih_*` / `brief_yasu_VERI-SEMA-DOGRULA-*` brifleri.

## Bulgular

- 🟡 **Brif varsayımı yanlıştı.** `306/326 NULL` gerekçesi "eşleşme başarısız"
  diyordu; ölçüm bu 306 kaydın `il_turu` alanının boş olduğunu gösterdi. Boş
  alan etiketlenecek metin taşımadığı için NULL **doğru** değerdir (D-249).
- 🟡 **Türkçe katlama sessiz veri kaybıydı.** `ı ş ğ ü ö ç` yutuluyordu;
  hata fırlatmıyordu, yalnız yanlış eşleme üretiyordu. 20 kanıt ilan türünün
  7'si bu yüzden kaçıyordu.
- 🔴 **`0037_tsg_olay_hatti.sql` `event_type` kolonunu içermiyor**, ancak kolon
  canlı DB'de mevcut. Başka bir migration'dan geliyor. Şema beyanı ile gerçek
  şema ayrışmış; gözden geçirilmeli.
- 🔵 **Kanıtta var, DB'de olmayan kayıt: 7** (biri etiketli değil). Kanıt
  dosyası silinmiş kayıtlara işaret ediyor olabilir; bu turda dokunulmadı.
- 🔵 **DB'de var, kanıtta yok: 88 kayıt.** Eski kanıt arşivi silinmiş; etiket
  yeniden hesaplanamaz. Kapsam dışı bırakıldı.

## Eksik / erteleme

- `D-317` karar metninde `tetik_ekle()` için belirtilen kapalı-durum yazma kapısı
  bu turda uygulanmadı; tetik dosyaları orkestratöründür (D-77).
- 306 boş `il_turu` kaydı için kaynak zenginleştirme ayrı görev gerektirir;
  bu teslimde yalnız doğru davranış (NULL) kanıtlandı.