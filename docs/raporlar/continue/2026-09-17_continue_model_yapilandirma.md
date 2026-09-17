# Continue IDE Model Yapılandırması — Tam Kayıt (2026-09-17)

> Arşiv klasörü: `docs/raporlar/continue/`
> Bu dosya = tüm turun kalıcı kaydı (kök nedenler, karar, model tablosu, elenenler, rutin).

## 0. Özet

| Konu | Durum |
|---|---|
| Model sayısı | 5 → **14** (13 ücretsiz + 1 ücretli) + 1 autocomplete |
| Gerçek POST doğrulaması | **15/15 OK**, exit 0 |
| Kurulum | `C:\Users\yasin\.continue\config.json` yazıldı, `.bak` alındı |
| Haftalık tarama | `--tara` alt komutu + `scripts/continue_tarama_haftalik.cmd` |
| Rapor arşivi | `docs/raporlar/continue/` |

---

## 1. Kök nedenler (çözülen hatalar)

| Hata | Kök neden | Çözüm |
|---|---|---|
| `401 Missing Authentication header` | Continue JSON'da `${env:X}` genişletmesi **yapmaz** | Kurucu script anahtarı kurulum anında dosyaya basar |
| `403 error code: 1010` (Groq/Together) | Cloudflare bot koruması, UA yok | `UA` sabiti eklendi |
| Together `HTML 404` | Yanlış apiBase + geçersiz anahtar (401) | Listeden çıkarıldı |
| Groq `llama-3.3-70b-versatile` 404 | Model hesapta yok | Çıkarıldı |
| DeepSeek `402 Insufficient Balance` | OpenRouter'da **21 deepseek slug'ının hiçbiri `:free` değil** | Listeye alınmadı |
| `--dogrula` çöküyor (`unknown url type`) | Anthropic kaydında `apiBase` yok; `/chat/completions` eklenemiyor | `anthropic_testi()` dalı: `POST /v1/messages` + `x-api-key` |

**Yöntem dersi:** `GET /models` **yetersiz**. Slug listede olsa da çağrı 404/429/403 dönebilir. Her model `POST /chat/completions` (`max_tokens: 1`) ile denenir.

### HTTP kodu → anlam
| Kod | Anlam |
|---|---|
| `401 Missing Authentication header` | Header hiç yok (env genişletmedi) |
| `401 Invalid API key` | Anahtar geçersiz |
| `402 Insufficient Balance` | Ücretli / bakiye yok |
| `403 error code: 1010` | Cloudflare UA koruması |
| `403 is only available to...` | Model belirli hesaplara kısıtlı |
| `404 model_not_found` | Slug yok |
| `429` | Kota / upstream rate-limit |

---

## 2. Aktif model listesi (14 + autocomplete)

| # | Başlık | slug | Sağlayıcı | ctx |
|---|---|---|---|---|
| 1 | `[UCRETSIZ] OR · Nemotron 3 Ultra 550B (1M, en guclu)` | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | 1.000.000 |
| 2 | `[UCRETSIZ] OR · Nemotron 3 Super 120B` | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 262.144 |
| 3 | `[UCRETSIZ] OR · Nemotron 3.5 Lightning (1M, hizli)` | `nvidia/nemotron-3.5-lightning:free` | OpenRouter | 1.000.000 |
| 4 | `[UCRETSIZ] OR · North Mini Code (kod odakli)` | `cohere/north-mini-code:free` | OpenRouter | 256.000 |
| 5 | `[UCRETSIZ] OR · Nemotron 3 Nano Omni 30B (reasoning)` | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | OpenRouter | 256.000 |
| 6 | `[UCRETSIZ] OR · Nex N2.5 Pro` | `nex-agi/nex-n2.5-pro:free` | OpenRouter | 262.144 |
| 7 | `[UCRETSIZ] OR · Nex N2.5 Mini` | `nex-agi/nex-n2.5-mini:free` | OpenRouter | 262.144 |
| 8 | `[UCRETSIZ] OR · Dots 3 Note Preview (512k)` | `dots-studio/dots-3-note-preview:free` | OpenRouter | 512.000 |
| 9 | `[UCRETSIZ] OR · LFM 2.5 2.6B (cok hafif)` | `liquid/lfm-2.5-2.6b:free` | OpenRouter | 65.536 |
| 10 | `[UCRETSIZ] NVIDIA · Nemotron 3.5 Lightning 30B` | `nvidia/nemotron-3.5-lightning-30b-a3b` | NVIDIA | 128.000 |
| 11 | `[UCRETSIZ] Groq · GPT-OSS 120B (hizli, guclu)` | `openai/gpt-oss-120b` | Groq | 131.072 |
| 12 | `[UCRETSIZ] Groq · GPT-OSS 20B` | `openai/gpt-oss-20b` | Groq | 131.072 |
| 13 | `[UCRETSIZ] Groq · Qwen 3.8 27B` | `qwen/qwen3.8-27b` | Groq | 131.072 |
| 14 | `[UCRETLI] Anthropic · Claude Sonnet 4.5 (ACIL IS)` | `claude-sonnet-4-5` | Anthropic | 200.000 |
| tab | `[UCRETSIZ] Groq · GPT-OSS 20B (autocomplete)` | `openai/gpt-oss-20b` | Groq | — |

