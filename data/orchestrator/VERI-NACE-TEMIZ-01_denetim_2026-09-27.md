---
tur: denetim-raporu
gorev: VERI-NACE-TEMIZ-01
denetci: ihsan
tarih: 2026-09-27
karar: SARTLI-KABUL
---

# VERI-NACE-TEMIZ-01 Denetimi — ŞARTLI KABUL

Ölçüm canlı Supabase üzerinde yapıldı (D-236 gereği SQLite yedeği değil).

## İstenen iş yapıldı

| ölçüt | önce | sonra | sonuç |
|-------|------|-------|-------|
| sayaç biçimli değer ('1163','794','757','780') | vardı | **0** | ✅ temiz |
| boş/NULL | — | 5658 | sayaçlar NULL'a çevrilmiş |

Brifin kapsamı "OSTİM sektör sayacı kirlenmesi"ydi; o kapsam **kapandı**.

## Ama asıl yanlışlık yerinde duruyor — YENİ BULGU

`nace_code` kolonunda 7642 firmada NN.NN biçimli değer var. Biçim geçerli, **içerik yanlış**:

```
10.11 (= et işleme ve muhafazası) → 911 firma:
  '3E ELEKTRO OPTİK SİSTEMLER SAN. VE TİC. A.Ş.'
  'A ARTI ULUSLARARASI YEMİNLİ DİL ÇEVİRİ HİZM. LTD. ŞTİ.'
  'ACAR FAKTORİNG A.Ş.'

29.10 (= motorlu kara taşıtı imalatı) → 1882 firma:
  '3S DEMİR ÇELİK SAN. TİC. LTD. ŞTİ.'
  '312 PROJE TASARIM UYGULAMA SAN. VE TİC. LTD. ŞTİ.'
```

Bu sayılar **temizlik öncesiyle birebir aynı** (10.11→911, 29.10→1882). Yani temizlik bu 7642 kayda hiç dokunmadı.

**Bu daha tehlikeli bir kusur.** Sayaç değeri ('1163') bariz saçmaydı, gözle yakalanıyordu. NN.NN biçimli yanlış kod sessizce doğru görünür — arama sonucuna, kesişim motoruna, müşteriye yanlış cevap olarak sızar.

## İkincil kusurlar

1. **6 haneli kodlar (35 satır):** `'62.10.00'` 26, `'28.99.99'` 9. Kolon 4 haneli sınıf bekliyor; ya kırpılmalı ya ayrı kolona alınmalı.
2. **Yetim kod (84 kod → 4146 firma):** `companies.nace_code` değeri `nace_codes` sözlüğünde yok. Sözlük 2097 satır. Yabancı anahtar kısıtı olmadığı için sessizce duruyor.
3. **`'98'` (16 satır):** iki haneli, ne kısım ne sınıf — geçersiz.

## Şart

TEMIZ-01 kendi kapsamında kabul edildi. Şu iki iş **VERI-KAYNAK-BAG-01** kapsamına ekleniyor (aynı kök: `source_records.company_id` bağı kurulmadan doğru NACE türetilemez):

- 7642 NN.NN kaydın `raw_nace`'ten **yeniden türetilmesi** — mevcut değer güvenilmez sayılacak
- 84 yetim kod + 35 altı haneli + `'98'` → sözlüğe göre eşlenecek veya NULL'a çekilecek, uydurulmayacak

`nace_code` üzerinde `nace_codes(nace_code)` referanslı yabancı anahtar kısıtı istenmesi ayrıca değerlendirilecek — şu anda hiçbir kısıt yok, yani kusur tekrar üretilebilir.

## İlgili Nodlar

- [[AGENTS]]
- [[plans/brief_utku_VERI-KAYNAK-BAG-01]]
