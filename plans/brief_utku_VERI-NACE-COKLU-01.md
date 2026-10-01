# Brif — VERI-NACE-COKLU-01: Çoklu NACE kodunu yaz → company_industries.is_primary

**Başlık:** [VERI] Çoklu NACE kodunu `company_industries.is_primary` ile yaz (3s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/nace_coklu_yaz.py`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Süre:** 3s · **Veren:** ihsan
**Önkoşul:** `VERI-NACE-SOZLUK-01` (referans liste olmadan başlanamaz)
**Kanıt tabanı:** `plans/brief_utku_VERI-NACE-SOZLUK-01.md` bölüm 1

---

## Neden

Ürün sahibi kararı:

> "Bir işletmenin birden fazla NACE kodu olabilir, bu kanuni bir durum. Ana NACE
> kodu esas alınarak varsa ek NACE kodları da toplanabilir ve tabloda belirtilir."

Bu bir iş kuralı, teknik tercih değil: Türkiye'de bir firma faaliyet
konularından birini **ana faaliyet** olarak beyan eder, yanında ek faaliyet
kodları taşıyabilir. Tek kolonda tek kod tutmak bu gerçeği kaybediyor.

Devam kararı (aynı oturum):

> "1 firmanın 3 tane NACE kodu varsa 3 iş yapıyordur demektir. Hepsi firmanın
> kalite verisinde anlamlı bir şey ifade eder, firmayı daha iyi optimize
> edebiliriz, firma detaylarını genişletiriz."

Yani çoklu NACE iki yerde kullanılacak: **firma detay sayfasında görünür bilgi**
ve **kalite/zenginlik göstergesi**.

### ⚠ İtirazım — "çok kod = iyi firma" sayılmamalı

Ürün sahibinin yönü doğru ama bir tuzak var, şimdiden söylüyorum:

1. **Kod sayısı kalite değil, kapsam.** 3 NACE kodu olan firma 3 iş yapıyor
   olabilir; ama tek işe odaklanmış firma daha *kaliteli* olabilir. Kalite
   puanına "kod sayısı" ham olarak eklenirse çeşitlenmiş firmalar haksız
   avantaj kazanır. Doğru kullanım: **veri zenginliği** (bu firma hakkında ne
   kadar biliyoruz) ile **iş kapsamı** (ne kadar iş yapıyor) ayrı ölçülmeli.
2. **Eksik veri ceza olmamalı.** Bir firmanın tek kodu olması, gerçekten tek iş
   yaptığı için mi, yoksa ek kodlarını **biz toplayamadığımız** için mi? Şu an
   ikincisi baskın (`company_industries` 0 satır). Bunu ayırt edemediğimiz
   sürece kod sayısını kaliteye çevirmek, kendi eksiğimizi firmaya fatura eder.
3. Öneri: önce **sadece göster** (firma detayında liste), kalite puanına
   bağlamayı ölçüm eline geçtikten sonra karar ver. Kaç firmada gerçekten çoklu
   kod var, bilmeden ağırlık atanamaz.

## 2. Ölçülen durum

Şema bu ihtiyacı **zaten karşılıyor** — kimse kullanmamış:

| Tablo / kolon | Durum |
|---------------|-------|
| `company_industries` | **0 satır** (tablo var, boş) |
| `company_industries.is_primary` | kolon **var** — ana/ek ayrımı için hazır |
| `companies.nace_code` | 8900 dolu ama **tek değer** — ek kod yeri yok |
| `source_records.raw_nace` | 7595 dolu — ham kaynak değerleri elde |

Yani yeni tablo/kolon açmaya gerek yok. Boş bırakılmış yapı doldurulacak.

## Adımlar
1. `source_records.raw_nace` içindeki değerleri ayrıştır. Çoklu kod tek hücrede
   ayırıcıyla gelmiş olabilir (`,` `;` `/` `|`) — **önce ölç**, kaç kayıtta
   birden fazla kod var, hangi ayırıcı kullanılmış. Ölçmeden kural yazma.
2. Her kodu `nace_codes` referansına karşı doğrula. Listede yoksa **yazma**,
   ayrı bir "eşleşmeyen" dökümüne düş — sessizce atma.
3. `company_industries`'e yaz: ana kod `is_primary=true`, diğerleri `false`.
   Bir firmada en fazla **bir** `is_primary=true` olacak.
4. `companies.nace_code` ana kodla tutarlı kalsın (özet/hız kolonu olarak).

## Kabul kriteri
- `company_industries` satır sayısı > 0
- Hiçbir firmada 1'den fazla `is_primary=true` yok (tek sorgu ile doğrulanır)
- `company_industries.nace_code` değerlerinin **tamamı** `nace_codes`'ta var
  (yetim kod yok)
- Çoklu koda sahip en az bir firma örneği elle bakıldığında doğru

## 5. Uyarı

Ölçmeden önce "raw_nace çoklu kod içeriyor" diye varsaymayın. 7595 kaydın
hepsinde tek kod da olabilir; o durumda çoklu NACE **şimdilik veri olarak
yok** demektir ve iş, gelecekte gelecek kaynaklar için altyapı hazırlığına
dönüşür. Bu da geçerli bir sonuç — ama ölçülerek söylenmeli.

## 6. DENETİM (2. tur) — bu iş REDDEDİLDİ, sebebi utku değil

Utku `src/company_master/etl/nace_coklu_yaz.py` yazdı ve çalıştırdı. Canlı
veritabanında ölçtüm:

| Ölçüm | Değer |
|-------|-------|
| `company_industries` satır | **21** |
| 14003 firmanın kapsanma oranı | **%0.15** |
| `companies.tax_number` DOLU | **40** |
| `source_records.raw_tax_number` DOLU | 617 |
| JOIN (`raw_tax_number = tax_number`) eşleşmesi | **33** ← yazılabilecek azami |

Kabul ölçütü 1 ("satır > 0") teknik olarak sağlandı ama **anlamsız**: 7595 dolu
`raw_nace`'in %99.6'sı yazılamadı. Kod doğru çalışıyor; **bağlanacak anahtar yok**.

### 6.1 ~~Kök neden — şemada firma↔kaynak bağı YOK~~ — BU TEŞHİS YANLIŞTI (2026-10-01)

> **DÜZELTME (ihsan, 2026-10-01):** Aşağıdaki bölüm **geçersizdir.**
> `source_records.company_id` kolonu **vardır** — D-263 ile 2026-09-28'de kuruldu.
> Bu yüzden verdiğim RED kararı **yanlış gerekçeliydi; utku haklıydı.**
> Geçerli tavan 33 değil **7065 satır** → bkz. §6.4. Hatam ajan chat'e yazıldı (#16).
> Bölüm tarihsel kayıt olarak duruyor, karar dayanağı olarak **kullanılmaz.**

`source_records` kolonları: `source_record_id, source_id, external_id, raw_name,
raw_address, raw_phone, raw_email, raw_website, raw_tax_number, raw_nace,
raw_payload, collected_at, content_hash`.

**`company_id` kolonu yok.** 14000 ham kaydın hangi firmaya ait olduğu
veritabanında hiç kayıtlı değil. Utku elindeki tek alanla (`raw_tax_number`) bağ
kurmaya çalıştı; o da 40 firmada dolu → tavan 33.

### 6.2 BENİM HATAM (brif)

Bu brifin 3. maddesi *"her kodu nace_codes'a karşı doğrula"* diyor ama **firmaya
nasıl bağlanacağını hiç söylemiyor**. Önkoşul olarak yalnız SOZLUK-01'i yazdım;
asıl önkoşul olan firma↔kaynak bağını atladım. Utku brife uydu, brif eksikti.

### 6.3 Kod kusurları (düzeltilecek)

1. **`.env` mutlak yolu gömülü** — `C:/Huginn Data Projesi/...`. Başka makinede
   veya CI'da çalışmaz. `load_dotenv()` yalın çağrılmalı.
2. **Tekrar** — `import` ve `create_engine` blokları dosyada iki kez
   (satır ~9-38 ve ~96-99).

### 6.4 Yeni sıra (D-263 güncellemesi, 2026-10-01)

~~COKLU-01 askıya alındı~~ — **artık değil.** `VERI-KAYNAK-BAG-01` D-263 ile
2026-09-28'de KAPANDI (`source_records.company_id` kolonu + trigger kuruldu).
Canlı ölçüm (2026-10-01): `company_id` VE `raw_nace` ikisi de dolu = **7065
satır** — eski 33 tavanının yerine geçen gerçek tavan budur. Önkoşul bitti,
iş başlayabilir.

---

*ponytail: raw_nace ayrıştırma. Skipped: NACE kod geçerlilik tarihi (bir kod ne
zamandan beri firmada), eklenmesi gereken an — firma faaliyet değişikliği
geçmişi sorulduğunda.*

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- Önkoşul `VERI-KAYNAK-BAG-01` **bitmiş** varsayıldı — `source_records.company_id` dolu olmalı. Boşsa **dur**, bu iş başlamaz (ilk turda %0.15 ile reddedildi).
- `company_industries` tablosunda `nace_code` ve `is_primary` kolonları varsayıldı. Yoksa **dur**, panoya sorun aç.
- `source_records.raw_nace` alanında birden fazla kod bulunduğu varsayıldı. Tek kod varsa çoklu yazım gereksiz — ölç, raporla.
- İtiraz kayda geçti: **çok kod = iyi firma değil**. Kod sayısı bir kalite/önem puanı olarak kullanılmayacak.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-NACE-COKLU-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-NACE-COKLU-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-NACE-COKLU-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-NACE-COKLU-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