**Başlık kuralı:** ücretsizler `[UCRETSIZ]`, ücretliler `[UCRETLI]`; ücretliler listenin **en sonunda**.

**Çapraz kullanım:** 3 ayrı kota havuzu — OpenRouter (9) · NVIDIA (1) · Groq (3+1). Biri tükenirse diğerine geçilir, OpenRouter kredisi korunur.

---

## 3. Elenenler (gerçek POST testi, 2026-09-17)

| slug | Sonuç | Neden |
|---|---|---|
| `poolside/laguna-s-2.1:free` | KOTA 429 | upstream kuyruk dolu |
| `poolside/laguna-xs-2.1:free` | KOTA 429 | aynı |
| `z-ai/glm-5.2:free` | KOTA 429 | aynı |
| `qwen/qwen3.8-27b:free` (OR) | KOTA 429 → sonra OK | Groq sürümü zaten listede |
| `google/gemma-4-26b-a4b-it:free` | KOTA 429 | kararsız |
| `google/gemma-4-31b-it:free` | KOTA 429 | kararsız |
| `thinkingmachines/inkling:free` | YETKI 403 | "is only available to..." — kısıtlı hesap |
| `thinkingmachines/inkling-small:free` | YETKI 403 | aynı |
| Together tüm modeller | 401 | anahtar geçersiz (sahip kararı bekliyor) |
| DeepSeek (21 slug) | — | **hiçbiri `:free` değil** |

---

## 4. Sonnet 4.5 vs Nemotron 3 Ultra 550B — güç / verim

| Kriter | `[UCRETLI]` Claude Sonnet 4.5 | `[UCRETSIZ]` Nemotron 3 Ultra 550B |
|---|---|---|
| Kod kalitesi / çok adımlı akıl yürütme | **Belirgin üstün** | İyi, ama uzun zincirde sapma artar |
| Talimata uyum (format, kısıt) | **Üstün** | Orta |
| Bağlam penceresi | 200k | **1M** |
| Gecikme | Düşük, kararlı | Değişken — OR upstream kuyruğu, 429 riski |
| Maliyet | ~$3/M giriş · ~$15/M çıkış | **0** |
| Kararlılık (kesinti) | Yüksek | Ücretsiz katman, garantisiz |

**Kullanım kuralı:**
- **Rutin iş, büyük dosya okuma, toplu tarama** → Nemotron Ultra (1M ctx, bedava).
- **Acil iş, kritik refactor, karmaşık hata ayıklama, tek seferde doğru olması gereken** → Sonnet 4.5.

### KRİTİK BULGU — Anthropic iki ayrı cüzdan
`ANTHROPIC_API_KEY` (pay-per-token, `api.anthropic.com/v1/messages`) ile **Claude Pro/Max aboneliğinin 5 saatlik yenilenen penceresi AYRIDIR**.

→ Continue'dan Sonnet kullanmak **Claude Code / GitHub kotanızı tüketmez**. Ayrı faturalanır (token başına).
→ Kanıt: canlı test `HTTP 200`, anahtar son4=`vQAA`.

Yani "hızlı kota bitiyor" sorunu Continue tarafında **yok**; Continue'daki Sonnet kendi cüzdanından harcar.

