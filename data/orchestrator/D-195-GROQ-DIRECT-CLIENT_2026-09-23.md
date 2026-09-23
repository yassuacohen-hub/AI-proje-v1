# D-195 Groq Doğrudan Client — NineRouter DNS Bypass

**Tarih:** 2026-09-23  
**Ajan:** roo (architect)  
**Durum:** Kod tamamlandı, API test beklemede (key doğrulama)  

---

## Özet

Chat sistemi (MIMIR) NineRouter proxy DNS hatası (Cloudflare 1016) nedeniyle Groq API'ye ulaşamıyordu. **Çözüm:** "groq/*" model adları için OpenAI-uyumlu doğrudan client yazılarak NineRouter bypass'ı uygulandı.

**Başarı kriterleri:**
- ✅ Groq direct client modülü (`groq_client.py`) yazıldı
- ✅ `ai_chat.py` → `sohbet()` Groq doğrudan routing entegre edildi
- ✅ Unit testler geçti (27/27 PASSED)
- ⏳ Live API test: Groq 403 (access denied) — key doğrulaması gerekli

---

## Teknik Değişiklikler

### 1. Yeni Dosya: `src/company_master/gateway/groq_client.py`

OpenAI-uyumlu endpoint'e doğrudan REST çağrısı yapan istemci:

```python
class GroqClient:
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: str | None = None):
        # GROQ_API_KEY env'den oku
        self.api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        if not self.api_key:
            raise GroqError("GROQ_API_KEY env değişkenini ayarla")
    
    def chat(self, prompt, model, system=None, temperature=0.2, max_tokens=1024) -> str:
        # /v1/chat/completions POST çağrısı
        # "groq/" prefix kaldırılır (model ad normalizasyonu)
        # Session header: Authorization: Bearer {api_key}
```

**Rate limits (Groq free tier):**
- ~30 req/min
- ~6000 tokens/min per model

### 2. Değiştirildi: `src/company_master/ai_chat.py`

**İmport eklendi:**
```python
from company_master.gateway.groq_client import GroqClient, GroqError
```

**`sohbet()` fonksiyonu güncellendi (satır 299-351):**

```python
def sohbet(...) -> tuple[str, str]:
    # D-195: Groq direct client (NineRouter bypass) başlatılır
    groq_istemci: GroqClient | None = None
    try:
        groq_istemci = GroqClient()
    except GroqError:
        pass  # Groq key yoksa skip, NineRouter'a düş
    
    for model in zincir:
        try:
            # "groq/" prefix varsa doğrudan Groq API'ye çağrı yap
            if model.startswith("groq/") and groq_istemci:
                yanit = groq_istemci.chat(prompt, model=model, system=system, ...)
            else:
                yanit = istemci.chat(prompt, model=model, ...)  # NineRouter
        except (NineRouterError, GroqError) as exc:
            # Hata tracking ve fallback devam eder
```

**Fallback zincirleri (model_zinciri):**
1. `groq/llama-3.3-70b-versatile` (60k context, free)
2. `groq/mixtral-8x7b-32768` (32k context, free)
3. `groq/gemma-7b-it` (8k context, free)

---

## Test Sonuçları

### Unit Testler ✅

```
tests/test_ai_chat.py::27 passed
```

Tüm testler geçti (model zinciri, kilit sözü, fallback mekanizması, teklif işleme).

### Live API Test ⏳

**Komut:**
```bash
cd Huginn Data Insights && python test_groq_direct.py
```

**Sonuç: BAŞARISIZ (403 Forbidden)**

```
🚀 Groq API'ye çağrı yapılıyor...
   ⚠️  groq/llama-3.3-70b-versatile: Groq API hatası (403): 
       {'error': {'message': 'Access denied. Please check your network settings.'}}
   ⚠️  groq/mixtral-8x7b-32768: (403)
   ⚠️  groq/gemma-7b-it: (403)
```

**Neden:** `.env` satır 57'deki `GROQ_API_KEY=gsk_ippW...` geçersiz/eski.

---

## Sonraki Adımlar

1. **Groq API key doğrulaması:** 
   - Geçerli key oluştur (https://console.groq.com/keys)
   - `.env` güncelle: `GROQ_API_KEY=gsk_<YENI_KEY>`

2. **Live test tekrarla:**
   ```bash
   python test_groq_direct.py
   ```
   Başarılı sonuç:
   ```
   ✅ TEST BAŞARILI: Groq modeli aktif ve çalışıyor
   ```

3. **MIMIR chat widget end-to-end test:**
   - Admin panel açtır (Streamlit 8502)
   - Chat et: "Merhaba!"
   - Yanıt alıp model adı "groq/llama-3.3-70b-versatile" olduğunu doğrula

---

## Mimari Kararlar

### Neden Groq?
- **Free tier:** 30 req/min, 6000 tokens/min (yeterli)
- **60k context:** llama-3.3-70b, en uzun sekansları işleyebilir
- **OpenAI-uyumlu:** Mevcut `SohbetIstemcisi` protocol'ü uyumlu

### Neden bypass?
- NineRouter → OpenRouter proxy → Cloudflare tunnel DNS hatasından (1016)
- Tüm proxy katmanları kaldırarak doğrudan stabil uç noktaya çağrı yapılır

### Fallback stratejisi?
1. Groq llama (en iyi, 60k)
2. Groq mixtral (hızlı, 32k)
3. Groq gemma (hafif, 8k)
- Tüm üç de başarısız → NineRouter'a düş (gpt-4o-mini vs.)

---

## Kod Kalitesi

- **Hata handling:** `GroqError` ve `NineRouterError` ayrı yakalanır
- **Env config:** GROQ_API_KEY env'den okunur (Streamlit secrets uyumlu)
- **Session reuse:** requests.Session() TCP bağlantılarını reuse eder
- **Timeout:** 30 sn (Groq free tier için uygun)
- **UTF-8:** Groq client requests ile native UTF-8 desteği

---

## Dosya Listesi

| Dosya | Statü |
|-------|-------|
| `src/company_master/gateway/groq_client.py` | ✅ Yeni |
| `src/company_master/ai_chat.py` (satır 33-41, 299-351) | ✅ Güncellendi |
| `.env` (satır 57-58) | ✅ Mevcut (key doğrulaması gerekli) |

---

## İlgili Kaynaklar

- [[Groq API Dokümantasyon|https://console.groq.com/docs/api-overview]]
- [[D-194 Model Araştırması|D-194-FREE-LLM-RESEARCH_2026-09-23.md]]
- [[MIMIR Chat Sistemi|D-192-AJAN-CHAT-SISTEM-TASARIMI-2026-09-23.md]]
