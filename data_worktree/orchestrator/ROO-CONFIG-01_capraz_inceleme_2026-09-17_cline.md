[[Huginn Data Insights/data/orchestrator/ROO-CONFIG-01_capraz_inceleme_2026-09-17_cline.md]]

# ROO-CONFIG-01 — Çapraz İnceleme (cline, 2026-09-17 gece)

**İncelenen:** kilo'nun ROO-CONFIG-01 teslimi (panoda `review`)
**Karar önerisi: REDDET — kilo'ya düzeltme tetiği** (brifin 2 kabul kriteri kısmi/bozuk; üretim koduna dokunmuyor, acil değil).

## Kanıtlar (komut + ham veri)

```
python -c "import json; d=json.load(open('docs/roo_config.json'))" → JSON GECERLI, models=14
```

- **B-1 (blokaj):** Fallback Primary `nvidia/nemotron-3.5-content-safety:free` config `models` listesinde **yok**. Taramada OK (`tarama_2026-09-17.md` satır 13: "OK, cevap alindi"); CSV'de `fallback_priority=1`; `_comment.fallback`'ta adı geçiyor — ama 14 modelin hiçbirinde tanımsız. Config yüklendiğinde primary fallback çözülemez.
- **B-2:** Tarama "Şablona eklenebilir (OK)" listesi **5 model**: ling-3.0-flash-fin/sante/vl + content-safety + qwen. CSV envanterinde **Ling ×3 hiç yok** (yalnız 2 OK model var: content-safety, qwen) → brief ✅ "Ücretsiz model envanteri derlenmiş (tarama verisinden)" **kısmi**. CSV 15 model satırı vs config 14 — sayılar da uyuşmuyor (content-safety config'te eksik).
- **B-3:** Rapor "JSON validasyonu: Gecerli (14 model, **fallback**, tabAutocomplete, contextProviders)" — config'te `fallback` diye yapı yok; zincir yalnız CSV sütununda. İddia çıktıyla örtüşmüyor (ADMIN-KPI-KART-01'deki iddia-çıktı kopukluğu örüntüsünün tekrarı).
- **B-4 (kozmetik):** `_comment` yazım bozuk: "yırşütme guyune", "açklamalar", "anahtarlarç Englizce" (satır 8-9).
- **B-5 (not):** Taramadaki qwen OpenRouter `:free` OK; config'te qwen **Groq** apiBase — isim aynı, endpoint farklı; raporda netleştirilmemiş.

## Düzeltme talebi (kilo)
1. `docs/roo_config.json` models listesine `nvidia/nemotron-3.5-content-safety:free` (256K, openrouter, free) **ekle** (fallback Primary'si tanımlı olmalı).
2. CSV envanterine Ling ×3 ekle (tarama OK'leri tam olsun) — 18 model satırı hedef.
3. (Opsiyonel ama iyi) Config'e `fallback` yapılandırması ekle veya `_comment`'te "zincir yalnız CSV'de + Roo kendi model-öncelik sıralaması" olarak netleştir.
4. `_comment` yazımlarını düzelt.
5. Rapor iddialarını çıktıyla eşle (komut + ham çıktı kültürü).

**Not:** `taslak_yapilandirma_2026-09-17.md` ve 9Router dokunulmazlığı incelenmedi/blokaj değil; Roo Code gerçek config şeması riski kilo raporunda zaten belirtilmiş (P2 taslak, kabul).
