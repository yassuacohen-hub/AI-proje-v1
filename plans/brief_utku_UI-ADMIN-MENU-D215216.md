# Brif — UI-ADMIN-MENU-D215216 (utku)

**Başlık:** [UI] Admin menü ağacını düzelt → web_dashboard/tabs/__init__.py (3s)
**Sahip:** utku · **Öncelik:** P2 · **Mod:** code
**Durum:** Geriye dönük kayıt — iş 2026-09-26 oturumunda orkestratör tarafından uygulanıp push edildi.

## Kapsam (D-215 + D-216)

### D-215 — Menü ağacı yeniden düzeni
- `GRUP_GELIR` altında **Gelir Kapısı** kökü kuruldu; `paket_kredi` sekmesi bu köke taşındı.
- `maliyet` sekmesi **Metrikler** köküne alındı.
- **Güvenlik Kapısı** kök seviyeye çıkarıldı.
- `admin_extras` içindeki eski/mükerrer kredi formu silindi.
- Navigasyon testleri güncellendi.

### D-216 — Hayalet görev arşivi
- `scripts/_hayalet_gorev_arsiv.py` yazıldı.
- Kod tabanında karşılığı olmayan 8 kayıt (`UTKU-02`, `UTKU-04`, `UTKU-05`, `ORCH-01..05`) `durum=archive`'e taşındı, gerekçe `not` alanına yazıldı.

## Kabul kriterleri
- `pytest tests/test_dashboard_nav.py` yeşil.
- `pytest tests/test_tabs_ia.py` yeşil.
- `pytest tests/test_naming_audit.py` yeşil (9 passed).

## Teslim izi
- Commit `0601388` — D-215
- Commit `c295166` — D-216
- Branch `chore/monorepo-merge`, push edildi.
- Karar kaydı: `AGENTS.md` D-215 / D-216 maddeleri + `ihsan_project_context.md`.
