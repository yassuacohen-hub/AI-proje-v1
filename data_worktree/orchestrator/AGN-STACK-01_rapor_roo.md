# AGN-STACK-01 — crewAI / LangChain vs Huginn Orkestratörü Kıyas Raporu

- **Ajan:** roo
- **Tarih:** 2026-09-18
- **Emir:** KAHİN (Ürün Sahibi)
- **Kısıtlar:** `requirements.txt`'ye ekleme YOK · 9Router + `docs/brand` dokunulmadı · commit YOK
- **Sonuç (tek cümle):** **Entegrasyon YOK** önerilir; tek istisna küçük, geri döndürülebilir bir "hibrit worker" pilotu.

---

## 1. crewAI v1.15.22 — Yetenek Özeti

Ortamda kurulu (cline kurmuş, `requirements.txt` dışında): `crewai 1.15.22`, `langchain_openai 1.6.2`.

| Kavram | Ne yapar | Huginn'deki karşılığı |
|---|---|---|
| `Agent` | rol + hedef + backstory ile LLM persona | `AGENTS.md` rol profilleri (kilo/cline/roo) |
| `Task` | tek iş tanımı + beklenen çıktı | `docs/plans/*_brief.md` + pano kaydı |
| `Crew` | ajan+görev topluluğu, tek `kickoff()` | `gorev_kutusu.py` + `trigger.py` akışı |
| `Process.sequential` | görevleri sırayla çalıştırır | `gorev_zinciri()` / `zincir_devam_et()` |
| `Process.hierarchical` | LLM "manager" görevleri dağıtır | **roo (insan+LLM orkestratör)** |
| `memory` | kısa/uzun vadeli hafıza (vektör DB) | `handoff.jsonl`, `decision_log.jsonl`, brief |
| `tools` | fonksiyon çağrısı araçları | Roo/Cline/Kilo'nun kendi araç seti |
| `human_input=True` | görev sonunda insan onayı | `review` → `onayla --ben roo` (ORCH-08) |
| `Flow` | deterministik, olay tabanlı akış | `runner.py` + `nobetci.py` |

**Kritik gözlem:** crewAI'nin sattığı ana değer *LLM'lerin birbirine görev dağıtması*. Huginn'de görev dağıtımı **deterministik CLI + JSON pano**. Bunlar aynı problemi çözmez; crewAI non-determinizmi *içeri* sokar.

---

## 2. Kıyas Tablosu

Mevcut Huginn orkestratörü ölçüldü: `src/company_master/orchestrator/` → **17 modül / ~2.877 satır Python**.

| Boyut | Huginn (mevcut) | crewAI 1.15.22 | Kazanan |
|---|---|---|---|
| **Görev dağıtımı** | Deterministik: `tetik_ekle` → `al` → `teslim`. Aynı girdi = aynı çıktı. | LLM manager karar verir; her koşu farklı olabilir. | **Huginn** |
| **Denetim / onay** | Zorunlu insan kapısı: `review` → `onayla --ben roo`. P0/P1 elle (S-07). Reddetme + geri dönüş var. | `human_input=True` var ama akış içi, kalıcı kuyruk yok. Ret sonrası durum yönetimi zayıf. | **Huginn** |
| **Kalıcılık** | JSON/JSONL SSOT: `task_board.json` (4.400 satır), `triggers/*.jsonl`, `handoff.jsonl`, `decision_log.jsonl`. Atomik yazma (`atomic_write_text`) + süreç kilidi (`_pano_kilit`). Git'te izlenebilir, diff'lenebilir. | Varsayılan hafıza = ChromaDB/SQLite; insan okuyamaz, git diff'i anlamsız. | **Huginn** |
| **Gözlemlenebilirlik** | Her şey düz metin. `bak`, `pano`, `ozet`, `health_check.py`, Telegram botu. KAHİN telefondan görebiliyor. | Verbose log + opsiyonel AgentOps/Langfuse (yeni SaaS bağımlılığı, ücretli). | **Huginn** |
| **Maliyet / token** | Orkestrasyon **0 token** — Python çalışıyor. Token yalnız gerçek iş için. | Manager ajan her dağıtım kararında LLM çağırır. Hiyerarşik modda tipik **%40-120 ek token**. D-48 hedefi "maliyet avantajı" ile ters. | **Huginn** |
| **Hata kurtarma** | `error_ledger.py`, retry istatistikleri, `bakim` (stale temizliği), `tetik_uyari_ekle` (5× uyarı), `devret`. Kısmi başarı diskte kalıcı. | `max_retries` + exception. Crew ortasında çökerse ara çıktılar kaybolabilir. | **Huginn** |
| **Öğrenme eğrisi** | Ekip (3 ajan + KAHİN) zaten biliyor. Kurallar `AGENTS.md`'de yazılı. | Yeni kavram seti, yeni hata modları, sürüm kırılganlığı (v0→v1 breaking change geçmişi). | **Huginn** |
| **Çok-ajan paralelliği** | Dosya kilidi ile çakışma engelleniyor; gerçek paralellik VS Code örnekleri kadar. | `async_execution` ile görev paralelliği yerleşik. | **crewAI** |
| **Hazır araç ekosistemi** | Elle yazılıyor. | `crewai-tools` (RAG, scrape, dosya, SQL) hazır. | **crewAI** |

