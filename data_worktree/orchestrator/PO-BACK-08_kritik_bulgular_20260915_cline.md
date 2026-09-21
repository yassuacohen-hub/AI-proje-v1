[[Huginn Data Insights/data/orchestrator/PO-BACK-08_kritik_bulgular_20260915_cline.md]]

İlgili: [[PROJECT_ROADMAP]]

# PO-BACK-08 — Kapanış Kritik Bulguları (cline → roo)

- **Raporlayan:** cline (iç ajan / işçi) · **Alıcı:** roo (aktif orkestratör — `python scripts/orkestrator_rotasyon.py --kim` → `roo`)
- **Kaynak görev:** PO-BACK-08 — Executive Dashboard v1 (durum: `review`, onay kuyruğunda)
- **Tarih:** 2026-09-15
- **Amaç:** PO-BACK-08 teslimi sırasında karşılaşılan, **görev kapsamı dışındaki** iki kritik kusuru kanıtlarıyla orkestratöre iletmek.
- **Dokunulmayan dosyalar:** Bu raporun konusu olan iki dosyaya **hiçbir yazma yapılmadı** (çakışma/kilit kuralı, AGENTS.md §Çoklu Ajan Koordinasyon Protokolü).

## Özet

| Kod | Öncelik | Dosya | Etki | Sahiplik / durum |
|---|---|---|---|---|
| **KR-1** | P1 | `tests/test_destek.py` | Tam pytest koleksiyonu duruyor → CI yeşil kapısı sahte negatif veriyor | kilo — PO-BACK-06 (`aktif`) |
| **KR-2** | P2 | `src/company_master/ui/charts/__init__.py` | Ortak grafik modülü import edilemiyor → CHART-01 altyapısı fiilen devre dışı | **ÇÖZÜLDÜ** — cline — BUG-CHART01-SYNTAX (`review`) |
| **KR-3** | P3 | `src/company_master/schema/migrations/0006_normalize_compat.py` | UTF-16LE + 1069 NUL, yetim dosya; hiçbir görevin dosya listesinde yok | rapor edildi — BUG-MIG0006-UTF8 (roo, `plan`) |
| **KR-5** | **P1** | `src/company_master/destek.py` | **0 bayt** → `ImportError` → `pytest tests/` koleksiyonu kesiliyor (CI kapısı hâlâ kırık) | rapor edildi — kilo aktif işi PO-BACK-06 (dokunulmadı) |
| **KR-4** | P3 | 85 `.py` dosyası (76'sı git-izlenen) | UTF-8 BOM yaygınlığı; AGENTS.md satır 106/122 ihlali; kök neden PS `Out-File -Encoding utf8` | rapor edildi — öneri: guard + denetim aracı |

---

## KR-1 (P1) — `tests/test_destek.py` bozuk kodlama: tüm pytest koleksiyonunu kilitliyor

**Belirti:** Dosya UTF-16LE + BOM olarak kaydedilmiş; içinde 4319 adet NUL (0x00) baytı var. Python kaynağı olarak okunamıyor.

**Kanıt — bayt düzeyi (komut + çıktı):**

```
python -X utf8 -c "b=open('tests/test_destek.py','rb').read(); print('ilk_baytlar', b[:6]); print('nul_sayisi', b.count(bytes([0]))); print('toplam_bayt', len(b))"

ilk_baytlar b'\xff\xfe#\x00 \x00'
nul_sayisi 4319
toplam_bayt 8744
```

**Kanıt — koleksiyon hatası:**

```
python -m pytest tests/test_destek.py -q

=================================== ERRORS ====================================
____________________ ERROR collecting tests/test_destek.py ____________________
E   SyntaxError: source code string cannot contain null bytes
ERROR tests/test_destek.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.23s
```

**Etki:**

- `pytest tests/` çalıştırıldığında koleksiyon **tamamen kesiliyor** (`Interrupted: 1 error during collection`); diğer testler hiç koşmuyor.
- Bu yüzden PO-BACK-08 tesliminin tam regresyonu ancak `--ignore=tests/test_destek.py` ile alınabildi. Yani **tam regresyon sayısı gerçekte olduğundan "yeşil" görünüyor**; CI kapısı şu an sahte negatif üretiyor.
- `tests/test_destek.py` PO-BACK-06'nın (Destek Merkezi MVP) test dosyası; kapsamı boşta kaldığı sürece o görev de doğrulanamaz.

**Dokunulmama gerekçesi:** Dosya, **kilo'nun aktif görevi PO-BACK-06**'nın `dosyalar` listesinde (`["src/company_master/destek.py", "web_dashboard/tabs/admin_destek.py", "tests/test_destek.py"]`). AGENTS.md: *"Başka bir ajanın aktif işi varsa aynı dosyalara dokunma."* cline dosyayı düzeltmedi, kilidi zorlamadı.

**Öneri (roo triyajı):** PO-BACK-06 sahibi (kilo) dosyayı **UTF-8 / BOM'suz** olarak yeniden yazsın (içerik doğruysa `bytes` → `utf-8-sig` çöz + NUL temizliği ile kurtarılabilir; dosya 8744 bayt, ~4 KB görünür içerik). Doğrulama tek komut:

```
python -m pytest tests/test_destek.py -q
```

Sonrasında tam regresyon `--ignore` olmadan koşmalı ve sayı raporlanmalı.

---

## KR-2 (P2) — `src/company_master/ui/charts/__init__.py`: CHART-01 kalıntısı SyntaxError

**Belirti:** Dosya satır 2'de docstring kaçış karakterleriyle yazılmış (`\"\"\"Charts module for Huginn UI.`), ayrıca dosya **UTF-8 BOM'lu** (`\xef\xbb\xbf`) — AGENTS.md "UTF-8, BOM yok" kuralına da aykırı.

**Kanıt (komut + çıktı):**

```
python -X utf8 -m py_compile src/company_master/ui/charts/__init__.py

  File "src/company_master/ui/charts/__init__.py", line 2
    \"\"\"Charts module for Huginn UI.
     ^
SyntaxError: unexpected character after line continuation character
```

```
python -X utf8 -c "b=open('src/company_master/ui/charts/__init__.py','rb').read(); print('toplam_bayt', len(b)); print(b[:300])"

toplam_bayt 4731
b'\xef\xbb\xbf# -*- coding: utf-8 -*-\r\n\\"\\"\\"Charts module for Huginn UI.\r\n\r\nProvides helper functions to create Plotly charts that can be rendered\r\nin Streamlit or exported as JSON.\r\n\r\nExample:\r\n    from company_master.ui.charts import line_chart\r\n    fig = line_chart(data, x=\'date\', y=\'value\', title=\'Sales T'
```

**Etki:**

- `company_master.ui.charts` modülü **import edilemiyor**; `line_chart`, `bar_chart`, `pie_chart`, `scatter_chart`, `fig_to_json` yardımcılarının tamamı kullanılamaz durumda.
- Yeni sekmeler (örn. PO-BACK-08 Executive Dashboard) bu altyapıyı kullanamıyor; grafik kodunu her modül kendi içinde yazmak zorunda kalıyor (tekrar/kopya grafik kodu riski).

**Uygulanan geçici çözüm (PO-BACK-08 kapsamı içinde):** `web_dashboard/tabs/admin_executive.py` bu modülü **import etmiyor**; grafikleri doğrudan `plotly.graph_objects` ile üretiyor, `plotly` yoksa `st.line_chart` yedeğine düşüyor. Yani PO-BACK-08 çalışır durumda; kırık olan **ortak altyapı**.

**Öneri (roo triyajı):** Ayrı bir düzeltme görevi açılsın (CHART-01 revizyonu). Talimat net: (1) satır 2'deki kaçışlı `\"\"\"` ifadelerini gerçek `"""` yap, (2) dosyayı UTF-8 **BOM'suz** + LF/CRLF tutarlı kaydet, (3) `python -m py_compile` + en az bir import testi (`python -X utf8 -c "from company_master.ui.charts import line_chart"`). Görev cline'a atanırsa düzeltmeyi yaparım.

---

## PO-BACK-08 Teslim Doğrulaması (bu raporun dayanağı)

| Koşu | Komut | Sonuç |
|---|---|---|
| Hedefli | `python -m pytest tests/test_executive_ozet.py tests/test_dashboard_nav.py tests/test_sayfa_iskeleti.py -q` | **186 passed, 1 skipped** (2.72s) |
| Tam regresyon | `python -m pytest tests -q --ignore=tests/test_destek.py` | **3274 passed, 3 skipped**, 126 warnings (75.74s) |

> **Uyarı:** Tam regresyon **KR-1 nedeniyle** `--ignore=tests/test_destek.py` ile koşulmak zorunda kaldı. KR-1 düzeltilince `--ignore` kaldırılmalı ve sayı yeniden alınmalıdır; aksi halde tam regresyon sayısı eksik kapsamı "yeşil" gösterir.

## İstenen Karar (roo)

1. **KR-1 (P1):** Düzeltme, dosya sahibi **kilo'ya PO-BACK-06 kapsamında** verilsin (dosya o aktif görevin `dosyalar` listesinde) veya ayrı bir fix görevi açılsın. cline bu dosyaya dokunmadı, kilidi zorlamadı.
2. **KR-2 (P2):** CHART-01 revizyonu için ayrı görev açılsın. cline'a atanırsa hemen düzeltir; dosya şu an kilitsiz.
3. **PO-BACK-08 onayı:** Teslim bu iki kusurdan **bağımsız doğrulanabilir** (Executive Dashboard ikisini de kullanmıyor). Onaydan önce PO-BACK-08 `not` alanındaki kapanış notunun okunması önerilir.

## İletişim İzi (bu raporun düştüğü yerler)

- **Posta (roo posta kutusu):** `BUG-DESTEK-UTF8` (P1), `BUG-CHART01-SYNTAX` (P2) → `data/orchestrator/triggers/roo.jsonl`
- **Handoff:** `data/orchestrator/handoffs.json` → `PO-BACK-08`
- **Pano notu:** `PO-BACK-08.not` (kapanış notu eklendi, durum `review` korundu)
- **Bu rapor:** `data/orchestrator/PO-BACK-08_kritik_bulgular_20260915_cline.md`
  - Not: `data/orchestrator/` `.gitignore` satır 46 ile dışlanmıştır (çalışma-zamanı artefaktı; `AR-01_*.md` gibi). Bu rapor diskte ve roo tarafından okunabilir; makine-okur durum (`task_board.json`, `handoffs.json`, `AGENT_SYNC.md`) ise takiplidir ve güncellenmiştir.

## Kapsam Beyanı

- cline bu rapor için **yalnızca okuma** yaptı; `tests/test_destek.py` ve `src/company_master/ui/charts/__init__.py` dosyalarına **hiçbir yazma** yapılmadı.
- İki triyaj kaydı panoya eklendi (sahip: roo = aktif orkestratör). Sahip (Ürün Sahibi) talimatı: *"sorunlar/kritikler varsa roo'ya not düş, posta atabilirsin."*
---

## Revizyon — "sıradaki adım" uygulandı (2026-09-15 ~10:17–10:26, aynı oturum)

Ürün Sahibi talimatı üzerine roo triyajı beklenmeden uygulandı. Orijinal bölümler **tarihsel kayıt** olarak korundu; aşağısı güncel durumdur.

| Kod | Öncelik | Dosya | Revize durum |
|---|---|---|---|
| **KR-1** | P1 | `src/company_master/destek.py` (+ `tests/test_destek.py`) | ✅ **Kodlama kusuru giderildi (kilo).** Kök neden atfı düzeltildi (aşağıya bak). Kalan iş fonksiyonel (kilo). |
| **KR-2** | P2 | `src/company_master/ui/charts/__init__.py` | ✅ **Düzeltildi ve teslim edildi (cline)** → `BUG-CHART01-SYNTAX` durum `review`. |
| **KR-3** | P3 | `src/company_master/schema/migrations/0006_normalize_compat.py` | 🔔 **Yeni bulgu:** UTF-16LE + 1069 NUL; **hiçbir görevde tanımlı değil** (orphan). Ticket açıldı → roo. |

### KR-1 revizyonu (kök neden atfı düzeltildi)

- **Doğru kök neden:** koleksiyonu durduran hata `tests/test_destek.py` dosyasından **değil**, onun import ettiği **`src/company_master/destek.py`** dosyasından geliyordu (`from company_master.destek import (...)` → `tests/test_destek.py:11`). Orijinal raporda belirti doğru, **adres yanlıştı** (test dosyası 10:15'te düzeltildiği halde hata sürdüğü için tespit edildi).
- **Kanıt (revizyon anı):**
  ```
  src/company_master/destek.py : 7648 bayt | bom16 True | nul 3814 | compile=HATA: SyntaxError: source code string cannot contain null bytes
  tests/test_destek.py         : 4601 bayt | bom16 False | nul 0 | compile=OK   (mtime 10:15:13)
  ```
- **kilo tarafından giderildi:** `tests/test_destek.py` 10:15:13, `src/company_master/destek.py` 10:20:52 (3936 bayt, 0 NUL). Koleksiyon açıldı: `python -m pytest tests/test_destek.py -q` → **8 passed, 2 failed** (`test_guncelle`, `test_durum_gecis_acik_inceleniyor` — fonksiyonel, PO-BACK-06 kapsamında).
- **Sonuç:** CI'nın sahte-negatif yeşil kapısı kapandı; tam regresyon artık `tests/test_destek.py`'yi de koleksiyona alıyor.

### KR-2 kapanışı (cline)

- `src/company_master/ui/charts/__init__.py` onarıldı: UTF-8 BOM kaldırıldı, kaçışlı `\"\"\"` → gerçek triple-quote, satır aralarındaki çift boşluk temizlendi; **API ve imzalar aynen korundu** (`line_chart`, `bar_chart`, `pie_chart`, `scatter_chart`, `fig_to_json`).
- **İkinci kusur (test sırasında yakalandı):** `fig_to_json` docstring'i "JSON-serializable dict" diyordu ama `fig.to_dict()` numpy `ndarray` döndürüyordu (`json.dumps` → `TypeError: Object of type ndarray is not JSON serializable`). `plotly.io.to_json` + `json.loads` ile sözleşme gerçekten karşılandı.
- **Kalıcı regresyon testi:** `tests/test_ui_charts.py` (9 test) — bu bozulma sınıfını (BOM/NUL/kaçışlı docstring) kalıcı yakalar.
- **Kanıt:** `tests/test_ui_charts.py` **9 passed**; `tests/test_ui_components.py` ile **137 passed**; `tests/ --ignore=tests/test_destek.py` → **3283 passed, 3 skipped** (64.57s; öncesi 3274 → +9 yeni test, regresyon yok).
- **Sağlık/kilit:** 4795 bayt, CRLF, BOM yok, 0 NUL; `file_locks.json` → her iki dosya `cline / BUG-CHART01-SYNTAX`.
- **Kapsam notu:** modülü hiçbir çağıran import etmiyor (`admin_executive.py` raw plotly + `st.line_chart` kullanıyor) → entegrasyon ayrı görev.

### KR-3 (yeni, P3) — orphan ve bozuk migration dosyası

- `src/company_master/schema/migrations/0006_normalize_compat.py`: **2140 bayt, UTF-16LE + BOM, 1069 NUL**, `compile` → `SyntaxError`.
- Repo taramasında `src/`, `tests/`, `web_dashboard/` altında NUL içeren **tek** `.py` dosyası bu (`destek.py` kilo tarafından düzeltildikten sonra).
- Aynı numarayı taşıyan gerçek migration `0006_nace_details.sql` (ok, 623 bayt); bu `.py` dosyası **hiçbir görevin `dosyalar` listesinde yok** ve hiçbir kod onu import etmiyor → yetim artefakt.
- **Kesin teşhis (ek tur):** `data/git_head_0006.py` kopyası bu dosyayla **birebir aynı** baytlar (sha256 `63b42fbad3e11ee4`) → bozulma **git HEAD'e commit edilmiş**, "git'ten geri al" çözüm değil.
- UTF-16'dan çözülünce 23 satır çıkıyor **ama içerik yalnızca kodlama değil yapı olarak da bozuk**: docstring 7. satıra düşmüş, SQL ifadeleri çıplak Python satırı olarak duruyor, `def run():` gövdesinde `conn.execute(...)` `engine.begin()`'den önce geliyor. Yani **tek satırlık literal düzeltmesi veya "decode edip yaz" yeterli değil; dosya onarılamaz.**
- **Öneri:** silinsin (gerçekten bir uyumluluk runner'ı gerekiyorsa sıfırdan yazılsın). Kanıt tam metni `BUG-MIG0006-UTF8.not` alanına yazıldı (çözülen içeriğin ilk 12 satırı dahil). cline dosyaya hiç yazmadı.

---

## İzlenmeyen (un-ignored) Tam Regresyon Ölçümü — KR-1 kapanış revizyonu, 2. tur (2026-09-15 10:47)

**Komut (kanıt dosyası: `data/orchestrator/tam_regresyon_unignored_20260915.txt`):**

```
python -m pytest tests/ -q --continue-on-collection-errors
```

**Sonuç:**

```
ERROR tests/test_destek.py
3283 passed, 3 skipped, 126 warnings, 1 error in 77.51s (0:01:17)
```

- KR-1'in **kodlama** kısmı gerçekten kapandı: `SyntaxError: source code string cannot contain null bytes` **artık yok** (KR-1'de dosyada 4319 NUL vardı).
- Ancak **`--ignore`'suz tam koşu hâlâ kırık**: `--continue-on-collection-errors` bayrağı olmadan pytest `Interrupted: 1 error during collection` ile **tamamen kesiliyor**. Yeni koleksiyon hatası kodlama değil → **KR-5**.
- Bu yüzden "CI yeşil kapısı düzeldi" ifadesi **koşulludur**: kapı ancak KR-5 de kapanınca gerçek olacaktır. Şu an kanıtlanan doğru sayı: **3283 passed, 3 skipped, 1 error (77.51s)**.

## KR-5 (P1, yeni) — `src/company_master/destek.py` 0 bayt: koleksiyon `ImportError` ile kesiliyor

**Belirti:** `src/company_master/destek.py` **0 bayt**; son değişiklik **2026-09-15 10:44:16**, saat 10:49'da hâlâ 0 bayt (≈5 dakika). Git'te **hiç yok** → `?? src/company_master/destek.py`; kurtarılacak commit/sürüm bulunmuyor.

**Kanıt (komut + çıktı):**

```
python -m pytest tests/ -q
...
tests\test_destek.py:11: in <module>
    from company_master.destek import (
E   ImportError: cannot import name 'ticket_olustur' from 'company_master.destek'
ERROR tests/test_destek.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 6.16s

Get-Item src\company_master\destek.py   ->   Length : 0   LastWriteTime : 15.09.2026 10:44:16
```

**Etki:** `pytest tests/` hâlâ kesiliyor; KR-1'deki "sahte negatif yeşil kapı" sorunu "koleksiyon kesintisi"ne dönüştü. Ek olarak `web_dashboard/tabs/admin_destek.py` **diskte yok** (PO-BACK-06 `dosyalar` listesinde var).

**Ek ölçüm (0 baytlık `.py` taraması):** `src/`, `tests/`, `web_dashboard/`, `scripts/` altında **7** adet 0 baytlık `.py` var; bunların **6'sı meşru boş paket işaretçisi** (`src/__init__.py`, `src/company_master/utils/__init__.py`, `src/company_master/etl/scrapers/__init__.py`, `tests/__init__.py`, `tests/company_master/__init__.py`, `tests/data_quality_toolkit/__init__.py`) → **tek anormal olan `src/company_master/destek.py`**. Yani bu bir "yaygın boş dosya" durumu değil, hedefli bir yazım kesintisi.

**Dokunulmama gerekçesi:** Dosya **kilo'nun aktif görevi PO-BACK-06**'nın (`aktif`) dosya listesinde ve `file_locks.json`'da kilitli. AGENTS.md §Çoklu Ajan Koordinasyon: *"Başka bir ajanın aktif işi varsa aynı dosyalara dokunma."* cline bu dosyaya **hiç yazmadı**.

**Öneri (roo triyajı):** (a) kilo'nun yazımı yarıda kaldıysa PO-BACK-06 kapsamında modül yeniden yazılsın (git'te sürüm yok; `data/orchestrator/` ve yedek klasörlerinde kopya olup olmadığı kontrol edilmeli); (b) dosya onarılana kadar tam regresyon **`--continue-on-collection-errors`** ile koşulup sayı raporlanmalı — aksi halde CI sessizce kesiliyor ve yeşil kapı sahte negatif üretmeye devam ediyor.

## KR-4 (P3, hijyen) — Repo genelinde UTF-8 BOM yaygınlığı: 85 `.py` dosyası

**Ölçüm (komut + çıktı):**

```
python -X utf8 -c "import pathlib;fs=[p for d in ('src','tests','web_dashboard','scripts') for p in pathlib.Path(d).rglob('*.py')];print(len(fs), sum(1 for p in fs if p.read_bytes()[:3]==b'\xef\xbb\xbf'))"
685 85
```

- 685 `.py` dosyasının **85'i UTF-8 BOM (`EF BB BF`) ile başlıyor**.
- Dağılım (git eşleştirmesiyle): **76'sı git-izlenen** (yani *komiteli*), **9'u yeni/izlenmeyen**. `HEAD:tests/test_decision_log.py` blob'u da `b'\xef\xbb\xbf# -'` ile başlıyor → BOM yalnızca yeni dosyalarda değil, **git HEAD'de de var**.
- **Ölçüm düzeltmesi (kendi hatam):** ilk taramada "izlenen 0 / yeni 85" çıkmıştı; bu sonuç benim yol kaçışı hatamdan (git forward-slash yolu ile Windows yolunu karşılaştırma) kaynaklanan **sahte negatifti**. `p.as_posix()` ile düzeltilmiş doğru sonuç **76 izlenen / 9 yeni**. Raporun önceki hiçbir sonucu bu düzeltmeden etkilenmez (KR-1/2/3/5 ölçümleri bayt düzeyinde ayrıca doğrulanmıştı).
- **Kök neden (canlı kanıt, bayt düzeyinde doğrulandı):** Bu raporun regresyon çıktısı `... | Out-File -Encoding utf8 data/orchestrator/tam_regresyon_unignored_20260915.txt` ile yazıldı; dosyanın ilk baytları **`b'\xef\xbb\xbf...'` → BOM VARDI** (7424 bayt, 10:48:17). Yani **bu ortamda `Out-File -Encoding utf8` BOM yazıyor**. Ajanların dosya yazımı bu yoldan geçtiğinde BOM oluşuyor; KR-2'nin tetiklendiği mekanizmanın aynısı. (Kanıt dosyası daha sonra **BOM'suz UTF-8'e normalize edildi**: 7424 → 7421 bayt, 0 NUL.)
- **Kontrast kanıtı:** `AGENTS.md` ilk baytları `b'# \xc3\x87al'` → **BOM yok**, Türkçe UTF-8 doğru yazılmış. Yani repo'da kurala uygun dosyalar da mevcut; sorun yazım yolunda.
- **9 izlenmeyen (yeni) BOM'lu dosya tam listesi:** `src/company_master/feature_flags.py`, `src/company_master/tazelik.py`, `src/company_master/odin_ai/__init__.py`, `src/company_master/odin_ai/rag.py`, `src/company_master/scheduler/__init__.py`, `src/company_master/scheduler/scheduler.py`, `tests/test_feature_flags.py`, `tests/test_tazelik.py`, `tests/test_odin_ai.py`. Hepsi son ajan işleriyle oluşmuş yeni dosyalar → **BOM halen aktif olarak üretiliyor** (yalnızca geçmişten kalan bir durum değil).
- **Fonksiyonel risk: düşük** (CPython kaynak dosyada UTF-8 BOM'u kabul eder; import/pytest etkilenmiyor) — ancak **AGENTS.md §Teslim Öncesi Kontrol Listesi satır 106** ("Dosyalar UTF-8, BOM yok, Türkçe karakterler bozulmamış") ve **satır 122** ihlal ediliyor; daha önemlisi BOM'lu yazım, KR-2/KR-5 gibi bozuk-yazım olaylarının **habercisi**.
- **Öneri (roo triyajı):** (1) `scripts/` altına BOM/NUL/0-bayt denetleyen tek komutluk bir araç eklensin; (2) teslim listesine "yeni dosyalarda BOM yok" guard testi eklensin (ratchet yaklaşımı: mevcut 85 dosya allowlist, yeni ihlal kırmızı). cline'a atanırsa uygular.

## Güncel Karar Talepleri (roo)

1. `BUG-CHART01-SYNTAX` (KR-2) → **onay bekliyor** (`onayla --task-id BUG-CHART01-SYNTAX --ben orkestrator`).
2. `BUG-CHART01-SYNTAX` bana devredildi ve uygulandı; gerekçe `not` alanına yazıldı (`devret --neden ...`). Triyaj kaydı: Ürün Sahibi talimatı.
3. `BUG-DESTEK-UTF8` (KR-1) → kodlama kısmı kapandı; kalan iş kilo'nun fonksiyonel düzeltmesi (2 kırmızı test). Kapatma/onay roo'ya ait.
4. `BUG-MIG0006-UTF8` (KR-3) → **öneri: dosya silinsin** (onarılamaz; yapısal bozukluk). Kanıt: git HEAD kopyası da aynı bozuk baytlar (sha256 `63b42fbad3e11ee4`), UTF-16 çözümü 23 satır veriyor ama satırlar karışık (SQL, çıplak Python satırı). Bir compat runner gerçekten gerekiyorsa sıfırdan yazılmalı; cline'a atanırsa hemen yapar (şu an dosyaya dokunulmadı, kilit yok).
5. **KR-5 (P1, yeni)** — `src/company_master/destek.py` **0 bayt** (10:44:16'dan beri) → `pytest tests/` hâlâ koleksiyonda kesiliyor. Dosya **kilo'nun aktif görevi PO-BACK-06**'da ve kilitli; cline dokunmadı. Karar: düzeltme kilo'ya mı bırakılacak, ayrı bir P1 fix görevi mi açılacak? (git'te sürüm yok — yeniden yazım gerekir.)
6. **KR-4 (P3, hijyen)** — repo genelinde 85 BOM'lu `.py` (76'sı git-izlenen, 9'u yeni; kök neden `Out-File -Encoding utf8`). Karar: (a) `scripts/` altına BOM/NUL/0-bayt denetim aracı + (b) teslim listesine "yeni dosyalarda BOM yok" guard testi eklensin mi? cline'a atanırsa uygular (mevcut dosyalara toplu yazma yapmaz — yalnızca yeni ihlalleri engelleyen ratchet).
7. **Ölçüm protokolü önerisi (süreç, P1 etkili)** — Tam regresyon artık **`python -m pytest tests/ -q --continue-on-collection-errors`** ile koşulsun; bu bayrak olmadan **tek bir bozuk modül tüm suite'i kesiyor** ve "yeşil" sayı sahte negatif oluyor. Bu durum KR-1 ve KR-5'te **iki kez** yaşandı (`.github/workflows/ci.yml`'e bayrağın eklenmesi önerilir).

- Hiçbir dosya kilidi alınmadı/yeniden atanmadı; mevcut kilit kümesi değişmedi. Rapor dışında yalnızca **tek kanıt dosyası** üretildi: `data/orchestrator/tam_regresyon_unignored_20260915.txt` (7421 bayt; üretildiğinde BOM'luydu — mekanizmanın canlı kanıtı — ardından BOM'suz UTF-8'e normalize edildi); geçici yardımcı dosya bırakılmadı.