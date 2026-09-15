# Çalışma Alanı Kuralları (Kök AGENTS.md)

Bu çalışma alanında birden fazla yapay zeka ajanı paralel çalışabilir
(örn. Kimi Code ve Kilo Code orkestratörü).

## Çoklu Ajan Koordinasyon Protokolü

- **Her işe başlamadan önce ana bağlam dokümanını ve `AGENT_SYNC.md` dosyasını oku.**
  Ana bağlam kaynağı: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- **Başka bir ajanın aktif işi varsa aynı dosyalara dokunma veya kullanıcıyla koordine et.**
- Büyük bir işe başlarken `AGENT_SYNC.md` → "Aktif İşler" bölümüne kaydını ekle.
- İş bitince aktif kaydını kaldırıp "Tamamlananlar" bölümüne özet yaz.
- **Yapılacak iş, ana bağlam dokümanındaki hedef/MVP/teknik sınırlarla uyumlu olmalıdır.**
- **Doküman hiyerarşisi:** `V9` aktif ana bağlamdır; `V8`, `V7`, `V6` ve benzeri sürümler referans devrelerdir. Karar ve iş akışı aktif `V9` kaynak üzerinden yürütülür.
- Kalıcı durum güncellemeleri için tek doğru kaynak:
  - Ana bağlam → `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
  - Görev listesi → `AI proje v1/V10/TODO.md` (görevler)
  - Proje durumu → `AI proje v1/V10/project_state.md` (durum ve kararlar)
  - Değişiklik geçmişi → `AI proje v1/V10/CHANGELOG.md`
- `AI proje v1/` altında çalışırken ayrıca `AI proje v1/AGENTS.md` kuralları geçerlidir
  (açıklamalı ilerleme, tip güvenliği, hardcoded secret yasağı vb.).
- **MVP kuralı:** Veri tabanı, temel temizleme ve iş akışı kanıtlanmadan kullanıcı odaklı web arayüzüne geçilmez. Hızlı iç görünüm için Streamlit gibi sade ara yüz seçilir.

## Görev Panosu ve Dosya Kilidi (Çakışma Önleme) — ZORUNLU

Bu çalışma alanında **canlı görev takibi ve dosya kilidi mekanizması** vardır. Birden fazla ajan aynı anda çalışırken kimin hangi dosyada, hangi görevde olduğunu görmeden dosya değiştirmeyin.

1. **İşe başlamadan önce mevcut durumu kontrol et:**
   - `data/orchestrator/task_board.json` (ham veri) veya `data/orchestrator/gorev_panosu.md` (okunabilir görünüm)
   - `AGENT_SYNC.md` → "Aktif İşler" tablosu
   - `data/orchestrator/file_locks.json` → değiştirmeyi planladığın dosyalar kilitli mi?
2. **Görev al / oluştur:** `src/company_master/orchestrator/task_board.py` içindeki `gorev_ekle(task_id, baslik, sahip, oncelik, dosyalar=[...])` fonksiyonunu kullan. `dosyalar` parametresi verdiğin dosyaları otomatik kilitler; başka bir ajan tarafından kilitliyse `PermissionError` fırlatılır — bu durumda o dosyaya dokunma, görevi farklı kapsamla aç veya kullanıcıya danış.
3. **Durum güncelle:** İş başladığında `gorev_guncelle(task_id, durum="aktif")`, bitince `durum="done"`, engellenince `durum="blocked"` + `not="..."`.
4. **Kilidi bırak:** İş bitince `lock_birak(dosya, sahip)` çağır (kalıcı kilit bırakma).
5. **Aynı dosyada paralel değişiklik yapma.** Kilit yoksa bile `file_locks.json`'u kontrol etmeden büyük/çok dosyalı değişikliğe girme.
6. `AGENT_SYNC.md` **otomatik üretilen bir dosyadır** (`sync.agent_sync_yaz()` / task_board kaynaklı). Elle büyük yeniden yazım yapmayın; yalnızca ilgili fonksiyonlarla güncelleyin veya küçük not eklemek için dosyanın sonuna ekleyin (üstteki tabloyu bozmayın).

## Orkestratör Rotasyonu ve Görev Emri Sözlüğü — ZORUNLU

### Tek Orkestratör Kuralı
- Projede **tek aktif orkestratör** vardır; kim olduğu `data/orchestrator/decision_log.jsonl` içindeki **son `orkestrator_rotasyonu` kaydından** okunur (SSOT).
- Sorgulama: `python scripts/orkestrator_rotasyon.py --kim`
- Orkestratör olmayan ajanlar (işçiler) panoya yalnızca **kendi görevlerinin durumunu** yazar; başkası adına karar kaydı atmaz.

### Rotasyon Ritüeli ("abrakadabra")
- Rotasyon **yalnızca sahibin sözüyle** başlar; ritüel sözcüğü `abrakadabra`'dır.
- Kayıt (tek komut): `python scripts/orkestrator_rotasyon.py <yeni_orkestrator> --kelime abrakadabra --gerekce "..."`
- Script üç iş yapar: (1) sözcüğü doğrular (yanlışsa reddeder), (2) `decision_log.jsonl`'e yapılandırılmış kayıt atar (`kimden`/`kime`/`tetikleyici`), (3) `AI proje v1/V10/CHANGELOG.md`'e insan-okur notu düşer.
- **Rotasyon cümlesi ile görev cümlesi aynı mesajda birleştirilmez** — önce rotasyon, sonra görev emri.

### Görev Emri Sözlüğü
| Sahip cümlesi | Anlamı |
|---|---|
| "X-01'i devret" | Orkestratör görevi subagent'a verir; raporu doğrulayıp kayda yazar |
| "X-01'i kendin yap" | Orkestratör bizzat yapar; subagent başlatmaz |
| "X-01'i hallet" (mod belirtilmezse) | Orkestratör karar verir; karar + gerekçe kayda düşer |

### Kilit Bekleme (Çakışma Önleme)
- Başlatılacak görev başka bir ajanın **kilitli** göreviyse (örn. kilo-D07): **beklenir**; kilit sahibi görevi `done` yapınca ORCH-05 kilidi otomatik düşürür, sonra başlanır. Kilitli dosyaya dokunulmaz.

### Subagent Kuralları
- Subagent **asla orkestratör olamaz**; rotasyon yalnızca sahip ritüeliyle.
- Subagent panoya görev **ekleyemez**, yalnızca rapor yazar.
- Subagent `decision_log.jsonl`'e doğrudan **yazamaz**; kaydı orkestratör atar (`subagent` alanıyla kimliklendirir).

## Görev Tetikleme ve Onay Kuyruğu (ORCH-08) — ZORUNLU

Atama ile başlamayı birbirine bağlayan "posta kutusu" sistemi. Görev panoya yazılınca ajan bunu ancak panoyu elle açarsa görüyordu; artık atama anında ajana **tetik düşer** ve ajan tek komutla postasını okur.

### Akış
1. **Atama**: `python scripts/gorev_at.py at --task-id X --baslik "..." --ajan kilo [--oncelik P1] [--dosya a.py,b.md] [--talimat "..."]` → görev panoya eklenir (dosyalar otomatik kilitlenir) + `data/orchestrator/triggers/kilo.jsonl` postasına tetik düşer.
2. **Ajan oturum başında**: `python scripts/gorev_kutusu.py bak --ajan kilo` → bekleyen görevler + talimat + kilitli dosyalar listelenir. Sonra `--task-id` ile `al` komutu işi `aktif`'e çeker.
3. **Teslim**: `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id X --ozet "..."` → görev **`review`'a düşer; `done` olmaz`**.
4. **Doğrulama zorunluluğu**: Onaysız `done` **geçersizdir**. Kontrolör: `python scripts/gorev_kutusu.py onay-bekleyen` → incele → `onayla --task-id X --ben orkestrator` (görev `done`, ORCH-05 kilitleri düşer) veya `reddet --neden "..."` (görev `aktif`'e döner, ajan düzeltir).
5. **Özet**: `python scripts/gorev_at.py pano` → tüm postalar + onay kuyruğu tek bakışta.

### Kurallar
- Ajan işini bitirince asla doğrudan `gorev_guncelle(durum="done")` çağırmaz; **teslim → onay** kapısından geçer.
- Reddedilen iş nedenle döner; ajan düzeltip yeniden teslim eder (kuyruk yeni kayıt ekler, eski reddedilmiş olarak kalır — denetim izi).
- `review` durumunda kilitler düşmez; yalnızca onayda (`done`) düşer.
- Tetikler ajan bazlı izoledir: kilo postası grok tarafından okunamaz.


### Ajan Başlangıç Protokolü (Otomatik İşi Alma)
- Ajan (Roo, Kilo, Claude vb.) oturum açtığında veya kullanıcı kendisine `"başla"`, `"go"`, `"devam"` gibi tek kelimelik bir tetik verdiğinde **ilk iş olarak**:
  1. `python scripts/gorev_kutusu.py bak --ajan <AJAN_ADI>` komutuyla posta kutusunu kontrol eder.
  2. Bekleyen görev varsa `python scripts/gorev_kutusu.py al --ajan <AJAN_ADI> --task-id <TASK_ID>` ile görevi aktif yapar.
  3. Talimattaki işi tamamlayıp `python scripts/gorev_kutusu.py teslim ...` ile teslim eder.
- Kullanıcının uzun uzun komut yapıştırmasına gerek yoktur; tek kelimelik onay ajanın postasını kontrol edip işe başlaması için yeterlidir.

## Ajan Kılavuzu (Tek Şablon)

1. **Ana bağlamı oku**: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
2. **Koordinasyonu kontrol et**: `AGENT_SYNC.md`, `data/orchestrator/gorev_panosu.md` ve `data/orchestrator/file_locks.json`
3. **Görev ve sınırı doğrula**: `AI proje v1/V10/TODO.md` + `AI proje v1/V10/project_state.md`
4. **Çakışma kontrolü yap**: `task_board.gorev_ekle(..., dosyalar=[...])` ile dosyaları kilitle; aynı dosyada paralel değişiklik yapma
5. **İşe başla**: yalnız hedef, MVP ve teknik sınırlarla uyumlu adım at
6. **Bitince güncelle**: `gorev_guncelle(..., durum="done")`, kilidi bırak, özet yaz, gerekli durum dosyalarını yenile
   - **Zorunlu:** İş bitirince mutlaka `gorev_guncelle(..., durum="done")` çağrılır, `lock_birak(dosya, sahip)` ile kilitlere açılır, `task_board.json` ve `AGENT_SYNC.md` güncellenir. Bu adımlar atlanamaz.
7. **Son kontrol**: hedef/MVP/sınır dışına çıkmadı mı?
8. **Teslim Öncesi Kontrol Listesi (ŞART — eksikse teslim reddedilir):**
   - Brifteki **her madde** karşılandı mı? (yarım iş "tamamlandı" sayılmaz)
   - Yeni/değişen dosyaların hepsi **gerçekten diskte var** (yol yol doğrula)
   - Belge işinde: kaynak + ayna **ikisi de** yazıldı; wikilink/bağlantı hedefleri mevcut
   - Kod işinde: hedefli testler yeşil + tam regresyon çalıştırıldı, sayı özete yazıldı
     - Tam regresyon komutu: `python -m pytest tests/ -q --continue-on-collection-errors` (tek bozuk modül tüm suite'i gizlemesin; koleksiyon hatası sayısı özete yazılır, 0 olmalı)
   - Dosyalar UTF-8, BOM yok, Türkçe karakterler bozulmamış
     - **Yasak:** PowerShell `Out-File -Encoding utf8` / `Set-Content -Encoding utf8` (BOM yazar). Python `open(..., encoding="utf-8")` veya PS 7+ `-Encoding utf8NoBOM` kullan.
     - Teslimden önce dosya boyutu kontrol: 0 bayt dosya ve NUL bayt (UTF-16 belirtisi) teslim edilemez (`python scripts/kodlama_denetim.py` — BUG-ENCODING-GUARD)
   - Kilit alınan dosya dışına dokunulmadı; dokunulduysa özette belirtildi
   - `--ozet` içinde: değişen dosya listesi + test sayısı + eksik/erteleme varsa açıkça yazıldı

## Ajan Rol Profilleri ve Bulgu Notu (2026-09-15, orkestratör kararı)

Gözleme dayalı iş bölümü (cline: KR-1..KR-5 gerçek bulgular; kilo: hacimli üretimde hızlı, kodlama/BOM hatalarına eğilimli):

| Ajan | Birincil rol | Tipik görev |
|---|---|---|
| **kilo** | Üretim / hacimli iş | dosya üretimi, scraper, migrasyon, toplu test yazımı |
| **cline** | Denetim / hata avı | review, refactor, kalite guard'ları, kilo teslimlerinin çapraz incelemesi |
| **roo** | Orkestratör | brif, onay/ret, decision_log, eskalasyon |

Kurallar:
1. **cline briflerine standart "BULGU NOTU" eklenir:** *"Kapsam dışında gördüğün bug/hata/kodlama sorununu DÜZELTME; `data/orchestrator/<TASK_ID>_bulgular_<tarih>_cline.md`'ye yaz ve roo'ya tetik düşür."* Kapsam dışı dosyaya dokunmak teslim reddi sebebidir (kilit disiplini korunur).
2. **kilo teslimleri cline'a çapraz incelemeye gider** (zincir: kilo teslim → cline review → roo onay). Reddedilen iş kilo'ya nedenle döner.
3. kilo teslim öncesi kodlama kontrolü zorunlu (`python scripts/kodlama_denetim.py` hazır olana dek: 0 bayt / BOM / NUL elle doğrulanır).
4. Son söz roo'da kalır; cline bulgusu "öneri"dir, karar ve önceliklendirme decision_log'a yazılır.

## İletişim Dili ve Akıl Yürütme (Demir Kural)

- **Kullanıcı ile İletişim:** Tüm ajanlar, kullanıcı ve Ürün Sahibi ile olan insan iletişiminin tamamını **istisnasız Türkçe** yürütmelidir. Bu kural iç ajandan, dış ajandan ve bu asistan dahil tüm çalışan ajanları kapsar.
- **Akıl Yürütme (Thinking / Reasoning):** Ajanlar düşünce süreçlerini kullanıcının takip edebilmesi için **kısa maddeler halinde ve Türkçe** yürütmelidir.
- **Teknik Katman:** Sistem, yazılım, teknik doküman, API, test çıktısı ve kod örnekleri İngilizce olabilir; ancak kullanıcıya sunulan açıklamalar tamamen Türkçe olmalıdır.
- **Orkestratörün Token Optimizasyonu Sorumluluğu:** Orkestrasyon rolünü üstlenen ajan veya koordinatör, token maliyetlerini optimize etmek için proaktif öneriler sunmak ve somut teknik önlemler (bağlam sıkıştırma, parçalı okuma, kısa brifler) almakla **yükümlüdür**.


## Genel

- Gizli bilgiler (API anahtarı, token, şifre) asla koda veya notlara yazılmaz; `.env` kullanılır.
- Kullanıcının dosyalarını gerekçe açıklamadan silme / üzerine yazma.
- Tüm dosyalar **UTF-8** kodlamasında oluşturulur/kaydedilir. Türkçe karakterlerin (ç, ğ, ı, İ, ö, ş, ü ve büyük halleri) bozulmadığından emin olmadan dosyayı kaydetme (bkz. `Token Verimliliği, Türkçe Dokümantasyon ve Karakter Kodlama Standardı ana kurallara eklenmesi.txt`).

## Proje Sınırı Kuralı (2026-09-15, Ürün Sahibi emri) — ZORUNLU

Projeye ait **her şey** yalnızca `C:\Huginn Data Projesi\Huginn Data Insights` (repo kökü) içinde yaşar. Üst dizin (`C:\Huginn Data Projesi\`) veya başka bir konum ajanlar için **yazma alanı değildir**.

1. **Dışarıya yazma yasağı:** Ajanlar repo kökü dışına dosya/klasör oluşturamaz, taşıyamaz, kopyalayamaz. Mutlak yol kullanan komut/script yazarken hedef daima repo içinde olmalıdır (`Path(__file__).resolve()` ile köke bağla; `..`/üst dizin hedefi yasak).
2. **Geçici dosya konumu:** Tek kullanımlık script/çıktı için `data/_tmp/` veya `_trash/` kullanılır (her ikisi `.gitignore`'da). Repo köküne `_*.py`, `*.bak`, `*.base`, `hello.txt` türü dosya bırakılmaz; kök yalnızca kalıcı proje dosyalarını taşır. İş bitince geçici dosya silinir.
3. **Dışarıda proje öğesi görülürse:** Ajan bunu **siler değil, içeri taşır** — içeriğine göre ilgili bölüme (`docs/po_notlari/`, `data/`, `src/…/i18n/` vb.; belirsizse `data/_arsiv_kok/dis/`) — ve teslim özetinde "dış dizinden taşındı: kaynak → hedef" satırıyla raporlar.
4. **Ürün Sahibi referans/konum dosyası:** Ürün Sahibi, üst dizine veya köke bir not dosyası bırakabilir (ör. `KONUM_NOTU.md` / `.txt`) — içinde "şu dosya şu bölüme gitsin" bilgisi olur. Ajan bu dosyayı okur, talimattaki hedefe taşır, dış kopyayı kaldırır ve decision_log'a kaydeder. Bu dosyalar kural ihlali değil, **taşıma emridir**.
5. **Denetim:** Orkestratör her oturum başında üst dizini kontrol eder (`python scripts/proje_siniri_denetim.py` hazır olana dek elle `dir ..`); `.pytest_cache` gibi araç kalıntıları dışında projeye ait öğe kalmaz.
6. **Ürün Sahibi notu (aynen):** *"Dizinin dışında projeye ait hiçbir şey görmek istemiyorum."*

## Streamlit Yeniden Başlatma Kuralı (2026-09-15, Ürün Sahibi emri) — ZORUNLU

- `.streamlit/config.toml` → `fileWatcherType = "none"`: kod değişikliği **otomatik yüklenmez**.
- UI/dashboard dosyasına (`app.py`, `web_dashboard/**`, `src/company_master/ui/**`, `.streamlit/**`) dokunan her ajan, teslimden önce sunucuyu **kendisi** yeniden başlatır: `python scripts/streamlit_restart.py` (durum: `--durum`, kapat: `--durdur`).
- Ürün Sahibi yalnızca tarayıcıda **F5** çeker; ondan terminal kapatıp açması istenmez.
- Script: portu dinleyen süreci öldürür, `.venv` python'u ile 8501'de yeniden başlatır, `/_stcore/health` "ok" dönene dek bekler; log `logs/streamlit_8501.log`.

## FastAPI (8000) Yeniden Başlatma Kuralı (2026-09-15, roo bulgusu) — ZORUNLU

- 8000 portu **Docker** container'ında (`huginndatainsights-api-1`, `docker-compose.yml` → `api`) dinler; `web_app.py` imaja **kopyalanır**, volume olarak bağlı değildir.
- `scripts/servisleri_baslat.py durdur/baslat --servis web` yalnızca yerel nöbetçiyi (watchdog) yönetir, container'a dokunmaz → yeni endpoint **canlıya çıkmaz** (belirti: `/api/health` ok ama yeni yol 404).
- `web_app.py` veya `src/**` (API tarafı) değişince: `docker compose up -d --build api` çalıştır, ardından yeni endpoint'i `curl` ile doğrula (404 dışı kod bekle).
- Yerel watchdog + Docker aynı anda çalışıyorsa port çakışması riski vardır; teslim özetinde hangisinin hizmet verdiğini yaz.

## VPN Kullanım Kuralı (2026-09-01)

- Kullanıcı VPN kullanmaktadır; gelecekte bazı ağ işlemleri (API istekleri, web scraping, kurumsal erişim) VPN kaynaklı hata verebilir.
- Aşağıdaki durumlarda kullanıcıya açıkça bildir:
  - Ağ isteği timeout / connection / DNS hatası veriyorsa: "Olası neden: VPN. Gerekirse VPN'i kapatıp deneyebilirsin." notu ekle.
  - IP kısıtlamalı bir endpointe erişim engellendiyse: VPN değiştirmeyi veya kapatmayı öner.
  - Erişilen hedef site/API coğrafi kısıtlama gösteriyorsa: VPN'in konumunu değiştirmeyi öner.
- Kullanıcı VPN'i kapatabileceğini onayladı. Şüpheli/güvenilir olmayan durumlarda (özellikle ödeme, kişisel veri, yasal riske girebilecek işlemler) VPN'i kapatmadan önce kullanıcıya sor.
- Kritik güvenlik uyarıları, yasal/yönetmelik riskleri, geri dönüşü olmayan işlemler her zaman NORMAL ve açık dilde yazılır.
- Kural referansı: `V10/09_kurallar_ve_promptlar/10_vpn_kurali.md`

---

## Harici Ajan Entegrasyonu (External Agents)

Bu çalışma alanında iç ajanlara ek olarak dış yapay zeka ajanları (Cursor Grok, GitHub Copilot, Claude Code vb.) da kullanılabilir. Tüm harici ajan etkileşimi **orkestratör üzerinden** ve **yalnızca `workspace/external/{agent_id}/` workspace'i** üzerinden yürütülür.

### Temel Kurallar

- Harici ajanlar proje köküne doğrudan erişemez; yalnız kendi workspace'inde çalışır.
- `.env`, gizli anahtarlar, KVKK kapsamındaki veriler ve üretim şeması harici ajana **gönderilmez**.
- Her görev, orkestratör tarafından hazırlanan **JSON/Markdown brief + bağlam + kısıtlar** paketiyle başlatılır.
- Harici ajan çıktısı güvenilir değildir; orkestratör + kalite ajanı + insan onayı döngüsünden geçmeden ana dala alınmaz.
- Başarısızlık durumunda **maksimum 3 deneme**, sonrasında iç ajanlara reassign yapılır.
- Tüm hatalar `AGENT_SYNC.md` → "ErrorLedger" bölümüne kaydedilir.

### Görev Tipleri (Harici Ajanlara Özel)

1. **Code Review** — mevcut kodları gözden geçirme, iyileştirme önerileri.
2. **Refactoring** — kod optimizasyonu, design pattern uyumu.
3. **Test Üretme** — unit test, integration test senaryoları.
4. **Dokümantasyon** — README, yorum, API dökümanları.
5. **Veri Dönüşümü** — CSV/JSON dönüşümleri, migration helper.
6. **Araştırma** — teknoloji karşılaştırma, benchmark.

### Referanslar

- [[AI proje v1/V10/08-Ajanlar/07_harici_ajan_protokolu]]
- [[AI proje v1/V10/08-Ajanlar/08_harici_ajan_gorev_onerileri]]
- [[AGENT_SYNC]] (External Agent Registry + ErrorLedger)
- Ana bağlam: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`

---

## Versiyon Hiyerarşisi ve Aktif Kaynaklar

### V9 → V10 Yapısı

Bu projede **iki katmanlı versiyonlama** sistemi vardır:

| Katman | Versiyon | Amaç | Konum |
|--------|----------|------|-------|
| **Ana Bağlam** | V9 | Tek tutarlı tasarım ve teknik kararlar | `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` |
| **Yönetim / Organizasyon** | V10 | Görevler, durum, ajanlar, kurallar | `AI proje v1/V10/` dizini |

**Kritik Fark:**
- **V9** = *Ne yapıldığı ve neden* (teknik tasarım, mimari kararlar, veri stratejisi)
- **V10** = *Nasıl yönetildiği* (görev panosu, ajan tanımları, kurallar, şablonlar)

### Kaynak Hiyerarşisi (SSOT — Single Source of Truth)

```
V9 Ana Bağlam (Teknik Kararlar)
├── 01_versiyon_9_baglam_dokumani.md  ← EN ÜST KAYNAK
│
V10 Yönetim Yapısı
├── 05_versiyonlar/                   ← V9 + önceki sürümler (referans)
├── 08-Ajanlar/                       ← Ajan tanımları ve protokoller
│   ├── 01_koordinator_ajan.md
│   ├── 02_mimar_ajan.md
│   ├── 03_arastirmaci_ajan.md
│   ├── 04_gelistirici_ajan.md
│   ├── 05_kalite_ajan.md
│   ├── 06_web_kazima_uzmani.md
│   ├── 07_harici_ajan_protokolu.md   ← YENİ: Harici ajan entegrasyon kuralları
│   ├── 08_harici_ajan_gorev_onerileri.md
│   └── 09_osint_rol_tanimi.md
├── 09_kurallar_ve_promptlar/        ← Ek kurallar
├── TODO.md                          ← Görev listesi
├── project_state.md                 ← Proje durumu
└── CHANGELOG.md                     ← Değişiklik geçmişi
```

### Hiyerarşi Kuralları

1. **Çakışma durumunda V9 zafer kazanır.** V10'daki herhangi bir karar V9 ile çelişiyorsa V9 geçerlidir.
2. **V8, V7, V6 gibi önceki sürümler referans devredir;** karar ve iş akışı aktif V9 kaynak üzerinden yürütülür.
3. **Yeni bir versiyon oluşturulmadan V9 güncellenemez;** büyük tasarım değişiklikleri için V11 taslağı oluşturulur.
4. **Görev atamaları V10'un TODO.md'si üzerinden yapılır;** teknik tasarım V9'a dayanır.
5. **Ajan tanımları V10/08-Ajanlar/ altında tutulur;** her ajan kendi dokümanını taşır.
6. **Harici ajan protokolü** [[07_harici_ajan_protokolu]] dosyasında tanımlıdır; bu dosya harici ajan entegrasyonu için tek kaynaktır.
7. **Orkestratör modülü** `src/company_master/orchestrator/` altında yer alır; detaylı kullanım kılavuzu oradaki README.md'dedir.

### Obsidian Vault Git Takibi (Submodule)

- `AI proje v1/` (Obsidian vault) **pinli submodule** olarak ana repoda takip edilir (bkz. `.gitmodules` → `AI-proje-v1` reposu).
- Ana repo yalnızca gitlink (commit hash) saklar; vault içeriği vault'un kendi reposunda yönetilir.
- Vault içinde değişiklik yapınca sıra: (1) vault reposunda commit + push (`git -C "AI proje v1" push`), (2) ana repoda `git add "AI proje v1"` ile yeni pin işle.
- Vault içindeki `.env` vb. hassas dosyalar vault'un kendi `.gitignore`'unda dışlanır; ana repoya asla girmez.

### Dosya Erişim Matrisi

| Dosya / Dizin | İç Ajan | Harici Ajan | Not |
|---------------|:-------:|:-----------:|-----|
| `AI proje v1/V10/05_versiyonlar/` | ✅ Oku | ❌ Yasak | V9 ana bağlam |
| `AI proje v1/V10/TODO.md` | ✅ Oku/Yaz | ❌ Yasak | Görev listesi |
| `AI proje v1/V10/08-Ajanlar/` | ✅ Oku | ⚠️ Kendi brief'i | Ajan tanımları |
| `data/orchestrator/` | ✅ Oku/Yaz | ❌ Yasak | Görev panosu |
| `src/company_master/orchestrator/` | ✅ Oku/Yaz | ❌ Yasak | Orkestratör kodu |
| `workspace/external/{agent_id}/` | ⚠️ İnceleme | ✅ Oku/Yaz | Harici ajan workspace |
| `.env`, `.env.*` | ❌ Yasak | ❌ Yasak | Gizli anahtarlar |
| `src/company_master/db/` | ⚠️ Yetkili | ❌ Yasak | Veritabanı bağlantısı |
| `src/company_master/schema/` | ⚠️ Yetkili | ❌ Yasak | Üretim şeması |
---

## Marka Terminolojisi

- **Huginn** 🦅: Müşteri yüzeyi (8000) — canlı izleme, "Ne oluyor?" Teknik önek: `huginn_`
- **Muninn** 🛡️: İç ekip yüzeyi (8501) — hafıza, denetim, "Ne oldu, neden?" Teknik önek: `muninn_`
- **Odin** ⚡: Çekirdek/altyapı (görünmez) — karar, yetki, köprü. Teknik önek: `odin_`
- Yazım kuralları: Huginn/Muninn/Odin çevrilmez, kısaltılmaz, ekle bölünmez. Yasak: Muginn, Hugin, Munin, Hugginn, Odın.
- "Tarihsel Çatı Adı" kuralı: `huginn` veritabanı/repo/adı, `HuginnMCPServer`, `admin@huginn.local` gibi teknik kimliklerde değişmez — sıfır migration.
- Detaylar: `ANA_KURALLAR.md` (Marka Adları ve Dil Sözleşmesi bölümü)