**Skor: Huginn 7 / crewAI 2.**

---

## 3. Ponytail / YAGNI Çerçevesi

Merdiven (ilk tutan basamakta dur):

1. **Buna gerek var mı?** — Mevcut orkestratör çalışıyor: 200+ görev done, zincir, onay, kilit, Telegram. Çözülmemiş bir problem yok. → **Merdiven burada duruyor.**
2. **Stdlib yeter mi?** — Zaten `json` + `pathlib` + `argparse` ile çözülmüş.
3. **Kurulu bağımlılık yeter mi?** — Evet, kendi paketimiz.
4. **Yeni bağımlılık?** — crewAI ağır transitive ağaç getirir (litellm, chromadb, embedchain...). `requirements.txt` kısıtı zaten yasaklıyor.

**Karşı argüman (dürüstçe):** crewAI'nin `async_execution` ve hazır araçları gerçek bir kazanç. Ama ikisi de bugün darboğaz değil. Darboğaz **kilo'nun tetikleri almaması** — bu bir framework sorunu değil, süreç sorunu. crewAI bunu çözmez.

**Değiştirme maliyeti:** 2.877 satır test edilmiş kodun yerine yeni bir soyutlama koymak = yeniden yazım + tüm testlerin çöpe gitmesi + KAHİN'in alışık olduğu `bak`/`pano`/Telegram arayüzünün kaybı.

---

## 4. Üç Senaryo + Maliyet / Token Etkisi

### Senaryo A — Entegrasyon YOK (önerilen)

| Kalem | Değer |
|---|---|
| Geliştirme maliyeti | 0 |
| Token etkisi | 0 (değişim yok) |
| Risk | Yok |
| Kayıp | `async_execution` ve hazır araçlardan feragat |

**Aksiyon:** `crewai` + `langchain_openai` paketlerini `requirements.txt`'ye **ekleme**. Kurulu kalsın, deney için kullanılabilir; üretim yolunda değil.

### Senaryo B — Hibrit Worker (pilot değeri var)

crewAI **yalnız tek bir görevin içinde** alt adımları koşturur. Pano, tetik, onay, kilit, karar defteri **Huginn'de kalır**. crewAI dışarıdan görülmez — `al` ve `teslim` arasındaki kutunun içi.

| Kalem | Değer |
|---|---|
| Geliştirme maliyeti | ~150-250 satır adaptör + testler |
| Token etkisi | Görev başına **+%30-60** (alt-ajan konuşmaları) |
| Risk | Orta — non-determinizm tek görev içine hapsedilmiş |
| Kazanç | Paralel alt-görev; araştırma/özetleme gibi "dağıt-topla" işlerde hız |

**Uygunluk:** Yalnız *çıktısı metin olan, kod yazmayan* görevler (pazar araştırması, doküman özeti, çoklu kaynak tarama). Kod yazan görevlerde **kullanılmamalı** — kalite denetimi zayıflar.

### Senaryo C — Tam Geçiş (reddedildi)

