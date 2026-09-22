# TEST-ISO-02 — Test İzolasyonu: sıraya bağımlı testlerin tespiti ve düzeltilmesi (kilo)

> Yazan: roo (orkestratör), 2026-09-16. Öncelik: **P2** (oto-onay kapsamında; pano/AGENT_SYNC'te farklı öncelik belirtilmediği için varsayılan).
> Neden `-02`: `TEST-ISO-01` panoda 2026-09-15'te `done` (test_api_integration.py izole DB). Bu görev onun devamıdır; done göreve tetik düşmez (idempotency).
> Sahip ajan: **kilo** · Onay: roo (P2 → oto-nöbetçi onaylayabilir).

## 0. Bağlam (neden şimdi)

- cline ara raporu (`data/orchestrator/SEC-AUTH-01_bulgular_2026-09-16_cline_ara.md`): tam `pytest` koşusunda
  `tests/test_web_dashboard_tabs.python, git, pytest, pippy::test_decision_tab_handles_empty_and_limits_recent_rows` ve
  `test_dlq_tab_handles_empty_and_populated_data` **tam koşuda kırmızı, tek başına yeşil** → sıra/paylaşılan state bağımlılığı şüphesi.
- `tests/test_web_dashboard_tabs.py:30` doğrudan `admin_panel.st.info = MagicMock()` atıyor (monkeypatch YOK) → modül düzeyi kalıcı mutasyon, sonraki testlere sızar.
- `pytest-randomly` / `pytest-xdist` kurulu DEĞİL (`pip show` → not found). Rastgele sıra doğrulaması için kurulum şart.

## 1. Kapsam

| # | İş | Dosya | Not |
|---|---|---|---|
| 1 | `pytest-randomly` dev bağımlılığı | `requirements-dev.txt` | Sürüm sabitle (`pytest-randomly>=3.15`). `pytest.ini`'ye `-p randomly` **ekleme** (varsayılan koşu deterministik kalsın; randomly yalnız CLI ile). |
| 2 | Sıraya bağımlı testleri tespit | `tests/` | `python -X utf8 -m pytest -q -p randomly -p randomly_seed=…` en az 3 farklı seed; ayrıca `pytest tests/test_web_dashboard_tabs.py` tek başına vs tam koşu karşılaştır. Tespit listesi rapora tablo olarak (test → paylaşılan state → kök neden). |
| 3 | `conftest.py` fixture izolasyonu | `tests/conftest.py` | Mevcut `isolated_spend_log` + `_no_real_env_secrets` korunur. Eklenecek: autouse `st.session_state` temizliği (Streamlit modülü import edilebiliyorsa), `tmp_path` tabanlı `data/` yönlendirmesi gerekiyorsa env ile, `sys.modules` cache'e dokunan testler için modül geri yükleme. **Global `monkeypatch` scope'u function kalır.** |
| 4 | Doğrudan modül mutasyonlarını monkeypatch'e çevir | `tests/test_web_dashboard_tabs.py` + tespit edilen diğerleri | `X.attr = MagicMock()` kalıbı → `monkeypatch.setattr(X, "attr", MagicMock())`. Kök nedeni değiştirmeden yalnız izolasyonu düzelt. |
| 5 | Paylaşılan DB/tmp temizliği | tespit edilenler | Test içinde `data/*.db`, `data/orchestrator/*.json` gibi gerçek dosyaya yazan test varsa `tmp_path` + monkeypatch ile izole et. Gerçek pano/kilit dosyalarına (`data/orchestrator/task_board.json`, `file_locks.json`) yazan test **KABUL EDİLMEZ**. |

## 2. Kilit ve sınırlar

- Kilitli (panoda): `tests/conftest.py`, `tests/test_web_dashboard_tabs.py`, `requirements-dev.txt`.
- Tespit sırasında **başka test dosyasına** dokunman gerekirse: önce `python scripts/gorev_kutusu.py bak --ajan kilo` ile kilit durumunu kontrol et. `tests/test_auth_gate.py` (cline, SEC-AUTH-01) ve `tests/test_data_log.py` sahibi değilsen dokunma; bulguyu `data/orchestrator/TEST-ISO-02_bulgular_<tarih>_kilo.md`'ye yaz, roo'ya tetik düş (`python scripts/gorev_kutusu.py` ile `TEST-ISO-02-REQUEST-KILIT` tetiği). `tests/test_i18n.py` + `tests/test_marka_denetim.py` zaten senin (MARKA-REVIZE-01B) kilidinde; iki görevin diff'ini karıştırma.
- Üretim kodu (`src/`, `web_dashboard/`, `web_app.py`, `app.py`) **değişmez**. Üretim koduna dokunmadan izole edilemeyen test → bulgu dosyası, düzeltme YOK.
- Test silme / `skip` ile susturma YASAK. `xfail` yalnız kök neden raporlanmış + roo onaylıysa.

## 3. Teslim kriterleri

1. `python -X utf8 -m pytest -q -p no:randomly` ve `python -X utf8 -m pytest -q -p randomly` (en az 3 seed, seed'ler özette) **aynı passed/failed/skipped sayısını** verir; failed = 0.
2. `tests/test_web_dashboard_tabs.py` iki hedef test tam koşuda yeşil.
3. Test sayısı özette raporlanır: `N passed, M skipped (süre)`; önceki referans: 3073 passed / 3 skipped (TEST-ISO-01 teslimi, 2026-09-15). Sayı düşerse gerekçesi yazılır.
4. `python scripts/kodlama_denetim.py` temiz (BOM/NUL/mojibake/sözdizimi).
5. Rapor: `data/orchestrator/TEST-ISO-02_rapor_<tarih>_kilo.md` → tespit tablosu + her düzeltme için dosya:satır + seed listesi.
6. Teslim yalnız:
   ```
   python scripts/gorev_kutusu.py teslim --ajan kilo --task-id TEST-ISO-02 --ozet "randomly seed a/b/c = no:randomly: N passed M skipped | duzeltilen: dosya:satir ... | kodlama temiz"
   ```
   Doğrudan `done` GEÇERSİZ. Commit ATMA (roo commitler).

## 4. Yapılmayacaklar

- `pytest.ini`'ye `addopts` ile randomly/xdist zorlamak.
- Fixture'ları `session` scope'a taşıyıp izolasyonu gevşetmek.
- Kök neden yerine `time.sleep` / retry ile testi "yeşil"e boyamak.
- MARKA-REVIZE-01B ile aynı diff'te çalışmak (ayrı teslim, ayrı özet).

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]


- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