---

## 5. Otomatik model değiştirme (fallback)

Continue'da **yerleşik otomatik geçiş yok**. Üç yol:

| Yol | Nasıl | Değerlendirme |
|---|---|---|
| A) Manuel geçiş | 14 model menüde; biri 429 verince elle seç | Şu anki durum. Sıfır risk, sıfır bakım. |
| B) OpenRouter `"models": [...]` dizisi | Tek kayıtta yedek slug listesi; OR kendi içinde sıradakine geçer | **Önerilen.** Sadece OR modelleri için çalışır, ek altyapı yok. |
| C) LiteLLM yerel proxy | Proxy tüm sağlayıcılar arası gerçek failover yapar | Gerçek çözüm ama yeni servis + bakım yükü. |

Sahip kararı bekliyor.

---

## 6. Haftalık rutin (kuruldu)

```
python scripts/continue_config_kur.py --tara
```
- OpenRouter kataloğunu çeker (445 slug), şablonda **olmayan** `:free` slug'ları bulur.
- Her birini **gerçek POST** ile dener.
- Rapor yazar: `docs/raporlar/continue/tarama_<tarih>.md`.

**Zamanlanmış görev kurulumu (tek seferlik, sahip çalıştırır):**
```
schtasks /Create /TN "Huginn-Continue-Tarama" /TR "\"c:\Huginn Data Projesi\Huginn Data Insights\scripts\continue_tarama_haftalik.cmd\"" /SC WEEKLY /D MON /ST 09:00 /F
```

**İlk tarama sonucu (2026-09-17) — 5 yeni aday OK:**
- `inclusionai/ling-3.0-flash-fin:free`
- `inclusionai/ling-3.0-flash-sante:free`
- `inclusionai/ling-3.0-flash-vl:free`
- `nvidia/nemotron-3.5-content-safety:free`
- `qwen/qwen3.8-27b:free`

(Hepsi dar amaçlı: fin/sağlık/görsel/içerik güvenliği. Genel kodlama için katkısı düşük → şablona **eklenmedi**, kayda geçti.)

---

## 7. Komut referansı

| Komut | İş |
|---|---|
| `python scripts/continue_config_kur.py` | Kur (yedek alır, `~/.continue/config.json` yazar) |
| `python scripts/continue_config_kur.py --kontrol` | Yazmadan özet |
| `python scripts/continue_config_kur.py --dogrula` | 15 modeli gerçek POST ile test et |
| `python scripts/continue_config_kur.py --tara` | Yeni `:free` modelleri ara + rapor |

**Çıkış kodları:** `0` başarı · `1` şablon yok · `2` anahtar çözülemedi · `3` sorunlu model var.

---

## 8. Açık işler

- [ ] Sahip: VS Code tamamen kapat+aç; Continue arayüzünden **elle eklenen** `deepseek`/`glm`/`anthropic` kayıtlarını sil (kurucu script bunları yönetmez).
- [ ] Fallback kararı: A / B / C.
- [ ] **GÜVENLİK — 5 anahtar rotate:** `DEEPSEEK_KEY`, `OPENROUTER_API_KEY`, `KIMI_API_KEY`, `BAZARLINK_API_KEY`, `GROQ_API_KEY`. Sonra `.env` güncelle + kurucu tekrar.
- [ ] Together anahtarı geçersiz (401) — yeni anahtar mı, bırakılsın mı.
- [ ] `docs/ARASTIRMA_API_PLAN_2026-09-17.md` §1 düzelt (Groq 403 = Cloudflare UA, Model Terms değil).

---

## 9. Dosyalar

| Yol | İş |
|---|---|
| `docs/continue_config.json` | Şablon (SSOT). Anahtar YOK, `${env:X}` yer tutucu. |
| `scripts/continue_config_kur.py` | Kurucu + doğrulayıcı + tarayıcı (stdlib-only). |
| `scripts/continue_tarama_haftalik.cmd` | Haftalık zamanlanmış görev sarmalı. |
| `docs/raporlar/continue/` | Bu arşiv + haftalık tarama raporları. |
| `C:\Users\yasin\.continue\config.json` | **Üretilen** dosya — düz anahtar içerir, repo dışı, paylaşılmaz. |
