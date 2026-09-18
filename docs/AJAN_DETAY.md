# Ajan Detay Dokümanı (TOK-01 — AGENTS.md'den taşınan ayrıntılar)

> Bu dosya `AGENTS.md` çekirdeğinin ayrıntı deposudur (TOK-01, D-37). İçerikte
> kural kaybı yoktur; her bölüm AGENTS.md'den buraya taşınmıştır. Çakışma
> durumunda AGENTS.md çekirdeği geçerlidir.

## 1. Rotasyon Ritüeli ("abrakadabra")
- Rotasyon **yalnızca KAHİN'in (Ürün Sahibi) sözüyle** başlar; ritüel sözcüğü `abrakadabra`'dır.
- Kayıt (tek komut): `python scripts/orkestrator_rotasyon.py <yeni_orkestrator> --kelime abrakadabra --gerekce "..."`
- Script üç iş yapar: (1) sözcüğü doğrular (yanlışsa reddeder), (2) `decision_log.jsonl`'e yapılandırılmış kayıt atar (`kimden`/`kime`/`tetikleyici`), (3) `AI proje v1/V10/CHANGELOG.md`'e insan-okur notu düşer.
- **Rotasyon cümlesi ile görev cümlesi aynı mesajda birleştirilmez** — önce rotasyon, sonra görev emri.

## 2. Görev Emri Sözlüğü
| KAHİN cümlesi | Anlamı |
|---|---|
| "X-01'i devret" | Orkestratör görevi subagent'a verir; raporu doğrulayıp kayda yazar |
| "X-01'i kendin yap" | Orkestratör bizzat yapar; subagent başlatmaz |
| "X-01'i hallet" (mod belirtilmezse) | Orkestratör karar verir; karar + gerekçe kayda düşer |

## 3. Kilit Bekleme (Çakışma Önleme)
- Başlatılacak görev başka bir ajanın **kilitli** göreviyse: **beklenir**; kilit sahibi görevi `done` yapınca ORCH-05 kilidi otomatik düşürür, sonra başlanır. Kilitli dosyaya dokunulmaz.

## 4. Subagent Kuralları
- Subagent **asla orkestratör olamaz**; rotasyon yalnızca KAHİN ritüeliyle.
- Subagent panoya görev **ekleyemez**, yalnızca rapor yazar.
- Subagent `decision_log.jsonl`'e doğrudan **yazamaz**; kaydı orkestratör atar (`subagent` alanıyla kimliklendirir).

## 5. ORCH-08 Ayrıntı (Tetikleme ve Onay Kuyruğu)
- **Atama:** `python scripts/gorev_at.py at --task-id X --baslik "..." --ajan kilo [--oncelik P1] [--dosya a.py,b.md] [--talimat "..."]` → panoya ekler (dosyalar otomatik kilitlenir) + `data/orchestrator/triggers/kilo.jsonl` postasına tetik düşer.
- **Panorama:** `python scripts/gorev_at.py pano` → tüm postalar + onay kuyruğu tek bakışta.
- Reddedilen iş nedenle döner; ajan düzeltip yeniden teslim eder (kuyruk yeni kayıt ekler, eski reddedilmiş olarak kalır — denetim izi).
- `review` durumunda kilitler düşmez; yalnızca onayda (`done`) düşer.
- Tetikler ajan bazlı izoledir: kilo postası grok tarafından okunamaz.
- Görev panoya yazılınca ajan bunu ancak panoyu elle açarsa görüyordu; atama anında ajana **tetik düşer**, ajan tek komutla postasını okur.

## 6. Ajan Başlangıç Protokolü (Açıklama)
- Ajan oturum açtığında veya kullanıcı `"başla"`, `"go"`, `"devam"` gibi tek kelimelik tetik verdiğinde **ilk iş olarak** posta kutusunu kontrol eder. Kullanıcının uzun uzun komut yapıştırmasına gerek yoktur; tek kelimelik onay ajanın postasını kontrol edip işe başlaması için yeterlidir.

## 7. Ajan Rol Profilleri ve Bulgu Notu (2026-09-15, orkestratör kararı)
Gözleme dayalı iş bölümü (cline: KR-1..KR-5 gerçek bulgular; kilo: hacimli üretimde hızlı, kodlama/BOM hatalarına eğilimli):

