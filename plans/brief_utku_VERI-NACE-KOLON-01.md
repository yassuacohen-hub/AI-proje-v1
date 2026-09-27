# Brif — VERI-NACE-KOLON-01: nace_validity kolon karışmasını düzelt → 86 satır

**Sahip:** utku · **Öncelik:** P2 · **Süre:** 1s · **Veren:** ihsan
**Önkoşul:** yok — bağımsız, tek başına yapılabilir
**Kanıt tabanı:** `plans/brief_utku_VERI-NACE-SOZLUK-01.md` bölüm 1

---

## 1. Ölçülen hata (canlı Supabase)

`companies.nace_validity` kolonuna **NACE kodu yazılmış**. 86 satır:

```
'41.00.02'   '35.12.00'   ...
```

Bu kolon geçerlilik **etiketi** taşımalı (`unknown`, `medium`, `fallback` gibi),
kod taşımamalı. Kolon karışması — kazıma/yazma sırasında iki alan takas edilmiş.

Doğru değerlerin dağılımı (kalan satırlarda kolon düzgün kullanılmış), yani
kolonun amacı belli; sadece bu 86 satır bozuk.

## 2. Yapılacak

1. `nace_validity` içinde NACE kodu deseni (`\d{2}\.\d{2}`) taşıyan satırları bul.
2. Her biri için: `nace_code` boş mu dolu mu **kontrol et**.
   - `nace_code` boşsa → kodu oraya taşı, `nace_validity`'ye uygun etiket yaz
   - `nace_code` doluysa → iki kod çelişiyor mu bak. Çelişiyorsa **karar verme**,
     dök ve rapora yaz. Hangisinin doğru olduğunu uydurmayın.
3. `nace_validity`'yi geçerli etiket kümesine çek. Mevcut kullanılan etiketleri
   önce sorgulayıp öğrenin — yeni etiket icat etmeyin.

## 3. Kabul ölçütü (test)

- `nace_validity` içinde NACE kodu deseni taşıyan satır **0**
- `nace_validity` değerlerinin tamamı bilinen etiket kümesinde
- Taşınan / çelişen satır sayıları raporda yazılı

## 4. Neden P2

86 satır — küçük. Ama küçük olduğu için ertelenmemeli: kolon karışması varsa
aynı hatayı üreten kod hâlâ çalışıyor olabilir. Düzeltirken **kaynağını da
bulun**: hangi yazıcı bu iki alanı takas ediyor? Sadece veriyi düzeltip kodu
bırakırsanız 86 satır yarın 200 olur.

---

*ponytail: desen ile bulup taşıma. Skipped: yazıcı kodunda kalıcı kolon
doğrulama (DB CHECK kısıtı), eklenmesi gereken an — aynı karışma ikinci kez
görülürse.*
