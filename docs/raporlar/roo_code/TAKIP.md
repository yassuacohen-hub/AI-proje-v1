# Roo Code IDE — Yapılandırma, Model ve Verimlilik Takip Dosyası

> **Sürekli güncellenen dosya.** Her turda ilgili bölüm güncellenir, satır silinmez; durum değiştirilir.
> Kapsam: Roo Code IDE eklentisinin model yapılandırması, fallback zinciri, token/maliyet verimliliği.
> **Kapsam dışı:** 9Router (`plans/9router_*`, `scripts/9router_optimizer.py`) — dokunulmaz.

## 0. Demir Kural (D-48, sahip kararı 2026-09-17)
Token verimliliği adına **modelin düşünme gücüne müdahale edilmez**.

| Yasak | İzinli |
|-------|--------|
| reasoning/thinking budget düşürme | bağlam seçimi (sadece ilgili dosya) |
| `max_tokens` daraltarak cevabı kesme | görev brief'i ile keşif token'ını sıfırlama |
| kaliteyi düşüren zayıf model seçimi | gereksiz okuma/exploration eleme |
| cevabı kısaltmak için dil değiştirme | tekrar eden çıktıyı azaltma |

Hedef dörtlü: **temiz kod yazımı · kaliteli iş · verimlilik planlaması · maliyet avantajı**.

## 1. Tur Planı
| Tur | Konu | Durum |
|-----|------|-------|
| (a) | kilo'ya görev ata → `ROO-CONFIG-01` | ✅ atandı 2026-09-17, tetik `bekliyor` |
| (b) | Roo Code yapılandırma (ücretsiz modeller + fallback) | ✅ kilo teslimi 2026-09-17 |
| (c) | Verimlilik turu (K1-K7 uyarlaması) | ⏳ (b) sonrası |

## 2. Model Envanteri (kaynak: `docs/raporlar/continue/tarama_2026-09-17.md`)
Katalog 445 slug · denenen yeni `:free` 12.

### OK (gerçek POST cevap verdi) — 5
| Slug | Not |
|------|-----|
| `nvidia/nemotron-3.5-content-safety:free` | fallback adayı 1 |
| `qwen/qwen3.8-27b:free` | fallback adayı 2 |
| `inclusionai/ling-3.0-flash-fin:free` | finans odaklı |
| `inclusionai/ling-3.0-flash-sante:free` | sağlık odaklı |
| `inclusionai/ling-3.0-flash-vl:free` | vision |

### KOTA / 429 — 5
`google/gemma-4-26b-a4b-it:free` · `google/gemma-4-31b-it:free` · `poolside/laguna-s-2.1:free` · `poolside/laguna-xs-2.1:free` · `z-ai/glm-5.2:free`

### YETKİ / 403 — 2
`thinkingmachines/inkling:free` · `thinkingmachines/inkling-small:free` — "only available on agentic harnesses"

## 3. Aktif Model Kombinasyonu (sahip emri 2026-09-17, 18/18 POST-OK)
Zincir: ücretsiz (otomatik) → ucuz ücretli → akıl yürütme → son yedek. Fiyat USD/1M token.

| Sıra | Katman | Model | in/out | ctx | Rol |
|------|--------|-------|--------|-----|-----|
| 1-13 | UCRETSIZ | 9 OR `:free` + NVIDIA + 3 Groq | 0 / 0 | 65k–1M | sahip otomatik kullanıyor |
| 14 | UCRETLI | `deepseek/deepseek-v4-flash-0731` (OR) | 0.060 / 0.120 | 1.31M | **ANA** — büyük bağlam, en ucuz |
| 15 | UCRETLI | `qwen/qwen3-coder-30b-a3b-instruct` (OR) | 0.070 / 0.280 | 262k | kod işi |
| 16 | UCRETLI | `deepseek/deepseek-v3.2` (OR) | 0.269 / 0.400 | 164k | akıl yürütme / zor iş |
| 17 | UCRETLI | `claude-sonnet-4-5` (Anthropic doğrudan) | — | 200k | **SON YEDEK** — kritik iş |

**Neden DeepSeek doğrudan değil, OpenRouter üzerinden:** `api.deepseek.com` anahtarı `HTTP 402 Insufficient Balance` döndü (bakiye yok). OR bakiyesi çalışıyor ve aynı modelleri veriyor → tek anahtar, tek fatura.

