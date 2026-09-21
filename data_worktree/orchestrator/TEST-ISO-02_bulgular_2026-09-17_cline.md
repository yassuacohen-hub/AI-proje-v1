[[Huginn Data Insights/data/orchestrator/TEST-ISO-02_bulgular_2026-09-17_cline.md]]

# TEST-ISO-02 — Tam Süit Regresyonu: Test İzolasyon Sızıntısı (durum raporu, teslim değil)

**ID notu:** Panoda TEST-ISO-01 roo kapanmis farkli gorevi oldugu icin bu rapor TEST-ISO-02 ile acildi.

**Bildiren:** cline · **Tarih:** 2026-09-17 · **Hedef:** roo (orkestratör) · **Tip:** durum raporu + düzeltme (kapsam: test altyapısı)

## 1. Özet
Tam süiti kırmızıya çeken **kök neden bulundu ve düzeltildi**: `tests/test_proje_yonetimi.py` içinde
`monkeypatch` fixture yerine **elle** oluşturuluyordu (`monkeypatch = pytest.MonkeyPatch()`); `undo()`
çağrılmadığı için yamalar süitin geri kalanına **sızıyordu**.

**Sonuç:** tam süit **3567 passed, 4 skipped, 0 failed** (önce: 8 failed).

> **GÜNCELLEME (aynı gün, 2. tur):** Aynı süit koşusunda **3 ayrı test izolasyon sızıntısı** bulundu;
> üçü de kapatıldı. Tam süit yine **3567 passed, 4 skipped, 0 failed** ve pano artefaktlarının
> (AGENT_SYNC.md, gorev_panosu.md, task_board.json, handoffs.json) md5'i koşu öncesi/sonrası **birebir aynı**.
> Ayrıntı: bölüm 7-9.

