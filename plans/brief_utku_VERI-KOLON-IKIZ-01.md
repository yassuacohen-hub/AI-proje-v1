# Brif — VERI-KOLON-IKIZ-01 (P0)

**Başlık:** [VERI] Kolon ikizlerini birleştir — eşleştirme motoru vergi numaralarının %95'ini görmüyor (3s)
**Öncelik:** P0 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/db/migrations/0023_kolon_ikiz_birlestir.sql`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Mod:** code · **Süre:** 3s · **Kaynak:** ihsan (KAHİN denetimi 2026-09-27, VERI-HAYALET-TEMIZ-01 kapanışında çıktı)

## Neden

`companies` tablosunda aynı anlamı taşıyan iki kolon çifti var. Bu sadece
dağınıklık değil — **eşleştirme motoru sessizce yanlış çalışıyor.**

### Kanıt (canlı Supabase, ölçüldü 2026-09-27)

```
vergi_no dolu     : 761
tax_number dolu   :  40
kesisim           :  31
birlesim          : 770

tax_number BOS ama vergi_no DOLU: 730   <-- kod bu 730 firmayi vergi numarasiz saniyor
```

### Kod hangi kolonu okuyor?

Tarama sonucu: **kod neredeyse tamamen `tax_number` okuyor**, veri ise
`vergi_no`'da duruyor.

| dosya | ne yapıyor | sonuç |
|---|---|---|
| `etl/nace_coklu_yaz.py:119` | `JOIN source_records sr ON sr.raw_tax_number = c.tax_number` | **730 firma JOIN'e girmiyor** |
| `etl/entity_resolution_db.py:61` | `WHERE tax_number IS NOT NULL` → VKN indeksi | indeks 761 yerine **40 kayıtla** kuruluyor |
| `etl/entity_resolution_optimized.py:54` | `vkn_index = {c["tax_number"]: ...}` | aynı kusur |
| `etl/kaynak_bagla.py:95` | `SELECT ... tax_number` | aynı kusur |
| `etl/mersis_api.py:216` | `WHERE tax_number IS NOT NULL` | 730 firma MERSİS'e hiç sorulmuyor |
| `etl/multi_osb_merger.py:54` | `ON CONFLICT (tax_number)` | çakışma yakalanmıyor |
| `intelligence/.../normalizer.py:118` | iş ilanı → firma eşleştirme | en güvenilir eşleşme yolu (VKN, güven 1.0) çalışmıyor |
| `search/engine.py:63` | `row.get("tax_number") or row.get("vergi_no")` | ✅ doğru, iki kolonu da okuyor |
| `etl/quality_recalc.py:17` | `row.get("tax_number") or row.get("vergi_no")` | ✅ doğru |

Yani **`COALESCE` yazmayı hatırlayan 2 dosya doğru, hatırlamayan 7 dosya
sessizce eksik çalışıyor.** Hata vermiyorlar, sadece az sayıyorlar — en kötü
hata türü.

Web tarafı aynı desen: `website_domain` 5397 dolu, `web_sitesi` 5049 dolu.
Kod ağırlıklı `website_domain` okuyor.

### Neden P0

FAZ 2 (`ZEKA-CUSTOMER-BRAIN-01`) firma eşleştirmesi üzerine kurulacak. Bugün
eşleştirme motoru vergi numarasının **%95'ini görmüyor**. Bu düzeltilmeden
müşteri beyni yanlış veri üzerine inşa edilir ve hata ileride ayıklanamaz.

## Doğrulanacak varsayım

**Varsayım:** `vergi_no`'daki 761 değer ile `tax_number`'daki 40 değer aynı
türden veridir (ikisi de 10-11 haneli VKN) ve kesişen 31 kayıtta **aynı**
değeri taşırlar.

## Faz A SONUCU — VARSAYIM ÇÖKTÜ, İŞ DURDU (ölçüldü 2026-09-27)

```
1_cakisma_vkn                   : 1        (kesisim 31'de 1 catisma)
2_tax_number_gecersiz_bicim     : 23   / 40
2b_vergi_no_gecersiz_bicim      : 633  / 761
3_birlesim_tekil_mi             : 9        (9 mukerrer deger!)
4_cakisma_web                   : 1    / 5000 kesisim

GECERLI VKN (^[1-9][0-9]{9,10}$):
  tax_number : 17
  vergi_no   : 128
  birlesim   : 128
```

### Kusur 1 — `vergi_no` kolonu VKN değil (P0)

761 değerin **633'ü geçerli VKN biçiminde değil.** Uzunluk dağılımı:

```
uzunluk  6: 526    <-- OSB uye/parsel numarasi, VKN degil
uzunluk  5:  78
uzunluk 10:  12    (ornek: '1105-BEYP.' -> harf iceriyor)
uzunluk  4:   5
uzunluk 11:   5    (ornek: '08507243387' -> 0 ile basliyor, gecersiz)
uzunluk  9:   5
uzunluk 12:   1
uzunluk 14:   1
```

**Gerçek vergi numarası sayısı 774 değil, 128.** Kolon yanlış isimlendirilmiş
ve içine OSB üye numarası doldurulmuş. Bu, önceki brifteki "774 vergi_no"
sayısının **baştan anlamsız** olduğunu gösteriyor — sayılan şey vergi numarası
değildi.

### Kusur 2 — `website_domain` firmaların değil, OSB'nin sitesi (P0)

```
http://www.isim.org.tr                  x2143   <-- Ivedik OSB'nin kendi sitesi
https://www.ostimistihdam.com            x474   <-- OSTIM istihdam portali
https://www.ostimonline.com/Home/...      x49   <-- OSTIM portali
```

**5397 "web sitesi"nin ~2660'ı (yaklaşık yarısı) firmanın sitesi değil**,
kazıyıcının yakaladığı OSB portal adresi. Kalite puanı bu firmalara "web
sitesi var" diye 10 puan vermiş. `VERI-IVEDIK-YENIDEN-01` ile aynı kök neden.

### Kusur 3 — `tax_number` UNIQUE, birleştirme çakışacak

`companies_tax_number_key (u)` kısıtı **var**. Ama birleşimde **9 mükerrer
değer** çıkıyor (`'151113' x2`, `'233263' x2`, ...). Yani planlanan
`UPDATE ... COALESCE` migration'ı **UNIQUE ihlaliyle patlar**. İyi haber:
kısıt veriyi koruyor, kötü haber: iş bu haliyle yürümez.

### Karar noktası — ÜRÜN SAHİBİNE

Bu iş yazıldığı gibi yapılamaz. Üç seçenek:

**A) Kolonları birleştirmeden önce içeriği temizle.** `vergi_no`'daki 633
geçersiz değeri ayrı kolona taşı (`osb_uye_no`), sadece 128 geçerli VKN'yi
`tax_number`'da topla. Web tarafında OSB portal adreslerini `NULL`'a çek.
Dürüst sonuç: 128 VKN + ~2700 gerçek web sitesi. Süre 3s → **5s**.

**B) Sadece kolon birleştir, içerik kirliliğine dokunma.** Hızlı ama
`tax_number` içine OSB üye numarası girer ve eşleştirme motoru yanlış
eşleştirme yapmaya başlar — bugünkü "hiç eşleştirmiyor" halinden **daha kötü**.
Önerilmiyor.

**C) İşi ikiye ayır.** `VERI-KOLON-IKIZ-01` sadece web tarafını yapar;
vergi numarası temizliği `VERI-VKN-TEMIZ-01` olarak ayrılır. Faz 2 için ikisi
de ön koşul olduğundan toplam süre değişmez, izlenebilirlik artar.

**KAHİN önerisi: C.** İki farklı kök neden var (kazıyıcı OSB portalını firma
sitesi sanıyor / kolon yanlış isimlendirilip yanlış veri dolduruluyor); tek
brifte karışırlar.

## Adımlar

### Faz A — ölç, migration yazma ✅ BİTTİ

1. ✅ **Çakışma ölçümü:** kesişen 31 kayıtta 1 çatışma
2. ✅ **Biçim ölçümü:** `vergi_no` 633/761 geçersiz, `tax_number` 23/40 geçersiz
3. ✅ **UNIQUE kısıt ölçümü:** `companies_tax_number_key` var, 9 mükerrer çakışacak
4. ✅ **Web tarafı ölçümü:** 1 değer çatışması, ama ~2660 kayıt OSB portal adresi

**Sonuç: iş durdu, ürün sahibi kararı bekleniyor** (yukarıdaki A/B/C).

### Faz B — birleştir (KARAR SONRASI, şu an geçersiz)

Birleştirme yönü: **`tax_number` ve `website_domain` kalır** (kod bunları
bekliyor), `vergi_no` ve `web_sitesi` düşürülür.

5. **Yedek al** (D-244 zorunlu): `yedekler/companies_<zaman>.jsonl`, satır
   sayısı doğrulanır
6. **Migration `0023_kolon_ikiz_birlestir.sql`:**
   - `UPDATE companies SET tax_number = COALESCE(NULLIF(TRIM(tax_number),''), NULLIF(TRIM(vergi_no),''))`
   - `UPDATE companies SET website_domain = COALESCE(NULLIF(TRIM(website_domain),''), NULLIF(TRIM(web_sitesi),''))`
   - `ALTER TABLE companies DROP COLUMN vergi_no, DROP COLUMN web_sitesi`
7. **Kod temizliği** — `vergi_no` / `web_sitesi` okuyan yerleri tek isme çek:
   - `etl/hayalet_kayit_temizle.py` (dataclass alanları + SELECT + UPDATE) —
     11 testi de güncellenir
   - `etl/quality_recalc.py`, `engine/quality_gate.py` (`or` zincirleri sadeleşir)
   - `search/engine.py` (SELECT + WHERE + sonuç eşlemesi)
   - `dashboard/perf_monitor.py` (4 ayrı SELECT + arama WHERE)
   - **DİKKAT:** scraper'lardaki `web_sitesi` alanı DB kolonu değil, kazıyıcı
     çıktısının alan adı — **dokunulmaz**. Yalnız DB yazımında eşlenir.
8. **Doğrulama sorgusu** çalıştır ve çıktıyı brife yapıştır.

## Kabul kriteri

- `select count(*) from companies where tax_number is not null` = **770**
  (birleşim; iş öncesi 40 idi)
- `select count(*) from companies where website_domain is not null` ≥ **5397**
- `vergi_no` ve `web_sitesi` kolonları `information_schema.columns`'ta **yok**
- `yedekler/` altında migration öncesi dosya var, satır sayısı = 9412 (D-244)
- Kolon adı taraması: `src/` altında DB kolonu olarak `vergi_no`/`web_sitesi`
  okuyan sorgu kalmamış (scraper alan adları hariç)
- Testler yeşil: `python -m pytest tests/ -q`

## Riskler

- **Kolon düşürmek geri alınamaz.** Yedek alınmadan migration çalıştırılmaz (D-244).
- `hayalet_kayit_temizle.py` kilitli dosyaydı; bu iş onun alan listesini
  değiştiriyor — 11 testi de güncellenmeli.
- `multi_osb_merger.py:54` `ON CONFLICT (tax_number)` çalışması için
  `tax_number` üzerinde UNIQUE kısıt gerekiyor; şu an var mı **ölçülmedi**
  (Faz A adım 3). Yoksa ayrı karar konusudur — 770 dolu değerin tekilliği
  doğrulanmadan kısıt eklenmez.

## Ajan chat zorunlu

Faz A ölçümü bitince ve iş teslim edilirken ürün sahibine haber verilir:

```bash
python ajan_chat.py gonder --kimden utku --kime ihsan --konu "VERI-KOLON-IKIZ-01 Faz A olcumu" --mesaj "<cakisma sonucu>"
```

Faz A'da çakışma çıkarsa iş **durur**, mesaj gönderilir, cevap beklenir.

## Teslim

- Faz A ölçüm çıktısı bu brife yapıştırılmış
- Migration dosyası `src/company_master/db/migrations/0023_kolon_ikiz_birlestir.sql`
- Yedek dosyası yolu ve satır sayısı brifte yazılı (D-244)
- Kabul kriterindeki sorguların çıktısı brifte yazılı
- `hubs/VERI_KALITESI_HUB.md` "Kapanan işler" satırı eklenmiş (B-14)
- `python -m pytest tests/ -q` yeşil
- `python scripts/brief_denetim.py plans/brief_utku_VERI-KOLON-IKIZ-01.md` UYUMLU

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[AGENTS]]
- [[plans/brief_utku_VERI-HAYALET-TEMIZ-01]]
