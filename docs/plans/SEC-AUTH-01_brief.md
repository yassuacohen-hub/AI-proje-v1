# SEC-AUTH-01 — Auth Uçları Güvenlik Düzeltmeleri (cline)

**Kaynak:** `data/orchestrator/REV-BATCH-01_rapor_2026-09-16_cline.md` (Y-1..Y-4, O-1, O-2, D-1, D-4)
**Sahip ajan:** cline (bulguyu bulan düzeltir; kilo BATCH-02'de `app.py` + `web_app.py` kilitli → **sıralama zorunlu**, aşağıda)
**Öncelik:** P1 · **Onay:** roo

## Ortak Kurallar (BATCH-01 ile aynı)
- Teslim komutu zorunlu; commit ATMA (roo commitler); `python scripts/kodlama_denetim.py` temiz; tam regresyon (`python -m pytest -q`).
- UI dosyasına dokunulursa `python scripts/streamlit_restart.py`; `web_app.py` değişirse `docker compose up -d --build api` + curl doğrulama.
- Şifre/token loglama YASAK. Hata mesajları kullanıcı var/yok sızdırmaz.

## Aşama A — kilitsiz dosyalar (hemen başla)
| # | Bulgu | Dosya | Yapılacak |
|---|---|---|---|
| Y-3 | `_env_kimlik` DEBUG kapısı yok | `web_dashboard/tabs/admin_auth.py` | `os.getenv("DEBUG") != "1"` → `("admin@huginn.local", "")`; caption yalnız DEBUG'da |
| Y-4 (UI tarafı) | misafir `admin_token="guest"` | `web_dashboard/tabs/admin_auth.py` | `get_admin_token()` misafirde `None`; misafir bayrağı `st.session_state["misafir"]=True` |
| O-1 | ESKI_URL ölü yönlendirme | `web_dashboard/tabs/__init__.py` | `kimlik`/`yonetim` SECTIONS'tan çıkar **veya** `tab_url_getir` içinde ESKI_URL önceliği; test `tab_url_getir` üzerinden parametrik |
| D-1 | secrets.toml | `.gitignore` | `.streamlit/secrets.toml` girdisi ekle |
| O-4 | AST seviyesi auth testleri | `tests/test_auth_gate.py` | TestClient + `dev_modu` fixture ile davranışsal testler: tek 401 mesajı, reset TTL, tek kullanım, 429 |

**DİKKAT:** `web_dashboard/tabs/__init__.py` şu an kilitsiz (NAV-IA-03 onaylandı). `admin_auth.py` **NAV-IA-04 kilidinde** → kilo NAV-IA-04'ü teslim edip roo onaylayana kadar dokunma; Aşama A'da önce `__init__.py`, `.gitignore`, `tests/test_auth_gate.py` ile başla, `admin_auth.py` kilit düşünce.

## Aşama B — `web_app.py` (kilo DATA-LOG-01 teslimi + roo onayı SONRASI; roo tetik atar)
| # | Bulgu | Yapılacak |
|---|---|---|
| Y-1 | auth uçlarında rate-limit yok | IP bazlı 5/dk dependency (`src/company_master/api/rate_limiter.py` yeniden kullan); `/api/admin/login`, `reset-request`, `reset-confirm`, `change-password` |
| Y-2 | var/yok sızması | login her durumda tek `401 "gecersiz email veya sifre"`; reset-request bilinmeyen e-postada da `{"ok": true}`; UI `st.error` genel mesaj |
| Y-4 (API tarafı) | `aktif_rol()` guest → admin | `app.py:151` guest'i anon'a indirge (app.py NAV-IA-04 kilidinde → onay sonrası) |
| O-2 | GET login 405 | `scripts/admin_login_probe.py` → POST (GET geri koyma) |
| D-4 | change-password `.strip()` | strip kaldır, login ile tutarlı |

## Teslim
```
python scripts/gorev_kutusu.py teslim --ajan cline --task-id SEC-AUTH-01 --ozet "Asama A/B: ... | test: N passed | kodlama temiz | docker curl OK"
```
Özet biçimi: bulgu → dosya:satır → test adı. Aşama A biterse önce **ara teslim** (`--ozet "ASAMA A tamam, B kilit bekliyor"`) — roo B için ayrı tetik atar.
