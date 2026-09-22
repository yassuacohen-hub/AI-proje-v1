# PERF-01 — CPU / Beyaz Ekran Optimizasyonu ve Repo Temizliği (2026-09-15)

> Sorun sürerse buradan devam edilir. Karar kaydı: `data/orchestrator/decision_log.jsonl` → `PERF-01` (2026-09-15T10:33:10Z).
> Commit: `320de61` (chore/monorepo-merge, push edildi: `fce69e0..320de61`).

## 1. Yapılan değişiklikler

| Alan | Değişiklik |
|---|---|
| Editör | `.vscode/settings.json` → `files.watcherExclude`, `search.exclude`, `files.exclude`, `python.analysis.exclude` (venv, node_modules, data/*, backups, logs, vault arşivi) |
| Ajan tarama | `.rooignore`, `.clineignore`, `.kilocodeignore`, `.cursorignore`, `.cursorindexingignore` aynı dışlama listesiyle hizalandı (çapraz indexleme yok) |
| Streamlit | `.streamlit/config.toml` → `fileWatcherType = "none"`, `runOnSave = false` |
| Git | `.gitignore` → `.pytest_cache/`, `test_reports/`, `.ruff_cache/` eklendi; BOM temizlendi |
| Silinen (~471 MB) | `V10/`, `_arsiv_kok/`, `test_reports/`, `cop_kutusu_*/`, `tmp/`, `_trash/`, `agent/`, `.playwright-mcp/`, `__pycache__/`, `loglar/`, `AI projet v1/` (yazım hatalı kopya), `data/_tmp/*` |
| Script temizliği | 88 tek-kullanımlık `scripts/_*.py` kaldırıldı (`_debug*`, `_fix_tb*`, `_pano_guncelle*`, `_9r04_*`, `_web_app_duzelt*` …). **Korunan:** `scripts/_kural_testleri.py` (ANA_KURALLAR.md referanslı) |
| Guard ihlali | `scripts/test_import.py` UTF-16 idi → silindi (kodlama guard testi yeşile döndü) |
| Süreçler | Mükerrer sistem-Python kopyaları kapatıldı: PID 7316 (`web_app.py`), PID 12256 (`streamlit run app.py`). `.venv` kopyaları (12820, 39296) korundu |

Doğrulama: `scripts/proje_siniri_denetim.py` → TEMİZ; `tests/orchestrator tests/test_gorev_kutusu_cli.py tests/test_kodlama_denetim.py` → 84 passed.

## 2. Geri alma / kurtarma

- Silinen scriptin içeriği: `git show 320de61~1:scripts/<ad>.py`
- V10 kök yedeği: `backups/V10_root_20260915.zip` (git dışı, yerel)
- Ayar geri alma: `git checkout 320de61~1 -- .vscode/settings.json .streamlit/config.toml`

## 3. Bilinen riskler

- Streamlit dosya izleyici kapalı → kod değişince tarayıcıda **elle Rerun (R)** gerekir.
- `data/_tmp/` artık ajan ignore listesinde; ajanlar oraya `write_to_file` ile yazamaz (cmd/`python -c` ile yazılır).
- Editör arama dışlamaları `data/`, `backups/`, `logs/` içeriğini gizler; oradaki bir dosyayı ararken `search.exclude`'u geçici kapat.

## 4. Kalan manuel adımlar (yapılmadı, bilerek bırakıldı)

| # | Adım | Durum | Not |
|---|---|---|---|
| 1 | Cursor/VS Code yeniden başlat | ⏳ Sahip | Ext host (PID 36788, ~439 MB) ancak yeniden başlatınca boşalır |
| 3 | Eklenti devre dışı | ⏳ Sahip | Önerilen liste: Zencoder, OpenCode, Continue, Kimi×2, CursorCode, Obsidian-md, DataCloud, Jupyter×4, Remote-*, Docker, eski claude-code .269 |
| 4 | 9router heap 6144 → 2048 MB | ⏳ Sahip | Ayar proje içinde değil (harici uygulama, `--max-old-space-size=6144`); 9router'ın kendi ayarından/kısayolundan düşürülür |
| 2 | Mükerrer süreçler | ✅ roo | Bu oturumda kapatıldı |
| 5 | `git push` | ✅ roo | `fce69e0..320de61` |

## 5. Sorun sürerse ilk bakılacaklar

1. `tasklist /FI "IMAGENAME eq python.exe"` → tek `streamlit` ve tek `web_app.py` olmalı, ikisi de `.venv` altından.
2. `powershell "Get-Process | Sort-Object CPU -Descending | Select -First 8 Name,Id,CPU,WS"` → CPU tüketen süreç ext host mu, node (9router) mu, python mu?
3. Beyaz ekran Streamlit'te ise: `fileWatcherType = "none"` nedeniyle eski bundle; tarayıcıda R / sayfa yenile.
4. Beyaz ekran Cursor'da ise: ext host bellek; eklenti listesini uygula, sonra yeniden başlat.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
