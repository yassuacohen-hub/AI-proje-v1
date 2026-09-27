# Brif — VERI-KAYNAK-BAG-01: Firma↔kaynak bağı (`source_records.company_id`)

**Başlık:** [VERI] Firma↔kaynak bağını kur (`source_records.company_id`) + NACE yeniden türetme (4s)
**Öncelik:** P0 · **Kit:** `VERI` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Süre:** 4s · **Veren:** ihsan
**Önkoşul:** yok — bu kendisi önkoşul
**Blokladığı:** `VERI-NACE-COKLU-01`, `VERI-NACE-TEMIZ-01` (B seviyesi),
`VERI-SEKTOR-01`, `VERI-KAYNAK-SIZINTI-01`

---

## Neden
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

## Adımlar
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

## Kabul kriteri
- `source_records.company_id` kolonu var, FK tanımlı, nullable
- Dolu `company_id` oranı **raporlanır** (hedef: > %90; ETL 1:1 yazdıysa
  ulaşılabilir)
- `company_id` dolu olan hiçbir satırda `companies`'te karşılığı olmayan id yok
  (FK zaten engeller, test yine de koşacak)
- Belirsiz/eşleşmeyen kayıtların sayısı ve örnekleri dökümde
- **Aynı `company_id`'ye bağlı kayıt sayısı dağılımı** raporlanır — 1 firmaya
  50 kayıt bağlandıysa normalizasyon hatalıdır, erken yakalanır

## 4b. EK KAPSAM — TEMIZ-01 denetiminden devredildi (2026-09-27)

TEMIZ-01 sayaç kirlenmesini temizledi (sayaç biçimli değer artık **0**) ama
`nace_code`'un asıl yanlışlığı duruyor. Canlı ölçüm:

```
10.11 (et işleme)        → 911 firma: '3E ELEKTRO OPTİK', 'ACAR FAKTORİNG A.Ş.'
29.10 (motorlu taşıt)    → 1882 firma: '3S DEMİR ÇELİK', '312 PROJE TASARIM'
```

Bu sayılar temizlik öncesiyle **birebir aynı** — 7642 NN.NN kayda dokunulmamış.
Sayaç değeri ('1163') bariz saçmaydı; NN.NN biçimli yanlış kod **sessizce doğru
görünür**, kesişim motoruna ve müşteriye yanlış cevap olarak sızar. Daha
tehlikelidir.

Bağ kurulduktan sonra, aynı iş emri içinde:

1. **7642 NN.NN kayıt `raw_nace`'ten yeniden türetilecek.** Mevcut değer
   güvenilmez sayılacak — üzerine yazılacak, korunmayacak.
2. **84 yetim kod → 4146 firma** (`companies.nace_code` değeri 2097 satırlık
   `nace_codes` sözlüğünde yok): sözlüğe göre eşlenecek, eşlenemiyorsa **NULL'a
   çekilecek**. Uydurma kod yazılmayacak.
3. **35 altı haneli kayıt** (`'62.10.00'` 26, `'28.99.99'` 9) ve **`'98'` (16)**:
   4 haneli sınıfa kırpılacak veya NULL. Kolon 4 hane bekliyor.
4. Sonrasında `nace_code` üzerine `nace_codes(nace_code)` referanslı **yabancı
   anahtar kısıtı** önerisi raporlanacak — şu anda hiçbir kısıt yok, yani bu
   kusur yarın tekrar üretilebilir. Kısıt eklenmesi ayrı karar, ölçüm bu turda.

Kabul ölçütü eki: yetim kod sayısı **0**'a inecek (eşlenmiş veya NULL), altı
haneli/iki haneli kalan **0**, ve 10.11/29.10 örnek firmaları sektörüyle tutarlı
olacak (et işleme kodunda faktoring şirketi kalmayacak).

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

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- `source_records` tablosunda `company_id` kolonu **yok** varsayıldı (13 kolon listesi brifte). Varsa **dur**, panoya sorun aç.
- `source_records.raw_tax_number` 617 dolu, `companies.tax_number` 40 dolu, JOIN tavanı **33** varsayıldı. Sayı farklıysa **dur**, yeniden ölç.
- `source_records` 14000 / `companies` 14003 satır varsayıldı; ETL 1:1 yazmış kabul edildi. Oran bozuksa eşleme planı geçersiz, KAHİN'e sor.
- `companies.nace_code` içinde 7642 kayıt NN.NN biçiminde ve **yanlış** varsayıldı (`10.11` → 911 firma, `29.10` → 1882 firma). Doğrula, sonra üzerine yaz.
- 84 yetim kod → 4146 firma, `nace_codes` sözlüğü 2097 satır varsayıldı. Sözlük boş/eksikse **dur** — SOZLUK-01 bitmemiş demektir.
- Eşik: dolu `company_id` oranı hedefi **%90**. Kodda başka eşik varsa KAHİN'e sor.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-KAYNAK-BAG-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-KAYNAK-BAG-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-KAYNAK-BAG-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-KAYNAK-BAG-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
