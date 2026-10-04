# TEST-SIMULASYON-B17-KIRIK-01 — Teslim Raporu

**Tarih:** 2026-10-03 · **Ajan:** Üretim/Hacim UTKU · **Öncelik:** P1

## Ne yapıldı

`tests/test_gorev_kutusu_cli.py::test_cmd_teslim_basarili` kırıktı. Ölçüldü ve
düzeltildi; düzeltme sırasında **ikinci bir hata** bulundu ve o da kapatıldı.

| # | Kusur | Kök neden | Sonuç |
|---|---|---|---|
| 1 | `test_cmd_teslim_basarili` kırmızı | D-318 kapısı teslimden önce bulgu defteri kaydı istiyor; test bulgu yazmadan `cmd_teslim` çağırıyor | `gk.bulgu.task_var_mi → True` monkeypatch |
| 2 | `test_cmd_teslim_hata` **yanlış sebeple yeşildi** | D-318 kapısı `rc=1` döndüğü için test geçiyor; **çift teslim reddi hiç denenmiyordu** | Aynı monkeypatch + kapı ayrıca ölçülüyor |
| 3 | Kapının kendisi ölçülmüyordu | Kapıyı atlama kırmızıyı düzeltirken kapıyı da sessizce kapatabilirdi | `test_cmd_teslim_bulgu_kapisi_reddeder` eklendi |

Kusur 2 asıl bulgudur: test yeşildi ama **hiçbir şey ölçmüyordu**. Bu, D-309/3 ve
D-265/2'nin aynı deseni — yeşil test, ölçülen şey değil.

Kapı atlatması yalnız monkeypatch ile yapıldı; `test_cmd_teslim_bulgu_kapisi_reddeder`
atlatmasız çalışır ve bulgu yoksa `rc=1` bekler. Kapı kırılırsa iki test kırmızı yanar.

## Değişen dosyalar

- `tests/test_gorev_kutusu_cli.py` — `_bulgu_kapisi_ac()` yardımcısı; 2 test düzeltildi,
  1 yeni kapı testi eklendi (17 → 18 test).
- `data/orchestrator/bulgu_defteri.md` — 2 kayıt.
- `utku_project_context.md` — KALDIĞIM YER güncellendi.

## Test sonuçları

| Komut | Önce | Sonra |
|---|---|---|
| `pytest tests/test_gorev_kutusu_cli.py -q` | 1 failed, 16 passed | **18 passed** |
| `pytest tests/test_gorev_kutusu_cli.py tests/test_gorev_kutusu_simulasyon.py -q` | — | **22 passed** |
| `kodlama_denetim.py --kapsam kod` | — | dosyam ihlalsiz |

Simülasyon kapısı `gorev_kutusu.py simulasyon` → **çıkış 1 (uyarı)**: 37 görevde hafıza
izi yok. Çıkış 2 (hata) değil; D-198 tablosuna göre tur başlayabilir, uyarılar
kronik borçtur ve görev brifinde kapsam dışı sayıldı.

## Bulgular

- 🟡 **Kilitli olmayan dosyada aynı kök neden (2 test).** `tests/test_gorev_kutusu_hafiza.py`
  → `test_hub_izi_varsa_teslim_gecer` ve `test_zorla_geercer_panoya_atlandi_islenir`
  de D-318 kapısında kırmızı. Dosya UTKU'da kilitli **değil**; D-58/D-77 gereği
  dokunulmadı. → `TEST-GOREV-KUTUSU-HAFIZA-D318-01` görevi açılmalı.
- 🔵 **Bu turun kendi hatası.** `ajan_chat.py bulgula` komutunu "ara" sandım; komut
  *eleştiri kaydeder*. `{"konu": "SCRAPE-005", "bulgu": "bulgu 105-108"}` çöp
  girdisi yazdı, sonra `ajan-chat-bulgular.jsonl`'den kendi satırımı sildim.

## Eksik / erteleme

- `test_gorev_kutusu_hafiza.py` bilerek dokunulmadı (başka ajanın alanı).
- Tam süit çalıştırılmadı; kapsam iki kilitli test dosyasıyla sınırlı.
- 37 görevin hafıza izi yok — kronik, bu görevle ilgisi yok.

## İlgili Nodlar

- [[Huginn Data Insights/tests/test_gorev_kutusu_cli]]
- [[Huginn Data Insights/scripts/gorev_kutusu]]
- [[Huginn Data Insights/data/orchestrator/bulgu_defteri]]