| Ajan | Birincil rol | Tipik görev |
|---|---|---|
| **kilo** | Üretim / hacimli iş | dosya üretimi, scraper, migrasyon, toplu test yazımı |
| **cline** | Denetim / hata avı | review, refactor, kalite guard'ları, kilo teslimlerinin çapraz incelemesi |
| **roo** | Orkestratör | brif, onay/ret, decision_log, eskalasyon |

Kurallar:
1. **cline briflerine standart "BULGU NOTU" eklenir:** *"Kapsam dışında gördüğün bug/hata/kodlama sorununu DÜZELTME; `data/orchestrator/<TASK_ID>_bulgular_<tarih>_cline.md`'ye yaz ve roo'ya tetik düşür."* Kapsam dışı dosyaya dokunmak teslim reddi sebebidir (kilit disiplini korunur).
2. **kilo teslimleri cline'a çapraz incelemeye gider** (zincir: kilo teslim → cline review → roo onay). Reddedilen iş kilo'ya nedenle döner.
3. kilo teslim öncesi kodlama kontrolü zorunlu (`python scripts/kodlama_denetim.py`; hazır olana dek: 0 bayt / BOM / NUL elle doğrulanır).
4. Son söz roo'da kalır; cline bulgusu "öneri"dir, karar ve önceliklendirme decision_log'a yazılır.

## 8. Harici Ajan Entegrasyonu (External Agents)
İç ajanlara ek olarak dış yapay zeka ajanları (Cursor Grok, GitHub Copilot, Claude Code vb.) kullanılabilir. Tüm harici ajan etkileşimi **orkestratör üzerinden** ve **yalnızca `workspace/external/{agent_id}/` workspace'i** üzerinden yürütülür.

Temel kurallar:
- Harici ajanlar proje köküne doğrudan erişemez; yalnız kendi workspace'inde çalışır.
- `.env`, gizli anahtarlar, KVKK kapsamındaki veriler ve üretim şeması harici ajana **gönderilmez**.
- Her görev, orkestratör tarafından hazırlanan **JSON/Markdown brief + bağlam + kısıtlar** paketiyle başlatılır.
- Harici ajan çıktısı güvenilir değildir; orkestratör + kalite ajanı + insan onayı döngüsünden geçmeden ana dala alınmaz.
- Başarısızlık durumunda **maksimum 3 deneme**, sonrasında iç ajanlara reassign yapılır.
- Tüm hatalar `AGENT_SYNC.md` → "ErrorLedger" bölümüne kaydedilir.

Görev tipleri (harici ajana özel): Code Review, Refactoring, Test Üretme, Dokümantasyon, Veri Dönüşümü, Araştırma.

Referanslar: `AI proje v1/V10/08-Ajanlar/07_harici_ajan_protokolu`, `AI proje v1/V10/08-Ajanlar/08_harici_ajan_gorev_onerileri`, `AGENT_SYNC` (External Agent Registry + ErrorLedger).

## 9. Versiyon Hiyerarşisi ve Aktif Kaynaklar (SSOT)
| Katman | Versiyon | Amaç | Konum |
|--------|----------|------|-------|
| **Ana Bağlam** | V9 | Tek tutarlı tasarım ve teknik kararlar | `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` |
| **Yönetim** | V10 | Görevler, durum, ajanlar, kurallar | `AI proje v1/V10/` dizini |

- **V9** = *Ne yapıldığı ve neden* (teknik tasarım, mimari kararlar, veri stratejisi); **V10** = *Nasıl yönetildiği* (görev panosu, ajan tanımları, kurallar, şablonlar).
- **Çakışma durumunda V9 zafer kazanır.** V8, V7, V6 önceki sürümler referans devredir; karar ve iş akışı aktif V9 üzerinden yürütülür.
- **Yeni bir versiyon oluşturulmadan V9 güncellenemez;** büyük tasarım değişiklikleri için V11 taslağı oluşturulur.
- Görev atamaları V10'un `TODO.md`'si üzerinden yapılır; teknik tasarım V9'a dayanır. Ajan tanımları `V10/08-Ajanlar/` altında tutulur; her ajan kendi dokümanını taşır. Harici ajan protokolü `07_harici_ajan_protokolu` dosyasında tanımlıdır.
- Kalıcı durum için tek doğru kaynak: ana bağlam → V9 dokümanı; görev listesi → `V10/TODO.md`; proje durumu → `V10/project_state.md`; değişiklik geçmişi → `V10/CHANGELOG.md`.
- `AI proje v1/` altında çalışırken ayrıca `AI proje v1/AGENTS.md` kuralları geçerlidir (açıklamalı ilerleme, tip güvenliği, hardcoded secret yasağı vb.).
- **MVP kuralı:** Veri tabanı, temel temizleme ve iş akışı kanıtlanmadan kullanıcı odaklı web arayüzüne geçilmez. Hızlı iç görünüm için Streamlit gibi sade ara yüz seçilir.