**Neden 9Router zinciri yedek değil:** `plans/9router_*SKILL.md` içinde somut önerilen kombinasyon tablosu yok, yalnız örnek slug'lar (`openai/gpt-5`, `openai/gpt-4o`, `cc/claude-opus-4-7`). 9Router ayrıca hâlâ 403 tanısı bekliyor (TUR2). Bu yüzden son yedek doğrudan Anthropic Sonnet.

### Fallback mekanizması
| Yol | Açıklama | Durum |
|-----|----------|-------|
| A | Manuel model değiştirme (Continue/Roo model seçici) | ✅ **aktif** — 17 model listede, sıralı |
| B | OpenRouter `models` dizisi (otomatik sıradaki) | ⏳ Roo Code desteği doğrulanacak |
| C | LiteLLM proxy | ⏳ B yetmezse |

## 3.5 Yerel Katman — Ollama (2026-09-17, sahip emri)

### Donanım sınırı
GPU: NVIDIA GeForce RTX 3050 Laptop, **4096 MiB (4 GB)**. Aynı anda tek model yükle.

| Model | Boyut | 4 GB VRAM'e sığar mı |
|-------|-------|----------------------|
| `qwen2.5-coder:3b` | 1.9 GB | ✅ evet |
| `deepseek-r1:1.5b` | 1.12 GB | ✅ evet |
| `qwen2.5-coder:1.5b-base` | 0.99 GB | ✅ evet (FIM/autocomplete) |
| `gemma4:26b` | 18.6 GB | ❌ **hayır** — CPU'ya taşar. Listeye alınmadı. |

### D-48 kapsam sınırı (ZORUNLU)
Yerel 1.5b/3b modeller **ANA MODEL DEĞİL**.
- İzinli: autocomplete/FIM · tek dosya küçük düzenleme · çevrimdışı/gizli iş.
- Yasak: mimari karar, çoklu dosya refactor, güvenlik incelemesi → ücretsiz OR katmanına gider.

### Continue yapılandırması
- `provider: "ollama"`, `apiBase: "http://localhost:11434"` — **`/v1` YAZILMAZ** (Continue kendi ekler).
- `apiKey` alanı YOK.
- `tabAutocompleteModel` → `qwen2.5-coder:1.5b-base` (**base** sürüm FIM için doğru, instruct değil).

### Roo Code / Cline / Kilo Code entegrasyonu — model listede çıkmıyorsa
**Kök neden:** yerel modeller OpenRouter kataloğunda yok; provider `OpenRouter` kaldıkça liste boş kalır. Provider ayarı `state.vscdb` (SQLite) içinde tutulur → script yazamaz, GUI adımı zorunlu.

1. Eklenti panelinde dişli simgesi → **Settings**
2. **API Provider** → **Ollama**
3. **Base URL** → `http://localhost:11434` (**`/v1` EKLEME**)
4. **Model ID** elle: `qwen2.5-coder:3b` veya `deepseek-r1:1.5b`
5. Kaydet, yeni sohbet aç.

Not: `.env` içindeki `OLLAMA_BASE_URL` `/v1` ekli — o OpenAI uyumlu istemciler içindir; Roo/Cline/Kilo alanına kopyalanmaz.

### Doğrulama
`python scripts/continue_config_kur.py --dogrula` → **20/20 OK** (3 yerel + 13 ücretsiz + 4 ücretli).

## 3.7 KARAR: Yerel modeller Roo Code agent modunda KULLANILMAZ (2026-09-18)

### Kanıt
Sahip 4 profil denedi. Sonuç:

| Profil | Sonuç |
|--------|-------|
| OpenRouter free | ✅ sorunsuz |
| Ollama `qwen2.5-coder:3b` | ❌ bozuk araç çağrısı |
| Ollama `deepseek-r1:1.5b` | ❌ "API başarısız" |
| Groq | ❌ anahtar **OLU** (plan kapalı) |

Roo Code hata metni: *"Model yanıtında herhangi bir araç kullanamadı."* Model üretimi:
```json
{"name": "ask_followup_question", "arguments": {"question": "Do you have any questions?"}}
{"name": "update_todo_list", "arguments": {"todos": "[ ] Create todo list"}}
```
Bağlantı **çalışıyor** — model yanıt üretiyor. Bozuk olan **araç çağrısı şeması**: zorunlu alanlar eksik, `follow_up` yok, todo içeriği anlamsız.

