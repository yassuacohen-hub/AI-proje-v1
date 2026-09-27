# Brif — VERI-NACE-TEMIZ-01: Sektör sayacı kirlenmesini düzelt → nace_code temizliği

**Sahip:** utku · **Öncelik:** P1 · **Süre:** 2s · **Veren:** ihsan
**Önkoşul:** `VERI-NACE-SOZLUK-01` (geçerlilik kontrolü referans listeye bağlı)
**Kanıt tabanı:** `plans/brief_utku_VERI-NACE-SOZLUK-01.md` bölüm 1

---

## 1. Ölçülen kirlilik (canlı Supabase)

`companies.nace_code` içinde NACE kodu **olmayan** değerler var:

| Değer | Firma | Ne olduğu |
|-------|-------|-----------|
| `1163` | 168 | OSTİM sektör sayfasındaki firma sayacı |
| `410` | 68 | aynı |
| `780` | 62 | aynı |
| `794` | 54 | aynı |
| `757` | 53 | aynı |

Bunlar kazıma sırasında sayfadaki **sektör firma sayısı** rakamının NACE kodu
sanılıp yazılmasından geliyor. Tamamı `nace_source='unknown'`.

Ayırt edici işaret: geçerli NACE kodları **noktalı** (`47.79.04`, `10.11`),
bu değerler **noktasız düz sayı**. Ama sadece desene güvenmeyin — `nace_codes`
referansına karşı doğrulamak kesin yol.

## 2. Yapılacak

1. `companies.nace_code` değerlerini `nace_codes` tablosuna karşı kontrol et.
2. Eşleşmeyenleri **silmeden önce** dök: kaç satır, hangi değerler, hangi
   `nace_source`. Sayıyı rapora yaz.
3. Eşleşmeyenleri `NULL`'a çek ve `nace_source='invalid_cleared'` işaretle.
   **Kaydı silme** — firma duruyor, sadece yanlış kod gidiyor.
4. `sector_default` / `fallback` kökenli kodlara **dokunmayın** bu görevde;
   onlar yanlış ama "uydurma varsayılan" başka bir problem (bkz. keşif notu).
   Bu görev sadece **NACE olmayan çöp** değerleri hedefliyor.

## 3. Kabul ölçütü (test)

- Temizlik sonrası `nace_code` değerlerinin **tamamı** `nace_codes`'ta var
- Firma sayısı değişmemiş (14003 → 14003) — hiçbir kayıt silinmedi
- Temizlenen satır sayısı raporda yazılı

## 4. Uyarı — yazma öncesi yedek

Canlı DB'de 14003 firma. Toplu `UPDATE` öncesi yedek alın, önce 100 satırlık
parti deneyin. Geri alınamaz bir hata bu görevde en olası risk.

---

*ponytail: geçersiz kodu NULL'lama. Skipped: doğru kodu yeniden bulma
(eşleştirme) — o VERI-NACE-COKLU-01 ve ünvan kesişimi işi.*