## 2. Kök Neden (kanıtlı)
- **Suçlu satır:** `tests/test_proje_yonetimi.py` → `test_render_tum_fonksiyonlar_cagiriliyor()` içinde
  `monkeypatch = pytest.MonkeyPatch()` (elle nesne; pytest teardown'ı yok).
- **Etki:** aynı test, 5 sekme modülündeki (`admin_panel`, `abrakadabra`, `admin_audit`, `admin_errors`,
  `admin_dlq`) `render_*` ile başlayan **tüm fonksiyonları kalıcı olarak `MagicMock`**'a çeviriyordu.
- **Belirti:** sonraki `tests/test_web_dashboard_tabs.py` testleri gerçek fonksiyon yerine mock'u çağırıyor,
  gövde hiç çalışmadığı için `st.info` / `st.success` **"Called 0 times"** veriyordu:
  - `test_decision_tab_handles_empty_and_limits_recent_rows` (mock.py:928)
  - `test_dlq_tab_handles_empty_and_populated_data` (mock.py:960)
- **Teşhis kanıtı:** geçici pytest eklentisiyle test anında `render_decision_tab`'ın `MagicMock` olduğu ve
  `AttributeError: __globals__` (mock.py:662) verdiği doğrulandı; `sys.path`'te `...\Huginn Data Insights\src`
  üç kez tekrarlanıyordu.

## 3. Düzeltme (tek dosya)
`tests/test_proje_yonetimi.py`
- `def test_render_tum_fonksiyonlar_cagiriliyor()` → `def test_render_tum_fonksiyonlar_cagiriliyor(monkeypatch)`
- `monkeypatch = pytest.MonkeyPatch()` satırı **silindi** (fixture enjekte edildi → teardown garanti)
- Kullanılmayan `import pytest` kaldırıldı

Etkilenen üretim kodu **yok**; yalnızca test altyapısı. Hiçbir pano kilidi ihlal edilmedi
(`tests/test_proje_yonetimi.py` kilit listelerinde yer almıyor).

## 4. Doğrulama (ölçülen sayılar)
| Deney | Sonuç |
|---|---|
| Eski (sızdıran) dosya + `test_web_dashboard_tabs.py` | **2 failed, 11 passed** (nedensellik kanıtı) |
| Düzeltilmiş dosya + `test_web_dashboard_tabs.py` | **13 passed** |
| Tam süit (`pytest -q`) | **3567 passed, 4 skipped, 0 failed** |
| `python scripts/kodlama_denetim.py` | **EXIT 0**, allowlist dışı ihlal yok |
| `tests/test_proje_yonetimi.py` byte kontrolü | BOM yok, NUL yok, strict UTF-8 decode OK |
| `pytest.MonkeyPatch()` deseni tüm repoda | **0 eşleşme** (başka sızıntı yok) |

## 5. Kapsam Dışı Gözlemler (engel değil)
- İlk koşudaki diğer 6 kırmızı, bu sızıntıyla **ilgisizdi**: `tests/test_i18n.py::test_bekci_13_marka_yazim_hatasi_yok`
  (4 vaka) ve `tests/test_marka_denetim.py` (2 vaka) — **MARKA-REVIZE-01B** (kilo) kapsamındaki marka
  revizyonu tamamlandığı için son koşuda yeşile döndü. Bu dosyalara dokunulmadı.
- Tam süitte kalan tek gürültü: `datetime.utcnow()` DeprecationWarning'ları (126 warning), hata değil.

## 6. Roo'dan İstenen
1. **Regresyon notunu güncelle:** "8 failed" kümesinin 2'si test izolasyon sızıntısıydı ve kapatıldı; 6'sı
   MARKA-REVIZE-01B ile yeşile döndü → **tam süit şu an 0 failed**.
2. **`REV-UI-SIDEBAR-02` (cline, P2, blocked):** blokaj gerekçesi bu süit kırmızıları ise **kaldırılıp
   değerlendirilebilir**; gerekçe başkaysa panoya not düşülmesi.
3. **`MARKA-REVIZE-01` (cline, P2, aktif — doküman katmanı):** yaptığım düzeltmenin bu görevin teslim
   kontrol listesine (test sayısı + UTF-8 temizlik) dahil edilmesi.
4. **Kural önerisi (dikkat notu):** `pytest.MonkeyPatch()` elle oluşturulmaz; her zaman `monkeypatch`
   fixture'ı kullanılır. Gerekçe: elle nesne `undo()` edilmediğinde mock'lar süite sızar ve **yanlış
   pozitif/negatif test sonucu** üretir (bu vakada 2 test sessizce sahte doğrulama yapıyordu).

---

## 7. İkinci sızıntı — `data/orchestrator/gorev_panosu.md` eziliyordu (çift modül kimliği)

**Kanıt:** tam süit öncesi/sonrası md5 `61F15489544E` → `0D5731318A6E`; takipli dosyaya test satırları
(`T-01 test`, `T1-DESTEK-KILO`) düşüyor, dosya ~238 satır kısalıyordu.

**Kök neden iki katmanlı:**

1. **Sabitler import anında donuyor.** `task_board.py` içinde `TASK_MD = STATE_DIR / "gorev_panosu.md"`
   modül yüklenirken hesaplanır. Testte yalnızca `STATE_DIR` yamamak bu sabiti **değiştirmez**.
   Örnek: `tests/test_gorev_kutusu_cli.py` fixture'ı `STATE_DIR`+`TASK_BOARD`+`FILE_LOCKS`+`AUTO_SYNC`
   yamalıyor ama `TASK_MD`'yi yamıyor → `tb.gorev_ekle("T-01", "T-01 test", ...)` gerçek
   `data/orchestrator/gorev_panosu.md` dosyasını yeniden üretiyor.
2. **Testler iki farklı modül kimliği kullanıyor:**
   `company_master.orchestrator.task_board` (`src/` sys.path'te) **ve**
   `src.company_master.orchestrator.task_board` (kökte). İkisi *ayrı* modül nesnesi, dolayısıyla
   sabitleri de ayrı. Yalnızca biri yamalanınca diğeri gerçek dosyayı yazmaya devam ediyor — bu yüzden
   düzeltme ilk turda "yarım kalmış" gibi göründü (AGENT_SYNC.md sabitlenirken `gorev_panosu.md`
   değişmeye devam ediyordu).

**Düzeltme:** `tests/conftest.py` → **tek** autouse fixture `_pano_dosyalari_yalitim`
(TEST-SYNC-01 + TEST-ISO-02 birleştirildi; daha önce eklediğim `_agent_sync_yalitim` mükerrer kalmıştı).
Fixture iki modül kimliğini de bulur ve her ikisinde `AUTO_SYNC=False`,
`AGENT_SYNC_MD` / `AGENT_SYNC_MD_KOPYA` / `TASK_MD` → `tmp_path` yönlendirmesi yapar.

**Kanıt:** sızıntı üreten 8 test modülü + `tests/orchestrator/` birlikte koşuldu → **147 passed**;
4 artefaktın (AGENT_SYNC.md, gorev_panosu.md, task_board.json, file_locks.json) md5'i önce/sonra **aynı**.

## 8. Üçüncü sızıntı — `task_board.json` + `handoffs.json` (P0-2) her koşuda "şimdi"ye çekiliyordu

**Kanıt:** her tam süit koşusunda `handoffs.json["P0-2"]["tarih"]` ve `task_board.json` içindeki P0-2
`bitis` alanı koşu anına ayarlanıyordu (gözlenen seri: `02:44:48` → `02:52:18` → `02:55:07`).

**Kök neden:** `tests/test_post_scrape_workflow.py::test_main_calls_vkn_validation`, üretim script'ini
`post_scrape_workflow.main()` ile çağırıyor. `run_step` mock'lu olsa da script'in sonundaki gerçek pano
bloğu (satır 124-131) çalışıyor:

```python
_tb.gorev_guncelle("P0-2", durum="done", **{"not": "Otomatik tetiklendi"})
_tb.handoff_yaz("P0-2", "Scrape pipeline tamamlandi", "P0-3 kalite kontrol")
```

**Düzeltme:** aynı test dosyasına `izole_pano` autouse fixture'ı eklendi; `STATE_DIR`, `TASK_BOARD`,
`STATE_JSON`, `FILE_LOCKS`, `TASK_MD`, `HANDOFF_FILE`, `AGENT_SYNC_MD`, `AGENT_SYNC_MD_KOPYA` →
`tmp_path`, `AUTO_SYNC=False`.

**Kanıt (tek dosya izole koşu):** `pytest tests/test_post_scrape_workflow.py` → **6 passed**;
`handoffs.json` md5 `ce330869b5` ve `task_board.json` md5 `6281a6b11c` koşu öncesi/sonrası **aynı**,
P0-2 `tarih`/`bitis` alanları değişmedi.

**Kapsam dışı bıraktığım artık (sahibi karar verir):** Bu test geçmişte gerçek panoya yazdığı için P0-2
görevinin `bitis`/`tarih` alanları artık "test zamanı" damgalı. **Panoyu elle düzeltmedim**; çünkü aynı
dosyalarda eşzamanlı **kilo** teslim kayıtları var (NAV-IA-04 → `review`, DATA-LOG-01 → `review`,
MARKA-REVIZE-01B → `review`) ve ajanın canlı yazımını ezme riski doğardı. İstenirse ayrı bir
temizlik görevi olarak açılsın (P0-2 kapanmış eski görev, işlevsel etkisi yok).

## 9. Doğrulama (2. tur ölçümleri)

| Deney | Sonuç |
|---|---|
| Sızıntı üreten 8 modül + `tests/orchestrator/` | **147 passed**; 4 artefakt md5 sabit |
| `tests/test_post_scrape_workflow.py` tek başına | **6 passed**; task_board.json/handoffs.json md5 sabit |
| Tam süit (`pytest -q`), konsolidasyon öncesi | **3567 passed, 4 skipped, 0 failed** |
| Tam süit (`pytest -q`), konsolidasyon sonrası | **3567 passed, 4 skipped, 0 failed** |
| `data/orchestrator/gorev_panosu.md` git durumu | **temiz** (diff yok), içinde test artığı yok (`T-01`/`test brifi` = 0 eşleşme) |
| `data/orchestrator/task_board.json` test artığı taraması | **0 şüpheli kayıt** |
| `python scripts/kodlama_denetim.py` | **EXIT 0**, allowlist dışı ihlal yok |
| Byte kontrolü (`tests/conftest.py`, `tests/test_proje_yonetimi.py`, `tests/test_isbirligi.py`, `tests/test_post_scrape_workflow.py`) | BOM yok, NUL yok, strict UTF-8 OK |

## 10. Roo'dan İstenen (ek maddeler)

5. **`tests/test_post_scrape_workflow.py` (TEST-ISO-02, 3. sızıntı):** bu düzeltmenin panoda kayıt
   altına alınması; aynı dosya geçmişte gerçek panoya yazdığı için P0-2 zaman damgası artığı var.
6. **Sınıf düzeyi kural önerisi (kalıcı koruma):** pano sabitleri (`TASK_BOARD`, `TASK_MD`,
   `HANDOFF_FILE`, `AGENT_SYNC_MD`, ...) import anında donduğu için **testte `STATE_DIR` yamamak
   yetmez**; ilgili sabitlerin kendisi `tmp_path`'e yönlendirilmeli. Ek olarak repoda iki farklı modül
   kimliği (`company_master...` ve `src.company_master...`) yaşadığı için koruma **iki kimliği de**
   kapsamalı. Bu iki kuralı `AGENTS.md` / `docs/AJAN_DETAY.md` test bölümüne eklemek sızıntıyı
   sınıf olarak kapatır (bu vakada 3 ayrı sızıntının 2'si bu iki nedenden çıktı).