### Kök neden (üç katman)
1. **Tool-calling kapasitesi.** Roo Code sistem promptu ~15-20k token, 20+ araç şeması, iç içe parametre. 1.5B/3B modeller bu şemayı tutarlı dolduramaz. Continue'da çalışması yanıltıcı — Continue düz sohbet, araç zinciri yok.
2. **Bağlam yalanı.** Panel `Bağlam Penceresi: 128.000 token` gösteriyor. **4 GB VRAM'de 128k KV cache imkânsız** — CPU'ya taşar, bu yüzden "çok yavaş". Alan elle **8192** yazılmadıkça yavaşlık sürer.
3. **Provider seçimi.** Ekranda `OpenAI Compatible` seçili. Ollama için Roo Code'un **kendi `Ollama` provider'ı** var; `OpenAI Compatible` dalı `/v1` bekler ve model meta verisini OpenAI kataloğundan uydurur (128k rakamı buradan geliyor).

### Karar
- Yerel modeller **Roo/Cline/Kilo agent modunda kapalı**. Profiller silinmez, **kullanılmaz**.
- Yerel katmanın yeri: **Continue autocomplete/FIM** (`qwen2.5-coder:1.5b-base`) + çevrimdışı düz sohbet. Burada zaten sorunsuz ve maliyeti sıfır.
- Roo Code'da ana hat: **OpenRouter free** (çalıştığı doğrulandı) → ucuz OR → Sonnet.
- Bu karar §3.5'teki D-48 kapsam sınırını **daraltır**: yerel model "tek dosya küçük düzenleme" için bile agent modunda kullanılmaz (araç çağrısı gerektiriyor).

### Yine de denenecekse (opsiyonel)
Provider'ı `OpenAI Compatible` → **`Ollama`** yap, bağlam alanına **8192** yaz, todo aracını **kapat**. Araç çağrısı yine bozulursa model kapasitesi yetersizdir; ısrar etme.

### Groq
`GROQ_API_KEY` → **OLU** (yetki yok / plan kapalı). Roo ayarı sorunu değil, hesap sorunu. Ya anahtar yenilenir ya Groq listeden düşer. OpenRouter free zaten aynı işi görüyor.

## 3.6 Roo Code Profil Şeması (sahip sorusu 2026-09-17)

**Evet — model başına ayrı profil.** Roo Code tek seferde tek provider+model tutar; profil = adlandırılmış ayar seti, her moda (Code/Architect/Ask/Debug) ayrı atanır.

> Profil **adı serbest** (sadece etiket). Hata veren yer **Model ID** alanı — birebir slug yazılmalı, açıklama/etiket yazılmaz.

| Profil adı | Provider (Roo) | **Model ID (birebir)** | Bağlam | Todo aracı | Hata limiti | Mod |
|-----------|----------------|------------------------|--------|-----------|-------------|-----|
| `yerel-qwen3b` | Ollama | `qwen2.5-coder:3b` | **8192** | **KAPALI** | 2 | elle |
| `yerel-r1` | Ollama | `deepseek-r1:1.5b` | **16384** | **KAPALI** | 2 | elle |
| `or-free-ultra` | OpenRouter | `nvidia/nemotron-3-ultra-550b-a55b:free` | boş | AÇIK | 3 | Architect |
| `or-free-lightning` | OpenRouter | `nvidia/nemotron-3.5-lightning:free` | boş | AÇIK | 3 | Ask |
| `or-free-code` | OpenRouter | `cohere/north-mini-code:free` | boş | AÇIK | 3 | Code (free) |
| `or-deepseek-flash` | OpenRouter | `deepseek/deepseek-v4-flash-0731` | boş | AÇIK | 3 | **Code (ana)** |
| `or-qwen3-coder` | OpenRouter | `qwen/qwen3-coder-30b-a3b-instruct` | boş | AÇIK | 3 | Debug |
| `anthropic-sonnet` | Anthropic | `claude-sonnet-4-5` | boş | AÇIK | 3 | son yedek |
| `groq-120b` | OpenAI Compatible | `openai/gpt-oss-120b` | boş | AÇIK | 3 | Code |
| `groq-20b` | OpenAI Compatible | `openai/gpt-oss-20b` | boş | AÇIK | 3 | Ask |
| `groq-qwen` | OpenAI Compatible | `qwen/qwen3.8-27b` | boş | AÇIK | 3 | Debug |
| `nvidia-lightning` | OpenAI Compatible | `nvidia/nemotron-3.5-lightning-30b-a3b` | boş | AÇIK | 3 | Architect |

