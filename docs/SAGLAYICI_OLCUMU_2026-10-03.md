# 9Router Web Sağlayıcı Ölçümü — 2026-10-03

**Sonuç:** 15 arama sağlayıcısından **8'i**, 7 fetch sağlayıcısından **5'i** çalışıyor. Combo'lar iyileşti (fetch-combo artık tavily'ye düşüyor: 37 ihale). Varsayılan `arac_dongusu.py` sabitleri `fetch-combo` / `search-combo` yapıldı.

Tekrar ölçüm: `python scripts/saglayici_olc.py liste|ara|getir|patent` (bkz. [`scripts/saglayici_olc.py`](../scripts/saglayici_olc.py)).

Önceki benzer çalışmalar: [[v10_OSINT_YETENEK_KATALOGU]] (9R-04, 2026-09-12 — web_fetch/web_search sözleşmesi), [[9r05_adim1_monitor_plan]] (combo otomatik fallback; yanıttaki `provider` alanı), [[9router_web_search_SKILL]], [[9router_web_fetch_SKILL]].

## 1. Gerçek kayıtlı sağlayıcılar — `/v1/models/web` (12 kayıt)

| Tür | Kayıtlı | Dashboard'da "bağlı" görünüp listede OLMAYAN |
|---|---|---|
| Arama | `search-combo`, `tavily`, `exa`, `brave`, `searchapi`, `ollama-search`, (`serper` 11:29'da eklendi) | perplexity, perplexity-agent, kimi, xai, openai, gemini, antigravity, searxng |
| Fetch | `fetch-combo`, `tavily`, `firecrawl`, `jina-reader`, `exa`, `ollama` | ollama-cloud |

Ders: ekranda "bağlı" ≠ kayıtlı. Yalnız `/v1/models/web`'de olanlar sayılır.

## 2. Arama — "DMO ihale listesi ekim 2026" (11:24) + serper turu (11:29)

| Sağlayıcı | Süre | DMO ilk 3'te | .gov.tr/5 | Not |
|---|---|---|---|---|
| **brave** | 1.0–1.3s | EVET | **5** | en hızlı, en isabetli, ücretsiz |
| search-combo | 2.2–4.5s | EVET | 3–4 | ilk sırada **tavily**'ye düşüyor |
| tavily | 1.7–3.6s | dalgalı (bir koşuda 0) | 0–4 | tek başına güvenilmez |
| exa | 2.1s | EVET (`/SM/Ihale`) | — | |
| searchapi | 5.2s | EVET | — | |
| serper | 1.3–3.3s | EVET | 3 | **ücretli**, 2.499 kredi |
| ollama-search | 1.8s | EVET | — | |
| perplexity-agent | 7.5s | EVET | — | yavaş |
| perplexity | — | 401 Invalid API key | | KIRIK |
| kimi | — | 401 Invalid Authentication | | KIRIK |
| xai | — | 403 team has no credit | | KIRIK |
| searxng | — | 502 Blocked URL: internal host | | KIRIK |
| openai | — | 502 Failed to parse URL | | KIRIK |
| gemini | — | 404 gemini-2.5-flash no longer | | KIRIK |
| antigravity | **56.9s** | 503 No capacity | | KIRIK + bekletiyor |

## 3. Fetch — DMO `/Ihale/Liste?type=1` ve Resmî Gazete

| Sağlayıcı | DMO süre | DMO karakter | DMO ihale | RG karakter | Not |
|---|---|---|---|---|---|
| **fetch-combo** | 1.2s | 20.000 | **37** | 3.220 | tavily'ye düşüyor (önce jina/8.734 idi) |
| tavily | 1.1s | 20.000 | 37 | 3.220 | |
| firecrawl | 1.1s | 16.594 | 30 | 3.374 | |
| jina-reader | 8.7s | 8.734 | 30 | 6.286 (14.5s) | yavaş |
| exa | 0.6s | 14.823 | **0** | 1.053 | DMO tablosunu okumuyor |
| ollama | — | 401 / 502 | | | KIRIK |
| ollama-cloud | — | 400 Unknown provider | | | yanlış ad |

## 4. Patent sorgusu — "firmaların patentleri" (11:37)

| Yol | Sonuç |
|---|---|
| SearchAPI doğrudan `engine=google_patents` | **401 Invalid API key** (`.env` anahtarı ölü) |
| 9Router `searchapi` + `extra={"engine": "google_patents"}` | `engine` düşüyor; 5 sonuç, 0 patent URL'si |
| 9Router `brave` `site:patents.google.com ASELSAN` | 3.5s, **5/5 patent** |
| 9Router `search-combo` aynı soru | 2.5s, 5/5 patent (tavily) |
| 9Router `serper` aynı soru | 9.4s, 5/5 patent (ücretli) |

Karar: patent için ayrı motor **gerekmez**; `site:patents.google.com <firma>` kalıbı `ARA` komutuyla yeter. SearchAPI'nin kategori ağacı (Scholar, News, Jobs, Maps…) 9Router'dan geçmiyor; gerekirse doğrudan SearchAPI çağrısı ayrı bir araç olur (yeni anahtar şart).

## 5. Apify

Hesap: `yasua_Hugin_Munin`, plan **FREE**, aylık tavan 10 $, kullanılmış ≈ 0 $. Bu ay 2026-10-09'da sıfırlanır. Şimdilik kullanan kod yok; F2'de EKAP (Cloudflare) için aday — ayrı onay.

## 6. 9Router UI'da önerilen combo sırası (koddan değil, dashboard'dan ayarlanır)

| Combo | Önerilen sıra | Gerekçe |
|---|---|---|
| search-combo | **brave → tavily → exa → searchapi → serper** | hız + .gov.tr isabeti; serper en sonda (kredi) |
| fetch-combo | **tavily → firecrawl → jina-reader** | 37 ihale; exa dışarı (0 ihale) |

## 7. Kod değişikliği

`src/company_master/odin_ai/arac_dongusu.py`: `FETCH_SAGLAYICI = "fetch-combo"`, `SEARCH_SAGLAYICI = "search-combo"`. Tek sağlayıcı yerine combo: biri düşerse 9Router kendisi sıradakine geçer.

## Öz-eleştiri

- Tavily'nin dalgalı olduğunu tek koşuda gördüm; 3 koşu ortalaması almadım. Betik artık kalıcı, tekrar koşmak ucuz.
- Antigravity'nin 57 s beklettiğini combo listesinde olup olmadığına bakmadan not ettim; combo'da olsaydı her ARA 57 s gecikirdi — UI'dan çıkarıldığı doğrulanmalı.
- Serper'ı eklerken kredi sayacını ölçmedim (yanıtta kredi alanı yok); UI'dan takip edilecek.

## Ilgili Nodlar

- [[BORC_DEFTERI]] — `BORC-9ROUTER-SAGLAYICI-KIRIK-01`
- [[v10_OSINT_YETENEK_KATALOGU]]
- [[9r05_adim1_monitor_plan]]
- [[9router_web_search_SKILL]]
- [[9router_web_fetch_SKILL]]
- [[mimir_sistem_promptu]]
- [[ODIN_GUVENLIK_ATIF]]
