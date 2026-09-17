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
| (b) | Roo Code yapılandırma (ücretsiz modeller + fallback) | ⏳ kilo teslimi bekleniyor |
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
