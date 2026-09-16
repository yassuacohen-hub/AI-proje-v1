# REV-BATCH-01 — cline çapraz incelemesi: BATCH-01 (AUTH-GATE-01 + NAV-IA-01 + NAV-IA-02)

**Tarih:** 2026-09-16 · **Kaynak:** `docs/plans/BATCH-01_brief.md`, `docs/plans/NAV-PLAN-01_v4.md` · **Kod:** commit `feea800` (dal `chore/monorepo-merge`, PR #14)

## Kapsam (yalnız oku; dosya değiştirme — kilo BATCH-02 ile aynı dosyalarda çalışıyor)
| Teslim | Dosyalar | Kontrol |
|---|---|---|
| AUTH-GATE-01 | `src/company_master/ui/components/modal.py`, `web_dashboard/tabs/admin_auth.py`, `app.py` (`_auth_modal_icerik`, `main`), `web_app.py` (`/api/admin/login` POST, `reset-request`, `reset-confirm`), `tests/test_auth_gate.py` | modal `dismissible=False`; misafir akışı; reset token süresi/tek kullanım; şifre loglanmıyor; `_env_kimlik` yalnız `DEBUG=1`; GET login geriye dönük |
| NAV-IA-01 | `web_dashboard/tabs/__init__.py` (`TabTanimi.ust/sira`, `ESKI_URL`, `ust_sayfalar/alt_sekmeler/yenile`), `app.py` `render_sidebar`, `tests/test_dashboard_nav.py` | 6 üst sayfa; `kimlik/yonetim/sistem` menüde yok; eski URL yönlendirme; rol filtresi (`ROL_SEVIYE`) alt sekmelerde de uygulanıyor mu |
| NAV-IA-02 | `web_dashboard/tabs/musteri_yonetimi.py`, `web_dashboard/tabs/admin_extras.py` (K-1 tier), `tests/test_musteri_yonetimi.py` | 6 alt sekme; tier JSON'a doğru gidiyor; `Section` deseni; grafik yalnız `charts.py` |

## Ek denetim
- Güvenlik: `web_app.py` yeni endpoint'lerde rate-limit (`_RATE_LIMIT_MAX`) + hata mesajı sızıntısı (kullanıcı var/yok ayrımı yapılmamalı).
- CI: `tests/test_api_integration.py`'de login POST + reset rotalarının kapsanıp kapsanmadığı (roo notu: kilo commit'inde bu testler düşmüş olabilir).
- Mojibake/BOM: `python scripts/kodlama_denetim.py --kapsam git`.
- Kapsam dışı bulgular: `data/orchestrator/REV-BATCH-01_bulgular_2026-09-16_cline.md` (düzeltme YOK).

## Teslim
- Rapor: `data/orchestrator/REV-BATCH-01_rapor_2026-09-16_cline.md` — tablo: `Bulgu | Seviye (YÜKSEK/ORTA/DÜŞÜK) | Dosya:satır | Öneri`.
- `python scripts/gorev_kutusu.py teslim --ajan cline --task-id REV-BATCH-01 --ozet "..." --cikti <rapor>`.
