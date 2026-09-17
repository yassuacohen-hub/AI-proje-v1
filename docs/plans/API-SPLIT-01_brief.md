# API-SPLIT-01 — web_app.py (3268 satır) modüllere bölme (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-01_ortak_kurallar.md`. Zincir halkası 6/6 (en ağır, en son).

## Hedef
`web_app.py` → `src/company_master/api/` paketi; `web_app.py` yalnız uygulama kurulumu + router include + **geriye uyumlu re-export**. Davranış birebir aynı (aynı path'ler, aynı yanıtlar).

## Kapsam / kilit
- `web_app.py`, `src/company_master/api/**` (yeni), `tests/test_api_*.py`, `tests/test_web_app*.py`, `Dockerfile` (yalnız import yolu gerekiyorsa).
- `web_dashboard/**`, `app.py` dokunma.

## Modül planı (öneri; mantıklı sapma rapora)
| Modül | İçerik (web_app.py satır ~) |
|---|---|
| `api/core/normalize.py` | `_tr_*`, `normalize_company_name`, `extract_trade_name`, `normalize_company`, `tr_normalize`, KVKK mask (103-645) |
| `api/core/security.py` | `require_api_key`, `_user_from_api_key`, `_record_api_usage`, rate limit, token/hash yardımcıları (693-786, 1693-1749) |
| `api/core/cache.py` | `cache_get`, `admin_cache` |
| `api/routers/webhooks.py` | `/api/webhooks/apify*` (846-971) |
| `api/routers/companies.py` | `/api/companies*`, `/api/company/{id}`, `/api/nace-distribution`, `/api/sources`, `/api/quality-trend` |
| `api/routers/match.py` | `_match_puan`, `_profil_bonus`, `buyer_scale_uygun`, `/api/match` |
| `api/routers/buyer.py` | `/api/buyer/*`, `/api/me`, e-posta/telegram yardımcıları, DATA-LOG-01 `_log_*` |
| `api/routers/admin.py` | `require_admin`, `/api/admin/*` |
| `api/routers/intelligence.py` | `_fetch_dashboard_data`, `/api/intelligence/*`, `/metrics`, `/api/kpi`, `/api/dashboard` |

## Zorunlu yöntem
1. Önce `grep -n "monkeypatch.setattr(web_app\|web_app\.\|from web_app import" tests/` → testlerin `web_app` üzerinden eriştiği isimlerin listesini çıkar (rapora). Bu isimler `web_app.py`'de re-export edilir **ve** monkeypatch'in etkili olması için ilgili fonksiyon modül-globalini `web_app` üzerinden değil kendi modülünden okuyorsa test uyarlanır (`monkeypatch.setattr(api.core.security, ...)`). Testin ne test ettiği değişmez.
2. Bölme sırası (bağımsızdan bağımlıya): normalize → cache/security → webhooks → intelligence → companies → match → buyer → admin. **Her adımdan sonra tam süit yeşil**; kırmızıysa o adımı düzelt, ilerleme.
3. Router'lar `APIRouter` ile; `web_app.py` `app.include_router(...)`. Route path/method/response_model değişmez → `python -c "import web_app; print(sorted(r.path+' '+','.join(r.methods) for r in web_app.app.routes))"` çıktısı **önce/sonra birebir eşit** (rapora diff=0).
4. `Depends(require_api_key)` / `require_admin` importları merkezi (`api/core/security.py`).
5. Docker açıksa: `docker compose up -d --build api` + `curl -s localhost:8000/api/webhooks/apify/health`; kapalıysa atla, rapora yaz.

## Yapılmayacaklar
- Davranış/iş mantığı değişikliği, endpoint ekleme/silme, "bu arada" temizlik.
- `web_app.py`'yi silme; 300 satır altına inmesi yeterli.

## Teslim kriteri
- Route listesi diff=0; tam süit yeşil (sayı değişmez); kodlama_denetim temiz.
- Rapor: `data/orchestrator/API-SPLIT-01_rapor_<tarih>_kilo.md` (modül tablosu satır sayıları, re-export listesi, test uyarlamaları dosya:satır).
