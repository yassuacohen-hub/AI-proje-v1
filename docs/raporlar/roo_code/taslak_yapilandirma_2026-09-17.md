# Roo Code IDE Yapçlandirma Taslagi — 2026-09-17

| Alan | Deger |
|------|-------|
| Tarih | 2026-09-17 |
| Ajan | kilo |
| Oncelik | P2 |
| Gorev | ROO-CONFIG-01 |
| Durum | Taslak (tasarruf bekleniyor) |

## Continue Tarama Sonuclari (2026-09-17)

Kaynak: docs/raporlar/continue/tarama_2026-09-17.md - 5 uücretsiz model gerçek POST ile OK oldu.

| # | Slug | Sonuc |
|---|------|-------|
| 1 | inclusionai/ling-3.0-flash-fin:free | OK |
| 2 | inclusionai/ling-3.0-flash-sante:free | OK |
| 3 | inclusionai/ling-3.0-flash-vl:free | OK |
| 4 | nvidia/nemotron-3.5-content-safety:free | OK |
| 5 | qwen/qwen3.8-27b:free | OK |

Not: Bu 5 model taramada OK cikti. Katalogda 445 slug vardi, 12 yeni :free slugi denendi. Diöleri KOTA (429) veya YETKI (403) hatasi ald.

## Fallback Kararlari

Fallback zinciri su sekilde belirlenmistir:

| Sira | Model | Rol | Aciklama |
|------|-------|-----|----------|
| 1 (Primary) | nvidia/nemotron-3.5-content-safety:free | Primary Fallback | En guclu uücretsiz secenek, icerik güvenligi odakli
| 2 (Secondary) | qwen/qwen3.8-27b (Groq) | Secondary Fallback | Qwen 3.8 27B, Groq altyapısşnde hızlı ve guclu
| 3 (Emergency) | claude-sonnet-4-5 (Anthropic) | Emergency | Acil is icin en kaliteli model ancak ucretli

Fallback mantigi: Once primary edilen → 429/403 gelirse secondary → emergency.

## Roo Code Config Yapisi

docs/roo_config.json dosyasi su yapçda duzenlenmistir:

- models: 14 model (13 uücretsiz [UCRETSIZ] + 1 ucretli [UCRETLI])
- tabAutocompleteModel: GPT-OSS 20B (Groq)
- contextProviders: code, diff, terminal, problems, folder, codebase
- Her model: title, provider, model, apiBase, apiKey, contextLength
- API anahtarlari ${env:X} formatinda ortam degiskeni yer tutucularidir
- _comment alanlarinda Türkçe açklamalar; JSON anahtarlarç Englizce
- OpenRouter modelleri: apiBase https://openrouter.ai/api/v1, apiKey ${env:OPENROUTER_API_KEY}
- NVIDIA modeli: apiBase ${env:NVIDIA_BASE_URL}, apiKey ${env:NVIDIA_API_KEY}
- Groq modelleri: apiBase ${env:GROQ_BASE_URL}, apiKey ${env:GROQ_API_KEY}
- Anthropic modeli: apiKey ${env:ANTHROPIC_API_KEY}, apiBase yok (varsayilan Anthropic endpoint)

## D-48 Uyumlulugu

D-48 kuralina tam uyumludur. Modelin dısşece/akül yırştme guyune herhangi bir müdahale yapilmad:

| Yasak | Durum |
|-------|-------|
| reasoning/thinking budget dısşurme | YOK - hiçbir modelde uygulanmad |
| max_tokens daraltarak cevabı kesme | YOK - yapçlandirmada bulunmamûr |
| kalitesi dısiren zıyıf model secimi | YOK - en guclu uücretsiz modeller secildi |

Hedef dortlü: temiz kod yazımı, kaliteli iük, verimlilik planlaması, maliyet avantajı.

## Test Sonuclari

| Test | Sonuc |
|------|-------|
| python scripts/kodlama_denetim.py | exit 0 (OK) |
| UTF-8 dogrulamasi | Geçerli (BOM yok, Türkçe karakterler dogru) |
| JSON sozdizimi | Geçerli |
| CSV sozdizimi | Geçerli |

## Kapsam

- Roo Code IDE eklentisi için uücretsiz model yapçlandirma ve fallback taslagç
- Continue config sıablonu (docs/continue_config.json) referans alınarak olusturuldu
- 14 model (13 uücretsiz + 1 ucretli) + tabAutocompleteModel dahil edildi
- Fallback zinciri (primary -> secondary -> emergency) belirlendi
- Disari: 9Router - dokunulmaz (D-48 kapsaminda, ayri sistem)
- Detaylı optimizasyon ve K1-K7 verimlilik kriterleri - sonraki turda

## Riskler

| # | Risk | Etki | Önlem |
|---|------|------|-------|
| 1 | Uücretsiz modellerde 429/rate-limit | Yıksek | Fallback zinciri ile otomatik geçiü |
| 2 | nemotron-3.5-content-safety stabilitesi | Orta | Sadece tarama OK |
| 3 | Claude Sonnet 4.5 ucretli - kota tıketimi | Orta | ANTHROPIC_API_KEY ayri cuzdan |
| 4 | env yer tutucuları cozılmemisse 401 | Yıksek | Kurucu script ile doldurulmalidir |
| 5 | Qwen 3.8 27B Groq kota durumu | Dısk | Taramada OK |
| 6 | Model slug deçimi (404 riski) | Orta | Haftalık tarama rutini kurulmalidir |

---

> Son gıncelleme: 2026-09-17 - kilo - ROO-CONFIG-01 taslak
