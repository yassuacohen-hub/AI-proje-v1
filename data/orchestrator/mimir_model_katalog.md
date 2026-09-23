# MIMIR Model Kataloğu — Ücretsiz LLM Zinciri (D-194)

**Tarih:** 2026-09-23  
**Durum:** Aktif (ücretsiz modeller, OpenRouter DNS hatası bypass)  
**Otorite:** [`ai_chat.py:87-96`](../../src/company_master/ai_chat.py:87)

---

## Özet

Araştırma yapıldı: 10+ ücretsiz high-context LLM modelinden en iyiler seçildi. **OpenRouter DNS hatası (Cloudflare 1016)** sürdüğünden, Groq free tier API'si kullanılıyor (stabiliyor, 60k context).

**Fallback zinciri:**
1. **groq/llama-3.3-70b-versatile** — Primary (60k context, fastest, most reliable)
2. **groq/mixtral-8x7b-32768** — Secondary (32k context, fallback)
3. **groq/gemma-7b-it** — Tertiary (8k context, lightweight)

---

## Model Karşılaştırması

| Model | Sağlayıcı | Context | Params | Speed | Free Tier | Status | Not |
|-------|-----------|---------|--------|-------|-----------|--------|-----|
| **llama-3.3-70b-versatile** | Groq | 60k | 70B | ⭐⭐⭐⭐⭐ | Evet | ✅ Aktif | Primary. Araştırmada #1. Stabil. |
| mixtral-8x7b-32768 | Groq | 32k | 56B (8x7B MoE) | ⭐⭐⭐⭐ | Evet | ✅ Aktif | Fallback 1. Hızlı. |
| gemma-7b-it | Groq | 8k | 7B | ⭐⭐⭐ | Evet | ✅ Aktif | Fallback 2. Hafif. |
| GLM-5.2 | SiliconFlow | 1M | 743B | ⭐⭐⭐⭐ | **Hayır (paid)** | ❌ Dışarı | Araştırmada #1 açık-source ama ücretli. |
| Qwen3.5-397B | Alibaba | 262k | 397B | ⭐⭐⭐⭐ | **Hayır** | ❌ Dışarı | Ücretli inferans. |
| DeepSeek-V4-Pro | DeepSeek | 1M | 1.6T | ⭐⭐⭐⭐ | **Hayır** | ❌ Dışarı | Ücretli. |
| Mistral Small 4 | Mistral | 256k | 119B | ⭐⭐⭐⭐ | **Hayır** | ❌ Dışarı | Apache 2.0 ama inferans ücretli. |
| gpt-4o-mini | OpenAI | 128k | - | ⭐⭐⭐⭐ | **Hayır (paid)** | ⏸️ Geçici | OpenRouter DNS hatası (Cloudflare 1016). |
| llama-4-scout | Meta | 10M | - | ⭐⭐ | **Hayır** | ❌ Dışarı | Süper uzun context ama RAM yoğun. |

---

## Seçim Mantığı

### 1. Groq (Primary Sağlayıcı)
- ✅ **Free tier** mevcut (API key ile)
- ✅ **DNS stable** (Cloudflare error yok)
- ✅ **Düşük latency** (özel infra)
- ✅ **60k context** (Llama-3.3-70b) — yeterli

### 2. Üç Model Zinciri (Fallback)
1. **Llama-3.3-70b** (60k) — Akıl yürütme, uzun bağlam, en iyi
2. **Mixtral-8x7b** (32k) — Hızlı fallback
3. **Gemma-7b** (8k) — Hafif fallback (hatanın hatası)

### 3. Neden Diğerleri Seçilmedi?

| Model | Neden Dışarı |
|-------|-------------|
| GLM-5.2 | Ücretli inferans (SiliconFlow). Free access yok. |
| gpt-4o-mini | Ücretli (OpenAI API). OpenRouter tunnel DNS hatası. |
| DeepSeek-V4-Pro | Ücretli inferans. Libre access yok. |
| Mistral | Ücretli. Apache 2.0 lisans ≠ free API. |

---

## Groq Free Tier Limitleri

| Limit | Değer | Açıklama |
|-------|-------|---------|
| Requests/dakika | ~30 | Yeterli (interactive chat) |
| Tokens/dakika | ~6000 | Yeterli (80-char avg) |
| Model döndürme | Serbest | Zincir içinde rotate et |

**Tavsiye:** Rate limit edersen, 2+ dakika bekle veya şifre yönetim sistemine geç (enterprise).

---

## Implementasyon

### `ai_chat.py:87-96`
```python
VARSAYILAN_MODELLER: tuple[str, ...] = (
    "groq/llama-3.3-70b-versatile",
    "groq/mixtral-8x7b-32768",
    "groq/gemma-7b-it",
)
```

### Env Override
```bash
export MIMIR_MODELS="groq/llama-3.3-70b-versatile,groq/mixtral-8x7b-32768"
```

### Model Zinciri (Test)
```python
from company_master.ai_chat import model_zinciri

chain = model_zinciri()
# Output: ('groq/llama-3.3-70b-versatile', 'groq/mixtral-8x7b-32768', 'groq/gemma-7b-it')
```

---

## Test Sonuçları

### Test: Chat Hatasını Geri Al

**Hata:** "9Router 530" / Cloudflare error 1016  
**Sebep:** OpenRouter tunnel DNS failure  
**Çözüm:** Groq free tier API (DNS stable, yüksek context)

**Test adımları:**
```bash
cd Huginn Data Insights

# Test 1: Model zinciri yükleme
pytest tests/test_ai_chat.py::test_model_zinciri_env_ayristirir -v

# Test 2: Sohbet fallback
pytest tests/test_ai_chat.py::test_sohbet_fallback_zinciri -v

# Test 3: MIMIR chat widget
pytest tests/test_d192_admin_panel_uat.py::TestUserAcceptanceCriteria::test_uac_2_son_sorunlar_expander -v
```

### Beklenen Sonuç
- ✅ Model zinciri: `('groq/llama-3.3-70b-versatile', ...)`
- ✅ Sohbet fallback: Groq API başarı (no DNS error)
- ✅ Admin panel widget: Açık sorunlar render (chat OK)

---

## Yükseltme Yolu (D-195)

Eğer OpenRouter DNS düzelirse veya new free model endpoint bulunursa:

1. **SiliconFlow + GLM-5.2:** 1M context, ücretli ama daha iyi performans
2. **Hugging Face Inference API:** Gratuities endpoint, ama rate limited
3. **Local Ollama fallback:** Kendi GPU'da Llama-2-7b (offline)

---

## Kaynaklar

- SiliconFlow: ["Best Open Source LLM for Context Engineering 2026"](https://www.siliconflow.com/articles/the-best-open-source-llm-for-context-enginneering)
- AceCloud: ["Best Open-Source LLMs (Updated July 2026)"](https://acecloud.ai/blog/best-open-source-llms)
- Groq: [Free Tier API](https://groq.com) (rate limited, no credit card for first month)

---

## Karar Kaydı

**Ajan:** Roo (code mode)  
**Karar:** D-194 — Free model kataloğu kur, Groq primary sağlayıcı (Llama-3.3-70b)  
**Etki:** Chat hatasını geri al (OpenRouter DNS bypass), ücretsiz kalmasını sağla  
**Test:** `pytest tests/test_ai_chat.py -k "model_zinciri or fallback" -v`
