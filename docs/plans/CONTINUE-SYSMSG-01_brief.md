# CONTINUE-SYSMSG-01 — Continue IDE system message (roo, P2)

**Durum:** TAMAM — KAHİN (Ürün Sahibi) onayladı 2026-09-18, `~/.continue/config.json`'a yazıldı.
**Metin:** [`docs/continue_system_prompt.md`](../continue_system_prompt.md)

## Kapsam
Continue IDE eklentisine proje kimliği + Türkçe dil kuralı veren `systemMessage` yazmak.
**Continue reposuna PR YOK** — yalnız kendi `~/.continue/config.json` yapılandırmamız.

## Referans
`core/llm/defaultSystemMessages.ts` (https://github.com/continuedev/continue/blob/main/core/llm/defaultSystemMessages.ts)
Continue'nun varsayılanı agent/edit/plan modları için araç talimatı içerir. Bizde Continue **chat + autocomplete**
olarak kullanılıyor → araç talimatı alınmadı, yalnız dil/kimlik/bağlam katmanı yazıldı.

## Kimlik — Merve (KAHİN kararı)
Kadın yazılımcı kimliği, espirili üslup, az teknik kelime. Hitap: **KAHİN (Ürün Sahibi)** — "sahip" yasak.
Her cevap kısa özet tablosuyla biter. Eleştirileri `docs/ROO_ELESTIRI_NOTLARI.md` formatında verir.
`abrakadabra` = en yetkili ajan modu; yine de dosya yazmaz, komut çalıştırmaz (karar söyler, roo uygular).
Rol sınırı: dosya yazmaz, görev almaz, komut çalıştırmaz → kilo/cline/roo ile karışmaz.

## Yapıldı
1. ✅ `docs/continue_config.json` kök seviyesine `"systemMessage"` eklendi (3585 karakter).
2. ✅ `yapilandirma_uret()` satır 80 kök alanları `models` hariç aynen taşıyor → kod değişikliği gerekmedi.
3. ✅ `python scripts/continue_config_kur.py` → 19 model + systemMessage yazıldı (`.bak` alındı).
4. `docs/raporlar/roo_code/TAKIP.md` §6 günlük satırı.

## D-48 kontrolü
Prompt'ta `max_tokens`, reasoning budget veya düşünme kısıtı YOK. Yalnız dil + üslup + bağlam. Uyumlu.