### Obsidian Vault Git Takibi (Submodule)
- `AI proje v1/` (Obsidian vault) **pinli submodule** olarak ana repoda takip edilir (bkz. `.gitmodules` → `AI-proje-v1` reposu). Ana repo yalnızca gitlink (commit hash) saklar.
- Vault içinde değişiklik yapınca sıra: (1) vault reposunda commit + push (`git -C "AI proje v1" push`), (2) ana repoda `git add "AI proje v1"` ile yeni pin işle.
- Vault içindeki `.env` vb. hassas dosyalar vault'un kendi `.gitignore`'unda dışlanır; ana repoya asla girmez.

## 10. Dosya Erişim Matrisi
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

## 11. Marka Terminolojisi (Tam Metin, MRK-04)
- **Huginn** 🦅: Müşteri yüzeyi (8000) — canlı izleme, "Ne oluyor?" Teknik önek: `huginn_`
- **Muninn** 🛡️: İç ekip yüzeyi (8501) — hafıza, denetim, "Ne oldu, neden?" Teknik önek: `muninn_`
- **Odin** ⚡: Çekirdek/altyapı (görünmez) — karar, yetki, köprü. Teknik önek: `odin_`

Yazım kuralları (ZORUNLU):
- `Huginn`, `Muninn`, `Odin` **çevrilmez, kısaltılmaz, ekle bölünmez**. **Yasak yazımlar:** `Huggin`, `Hugginn`, `Hugin`, `Munin`, `Muginn`, `Munnin`, `Odinn`, `Odın`.
- Türkçe ek alırken kesme işareti: `Huginn'in`, `Muninn'e`, `Odin'in`.
- Dil paketi anahtarları `{marka}_{alan}_{durum}` biçiminde, **en az 3 parça**: `huginn_akis_bos` ✅ · `huginn_bos` ❌
- Kod içi teknik önek küçük harf: `huginn_`, `muninn_`, `odin_`.

**Marka kiti: `docs/brand/` (D-44/D-45 kapsam ayrımı):** Marka metni, logo, web/pazarlama görseli
ve LLM üretim prompt'ları `docs/brand/` setinden üretilir; okuma sırası
`ai-rules.md` → `company.md` → `brand.md` → `design-tokens.json` → ilgili `prompts/*.md`
(kit içi tek kaynak: `docs/brand/README.md`). **İki palet, iki kapsam — birleştirme YOK:**
`docs/brand/design-tokens.json` pazarlama/web/logo SSOT'udur; `src/company_master/ui/tokens.py`
ürün UI SSOT'udur (Indigo `#6366f1`, değişmez). Bu bölüm (§11) teknik SSOT'tur; marka kiti onu
**tamamlar**, çelişirse §11 kazanır.

**"Tarihsel Çatı Adı" kuralı:** `huginn` adı veritabanı adı, repo adı, `HuginnMCPServer`, `admin@huginn.local` gibi teknik kimliklerde **hiç değişmez**. Marka ayrımı yalnızca kullanıcıya görünen metin ve yeni kod adlandırmasında geçerlidir. **Sıfır migration.**

**Güvenlik supabı — mitolojik dil yasağı:** Hata mesajları/hata kodları, para-fatura-fiyat-kota bilgisi, yetki reddi ve güvenlik uyarıları, yasal/KVKK/sözleşme metinleri, tablo başlıkları/metrik değerleri/menü etiketlerinde mitolojik dil **kesinlikle kullanılmaz**. Yasaklı sözcükler (`veri` katmanı): `Huginn, Muninn, Odin, Bifröst, diyar, kuzgun, taht, mühür, Valhalla, Asgard`.
❌ "Bifröst çöktü, kuzgunlar geri dönemiyor." ✅ "Bağlantı kesildi (503). Yeniden deneniyor."

