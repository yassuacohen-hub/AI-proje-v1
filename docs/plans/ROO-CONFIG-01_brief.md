# ROO-CONFIG-01 — Roo Code IDE için ücretsiz model yapılandırması ve fallback taslağı

**Sahip:** kilo  
**Öncelik:** P2  
**Tarih:** 2026-09-17

## Sorun

Roo Code IDE eklentisinin en verimli/düşük maliyetli model yapılandırması henüz tanımlanmamıştır. Continue'da (`docs/continue_config.json` + `scripts/continue_config_kur.py`) kurulu 14 model + ücretsiz taraması ve fallback mekanizması örnek alınarak, Roo Code IDE için benzer yapı taslak edilmesi gerekiyor.

## Sıra

1. **Araştırma:** Continue tarama sonuçları (`docs/raporlar/continue/tarama_2026-09-17.md`) oku — 5 ücretsiz model (OK), fallback seçkisi yap
2. **Taslak:** 
   - Roo Code config şablonu (Continue desenine benzer): `docs/roo_config.json` 
   - Ücretsiz model listesi CSV: `docs/raporlar/roo_code/ucretsiz_modeller_2026-09-17.csv`
   - Konfigürasyon taslak raporu: `docs/raporlar/roo_code/taslak_yapelandirma_2026-09-17.md`
3. **Tespit etme:** En iyi 2 fallback adayını seç (Nemotron vs Qwen karşılaştırması)
4. **Sınırlar:** 9Router'a dokunma. Sadece Roo Code IDE aracının kendisi kapsamı. Detaylı optimizasyon + verimlilik (`K1-K7` kriterleri) sonraki turda (roo config turu).

## Demir Kural — Düşünce Gücüne Müdahale YOK (sahip kararı, 2026-09-17)
Token verimliliği adına modelin **düşünme/akıl yürütme gücü kısılmaz**:
- ❌ reasoning/thinking budget düşürme
- ❌ `max_tokens` daraltarak cevabı kesme
- ❌ iş kalitesini düşüren zayıf model seçimi
- ✅ Hedef dörtlü: **temiz kod yazımı · kaliteli iş · verimlilik planlaması · maliyet avantajı**
- ✅ İzin verilen tasarruf: bağlam seçimi, brief hazırlama, gereksiz keşif/okuma eleme, çıktı tekrarını azaltma.

## Kilitli Dosyalar

- `docs/continue_config.json` (referans)
- `scripts/continue_config_kur.py` (referans)
- `docs/raporlar/roo_code/taslak_yapelandirma_2026-09-17.md` (çıktı)
- `docs/raporlar/roo_code/ucretsiz_modeller_2026-09-17.csv` (çıktı)
- `docs/roo_config.json` (taslak çıktı)

## Kurallar

- UTF-8, satır sonu hijyeni
- Türkçe açıklamalar + JSON yapısı İngilizce
- Continue örneği takip et (model listesi, provider kontrolü, etiketler)
- `python scripts/kodlama_denetim.py` temiz

## Teslim

**Dosya:** `data/orchestrator/ROO-CONFIG-01_teslim_<tarih>_kilo.md`

- ✅ Ücretsiz model envanteri derlenmiş (tarama verisinden)
- ✅ Fallback adayları belirlenmiş (Nemotron vs Qwen)
- ✅ Roo Code config taslağı yazılmış (`docs/roo_config.json`)
- ✅ Yapılandırma raporu yazılmış (`docs/raporlar/roo_code/taslak_yapelandirma_2026-09-17.md`)
- ✅ `python scripts/kodlama_denetim.py` OK
