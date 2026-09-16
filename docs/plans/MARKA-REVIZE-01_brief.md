# MARKA-REVIZE-01 — Marka Kimliği Revizyon Zinciri (cline → kilo → roo)

> Yazan: roo (orkestratör), 2026-09-16. Karar dayanağı: D-44, D-45 (decision_log).
> Sahip emri: "marka kimliği ile ilgili sistemdeki eski tüm ilgili dosyalara bakıp içeriği güncelleyelim; her ajan sırayla katkı sağlasın."

## 0. Kararlar (tartışmasız, uygulanır)

| # | Karar | Kaynak |
|---|---|---|
| 1 | Tek yazım: **Huginn / Muninn / Odin**. Yasak: Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın | D-44 §1 |
| 2 | Tipografi: Inter birincil, Geist yedek, sayılar `tabular-nums` | D-44 §2 |
| 3 | Renk rolleri: dark=#09111F zemin, gray900=#0F172A yüzey, darkSecondary=#131C2F yükseltilmiş | D-44 §3 |
| 4 | Kuş/kuzgun görsel yasağı: logo + pazarlama. İç doküman emoji (🦅🛡️⚡) serbest. Müşteri UI'da mitolojik dil yasağı sürer | D-44 §4 |
| 5 | **İki palet, iki kapsam:** `docs/brand/design-tokens.json` = pazarlama/web/logo SSOT; `src/company_master/ui/tokens.py` = ürün UI SSOT (Indigo #6366f1, değişmez). Birleştirme YOK | D-45 |
| 6 | `.streamlit/config.toml` `primaryColor` Streamlit kırmızısından (#FF4B4B) ürün paletine (#6366f1) hizalanır | D-45 |
| 7 | Teknik SSOT `docs/AJAN_DETAY.md §11`; marka kiti onu **tamamlar**, çelişirse §11 kazanır | AGENTS.md |

## 1. Envanter (dokunulacak dosyalar)

| Dosya | Katman | Sorumlu | Ne yapılacak |
|---|---|---|---|
| `AGENTS.md` 39-43 "Marka Terminolojisi (öz)" | doküman | cline | `docs/brand/` köprü satırı (1 satır, çekirdek şişmesin) |
| `ANA_KURALLAR.md` 80-82 | doküman | cline | Aynı köprü; yasak listesine Huggin/Hugginn |
| `docs/AJAN_DETAY.md` §11 (101-121) | doküman | cline | "Marka kiti: `docs/brand/`, D-44/D-45 kapsam ayrımı" alt bölümü; yasak listesine Huggin |
| `plans/MRK_marka_ve_dil_paketi_plani.md` 143-144, 237-239 | doküman | cline | Bayat "kök dizindeki kit" ifadeleri → `docs/brand/` |
| `plans/brief_cline_MRK02fg.md`, `plans/brief_kilo_MRK03_MRK04.md` | doküman | cline | Başa "ARŞİV — tamamlandı, güncel: docs/brand/" notu (içerik silinmez) |
| `plans/muninn_prn_vs_huginn_analiz.md` | doküman | cline | Yazım denetimi (Huggin var mı), kit köprüsü |
| `docs/brand/prompts/*.md`, `personas/*.md`, `assets/LOGO.md` | doküman | cline | "kok dizindeki ai-rules.md" → "`docs/brand/ai-rules.md`" (13 yer) |
| `docs/brand/company.md`, `ai-rules.md` | doküman | cline | D-45 kapsam notu (pazarlama vs ürün UI); yazım listesi |
| `tests/test_i18n.py:29` `HATALI_YAZIM` | kod | kilo | `Huggin\b`, `Odın` ekle; tarama kapsamına `docs/brand/**/*.md` ekle; testin ilk çalışmada yeşil olması şart |
| `.streamlit/config.toml` `[theme]`/`[theme.dark]`/`[theme.light]` | kod | kilo | `primaryColor="#6366f1"` (tokens.py ile aynı); font Inter kalır |
| `src/company_master/ui/tokens.py` | kod | kilo | **Değişmez.** Yalnız modül docstring'ine D-45 kapsam notu (2 satır) |
| `scripts/marka_denetim.py` (YENİ) | kod | kilo | Repo genelinde yasak yazım + "kök dizindeki kit" bayat ifade taraması; `--fix` yok, sadece rapor; `kodlama_denetim.py` kalıbı; birim testi `tests/test_marka_denetim.py` |
| `AGENTS.md` sözlük | doküman | roo | Son onayda: D-29/D-30 kural satırı + sözlük |

## 2. Sıra ve teslim

1. **cline (doküman katmanı)** — yukarıdaki doküman satırları. Kilit: `AGENTS.md`, `ANA_KURALLAR.md`, `docs/AJAN_DETAY.md`, `plans/MRK_*.md`, `docs/brand/**`. Teslim: `gorev_kutusu.py teslim --ajan cline --task-id MARKA-REVIZE-01`; rapor `data/orchestrator/MARKA-REVIZE-01_rapor_<tarih>_cline.md`. Kapsam dışı bulgu → `_bulgular_` dosyası, düzeltme YOK.
2. **kilo (kod katmanı)** — zincir otomatik tetikler. Kilit: `tests/test_i18n.py`, `.streamlit/config.toml`, `scripts/marka_denetim.py`, `tests/test_marka_denetim.py`. UI dosyasına (`config.toml`) dokunduğu için teslimden önce `python scripts/streamlit_restart.py`. Teslim aynı kalıp.
3. **roo** — onay, AGENTS.md sözlük, commit, push.

## 3. Kabul kriterleri

- `findstr /s /i /n "Huggin" AGENTS.md ANA_KURALLAR.md docs\*.md docs\brand\*.md plans\*.md` → 0 satır (Hugginn dahil; yalnız yasak listesi satırları muaf).
- `findstr /s /i "kok dizin" docs\brand` → 0 satır.
- `pytest tests/test_i18n.py tests/test_marka_denetim.py -q` yeşil; `python scripts/marka_denetim.py` → temiz.
- `python scripts/kodlama_denetim.py` temiz (BOM/mojibake yok).
- `config.toml` primaryColor üç temada da `#6366f1`.
- `tokens.py` diff'i yalnız docstring (git diff ile doğrulanır).
- Rapor "Dikkat (eleştirel notlar)" bölümü → aynı turda `ROO_ELESTIRI_NOTLARI.md` Bölüm 7'ye D- satırı.

## 4. Yapılmayacaklar

- `tokens.py` renk değeri değiştirme; kit rengini dashboard'a taşıma.
- `docs/brand/` yapısını değiştirme, dosya silme/yeniden adlandırma.
- Marka adını çevirme/bölme (`Huginn Data Insights` teknik kimlik değişmez).
- Copilot'a iş verme (sahip emri: devre dışı).