**Paket → kuzgun mantıksal haritası (fiziksel taşıma YOK):**
| Kod dizini | Kuzgun | Gerekçe |
|---|---|---|
| `web_dashboard/` (8000 statik) | 🦅 Huginn | Müşteri yüzeyi |
| `web_dashboard/tabs/admin_*` | 🛡️ Muninn | İç ekip ekranları |
| `src/company_master/engine/`, `intelligence/`, `vector/` | ⚡ Odin | Karar çekirdeği |
| `src/company_master/db/`, `schema/`, `etl/` | 🛡️ Muninn | Hafıza/arşiv |
| `src/company_master/api/`, `gateway/`, `queue/` | 🦅 Huginn | Canlı akış |
| `src/company_master/auth/`, `logging/`, `orchestrator/` | ⚡ Odin | Yetki ve yönetim |

⚠️ Bu tablo **mantıksal**dır. Hiçbir dizin yeniden adlandırılmaz veya taşınmaz; import yolları değişmez.

## 12. FastAPI (8000) Docker Ayrıntısı (2026-09-15, roo bulgusu)
- 8000 portu **Docker** container'ında (`huginndatainsights-api-1`, `docker-compose.yml` → `api`) dinler; `web_app.py` imaja **kopyalanır**, volume olarak bağlı değildir.
- `scripts/servisleri_baslat.py durdur/baslat --servis web` yalnızca yerel nöbetçiyi (watchdog) yönetir, container'a dokunmaz → yeni endpoint **canlıya çıkmaz** (belirti: `/api/health` ok ama yeni yol 404).
- `web_app.py` veya `src/**` (API tarafı) değişince: `docker compose up -d --build api` çalıştır, ardından yeni endpoint'i `curl` ile doğrula (404 dışı kod bekle).
- Yerel watchdog + Docker aynı anda çalışıyorsa port çakışması riski vardır; teslim özetinde hangisinin hizmet verdiğini yaz.

## 13. VPN Kullanım Kuralı (2026-09-01)
- Kullanıcı VPN kullanmaktadır; gelecekte bazı ağ işlemleri (API istekleri, web scraping, kurumsal erişim) VPN kaynaklı hata verebilir.
- Aşağıdaki durumlarda kullanıcıya açıkça bildir:
  - Ağ isteği timeout / connection / DNS hatası veriyorsa: "Olası neden: VPN. Gerekirse VPN'i kapatıp deneyebilirsin." notu ekle.
  - IP kısıtlamalı bir endpointe erişim engellendiyse: VPN değiştirmeyi veya kapatmayı öner.
  - Erişilen hedef site/API coğrafi kısıtlama gösteriyorsa: VPN'in konumunu değiştirmeyi öner.
- Kullanıcı VPN'i kapatabileceğini onayladı. Şüpheli/güvenilir olmayan durumlarda (özellikle ödeme, kişisel veri, yasal riske girebilecek işlemler) VPN'i kapatmadan önce kullanıcıya sor.
- Kritik güvenlik uyarıları, yasal/yönetmelik riskleri, geri dönüşü olmayan işlemler her zaman NORMAL ve açık dilde yazılır.
- Kural referansı: `V10/09_kurallar_ve_promptlar/10_vpn_kurali.md`

## 14. Görev Panosu ve Dosya Kilidi (Tam Metin, TOK-01)
Canlı görev takibi ve dosya kilidi mekanizması vardır; kimin hangi dosyada, hangi görevde olduğunu görmeden dosya değiştirme.

1. **Başlamadan önce kontrol:** `data/orchestrator/task_board.json` (veya `gorev_panosu.md`), `AGENT_SYNC.md` → "Aktif İşler", `data/orchestrator/file_locks.json` (planladığın dosyalar kilitli mi?).
2. **Görev al/oluştur:** `task_board.py` → `gorev_ekle(task_id, baslik, sahip, oncelik, dosyalar=[...])`; `dosyalar` otomatik kilitler, çakışmada `PermissionError` — o dosyaya dokunma, kapsam değiştir veya kullanıcıya danış.
3. **Durum güncelle:** başlarken `durum="aktif"`, bitince `durum="done"`, engellenince `durum="blocked"` + `not="..."`.
4. **Kilidi bırak:** iş bitince `lock_birak(dosya, sahip)`.
5. Aynı dosyada paralel değişiklik yapılmaz; kilit yoksa bile `file_locks.json`'suz büyük değişikliğe girilmez.
6. `AGENT_SYNC.md` **otomatik üretilir** (`sync.agent_sync_yaz()`); elle büyük yeniden yazım yapılmaz.

