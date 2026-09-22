# SEC-BANDIT-01 — Bandit statik güvenlik taraması + yüksek bulgular (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-01_ortak_kurallar.md`. Zincir halkası 4/6.

## Kapsam
- Yeni: `scripts/sec_bandit.py`, `tests/test_sec_bandit.py`, `.bandit` (yaml config), `docs/SECURITY_BANDIT.md`.
- `requirements-dev.txt`: `bandit>=1.7` (kilit zaten sende — TEST-ISO-02).
- Bulgu düzeltmesi: `src/company_master/**`, `scripts/**` (cline kilitli dosyalar hariç; `web_app.py` ve `app.py` HARİÇ — API-SPLIT-01 sonrası).

## İş
1. `pip install bandit` → `bandit -r src scripts -f json -o data/_tmp/bandit.json -c .bandit`.
2. `.bandit`: `exclude_dirs: [tests, .venv, node_modules, data]`, `skips` yalnız gerekçeli (her skip için yorum).
3. `scripts/sec_bandit.py`: bandit'i çalıştırır, JSON'u özetler (severity × confidence tablosu), `--esik HIGH` ile exit 1. `--json` bayrağı ham çıktıyı basar. Bandit kurulu değilse anlaşılır mesaj + exit 2.
4. **HIGH severity** bulguları düzelt (örn. `subprocess shell=True`, `hashlib.md5` güvenlik amaçlı, `assert` prod kodda, hardcoded tmp). MEDIUM/LOW → rapora tablo, düzeltme YOK (`# nosec` ekleme YASAK, gerekçesiz).
5. Testler: `sec_bandit.py` özetleyici fonksiyonu sahte JSON ile; eşik mantığı; bandit yokken davranış (monkeypatch `shutil.which`).
6. `docs/SECURITY_BANDIT.md`: nasıl çalıştırılır, eşik politikası, skip gerekçe listesi (Türkçe, kısa).

## Teslim kriteri
- `python scripts/sec_bandit.py --esik HIGH` exit 0.
- Tam süit yeşil; kodlama_denetim temiz.
- Rapor: `data/orchestrator/SEC-BANDIT-01_rapor_<tarih>_kilo.md` (önce/sonra bulgu sayıları, düzeltilen dosya:satır).

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]


- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
