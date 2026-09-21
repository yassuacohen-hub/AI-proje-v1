[[Huginn Data Insights/data/orchestrator/SEC-AUTH-01_asama_b_rapor_2026-09-17_cline.md]]

# SEC-AUTH-01 — Aşama B Rapor (cline, 2026-09-17)

**Görev:** SEC-AUTH-01 (roo brief, Aşama B) · **Durum:** tamamlandı, review bekliyor
**Önceki teslim:** Aşama A (O-1 ESKI_URL, D-1 secrets.toml, O-2'nin ilk yarısı) — `review` durumundaydı.
**Kilit kontrolü:** NAV-IA-04 `done` → `app.py` + `web_dashboard/tabs/admin_auth.py` kilidi düştü; `tests/test_auth_gate.py` ve `scripts/admin_login_probe.py` (brief'in Aşama B kapsamında) düzenlendi.

## Yapılanlar (brief §Kod, Aşama B)

| Kalem | Dosya | Değişiklik |
|---|---|---|
| Y-1 | `web_app.py` | `_AUTH_RATE_LIMIT` / `_AUTH_RATE_LIMIT_MAX` (env `AUTH_RATE_LIMIT_MAX`, vars. 5/dk) + `_auth_rate_guard()` — genel kovadan **bağımsız** ayrı kova; 4 auth ucuna `Depends(_auth_rate_guard)` bağlandı (login, reset-request, reset-confirm, change-password) |
| Y-2 | `web_app.py` | login: hatalı şifre 401 detayı → `"gecersiz email veya sifre"` (bilinmeyen e-posta ile aynı); reset-request: `404 "admin bulunamadi"` kaldırıldı → her durumda tek tip `{"ok": true, "message": "sifirlama linki gonderildi"}` |
| Y-2 UI | `web_dashboard/tabs/admin_auth.py` | `APIError` → genel mesaj `"Giriş başarısız: e-posta/şifre kontrol ediniz."` (sunucu detayı sızmaz); 401 `.env` ipucu caption'ı korundu |
| D-4 | `web_app.py` | change-password: `old_password`/`new_password` alanlarından `.strip()` kaldırıldı (login ile tutarlı) |
| O-2 | `scripts/admin_login_probe.py` | `requests.get` → `requests.post(json=...)`; "405 beklenir" ikinci sondaj bloğu + not kaldırıldı |
| Y-4 | `app.py` | `aktif_rol()`: `"guest"` (misafir) token'i `ROL_ADMIN` yerine `ROL_ANON`a indirgenir |
| Test | `tests/test_sec_auth_01.py` (**yeni**, 10 test) + `tests/test_api_integration.py` (fixture'a `_AUTH_RATE_LIMIT.clear()`) + `tests/test_admin_auth_login.py` (Y-2 genel mesaj beklentisi güncellendi — test silinmedi) |

## Doğrulama (komut + ham çıktı)

```
python -m pytest tests/test_sec_auth_01.py -q --tb=short
→ 10 passed in 4.90s

python -m pytest tests/test_auth_gate.py tests/test_admin_auth_login.py tests/test_admin_reset.py tests/test_sec_auth_01.py -q
→ 51 passed in 5.19s

python -m pytest tests/test_api_integration.py tests/test_app_nav_tek_tik.py tests/test_dashboard_nav.py tests/test_admin_sistem.py -q
→ 176 passed, 1 skipped in 9.94s

python -X utf8 -m pytest -q   (TAM SÜİT)
→ 3843 passed, 5 skipped, 129 warnings in 237.29s   (0 failed)

python -X utf8 scripts/kodlama_denetim.py
→ temiz: kodlama ihlali yok / allowlist dışı ihlal yok

python -X utf8 scripts/streamlit_restart.py   (UI dosyası dokunuldu → zorunlu)
→ BASLADI: PID 22676 -> http://127.0.0.1:8501 (saglik ok)
```

## Riskler / notlar
- 5/dk limit prod'da agresif olabilir; env `AUTH_RATE_LIMIT_MAX` ile ayarlanabilir (koda sabitlenmedi).
- reset-request artık DB yazım hatasında da 200 döner (Y-2 tek-tip zorunluluğu); kalıcı yazma hatası log'a düşmeli — mevcut kod `except: pass` (Y-2 uyumu için bilinçli).
- Buyer uçları (`/api/buyer/*`) guard kapsamı dışı — brief yalnız 4 admin ucu istedi.
- Y-4 sonrası "Misafir olarak devam et" kullanıcıları `anon` menüyle gezer (daha önce admin menü sızıyordu — bu istenen davranış).

**Test: 3843 passed / 0 failed · Kodlama denetimi: temiz · Streamlit: yeniden başlatıldı (PID 22676)**
