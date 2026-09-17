# API Anahtarları — Envanter ve Ortak Kullanım

Test aracı: `python scripts/api_anahtar_testi.py` (tek sağlayıcı: `... openrouter`)
Son test: 2026-09-17 · **AKTIF=14 · OLU=6**
Açık tanı/aksiyon dosyası: [`docs/ARASTIRMA_API_PLAN_2026-09-17.md`](ARASTIRMA_API_PLAN_2026-09-17.md)

## Kurallar (ihlal = anahtar bulunamaz)
1. Anahtar **adı ASCII** olmalı. Türkçe `İ` (U+0130) kullanılırsa `os.getenv()` bulamaz.
   Geçmiş hata: `ANTROPİC_API_KEY`, `OPENAİ_API_KEY`, `TAVİLY_API_KEY`, `KİLO_GATEWAY_API_KEY`.
2. Aynı ad **iki kez** yazılmaz. dotenv **sonuncuyu** alır; ilk satır ölü kalır.
   Geçmiş hata: iki `OPENROUTER_API_KEY` — canlı olan ölü olan tarafından eziliyordu.
3. Değerler yalnız `.env`'de. `.env.example` şablon (boş değerler), git'e giren tek sürüm.
4. Ölü anahtar silinmez, `# OLU_<tarih>` önekiyle yorumlanır (geri dönüş kolay olsun).

## Aktif sağlayıcılar (14)
| Sağlayıcı | ENV adı | Kullanım |
|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | Continue IDE (free modeller) · kredi yüklü |
| Deepseek | `DEEPSEEK_KEY` | doğrudan API |
| OpenAI | `OPENAI_API_KEY` | doğrudan API |
| Anthropic | `ANTHROPIC_API_KEY` | doğrudan API |
| NVIDIA NIM | `NVIDIA_API_KEY` + `NVIDIA_BASE_URL` | OpenAI uyumlu |
| Moonshot | `MOONSHOT_API_KEY` | OpenAI uyumlu |
| Kimi | `KIMI_API_KEY` | OpenAI uyumlu (2026-09-17 yeni anahtar) |
| Brave Search | `BRAVE_API_KEY` | MCP web arama |
| Tavily | `TAVILY_API_KEY` | arama/araştırma |
| Exa | `EXA_API_KEY` | `scripts/exa_arastir.py` |
| Firecrawl | `FIRECRAWL_API_KEY` | web kazıma |
| Cloudflare | `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` | altyapı |
| GitHub | `GH_TOKEN` | PR/Actions okuma |
| Ollama | `OLLAMA_API_KEY` + `OLLAMA_BASE_URL` | yerel model |
| Apify | `APIFY_TOKEN` | web scraping actor (iş ilanı / kariyer sayfası) — `src/company_master/intelligence/job_intelligence/sources/apify_client.py` |

## Ölü sağlayıcılar (6) — karar gerekli
| Sağlayıcı | ENV adı | HTTP | Tanı | Yapılacak |
|---|---|---|---|---|
| Groq | `GROQ_API_KEY` | 403 | **plan değil** — Free zaten "Current Plan" (sahip ekranı) | Model Terms kabulü / anahtarın projesi / VPN → §1 |
| Together | `TOGETHER_API_KEY` | 403 | plan kapalı | **para yükle** ya da anahtar yenile (öneri: yükleme) |
| xAI | `XAI_API_KEY` | 403 | plan kapalı | **para yükle** (xAI ücretsiz katman yok — öneri: yükleme) |
| BazaarLink | `BAZARLINK_API_KEY` + `BAZARLINK_API_URL` | 403 | agent self-kaydı **kapatıldı** (2026-09-05, `/agents/register` → 410); eski agent anahtarları iptal | normal hesap aç → panelden yeni anahtar üret → §3 |
| Perplexity | `PERPLEXITY_API_KEY` | 400 | istek gövdesi/model adı şüpheli | test isteği düzelt, sonra yeniden bak (düşük) |
| 9Router | `NINEROUTER_KEY` + `NINEROUTER_URL` | 403 | gateway tarafı | §2.1 tanı sırası; yedek gateway olarak kalır |

**Öncelik kuralı (sahip):** ücretsiz modeller önce. Ücretli katman yalnız ücretsizi tükettikten sonra.
Ücretsiz/kredili aktif üçlü: OpenRouter (`:free` modeller) → Ollama (yerel, bedava) → NVIDIA NIM (ücretsiz kota).

## Ortak kullanım deseni
Her araç `.env`'i okur, anahtar adı yukarıdaki tabloyla aynıdır. Yeni araç eklerken
kendi ad şeması **uydurulmaz**, bu tablodaki ad kullanılır.

| Araç | Okuduğu anahtarlar | Yapılandırma dosyası |
|---|---|---|
| Continue IDE | `OPENROUTER_API_KEY`, `BRAVE_API_KEY` | `docs/continue_config.yaml` → `.continue/config.yaml` |
| `scripts/exa_arastir.py` | `EXA_API_KEY` | — |
| `scripts/api_anahtar_testi.py` | hepsi (yalnız okur, asla basmaz) | — |
| FastAPI / Streamlit | `DATABASE_URL`, `ADMIN_*` | `docker-compose.yml` / `.streamlit/` |

## HTTP kodu → anlam
`401` anahtar geçersiz · `402` ödeme gerekli · `403` plan kapalı/yetki yok ·
`429` kota dolu (anahtar **geçerli**) · `400` istek hatalı (anahtar suçlu değil) · `404` endpoint değişmiş.
