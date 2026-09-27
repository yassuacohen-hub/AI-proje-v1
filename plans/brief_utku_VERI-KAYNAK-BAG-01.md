# Brif — VERI-KAYNAK-BAG-01: Firma↔kaynak bağı (`source_records.company_id`)

**Sahip:** utku · **Öncelik:** P0 · **Süre:** 4s · **Veren:** ihsan
**Önkoşul:** yok — bu kendisi önkoşul
**Blokladığı:** `VERI-NACE-COKLU-01`, `VERI-NACE-TEMIZ-01` (B seviyesi),
`VERI-SEKTOR-01`, `VERI-KAYNAK-SIZINTI-01`

---

## 1. Neden açıldı

`VERI-NACE-COKLU-01` denetiminde çıktı. Utku kodu doğru yazdı, çalıştırdı,
sonuç **21 satır / 14003 firma = %0.15**. Sebep kod değil, **şema**:

`source_records` kolonları:

```
source_record_id, source_id, external_id, raw_name, raw_address, raw_phone,
raw_email, raw_website, raw_tax_number, raw_nace, raw_payload, collected_at,
content_hash
```

**`company_id` yok.** 14000 ham kaydın hangi firmaya ait olduğu veritabanında
kayıtlı değil. ETL kaydı okudu, `companies`'e yazdı, **bağı yazmadı**.

## 2. Ölçülen durum — mevcut bağ seçenekleri

| Alan | `source_records` | `companies` | JOIN eşleşmesi |
|------|------------------|-------------|----------------|
| vergi no | `raw_tax_number` **617** dolu | `tax_number` **40** dolu | **33** |
| ünvan | `raw_name` (dolu) | `company_name` (dolu) | ölçülmedi |
| `external_id` | dolu | karşılığı yok | — |

Vergi numarası bağ kuramaz: `companies.tax_number` 14003 satırdan **40**'ında
dolu. Tavan 33. Elde kullanılabilir tek gerçek anahtar **ünvan**.

Ayrıca `source_records` 14000, `companies` 14003 — sayılar neredeyse eşit, yani
**ETL büyük olasılıkla 1:1 yazmış**, sadece bağı kaydetmemiş. Bu iyi haber:
eşleme muhtemelen yüksek isabetle kurulabilir.

## 3. Yapılacak

1. **Önce ölç, sonra yaz.** `raw_name` ↔ `company_name` normalize edilmiş
   (büyük/küçük, `A.Ş.`/`AŞ`, fazla boşluk, `LTD.ŞTİ.`) karşılaştırmada kaç
   kayıt **birebir tek** eşleşiyor? Kaç tanesi çoğa eşleşiyor (belirsiz)? Kaç
   tanesi hiç eşleşmiyor? Bu üç sayı raporlanmadan yazma adımına geçilmeyecek.
2. `source_records.company_id` kolonu (nullable, FK → `companies`) eklenecek.
   **Nullable şart** — eşleşmeyen kayıt silinmez, boş bırakılır.
3. Eşleme kademeli: (a) vergi no eşleşenler (33, en güvenilir), (b) normalize
   ünvan birebir, (c) belirsizler **boş bırakılır**, ayrı döküme yazılır.
4. `source_id` + `external_id` çifti üzerine tekillik gözden geçirilecek —
   aynı kaynaktan aynı firma iki kez girmiş mi (SIZINTI-01 ile kesişiyor).
5. ETL'in bundan sonraki koşularında bağı **yazma anında** kurması: hangi
   `source_record` hangi `company`'ye dönüştüyse `company_id` o an set edilecek.
   Geri dönük eşleme tek seferlik onarım, kalıcı çözüm ETL'de.

## 4. Kabul ölçütü (test)

- `source_records.company_id` kolonu var, FK tanımlı, nullable
- Dolu `company_id` oranı **raporlanır** (hedef: > %90; ETL 1:1 yazdıysa
  ulaşılabilir)
- `company_id` dolu olan hiçbir satırda `companies`'te karşılığı olmayan id yok
  (FK zaten engeller, test yine de koşacak)
- Belirsiz/eşleşmeyen kayıtların sayısı ve örnekleri dökümde
- **Aynı `company_id`'ye bağlı kayıt sayısı dağılımı** raporlanır — 1 firmaya
  50 kayıt bağlandıysa normalizasyon hatalıdır, erken yakalanır

## 5. Uyarılar

1. **Ünvan eşlemesi risklidir.** "ÖZ YILMAZ MAKİNA SAN. TİC. LTD. ŞTİ." ile
   "ÖZ YILMAZ MAKİNA" aynı firma olabilir de olmayabilir de. Bulanık eşleme
   (fuzzy) **bu turda yapılmayacak** — birebir normalize eşleşme yeter, gerisi
   boş kalır. Yanlış bağ, boş bağdan **daha zararlıdır**: yanlış firmaya yanlış
   NACE yazılır ve bir daha kimse fark etmez.
2. **Yazma öncesi yedek.** Canlı DB'de 14003 firma var (D-234 turunda da
   söylendi). Kolon ekleme geri alınabilir, yanlış eşleme geri alınamaz.
3. Bu bağ kurulduktan sonra COKLU-01, TEMIZ-01 (B seviyesi) ve SEKTOR-01 aynı
   anda açılabilir hale gelir — sıra buradan geçiyor.

## 6. BRİF HATASI İTİRAFI (ihsan)

COKLU-01 brifini yazarken önkoşul olarak yalnız `VERI-NACE-SOZLUK-01`'i
koydum. Firma↔kaynak bağının **hiç olmadığını** kontrol etmedim; brifin 3.
maddesi "company_industries'e yaz" diyor ama "firmayı nasıl bulacaksın"
sorusunu boş bıraktı. Utku brife uydu, brif eksikti. Bu görev o eksiğin
karşılığıdır.

---

*ponytail: birebir normalize ünvan eşlemesi. Skipped: bulanık eşleme (fuzzy /
trigram), eklenmesi gereken an — birebir eşleşme %90'ın altında kalır ve
eşleşmeyen kayıtlardaki veri (NACE, sektör, iletişim) gerçekten gerekli olursa.*