### Roo Code'da her provider için **zorunlu alanlar** (Continue'dan FARKLI)

| Provider | Base URL | API Key | Model ID formatı | Sık hata |
|----------|----------|---------|------------------|----------|
| **Ollama** | `http://localhost:11434` **(/v1 YOK)** | boş / `ollama` | `qwen2.5-coder:3b` | `/v1` eklersen 404; provider `OpenRouter` kalsa liste boş |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | `nvidia/nemotron-3-ultra-550b-a55b:free` | `:free` eksik = 404; key geçersiz = 401 |
| **Anthropic** | `https://api.anthropic.com` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-5` | Key yok/yanlış = 401 |
| **OpenAI Compatible (Groq)** | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | `openai/gpt-oss-120b` | Base URL yanlış = 404/timeout |
| **OpenAI Compatible (NVIDIA)** | `${env:NVIDIA_BASE_URL}` | `NVIDIA_API_KEY` | `nvidia/nemotron-3.5-lightning-30b-a3b` | Key yok = 401 |

### "Çalışmadı / yavaş / istek atmadı" teşhis listesi

1. **Ollama (yerel) çalışmıyor** → Provider **Ollama** seçili mi? Base URL **`http://localhost:11434`** (port 11434, `/v1` YOK)? `ollama serve` çalışıyor mu? `ollama list` model var mı?
2. **OpenRouter bazıları çalışıyor bazıları değil** → Model ID **birebir** mi (`:free` dahil)? Key geçerli mi (`python scripts/api_anahtar_testi.py`)?
3. **Groq çalışmıyor** → Provider **OpenAI Compatible** mi? Base URL **`https://api.groq.com/openai/v1`**? `GROQ_API_KEY` doğru mu?
4. **Anthropic çalışmıyor** → Provider **Anthropic** mi? `ANTHROPIC_API_KEY` doğru mu? (Sonnet 4.5 pahalı, son yedek)
5. **NVIDIA çalışmıyor** → Provider **OpenAI Compatible** mi? `NVIDIA_BASE_URL` + `NVIDIA_API_KEY` `.env`'de mi?
6. **Hepsi yavaş** → Yerel modellerde bağlam penceresi çok yüksek (32768) → CPU'ya taşır. 8192/16384'e düşür. Bulutta 429 alıyorsan hız sınırı 2-3s yap.

### Hızlı doğrulama (terminal)
```bash
# Tüm anahtarları test et
python scripts/api_anahtar_testi.py

# Continue config testi (zaten 19/19 OK)
python scripts/continue_config_kur.py --dogrula
```

**Roo Code'da test etmenin yolu:** Profil kaydet → Yeni sohbet aç → Profil seç → "Merhaba" de → yanıt gelirse çalışıyor. Yanıt gelmezse **Developer Tools (F12) → Console / Network** sekmesinden hata kodu bak (401/404/500).

### Ayar gerekçeleri
- **Bağlam penceresi:** 4 GB VRAM sınırı. `qwen3b` ağırlık 1.9 GB + KV cache → 8192 güvenli tavan; 32768 CPU'ya taşar ve yavaşlar. `r1:1.5b` ağırlık 1.12 GB, düşünce zinciri uzun → 16384. Boş bırakmak Modelfile varsayılanına (2048/4096) düşer, çok kısa kalır. Bulut profillerde boş bırak (sağlayıcı zaten doğru değeri verir).
- **Özel sıcaklık:** **İŞARETSİZ** — D-48 gereği modelin varsayılan davranışına dokunulmaz. Özellikle `deepseek-r1` sıcaklık değişimine hassastır, akıl yürütmesi bozulur.
- **Hız sınırı:** **0s** — yerel sunucuda kota yok, gecikme eklemek anlamsız. Bulut ücretsiz profillerde 429 alınırsa 2-3s'e çıkarılır.
- **Hata ve Tekrar Limiti:** yerelde **2** (küçük model tekrar döngüsüne girerse erken yakala, boşa token yakmasın), bulutta **3**. **0 YAPMA** — güvenlik mekanizması kapanır, sonsuz döngü riski.
- **Yapılacaklar listesi aracı:** yerel 1.5b/3b profillerde **KAPAT** — küçük modeller araç çağrısını bozar, sistem promptunu gereksiz şişirir. Bulut profillerde açık kalsın.