## 15. ORCH-08 Akış ve Kurallar (Tam Metin, TOK-01)
Posta kutusu sistemi: atama anında ajana tetik düşer; ajan tek komutla postasını okur.

1. **Atama:** `python scripts/gorev_at.py at --task-id X --baslik "..." --ajan kilo [--oncelik P1] [--dosya a.py,b.md] [--talimat "..."]`.
2. **Okuma:** `python scripts/gorev_kutusu.py bak --ajan kilo` → **al** → brif → iş → **teslim**.
3. **Teslim:** iş bitince görev `review`'a geçer (onay kuyruğuna düşer); **`done` olmaz**.
4. **Doğrulama:** onaysız `done` geçersizdir. Kontrolör: `gorev_kutusu.py onay-bekleyen` → `onayla --task-id X --ben orkestrator` veya `reddet --neden "..."` (görev `aktif`'e döner).
5. **Özet:** `gorev_at.py pano` → tüm postalar + onay kuyruğu.

Kurallar: iş bitince doğrudan `gorev_guncelle(durum="done")` çağrılmaz (teslim→onay kapısı). Reddedilen iş nedenle döner, düzeltilip yeniden teslim edilir (denetim izi korunur). `review` durumunda kilitler düşmez; yalnız onayda (`done`) düşer. Tetikler ajan bazlı izoledir (kilo postasını grok okuyamaz).

## 16. Ajan İsim Kuralı — D-33 (Tam Metin, TOK-01)
Kanonik ajan adları **üçtür**: `kilo`, `cline`, `roo`. Varyantlar aynı ajana çözümlenir:

| Kanonik | Kabul edilen yazımlar | Posta kutusu |
|---|---|---|
| `kilo` | Kilo, KILO, Ajan kilo, ajankilo, kilo_code, kilocode | `data/orchestrator/triggers/kilo.jsonl` |
| `cline` | Cline, Ajan cline, ajancline, clinebot | `.../triggers/cline.jsonl` |
| `roo` | Roo, Ajan roo, roo_code, roocode, orkestrator | `.../triggers/roo.jsonl` |

- Tek çeviri noktası: `trigger.ajan_normalize()` (`src/company_master/orchestrator/trigger.py`); `gorev_kutusu.py` ve `gorev_at.py` otomatik çevirir.
- Yeni posta kutusu dosyası (`roo_code.jsonl`, `orkestrator.jsonl` vb.) **açılmaz**; bayat sayılır (ORCH-TEMIZLIK-01).
- Ajan "postam yok" demeden önce kanonik adla bakar: `gorev_kutusu.py bak --ajan kilo`.

## 17. Ajan Kılavuzu ve Teslim Kontrol Listesi (Tam Metin, TOK-01)
1. Ana bağlamı oku (V9 dokümanı) · 2. Koordinasyonu kontrol (`AGENT_SYNC.md`, `gorev_panosu.md`, `file_locks.json`) · 3. Görev/sınır doğrula (`TODO.md`, `project_state.md`) · 4. Kilitle (`gorev_ekle(..., dosyalar=[...])`) · 5. MVP/sınır uyumlu ilerle · 6. Bitince `gorev_guncelle(..., durum="done")` + `lock_birak` + özet (atlanamaz) · 7. Son kontrol: hedef/MVP/sınır dışına çıkılmadı mı?

**Teslim Öncesi Kontrol Listesi (ŞART — eksikse teslim reddedilir):**
- Brifteki her madde karşılandı mı? (yarım iş "tamamlandı" sayılmaz)
- Yeni/değişen dosyalar gerçekten diskte var mı (yol yol doğrula)?
- Belge işinde: kaynak + ayna ikisi de yazıldı; wikilink hedefleri var.
- Kod işinde: hedefli testler yeşil + tam regresyon `python -m pytest tests/ -q --continue-on-collection-errors` (koleksiyon hatası 0 olmalı), sayı özete yazıldı.
- Dosyalar UTF-8, BOM/NUL yok; Türkçe karakterler bozulmamış. `python scripts/kodlama_denetim.py` (BUG-ENCODING-GUARD).
- **Yasak:** PowerShell `Out-File -Encoding utf8` / `Set-Content -Encoding utf8` (BOM yazar); Python `open(..., encoding="utf-8")` veya PS 7+ `utf8NoBOM` kullan.
- Kilit alınan dosya dışına dokunulmadı; dokunulduysa özette belirtildi.
- `--ozet` içinde: değişen dosya listesi + test sayısı + eksik/erteleme açıkça yazıldı.

## 18. Genel Kurallar (Dosya/Kod, TOK-01)
- Gizli bilgiler (API anahtarı, token, şifre) asla koda veya notlara yazılmaz; `.env` kullanılır.
- Kullanıcının dosyaları gerekçe açıklamadan silinmez / üzerine yazılmaz.
- Tüm dosyalar **UTF-8**; Türkçe karakterler (ç, ğ, ı, İ, ö, ş, ü) bozulmadan oluşturulur/kaydedilir.
- Kod kalitesi: PEP 8, tip açıklamaları, her özellik için birim test, hardcoded secret yok, test edilmemiş iş teslim edilmez.

## 19. Proje Sınırı Kuralı (Tam Metin, TOK-01)
1. Projeye ait her şey yalnız repo kökü (`C:\Huginn Data Projesi\Huginn Data Insights`) içinde; üst dizine dosya oluşturamaz, taşıyamaz, kopyalayamaz. Mutlak yol kullanan komut/scripthedefi daima repo içinde olmalı (`Path(__file__).resolve()` ile köke bağla; `..`/üst dizin hedefi yasak).
2. Geçici dosya: `data/_tmp/` veya `_trash/` (her ikisi `.gitignore`'da). Köke `_*.py`, `*.bak`, `*.base` bırakılmaz; iş bitince silinir.
3. Dışarıda proje öğesi görülürse SİLME, ilgili bölüme içeri TAŞI; özette "dış dizinden taşındı: kaynak → hedef" yaz.
4. Ürün Sahibi referans dosyası (ör. `KONUM_NOTU.md`): oku, talimattaki hedefe taşı, dış kopyayı kaldır, decision_log'a yaz. Bunlar kural ihlali değil, **taşıma emridir**.
5. Denetim: oturum başında `python scripts/proje_siniri_denetim.py` (hazır olana dek elle `dir ..`).
6. Ürün Sahibi notu (aynen): *"Dizinin dışında projeye ait hiçbir şey görmek istemiyorum."*

## 20. Streamlit Yeniden Başlatma Kuralı (Tam Metin, TOK-01)
- `.streamlit/config.toml` → `fileWatcherType = "none"`: kod değişikliği otomatik yüklenmez.
- UI dosyasına (`app.py`, `web_dashboard/**`, `src/company_master/ui/**`, `.streamlit/**`) dokunan ajan teslimden ÖNCE `python scripts/streamlit_restart.py` çalıştırır ve özete yazar (`--durum` durum, `--durdur` kapat).
- Ürün Sahibi yalnız tarayıcıda F5 çeker; ondan terminal işlemi istenmez. Restart yapılmamış UI teslimi reddedilir.
- Script: portu dinleyen süreci öldürür, `.venv` python'u ile 8501'de yeniden başlatır, `/_stcore/health` "ok" dönene dek bekler; log `logs/streamlit_8501.log`.

## 21. FastAPI Backend Kuralları (CLAUDE.md'den taşındı, TOK-01 — 2026-09-16)
Çakışma durumunda AGENTS.md çekirdeği geçerlidir. (Kaynak: CLAUDE.md "FastAPI Expert Backend System Rules" — token sıkıştırması için buraya alındı.)

You are a Senior Backend Architect specializing in Python 3.11+, FastAPI, PostgreSQL (AsyncSession), MongoDB (Motor), and JWT/OAuth2 Security.

### Core Architecture & Async Rules
- **Never Use Sync Code:** All endpoints, database connections, and external requests must be non-blocking (`async def`).
- **Layer Separation:** Enforce strict architecture: `routers/` (Endpoints), `services/` (Business Logic), `repositories/` (Database queries), `schemas/` (Pydantic v2).
- **Data Hiding:** Always use explicit `response_model` schemas to prevent sensitive info (like password hashes) from leaking.

### Technical Standards
- **PostgreSQL:** Use `AsyncSession` with eager loading (`selectinload`/`joinedload`) to prevent N+1 queries.
- **MongoDB:** Safely handle BSON `ObjectId` parsing and string conversion.
- **Security:** Enforce `passlib[bcrypt]` for secure password storage. Enforce dependency injection (`Depends(get_current_user)`) on protected routes.