| Kalem | Değer |
|---|---|
| Geliştirme maliyeti | 2-4 hafta tam zaman + regresyon |
| Token etkisi | **+%40-120** kalıcı (manager ajan her turda çalışır) |
| Risk | **Yüksek** — denetlenebilirlik, git-izlenebilirlik, Telegram kontrolü kaybı |
| Kazanç | Yok denecek kadar az |

**Karar: REDDEDİLDİ.** D-48 demir kuralının "maliyet avantajı" ayağıyla doğrudan çelişiyor.

---

## 5. Pilot Önerisi (küçük, geri döndürülebilir)

**Ad:** `AGN-CREWAI-PILOT-01` (henüz açılmadı — KAHİN onayı bekler)

**Kapsam:**
- Tek dosya: `scripts/deney/crewai_arastirma_deneyi.py` (üretim yolunda değil, `scripts/deney/` yeni dizin)
- Tek iş: verilen bir konuda 3 alt-ajan (arayıcı / okuyucu / özetleyici) sıralı çalışsın, çıktı `data/_tmp/` altına markdown.
- `requirements.txt` **değişmez**; script başında `try: import crewai / except ImportError: "kurulu değil, atlanıyor"`.
- Pano/tetik/onay akışına **hiç dokunulmaz**.

**Kabul kriterleri:**

| # | Kriter | Eşik |
|---|---|---|
| 1 | Çıktı kalitesi | Mevcut tek-ajan çıktısıyla en az eşdeğer (KAHİN gözüyle) |
| 2 | Token maliyeti | Tek-ajan yoluna göre **en fazla +%50** |
| 3 | Süre | Tek-ajan yoluna göre **en fazla 2×** |
| 4 | Determinizm | 3 koşuda çıktı yapısı (başlıklar) aynı kalmalı |
| 5 | Geri alma | Tek dosya silinince sistem etkilenmemeli (kanıt: tam test süiti yeşil) |

**Başarısızlık eşiği:** 5 kriterden 2'si düşerse pilot kapanır, `scripts/deney/` silinir, karar defterine "denendi, tutmadı" yazılır.

**Zaman kutusu:** 1 oturum. Uzarsa iptal.

---

## 6. Bulgu — Pano/Tetik Tutarsızlığı (kapsam dışı, kayıt için)

Bu görevi alırken çıktı: `AGN-STACK-01` tetiği `data/orchestrator/triggers/roo.jsonl`'de vardı ama `task_board.json`'da kayıt **yoktu**.

```
HATA: Görev panoda bulunamadı: AGN-STACK-01
```

- `al --zorla` tetik kontrolünü atlıyor ama **pano kaydı yaratmıyor** → görev alınamıyor.
- Geçici çözüm: elle `tb.gorev_ekle(...)` + `al --zorla`.
- **Kök neden adayı:** `tetik_ekle()` pano kaydının varlığını doğrulamıyor.
- **Öneri:** `tetik_ekle()` başında `tb.gorev_getir(task_id)` kontrolü; yoksa ya otomatik `gorev_ekle` ya da net hata. D-1/D-3 (ADMIN-ROO-DENETIM-01) ile aynı aile.
- Ayrı görev önerisi: `ORCH-TETIK-PANO-01`.

---

## 7. Nihai Tavsiye

| Soru | Cevap |
|---|---|
| crewAI'ye geçelim mi? | **Hayır.** |
| `requirements.txt`'ye ekleyelim mi? | **Hayır.** |
| Hiç mi kullanmayalım? | Tek metin-üretimi görevinde pilot denenebilir (Senaryo B), pano dışında. |
| Mevcut orkestratöre ne yapalım? | Framework değil, **süreç** düzelt: kilo'nun tetik almama sorunu + pano/tetik tutarsızlığı (D-1, D-3, bu raporun §6). |

**Gerekçe özeti:** Orkestrasyon katmanımız 0 token harcıyor, deterministik, git'te izlenebilir ve KAHİN telefondan kontrol edebiliyor. crewAI bunların dördünü de zayıflatır, karşılığında bugün ihtiyacımız olmayan paralellik verir. YAGNI merdiveni 1. basamakta duruyor.
