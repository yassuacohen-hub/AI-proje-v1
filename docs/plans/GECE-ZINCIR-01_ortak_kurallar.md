# GECE-ZINCIR-01 — kilo gece zinciri ortak kuralları (roo, 2026-09-17)

Zincir sırası: **TEST-ISO-02 → VEC-TEST-01 → GUARD-ENC-02 → SEC-BANDIT-01 → FMT-01 → API-SPLIT-01**
Her görev P2 → teslimde oto-nöbetçi onaylar; bir görev teslim edilince sonraki otomatik postaya düşer.

## Süreklilik döngüsü (ZORUNLU)
1. `python scripts/gorev_kutusu.py bak --ajan kilo` → bekleyen görevi **onay istemeden** `al`.
2. Brif: `docs/plans/<TASK-ID>_brief.md`. Brif dışına çıkma; kapsam dışı bulguyu `data/orchestrator/<TASK-ID>_bulgular_<tarih>_kilo.md`'ye yaz.
3. Teslimden önce: tam süit `python -X utf8 -m pytest -q` yeşil (failed=0) + `python scripts/kodlama_denetim.py` temiz. UI dosyasına dokunduysan `python scripts/streamlit_restart.py`.
4. `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."` (özet: test sayısı + değişen dosya listesi + rapor yolu).
5. Teslimden hemen sonra **1. adıma dön**. Posta boşsa 60 sn bekle, tekrar bak; 5 boş turdan sonra dur ve son özeti yaz.

## Sınırlar
- **Commit ATMA** (sabah roo commitler). `git stash/checkout/reset` YASAK.
- Dokunma (cline kilidi): `web_dashboard/tabs/__init__.py`, `tests/test_auth_gate.py`, `.gitignore`, `scripts/admin_login_probe.py`, `docs/brand/**`, `AGENTS.md`, `app.py`.
- Test silme / `skip` ile susturma YASAK. Üretim davranışı değişmez (refactor = aynı çıktı).
- Bir görevde 3 denemede yeşile gelmeyen durum → görevi `bulgular` dosyasıyla teslim et (özete "KISMI" yaz), zinciri bekletme.
- Rapor: `data/orchestrator/<TASK-ID>_rapor_<tarih>_kilo.md` (kısa: yapılan, test sayısı, riskler).