### Roo Code'un kendi uyarısı (panelde kırmızı)
> "Roo Code karmaşık istemler kullanır ve Claude modelleriyle en iyi şekilde çalışır."

Bu uyarı §3.5'teki **D-48 kapsam sınırını doğruluyor**: yerel modeller ana model değil; mimari karar / çoklu dosya refactor / güvenlik incelemesi bulut profillerine gider.

## 4. Verimlilik Kriterleri (kaynak: `AI proje v1/V10/09_kurallar_ve_promptlar/04_token_verimliligi_ve_dil_politikasi.md` BÖLÜM 3)
| # | Kriter | Tasarruf | Roo Code'a uyarlama |
|---|--------|----------|---------------------|
| K1 | Delta-Only Board Okuma (`gorev_getir` 50 tk vs tam board 2000 tk) | -1500/-2000 | ⏳ |
| K2 | Görev Brief (keşif token'ı sıfırlanır) | -2000/-3000 | ✅ brief deseni kullanılıyor |
| K3 | Session Handoff (`tamamlandı/sonraki_adım/dikkat`) | -2000/-4000 | ⏳ |
| K4 | Sıkıştırılmış AGENT_SYNC (satır ≤80 karakter) | -1000/-1500 | ⏳ |
| K5 | Tool call çıktısı kısalt (≤500 tk/call) | -1000/-2000 | ⏳ |
| K6 | Otomatik "ne okunmalı" listesi | -1500/-3000 | ⏳ |
| K7 | Retry/backoff optimizasyonu | — | ⏳ satır 401-451 okunmadı |

Net proje hedefi: oturum başına ~18000 → ~7000 token (%60). **K5/K7 uygulanırken D-48 ihlal edilmez** — çıktı kısaltma tool sonucu içindir, modelin düşünmesi için değil.

## 5. Açık Sorular
- [ ] cline'ın "2 GitHub linkli token verimliliği raporu" bulunamadı. Tarananlar: tüm `*.md` (49 github.com eşleşmesi), `data/orchestrator/*.jsonl`, `AGENT_SYNC.md`. Sahipten link istenecek.
- [ ] `04_token_verimliligi_ve_dil_politikasi.md` satır 401-451 (K7 devamı) okunacak.

## 6. Değişiklik Günlüğü
| Tarih | Değişiklik |
|-------|-----------|
| 2026-09-17 | Dosya oluşturuldu. D-48 kaydedildi. `ROO-CONFIG-01` kilo'ya atandı + tetik. |
| 2026-09-17 | Model kombinasyonu kuruldu: 13 ücretsiz + 3 ucuz OR ücretli + Sonnet son yedek = 17 model, `--dogrula` 18/18 OK, `~/.continue/config.json` yazıldı (`.bak` alındı). DeepSeek doğrudan 402 → OR üzerinden. |
| 2026-09-17 | **Yerel katman eklendi (§3.5):** Ollama 2 sohbet modeli + yerel autocomplete. `qwen2.5-coder:3b` indirildi (1.9 GB). `continue_config_kur.py` içine `provider == "ollama"` dalı (apiBase + `/v1`, dummy anahtar) ve autocomplete atlama kuralına ollama istisnası. `--dogrula` **19/19 OK**, config diske yazıldı. Autocomplete Groq GPT-OSS 20B → yerel (maliyet sıfır). `gemma4:26b` VRAM'e sığmadığı için dışarıda. |
| 2026-09-18 | **§3.6 Roo Code profil şeması:** 20 gerçek slug'la 12 profil tablosu + provider zorunlu alanlar tablosu + teşhis listesi. `--dogrula` **20/20 OK**, `api_anahtar_testi.py` → AKTIF=15/OLU=6 (Groq OLU = hesap sorunu). |
| 2026-09-18 | **§3.7 KARAR:** Yerel modeller (Ollama) Roo Code agent modunda **kullanılmaz** — kanıt: bozuk araç çağrısı JSON'u, sahte 128k bağlam, provider `OpenAI Compatible` yanlış seçimi. Yerel katman Continue autocomplete'te kalır. Roo ana hat: OpenRouter free → ucuz OR → Sonnet. |
| 2026-09-18 | **Merve 👩‍💻 (Continue IDE) kuruldu:** KAHİN onayıyla `docs/continue_config.json` kök seviyesine `systemMessage` eklendi (3585 karakter). `continue_config_kur.py` değişmedi — `yapilandirma_uret()` satır 80 kök alanları `models` hariç aynen taşıyor. Kurulum çalıştı: 19 model + systemMessage `~/.continue/config.json`'a yazıldı (`.bak` alındı). Doğrulama: `KAHIN/Merve/abrakadabra` anahtarları geçti. |
| 2026-09-18 | **D-49 hitap demir kuralı:** Ürün Sahibi'ne tüm ajanlar `KAHİN (Ürün Sahibi)` der; "sahip/kullanıcı/efendim" yasak. Merve dördüncü ajan = danışman (dosya yazmaz, görev almaz, komut çalıştırmaz, panoya girmez). `AGENTS.md` + `decision_log.jsonl` güncellendi. İlk görev: `docs/plans/MERVE-GOREV-01.md`. |
| 2026-09-18 | **Gece kuruluşu (KAHİN emri):** 2 zincir kuruldu — kilo: `ADMIN-HATA-02` → `ADMIN-KPI-KART-02` → `ADMIN-MUSTERI-02`; roo: `ADMIN-KOK-TEMIZLIK-01` → `ADMIN-HITAP-01` → `ADMIN-ROO-DENETIM-01`. Merve 2. görev: `docs/plans/MERVE-GOREV-02.md`. `TG-01` onaylandı → done. Push `f68b122` (19 dosya, +439/-109). |
| 2026-09-18 | **3 karar KAHİN tam yetkisiyle verildi:** `D-50` ROO-CONFIG-01-B1 kapatıldı (content-safety modeli moderasyon sınıfı, kodlama fallback olamaz; primary fallback `nvidia/nemotron-3.5-lightning:free`, son yedek `claude-sonnet-4-5`). `D-51` TEST-ISO-03 geri alma yapılmayacak (`data/dummy/firmalar.jsonl` zaten dummy; koruma `conftest.py` izolasyonunda). `D-52` K-02 çözüldü (cline çapraz doğrulaması temiz). |
| 2026-09-18 | **Pano temizliği (KAHİN emri "pano görevleri azalsın"):** roo bekleyen tetik 12 → 3. Kapatılan 9: KPI-KART-01 çapraz+düzeltme, SEC-AUTH-01-ASAMA-B, GIT-HIJYEN-01 çapraz, TEST-ISO-03-FIRMALAR (D-51), KOK-TEMIZLIK-ENVANTER (göreve dönüştü), ROO-CONFIG-01 çapraz + B1-ACIK (D-50), K-02-DOGRULAMA (D-52). Kalan 3: `MARKA-REVIZE-01-BULGU`, `AGN-STACK-01`, `ADMIN-KOK-TEMIZLIK-01` (aktif zincir). |
| 2026-09-18 | **roo zinciri tamamlandı (3/3 done):** `ADMIN-KOK-TEMIZLIK-01` (kök `fix_*.py` x3 silindi, `.gitignore` kuralı), `ADMIN-HITAP-01` (D-49 uygulaması — `AGENTS.md`, `docs/AJAN_DETAY.md`, `docs/ARASTIRMA_API_PLAN_2026-09-17.md` toplam 7 satır `sahip` → `KAHİN`; kod parametresi / JSON şema alanı / otomatik tablo başlıkları muaf), `ADMIN-ROO-DENETIM-01` (sonuç **KISMİ** — kilo 3 tetiğin hiçbirini almamış). Denetim bulguları `D-53`: D-1 tetik duplikasyonu (`ADMIN-HATA-01` 2 kayıt, `bakim` dedupe yakalamıyor), D-2 5x uyarıya rağmen eskalasyon yok, D-3 zincir blokajı sessiz. Kod fixi kapsam dışı → `ORCH-TETIK-DEDUPE-01` önerildi. |
