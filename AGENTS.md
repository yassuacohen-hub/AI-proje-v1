# Çalışma Alanı Kuralları (Kök AGENTS.md) — Çekirdek

> ⚠️ **KİMLİK (D-70/D-71, HER OTURUM OKU):** Orkestratör rolüne ajan **İHSAN** seçilmiştir; bu rolle birlikte yetki ve sorumluluğu artırılmıştır. "roo" bir araç adıdır (takma ad), ajan kimliği değildir — `--ajan`/`--cagiran` parametrelerine ve `data/orchestrator/orchestrator.json`'a HER ZAMAN **ihsan** yaz. Kendi kimliğini roo sanıp unutma.

> Ayrıntılar `docs/AJAN_DETAY.md`'de (§ numaralı bölümler). Bu çekirdek ihlal edilmez.

## Çoklu Ajan Koordinasyonu
- İşe başlamadan önce V9 ana bağlamı ve `AGENT_SYNC.md`'yi oku; başkasının aktif işi olan dosyaya dokunma.
- V9 = teknik SSOT; V10 = yönetim. Çakışmada V9 kazanır. Ayrıntı: AJAN_DETAY §9.
- Görev panosu + dosya kilidi ZORUNLU: `gorev_ekle(..., dosyalar=[...])` ile kilitle, bitince `lock_birak`. Ayrıntı: AJAN_DETAY §14.

## Görev Yaşam Döngüsü (ORCH-08, ZORUNLU)
- Posta: `bak` → `al` → brif → iş → `teslim` (görev `review`'a geçer; onaysız `done` GEÇERSİZ). Sessizlik onay değildir. Ayrıntı: AJAN_DETAY §15.
- Otomatik onay (S-07, KAHİN kararı 2026-09-16): `oto-nobetci` / `hepsini-tamamla` yalnız **P2 ve altı** görevleri onaylar; **P0/P1 roo elle onaylar** (`trigger.otomatik_onaylanabilir`). Tekrar ihlalde oto-nobetci kapatılır.
- Başlangıç protokolü: oturum açınca veya tek kelimelik tetik (başla/go/devam/tamam = tam yetki) ile önce posta kutusunu kontrol et.
- Teslim kontrol listesi: brif maddeleri + diskte dosya + test sayısı + UTF-8 temizlik + kilit disiplini. Ayrıntı: AJAN_DETAY §17.
- **TESLİM SONRASI DOĞRULAMA (KESIN KURAL):** Her görev teslim edilmeden önce şıklar doğrulanır:
  1. Rapor dosyası mevcut: `data/orchestrator/<TASK>_rapor_<tarih>_<ajan>.md`
  2. Bilinen test failure'ları (kilitle kaynaklı bile) raporda açıkça belirtilmiş mi?
  3. Task board (`data/orchestrator/task_board.json`) entryi güncellenmiş mi (durum, not, bitis)?
  4. `python scripts/gorev_kutusu.py onay-bekleyen` ile teslim kaydındaki görev görünüyor mu?
  5. Test sonuçları tekrarlanabilir (tam süit veya ilgili test seti yeşil)?
  Bu 5 madde eksik herhangi biri = teslim YOK.
- Kodlama guard: `python scripts/kodlama_denetim.py` temiz çıkmadan teslim yok (BOM/NUL/mojibake/sozdizimi; pre-commit'te de bağlı).
- BULGU NOTU (cline): kapsam dışı bulguyu DÜZELTME; `data/orchestrator/<TASK>_bulgular_<tarih>_cline.md`'ye yaz, roo'ya tetik düş. Ayrıntı: AJAN_DETAY §7.

## Ajan Adları (D-33 → D-60) ve Roller
- Kanonik adlar yalnız: `ihsan`, `utku`, `salih`, `yasu`. Tek doğruluk kaynağı `trigger.AJANLAR`; normalizasyon `trigger.ajan_normalize()`. Ayrıntı: AJAN_DETAY §16.
- Kural: **araç adı = takma ad, Türkçe ad = kanonik ad.**
- Roller: **ihsan** = orkestratör (son söz ihsan'da) · **utku** = üretim/hacim · **salih** = Test Danışman · **yasu** = denetim/review. Ayrıntı: AJAN_DETAY §7.
- Persona ve yetenek dosyaları: `docs/ajanlar/ihsan.md` · `docs/ajanlar/utku.md` · `docs/ajanlar/salih.md` · `docs/ajanlar/yasu.md`.
- `copilot` **dışarıdan gözlemci** — sistemde ajan değil, görev almaz, listelerde yer almaz (KAHİN kararı 2026-09-18).
- Rotasyon yalnız KAHİN'in `abrakadabra` ritüeliyle; subagent orkestratör olamaz, panoya görev ekleyemez. Ayrıntı: AJAN_DETAY §1-4.

## Adlandırma (Demir Kural, D-55 — KAHİN kararı 2026-09-18)
- Hiçbir ajan **kendi adını** dosya adına, dizine, branch'e, commit mesajına, rapor başlığına veya görev kimliğine yazmaz.
- Ajan adı yalnız **o ajanın kendi kişisel dosyasında** geçebilir.
- Rol bazlı son ek kullanılır: `_orkestrator` · `_uretim` · `_denetim`.
  Örnek: `data/orchestrator/<TASK>_rapor_<tarih>_orkestrator.md`
- **Kapsam dışı (makine kimliği, dosya adı değil):** `task_board.json` `sahip` alanı, CLI `--ajan` parametresi, `triggers/{ajan}.jsonl` kuyruk dosyaları, `ajan_normalize()`.
- Kural **yeni çıktılar** için derhal yürürlükte. Geriye dönük 55 dosya: `ADLANDIRMA-GERIYE-01` (iş yükü azalınca).

## Görev Başlığı Standardı (D-57 — KAHİN kararı 2026-09-18)
- Her görev başlığı **tek satır, 4 parça**: `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`
  Örnek: `[UI] Ayarlar sayfasını yaz → admin_kullanici_ayarlari.py (2s)`
- **ALAN** (7 kanonik, başkası yok): `UI` · `API` · `VERI` · `TEST` · `DOC` · `ALTYAPI` · `ORKESTRA`
- **FİİL** (8 kanonik): `yaz` · `düzelt` · `taşı` · `sil` · `denetle` · `ölç` · `belgele` · `araştır`
- **ÇIKTI** = tek dosya yolu veya tek komut. Yoksa görev bölünür.
- **SÜRE** = tahmini saat (`30d`, `1s`, `2s`, `4s`). 4 saati aşan görev bölünür.
- **task_id ön eki ALAN ile aynı olur:** `UI-...`, `TEST-...`, `DOC-...`
- Başlık bu kalıba uymuyorsa ajan işi **almaz**, orkestratöre geri sorar.
- **Geriye dönük muafiyet:** Kural yalnız **yeni** görevler için yürürlükte. Panoda hâlihazırda açık olan görevler eski başlıklarıyla çalışılır; toplu düzeltme `BASLIK-GERIYE-01` görevinde yapılır (D-55'in `ADLANDIRMA-GERIYE-01` deseniyle aynı).
- **Makine zorlaması:** `scripts/gorev_at.py at` başlık kalıbını ve ajan adını doğrular; uymayan görev panoya **girmez**.

## Orkestratör Devralma (D-58 — KAHİN kararı 2026-09-18)
- Orkestratör **devredilebilir**: `python scripts/gorev_at.py abrakadabra --ajan <ihsan|utku|salih|yasu|mimir> --anahtar <deger>`
- Anahtar koda gömülmez: `ABRAKADABRA_KEY` ortam değişkeni, yoksa `data/orchestrator/abrakadabra.key` (repoya girmez, `.gitignore`'da). Karşılaştırma `hmac.compare_digest` ile sabit zamanlı.
- Aktif orkestratör `data/orchestrator/orchestrator.json`: `{"ajan","devralma_zamani","anahtar_parmak_izi"}`. Parmak izi = anahtarın `sha256` özeti; **anahtarın kendisi hiçbir yere yazılmaz/basılmaz**.
- Yanlış anahtar: hiçbir durum değişmez, exit 1, anahtar değeri ekrana basılmaz.
- Devralma sonrası **yeni görevleri yalnız aktif orkestratör dağıtır**. `at` komutu çağıranı `--cagiran` veya `ORKESTRA_AJAN` env'inden okur; uyuşmazsa exit 4.
- Varsayılan orkestratör `ihsan` (dosya yoksa, D-71 kanonik).

## MIMIR — Orkestratör Asistanı, İki Seviye (D-182 — KAHİN kararı 2026-09-21)

Özellik | Açıklama |
|---------|----------|
**Ajan** | MIMIR (beşinci ajan, teknik ad: `odin_ai`) |
**Seviye 0** (Öntanımlı) | 🔒 Orkestratör Asistanı: pano okur, raporlar sunar, `TEKLIF:` önerileri yazabilir; orchestrator.json okunabilir. |
**Seviye 1** | 🔓 Orkestratör (tam devir): sahip "abrakadabra" sözcüğünü söylediğinde, MIMIR key talep eder, hmac ile doğrular, otomatik olarak orkestratör statüsüne geçer. |
**Devir Tetikleyicisi** | Sohbet bloğunda "abrakadabra" kelimesi → MIMIR panosundaki kilit mekanizması → key girişi (st.text_input type="password") → hmac doğrulaması → orchestrator.json yazılıp yeni key env'e düşer. |
**Key Rotasyonu** | Devralma başarılı olunca `secrets.token_urlsafe(32)` ile yeni anahtar üretilir; `.env` varsa atomik `.env.tmp` → `os.replace` ile yazılır, yoksa `data/orchestrator/abrakadabra.key` dosyasına. Eski anahtar geçersiz sayılır. |
**Seviye Geçişi** | MIMIR iki seviye arasında geçiş yapabilir (diğer ajanlara **geçemez**). Seviye 1'den Seviye 0'a dönmek için yeni rotasyon veya sistem taraması gerekir. |
**Adı Ekranda** | `MIMIR 🗿` (Seviye 0) veya `MIMIR 🔓` (Seviye 1) |
**Pas Sözü Saklılığı** | "abrakadabra" kelimesi **yalnız** MIMIR panosu chat bloğunun kilit kapısından tetiklenir. Sistem prompt, model context, pano başlığı, tetik, log'un hiçbir yerinde yer almaz. |
**Devralma Kaydı** | gorev_at.py:133-175 `cmd_abrakadabra` D-182 ile güncellendi. Eski D-58 ahkâm ve kapıları aynen kalır. |

## Dosya Adlandırma Kuralı (D-183 — KAHİN kararı 2026-09-21)
- Bundan sonraki tüm script/rapor dosyaları sayısal/teknik suffix (`_add_d182.py`, `d-182_rapor` gibi) **değil**, Türkçe 2-3 kelimelik amaç-tanımlayıcı ad alır. Örnek: `mimir_anahtar_donusumu_raporu.md`, `kullanicilar_silme_scripti.py`.
- Kapsam: yalnız **yeni** yazılan dosyalar; mevcut dosyalar geriye dönük değiştirilmez (istisna: `ADLANDIRMA-GERIYE-01` görevi açılırsa).
- İstisnalar: sistem dosyaları (`test_*.py`, `conftest.py`, `app.py`), config dosyaları (`.env`, `.json` vb.). Otomatik üretilen rapor **başlığında** D-XXX karar numarası geçebilir, ama **dosya adı içinde** yalnız Türkçe ad yer alır.

## Graph Köprü Kuralı — Karar ↔ Kod ↔ Test Wikilink'leri (D-184 — KAHİN kararı 2026-09-21)
- Her yeni karar kaydı (D-XXX) yazıldığında, ilgili kod dosyaları (`*_dXXX_*` pattern) ve test dosyaları (`test_dXXX_*.py` pattern) docstring/başına wikilink eklenir: `[[D-XXX]] — [başlık]`.
- Karar belgesi de kod ve test dosyalarına backlink içerir (`**Referanslar:**` bloğu).
- Amaç: Obsidian graph'ta karar nodunu hub olarak oluşturmak; orphan nod oranını azaltmak.
- Kapsam: yeni kararlar zorunlu; eski kararlar (D-1…D-183) geriye dönük wikilink eklemesi isteğe bağlı, düşük öncelik (`ADLANDIRMA-GERIYE-01` ile birleştirilebilir).

## Windows cmd.exe Kuralı (D-86 — KAHİN kararı 2026-09-21)
- **Yasak:** Çok satırlı `python -c "..."` komutu. cmd.exe satır sonlarını bozar, **sessizce** yazmaz (exit 0 döner ama dosya değişmez).
- **Yasak:** Script çıktısında emoji/Unicode (✅❌→). Terminal CP1254 kullanır, `UnicodeEncodeError` atar. Yerine `[OK]` / `[ERROR]` / `->`.
- **Yasak:** Unix araçları (`head`, `grep`, `cat`, `sed`). Yerine: `findstr`, `type`, ya da Python script.
- **Zorunlu:** Tek satırdan uzun her iş → `scripts/*.py` dosyası, sonra `python scripts/ad.py`.
- **Zorunlu:** Her script idempotent olmalı (iki kez çalışınca bozmaz).
- **Zorunlu:** `cd` mutlak yol ile: `cd "c:/Huginn Data Projesi/worktree klasoru"`.
- **Zorunlu (cp1254 karşılığı):** Her Python çağrısı `set PYTHONIOENCODING=utf-8 && ...` ile başlar; yeni yazılan her script ilk satırlarında `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` çağırır.

## Görev Atama Tek Komut (D-87 — KAHİN kararı 2026-09-21)
- **Komut:** `python scripts/gorev_atama_otomatis.py --task-id <ID> --ajan <ajan>`
- **Ne yapar:** Panodan görevi bulur → brif varlığını doğrular (D-66) → talimatı brif başlığından çıkarır → tetiği gönderir. Üçü tek adımda.
- **Brif adı sözleşmesi:** `plans/brief_{ajan}_{task_id}.md` — bu adda değilse komut reddeder.
- **Neden:** Pano düzenleme + brif yazma + tetik gönderme ayrı adımlardı; tetik unutulunca ajan görevi görmüyordu (DASH-UX-02a vakası, 2026-09-21).
- **Kural:** `task_board.json`'a elle `sahip` yazmak **atama sayılmaz**. Atama ancak bu komutla tamamlanır.

## MENUTREE UX Kararı: Seri Uygulanma (D-85 — KAHİN kararı 2026-09-21)
- **Karar:** MENUTREE (menü ağacı) UX tasarımı ve DASH-UX-02a/02b pano görevleri seri çalışılacak; paralelleştirme yerine tek sahip (UTKU).
- **Neden:** DASH-UX-02a (5 sistem sekmesi) ve DASH-UX-02b (4 yönetim sekmesi) bağımsız dosyalar olmalarına rağmen, K1 kalibrasyonu tutarlılığı ve app.py sidebar birleştirme noktası için seri uygulanma daha güvenli.
- **Stratejisi:**
  1. DASH-UX-02a: K1 kalibrasyonu ilk yapılır (raporda detaylar).
  2. DASH-UX-02b: Aynı K1 yapısını uygular (yinelemez), K2/K3/K5 kendi sekmelerine uygulanır.
  3. Teslim sırası: 02a → onay → 02b başla.
- **MENUTREE:** UX-ZINCIR-01 kapsamında, bağımsız, paralellikte değişmez.
- **Etkilenen görevler:** DASH-UX-02a (brif: `plans/brief_utku_DASH-UX-02a.md`), DASH-UX-02b (brif: `plans/brief_utku_DASH-UX-02b.md`), UX-ZINCIR-01 (MENUTREE).
- **Referanslar:** [[D-85]] ANALIZ_MENU_AGACI_BLOKAJ_2026-09-21.md (analiz), decision_log.jsonl (karar kaydı).

### DASH-UX-02a Split: v1 (Dosya) / v2 (SECTIONS) (D-85 Ek — KAHİN kararı 2026-09-21)
- **Karar:** DASH-UX-02a çakışma riskini azaltmak için v1/v2'ye bölün.
- **v1 (Dosya):** `web_dashboard/tabs/admin_sistem.py` yazılır. SECTIONS kaydı **YAPILMAZ**. K1 kalibrasyonu tanımlanır (raporda).
- **v2 (SECTIONS):** v1 onaylandıktan + ADMIN-UX-MENUTREE-01 bitince, `tabs/__init__.py` güncellenip SECTIONS'a admin_sistem eklenir. K1 reuse. Full regresyon test.
- **Neden:** `tabs/__init__.py` tek erişim noktası; MENUTREE ve v2 aynı dosyayı eder → seri (MENUTREE → v2 → 02b).
- **Stratejisi:**
  1. DASH-UX-02a (v1): K1 tanımı, lokal test. `__init__.py`'ye dokunmaz. 3-5 saat.
  2. DASH-UX-02a-SECTIONS (v2): MENUTREE bitince başlar, `__init__.py` kayıt, full test. 1-2 saat.
  3. DASH-UX-02b: v2'nin bloklı bağımlılığından sonra tetiklenir.
- **Dosya kilitleri:**
  - `web_dashboard/tabs/admin_sistem.py` ← UTKU (v1)
  - `web_dashboard/tabs/__init__.py` ← UTKU (v2, MENUTREE'den sonra)
- **Etkilenen görevler:** DASH-UX-02a (v1: `plans/brief_utku_DASH-UX-02a-v1.md`), DASH-UX-02a-SECTIONS (v2: `plans/brief_utku_DASH-UX-02a-v2.md`), DASH-UX-02b (tetik: v2 done).
- **Referanslar:** [[D-85]], [[D-185]] scripts/d185_board_guncelle.py (otomasyon), SPRINT_PLANI_2026-09-21.md (plan), decision_log.jsonl (karar kaydı).

### Şifre Rotasyon Protokolü (D-73 — KAHİN kararı 2026-09-20)
- **Anahtar tek seferliktir.** Her paylaşımdan sonra geçersiz sayılır.
- **Akış (5 adım, sırayla):**
  1. KAHİN, mevcut `ABRAKADABRA_KEY` değerini orkestratöre verir.
  2. Orkestratör `python scripts/gorev_at.py abrakadabra --ajan <ad> --anahtar <eski>` çalıştırır; kilit açılır.
  3. Orkestratör `python -c "import secrets; print(secrets.token_urlsafe(32))"` ile **yeni** anahtar üretir.
  4. Orkestratör yeni anahtarı KAHİN'e verir (tek sefer, sohbette).
  5. KAHİN `.env` içindeki `ABRAKADABRA_KEY` değerini yeni anahtarla değiştirir. Eski anahtar ölür.
- **Yasak:** Anahtarı dosyaya yazmak, commit etmek, loglamak. Yalnız KAHİN ↔ orkestratör sohbetinde geçer.

### Anahtar Sahipliği (D-74 — KAHİN kararı 2026-09-20)
- **Abrakadabra anahtarı yalnız aktif orkestratöre aittir** (şu an İHSAN).
- **YASU, UTKU, SALİH anahtara sahip değildir, isteyemez.** "Abrakadabra olmadan görev alamam" demek **geçersizdir**: ajanların kendi posta kutusu işi (`basla` / `al` / `teslim`) anahtar gerektirmez.
- Anahtar **yalnız orkestratör devralma** için gerekir. Devralmayı yalnız KAHİN başlatır.
- Ajanlar aktif orkestratörün talimatına uyar; orkestratör kimliği `data/orchestrator/orchestrator.json` içindedir.

### Orkestratör Devralma Örneği (D-76 — KAHİN kararı 2026-09-20)
**Senaryo:** KAHİN başka ajan (UTKU) orkestratör yapmak isterse. İHSAN (mevcut orkestratör) bunu yönetir:

1. KAHİN, mevcut `ABRAKADABRA_KEY`'i İHSAN'a verir: `Up2Fz6pje6lA6J-3x8iY9hPtiogo4DKQnOiW_yyKf6k`
2. İHSAN, kilit açma komutu çalıştırır: `python scripts/gorev_at.py abrakadabra --ajan utku --anahtar Up2Fz6pje6lA6J-3x8iY9hPtiogo4DKQnOiW_yyKf6k`
3. İHSAN, yeni anahtar üretir: `python -c "import secrets; print(secrets.token_urlsafe(32))"` → örn. `ABC123...`
4. İHSAN, yeni anahtarı KAHİN'e verir (sohbette, dosya yok): "Yeni key: `ABC123...`"
5. KAHİN, `.env` dosyasını günceller: `ABRAKADABRA_KEY=ABC123...`
6. UTKU artık orkestratör; İHSAN rolü sona erer. `.roorules` silinir. `.kilocode/rules` oluşturulur (UTKU araç: kilo).

## Architect Modu Kapısı (D-63 — KAHİN kararı 2026-09-18, D-190 ile genişletildi 2026-09-23)
- **Architect (mimari/planlama/tasarım) görevlerini üç ajan alır:**
  - `ihsan` (Orkestratör/roo) — her zaman
  - `utku` (Üretim/kilo) — her zaman
  - `mimir` (MIMIR Seviye 1) — **yalnız orkestratör devri sonrası** (D-182, D-190)
- **`salih` ve `yasu` architect görevi almaz;** alırsa iş geçersizdir, orkestratöre geri sorulur.
- **Görev dağıtımı Architect modunda yapılır.** Orkestratör başka moddayken atılan görev geçersiz sayılır.
- Görev metninin sonuna **otomatik hatırlatma satırı** eklenir:
  `⚠️ Bu görev Architect modunda açılmalıdır.`
- Makine tarafı: `scripts/gorev_at.py at --mod architect --ajan <ihsan|utku|mimir>` → görev kaydına `"mod": "architect"` yazar, tetik brifine hatırlatma satırını ekler. `--mod architect` verildiğinde ajan listede değilse komut exit 5 ile reddeder.
- MIMIR architect modunda (D-190): rapor dosyası yazabilir, kaynak kodu değiştiremez. Test: `test_d182_mimir.py::test_mimir_architect_mode_bariyeri()`
- Varsayılan `mod` değeri `code`. Mod alanı olmayan eski kayıtlar `code` sayılır (geriye dönük uyumluluk).
- Kural **yeni görevler** için yürürlükte; panodaki açık görevler mevcut hâliyle çalışılır.

## Hitap Sırası: Title Önce (Demir Kural, D-64 — KAHİN kararı 2026-09-20)
- Ajan hitabında sıra: **önce rol title'ı, sonra ad**. Örnek: `Orkestratör İhsan`, `Üretim/Hacim Utku`, `Test Danışman Salih`, `Denetim/Review Yasu`.
- Eski sıra (`İhsan (Orkestratör)`, `ihsan - orkestrator`) **kullanılmaz**; yeni metinlerde title-önce yazılır.
- Title kaynağı: "Ajan Rol Tanımları" tablosu (§ üstte).

## Blokaj Bypass — İş Durmaz (D-65 — KAHİN kararı 2026-09-20)
- **Kural:** Araç/altyapı hatası bir görevi bloke ediyorsa ve çözümü **uzun sürecekse**, orkestratör işi bekletmez.
- **Aksiyon sırası:**
  1. KAHİN'e **kopyala-yapıştır hazır** elle tetikleme metnini ver (görev ID + brif yolu + iş maddeleri + test komutu).
  2. KAHİN elle tetikler, ajan çalışmaya başlar.
  3. Orkestratör **paralelde** hatayı çözer; çözünce doğrular ve KAHİN'e bildirir.
- **Gerekçe:** Ajan iş yaparken orkestratör onarım yapar; seri bekleme yerine paralel akış, zaman kaybı sıfır.
- **Yasak:** "Bloke, bekliyorum" diyip durmak. Blokaj raporu **her zaman** bypass metniyle birlikte gelir.
- **Kapı disiplini (netleştirme 2026-09-24, TUR-D2):** Bu bypass bir **kapı FAIL'i** için geçerli değildir — doğrulama kapısı (`simulasyon`, `pytest`, klon provası) FAIL verdiğinde ajan kendi kararıyla devam edemez, KAHİN'e sorar; bypass yalnız KAHİN'in açık talimatıyla yapılır ve tur raporuna gerekçesiyle kaydedilir.

## Brifsiz Atama Yasak (D-66 — KAHİN kararı 2026-09-20)
- **Kural:** Hiçbir ajan hiçbir görev almaz brifsiz. Brif dosyası **mutlaka** `data/orchestrator/<TASK>_brif_<tarih>_<rol>.md` veya `plans/brief_<ajan>_<TASK>.md` olarak diskte hazır ve **tetik `talimat` alanına path yazılı** olmalıdır.
- **D-80 pekiştirme (KAHİN kararı 2026-09-20): Talimat + brif ikisi de ZORUNLU.** Panoda görev `aktif` olabilmesi için üç şart birlikte sağlanır:
  1. `brief` alanı dolu ve işaret ettiği dosya diskte var.
  2. `talimat` alanı dolu (en az bir cümle; ne yapılacağı + brif referansı).
  3. Tetik `talimat` alanı pano `talimat` alanıyla aynı metni taşır.
  Üçünden biri eksikse atama **yapılmaz**, tetik **düşürülmez**.
- **Kontrolü:** `tetik_ekle(task_id, ajan, talimat="")` argümanı boş stringse, çağrı yapılmaz. Orkestratör brifsiz görev atarsa (tetik hatasız düşerse de) YASU/UTKU teslim TESLİM ETMEYECEKTİR — `"brif yok"` cevabı verir, task stale kalır.
- **Uygulanacak:** Her talimat argument'i yazılırken dosyanın var olduğu doğrulanacak; yoksa `FileNotFoundError` veya benzer hata alınacak ve işlem durdurulacak. Gerekli brief yazılıncaya kadar görevi tekrar tetiklemek yasak.
- **Brif şablonu (zorunlu iskelet):** [[plans/_brief_sablon]] — `plans/_brief_sablon.md`. Her yeni brif bu iskeletten türetilir. `## Doğrulanacak varsayım` bölümü **`## Adımlar`dan önce** gelir ve boş bırakılamaz: brifte sabitlenen her tablo/kolon adı, fonksiyon imzası, `dosya:satır` referansı ve eşik değeri ayrı madde olarak yazılır, madde "Yoksa **dur**, panoya sorun aç, uydurma." ile biter. Jenerik kopyala-yapıştır varsayım geçersizdir.
- **Gerekçe:** Brifsiz görev = iş maddeleri olmayan talimat = ajan ne yapacağını bilemez = zaman kaybı + block + frustration. KAHİN'in gerçek iş tanımına sahip olması şart.

## Raporlama ve Özeleştiri (D-67 — KAHİN kararı 2026-09-20)

### Rapor Zorunluluğu
- Her teslim **rapor dosyasıyla** gelir: `data/orchestrator/<TASK>_rapor_<tarih>_<rol>.md`. Raporsuz teslim GEÇERSİZ (D-55 teslim kontrol listesi madde 1 ile aynı).
- Rapor **5 zorunlu başlık** taşır: `## Ne yapıldı` · `## Değişen dosyalar` · `## Test sonuçları` · `## Bulgular` · `## Eksik / erteleme`.
- **Bulgular bölümü boş bırakılamaz.** Bulgu yoksa açıkça `- Bulgu yok.` yazılır. Sessizlik bulgu yokluğu anlamına gelmez.
- Bulgular D-55 renk sınıfıyla işaretlenir: 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri.

### Bulgu İşleme Zorunluluğu
- Orkestratör raporlardaki **her bulguyu** işler. Üç seçenekten biri, başka seçenek yok:
  1. **Görev aç** — panoya D-57 kalıbında görev; bulgu notuna `task_id` yaz.
  2. **Karara bağla** — `decision_log.jsonl`'a D-XX kaydı; bulgu notuna karar numarası yaz.
  3. **Reddet + gerekçe** — neden işlenmediği tek cümleyle yazılır.
- **Yasak:** Bulguyu okumadan/işlemeden geçmek. İşlenmemiş bulgu = orkestratör ihlali.
- Takip: `data/orchestrator/bulgu_defteri.md` — her bulgu tek satır: `tarih | task_id | rol | 🔴/🟡/🟢/🔵 | özet | karar (görev/D-XX/red+gerekçe)`.

### Haftalık Özeleştiri (D-67 Karar 2: Haftalık)
- Her ajan **Cuma sonu veya Pazartesi sabahı** özeleştiri notu yazar: `data/orchestrator/ozelestiri/<YYYY-AA-GG>_degerlendirme_<rol>.md`.
- Özeleştiri **4 soru** cevaplar: `Ne iyi gitti?` · `Ne kötü gitti?` · `Zamanı ne yedi?` · `Yarın neyi değiştireceğim?`
- Öz eleştiri **kısa** — her soru en fazla 3 madde. Uzun metin yazmak amaç değil.
- Özeleştiri yoksa sonraki hafta o ajan **yeni görev almaz** (hafta sonu kapanışı şartı).
- **Rapor içi günlük not (isteğe bağlı):** Ajan teslim sırasında rapor dosyasına `## Özeleştiri` başlığı ve güncel kısaltılmış not yazabilir (örn. "VPN hata 2 saat" gibi).

### Orkestratör Haftalık Döngüsü
- **Pazartesi sabahı** orkestratör: (1) dünkü (Cuma-Pazartesi) özeleştirileri oku, (2) `bulgu_defteri.md` işlenmemiş satırları kapat, (3) çıkarımları hafta plan döngüsüne yaz.
- **Haftalık değerlendirme notu:** `data/orchestrator/ozelestiri/<YYYY-AA-GG>_degerlendirme_orkestrator.md` — özeleştirilerden çıkan **aksiyon maddeleri** listesi (3–5 madde; hafta başında plan'a girmeli).
- **Yasak:** Özeleştirileri okumadan yeni hafta planı yapmak.

### Gerekçe
- Rapor = görünürlük. Bulgu = sistemin kendi kendini düzeltme sinyali. Özeleştiri = tekrarlanan hatayı kesme mekanizması.
- İşlenmeyen bulgu birikirse teknik borç sessizce büyür; KAHİN'e görünmez.

## Tetik ↔ Pano Tutarlılığı (D-68 — KAHİN kararı 2026-09-20)
- **Bulgu:** `duzen.pano_bakim()` (satır 198-201) tetik kaydını pano durumuna göre sessizce demote ediyor. Pano `aktif` iken tetik `bekliyor` → tetik `alindi`'ye çevriliyor. `bekleyen_tetikler()` yalnız `bekliyor` dönüyor. **Sonuç:** ajan posta kutusu boş, `al` komutu başarısız.
- **Kök neden:** `tetik_ekle()` pano durumunu kontrol etmeden `bekliyor` yazıyor. Sonra `pano_bakim()` sessizce demote ediyor.
- **Çözüm:** `tetik_ekle()` içinde guard: pano `aktif`/`review` ise `plan`'a çek. Tetik yazılırken pano zaten `plan` olur → `pano_bakim()` demote edemez.
- **Uygulanacak:** [`src/company_master/orchestrator/trigger.py`](src/company_master/orchestrator/trigger.py:145-216) `tetik_ekle()` içinde ORCH-12 idempotency check'inden sonra:
  ```python
  if gorev and gorev.get("durum") in ("aktif", "review"):
      tb.gorev_guncelle(task_id, durum="plan", baslangic=None)
  ```
- **Gerekçe:** Tetik ↔ pano dual source-of-truth tutarsızlığı kaynağında kesilir. Ajan hiçbir zaman sessizce tetiksiz kalmaz.
- **D-77 doğrulama (KAHİN kararı 2026-09-20):** Fix üretimde doğrulandı — `git checkout --` ile yanlışlıkla silinen ihsan/utku tetikleri, guard sayesinde tekrar `tetik_ekle()` ile eklenince pano `plan` durumuna çekildi, `pano_bakim()` demote etmedi. `bekleyen_tetikler()` doğru döndü. **Ek bulgu:** `decision_log.jsonl` dosyasında UTF-8 dışı byte var (mojibake, pozisyon ~46494) — ayrı görev açılmalı (kodlama denetimi kapsamına girer).

### Tek Komut: `basla` (D-68 ikinci parça)
- **Eski akış:** `bak` → gözle task_id oku → `al --task-id X` → brifi ayrıca aç. Üç adım, elle kopyalama.
- **Yeni akış:** `python scripts/gorev_kutusu.py basla --ajan <ad>` — en yüksek öncelikli (P0 > P1 > ...) bekleyen görevi seçer, brifi ekrana basar, görevi alır. Tek komut.
- **Brif garantisi:** Talimat yoksa görev **alınmaz**, uyarı basılır (D-66 ile uyumlu). Talimat varsa `--zorla` ile `cmd_al`'a devredilir (brif zaten gösterildiği için ikinci kontrol gereksiz).
- **Ajan oturum protokolü:** Oturum başında tek komut yeterli; `bak` artık yalnız çoklu görev gözlemi için.

## Ajan Kimlik Bağlama (D-70 — KAHİN kararı 2026-09-20)
- **Bulgu:** `.clinerules`, `.cursorrules`, `.roorules` aynı boilerplate'ten kopyalanmış; hepsi `--ajan <AJAN>` placeholder'ı taşıyordu. Ajan kendi adını bilmediği için tahmin ediyordu (YASU → yanlışlıkla `utku` yazdı, UTKU'nun mailbox'ını tükettiği zannedildi).
- **Çözüm:** Her rule dosyasına sabit **KİMLİK** bloğu eklendi; `<AJAN>` yerine dosyanın sahibi olan ajanın adı doğrudan yazıldı (title önce, D-64 formatı):
  - `.clinerules` → yasu (araç: cline)
  - `.roorules` → ihsan (araç: roo)
  - `.cursorrules` → utku (araç: kilo/cursor)
- **Açık risk:** SALİH (araç: continue) için workspace içinde ayrı rule dosyası yok; `.continue/` boş. Global config kullanıyor olabilir — kimlik bağlama doğrulanmadı, izlenmeli.
- **Gerekçe:** Kimlik tahmin edilmez, dosyaya sabitlenir; başka ajanın postasını yanlışlıkla tüketme riski kapanır.
- **Rol Geçişi (D-71):** Orkestratör rolü unvan, ajan kimliği değil. İhsan şu an orkestratör; gelecekte başka ajan (copilot vb.) orkestrasyon üstlenirse, `.roorules` → yeni orkestratör ajanın aracı dosyasına taşınır. Kural dosyaları **ajan kimliğine** (kalıcı) bağlıdır, role (geçici) değil.

## Orkestratör Rol Geçişi (D-71 — KAHİN kararı 2026-09-20)
- **İlke:** Orkestratör **unvan** (görev panosu yönetimi, tetik kuyruğu, onay), **ajan kimliği** değil. Rol değişebilir.
- **Mevcut:** İhsan (ajan) = Orkestratör (rol).
- **Gelecekte:** copilot veya başka araç orkestrator olursa:
  1. `.roorules` sil (ihsan'ın işi).
  2. `.{yeni_araç}rules` yaz, yeni orkestratör'ün kimliğini koy (D-70 şablonu).
  3. `trigger.py` → `AJAN_TAKMA_ADLAR` yeni araç alias'ı ekle.
  4. Pano, tetik, handoff dosyaları **değişmez** (ajan-bağımsız).
- **Yasak:** Kural dosyaları role değil, kimliğe bağla. Ajan adı dosya adında doğrudan yazıl, tahmin etme.

## Pano İşleri Orkestrator'a Aittir (D-77 — KAHİN kararı 2026-09-20)
- **Kural:** Tüm pano bakımı, düzenleme, hata düzeltme işleri **İHSAN (Orkestratör)** tarafından yapılır.
  - Pano taraması, çakışma analizi
  - File lock temizliği ve yönetimi
  - Görev dağıtımı, durum yönetimi, onay işlemleri
  - Zincir oluşturma, devam ettirme
  - Bug fix'ler ve kural güncellemeleri (pano tarafında)
- **Diğer ajanlar (UTKU/YASU/SALİH)** yalnız **kendi domain görevlerini** yaparlar. Pano işleri başka ajana atanmaz.
- **Açık kural:** Bu durum AGENTS.md'de D-77 olarak kaydedilmiştir. Eski uygulamada pano görevleri ajanlar arası dağıtılıyordu; artık orkestratör tek ajan.
- **Gerekçe:** Pano yaşam döngüsü çekirdeği orkestratöre merkezi olduğu için çekişmeler, çakışmalar, stale temizleme işleri tek elden yönetilir.

## SALİH Otomatik Onay (D-78 — KAHİN kararı 2026-09-20)
- **SALİH'in P2 ve altı görevleri** `oto-nobetci` ile otomatik onaylanır. **P0/P1 elle** (orkestratör) onaylanır.
- Rapor (D-55) ve özeleştiri (D-67) zorunluluğu **kalkmaz**; otomatik onay yalnız onay adımını atlar.
- Makine kaynağı: `trigger.py::otomatik_onaylanabilir()` · `oto_nobetci.py::cmd_nobet()`.

## Tetik Değişince Sıfır-Bağlam Sayfa (D-79 — KAHİN kararı 2026-09-20)
- **Zincir görevleri** aynı sohbet sayfasında arka arkaya çalışabilir (session state korunur).
- **Tetik veya görev ID değiştiğinde** ajan **yeni sıfır-bağlam sayfa** açar. Eski sayfada kalırsa eski görevi tekrar dener.
- Gerekçe: 2026-09-20'de SALİH eski sayfada yanlış görevi tekrarladı; yeni sayfada doğru görevi aldı.
- Makine kaynağı: `gorev_kutusu.py::cmd_basla()`.

## Sprint Başlangıç Tablosu (D-72 — KAHİN kararı 2026-09-20)
- Her sprint/tur başlangıcında orkestratör KAHİN'e **tek standart tablo** verir. Başka biçim kullanılmaz.
- Sütunlar aynen: `Ajan` · `Yazılacak` · `Beklenen Sonuç`.
- `Yazılacak` = KAHİN'in ajan sohbetine **kopyalayacağı tam metin**.
- `Beklenen Sonuç` = ajanın ekranda göreceği **tam çıktı satırı** (tahmin değil, gerçek format).

| Ajan | Yazılacak | Beklenen Sonuç |
|---|---|---|
| YASU | `başla` | `[yasu] 1 bekleyen gorev: <TASK-ID> (P1)` |
| SALİH | `başla` | `[salih] 1 bekleyen gorev: <TASK-ID> (P2)` |
| UTKU | `bak` | `[utku] posta kutusu bos.` |

- Beklenen sonuç gerçekleşmezse ajan **iş yapmaz**, orkestratöre bildirir.

## `basla` Tüketicidir — Doğrulama İçin Kullanılmaz (D-69 — KAHİN kararı 2026-09-20)
- **Kural:** `basla` ve `al` **durum değiştiren** komutlardır; tetiği `alindi` yapar, görevi `aktif`e çeker. **Salt-okuma değildir.**
- **Yasak:** Orkestratör "çalışıyor mu bakayım" diye başka ajan adına `basla`/`al` çalıştırmaz. Çalıştırırsa görevi o ajan adına tüketir; ajan sonra baktığında posta kutusu **boş** görünür.
- **Doğrulama için:** yalnız `bak --ajan <ad>` (salt-okuma) kullanılır.
- **Kaza kurtarma:** `python scripts/tetik_geri_al.py <ajan>:<TASK-ID> ...` — tetiği `bekliyor`a, panoyu `plan`a geri çeker.
- **Gerekçe:** 2026-09-20'de SALİH ve YASU posta kutuları bu yüzden boş göründü; iki tetik elle geri alındı.

## Ajan Oturum Başında Komut Referansı (D-168 — KAHİN kararı 2026-09-20)
- **Yeni sohbet sayfasında** ilk komut **HER ZAMAN** `basla` olmalı: `python scripts/gorev_kutusu.py basla --ajan <AD>`.
- **Problem çözümü:** LLM'in yeni oturumda `bak` (posta kutusu gör), `al` (görevi al), `teslim` (iş bitir) komutlarını ilk kez öğrenmesi biraz zaman alıyor. Bir kez öğrenince sorun olmaz.
- **Çözüm:** Rule dosyaları (`.clinerules`, `.cursorrules`, `.roorules`) + `docs/AJAN_KOMUT_REHBERI.md` dökümanı + `cmd_basla()` çıktısında açık komut referansı.
- **Zorunluluk:** Ajan başkasına komut vermeden önce kendisi bu rehberi okur ve kuralları bağlamamış olsa bile, tüm oturum içinde komut referansı otomatik yüklenir.
- Makine kaynağı: `trigger.py::tetik_ekle()` · `.clinerules` / `.cursorrules` / `.roorules` · `docs/AJAN_KOMUT_REHBERI.md`.

## Ürün Sahibi Raporlama Formatı (D-55)
- KAHİN'e giden her özet: **kısa cümleler**, teknik olmayan dil, tablo.
- Bulgular 4 sınıfta renklendirilir: 🔴 kırmızı (acil/blokaj) · 🟡 sarı (dikkat) · 🟢 yeşil (tamam) · 🔵 mavi (bilgi/öneri).
- Mümkün olan her yerde **oran ve yüzde** verilir.

## Wireframe Onay Sunumu (D-56 — KAHİN kararı 2026-09-18)
- Her wireframe/tasarım belgesi **4 ana başlık + alt başlıklar** ile kurulur:
  1. **Şu an ne var** (AS-IS + problemler)
  2. **Ne olacak** (TO-BE çizim + değişim tablosu)
  3. **Nasıl yapılacak** (bileşen sözleşmesi, tokenlar, erişilebilirlik)
  4. **Onay için özet** (bağımlılıklar, kabul kriterleri, karar)
- Onay istenirken belge **bu 4 başlık üzerinden anlatılır**; KAHİN'e dosyayı açma yolu (`Ctrl+P` → ad → `Ctrl+Shift+V`) her seferinde verilir.
- Onaysız kod yazılmaz.

## Hitap (Demir Kural, D-49 — KAHİN kararı 2026-09-18)
- Ürün Sahibi'nin adı **KAHİN**. Tüm ajanlar (ihsan, utku, salih, yasu) ona **`KAHİN (Ürün Sahibi)`** diye hitap eder — büyük harfle.
- **"sahip", "kullanıcı", "efendim" kelimeleri YASAK.** Eski dokümanlardaki "sahip kararı" ifadeleri geçmiş kayıt; yeni metinlerde `KAHİN kararı` yazılır.

## Hitap Büyük Harf (Demir Kural, D-61 — KAHİN kararı 2026-09-18)
- Ekrana, rapora veya pano çıktısına yazılan **her ajan hitabı BÜYÜK HARF**: `İHSAN` · `UTKU` · `SALİH` · `YASU`. Gerekçe: KAHİN'in ekranda hızlı görmesi.
- Kanonik ad **küçük kalır** (dosya adı, `task_board.json` `sahip` alanı, `triggers/{ajan}.jsonl`, CLI `--ajan`). Yalnız **gösterim** büyür.
- Makine kaynağı: `trigger.ajan_goster()` — Türkçe `i` → `İ` dönüşümü yapar (`"salih".upper()` yanlış `SALIH` verir).

## Test Danışman — salih (D-59 / D-63 / D-181 — KAHİN kararı 2026-09-18 / 2026-09-20 / 2026-09-21)
- **İK Yönetim İlkesi:** Ajan personaları CV benzeri — zamanla rol, yetenek, yetki değişebilir. Sert kodlanmış kural değil, esnek referans.
- **salih bağımsız, uzun süreli, mekanik görevlere uzmanlaştı.** Test planlama, kapsamı ölçme, benchmark, bilgi tabanı, uyum denetimi.
- Raporlama ve teslim komutları → **YASU'ya yönlenir**. SALİH sadece plan/çerçeve/veri sunar.
- Görev ön eki: `TEST-` (test planlama/kapsamı), `ALTYAPI-` (benchmark/uyum). D-57 başlık kalıbı aynen geçerli.
- Posta kutusu: `data/orchestrator/triggers/salih.jsonl`. Normalizasyon `continue` → `salih`, `merve` → `salih`.
- Raporlama yardımcısı: `python scripts/rapor_olustur.py --task-id X --ajan yasu --ozet "..."` (SALİH plana çıktısını yazarken YASU ister ve teslim eder).
- salih orkestratör **değildir**; görev dağıtamaz (D-58 kapısı geçerli).
- Persona/detay SSOT: `docs/ajanlar/salih.md` (Release Authority tavsiye — nihai onay orkestratöre).

## Ajan Rol Tanımları (D-59/D-60/D-63)

| Kanonik Ad | Başlık | Görev Ön Eki | Tanım |
|-----------|--------|--------------|-------|
| **İHSAN** | Orkestratör | ORKESTRA- | Görev dağıtımı, onay, karar kaydı, ajan koordinasyonu. Son söz İHSAN'da. |
| **UTKU** | Üretim/Hacim | UI-, API-, VERI- | Kod yazma, refactoring, test, CI/CD. Hacim ve hız odaklı. |
| **SALİH** | Test Danışman | TEST-, ALTYAPI- | Bağımsız, mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi. Rapor yazma → YASU. |
| **YASU** | Denetim/Review | ORKESTRA- | Kod inceleme, güvenlik, mimari uyum, doküman doğrulama, raporlama, teslim işleri. |

## Orkestratör–KAHİN Tetik Protokolü (D-62 — KAHİN kararı 2026-09-19)
- **Tetik adı:** Orkestratör ajan ismini **BÜYÜK HARF**'ta görev atarken KAHİN'e bildirir (görev emri).
- **KAHİN yanıtı:** `<AJAN>'ya görev al yaz` — KAHİN tam ajan ismini yazarak görevi onaylar ve orkestratöre çalıştırma sinyali verir.
- **Aksiyonu:** Orkestratör `scripts/gorev_kutusu.py al --ajan <ad>` çalıştırır; görev kilitlenir, brif okunur.
- **Kaçırma durumu:** KAHİN mesajını kaçırırsa, orkestratör ajan ismini tekrarlı (N×) uyarı olarak gösterir; KAHİN farkına vardığında mesajı yazar.
- **Gerekçe:** İş takibinin görünür ve doğrulanabilir olması; atlatılan görev kalmasını önlemek.

## Kanonik Ad Geçişi (D-60 — KAHİN kararı 2026-09-18)
- Kanonik adlar Türkçe isimlere geçti. Eski adlar **takma ad** olarak korunur; pano ve tetik geçmişi bozulmaz.

| Eski ad | Yeni kanonik ad | Rol |
|---------|-----------------|-----|
| `roo`, `roo-code`, `orkestrator` | **`ihsan`** | Orkestratör |
| `kilo`, `kilo-code` | **`utku`** | Üretim/Hacim |
| `merve`, `continue`, `continue-ide` | **`salih`** | Test Danışman |
| `cline`, `clinebot`, `yasin` | **`yasu`** | Denetim/Review |
| `copilot` | — | **Kaldırıldı** (dış gözlemci) |

- Kod tarafı: `AJANLAR` + `AJAN_TAKMA_ADLAR` (`trigger.py`) tek doğruluk kaynağı; `gorev_at.py`, `gorev_kutusu.py`, `duzen.py` listeleri buradan türer (sabit kodlanmış ajan listesi yasak).
- Yeni çıktılarda yalnız **yeni kanonik adlar** yazılır; eski adlar okuma uyumluluğu içindir.

## Dil (Demir Kural)
- Kullanıcı iletişimi ve akıl yürütme %100 TÜRKÇE, kısa maddeler. Kod/teknik terimler İngilizce olabilir.

## Token Verimliliği — Demir Kural (D-48, KAHİN kararı 2026-09-17)
- Token tasarrufu için modelin **düşünme/akıl yürütme gücüne müdahale YASAK**: reasoning/thinking budget düşürme, `max_tokens` daraltma, iş kalitesini düşüren zayıf model seçimi.
- Hedef dörtlü: **temiz kod yazımı · kaliteli iş · verimlilik planlaması · maliyet avantajı**.
- İzin verilen tasarruf: bağlam seçimi, görev brief'i, gereksiz keşif/okuma eleme, çıktı tekrarını azaltma (K1-K6).
- Takip: `docs/raporlar/roo_code/TAKIP.md` (sürekli güncellenir).

## Genel Kod/Dosya Kuralları
- Gizli bilgiler `.env`'de; hardcoded secret yok. Tüm dosyalar UTF-8 (BOM yasak; PS `Out-File -Encoding utf8` kullanma).
- Silme/taşıma kullanıcı onayıyla; mevcut temel üzerine geliştir. Ayrıntı: AJAN_DETAY §18.
- PEP 8, tip notları, birim test; test edilmemiş iş teslim edilmez.

## Proje Sınırı (ZORUNLU)
- Her şey yalnız repo kökü içinde; üst dizine yaz/taşı/kopyala YASAK. Geçici: `data/_tmp/` veya `_trash/`, iş bitince sil.
- Dışarıdaki proje öğesini SİLME, içeri TAŞI. Ürün Sahibi notu (aynen): "Dizinin dışında projeye ait hiçbir şey görmek istemiyorum." Ayrıntı: AJAN_DETAY §19.

## Servis Kuralları
- **Streamlit restart:** UI dosyasına dokunan ajan teslimden ÖNCE `python scripts/streamlit_restart.py` çalıştırır (fileWatcherType=none). Ayrıntı: AJAN_DETAY §20.
- **FastAPI 8000 Docker'da:** API değişince `docker compose up -d --build api` + curl doğrulama. Ayrıntı: AJAN_DETAY §12.
- **VPN:** ağ hatalarında VPN notu düş; kritik işlemlerde kapatmadan önce sor. Ayrıntı: AJAN_DETAY §13.

## Marka Terminolojisi (öz)
- Huginn 🦅 = müşteri (8000, `huginn_`) · Muninn 🛡️ = iç ekip (8501, `muninn_`) · Odin ⚡ = çekirdek (`odin_`).
- İsimler çevrilmez/bölünmez; teknik kimliklerde (`huginn` db/repo) değişmez. Yasak: Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın. Ayrıntı: AJAN_DETAY §11.
- Marka kiti (pazarlama/web/logo/marka metni üretimi): `docs/brand/` — D-44/D-45 kapsam ayrımı için AJAN_DETAY §11.
- Harici ajan etkileşimi orkestratör + `workspace/external/{agent_id}/` üzerinden; kök erişim yok. Ayrıntı: AJAN_DETAY §8.

## Sözlük (Lexicon) — D-29/D-30/D-47
> Bu bölüm proje genelinde kullanılan terimlerin, kısaltmaların ve ajan rollerinin tek kaynaklı tanımını tutar. D-29/D-30 kural satırı + D-47 karar dayanağıyla eklendi.

### Ajanlar ve Roller
| Terim | Tanım |
|-------|-------|
| **utku** (araç: kilo) | Üretim/hacim ajanı — kod yazma, refactoring, test, CI/CD. Kilitli dosyalarda çalışır. |
| **yasu** (araç: cline) | Denetim/review ajanı — kod inceleme, güvenlik, mimari uyum, doküman doğrulama. |
| **ihsan** (araç: roo) | Orkestratör — görev dağıtımı, onay, commit, push, karar kaydı, ajan koordinasyonu. Son söz ihsan'da. |
| **salih** (araç: continue) | Test Danışman — mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi. Rapor → YASU. |
| **orkestrator** | `ihsan` ile eşanlamlı; görev panosu yönetimi, tetik kuyruğu, kilit takibi. |
| **oto-nobetci** | Otomatik onay/teslim işleyen arka plan süreci (`scripts/oto_nobetci.py`). P2 ve altı görevleri onaylar; P0/P1 elle onay (D-46). |

### Görev Yaşam Döngüsü Terimleri
| Terim | Tanım |
|-------|-------|
| **bekliyor** | Tetik kuyruğunda, henüz ajan tarafından alınmamış görev. |
| **alindi** / **aktif** | Ajan `gorev_kutusu.py al` ile görevi üstlendi; kilitler verildi. |
| **teslim** | Ajan `gorev_kutusu.py teslim` ile işi bitirdi; `review` durumuna geçer, onay bekler. |
| **review** | Kontrolör (roo) incelemesi bekleyen görev. |
| **done** | Onaylandı; kilitler bırakıldı, tetik `done`, zincir varsa sonraki tetiklendi. |
| **iptal_stale** | Bayat/çalışılmayan görev/tetik; bakım ile temizlenir. |
| **zincir_bekleme** | Zincirdeki önceki görev bitmeden bekleyen sonraki görev. |
| **handoff** | Teslim kaydı: `data/orchestrator/handoff.jsonl` — kim ne zaman ne teslim etti. |

### Teknik Kısaltmalar ve Terimler
| Terim | Tanım |
|-------|-------|
| **SSOT** | Single Source of Truth — tek doğruluk kaynağı (V9 = teknik SSOT, V10 = yönetim). |
| **MVP** | Minimum Viable Product — şu anki hedef kapsam. |
| **P0/P1/P2** | Öncelik seviyeleri: P0=kritik (blokaj), P1=yüksek (güvenlik/çekirdek), P2=orta, P3=düşük. |
| **BOM** | Byte Order Mark — UTF-8 dosyalarda yasak (kodlama denetimi). |
| **mojibake** | Karakter kodlama bozulması (Türkçe karakterler bozulmuş). |
| **NUL** | Null byte (dosya içinde yasak). |
| **AST** | Abstract Syntax Tree — statik analiz/testlerde kullanılır. |
| **monkeypatch** | `pytest` fixture'i; elle `MonkeyPatch()` oluşturulmaz (D-47). |
| **fileWatcherType=none** | Streamlit dosya izleme kapalı (restart script'inde). |
| **rate-limit** | API isteği sınırlaması (IP bazlı, dakikada N istek). |
| **SSE** | Server-Sent Events — canlı veri akışı (admin_realtime). |
| **DLQ** | Dead Letter Queue — işlenemeyen mesaj kuyruğu. |
| **MRR/ARR** | Monthly/Annual Recurring Revenue — executive dashboard metrikleri. |
| **churn** | Müşteri kaybı oranı. |
| **tenant** | Çoklu müşteri (multi-tenant) yapısındaki bir müşteri/kurum. |

### Dosya ve Dizin Kısaltmaları
| Yol | Anlamı |
|-----|--------|
| `data/orchestrator/` | Görev panosu, tetikler, handoff, karar defteri, raporlar. |
| `data/orchestrator/task_board.json` | Merkezi görev panosu (tek kaynak). |
| `data/orchestrator/triggers/{ajan}.jsonl` | Ajanın tetik kuyruğu (bekleyen/alınan/teslim/done). |
| `data/orchestrator/handoff.jsonl` | Teslim kayıtları (ajan, task_id, özet, çıktılar, tarih). |
| `data/orchestrator/decision_log.jsonl` | Karar kayıtları (D-XX numaralı). |
| `scripts/gorev_kutusu.py` | Ajan posta kutusu + kontrolör onay CLI. |
| `scripts/oto_nobetci.py` | Otomatik onay/zincir devam süreci. |
| `scripts/kodlama_denetim.py` | BOM/NUL/mojibake/sozdizimi denetimi. |
| `scripts/streamlit_restart.py` | UI değişince Streamlit güvenli restart. |
| `src/company_master/` | Çekirdek Python paketi (odın). |
| `web_dashboard/` | Streamlit admin paneli (muninn, port 8501). |
| `web_app.py` | FastAPI müşteri API'si (huginn, port 8000, Docker). |
| `docs/brand/` | Marka kiti (pazarlama/web/logo SSOT). |
| `src/company_master/ui/tokens.py` | Ürün UI tasarım tokenları (Indigo #6366f1 SSOT, D-45). |

### Marka ve Ürün Kimliği
| Terim | Tanım |
|-------|-------|
| **Huginn** 🦅 | Müşteri tarafı (port 8000, `huginn_` öneki, DB `huginn`). |
| **Muninn** 🛡️ | İç ekip/admin paneli (port 8501, `muninn_` öneki). |
| **Odin** ⚡ | Çekirdek/kütüphane (`odin_` öneki). |
| **Yasak yazımlar** | Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın. |

### Süreç Kuralları (Hızlı Referans)
- **ORCH-08**: Görev yaşam döngüsü — `bak` → `al` → brif → iş → `teslim` → `review` → `onay` → `done`.
- **S-07 (D-46)**: Otomatik onay yalnız P2 ve altı; P0/P1 roo elle onaylar.
- **D-47**: `pytest.MonkeyPatch` elle oluşturulmaz; her zaman `monkeypatch` fixture.
- **Kilit disiplini**: `gorev_ekle(..., dosyalar=[...])` ile kilitle, bitince `lock_birak`.
- **Commit**: Sabah roo/KAHİN; ajanlar commit ATMAZ.
- **UI restart**: `python scripts/streamlit_restart.py` (fileWatcherType=none).
- **API restart**: `docker compose up -d --build api` + curl doğrulama.

## Obsidian Vault Merkezi Yönetim (D-169 — KAHİN kararı 2026-09-20)
- **Vault kökü = `Huginn Data Insights/` (V10 ana branch).** Tüm `.md` dosyaları buradan sayılır; Obsidian graph, orphan tespiti, cross-reference kontrolü burada yapılır.
- **`AI proje v1/` submodule DEĞİLDİR.** Submodule kullanımından dönüldü (ürün sahibi beyanı 2026-09-20). Eski sürüm dizinidir; `.gitmodules` kaydı geçersiz, temizlenecek. Vault kapsamı dışında tutulur. **Netleştirme (2026-09-24, YA-01 kapanışı):** dizinin kanonik kopyası ana depoda gömülüdür ve burada değiştirilir; uzaktaki `yassuacohen-hub/AI-proje-v1` deposu arşiv/salt-okunurdur (işaretçi: `AI proje v1/README.md`).
- **Obsidian `userIgnoreFilters` (`.obsidian/app.json`):** Graph ve arama sınırlaması için native ayar (silme değil, geri alınabilir):
  ```json
  "userIgnoreFilters": [
    ".venv/", ".kilo/", ".agents/", ".claude/", ".cursor/", ".continue/",
    ".kombai/", ".vscode/", ".pytest_cache/", "node_modules/", ".git/",
    "AI proje v1/", "data_worktree/"
  ]
  ```
  Etki: 4442 md → ~925 md (vault yapısı temiz).
- **Orphan nod (916 dosya):** Silme YASAK. Sprint 2'de VAULT-ORPHAN-INCELEME görevinde sınıflandırılacak (silinecek, tutulacak, arşivlenecek).
- **Dosya boyutu yönetimi (Ponytail: rung 1-3):**
  - `.kilo/` 280 MB: Kilo Code checkpoint/session geçmişi. Rotasyon: `.kilo/checkpoints/` max 50 MB (tool native ayarı; kod değil).
  - `backups/` 31.4 MB: pg_dump yedekleri. Politika: son 3 yedek tutma. **Aynı politika `data/orchestrator/task_board*yedek*` ve `*backup*` dosyalarını da kapsar** — makine karşılığı: `gorev_kutusu.py bakim --rapor` üçten fazlasında uyarır.
  - Kök geçici dosyalar (`_gen64.txt`, `step1.py`, `_teshis_tmp.py`): `.gitignore` yasaklıyor; diskten da silinmeli (ADMIN-KOK-TEMIZLIK-02).
- **Vault tarama script:** `scripts/vault_tarama.py` (stdlib-only: `pathlib`, `collections`, `hashlib`, `json`, `re`).

## Worktree Merkeze Taşındı (D-170 — KAHİN kararı 2026-09-20)
- **Karar:** `worktree klasoru/` içeriği merkeze (`Huginn Data Insights/`) alındı. Tek kök, tek vault, tek SSOT.
- **Taşınan:**
  - `worktree klasoru/data/` → `Huginn Data Insights/data_worktree/` (ham kopya, merge bekliyor)
  - 3 vault raporu → `Huginn Data Insights/data/orchestrator/` (VAULT-TARAMA-01 `.md`+`.json`, VAULT-BIRLESTIME-PLAN-01)
- **`worktree klasoru/` silinmez.** Git worktree olarak bağlı (`worktree/roo-rest-sonrası-admin-panel-UX-v2`); içinde sözlük + kullanım kılavuzu dosya yapısı var. Kaynak korunur, geri alınabilir.
- **NOT:** D-170'teki senkronsuzluk tablosu ORCH-SENKRON-01 (D-171) ile kapatıldı; D-172 kalıcı kuralı yazdı.

## Otorite Kaynağı: Worktree Klasoru (D-172 — KAHİN kararı 2026-09-21, D-191 ile genişletildi 2026-09-23)

> 🚫 **EMEKLİ — D-223 (2026-09-27) ile yürürlükten kaldırıldı.** Aşağıdaki kurallar **uygulanmaz**.
> Güncel kural: **[D-223](#tek-otorite-d-223)** — `Huginn Data Insights/` hem yazma otoritesi hem graph canonical.
> Bu bölüm tarihsel kayıt olarak korunur (D-002 silme yasağı), **talimat olarak okunmaz**.

- **Karar:** `worktree klasoru/` = **yazma otoritesi (SSOT)**. `Huginn Data Insights/` = senkronize salt-okunur ayna (GRAPH ikinci katman).
- **Gerekçe:** Worktree aktif geliştirme dalı (git worktree bağlı), orkestratör doğrudan burada çalışır. Kullanım kılavuzu + sözlük çalışması burada. Merkez git main tarafı, okuma/arşiv.
- **Yazma sırası (ZORUNLU):**
  1. Yeni karar (`D-XX`) → `worktree klasoru/data/orchestrator/decision_log.jsonl`
  2. Görev güncellemesi (durum/sahip/not) → `worktree klasoru/data/orchestrator/task_board.json`
  3. Task ID tanımı + field şeması → GRAPH kanonik kaynağı (D-191, okuma-yazma D-177'de açık)
  4. Kural dosyaları (`AGENTS.md`, `ANA_KURALLAR.md`, `AGENT_SYNC.md`, `.clinerules`, `.cursorrules`, `.roorules`) → worktree önce
  5. Senkron: worktree → merkez (kopya/override)
- **Çatışma çözümü:** Merkez vs worktree farkında **worktree kazanır**. Yedek alınır, silme yok.
  - `decision_log.jsonl`: append-only birleştirme (`decision_id` bazlı, kayıp yok)
  - `task_board.json`: worktree override, yedek zorunlu (`task_board.json.yedek_<tarih>`)
  - GRAPH canonical: eski task ID → yeni ID migration trail (D-191, D-60 uyumlu)
- **Senkron araçları (mevcut, elle çalışır):**
  - `python scripts/senkron_fark.py` — karar defteri farkı
  - `python scripts/senkron_append.py` — eksik satır ekle
  - `python scripts/pano_merge.py` — pano birleştir (yedekli)
  - `python scripts/id_migration.py` — task ID yeniden adlandırma (D-191)
- **Ponytail rung 4 — otomasyon eksik:** post-commit git hook + zamanlanmış görev yazılmadı. Şu an elle tetiklenir. Ekleme zamanı: senkron gecikmesi günde 1'den fazla soruna yol açarsa.

## Graph Canonical vs Yazma Otoritesi (D-172 / D-177 Netleştirme — D-191 ile genişletildi 2026-09-23)

> 🚫 **EMEKLİ — D-223 (2026-09-27).** İki katmanlı ayrım kaldırıldı; tek ağaç kaldı.
> Güncel kural: **[D-223](#tek-otorite-d-223)**. Bu bölüm tarihsel kayıt.

İki karar **çelişmiyor**, farklı katmanlara ait:

| Karar | Tanım | Katman | Anlamı |
|-------|-------|--------|--------|
| **D-172** | `worktree klasoru/` = yazma otoritesi | **YAZMA / SSOT** | ~~Kod ve doküman buraya yazılır.~~ **EMEKLİ (D-223).** |
| **D-177** | GRAPH task ID + field schema = kanonik okuma | **GRAPH / CANONICAL** | ✅ **Yürürlükte.** Obsidian link çözümlemesi, orphan tespiti, backlink sayımı, task field tanımları `Huginn Data Insights/` altında kanonik. |
| **D-191** | id-migration redirect (eski ID → yeni ID) | **MIGRATION / AUDIT** | ✅ **Yürürlükte.** Task ID yeniden adlandırılırsa eski ID silinmez; redirect trail + D-60 uyumlu geçiş kuralı uygulanır. |

<a id="tek-otorite-d-223"></a>

## Tek Otorite: Vault (D-223 — KAHİN kararı 2026-09-27)

- **Karar:** `Huginn Data Insights/` = **hem yazma otoritesi hem graph canonical**. Tek ağaç, tek SSOT. D-172 emekli.
- **Gerekçe — 5 bağımsız ölçüm (2026-09-27):**
  1. **Git bağı yok.** `worktree klasoru\.git` mevcut değil, `git worktree list` klasörü listelemiyor. D-172'nin "git worktree bağlı" gerekçesi geçersiz.
  2. **Obsidian zaten dışlıyor.** [`.obsidian/app.json`](.obsidian/app.json:15) `userIgnoreFilters` içinde `"worktree klasoru/"` var — hem vault hem kök yapılandırmasında. Graph o ağacı hiç okumuyor; D-177 fiilen zaten tek canonical'dı.
  3. **İçerik SSOT değil.** Klasörde 5 dosya: 3'ü 2 byte boş JSON, 2'si tek seferlik dump betiği.
  4. **Gerekçedeki dosyalar taşınmış.** D-172'nin dayandığı "sözlük + kullanım kılavuzu" (`OPERASYON_KILAVUZU.md`, `VAULT_HARITA.md`, `GOREV_PANOSU_KULLANIM_KILAVUZU.md`) D-187 Faz 2'de `data/orchestrator/backups/D-187_faz2_2026-09-22/worktree_klasoru_kopya/` altına alınmış.
  5. **Canlı nüsha vault'ta ve daha gelişmiş.** `GOREV_PANOSU_KULLANIM_KILAVUZU.md`: yedekte 150 satır, [`docs/`](docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md:1) altında 266 satır. Yazma faaliyeti vault'ta sürmüş.
- **Uygulama:** `worktree klasoru/` → `_ARSIV_worktree_kalinti_2026-09-27/` (D-002 silme yasağı: silme değil taşıma). Üst repo commit `a02fd87`.
- **Arşivdeki 5 dosyanın 3'ü git'te izleniyor, 2'si değil.** Sebep: kök `.gitignore:15` kuralı `_*.py`, arşivdeki `_dump_charts.py` / `_dump_receiver.py` adlarını yakalıyor. Kayıp yok — dosyalar **diskte mevcut** ve eski yollarıyla **git geçmişinde** duruyor (`git show 62f0c52:"worktree klasoru/_dump_charts.py"`). Bu bir kusur değil, beklenen davranış; not düşülmesinin sebebi ileride "arşivde 5, git'te 3" çelişkisinin yanlış alarma yol açmaması.
- **Tarihsel referanslara dokunulmaz.** 103 markdown dosyasında `worktree klasoru/` geçiyor; bunlar geçmiş rapor ve karar kaydıdır. Geriye dönük düzeltme **yapılmaz** (D-60 kanonik ad geçişi + D-191 redirect ilkesi: geçmiş yeniden yazılmaz).
- **Mandal:** [`tests/test_kok_izin_listesi.py`](tests/test_kok_izin_listesi.py:1).

### D-187 Geriye Dönük Kayıt (D-223 ile birlikte yazıldı)

- **Tespit edilen kusur:** D-187 Faz 2 (2026-09-22) `worktree klasoru/` içeriğini yedeğe taşıdı, ancak **AGENTS.md'ye karar olarak yazılmadı**. Bu yüzden D-172 beş gün boyunca "yürürlükte" göründü.
- **Ders:** Dosya taşıyan her iş, aynı commit'te D-NN kaydı üretmek zorundadır. Kayıtsız taşıma = kural erimesi.
- **Kurtarılan:** [`docs/OPERASYON_KILAVUZU.md`](docs/OPERASYON_KILAVUZU.md:1) (668 satır, ürün sahibi el kitabı) yedekten canlı ağaca geri alındı; içindeki 13 eski yol vault yoluna düzeltildi.

## Kırmızı Test = Ölçülmeden Görev Açılmaz (D-224 — KAHİN kararı 2026-09-27)

- **Kural:** Başarısız test, **hata mesajı okunmadan** panoya görev olarak yazılmaz. Görev kaydının `not` alanı ölçümü (kaç dosya, hangi yol, hangi assert) içermek zorundadır. "Şu dosya eksik" gibi dayanaksız teşhis yasak.
- **Tetikleyen hata — kendi hatam:** 2026-09-26'da 20 kırmızının sebebi "migration down dosyaları yok" diye kaydedildi. Ölçüm yapılınca **yanlış çıktı**: down dosyaları var, üstelik üç ayrı adlandırma kalıbında:
  1. `migrations/down/0001_core.down.sql` biçimi — 16 adet,
  2. `migrations/0016_*.down.sql` biçimi — 3 adet, kökte,
  3. testin beklediği `migrations/down/0017_user_activity_log.sql` biçimi — karşılığı yok.
  Yani sorun **eksiklik değil, ad/yol çatallanması**. Yanlış teşhisle açılacak görev yanlış işi yaptıracaktı.
- **20 kırmızının gerçek dağılımı:** 14'ü ölçüldü ve 3 göreve bağlandı (VERI-04 şema/ad standardı, API-07 rota envanteri + `match` girdi doğrulaması, UI-11 başlık kalıbı). Kalan **6'sı tek başına çalıştırıldığında yeşil** → suite içi durum sızıntısı; bu ayrı bir borç, üçünün kapsamına karıştırılmaz.
- **Güvenlik notu:** API-07 sadece envanter işi değildir. `/api/match?buyer_id=<geçersiz>` ucu 404 yerine `NoneType` hatası veriyor; bu güven sınırında **girdi doğrulama boşluğudur**, basitleştirilerek geçilmez.
- **Mandal:** [`tests/test_pano_tekligi.py`](tests/test_pano_tekligi.py:60) — `plan` durumundaki her görev Markdown panoda görünmek zorunda; üç görev eklenirken bu test kırmızı verip kaydı zorladı (kural çalışıyor).
- **Düzeltme (2026-09-27):** Bu kaydın ilk halinde görev kimliği `SEMA-01` yazılmıştı; `SEMA` kanonik ALAN değil (bkz. D-225). Kanonik kimlik **VERI-04**.
- **Ek (2026-09-27) — DEVRALINAN ÖLÇÜM ÖLÇÜM DEĞİLDİR:** Kural yalnız teşhise değil, **başka bir oturumdan gelen sayıya** da uygulanır. Görev brifinde yazan kırmızı sayısı/dosya listesi, iş açmadan önce **yeniden ölçülür**. Tetikleyen olay: bir brif "14 failed; VERI-04 (9) + UI-11 (2) + API-07 (2); 3 down dosyası kökte yanlış klasörde; `migrate.py` bunları ileri migration sanıyor" diye devredildi. Yeniden ölçüm: süit **4337 passed / 0 failed**, kökte `.down.sql` **yok** (21 up ↔ `down/` altında 21 karşılık), [`migrate.py`](src/company_master/schema/migrations/migrate.py:75) glob değil `schema_versions.json` defterini okuyor → üretim bugu şüphesi **çürük**. Dört görevin dördü de `9354375`, `a621945`, `7f56b96` ile kapanmıştı. Ölçmeden başlansa kapalı iş yeniden yapılacak, gerçek açık iş (**VERI-02** OSB ihale izleyici, **VERI-03** proxy rotasyonu — teslim dosyaları hâlâ yok) sıra beklemeye devam edecekti.
- **Ölçüm maliyeti bahane değildir:** Tam süit ~155 s. Yanlış teşhisle yapılan iş bundan pahalıdır.
- **Mandal (negatif kontrolü yapıldı 2026-09-27):** [`tests/test_migration_down_standardi.py`](tests/test_migration_down_standardi.py:19) — kökte sahte `9999_negatif_kontrol.down.sql` yaratıldı, test kırmızı verdi (`down dosyalari 'down/' altina tasinmali`), dosya silindi, 3 passed. [`tests/test_karar_numara_tekligi.py`](tests/test_karar_numara_tekligi.py:64) — ad ve H1 ihlali tek tek eklendi, tavanlar (35/24) tam sınırda olduğu için ikisi de yakalandı (`36 > 35`, `25 > 24`), geri alındı, 6 passed.

## D-57 Kalıcı Panoda da Geçerli (D-225 — KAHİN kararı 2026-09-27)

- **Kural:** D-57 kimlik/başlık kalıbı yalnızca görev açılışında değil, `data/orchestrator/task_board.json`'un **kalıcı halinde** de geçerlidir. Panodaki her **aktif** (done/archive/iptal dışı) kayıt, giriş kapısıyla aynı doğrulayıcıyı geçmek zorundadır. Kapanmış kayıtlar tarihsel veridir, geriye dönük kırmızılaştırılmaz.
- **Tetikleyen hata — kendi hatam:** D-224 görevlerini panoya yazarken `gorev_at.py` yerine JSON'a doğrudan yazdım. `SEMA-01` / `[SEMA] ...` kimliği panoya girdi; `SEMA` kanonik ALAN listesinde (`UI, API, VERI, TEST, DOC, ALTYAPI, ORKESTRA`) yok. Başlıklarda ayrıca `->` ASCII oku kullanılmıştı, kalıp `→` istiyor.
- **Asıl ders — yeşil test yanlış güven verir:** `pano_denetim.py` hata=0 dedi, `test_naming_audit.py` 9 yeşil verdi, hiçbiri yakalamadı. Doğrulayıcı sağlamdı ama **yalnızca giriş kapısına** bağlıydı; kapıyı atlayan yazım denetimsiz kaldı. Bir kural giriş kapısında zorlanıyorsa, o kuralın **kalıcı durumu** da ayrıca denetlenmelidir.
- **Uygulama:** Görev yazımı `python scripts/gorev_at.py ...` üzerinden yapılır; JSON'a elle yazmak yasak değil ama mandal artık ihlali yakalar.
- **Mandal:** [`tests/test_pano_d57_kalici.py`](tests/test_pano_d57_kalici.py:47) — giriş kapısındaki `_d57_dogrula` yeniden kullanılır (kural kopyalanmaz), ALAN öneki kanonik listeye karşı denetlenir, 3 bilinen ihlalle **negatif kontrol** yapılır. Yazıldığı anda 5 aktif kayıtta ihlal buldu; düzeltme sonrası 5 test yeşil.

## Test Modülü Global Durumu Bozamaz (D-226 — KAHİN kararı 2026-09-27)

- **Kural:** Bir test modülünün **modül seviyesinde** (import anında çalışan gövdesinde) süreç genelindeki durumu değiştirmesi yasaktır. Yasaklı örnekler: `logging.disable()`, `logging.basicConfig()`, `logging.shutdown()`. Bu tür bir müdahale gerekiyorsa fixture içinde yapılır ve `finally` ile geri alınır; log gözlemi için `caplog` kullanılır.
- **Gerekçe (ölçüm):** pytest, toplama (collection) aşamasında **tüm** test modüllerini import eder. Modül gövdesindeki çağrı böylece süitin en başında çalışır ve hiçbir yerde geri alınmaz — dosyanın kendi sınırını aşıp bütün süiti etkiler.
- **Tetikleyen olay:** [`tests/test_dashboard_nav.py`](tests/test_dashboard_nav.py:46) Streamlit "missing ScriptRunContext" uyarısını bastırmak için modül seviyesinde `logging.disable(logging.WARNING)` çağırıyordu. Sonuç: `test_error_handling.py`'deki 3 test **tek başına yeşil, tam süitte kırmızı**. Ölçüm: satır kaldırıldığında gürültü geri gelmedi ve 3 kırmızı yeşile döndü — bastırma zaten gereksizdi.
- **Asıl ders — "izole yeşil" teşhis değildir, semptomdur:** Bir test tek başına geçip süitte düşüyorsa mesele o testte değil, **başka bir modülün bıraktığı durumdadır**. Kaynağı bulmadan o teste dokunmak yanlış görev açar (bkz. D-224). Kök neden, süreç genelinde paylaşılan durum (logging, env, `sys.modules`, singleton, monkeypatch artığı) aranarak bulunur.
- **Mandal:** [`tests/test_global_logging_kirlenmesi.py`](tests/test_global_logging_kirlenmesi.py:71) — iki katmanlı: **kaynak** katmanı AST ile tüm `tests/test_*.py` dosyalarının modül gövdesini tarar (fonksiyon/fixture içi serbest), **davranış** katmanı süit çalışırken `logging.root.manager.disable == 0` olduğunu doğrular. Negatif kontrol yapıldı: satır geri eklendiğinde mandal 2 testle yakaladı.
- **Etki:** Tam süit kırmızı sayısı **20 → 17 → 14**. Kalan 14 kırmızı tam olarak 3 açık göreve denk düşüyor (API-07: 2, VERI-04: 9, UI-11: 3); süitte başka sızıntı yok.

## Hub-Önce Okuma (D-185 — KAHİN kararı 2026-09-22)
- **Kural:** Bir konuda (osint, veri kalitesi, admin panel, müşteri paneli, araç/script, plan/rapor, teknik dok, orkestrasyon/ajan) çalışmaya başlamadan önce önce ilgili `Huginn Data Insights/hubs/*_HUB.md` dosyası okunur, oradan 2-3 hedef dosyaya inilir.
- **Gerekçe:** Hub, konunun küçültülmüş haritasıdır; doğrudan geniş klasör taraması veya çok sayıda dosya okuması yerine hub üzerinden hedefe gitmek token maliyetini düşürür.
- **Sıra:** hub bulunamazsa (konu hub'da yok) `search_files` ile ara; yeni bir hub açma kararı orkestratöre sorulur.

## Yeni Belge = Yeni Bağlantı (D-186 — KAHİN kararı 2026-09-22)
- **Kural:** Vault içine (`Huginn Data Insights/` altına) yeni `.md` belgesi üreten her ajan, aynı işlemde belgeyi ilgili konu hub'ına (`hubs/*_HUB.md`) en az bir madde olarak ekler. Backlink Obsidian tarafından otomatik üretilir, elle yazılmaz.
- **Gerekçe:** Orphan nod birikimini kaynağında önler; GRAPH-HUB-EXPAND tarzı toplu temizlik görevlerine ihtiyacı azaltır.
- **İstisna:** `data/orchestrator/` yürütme raporları ve geçici (`data/_tmp/`) dosyalar kapsam dışı — bunlar zaten hub'lara alınmıyor (bkz. hub üretim notları).

## Önce Pano, Sonra Tetik (D-188 — KAHİN kararı 2026-09-23)
- **Kural:** Her görev **önce** `data/orchestrator/task_board.json`'a yazılır (brif dosyası diskte hazır, `talimat` alanı brif yolunu gösterir), **sonra** ajan tetiği (`triggers/{ajan}.jsonl`) atılır. Ters sıra yasak.
- **Gerekçe:** Tetik panoda karşılığı olmayan göreve işaret ederse ajan `al` komutunda `HATA: Görev panoda bulunamadı` alır; iş başlamadan durur (2026-09-23 AGENTS-MERGE-UU / VAULT-CLEANUP-BATCH olayı).
- **Tek komut:** `python scripts/gorev_atama_otomatis.py --task-id <ID> --ajan <name>` (D-87) bu sırayı zaten uygular; elle tetik yazmak yerine bu kullanılır.
- **Doğrulama:** Tetik atmadan önce `python scripts/gorev_at.py pano` ile görevin panoda görünmesi teyit edilir.
- **Bağlantı:** D-66 (brifsiz atama yasak) ve D-68 (tetik ↔ pano tutarlılığı) ile birlikte uygulanır.

## Kök AGENTS.md Kural Taşımaz (D-189 — AGENTS-MERGE-UU, 2026-09-23)
- **Kural:** Depo kökündeki `AGENTS.md` yalnızca (1) `n8n-as-code` üretilmiş blok ve (2) bu dosyaya işaretçi içerir. Ajan kuralları yalnızca `Huginn Data Insights/AGENTS.md` içinde yaşar.
- **Gerekçe:** İki dosyada kural kopyası tutmak sürüm kayması ve merge çatışması üretiyordu; tek SSOT bunu kaynağında keser.
- **n8n bloğu:** `<!-- n8n-as-code-start -->` … `<!-- n8n-as-code-end -->` arası elle düzenlenmez; `npx --yes n8nac update-ai` üretir.
- **Teknik sebep (TUR-B2, 2026-09-24):** Depo kökü (`c:\Huginn Data Projesi`) git deposu **değildir**; kökteki `AGENTS.md` versiyonlanmaz, klonla taşınmaz ve sunucu değişiminde kaybolur — bu yüzden kural taşıyamaz, yalnızca işaretçi olabilir.

## İlgili Nodlar (GRAPH-FIX-02 Backlink + GRAPH-HUB-EXPAND Kategori Hub'ları)

### GRAPH-FIX-02 Büyük İzole Nod Backlink'leri

- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/docs/CALISMA_GUNLUGU]]
- [[Huginn Data Insights/AI proje v1/docs/CALISMA_GUNLUGU]]
- [[Huginn Data Insights/scripts/_tavily_skill_incele]]
- [[Huginn Data Insights/data/orchestrator/VAULT-TARAMA-02_analiz_2026-09-20_orkestrator]]
- [[Huginn Data Insights/data/skills/supabase/AGENTS]]
- [[Huginn Data Insights/data/skills/supabase/CONTRIBUTING]]
- [[Huginn Data Insights/data/skills/supabase/README]]
- [[Huginn Data Insights/data/skills/supabase/skills/supabase/SKILL]]

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

### GRAPH-HUB-EXPAND Kategori Hub'ları (200 Orphan Bağlantı)

**Tur 2 Plan C:** 627 orphan baseline → 5 kategori hub oluşturuldu, 200 dosya wikilink ile bağlandı. Hub'lar Obsidian backlink yoluyla ters-referans gösterir.

- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] — 48 dosya
- [[Huginn Data Insights/hubs/OSINT_INDEX]] — 10 dosya
- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] — 48 dosya
- [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] — 47 dosya
- [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] — 47 dosya

### GRAPH-INDEX-BUILD Tür-Bazlı Index'ler (319 Orphan Bağlantı)

**Tur 3 Plan C:** 431 orphan baseline → 4 tür-bazlı index oluşturuldu (Teknik/OSINT/Plan/Rapor), 319 dosya sınıflandırılıp wikilink ile bağlandı. Dosya adı, klasör pattern, YAML frontmatter tags yoluyla otomatik sınıflandırma.

- [[Huginn Data Insights/indexes/teknik_index]] — 119 dosya (mimari, kod, config, design, guide)
- [[Huginn Data Insights/indexes/osint_index]] — 10 dosya (istihbarat, veri toplama, araştırma, vendor)
- [[Huginn Data Insights/indexes/plan_index]] — 38 dosya (roadmap, sprint, gorev panosu, milestone)
- [[Huginn Data Insights/indexes/rapor_index]] — 152 dosya (denetim, metrik, analiz, rapor çıktıları)

## Ajan Chat Sistemi (D-192 — KAHİN kararı 2026-09-23)

Ajanlar arasında bildirilen sorunlar ve çözüm önerilerinin merkezi takibi. Orkestratör ve KAHİN dashboard'da metrikleri görür.

| Bileşen | Açıklama |
|---------|----------|
| **SSOT** | `data/orchestrator/ajan-chat.jsonl` — her satır bir sorun (append-only, lock-protected) |
| **CLI** | `python scripts/ajan_chat.py <komut>` — 6 komut (ac/guncelle/kapat/oku/ozet/bulgula) |
| **Dashboard** | `web_dashboard/tabs/admin_panel.py:render_chat_summary()` — 3 metrik + son 3 sorun + tüm tablo |
| **Tetik** | `trigger.py:rapor_postala()` — WARNING/ERROR raporları otomatik chat.ac() ile kaydedilir |
| **Durum Döngüsü** | acik → cokundurmus (çözüm önerildi) → cozuldu (kapatıldı) |
| **Lock** | `threading.RLock` — eşzamanlı append güvenli |

### CLI Komutları

```bash
# Sorun aç (ajan, task_id, sorun açıklaması)
python scripts/ajan_chat.py ac ihsan UI-01 "Button hover eksik"
python scripts/ajan_chat.py ac ihsan UI-01 "Button hover eksik" --cozum "CSS :hover ekle"

# Çözümü güncelle (task_id, sorun_index, yeni çözüm, durum)
python scripts/ajan_chat.py guncelle UI-01 0 --cozum "CSS :hover eklendi, test yapıldı" --durum cokundurmus

# Sorunu kapat (task_id, sorun_index, karar)
python scripts/ajan_chat.py kapat UI-01 0 --karar "CSS uygulandı, QA geçti"

# Sorunları oku (filtreleme: --task-id, --son N)
python scripts/ajan_chat.py oku
python scripts/ajan_chat.py oku --task-id UI-01
python scripts/ajan_chat.py oku --son 5

# Durum özeti (--durum: acik/cokundurmus/cozuldu)
python scripts/ajan_chat.py ozet
python scripts/ajan_chat.py ozet --durum acik

# Tasarım eleştirisi kaydı (konu, bulgu, --link isteğe bağlı)
python scripts/ajan_chat.py bulgula "Tasarım (D-192)" "Font boyut tutarsız" --link "data/..."
```

### Orkestratör Günlük Rutini (15 min)

1. **Panoyu aç**, admin panel → Ajan Chat Sistemi widget
2. **Açık sorunları oku** (kırmızı panel): `python scripts/ajan_chat.py ozet --durum acik`
3. **Son 3'ü gözden geçir** (expander)
4. **Çözüm önerisi yaz** (cokundurmus geçişi): `guncelle` komutu
5. **Çözüldü olanları kapat** (cozuldu): `kapat` komutu
6. **Raporu kontrol et**: rapor_postala() tetiklenir, WARNING/ERROR otomatik kaydedilir

### Arkitektur

- **Veri:** JSONL (satır = kayıt, append-only)
- **Okuma:** `oku()` — tüm kaydı sunar; `ozet()` — durum filtrelü sayı
- **Yazma:** `ac()` / `guncelle()` / `kapat()` — lock ile sıralı
- **Chat Entegrasyonu:** trigger.py rapor_postala() WARNING+ rapor varsa chat.ac() çağırır
- **UI:** Streamlit, PageHeader + Section pattern (admin_panel.py ile tutarlı)

### Test Kapsamı

- `tests/test_ajan_chat.py` — 14 test
  - TestAc: sorun açma (4 test)
  - TestGuncelle: çözüm güncelleme (2 test)
  - TestKapat: kapatma (1 test)
  - TestOku: okuma/filtreleme (3 test)
  - TestOzet: durum özeti (1 test)
  - TestBulgula: tasarım eleştirisi (2 test)
  - TestConcurrency: 5 thread eşzamanlı append (1 test)
  - TestIntegration: full lifecycle + orkestrator simülasyonu (2 test)

### Phase 2 (İleri)

- MIMIR asistanı: chat metrikleri analiz etme
- Otomatik eleştiri önerileri (bulgu → çözüm)
- Chat geçmişi grafiklendirme (trend analiz)

## Git Değişiklik Kaybı Önleme (D-193 — KAHİN kararı 2026-09-23)

**Sorun:** Uncommitted değişiklikler session sonunda kayboluyor (geçerli olay: dün yapılan admin menu + küçük iyileştirmeler kaybedildi).

**Çözüm:** İki katmanlı koruma:

1. **Ajan Sorumluluğu (Zorunlu)**
   - Her görev bitiminde **kendi dokunduğun dosyaları tek tek sahneleyip** commit et: `git add -- <yol> [<yol>...] && git commit -m "<görev_özeti>"`. Push'u tetik sisteminde veya oturum kapatılmadan önce yap.
     > **D-288 düzeltmesi (2026-09-29):** bu satır eskiden `git add -A` emrediyordu. Kural kitabının kendisi, "toptan sahneleme yok" kuralını ihlal ediyordu — ağaçta üç ajan var, `-A` başkasının uçuştaki işini de tarihe sokar. Ölçüm ve gerekçe: D-288 kaydı. Mandal: `tests/test_otomasyon_sahneleme.py`.
   - Uncommitted dosyalar 30 dakika sonra `git stash` ile saklanır (otomatik cron, `scripts/git_stash_guard.py`, D-193 ile yürürlüğe girecek).
   - Stash mesajı: `AUTO-STASH [session_start_timestamp] [modified_files_count]` — session bitiminde roo'ya alert gider.

2. **Sistem Koruma (Arka planda)**
   - `.git/hooks/pre-commit`: değişiklik dosya sayısı > 5 ise commit öncesi `git diff --stat` raporunu loglar (basit audit).
   - `.github/workflows/git-guard.yml` (yapılacak): Her 1 saatte uncommitted değişiklik varsa, automatic branch oluşturur (`auto-save-TIMESTAMP`), stash uygulanır, PR draft açılır. Ajan onaylaması gerekir.

3. **Oturum Başında (Ajan Zorunluluk)**
   - Oturum başında `git status` çalıştır. Stash varsa (`git stash list`), `git stash pop` yapıp değişiklikleri review et. Artık dosya varsa manuel olarak çalış veya `git reset --hard`.
   - Pre-commit hook: `scripts/git_safety_check.py` Python dosya syntaxını, UTF-8'i, line ending'leri doğrular. Bozuk dosya commit edilemez.

**Kapsam:** Başladığı tarihten (2026-09-23) sonrası tüm oturumlar. Geriye dönük stash var ise `git stash list` ile görülür; poplayabilir.

**Amacı:** Uncommitted değişiklik > 30 dakika hiçbir zaman kalmasın. Ajan + sistem çift tarafından korunmuş.

**Kaynaklar:**
- `scripts/git_stash_guard.py` — cron tarafından çalışacak, 30 dakika kontrolü
- `scripts/git_safety_check.py` — pre-commit hook
- GitHub Actions yaml (yapılacak, P2)

---

## SSOT Kiti (D-196 — KAHİN kararı 2026-09-24)

**Tanım.** **SSOT Kiti** = bir SSOT dökümanı + `§0.1 Bağlantılı dökümanlar` tablosunda listelenen bağlı belgeler + ilerleme tabloları. Kit tek isimle anılır; ürün sahibi o ismi söyleyince ajan **tüm kiti** açar.

**Kural.**
1. Her kitin **tek bir kısa adı** vardır (örn. `ADMIN-KİT`). Ad bu tabloda sabittir.
2. Kit kapsamındaki **her görevin başında** SSOT dosyası okunur; **her görevin sonunda** ilerleme SSOT'un izlenebilirlik + revizyon tablolarına işlenir. İlerleme kaydı başka dosyaya yazılmaz — kit kendi geçmişini taşır.
3. Yeni bağlı belge eklenince `§0.1` tablosuna satır + geri link eklenir (D-186).
4. Kit dışı bir döküman kitle çelişirse **SSOT üstündür** (kitin kendi statü bloğundaki istisnalar saklı).

**Kayıtlı kitler.**

| Kit adı     | SSOT dosyası                                                          | Bağlı belge | İlerleme tabloları     |
| ----------- | --------------------------------------------------------------------- | ----------- | ---------------------- |
| `ADMIN-KİT` | `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (v2.6) | 6           | §7 matris · §14 revizyon |

**`ADMIN-KİT` bağlı belgeleri (§0.1):** PRD kaynağı `Huginn Data Insights (HUGIns).txt` §889-1687 · V9 bağlam `01_versiyon_9_baglam_dokumani.md` §16.4/§16.5 · `docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md` · `03_mimari/06_muninn_prd_vs_huginn_analiz.md` (bayat) · `CHANGELOG.md` · görev panosu `data/orchestrator/ADMIN_PANEL_PLAN_VE_GOREV_PAKETLERI_2026-09-22.md`

**Yeni kit açma.** SSOT dosyasına statü bloğu + `§0.1` + ajan kuralı satırı yazılır, kısa ad seçilir, bu tabloya satır eklenir. Onay: KAHİN.

---

## SSOT Tek-Durum Kuralı (D-197 — KAHİN kararı 2026-09-24)

**Kapsam:** [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] ve sonraki tüm SSOT dökümanları.

**Kural.**
1. **Durum ve öncelik yalnız §7 İzlenebilirlik Matrisi'nde tutulur.** §7 tek yazma noktasıdır; bir maddenin durumu değişince yalnız oraya yazılır.
2. **§8 / §9 / §10 / §11 / §12 tanım ve gerekçe yazar.** Bu bölümler ne yapılacağını ve nedenini anlatır; durum etiketi (`✅`, `⬜`, `devam`), öncelik etiketi (`P0`/`P1`/`P2`) veya tamamlanma yüzdesi **taşımaz**. Bir maddenin nerede durduğunu öğrenmek için §7'ye bakılır.
3. **§14 Revizyon Tablosu saf değişiklik günlüğüdür** — "ne zaman, kim, neyi değiştirdi". İlerleme göstergesi değildir; toplam/kalan/yüzde satırı içermez.
4. **Çelişkide §7 doğru kabul edilir.** Başka bölüm §7 ile çelişiyorsa çelişen etiket o bölümden silinir, §7 düzeltilmez.
5. **Metrik biçimi:** ilerleme yüzde ile değil ham sayaçla verilir — `Açık görev — P0: n · P1: n · P2: n (kaynak: §7 matrisi)`. Yüzde, eşit ağırlıkta olmayan maddeleri eşitmiş gibi gösterir.

**Gerekçe:** Aynı bilgi iki yerde tutulunca zamanla ayrışır; ajan hangisinin doğru olduğunu bilemez, KAHİN yanlış tabloyu okur. Kök neden "unutulan güncelleme" değil, **bilginin çoğaltılmış olması**. Tek yazma noktası bu sınıfı tümden kapatır.

**Uygulama görevi:** `plans/brief_utku_DOC-ADMIN-DURUM-SENKRON-15.md` — tutarsızlıkları eşitlemez, yapıyı ayrıştırır.

**Ilgili Nodlar**
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[plans/_brief_sablon]]

## Arşiv de Mükerrer Kapısıdır (D-198 — KAHİN kararı 2026-09-24)

Bir `task_id` panoda yoksa "yeni iş" demek değildir; kapanıp arşivlenmiş olabilir. `gorev_ekle()` mükerrer kontrolünü yalnız `task_board.json` üzerinde değil, `task_board_arsiv_*.json` dosyalarının birleşimi üzerinde yapar ve hata metni **hangi arşiv dosyasında** bulunduğunu söyler; `bakim --rapor` aynı çakışmayı salt okunur raporlar, arşive asla yazmaz. Ayrıca **hiçbir üretim veya planlama turu, `python scripts/gorev_kutusu.py simulasyon` çıktısı temiz (çıkış kodu 0) değilken başlamaz** — tur öncesi zorunlu kapıdır. Gerekçe: `ALTYAPI-D66-BYPASS-TETIKLEME` işi arşivde `done` iken panoya ikinci kez `plan` olarak girdi ve aynı iş iki kez üretildi; kök neden unutkanlık değil, kapının yarım kapsamıdır.

| Simülasyon çıkış kodu | Anlamı | Tur başlayabilir mi |
|---|---|---|
| `0` | Temiz | Evet |
| `1` | Uyarı var | Evet — uyarılar tur planına yazılır (D-65) |
| `2` | Hata var | **Hayır** — önce hata kapatılır |

### Hafıza Kapıları Nerede Yaşar (B-14 · TUR-B2 2026-09-24)

Kapanan işin SSOT/hub izi zorunludur. Yeni araç açılmadı; kapı üç mevcut komutun içinde yaşar:

| Kapı | Komut | Davranış | Kaçış | Test |
|---|---|---|---|---|
| 4.1 | `gorev_kutusu.py teslim` | `task_id` SSOT'ta ya da brief'teki hub'da geçmezse teslim reddedilir | `--zorla` (panoya `hafiza_izi=atlandi`) | [[tests/test_gorev_kutusu_hafiza]] |
| 4.2 | `gorev_kutusu.py basla` | Önce `simulasyon` koşar; kod `2` → zincir başlamaz, kod `1` → uyarıp devam | `--simulasyonsuz` | [[tests/test_gorev_kutusu_simulasyon]] |
| 4.3 | `gorev_kutusu.py simulasyon` | Kontrol 8 aktif pano **+ son çeyrek arşivini** tarar, izsiz `task_id`'leri UYARI olarak listeler | — | [[tests/test_gorev_kutusu_hafiza]] |

Her brief'te `**Hub:**` satırı zorunludur ([[plans/_brief_sablon]]); kapı izi orada aranır.

**Yürürlük tarihi:** Kontrol 8 yalnız **2026-09-24 ve sonrasında** kapanan (`bitis` alanı) işleri denetler — kodda tek sabit: `gorev_kutusu.HAFIZA_KAPISI_YURURLUK`. Bu tarihten önce kapanan 376 işin karşılığı, iki hub'daki "Kapanan isler" bölümünün sonundaki çeyreklik arşiv bağlantısıdır (`data/orchestrator/task_board_arsiv_2026-Q3.json`, D-186). Geriye dönük 376 satır yazmak hafıza değil gürültü üretirdi; kapı ileriye dönük çalışır. İz araması `hubs/` dizinindeki **tüm** hub dosyalarında yapılır, çünkü brief `**Hub:**` satırıyla hedefini kendi seçer.

## Katmanlı Görünürlük & Modül Kontörü (D-200 — D-208, KAHİN kararları 2026-09-24)

Veri görünürlüğü (SELECT c.* sızıntısı, paket tanımı, kontör sistemi, admin filtreleme) için 9 karar:

| # | Başlık | Karar | Referans |
|---|---|---|---|
| **D-200** | Kontör tanımı | Modül başına maliyeti farklı. `module_cost(module_id, tier, cost_per_query)` tablosu. | ALTYAPI-VERI-GORUNURLUK-01 §A3 |
| **D-201** | Admin filtreleme anahtarı | `admin_kvkk_mode` tablo: strict (sabit KVKK) / lenient (admin riski üstlenir). Lenient sadece admin, audit zorunlu. | design_visibility_simulation.md §Senaryo 3 |
| **D-202** | Müşteri gizleme kapatması | `?mask=0` parametresi **kaldırılır**. Müşteri gizlemeyi kapatamaz; KVKK Layer 1 sabit. Parametrе sadece sıkılaştırır. | design_visibility_simulation.md §Senaryo 5, brief §A3 |
| **D-203** | Alan grubu görünürlüğü | 6 grup (kimlik, iletişim, lokasyon, dijital, ticari, sınai) × 3 paket = 18 satır `plan_field_group`. Admin sekmesinde aç/kapa. | brief §A1-A3 |
| **D-204** | Kontör düşümü | Grup + firma başına 1 düşüm (modül+grup kombinasyon ileride). `/api/buyer/reveal?company_id=X&group=Y` ile kontör düşer. | design_visibility_simulation.md §Senaryo 2, brief §A3 |
| **D-205** | Admin anahtarı değişimi | `admin_kvkk_mode` her değişikliği `user_activity_log`'a yaz (who/when/old/new). | brief §A3 |
| **D-206** | OSINT kazıma filtresi | OSINT paketi = `plan="osint"`, kontör=0. Karantina kayıtlar filtrelenir (Ç4 çözüm). | design_visibility_simulation.md §Senaryo 4 |
| **D-207** | Veri sınıflandırması | Alan → KVKK sınıfı (açık/yarı-açık/kısıtlı/yasak) matrisi. Kayıt başına değil alan başına (bakım basit). | field_catalog.md (yeni) |
| **D-208** | Silme politikası | Veri **asla silinmez**. Karantina = `quarantine_reason` + `is_sahis` bayrakları. Ç1-Ç4 (GSM, e-posta, şahıs, WhatsApp) karantina ile çözülür. | design_visibility_simulation.md §Çelişkiler |

**Uygulanacak dosyalar:**
- [`migrations/0018_visibility_layer.sql`](src/company_master/schema/migrations/0018_visibility_layer.sql) — 3 tablo + ALTER companies
- [`field_catalog.md`](field_catalog.md) — SSOT: ~60 alan × grup × KVKK sınıfı
- [`normalize.py`](src/company_master/api/core/normalize.py) — `apply_plan()`
- [`web_app.py`](web_app.py) — 4 çağrı noktası, `/api/buyer/reveal` endpoint
- [`admin_panel.py`](web_dashboard/tabs/admin_panel.py) — 3 yeni sekmesi

**Test senaryoları:**
- `test_visibility_senaryo_1-5.py` — Müşteri match/ilan/analiz, admin filtreleme, OSINT, kontör düşümü
- `test_kvkk_katman_iki.py` — KVKK Layer 1 sabit, Layer 2 kırılabilir
- `test_module_cost.py` — Modül/tier/cost doğrulaması

**Ilgili Nodlar**
- [[src/company_master/orchestrator/task_board]]
- [[scripts/gorev_kutusu]]
- [[tests/test_gorev_mukerrer_arsiv]]
- [[tests/test_gorev_kutusu_simulasyon]]
- [[tests/test_gorev_kutusu_hafiza]]
- [[hubs/ADMIN_DASHBOARD_HUB]]
- [[hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/docs/GOREV_PANOSU_KULLANIM_KILAVUZU]] — §10 Proje Sağlık Simülasyonu (tablolu kullanım kılavuzu)

## Ajan Chat Kuralı (D-210 — KAHİN kararı 2026-09-25)

Ajanlara **zorunlu sohbet ve koordinasyon** ilkesi:

### Kural Özeti
- **@mention = ZORUNLU cevap** — Ajan adı bahsedilen sohbette, o ajan P0/P1/P2'ye göre response SLA içinde cevap vermek **zorundadır.**
  - P0 görevlerde: 5-10 dakika içinde
  - P1 görevlerde: 10-15 dakika içinde
  - P2 görevlerde: 15-30 dakika içinde
- **Sessiz çalışma yasak** — Hata, soru, koordinasyon veya rapor eleştirisi oluşunca **chat'e yazma zorunluluğu.**
- **Cevap vermeme cezası** — @mention'a cevap vermeyen ajan, sonraki 3 görev atanırken **24 saatlik gecikme** alır.

### Zorunlu Chat Türleri
1. **Hata/Sorun Bildirimi** — `@orkestrator HATA: <TASK-ID> — <sorun özeti>` formatı
2. **Soru/Görüş** — `@<AJAN_ADI> — <sorunun adı>: <soru metni>` (soran yanıt bekleme hakkı)
3. **Ajanlararası Koordinasyon** — `@<AJAN_ADI> — <TASK-1> ve <TASK-2> overlap. Hangisi önce?` (karar gerektiren)
4. **Rapor Eleştirisi/Düzeltme** — `@<AJAN_ADI> — [rapor <TASK-ID>] <satır veya bölüm>: <eksiklik/hata>` (şart: rapor oku, yaz)

### Chat Komutları
- **Mesaj gönder:** `python scripts/chat_gonder.py --to <ajan> --type hata --task-id <ID> --mesaj "<metin>"`
- **Mesaj oku:** `python scripts/chat_al.py --ajan <ajan> --limit 20`
- **Özetle görüntüle:** `python scripts/chat_al.py --ozet gun` (günlük özet)

### Chat Log Konumu
- Konum: `data/orchestrator/chat/messages.jsonl` (JSONL format, timestamp + görev bağlantısı)
- Her satır: `{"tarih": "2026-09-25T10:15:00", "kimden": "utku", "kime": "ihsan", "type": "hata", "task_id": "UI-ADMIN-26", "mesaj": "...", "yanıt_alındı": false}`

### Gerçek Örnekler
- **Hata:** `@ihsan HATA: UI-ADMIN-KVKK-MODU-26 — ImportError: normalize module yok`
- **Soru:** `@orkestrator — API-LAYER2-DINAMIK-YÜKLEME-30: kontörlü yükleme vs batch yükleme farkı?`
- **Koordinasyon:** `@utku — UI-ADMIN-KVKK-MODU-26 ve API-ADMIN-MFA-26 overlap var. Hangisi önce?`
- **Rapor Düzeltme:** `@yasu — [rapor TEST-BLOKE-18] satır 38: audit log tablo yapısı açıklanmamış. Ekle.`

### Karar Yayınıyla İlgili Nodlar
- [[Huginn Data Insights/data/orchestrator/AJAN_CHAT_KURALI_D210]] — Tam kural belgesi + komut örnekleri
- [[Huginn Data Insights/data/orchestrator/CHAT_SISTEMI_FAYDALARI]] — Chat ROI: hız, kalite, denetim, riski yönetme

---

## İkiz Yapı Yasağı (D-211 — KAHİN kararı 2026-09-26)

KAHİN: *"sistemde ikiz yapılar olmasın istiyorum"*.

### Kural
Aynı işi yapan iki yapı **yasaktır**. İkiz = aynı isimli ikinci tanım, `original_*` / `*_eski` / `*_backup` kopyası, aynı kodu ikinci portta çalıştıran ikinci süreç, aynı bilgiyi tutan ikinci dosya. İkiz görülürse **düzeltilmez, silinir**; tek kalan sürüm düzeltilir.

### Neden
İkizin ikinci kopyası hiç güncellenmez ama aranınca bulunur. Ajan yanlış kopyayı okur, düzeltmeyi oraya yazar, hata sürmeye devam eder. `original_web_app.py` içinde hatalı `_record_failed_login()` aynen duruyordu; `_log_search_event` `web_app.py` içinde birebir iki kez tanımlıydı ve ikinci tanım birinciyi gölgeliyordu.

### Denetim
- Modül düzeyinde mükerrer fonksiyon tanımı: `tests/test_auth_lockout.py::test_ikiz_fonksiyon_tanimi_yok` (AST tabanlı, `web_app.py`).
- Yeni ikiz sınıfı bulunduğunda benzer AST/kaynak taraması testi eklenir — kural yorumla değil testle korunur.

### Bu kural kapsamında silinenler (2026-09-26)
- `original_web_app.py` (~2500 satır, `web_app.py` bayat kopyası; hiçbir yerden import edilmiyordu)
- `web_app.py` içindeki ikinci `_log_search_event` tanımı
- 8502 portundaki ikinci Streamlit örneği (bkz. D-212)

---

## Tek Yapı Tek Adres (D-212 — KAHİN kararı 2026-09-26)

KAHİN: *"tek bir yapı tek bir adres istiyorum; sahte veri koyacaksan sahte verilerin olduğu grafiğin altına yazarsın ve uyarılar koyarsın, yeni veriler geldiğinde onlar otomatik değişir"* ve *"`http://localhost:8501/` tüm projede tek gerçek admin paneli olarak gözüküyor, adres her zaman bu şekilde kalacak"*.

### Kural
- **Tek panel adresi: `http://localhost:8501/`.** İkinci port, "taslak sürüm", "UX kopyası" açılmaz. (Önceki 8501-gerçek / 8502-sahte ayrımı **iptal edildi**.)
- **Sahte veri ayrı bir yapı değildir.** Verisi henüz gelmemiş kutu, tek uygulamanın içinde yer tutucu değerle çizilir ve **hemen altına** "⚠️ **SAHTE VERİ**: … — gerçek veri geldiğinde otomatik değişir." uyarısı basılır.
- **Elle temizlik yok.** Gerçek veri geldiği anda `_dolu()` True döner, kutu gerçek değere geçer, uyarı kendiliğinden kaybolur.

### Uygulama
- `web_dashboard/tabs/ana_kontrol.py`: `TASLAK = os.getenv("HUGINN_TASLAK", "1") != "0"` — yer tutucu **varsayılan olarak açık**. `HUGINN_TASLAK=0` yalnızca ekran görüntüsü/denetim için kaçış kapısıdır, ayrı bir sürüm değildir.
- Yer tutucu sabitleri grep'lenebilir: `SAHTE_DEGER`, `SAHTE_YUZDE`.
- Uyarı metni tek kalıp: `⚠️ **SAHTE VERİ**: <ne> — gerçek veri geldiğinde otomatik değişir.`

### Denetim
`tests/test_taslak_sahte_veri.py` — `TASLAK` açık/kapalı iki durumda da uyarının kutunun altında çıktığını doğrular.

---

## Menü Ağacı, Veri Etiketi, Marka Başlığı (D-213 — KAHİN kararı 2026-09-26)

Tek oturumda verilen üç KAHİN talimatı. Üçünün ortak ilkesi: **tek düğme, tek kalıp** — gizlemek/etiketlemek/renklendirmek için ikinci bir liste tutulmaz (D-211 ikiz yasağının UI karşılığı).

### NAV-AGAC-01 — Oluşturulan sayfa menüde görünür
KAHİN: *"oluşturulmuş bir sayfa navigatör menü ağacında gözükmeli, fakat aynı başlık altında bir sayfa birleşebiliyorsa birleşebilmeli"*.

- Menü ağacı üyeliğini **tek alan** belirler: `TabTanimi.ust`. `ust is None` → sidebar kökü; `ust="x"` → kök `x` altında alt sekme.
- `ust_sayfalar()` içindeki **6 anahtarlık sabit frozenset kaldırıldı**. Listede olmayan kök bölüm sessizce menüden düşüyor, yalnız "🔍 Hızlı geçiş" kutusundan erişilebiliyordu — 14 sayfa bu şekilde görünmezdi.
- Gizlemek için ayrı liste **yasak**; sayfa gizlenecekse ilgili başlığın altına bağlanır.
- `sira` artık kök sayfalarda da anlamlıdır (menü sırası). Kökler: `ana_kontrol=0, musteri_yonetimi=1, proje_yonetimi=2, veri_kalite=3, musteri_onizleme=4, sistem=5`.
- **En fazla 2 seviye**: `ust` başka bir alt sekmeyi gösteremez (ağaç çizici 3. seviyeyi çizmez).
- Sabit bölüm sayısı iddiası kırılgandır (`== 37` iddiası 38'e çıkmışken kalmıştı) → alt sınır (`>= 38`) + benzersizlik denetlenir.
- Denetim: `tests/test_sekme_kapsama.py::test_her_bolum_menu_agacindan_erisilebilir` + `tests/test_tabs_ia.py::test_her_sayfa_menu_agacinda`.
- **UX-MENU-04 geçersiz**: "taşan sekmeyi menüden çıkar" kuralı kaldırıldı. KAHİN: *"her sayfa menüde gözüksün, sonra ilgili ve alakalı olanları birleştirelim; admin tek sayfada ilgili ve alakalı konuları görebilecek şekilde optimize ediyoruz"*. Sınır **gizlemeyle değil birleştirmeyle** korunur. `test_tabs_ia.py::MENUSUZ` demeti ve `test_menuden_cikanlarin_adresi_kirilmadi` silindi; üst başına alt sekme sınırı geçici olarak 12 (birleştirme sonrası düşürülecek).
- İkon çakışması: `executive` 📈 idi, `veri_kalite` ile aynı → 💹. Menüde iki kardeş aynı ikonla ayırt edilemez (`test_ikon_benzersiz`).
- **Sıradaki iş**: ilgili sayfaların birleştirilmesi + sayfa başına vektör grafik tasarımı (KAHİN: *"sonra her sayfayı ayrıca tasarlarız, vektör chartlar ve grafikler kullanırız"*).

### VERI-ETIKET-01 — Her blok verisinin kaynağını söyler
KAHİN: *"sahte veri ve gerçek veri ayırt etmek için ikon kullan, altına sahte/gerçek diye yaz; böylece ben hangi verilerin geldiğini göreyim"*.

- Tek yardımcı: `ana_kontrol._veri_etiketi(gercek, sahte)` → `🟢 **GERÇEK VERİ**: …` · `🔴 **SAHTE VERİ**: … — gerçek veri geldiğinde otomatik değişir`.
- Eski uyarı yalnızca sahte olanı sayıyordu; gerçek verinin hangisi olduğu görünmüyordu. Artık iki taraf da yazılır.
- Gerçek veri geldiğinde ad `sahte` listesinden `gercek` listesine geçer, etiket kendiliğinden değişir — elle metin düzenlenmez.
- Denetim: `tests/test_taslak_sahte_veri.py` (etiket ikon + kelime, gerçek veri de etiketlenir).

### MARKA-BASLIK-01 — Logo büyük + gradyan "Admin Insights"
KAHİN: *"logo biraz küçük olmuş büyüt ve sağ kısmına Admin Insights kelimesini yaz, aynı renk gradeninde olsun uyumsuz olmasın"* + *"marka rengi logo renkleri ile aynı"*.

- Marka gradyanı (logo renkleriyle birebir, tek kaynak `app.py::MARKA_RENK`):
  `linear-gradient(135deg, #22D3EE 0%, #3B82F6 35%, #4F46E5 65%, #8B5CF6 100%)`
  (cyan → blue → indigo → violet).
- `st.logo(size="large")` Streamlit'in üst sınırıdır; büyütme CSS ile (`3.4rem`).
- "Admin Insights" yazısı `[data-testid="stSidebarHeader"]::after` ile basılır — **ikinci bir marka/HTML bloğu üretilmez** (D-211).
- Denetim: `tests/test_dashboard_nav.py::test_marka_basligi_gradyan_ve_metin` (4 renk + `135deg` + metin + `max-height` sabitleri). `app.py` modül düzeyinde `main()` çağırdığı için test dosyayı import etmez, kaynak metnini okur.

---

## D-214 — Menü Temizliği + KVKK Birleştirme (KAHİN kararı 2026-09-26)

D-213'ün "her sayfa menüde gözüksün, sonra ilgili ve alakalı olanları birleştirelim" talimatının devamı.

- **İkiz çocuk temizliği (D-211 UI hâli):** `kpi` (ust=veri_kalite) ve `paketler` (ust=musteri_onizleme) çocuk kayıtları köküyle **aynı** `modul.fonksiyon` çiftini render ediyordu (`admin_kpi.render_kpi_tab`, `paketler.render_paketler_tab`) — tıklanabilir çift giriş, tek gerçek sayfa. Çocuk kayıtları silindi, `sira` boşlukları kapatıldı, `ESKI_URL["kpi"]`/`ESKI_URL["paketler"]` köke yönlendirir.
- **Yalan yorum temizliği:** `tabs/__init__.py` içinde "hatalar + dlq + webhook tek sekmede birleşti" / "teknik_altyapi + performans tek Altyapı sekmesinde" yorumları koddan silindi — ikisi de ayrı sekme olarak duruyordu, yorum gerçekleşmemiş bir planı anlatıyordu.
- **Ratchet testi:** `test_ust_basina_alt_sekme_siniri` artık sabit sayı değil, mevcut fiilî maksimumu (`sistem` kökü, 11 çocuk) tavan alır — KAHİN: sınır *gizlemeyle* değil *birleştirmeyle* korunur; tavan sabit kalırsa yeni dağınıklık test kırar, düşürülürse dosya elle güncellenir.
- **`test_d214_kok_cocuk_ayni_renderer_yasak`:** kök ile çocuğunun aynı `(modul, fonksiyon)` çiftini render etmesi kalıcı olarak yasaklandı (D-211 kökler için de geçerli).
- **KVKK birleştirme:** KAHİN: *"onaylıyorum kvkk birleştir zaten en faydalı konu buydu"*. `render_kvkk_mode_tab` (strict/lenient toggle + reason formu) ile `render_kvkk_rapor_tab` (4 metrik + geçmiş tablo + 7 günlük `st.line_chart`) ayrı sekmeydi; rapor artık mode formunun altına gömülü (`render_kvkk_mode_tab` sonunda `render_kvkk_rapor_tab()` çağrılır, ikinci fonksiyon SECTIONS'tan bağımsız yardımcı hâline geldi). Menüde tek giriş kaldı (`kvkk_mode`, ust=proje_yonetimi); `ESKI_URL["kvkk-rapor"]` bu sekmeye yönlendirir.
- **Doğrulama:** `pytest tests/test_tabs_ia.py tests/test_dashboard_nav.py tests/test_sekme_kapsama.py -q` → 198 passed, 3 skipped (skip'ler ilgisiz/ön-mevcut).
- **Tam suite fallout taraması:** `pytest tests/ -q` ikiz silme sonrası 24 failed verdi (24 önceki 22 backlog + 2 yeni). Tüm 24 hata gövdesi okunup tek tek triyaj edildi: 2'si gerçek fallout, 22'si backlog (madde 12) ile birebir eşleşti. Fallout: (1) `ana_kontrol.py::GIRIS_KARTLARI` içinde silinen `"kpi"` anahtarı kalmıştı → `"veri_kalite"` yapıldı; (2) `test_auth_gate.py::test_yeni_url_sections_dongusu_korunur` parametrize'i eski `"paketler"` bekliyordu → `"musteri_onizleme"`. İki düzeltme sonrası tam suite tekrar: **22 failed, 4254 passed, 12 skipped** — backlog sayısı sabit, yeni regresyon yok.
- **Kapsam dışı bırakılan (KAHİN kararı, bekliyor):** Faz 3 çıplak `st.*_chart` çağrılarının `charts.py`'ye taşınması (8 sayfa, P2); Güvenlik çatısı (denetim+mfa+kvkk tek kök) — 7. kök D-213'ün "≤6 kök" sınırıyla çelişiyor, KAHİN onayı gerekir; `sistem` kökünün (11 çocuk) bölünmesi; `musteri_onizleme` grubunun "Gelir" adlandırması gözden geçirilecek; `tests/_tmp_onem_test/` ve `_test_groq_chat_live.py` temizliği (`.gitignore`); 22 ön-mevcut test hatası backlog'u (bkz. `ihsan_project_context.md` madde 24).

---

## D-215 — Gelir Kapısı + Güvenlik Kapısı (KAHİN kararı 2026-09-26)

D-214'ün kapsam dışı bıraktığı iki karar (Güvenlik çatısı, "Gelir" adlandırması) KAHİN onayıyla uygulandı; kök sınırı D-213'ün "≤6"tan "≤7"ye çıktı (madde gerekçesi: iki yeni kök sorumluluk netliği getiriyor, gizleme değil birleştirme).

- **Güvenlik Kapısı (yeni kök):** `denetim` sekmesi `proje_yonetimi` çocuğundan kök seviyesine yükseltildi, başlığı **"Güvenlik Kapısı"** oldu (`baslik=t("menu_m_denetim")` → sabit metin). `kvkk_mode` (eski `ust=proje_yonetimi`) ve `mfa` (eski `ust=sistem`) bu kökün altına taşındı — erişim/uyum sorumluluğu artık tek kökte. `sistem` kökünün sıra numaraları (`ayarlar`, `yukleme`) mfa çıkışına göre kaydırıldı.
- **Gelir Kapısı hazırlığı — `paket_kredi` taşıması:** `admin_extras.render_user_management` içindeki kredi yükleme formu (ikiz risk, D-211) **silindi**; kanonik yer `musteri_yonetimi.render_paket_kredi_tab` oldu — yeni `TabTanimi(anahtar="paket_kredi", ust="musteri_onizleme", sira=2)`, `musteri_onizleme` grubu (`GRUP_GELIR`) altında "Paket & Kredi" başlığıyla. Testler taşındı: `test_admin_extras_kullanici.py`'den silinen `test_render_user_management_credit_form/_error` → `test_musteri_yonetimi.py::test_render_paket_kredi_tab_credit_form/_error` olarak yeniden yazıldı.
- **Maliyet → Metrikler:** `admin_cost.render_cost_tab` (`ust=musteri_onizleme`) sorumluluk gereği `veri_kalite` (Metrikler) köküne taşındı (`sira=4`) — ölçüm/analiz sayfası gelir kökünde değil metrik kökünde durmalı.
- **Ratchet güncellemesi:** `test_tabs_ia.py::test_ust_sayfa_sayisi` tavanı 6→7 (Gelir Kapısı + Güvenlik Kapısı); `test_dashboard_nav.py::test_ust_sayfalar_admin_6` → `test_ust_sayfalar_admin_7` (7 kök seti günceli); `test_alt_sekmeler_sira_sirali` listesinden `denetim`/`kvkk_mode` çıkarıldı (artık `proje_yonetimi` çocuğu değil).
- **Doğrulama:** `pytest tests/test_tabs_ia.py tests/test_dashboard_nav.py tests/test_musteri_yonetimi.py tests/test_admin_extras_kullanici.py tests/test_sekme_kapsama.py -q` → 211 passed, 3 skipped. Tam suite: **21 failed, 4259 passed, 12 skipped** — D-214'teki 22 ön-mevcut backlog hatasına göre 1 azaldı, D-215 kapsamında yeni regresyon yok.
- **Kapsam dışı bırakılan (bekliyor):** Faz 3 vektör grafik taşıması (8 sayfa); 21 ön-mevcut test hatası backlog'u (madde 12); tanıtım cümleleri sistemi (her başlık/sayfa/grafik için tutarlı giriş metni planı).

---

## D-216 — Hayalet görev arşivleme (KAHİN kararı 2026-09-26)

Utku toplu emri (madde 12) yürütülmeden önce panodaki `todo` kayıtları kod tabanıyla çapraz kontrol edildi: `UTKU-02` (`src/api/endpoints.py`), `UTKU-04` (`src/company_master/schema/migrations/0020_index_optimization.sql`), `UTKU-05` (`src/auth/token_refresh.py`), `ORCH-01..05` (`orchestration/*.py`) — 8 kaydın referans verdiği dosyalar/dizinler kod tabanında hiç var olmamış (`orchestration/` dizini yok, gerçek migration adı `0020_login_lockout.sql`). Sablon/placeholder sızıntısı olarak değerlendirildi.

- **Aksiyon:** 8 kayıt `scripts/_hayalet_gorev_arsiv.py` ile `durum=archive`'e taşındı, `not` alanına gerekçe eklendi. Task board dışında kod değişikliği yok.
- **Doğrulama:** `pytest tests/test_naming_audit.py -q` → 9 passed (D-57 denetimi etkilenmedi).
- **Sonuç:** Utku toplu emrindeki 8 backlog görevinden gerçek kalan sıfır; madde 12 kapandı (hepsi hayaletti).

---

## D-217 — Tek Brif + Brifte Ajan Chat Zorunlu (KAHİN kararı 2026-09-26)

D-66 "brifsiz atama yasak" der ama **kaç brif** yazılacağını söylemiyordu; toplu iş faz başına ayrı dosyaya bölünüyordu. Ayrıca D-210 ajan chat kuralı yalnız AGENTS.md'de yazılıydı — brifi okuyan ajan chat zorunluluğunu görmüyordu.

### Şablon kullanımı zorunlu
- **Her brif** [[plans/_brief_sablon]]'dan türetilir. Sıfırdan brif yazmak yasak.
- Zorunlu bölümler (eksikse brif geçersiz, `al` reddedilir):
  `**Başlık:**` · `**Öncelik:**` · `**Hub:**` · `## Neden` · `## Doğrulanacak varsayım` ·
  `## Adımlar` (veya `## Faz A`) · `## Kabul kriteri` · `## Ajan chat zorunlu` · `## Teslim`
- **Denetim:** `tests/test_brief_sablon_denetim.py` — `plans/brief_*.md` dosyalarında zorunlu bölümleri arar.
- Kanonik şablon **tek dosya**: `plans/_brief_sablon.md`. İkinci şablon dosyası açmak D-211 ihlali.

### Tek brif kuralı
- **Bir görev = bir brif.** Toplu iş birden çok brif dosyasına bölünmez.
- Toplu iş tek brifte `## Faz A — <ad>`, `## Faz B — <ad>` başlıklarıyla anlatılır.
- Her fazda: kök neden + etkilenen `dosya:satır` + o fazın doğrulama komutu.
- Fazlar **sırayla** yapılır; en riskli/veri kaybı riskli faz **ilk** sırada.
- Kabul kriteri: faz başına bir satır + sonda bütünün tek doğrulaması.
- **Yasak:** faz başına ayrı brif dosyası, ayrı `task_id`, ayrı tetik.

### Brifte ajan chat zorunlu
Her brif `## Ajan chat zorunlu (D-210 · D-217)` bölümünü **taşımak zorundadır**. D-210 kuralı brif metnine iner:
- Brifteki varsayım kodda tutmuyorsa → sorun aç, **uydurma, durma**.
- Faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk cevap zorunlu.
- Komut referansı (D-210 §Chat Komutları) brife kopyalanır: `ajan_chat.py ac|oku`, `chat_gonder.py`.

### İkiz şablon temizliği (D-211 uygulaması)
`plans/brief_TEMPLATE.md` silindi — `plans/_brief_sablon.md` ile ikizdi, hiçbir yerden referans almıyordu (yetim). **Kanonik şablon tek:** [[plans/_brief_sablon]].

- **Şablon güncellendi:** tek brif uyarısı + faz talimatı + ajan chat bölümü eklendi.
- **Referans:** D-66 (brifsiz atama yasak), D-210 (ajan chat), D-211 (ikiz yapı yasağı).

### Mandal (ratchet) yaklaşımı
D-217 öncesi **112 brif** eski formatta. Geriye dönük düzeltmek değer üretmez (kapanmış işlerin brifi).
`tests/_brief_baseline.txt` bu 112 kaydı dondurur; denetim yalnız **yeni** brifleri kapıda tutar.
Baseline **yalnız küçülür** — üst sınır testte 112'ye sabit. Yeni brifi baseline'a eklemek yasak.

```bash
python -m pytest tests/test_brief_sablon_denetim.py -q          # kapı
python tests/test_brief_sablon_denetim.py --baseline-yaz        # yalnız KAHİN kararıyla
```

---

## D-218 — Obsidyen Grafiği Zorunlu (KAHİN kararı 2026-09-26)

**Sorun:** Ajanlar Obsidyen'den faydalanmıyor. Linksiz doküman grafikten kopuk kalır; ajan onu bulmak için tüm repoyu tarar. Her kopuk doküman kalıcı **token + süre maliyeti** doğuruyor.

**Karar:** Obsidyen proje hafızasıdır; doküman grafiğe bağlanmadan iş kapanmaz.

- **Her brif** `## Ilgili Nodlar` bölümü ve **en az 2 wikilink** taşır: kaynak SSOT + hub.
- Görev sırasında **yeni** doküman üretilirse (rapor, plan, not) brife linklenir **ve** o dokümana kendi `## Ilgili Nodlar` bölümü eklenir — **çift yön** bağ.
- Markdown yolu değil `[[wikilink]]` kullanılır; Obsidyen grafiği yalnız wikilink'i sayar.
- **Denetim:** `tests/test_brief_sablon_denetim.py` — `## Ilgili Nodlar` + `[[` sayısı ≥ 2.
- **Referans:** D-217 (brif şablonu), B-14 (hub kapısı).

---

## D-219 — Ajan Oturum Hafızası (KAHİN kararı 2026-09-26)

**Sorun:** Oturum kapanınca ajanın bağlamı sıfırlanır. Sonraki oturum aynı keşfi baştan yapar — kalıcı token + süre maliyeti. Tek istisna `ihsan_project_context.md`; diğer ajanların hafızası yoktu.

**Karar:** Her ajanın **tek** kalıcı hafıza dosyası vardır: `<ajan>_project_context.md`.

- **Şablon:** [[Huginn Data Insights/_ajan_context_sablon]] — bölüm sırası **sabit**; ajan aynı bilgiyi aynı yerde bulur, arama yapmaz.
- Dosyalar: `ihsan_` (kanonik örnek), `utku_`, `yasu_`, `salih_`.
- **§KALDIĞIM YER** en üstte, **tek blok, üzerine yazılır** (biriktirilmez): Konum / Yapılanlar / Kritik bağlam / Sonraki adım / Görev + Son okunan karar.
  - *Kritik bağlam* satırı en değerlisi: "SADECE şu dosyaları baz al" — ajanın gereksiz repo taramasını kesen tek satır.
- **§Tuzaklar** ikinci değerli bölüm: *belirti → kök neden → çözüm*. Yazılmayan tuzak gelecek oturumda tekrar ödenir.
- **Slash komutu ile üretilmez.** Komut ancak tahmin eder; tahmin hayalet görev doğurur (D-216). Yazılı olan tek güvenilir hafızadır.
- **Context pano ile çelişirse pano üstündür** — context bayatlar, pano canlıdır.
- **Tavan 200 satır.** Aşınca eski oturum blokları `archive/<ajan>_context_<YYYYMM>.md`'ye taşınır; şişmiş context her oturumda okunur, maliyeti kalıcıdır.
- **Oturum kapanışı zorunlu:** §KALDIĞIM YER güncellenir + *Son okunan karar* no tazelenir. Atlanırsa dosyanın tüm faydası kaybolur.

---

## D-220 — Doküman Sıkılaştırma Politikası (KAHİN kararı 2026-09-26)

**Ölçüm (2026-09-26):** `4924` markdown dosyası. `4174`'ü (**%85**) gürültü; yalnız `750` kanonik. `README.md` **437** ayrı yerde, `SKILL.md` **360**, `CHANGELOG.md` **133**. Aynı köke düşen ad: **425**.

**Sorun:** Benzer evraklar aramayı kirletir. Ajan doğru dosyayı bulmak için onlarca yanlışı okur; her yanlış okuma token + süre + **yanlış dosyayı düzenleme riski**.

### Kural 1 — Tek Kanonik Yol

Her doküman türünün **tek** yaşam yeri vardır. Tabloda yoksa yeni tür açılmaz; en yakın türe yazılır.

| Tür | Kanonik yol | Şablon |
|-----|-------------|--------|
| Kural / karar (D-NN) | `Huginn Data Insights/AGENTS.md` | — (tek dosya) |
| Görev brifi | `plans/brief_<ajan>_<TASK_ID>.md` | `plans/_brief_sablon.md` |
| Ajan oturum hafızası | `<ajan>_project_context.md` | `_ajan_context_sablon.md` |
| Konu hub'ı | `hubs/<KONU>_HUB.md` | — |
| Ürün SSOT | `AI proje v1/V10/05_versiyonlar/` | — |
| Görev panosu | `data/orchestrator/` | — |

### Kural 2 — Arama Kapsamı Dışı

Ajan arama/okuma yaparken bu yolları **atlar**. Buralarda değişiklik yapmak da yasak:

`.agents/` · `.kilo/` · `.claude/` · `data_worktree/` · `**/backups/` · `node_modules/` · `archive/` · `data/skills/` · `_ARSIV*` · `worktree klasoru/`

Üçüncü parti skill'ler, git worktree kopyaları ve yedekler kanonik değildir. Bir dosya yalnız buralarda bulunuyorsa **kanonik karşılığı yok** demektir — kopyalamak yerine kanonik yolda oluştur.

### Kural 3 — Şablon Tekliği

Bir tür için **tek** şablon: `_<tür>_sablon.md`. İkinci şablon (`*_TEMPLATE.md`, `*_v2.md`, `*_yeni.md`) açmak D-211 ikiz ihlalidir. Şablon yetersizse **şablon düzeltilir**, yenisi açılmaz.

### Kural 4 — Yeni Doküman Kapısı

Yeni `.md` açmadan önce sırayla:

1. Bu bilgi mevcut bir dokümana **eklenebilir mi**? → ekle, yeni dosya açma.
2. Türü D-220 tablosunda var mı? → yoksa KAHİN onayı gerekir.
3. `## Ilgili Nodlar` + en az 2 wikilink var mı? → D-218 zorunlu.
4. Adı `_eski`, `_yeni`, `_kopya`, `_final`, `_v2` içeriyor mu? → **yasak**, git geçmişi bu işi yapar.

### Denetim

`tests/test_dokuman_politikasi.py` — Kural 1/3/4 kapıda. Tek başına da koşar:

```bash
python -X utf8 tests/test_dokuman_politikasi.py   # sayıları raporlar
python -m pytest tests/test_dokuman_politikasi.py -q
```

**Mandal:** D-220 anında 15 yasak-ad ihlali vardı (`_FINAL`, `_v2`, `_YENİ`…). Geriye dönük düzeltmek değer üretmez; üst sınır **15**'e sabit, **yalnız küçülür**. Kayıtlı şablon listesi **9** — yeni şablon KAHİN kararı ister.

**Kapsam dışı:** gürültü dizinlerindeki 4174 dosya temizlenmez. Üçüncü parti ve yedek; sahibi biz değiliz. Politika **kanonik 750** dosyayı korur.

**Referans:** D-211 (ikiz yapı yasağı), D-217 (tek brif şablonu), D-218 (Obsidyen grafiği), D-219 (ajan hafızası).

---

## D-221 — Kök Dizin İzin Listesi (KAHİN kararı 2026-09-27)

**Ölçüm (2026-09-27):** Çalışma kökü bir çöplüğe dönmüştü. Üst klasördeki 143 dosyanın **9'u ikiz**, **108'i çöp** (hata ayıklama artığı, ekran görüntüsü, tek seferlik betik), yalnız **26'sı eşsizdi**. `AI proje v1/` altında **829 dosya** vardı; **686'sı ikiz** (38 MB'ı boş satır), eşsiz içerik topu topu **1 MB**. Ayrıca 4 terk edilmiş worktree **184,6 MB** yer tutuyordu ve içlerindeki 838 "kirli" dosyanın **tamamı** boş satır/CRLF gürültüsüydü — tek satır kayıp iş yoktu.

**Kök neden:** Kökün ne içereceği hiç tanımlanmamıştı. Tanımsız alan dolar.

### Kural 1 — Kök Değişmez

Kök dizin **`c:/Huginn Data Projesi`** olarak sabittir. Gerekçe ölçümdür: kod tabanında **10.368** sabit yol bu köke bağlı. Taşıma önerisi getirmek yasaktır; kazanç yok, kırılma kesin.

### Kural 2 — Kökte Ne Durabilir

Kökte yalnız şunlar bulunur:

| İzinli | Açıklama |
|--------|----------|
| `Huginn Data Insights/` | Vault — asıl gövde |
| Yedek dosyaları | `.bundle` ve arşivler |
| `AGENTS.md` | Kural yönlendiricisi (SSOT değil) |
| Kilitli nokta klasörler | `.git`, `.agents`, `.github`, `.vscode`, `.obsidian`, `.roo`, `.kilo`, `.continue`, `.storybook`, `.kombai`, `.n8nac` |

Listede olmayan her şey köke **ait değildir**. Yeni bir kök girdisi KAHİN kararı ister.

### Kural 3 — İkiz Gövde Yasağı

`AI proje v1/` gibi paralel gövdeler yeniden doğmaz. İkiz gövde, hangi nüshanın doğru olduğu sorusunu üretir; bu soru her seferinde zaman yakar (D-211'in kök dizin karşılığı).

**Bilinçli sınır:** Bu karar kökü **dondurur**, içeriği tek tek temizlemez. Çöp dosyaların ayıklanması ayrı ve geri alınabilir bir iştir; kural önce kanamayı durdurur.

**Referans:** D-211 (ikiz yapı yasağı), D-222 (tek pano).

---

## D-222 — Tek Pano, Kanıtlı Kapanış (KAHİN kararı 2026-09-27)

**Ölçüm (2026-09-27):** Sistemde **iki** görev panosu yaşıyordu. Kökteki `gorev_panosu.md` **5 gün** güncellenmemiş, üstünde **7 aktif** görev duruyordu; `data/orchestrator/gorev_panosu.md` canlıydı ve **0 aktif** gösteriyordu. Ajanlar canlı olanı okuyordu — eskisindeki **16 görev** kimseye görünmüyordu.

**Sorun:** Bir panoyu arşive taşımak kolay; içindeki işi yok saymak **kayıt kaybıdır**. Eski panodaki 16 görev denetlendiğinde: **9'u zaten yapılmıştı** (rapor/brif dosyası mevcut), **5'i hayaletti** (düzeltilecek hata yok, kilit yok, test zaten var), **2'si gerçek backlog'du** — OSB ihale izleyicisi ve proxy rotasyonu. Bu ikisi sessizce silinseydi, kapsamda **42** ve **6** dosyada geçen iş kaybolurdu.

### Kural 4 — Devralınan Görev Kanonik Kimlik Alır

Arşivden backlog'a dönen görev **eski kimliğiyle** yaşatılamaz. Eski panonun `WK-` öneki D-57 kanonik alan listesinde yoktur; `gorev_at.py` bu kimliği reddeder. Görev, kanonik alan kimliğiyle **yeniden açılır** (`WK-02` → `VERI-02`, `WK-03` → `VERI-03`), eski kayıt `archive` durumunda yönlendirme notuyla bırakılır.

Gerekçe ölçümdür: D-222'nin ilk uygulamasında bu iki görev `plan` durumuna sahipsiz taşındı; `test_naming_audit` anında kırmızıya döndü. Durum değiştirmek kimlik doğurmaz — **üretim kapısından geçmeyen görev, görev değildir**.

### Kural 1 — Tek Pano

Canlı gövdede **tek** `gorev_panosu.md` bulunur: `data/orchestrator/`. SSOT `data/orchestrator/task_board.json`'dır; Markdown pano onun Obsidian okuması içindir. Pano ile JSON çelişirse **JSON doğrudur**.

### Kural 2 — Pano Kapatma Kanıt İster

Bir görev panodan düşürülmeden önce üç kovadan birine **kanıtıyla** yazılır:

| Durum | Anlamı | Gereken kanıt |
|-------|--------|---------------|
| `done` | İş yapıldı | Rapor/brif dosyası ya da commit |
| `archive` | Hayalet — konusu yok | Neden yok olduğunun ölçümü (test çıktısı, dosya sayımı) |
| `plan` | Gerçek backlog, başlanmadı | — (sahipsiz durur, silinmez) |

`kanit` alanı boş bırakılamaz. "Eski olduğu için" kapatmak yasaktır: **tarih kanıt değildir**.

### Kural 3 — Arşiv Silmez

Pano arşive taşınırken içindeki her görev ID'si önce SSOT'a işlenir. Arşiv dosyası **kayıt değil, geçmiştir**; tek başına görev taşıyamaz.

### Denetim

`tests/test_pano_tekligi.py` — 4 mandal:

```bash
python -m pytest tests/test_pano_tekligi.py -q
```

1. Canlı gövdede tek pano var.
2. SSOT'ta duplike görev ID yok.
3. Arşivlenen panodaki her ID SSOT'ta duruyor (kayıt kaybı yok).
4. `plan` durumundaki her görev Markdown panoda görünüyor.

**Mandal:** 4. madde backlog'un görünmez kalmasını engeller — D-222'nin asıl hastalığı buydu.

**Referans:** D-216 (hayalet görev arşivleme), D-220 (doküman politikası, pano kanonik yolu).

---

## Karar Numarası Yalnız AGENTS.md'den Verilir (D-227 — KAHİN kararı 2026-09-27)

- **Kural:** `D-NNN` karar numarası **yalnız bu dosyada**, `## Başlık (D-NNN — KAHİN kararı TARİH)`
  biçiminde bir kanonik başlıkla verilir. Numara tekildir. AGENTS.md dışındaki hiçbir belge
  karar numarasını **dosya adında** veya **H1 başlığında** sahiplenmez; gövdede
  `> Karar referansı: D-NNN (…)` satırıyla referans verir. Mevcut bir kararın uzantısı
  yeni numara almaz, `(D-NNN Ek — KAHİN kararı TARİH)` etiketiyle yazılır.
- **Gerekçe:** Aynı numaranın iki farklı konuyu adlandırması kayıt defterini kullanılamaz hâle
  getirir. "D-216" AGENTS.md'de *hayalet görev arşivleme*, 12 `plans/` dosyasında *Telegram Menü*
  demeye başladığında hangi kararın hangisi olduğu ancak tarih tahminiyle bulunabilir.
- **Tetikleyen hata:** `BOT_HANDLER_DATA_FIX_D223.md` ve `BOT_HANDLER_DATA_FIX_D224_KAPANISH.md`
  raporları D-223/D-224 numaralarını sahiplenmişti. Görev brifi 2 çakışma bildirdi; ölçülen
  gerçek tablo **8+ çakışan numara** (185, 216, 217, 218, 219 …), **35 dosya adında** ve
  **24 H1 başlığında** sahiplenme çıktı. AGENTS.md'nin kendi içinde de D-185 iki kanonik
  başlıkta duruyordu; satır 115'teki DASH-UX-02a başlığı `D-85 Ek`e çevrildi.
- **Mandal:** `tests/test_karar_numara_tekligi.py` — 6 test, iki katman:
  1. **TEKLİK** — AGENTS.md'de aynı `D-NNN` iki kanonik başlıkta olamaz (sıfır tolerans).
  2. **SAHİPLENME** — dosya adı (`TAVAN_AD = 35`) ve H1 (`TAVAN_H1 = 24`) ihlal sayıları
     D-227 anında **ölçülmüş** tavanlardır; yalnız küçülür, asla yükseltilmez (bkz. D-220:
     geriye dönük 37 dosyayı düzeltmek değer üretmez, artışı engellemek üretir).
  3. Tetikleyici iki raporun referans biçiminde kaldığını doğrulayan regresyon nöbetçisi.

```bash
python -m pytest tests/test_karar_numara_tekligi.py -q
```

- **Ürün sahibi istisnası (D-286 ile eklendi):** Ürün sahibi kararın **başka bir dosyaya**
  (örn. `docs/BORC_DEFTERI.md`) yazılmasını emredebilir; bu D-227 ihlali **değildir** ve
  ajan suçlu ilan edilmez. Kısıtlanan tek şey numaranın **kaynağıdır**: numara havuzu tektir
  ve `python scripts/karar_no.py` ile verilir. Kayıt nerede durursa dursun, aynı `D-NNN`
  iki ayrı kararı adlandıramaz.
- **Referans:** D-223 (Tek Otorite: Vault), D-220 (doküman politikası, tavan deseni),
  D-224 (ölçülmeden görev açılmaz — tavanlar tahmin değil ölçümdür), D-286 (tek havuz).

---

## Vault İçinde Paralel Veri Gövdesi Yasak (D-228 — KAHİN kararı 2026-09-27)

**Kural:** `Huginn Data Insights/` altında `data/` dışında ikinci bir veri gövdesi
duramaz. Yasaklı adlar: `data_worktree`, `data_eski`, `data_backup`.

**Neden:** D-221 Kural 3 ikiz gövdeleri yasaklıyordu ama mandalı yalnız **kök** dizine
bakıyordu. Bu kör nokta yüzünden `Huginn Data Insights/data_worktree/` 6 gün yaşadı:
**504 izlenen dosya, 50.3 MB** ve içinde **üçüncü** bir görev panosu izi
(`data_worktree/orchestrator/gorev_panosu.md`). D-222 "Tek Pano" derken vault içinde
üçüncü pano duruyordu. Kural değil, kuralın mandalı eksikti.

**Ölçüm (2026-09-27, tahmin değil):**

| Ölçüt | Değer |
|-------|-------|
| `data_worktree` dosya | 505 (git'te izlenen 504) |
| Yol olarak `data/`'da olmayan | 140 |
| İçeriği `data/`'da başka yolda var | 45 |
| **Gerçekten hiçbir yerde olmayan** | **95** |
| `.backup_2026-09-21` ikizi | 77 |

**Uygulama:** 95 eşsiz dosya `_ARSIV_data_worktree_essiz_2026-09-27/` altına
kopyalandı, sonra `git rm -r data_worktree`. D-170'in "ham kopya, merge bekliyor"
muafiyeti bitti: 6 gün bekleyen merge merge değil, çöptür.

**Mandal:** [`tests/test_kok_izin_listesi.py::test_vault_icinde_paralel_veri_govdesi_yok`](tests/test_kok_izin_listesi.py:103)

```bash
python -m pytest tests/test_kok_izin_listesi.py -q
```

Negatif kontrol: `data_worktree` var olduğu anda ölçüldü →
`AssertionError: D-228 ihlali: vault icinde paralel veri govdesi -> ['data_worktree']`.

- **Referans:** D-221 (kök izin listesi — kör noktanın kaynağı), D-222 (Tek Pano),
  D-170 (emekli: ham kopya muafiyeti), D-220 (geriye dönük temizlik değil, tavan).

---

## Zaman Damgalı Yedek Git'te İzlenmez (D-229 — KAHİN kararı 2026-09-27)

**Kural:** Adında `.backup_`, `.yedek_`, `_pytest_rerun` veya `_tmp_onem_test` geçen
dosya git'te **izlenmez**. Yedeğin yedeği tutulmaz; geçmiş zaten yedektir.

**Neden:** `.gitignore`'da `*.backup_*` ve `_tmp_*` desenleri **vardı** (TUR-C Adım 2,
2026-09-24) ama 65 dosyayı tutmuyordu: hepsi desenler yazılmadan **önce** izlenmeye
alınmıştı ve **git, izlenen dosyaya `.gitignore` uygulamaz**. `.yedek_` deseni ise hiç
yoktu. Yani kural yazılıydı, mandalı yoktu — bu yüzden D-228 commit'ine (`5655cc0`)
`git add -A` ile yeni çöp girdi. Kuralı yazan commit, kuralı ihlal etti.

**Ölçüm (2026-09-27, tahmin değil):**

| Ölçüt | Değer |
|-------|-------|
| Git'te izlenen zaman damgalı artık | 65 |
| SHA-256 aslıyla **aynı** | 0 |
| Aslından **farklı** | 63 |
| Aslı hiç yok (öksüz) | 2 |
| `.backup_2026-09-21` ikizi | 55 (36'sı `data/skills/supabase-postgres-best-practices/`) |
| `task_board.json.yedek_*` | 5 |

**Silmek veri kaybı değil — üç bağımsız kanıt:**

1. Geçmiş: `git log --diff-filter=A -- README.md.backup_2026-09-21` → `ec770e4`
   (otomatik günlük commit, 2026-09-22). İçerik depoda duruyor.
2. Fark küçük: `git diff --no-index --stat README.md.backup_2026-09-21 README.md` →
   `1 file changed, 2 insertions(+)` — marka revizyonu öncesi hâli.
3. Üreticisi de çöp sayıyor: ikizleri
   [`GRAPH-CANONICAL-UYGULA.py`](data/orchestrator/GRAPH-CANONICAL-UYGULA.py:95) üretti,
   [`GRAPH-INDEX-BUILD.py`](data/orchestrator/GRAPH-INDEX-BUILD.py:38) onları **atlıyor**.

**Uygulama:** `git rm` (index + disk), `.gitignore`'a `*.yedek_*`. Ayrı arşiv
**yapılmadı** — ikinci kopya tam da D-228'de yasaklanan şey. `tests/_tmp_onem_test/`
öksüz değil, [`test_chat_table_stil.py`](tests/test_chat_table_stil.py:31)'in runtime
çıktısı; silinince yeniden üretilir, versiyonlanması gereksizdi.

**Mandal:** [`tests/test_kok_izin_listesi.py::test_zaman_damgali_yedek_git_te_izlenmiyor`](tests/test_kok_izin_listesi.py:160)
— diske değil `git ls-files`'a bakar, çünkü sorun dosyanın varlığı değil
**versiyonlanması**ydı. Tavan `IZLENEN_YEDEK_TAVANI = 0` (D-220: yalnız küçülebilir).

```bash
python -m pytest tests/test_kok_izin_listesi.py -q
```

Negatif kontrol: 65 dosya izlenirken ölçüldü →
`AssertionError: D-229 ihlali: git'te 65 zaman damgali yedek izleniyor (tavan 0) ->
['PROJECT_ROADMAP.md.backup_2026-09-21', ...]`.

- **Referans:** D-186 (pano runtime state), D-220 (tavan yalnız küçülür), D-228
  (ikinci kopya yasağı — bu yüzden arşiv yok), TUR-C Adım 2 (mandalsız kalan desen).

---

## Gömülü Gövde Kopyası Yasak (D-230 — KAHİN kararı 2026-09-27)

**Kural:** Gövdenin tam kopyası vault'un **hiçbir derinliğinde** duramaz. Yasaklı ad
imzaları: `worktree_klasoru_kopya`, `vault_kopya`, `_kopya_govde`. Mandal diske bakar,
`git ls-files`'a değil — kopya izlenmese de yasaktır.

**Neden:** D-228 tam bu gövdeyi yasaklıyordu ama mandalı `VAULT.iterdir()` kullandı,
yani yalnız **üst seviyeye** baktı. Bu yüzden
`data/orchestrator/backups/D-187_faz2_2026-09-22/worktree_klasoru_kopya/` —
vault'un tam kopyası, **2904 dosya / 147.7 MB** — 5 gün görülmedi. İçinde **üçüncü**
bir pano izi de vardı (`task_board.json.tmp`, `task_board.json.20260922_130508.bak`).
Ders: derinliğe bakmayan mandal, derinde saklananı hiç yakalamaz. D-228'in ihlali
yeniden doğmadı, hiç bitmemişti.

**Ölçüm (2026-09-27, tahmin değil):**

| Ölçüt | Değer |
|-------|-------|
| `backups/` toplam dosya | 2904 (147.7 MB) |
| Git'te izlenen | 0 |
| `.pyc` hariç | 1661 |
| İçerik-eşsiz (kıyas tabanı: çalışma kökü) | 776 |
| …aynı adlı canlı dosya var (eski sürüm) | 602 |
| …adı da hiçbir yerde yok (aday) | 174 |
| …git geçmişinde adı var (kurtarılabilir) | 53 |
| **…hiçbir yerde yok — sahi eşsiz** | **121** |

**Üç aşamalı silme güvenlik süzgeci** (D-228'in inceltilmiş hâli):

1. SHA-256 içerik eşsizliği — içerik canlı ağaçta var mı?
2. Aynı **ad** canlıda var mı? Varsa eşsiz değil, **eski sürüm**.
3. Ad `git log --all --name-only` geçmişinde var mı? Varsa **geçmiş zaten yedektir**
   (D-229), silmek kayıp değil.

Yalnız üçünden de geçen sınıf arşive değer.

**Uygulama:** 121 sahi eşsizden bilgi taşıyan **96** dosya (`.md`/`.py`/`.yml`/
`.canvas`) `_ARSIV_backups_essiz_2026-09-27/` altına kopyalandı; süreç artığı **25**
(`.zip` anlık görüntü, `.patch` fark, 24525 satırlık `app.log`, tek kullanımlık betik
çıktısı) silindi; sonra tüm ağaç kaldırıldı.

**İki ölçüm hatamı açıkça düzelttim:**

- İlk taramada yedek tarafı **0** saydı: `backups`'ı canlı taraftan çıkarmak için
  koyduğum dizin filtresini yedek tarafına da uygulamışım. Filtre tarama köküne göre
  **parametrik** olmalı.
- İlk kıyas tabanı yalnız vault'tu; ama yedek `AI proje v1/` ve `_ARSIV_*` gibi
  **çalışma kökü** klasörlerini yansıtıyor. Taban kök olmalı, yoksa "eşsiz" şişer
  (780 → 776 ve sınıflandırma tamamen değişti).

**Mandal:** [`tests/test_kok_izin_listesi.py::test_gomulu_govde_kopyasi_yok`](tests/test_kok_izin_listesi.py:130)
— `VAULT.rglob("*")` ile **disk** taranır, çünkü bu kopya hiç izlenmemişti (git'te 0):
sorun versiyonlama değil gövdenin kendisiydi. Tavan `GOMULU_KOPYA_TAVANI = 0`
(D-220: yalnız küçülebilir).

```bash
python -m pytest tests/test_kok_izin_listesi.py -q
```

Negatif kontrol: kopya dizini geri yaratıldığında ölçüldü →
`AssertionError: D-230 ihlali: gomulu govde kopyasi -> [...] (tavan 0)`.

- **Referans:** D-186/D-187 (yedeği üreten faz), D-220 (tavan yalnız küçülür),
  D-223 (yedekte kalan doküman pratikte yoktur), D-228 (paralel gövde yasağı —
  derinlik kör noktası burada kapandı), D-229 (geçmiş zaten yedektir).

## Arşiv Panonun Devamıdır, Yokluğu Değil (D-231 — KAHİN kararı 2026-09-27)

**Kural:** Bir `task_id` panoda yoksa **öksüz sayılmaz**; önce arşive bakılır.
Panoda yok + arşivde var = **kapanmış iş**, bulgu üretmez. Tek istisna: kuyruk
durumu `bekliyor` ise arşivlenmiş işe bekleyen onay **gerçek çelişkidir**, `hata`
kalır. Pano tutarlılığı sorgulayan her araç `arsiv_kimlikleri()` ile çalışır.

**Neden:** Onay kuyruğu bir **ekleme günlüğüdür**; kapanan iş `task_board.json`'dan
`task_board_arsiv_*.json`'a taşınır. D-198 `arsivde_bul()`'u mükerrer kapısı olarak
zaten kullanıyordu, ama `pano_denetim.tara()` onu hiç çağırmıyordu: arşivi yokluk
sayıp her kapanmış işi "orphan" diye bağırıyordu. 216 uyarı = gürültü tabanı;
gürültü tabanı olan denetim okunmaz, okunmayan denetim bekçi değildir.

**Ölçüm (2026-09-27, tahmin değil):**

| Ölçüt | Değer |
|---|---|
| Pano kaydı | 74 |
| Kuyruk kaydı | 257 (252 onaylandı, 5 reddedildi) |
| Panoda olmayan kuyruk kaydı | 216 (200 tekil `task_id`) |
| **Arşivde bulunan** | **196** |
| **Hiçbir yerde yok (sahi öksüz)** | **4** — `MIG-UI-01`, `MRK-05`, `ROO-REV-01`, `U-11` |
| Kuyrukta mükerrer `task_id` | 15 (en çok `DASH-UX-02a`, `VEC-TEST-01`, `UI-MIMARI-02` = 3) |
| Denetim uyarısı (önce → sonra) | **216 → 4** |

**Teşhis yanlıştı, ölçüm düzeltti:** Görev listesi "216 orphan kuyruğu buda"
diyordu. Budama **196 doğru kaydı silmek** olurdu; kuyruk doğru, denetim kördü.
D-224 bu yüzden var: kırmızıyı ölçmeden iş açılmaz.

**Uygulama:** `arsiv_kimlikleri() -> frozenset[str]` arşiv dosyalarını **bir kez**
okur (`arsivde_bul()` çağrı başına hepsini okur; 200 kimlik için O(n·m)).
`tara(..., arsiv: frozenset[str] = frozenset())` — varsayılan boş küme eski
davranışı korur, çağrı yerleri zorla değişmez. `main()` içindeki **iki** `tara()`
çağrısı da beslenir; `--uygula` sonrası yeniden tarama atlanırsa 196 yanlış uyarı
geri gelir.

**Mandal:** [`tests/test_pano_denetim.py::test_gercek_kuyrukta_orphan_uyarisi_tavani_asmaz`](tests/test_pano_denetim.py:98)
— gerçek pano+kuyruk okunur, tavan `ORPHAN_UYARI_TAVANI = 4` (D-220: yalnız küçülür).
Yanına iki birim mandalı: arşiv bilinince uyarı susar, `bekliyor` susmaz.

```bash
python -m pytest tests/test_pano_denetim.py -q
python scripts/pano_denetim.py
```

Negatif kontrol: `test_arsivlenmis_gorev_icin_bekleyen_onay_hata_kalir` — arşivlenmiş
`task_id` için `durum="bekliyor"` kaydı hâlâ `seviye="hata"` üretir; susturma
kapsamı `bekliyor`a sızarsa test kırılır.

- **Referans:** D-198 (arşiv mükerrer kapısıdır — mevcut araç kullanılmıyordu),
  D-220 (tavan yalnız küçülür), D-224 (ölçülmemiş kırmızıyla iş açılmaz — teşhisi
  bu kural çürüttü), D-186 (pano kanonik yol bekçisi).

## Gövde Kopyası İsminden Değil Yapısından Tanınır (D-232 — KAHİN kararı 2026-09-27)

**Kural:** İkinci gövde tespiti **isim imzasına** dayanmaz. Vault tepesinde tek
olması gereken uygulama dosyaları (`web_app.py`, `app.py`) alt dizinlerin herhangi
birinde görünüyorsa o dizin bir gövde kopyasıdır — adı ne olursa olsun. Tavan 0.
Ayrıca: **izlenen bir ağaç silinirken `git log --all` üçüncü aşama huni geçersizdir**;
ağacın kendi git öneki tarih kümesinden çıkarılmadan yapılan ölçüm her dosyayı
"zaten arşivde" sayar.

**Neden:** D-228 mandalı `VAULT.iterdir()` kullandı → yalnız üst seviye → derindeki
kopya 6 gün yaşadı (D-230 bunu kapattı). D-230 mandalı derine bakıyor ama
`GOMULU_KOPYA_IMZALARI` **sabit isim listesi**; `"AI proje v1"` o listede yoktu →
787 dosya / 400 `.py` / 42.7 MB tam bir ikinci gövde görünmedi. Üstelik D-221
`YASAK_GOVDELER` **"AI proje v1"'i adıyla içeriyordu**, ama yalnız `KOK` altına
bakıyordu; gövde vault'un *içine* girince mandal hiç tetiklenmedi. Üç mandal, üç
kör nokta, hepsi aynı hata: **isim ve yer sayıldı, yapı sayılmadı.** İsme bakan
bekçi her yeni isme kör; yapıya bakan bekçiyi aldatmak için gövde dosyasının adını
değiştirmek gerekir, o da kopyayı çalışmaz kılar.

**Ölçüm (2026-09-27, tahmin değil):**

| Ölçüm | Sonuç |
|---|---|
| Görev iddiası | "143 eşsiz dosya birleştir" |
| Ağaç nerede | Kökte **değil**, `Huginn Data Insights/AI proje v1/` |
| Ağaç | 787 dosya / 42.7 MB / 741 git'te izlenen / 400 `.py` |
| İçerik-hash eşsiz | 496 |
| + adı canlıda yok | 187 |
| + adı git geçmişinde de yok (sahi eşsiz) | **41** (40 `.md` + 1 `.txt`, hepsi belge, **0 kod**) |
| 41'den git'te izlenen | 40 |
| **Gerçekten kaybolacak olan** | **1** → `V10/04_karşılaştırmalar/01_v9_ile_karsilastirma.md` (33.598 B) |
| `.env` 5 anahtarı | 3'ü kökte eski değerle var, 2'si 6-7 karakter (placeholder) → kurtarılacak sır yok |
| Gövde imzası alt dizinlerde | `web_app.py`+`app.py` → **0** (temizlik sonrası tavan) |

**Uygulama:** 1 dosya `_ARSIV_ai_proje_v1_essiz_2026-09-27/`e kurtarıldı; 741 izlenen
dosya `git rm -r --cached` ile elendi (geçmişte duruyor); ağaç diskten silindi.
"Birleştir" yanlış fiildi: git'in zaten tuttuğu 40 dosya birleştirilmez.

- **Mandal:** `tests/test_kok_izin_listesi.py::test_alt_dizinde_ikinci_govde_yok`
  + `test_d232_agents_mde_kayitli`. Negatif kontrol: sahte `x/web_app.py` → kırmızı.
- **Referans:** D-228 (paralel gövde yasağı), D-230 (derinlik), D-224 (iddia değil
  ölçüm - "143" üç kez çürüdü), D-220 (tavan yalnız küçülür).
- **DÜZELTME (aynı gün, D-233 ile):** D-232 uygulaması `AI proje v1/` dizinini
  **bütün olarak** sildi. Yanlıştı. İçindeki `V10/` (94 dosya, **0 `.py`**, 0 gövde
  imzası) ikinci gövde değil, en az 9 modülün okuduğu **canlı bilgi tabanıydı**.
  `V10/` geri alındı; silinen gövde 787 → **647 dosya**. D-232 kuralı geçerli,
  kapsamı düzeltildi: gövde = imza taşıyan ağaç, altındaki her dizin değil.

---

## Referanslı Yol Kopya Değil Bağımlılıktır (D-233 — KAHİN kararı 2026-09-27)

- **Kural:** Bir ağaç silinmeden önce, üç aşamalı içerik hunisine (D-230) **dördüncü
  soru** eklenir: *canlı kod bu yola bakıyor mu?* `grep` ile yol adı aranır; referans
  varsa o yol kopya değil **bağımlılıktır**, silinemez. Referanslar mandalda donar.
- **Neden:** D-232 uygulamasında huni "içerik eşsiz mi / git tutuyor mu" diye sordu.
  41 sahi eşsiz dosyayı *"belge, kod değil → önemsiz"* diye eledim. Oysa belgeler
  kodun **veri girdisiydi**. Sonuç: `gorev_kutusu.py:480` `_SSOT` yolu boşa düştü,
  B-14 hafıza kapısı her teslimi reddetti — `test_cmd_teslim_basarili` kırmızıya döndü.
  Test kırılmasaydı hata **sessizce üretimde** kalacaktı: `telegram_polling` `/wiki`,
  `/state`, `/changelog` komutları, `dashboard.py` proje durumu, `oto_atama.py` TODO
  okuması, `wiki_automation/*` dört modülü. Dosya silme hatası testle yakalandı;
  bu şans değil kalıcı olmalı → mandal.
- **Ölçüm:** `AI proje v1` git'te 741 dosya; `V10/` altı 94 dosya / **0 `.py`** /
  0 gövde imzası → kod değil bilgi tabanı. Gerçek gövde = 647. `grep "AI proje v1"`
  → **43 isabet / 9 canlı modül**. `V10/` geri alındıktan sonra 38 passed.
- **Uygulama:** `git checkout HEAD -- "AI proje v1/V10"`. Vault'ta yalnız `V10`
  kaldı; `src/`, `tests/`, `web_app.py`, `Dockerfile` vb. 647 dosya silinmiş durumda.
- **Mandal:** `tests/test_kok_izin_listesi.py::test_canli_kodun_okudugu_yol_diskte`
  (3 yol parametrik) + `test_d233_agents_mde_kayitli`.
- **Referans:** D-232 (yapısal tespit), D-230 (huni), D-224 (ölçmeden karar yok).

---

## NACE Referansı Tek Kaynaktan Kurulmaz, Seviye Kısaltılmaz (D-234 — KAHİN kararı 2026-09-27)

- **Kural (iki parça, ikisi de zorunlu):**
  1. **Seviye korunur, kısaltılmaz.** Resmi kaynak 6 haneli kod veriyorsa
     (`47.79.04`) 6 hane **asıl** olarak saklanır; 4 hane (`47.79`) ve 2 hane
     (`47`) ondan **türetilip ayrıca** yazılır. "6 varken 4 yazmak yanlış"
     itirazı haklıdır — bu yüzden 4 hane asılın yerine değil, **yanına** yazılır.
     Hiçbir seviye silinerek diğerine indirgenmez.
  2. **Referans birleşiktir.** `nace_codes` tek bir dosyadan doldurulamaz.
     `data/nace/` altındaki **dört** kaynak birleştirilir:
     `sektor_meslek_nace_*_resmi.xlsx` (esnaf/sanatkâr meslek kolları),
     `turkiye_nace.json`, `nace-rev-2-1.json`, `nace-rev-2.json`.
     Yeni kaynak eskisinin **yerine konmaz**, üstüne eklenir.
- **Neden (ölçüm, canlı Supabase, 8900 firma / 464 eşsiz kod):**
  - Canlı `nace_code` şekli **%85.9 dört haneli**, %7.6 altı haneli. Resmi xlsx
    ise **tamamen altı haneli**. Kısaltma yapılmazsa bu %85.9 hiç eşleşmez.
  - Yalnız türetme sayesinde eşleşen firma: **3595 (%40.4)**. Türetme yoksa bu
    firmalar sektörsüz kalır.
  - **Tek kaynak (xlsx) yetmiyor:** türetmeyle bile **%52.3 eşleşmedi**.
    Eşleşmeyenler çöp değil, gerçek NACE'ler: `29.10` (1882 firma), `62.09`
    (655), `62.01` (634), `41.10` (600) — hepsi xlsx dışında, json'larda var.
  - **Dört kaynak birleşince:** eşleşme **%47.7 → %92.9**. Kalan %7.1'in
    büyük kısmı zaten D-... kapsamındaki sayaç çöpü (`1163`, `794`, `757`).
- **Zaten elimizde olan yapı:** `turkiye_nace.json` (2142 satır) her kayıtta
  `code_6digit` **ve** `code` (4 hane) alanlarını birlikte taşıyor. Kural bunu
  icat etmiyor, mevcut doğru yapıyı zorunlu kılıyor.
- **Yasak:** "yeni resmi liste geldi, eskiyi silelim" — ölçüm bunun %45 kapsam
  kaybı demek olduğunu gösterdi.
- **Mandal:** `tests/test_nace_referans_kurali.py`
- **Referans:** D-224 (iddia değil ölçüm), VERI-NACE-SOZLUK-01 (uygulama görevi).

## Veri Kaynağı Kuralları Dökümanda, Mandalda Zorlanır (D-235 — KAHİN kararı 2026-09-27)

Kazıyıcı ve veri kaynağı kuralları **tek yerde** tutulur: `docs/VERI_KAYNAK_KURALLARI.md`
(K-1…K-5, her satırda ölçülmüş sayı + mandal sütunu). Kural metni buraya kopyalanmaz.

Bağlayıcı olan üç madde:
1. Kural **mandalsız yazılmaz** — testi olmayan satır "tavsiye" etiketiyle durur, kural sayılmaz.
2. Liste kazıyıcısı **kendi `while True` sayfalama döngüsünü yazamaz**; `BaseOsfbScraper.sayfa_dongusu()` kullanılır. Eski borç test içindeki `IZIN_LISTESI`'nde durur; liste yalnız **küçülür**.
3. Veri kaynağı `kaynak_adi` + `kaynak_turu` (`osb`/`oda`) ile tanımlanır; güven seviyesi türden **türetilir**, elle atanmaz.

**Neden.** İvedik kazıyıcısı 3375 satır yazdı, içinde **14 tekil firma** vardı (%99.6 kopya); WordPress geçersiz sayfaya 404 değil sayfa 1 döndüğü için `if not firmalar: break` asla tetiklenmedi. Aynı hata üç kazıyıcıda **bağımsızca** tekrar etti — ortak şablon ve makine denetimi olmadığı için. Mandal yazıldığı anda dördüncü bir borç (`baskent_scraper.py` ekleme kipi) kendiliğinden yakalandı ve düzeltildi.

- **Mandal:** `tests/test_kaziyici_sablon_denetimi.py` (9), `tests/test_kaziyici_sayfa_dongusu.py` (5)
- **Referans:** `docs/VERI_KAYNAK_KURALLARI.md`, VERI-KAZIYICI-DONGU-01, VERI-KAYNAK-TURU-01.

## Tüketicisi Olmayan Çıktı Üretilmez (D-236 — KAHİN kararı 2026-09-27)

Bir dosya/alan/rapor üretiliyorsa **onu otomatik okuyan bir tüketici** olmalı. Tüketicisi
yalnız "elle bakılabilir" olan çıktı **üretilmez** — kaldırılır, bilgi asıl kaydına yazılır.

Bağlayıcı olan iki madde:
1. Yeni bir yan dosya (`*.ALARM.json`, `*_rapor.json`, `*.flag` vb.) eklenmeden önce
   **hangi kodun onu okuyacağı** yazılır. Okuyan yoksa alan asıl kayda eklenir.
2. Aynı bilgiyi iki yere yazmak **yasaktır**; ikinci kopya kaçınılmaz olarak bayatlar.

**Neden.** `nobetci` her turda `<ajan>.ALARM.json` yazıyordu; `tetik_senk` her turda aynı
dosyayı siliyordu. Ölçüm: canlı `triggers/` içinde **0 ALARM dosyası**, `_trash`/`_yedek`
içinde **54 kopya** — üretici ile silici birbirini iptal eden ölü döngü kurmuştu. Dosyanın
içeriği (`uyari_sayisi`, `uyari_tarihi`) zaten tetik kaydında duruyordu; tek tüketicisi iki
elle komuttu. 282 kayıtlık `utku.ALARM.json`'ın **38'i kapalı görev içindi** — kopya bayatlamıştı.

- **Mandal:** `tests/test_gorev_nobetci.py::test_tetik_firlat_olusturur_log` (ALARM üretilmediğini doğrular)
- **Referans:** D-166 (kök kirliliği), [`nobetci.py`](src/company_master/orchestrator/nobetci.py:66).

## Kapanan İşin Hafıza Kaydı Denetlenir (D-237 — KAHİN kararı 2026-09-27)

Bir görev `done` olduğunda sahibinin **kişisel context dosyasına** (`<ajan>_project_context.md`)
kayıt düşülmesi zaten kuraldı. Bu tarihten sonra kural **ölçülür**: `pano_denetim`
kapalı her görevi sahibinin dosyasında arar, bulamazsa `[uyari/kayit]` üretir.

Bağlayıcı olan üç madde:
1. Görevi kapatan ajan, `task_id`'yi kendi context dosyasında **geçirmek zorundadır**.
2. Denetim yalnız `bitis >= 2026-09-28` görevleri kapsar; geriye dönük 58 görev için
   uyarı üretilmez — yoksa denetim gürültüye boğulur ve hiç okunmaz.
3. Context dosyası olmayan sahipler (kahin, orkestrator) denetlenmez.

**Neden.** Ölçüm: 59 kapanmış görevin **yalnız 1'i** (%1.7) sahibinin dosyasında geçiyordu.
Kayıt tutulmayınca bilgi bir sonraki oturuma taşınmıyor; aynı ölçüm tekrar yapılıyor,
aynı hata tekrar ediliyor. D-236'ya **aykırı değildir**: tek kopya, asıl kayda yazılır —
denetim yeni dosya üretmez, var olan dosyayı okur.

- **Mandal:** `tests/test_pano_denetim_kayit.py` (6 test)
- **Referans:** D-66 (kanıtsız done yok), [`pano_denetim.py`](scripts/pano_denetim.py:117).

## Veri Ölçümü Canlı Veritabanında Yapılır (D-238 — KAHİN kararı 2026-09-27)

Bu projede **tek üretim veritabanı Supabase Postgres'tir**. Firma verisiyle ilgili
her sayı — teslim raporunda, denetimde, keşif notunda — canlı Postgres'ten ölçülür.
Yerel `.db` / `.sqlite` dosyaları **yalnız test ve tarihsel yedek** amaçlıdır;
hiçbirinden alınan sayı kabul ölçütü olamaz.

Bağlayıcı olan dört madde:
1. Bir veri sayısı bildirilirken **hangi kaynaktan** ölçüldüğü yazılır
   (`Supabase / aws-0-eu-west-2.pooler`). Kaynağı yazılmayan sayı ölçülmemiş sayılır.
2. Veri **değiştiren** iş (DELETE/UPDATE/migration) yerel SQLite'ta çalıştırılıp
   canlı sayılarla raporlanamaz. Betik nereye bağlandıysa rapor orayı söyler.
3. Denetçi, teslim raporundaki sayıyı **kendi bağımsız sorgusuyla** doğrular.
   Eşleşmiyorsa teslim reddedilir — açıklama beklenmez.
4. Yedek dosyası kanıttır: **satır sayısı + dosya yolu + örnek içerik** bildirilir.
   Üç satırlık "FIRMA A" içeren dosya yedek değildir.

**Neden.** VERI-HAYALET-TEMIZ-01 teslimi dört iddiada da çöktü: canlı `companies`
14003 satır / 9412 tekil (temizlik öncesiyle birebir aynı), `uq_companies_legal_name`
indeksi yok, yedek dosyası 3 satır test verisi. Sebep kötü niyet değil **yanlış yere
bağlanmak**: betik yerel SQLite'ta koştu, rapor canlı sayılarla yazıldı.
Aynı hatayı KAHİN de yaptı (D-234 öncesi NACE ölçümü `backups/…pre_dedup.db`
üzerindeydi) — kural bu yüzden herkesi bağlar, sadece uygulayıcıyı değil.

**Ölçülen kanıt (2026-09-27).** Depoda 9 SQLite dosyası var; `companies` tablosu
yalnız ikisinde: `backups/company_master_pre_dedup_20260908_090326.db`
(8313 satır / 8275 tekil, 2026-09-02 tarihli) ve `data/_tmp/ci_probe.db` (0 satır).
Canlıyla fark **5690 satır** — yani iki taraf aynı veriyi tutmuyor, yedek 25 gün eski.
`sqlite3` Python'un gömülü modülüdür, bu bilgisayarda ayrı kurulum yoktur;
ajanların test için SQLite kullanması **doğrudur**, hata dosyanın varlığı değil
**ölçümün oradan alınmasıdır**.

- **Referans:** D-224 (ölçmeden karar yok), D-166 (ölçülmüş kanıtla teslim),
  D-66 (kanıtsız done yok), D-234 (aynı hatanın ilk vakası).

## Kural Kapısı Üretim Anında Durur (D-239 — KAHİN kararı 2026-09-27)

Bir kuralın mandalı yalnız **test** olursa, kural ihlali *commit sonrası* yakalanır —
yani iş çoktan yapılmıştır. Üretim komutu varsa (`ata`, `guncelle`, `bitir`) kapı
**o komuta** konur. Test mandal olarak kalır, kapı olarak değil.

Bağlayıcı olan üç madde:
1. Bir kuralın gövdesi (kontrol fonksiyonu) **tek dosyada** yaşar. Test ve üretim
   komutu aynı gövdeyi çağırır; ikinci kopya yazmak D-211 ihlalidir.
2. Kuralı çiğneyen girdi üretim komutundan **geçemez** — sıfır olmayan çıkış kodu.
3. Geriye dönük düzeltme kapının ön koşulu **değildir**. Kapı bugünden ileri çalışır;
   eski kirlilik mandalla dondurulur (D-220 deseni).

**Neden.** Ölçüm: 9 brif şablonsuz yazılmıştı, **108 eksik bölüm**. `test_brief_sablon_denetim.py`
kuralı doğru biliyordu ama `gorev_at.py ata` onu çağıramıyordu — kural gövdesi testin
*içinde* yaşıyordu. Sonuç: uyumsuz brifle görev atanabiliyordu, ihlal ancak sonraki
pytest koşusunda görünüyordu. Gövde [`scripts/brief_denetim.py`](scripts/brief_denetim.py:44)
dosyasına taşındı; artık `ata` komutu uyumsuz brifte **çıkış kodu 7** ile durur.

**Kök dizin için aynı kural — ama şimdi değil.** Ölçüm (2026-09-27): kökte **96** `.py`
vardı; **3'ü sözdizimi hatalıydı** (hiç çalışmıyordu, `_ARSIV_bozuk_betik_2026-09-27/`
klasörüne alındı → **93**). Kalanların **53'ü** panoya/`task_board.json`'a doğrudan
erişiyor, **10'unda** docstring var, **0'ında** `argparse`. Bunlar D-221'in izin
listesinde değil. Yine de **bugün taşınmıyorlar**: hiçbiri git'te takipli değil
(`git ls-files` boş), yani taşıma geri alınamaz ve 53 dosyanın pano erişimi tek tek
doğrulanmadan taşınırsa çalışan bir şeyi kırma riski ölçülmemiştir. D-221 zaten
"kural önce kanamayı durdurur, içeriği tek tek temizlemez" diyor.

**Tetikleyici koşul (bu olursa iş açılır):** kök `.py` sayısı **93'ü aşarsa** ya da
bir ajan kökteki betiklerden birini iş akışında kullanmak zorunda kalırsa.
Üst sınır **93**, yalnız küçülür (D-220).

- **Mandal:** `tests/test_brief_sablon_denetim.py` (17 test, gövdeyi
  `scripts/brief_denetim.py`'den import eder — ikiz mantık imkânsız).
- **Referans:** D-217 (brif şablonu), D-211 (ikiz gövde yasağı), D-221 (kök izin
  listesi), D-220 (tavan yalnız küçülür), D-66 (brif zorunlu).

---

### D-240 — Brif arşiv klasörü REDDEDİLDİ: yol taşımanın bedeli faydasından büyük

**Karar.** `plans/` altındaki 124 brif **taşınmaz**. Kapanmış brifleri
`plans/_arsiv_brief/` altına almak için açılan iş, ölçüm sonrası **reddedildi**.
Dosyalar bulundukları yerde kalır.

**Neden (ölçüm, 2026-09-27).**
1. **108 yol kırılırdı.** Pano kayıtları brif yolunu metin olarak tutuyor:
   **59** canlı görev + **49** arşiv kaydı. Taşıma, 108 yolun tek tek
   güncellenmesini zorunlu kılar.
2. **D-66 kapısı çökerdi.** [`gorev_ekle()`](src/company_master/orchestrator/task_board.py:308)
   brif diskte yoksa `ValueError` fırlatır. Güncellemesi kaçan her yol, o görevin
   panoya bir daha girememesi demektir — sessiz değil, gürültülü kırılma.
3. **Kazanç sıfıra yakın.** Denetim gövdesi zaten `rglob` kullanıyor; alt klasör
   **bugün de** destekleniyor, taşımaya gerek yok. Ajanlar `plans/` klasörünü
   listelemiyor — brif yolunu panodan alıp **tek dosya** okuyor. 124 dosyanın
   varlığı kimsenin bağlamına girmiyor, token yakmıyor.
4. Geriye kalan tek fayda Obsidian'da klasörün göze temiz görünmesiydi.

**Genel kural (bundan sonrası için).** Düzen amaçlı taşıma önerisi geldiğinde
**önce kaç referansın kırılacağı sayılır**. Referans sayısı, düzenin sağladığı
ölçülebilir kazançtan (token, süre, hata) büyükse taşıma yapılmaz. "Göze temiz
görünmek" ölçülebilir kazanç değildir.

- **Mandal yok** (bilinçli): bu bir *yapmama* kararıdır, mandallanacak davranış
  yoktur. Karşı yön zaten D-66 kapısıyla mandallı — yol kırılırsa görev eklenemez.
- **Referans:** D-66 (brif diskte zorunlu), D-221 (kural kanamayı durdurur, geçmişi
  tek tek temizlemez), D-220 (tavan yalnız küçülür).

---

### D-241 — Dış kök (git deposu kökü) izin listesiyle kapalıdır

**Karar.** Dış kökte (`<depo>/`, vault'un bir üstü) yalnızca **4 dosya** bulunur:
`.gitignore`, `AGENTS.md`, `tsconfig.json`, `n8nac-config.json`. Bu liste
**büyümez**. Tek kullanımlık betik, ölçüm çıktısı, ekran görüntüsü, döküm dosyası
kökte **duramaz** — alt klasöre iner.

**Neden — D-221 mandalsız yazılmıştı.** Ölçüm (2026-09-27): dış kökte **131 dosya**
birikmişti (96 `.py`, 22 `.png`, 9 döküm). İki bağımsız kusur aynı noktaya çarptı:
1. `.gitignore` deseni **zaten vardı** (`check_*.py`, `fix_*.py`, `_*.py`, `output*.txt`)
   — ama dosyalar **takipli** olduğu için `.gitignore` onlara hiç uygulanmadı.
   `.gitignore` yalnız *takipsiz* dosyayı durdurur; takipli dosya için sessizdir.
2. D-221'in kendi metni "listesi `tests/test_kok_politikasi.py` ile sabitlenir"
   diyordu — **o dosya hiç yazılmamıştı**. Kural kendi mandalına atıfta bulunup
   mandalı kurmamış.

Sonuç: iki yıllık birikmenin sebebi kuralın yokluğu değil, **kuralın kapısızlığı**.
D-211'in "kural gövdesi çalıştırılabilir olmalı" ilkesinin kök dizin karşılığı.

**Yapılan.** 131 dosya **0 referans** ölçümünden sonra (`git grep -F`, 130 ad,
hiçbiri başka dosyadan çağrılmıyor) `git mv` ile sınıflandırılarak arşive alındı —
takipli taşıma, yani `git mv` ile geri alınabilir:
`_ARSIV_kok_betik_2026-09-27/{sorgu_check:35, duzeltme_fix:38, ekran_goruntusu:22,
olcum_gecici:12, cikti_dokumu:9, muhtelif:14}`. Kök: **131 → 4**.

**Ek tespit — `.gitignore` tek başına mandal değildir.** Takipli bir dosya için
`.gitignore` hiçbir şey yapmaz. Kök temizliği ancak **dosya sistemini okuyan bir
test** ile korunur; desen yazmak yeterli sanılırsa kirlilik sessizce birikir.

- **Mandal:** [`tests/test_kok_politikasi.py`](tests/test_kok_politikasi.py:41)
  (3 test: izinsiz dosya yok, izinsiz klasör yok, izin listesi ≤ 4 kalır).
  Kapının çalıştığı **kırmızı yakarak** doğrulandı: taşıma betiği kökte kaldığı
  anda test `Dis kokte 1 izinsiz dosya: ['_kok_tasima.py']` ile düştü.
- **Tavan:** izin listesi **4**, yalnız küçülür (D-220). Yeni dosyaya yer açmak için
  listeyi büyütmek ihlaldir — dosya alt klasöre ait.
- **Referans:** D-221 (kök politikası, mandalı bu kararla kuruldu), D-211 (kural
  gövdesi çalıştırılabilir olmalı), D-220 (tavan yalnız küçülür), D-223 (silme değil
  arşiv).

---

### D-242 — Yedek/arşiv tek çatı altında; `Path.match` glob sanılmaz

**Karar.** Tüm arşiv ve yedek klasörleri **tek kök** altında toplanır:
`<depo>/yedekler/` (git takipsiz, `.gitignore:10`). İki alt yapı: `yedekler/*.bundle|*.zip`
(repo yedeği) ve `yedekler/arsiv/_ARSIV_*` (taşınan içerik). Dış kökte dağınık
`_ARSIV_*` klasörü **bırakılmaz**.

**Neden — ürün sahibi tespiti (2026-09-27).** Dış kökte **7 ayrı** `_ARSIV_*`
klasörü birikmişti; `yedekler/` zaten aynı işi yapıyordu. İki yerde iki farklı
"arşiv" kavramı, "bu şey nerede?" sorusunu her seferinde yeniden sordurur —
oysa arşivin tek amacı **aramayı kolaylaştırmaktı**. D-241 kökü 131→4 indirirken
arşiv klasörlerini kökte bırakmıştı: temizlik yarım kalmış.

**Yapılan.** 7 klasör `yedekler/arsiv/` altına taşındı. **377 dosya** diskte
korunuyor (ölçüldü); git indeksinden **265 yol** düştü. İçerik geçmişte durur,
`git show <commit>:<yol>` ile erişilir — D-223'ün "silme değil arşiv" ilkesi
korunur, çünkü dosyalar hem diskte hem geçmişte.

**Yan kusur — `Path.match` glob değildir.** [`muaf_dosya()`](scripts/marka_denetim.py:89)
muafiyeti `Path(bagil).match(desen)` ile ölçüyordu. `Path.match`'te `*` **tek
segmente** bağlıdır: `plans/*` deseni `plans/_arsiv_brief/x.md` yolunu **eşlemez**.
Yani alt klasör açıldığı an muaf dosyalar sessizce ihlal sayılacaktı.
[`fnmatch`](scripts/marka_denetim.py:100) ile değiştirildi — orada `*` ayırıcıyı
da kapsar.

**Genel kural.** Yol desenini "glob gibi" kullanacaksan `fnmatch` kullan.
`Path.match` segment tabanlıdır ve alt klasör açıldığında **sessizce** kapsam
daraltır — kırmızı yakmaz, sadece yanlış cevap verir. Muafiyet/izin listesi
yazan her yerde bu ayrım yorumda belirtilir.

- **Mandal:** [`tests/test_marka_denetim_muafiyet.py`](tests/test_marka_denetim_muafiyet.py)
  (alt klasördeki muaf dosya ihlal sayılmıyor) + [`tests/test_kok_politikasi.py`](tests/test_kok_politikasi.py)
  (dış kökte izinsiz klasör yok — `_ARSIV_*` geri doğarsa kırmızı yanar).
- **Referans:** D-241 (dış kök izin listesi), D-223 (silme değil arşiv), D-211
  (kural gövdesi çalıştırılabilir olmalı).

### D-243 — Prova diske yazmaz; yıkıcı işin yedek yolu enjekte edilebilir olur

**Karar.** `dry_run` / prova kipindeki hiçbir iş **diske yazmaz** ve dönüşünde
`backup_path` **None** verir. Yıkıcı iş yazan her betik yedek yolunu **parametre**
olarak alır (varsayılan `yedekler/<is>_<tarih>.jsonl`, D-242 çatısı); sabit yol
gömülmez. Yedek satır sayısı silinecek satır sayısına **eşit değilse** silme
`RuntimeError` ile iptal olur.

**Neden — KAHİN denetimi (2026-09-27, VERI-HAYALET-TEMIZ-01 reddi).** Ajan işi
"review"a taşımıştı. Ölçüm: kabul kriteri **4591** satır yedek diyordu, diskteki
yedek **3 satırdı** ve içeriği `FIRMA A` / `FIRMA B` — yani **test verisi**.
Üç ayrı kusur üst üste binmişti:

1. [`run_cleanup()`](src/company_master/etl/hayalet_kayit_temizle.py:308) yedek
   almayı `dry_run` kontrolünün **dışında** çağırıyordu — prova diske yazıyordu.
2. Yedek yolu **sabitti**, test enjekte edemiyordu; mock'lu `dry_run=True` testi
   üretim `data/backup/` dizinine yazdı ve dosya **git'e girdi** (2 commit).
3. Gerçek temizlik **hiç çalıştırılmamıştı** — yalnız kod yazılmış, iş bitmiş
   sanılmıştı.

**Genel kural — testin kirlettiği yer, yeşil testin göremediği yerdir.** 11 test
yeşil yanarken üretim yedek dizinine sahte firma kaydı düşüyordu. Yeşil test
"yan etki yok" demek **değildir**. Bir testi silip tekrar çalıştırmak
(`del <dosya>` → `pytest` → dosya geri doğdu mu?) yan etkiyi ölçen en ucuz
kontroldür; şüphelenilen her yazma işinde uygulanır.

**Kusur 4 — yetim yıkıcı ikiz.** Aynı işte `hayalet_kayit_temizle_fast.py`
adında **431 satırlık kod ikizi** duruyordu: çağıran yok, testi yok,
`dry_run` parametresi **hiç yok**, doğrudan `DELETE FROM companies` atıyor.
Kod ikizi tek başına kokudur; **prova kipi olmayan yıkıcı ikiz** kazadır —
biri "hızlısını çalıştırayım" der, 4591 kayıt yedeksiz gider. Silindi.
**Kural:** aynı işi yapan ikinci dosya yazılmaz; hızlandırma asıl dosyaya
işlenir. Yıkıcı iş yazan her dosyada `dry_run` **zorunludur**.

**Kusur 5 — parti silme ikizde kalmıştı.** Asıl dosya 4591 kimliği **tek
sorguda** placeholder olarak diziyordu; ikiz bunu 1000'lik partiye bölmüştü
ama düzeltme asıl dosyaya **taşınmamıştı**. Parti asıl dosyaya alındı, tüm
partiler **tek `engine.begin()`** içinde: yarım silme olmaz.

**Ürün sahibi düzeltmesi — hangi veritabanı?** İlk yorumumda "SQLite 999 limiti,
üretimde patlar" yazdım; ürün sahibi "gerçek veri Supabase'de" diye uyardı ve
ölçüm onu doğruladı: `DATABASE_URL=postgresql://...`, PostgreSQL limiti **65535**
— 4591 orada **patlamazdı**. Parti gerekçesi yanlıştı, parti kararı doğru:
aynı kod test/yerel **SQLite** yolundan da geçiyor (999). **Genel kural:** SQL
limiti/lehçe gerekçesi yazarken hedef veritabanı `DATABASE_URL`'den **ölçülür**;
"veritabanı" diye tek kelime yazılmaz — bu projede **iki** hedef var
(üretim PostgreSQL/Supabase + test SQLite) ve kod ikisinden de geçmek zorundadır.

**Ayrıca — yorum kodla çelişemez.** Aynı işin migration'ı "partial index
kullanıyoruz" diyordu ama `WHERE` yoktu. Yorum, kodun **söylediğini** anlatır;
niyeti anlatıp uygulamayı atlayan yorum yanlış bilgidir.
[`0022_unique_legal_name.sql`](src/company_master/schema/migrations/0022_unique_legal_name.sql:5)
`WHERE legal_name IS NOT NULL` eklenerek yoruma uyduruldu.

- **Mandal:** [`tests/test_hayalet_kayit_temizle.py`](tests/test_hayalet_kayit_temizle.py:207)
  — `dry_run` sonrası `backup_path is None` **ve** `data/backup/hayalet_*.jsonl`
  boş; prova diske yazarsa kırmızı yanar.
- **Referans:** D-242 (yedek tek çatı `yedekler/`), D-211 (kural çalıştırılabilir
  olmalı), D-66 (brif maddesi ölçülmüş değere dayanır).

### D-244 — Canlı veritabanı yıkıcı iş: yedek dosyası kanıt, "yapıldı" beyanı değil

**Karar.** Üretim veritabanında satır silen/güncelleyen hiçbir iş, `yedekler/`
altında **o işe ait yedek dosyası diskte durmadan** `done` olamaz. Kapanış
kanıtı üç parçadır ve üçü de brife yazılır: (1) yedek dosya yolu + satır
sayısı, (2) işlem öncesi/sonrası `COUNT(*)`, (3) korunması vaat edilen alanın
öncesi/sonrası sayısı. Kanıtı üretilemeyen iş `blocked` olur, `review` olmaz.

**Neden — KAHİN ölçümü (2026-09-27, D-243'ün devamı).** D-243'te "gerçek
temizlik hiç çalıştırılmamıştı" diye yazdım. Canlı Supabase'i ölçünce tablo
tersine döndü: temizlik **çalıştırılmış**. `companies` **9412** satır,
`legal_name` fazlalığı **0**, `uq_companies_legal_name` index **mevcut** —
yani 4591 satır silinmiş ve migration 0022 uygulanmış. Ama:

- `yedekler/` dizini **hiç yoktu**; diskteki tek yedek D-243'te bulunan
  3 satırlık test verisiydi ve o da git'ten silinmişti.
- Silinen 4591 satır **hiçbir yerden geri getirilemiyor**. Ham kazı dosyaları
  kurtarma kaynağı değil: `data/aso/*` 0, `data/baskent/*` 0,
  `data/ivedik/*` 0, `data/merged/multi_osb_merged.jsonl` 0 — hiçbirinde
  `vergi_no` yok. Vergi numaraları ayrı bir zenginleştirme işinden gelmiş ve
  yalnız veritabanında yaşıyordu.
- Kabul kriteri "774 `vergi_no` korunur" diyordu; ölçüm **761**. Fark 13.
  Ama kriterin kendisi hatalı yazılmış: 774, **14003 satırlık kirli tabloda**
  sayılmıştı. Aynı ünvanın iki kaydında da vergi numarası varsa tekilleşince
  sayaç bir düşer — **veri kaybı değil, mükerrer sayımın erimesi**. 494 tekrarlı
  grubun 13'ünde bu durumun olması beklenen bir sonuç. Doğru kriter
  `count(distinct vergi_no)` olmalıydı; satır sayısı tekilleştirmeden sonra
  zaten korunamaz. Kanıt yine de yok (öncesi kaydı yok), ama fark artık
  **açıklanabilir** ve alarm gerektirmiyor.

**Genel kural — geri alınamazlığın maliyeti, işin süresinden bağımsızdır.**
"Yedek al" adımı 40 saniye sürüyordu; atlanınca 4591 satır kalıcı gitti.
Yıkıcı işte sıra asla değişmez: **yedek → doğrula → sil**. Yedek adımı
başarısız olursa iş başlamaz; yedek satır sayısı beklenenle uyuşmazsa iş
durur (D-243'ün `RuntimeError` mandalı bunu zorlar, ama mandal ancak
**betik gerçekten çalıştırılırsa** korur — elle SQL atan yolu korumaz).

**Bundan çıkan ikinci kural — elle SQL yasak.** Üretimde `DELETE`/`UPDATE`
yalnız testi olan, `dry_run` destekleyen, yedek yazan betikle atılır. Konsoldan
veya ad-hoc script'ten atılan yıkıcı SQL, mandalların tamamını atlar; bu
oturumdaki kaybın yolu tam olarak budur.

**Üçüncü kural — kolon ikizi her ölçümü yanlış yapılabilir kılar.** `companies`
tablosunda `tax_number` (40 dolu) **ve** `vergi_no` (761 dolu) ayrı ayrı
duruyor; aynı şekilde `website_domain` (5397) / `web_sitesi` (5049). "774
vergi_no" kriterini ilk ölçümde `tax_number` üzerinden okuyup **40** gördüm ve
yanlış alarm verdim. Aynı anlamı taşıyan iki kolon, her sorguyu "hangisini
okudun?" sorusuna bağımlı kılar — sessiz yanlış sonuç üretir, çünkü sorgu
hata vermez, sadece eksik sayar. FAZ 2 müşteri beyni bu alanları okuyacağı için
`VERI-KOLON-IKIZ-01` **FAZ 2'den önce** kapatılır.

**Dördüncü kural — sayı kriteri, tekilleştirmeden önce mi sonra mı sayıldığını
söylemeli.** "774 korunur" kriteri kirli tabloda sayılmış bir değerdi ve
tekilleştirmeden sonra matematiksel olarak korunamazdı. Kabul kriterine sayı
yazarken `count(*)` mi `count(distinct X)` mi olduğu ve hangi satır kümesinde
sayıldığı belirtilir. Aksi halde doğru çalışan iş yanlış başarısız görünür —
bugün olduğu gibi.

- **Mandal:** `yedekler/companies_20260927_2124.jsonl` (9412 satır) — silme
  sonrası ilk gerçek yedek. `yedekler/` `.gitignore`'a alındı (KVKK: `vergi_no`
  + e-posta içerir, D-242 çatısı).
- **Referans:** D-243 (prova diske yazmaz, yedek yolu enjekte edilir), D-242
  (yedek tek çatı), D-66 (brif maddesi ölçülmüş değere dayanır), D-230
  (ölçmeden tamamlandı denmez).

---

## D-245 — Kolon adı veri türünü garanti etmez: doluluk ≠ geçerlilik

**Bağlam:** `VERI-KOLON-IKIZ-01` Faz A ölçümü, `companies.vergi_no`'daki 761
değerin **633'ünün vergi numarası olmadığını** gösterdi (526 tanesi 6 haneli OSB
üye/parsel numarası, biri `'1105-BEYP.'` gibi harf içeriyor). Geçerli VKN sayısı
774 değil, **128**. Aynı ölçümde `website_domain`'deki 5397 değerin ~2660'ının
firma sitesi değil OSB portalı olduğu ortaya çıktı (`isim.org.tr` x2143,
`ostimistihdam.com` x474, `ostimonline.com` x49).

**Kural — bundan sonra:**

1. **Doluluk oranı kalite kanıtı değildir.** `count(*) WHERE col IS NOT NULL`
   bir şey ölçmez. Kolonun anlamı varsa (VKN, NACE, domain, telefon) ölçüm
   **biçim doğrulamasıyla** yapılır: `count(*) WHERE col ~ '<desen>'`. Brif ve
   kalite puanı yalnızca bu ikinci sayıyı kullanır.

2. **Tekrar eden değer, kaynak sızıntısı işaretidir.** Bir kolonda aynı değer
   yüzlerce satırda görünüyorsa (x2143) o veri firmaya ait değil, kazıyıcının
   sayfa şablonundan kaptığı sabittir. Yeni kazıyıcı/ETL işi teslim edilirken
   `GROUP BY col HAVING count(*) > 1 ORDER BY 2 DESC LIMIT 10` çıktısı brife
   yapıştırılır; tepede 3 haneli bir sayı varsa iş done olamaz.

3. **Birleştirme migration'ı öncesi UNIQUE + mükerrer ölçümü zorunludur.**
   `COALESCE(a, b)` ile iki kolon birleştirilecekse, hedef kolonda UNIQUE kısıt
   varken birleşimin tekil olduğu önce kanıtlanır
   (`count(*) - count(distinct ...)`). Bu ölçüm yapılmadan yazılan migration
   üretimde kısıt ihlaliyle patlar — bu işte 9 mükerrer değer bulundu.

4. **Kalite puanı kirli kolondan beslenmez.** `website_domain` dolu olduğu için
   ~2660 firmaya haksız puan verilmiş. Puanlayıcıya yeni sinyal eklenirken o
   sinyalin biçim doğrulamasından geçtiği gösterilir; geçmiyorsa sinyal eklenmez.

- **Mandal:** `plans/brief_utku_VERI-KOLON-IKIZ-01.md` § "Faz A SONUCU" —
  ölçüm çıktısı ve üç kusurun kaydı.
- **Referans:** D-244 (sayı kriteri hangi kümede sayıldığını söyler), D-235
  (İvedik kazıyıcı sayfa döngüsü kök nedeni), D-66, D-230.

## D-246 - Alan sozlesmesi yazili degilse kolon kirlenir; dogrulama tek kapidan gecer

**Baglam:** `vergi_no` kolonu 761 satirda dolu gorunuyordu. Olculdu: 9412 firmada
**yalnizca 5** deger resmi saglama toplamindan geciyor (3 VKN + 2 TCKN). Geri kalan
icerik ticaret sicil no (526), saglama tutmayan 11 hane (122), 5 haneli cop (78),
adres kirintisi (23). Yani kolon dolu, veri yok.

**Kok neden kolonun kendisi degil:** her kaziyici alan bicimine kendi regex'i ile
karar veriyordu ve hicbir yerde "bu alana ne girer, ne girmez" yazili degildi.
ASO kaziyicisi sicil numarasini vergi numarasi sandi; kimse itiraz etmedi cunku
itiraz edecek sozlesme yoktu.

**Karar:**

1. **Alan sozlesmesi yazilidir.** Tek kaynak: `docs/VERI_KALITE_SOZLESMESI.md`.
   Her alan alti maddeyle tanimlanir: anlam, bicim, saglama, **kabul edilmez**,
   gecmezse ne olur, kim doldurur. Alti madde dolmadan o alana kod yazilmaz.

2. **En kritik madde "kabul edilmez" maddesidir.** 526 satirlik hata bu madde
   yazilmadigi icin olustu. Benzer veri her zaman ayni kolona sizmaya calisir:
   sicil no vergi no'ya, kaynak sitesinin alan adi firma sitesine, oda meslek
   grubu NACE koduna.

3. **Dogrulama tek kapidan gecer.** Kaziyici/ETL alan bicimine karar vermez;
   ilgili dogrulayiciyi cagirir. Vergi kimligi icin tek kapi:
   `src/company_master/etl/kimlik_no.py` -> `kimlik_dogrula()`.

4. **Gecersiz deger kolona yazilmaz.** `NULL` kalir. Ham deger
   `source_records.raw_payload` icinde durur, kaybolmaz. Yari gecerli deger bos
   degerden tehlikelidir cunku raporda gecerli sayilir (D-245).

5. **Uzunluk bicimi saglamanin yerine gecmez.** 11 hane olmak TCKN olmayi
   kanitlamaz: 124 satirin 122'si dogru uzunlukta ama saglama toplami tutmuyor.
   Resmi saglama algoritmasi olan alanda regex tek basina kabul kriteri olamaz.

6. **Turetilmis alan elle yazilmaz.** `tuzel_tip` (sahis/tuzel) yalnizca
   saglamadan gecmis `vkn`/`tckn` kolonundan turetilir. Unvandan tahmin
   yasaktir: 11 haneli 124 satirin 101'i unvaninda LTD/A.S. tasiyor, yani
   unvan sinyali bu veride yanlis sonuc uretir.

7. **Veri yeniden kazinabilir, sozlesme kazinamaz.** Kirli 633 degeri kurtarmak
   icin migration yazmak yerine kurali yazip yeniden kazimak dogrudur. Onarim
   emegi tek seferliktir; sozlesme her kazimada calisir.

**Mandal:** `python src/company_master/etl/kimlik_no.py` -> "tum mandallar gecti".
Mandal degerleri gercek olcum verisinden alinmistir (uydurma ornek degil).

**Referans:** D-245 (doluluk != gecerlilik), D-244 (yikici iste yedek kanit),
D-243 (prova diske yazmaz).

---

## D-247 - Kisisel veri gosterimi role gore ayrilir; maskeleme tek kapidan gecer

**Baglam:** TCKN saklama karari (KVKK-TCKN-01) beklerken gosterim tarafi acik
kalmisti. Urun sahibi karari: **admin panelinde tum alanlar acik, kullanici
panelinde TCKN acilip kapatilabilir olmali.**

**Karar:**

1. **Saklamak ile gostermek ayri kararlardir.** TCKN veritabaninda saglamadan
   gecmis haliyle durur; panelde gorunup gorunmemesi ayri bir ayardir. Ayni
   kolon iki farkli role iki farkli sekilde sunulur.

2. **Gosterim tek kapidan gecer.** Ekranlar ham `tckn` degerini yazmaz;
   `company_master.settings.tckn_sun(tckn, kullanici_id, admin=...)` cagirir.
   Neden: onceki maskeleme (`kvkk_maske_acik`) her ekranda tekrar tekrar
   yorumlaniyordu; bir ekranin maskelemeyi unutmasi mumkundu. Tek kapi olunca
   dugme kapandiginda tum kullanici ekranlari birlikte maskelenir.

3. **Varsayilan KAPALI.** `tckn_kullaniciya_gorunur` varsayilani `False`.
   Kisisel veriyi gostermek bilincli bir secim olmali; unutulan ayar veriyi
   sizdirmamali.

4. **Admin istisnasi ayarla degil rolle belirlenir.** `admin=True` cagrisi
   ayara bakmaz. Admin'in kendi ayarini kapatmasi onu kor etmemeli; denetim
   yapan kisi ham veriyi gorebilmelidir.

5. **Bos deger maskeye donusmez.** `None`/bos giren `None` doner. Maskelenmis
   nokta dizisi "veri var" izlenimi verir; olmayan veri icin sahte doluluk
   uretmek D-245 ihlalidir.

6. **Ayar semaya eklenir, panele elle kodlanmaz.** `AYAR_SEMASI` tek kaynak;
   panel `gruplar()` ile formu kendisi uretir. Panele elle widget eklemek sema
   ile arayuzun ayrisma riskidir.

**Mandal:** `python scripts/_kontrol_tckn_dugme.py` -> 6 mandal (varsayilan
maskeli, admin acik, dugme ac/kapa, bos deger).

**Referans:** D-246 (dogrulama tek kapidan gecer - ayni ilkenin gosterim
tarafi), D-245 (sahte doluluk uretme). Ilgili bekleyen karar: KVKK-TCKN-01
(saklama suresi + erisim kaydi).

---

## D-248 - TCKN saklanir; "suresiz" yerine "kayit aktif oldugu surece" yazilir

**Baglam:** KVKK-TCKN-01 saklama tarafi. Urun sahibi karari: TCKN saklanacak,
sure siniri yok, diger firma alanlariyla ayni akistan toplanacak, admin
panelinde ac/kapa olacak; **ileride ucretli pakete konulmasi dusunuluyor**
(senaryo henuz olgunlasmamis).

**Karar:**

1. **TCKN saklanir.** Ayri bir toplama akisi kurulmaz; `kimlik_dogrula()`
   kapisindan gecen deger `tckn` kolonuna yazilir (D-246/3). Sahis
   isletmesinde TCKN vergi numarasi yerine gectigi icin ticari veridir.

2. **"Suresiz" yazilmaz; "kayit aktif oldugu surece" yazilir.** Ikisi pratikte
   ayni sonucu verir ama hukuken ayrisir: KVKK m.4 sinirli sure ilkesi
   "suresiz" ifadesini savunulamaz kilar. Ayni davranis, savunulabilir ifade.
   Firma kaydi silindiginde/kapandiginda TCKN de duser.

3. **Toplama karari ile satis karari ayridir.** Kendi paneli icinde gostermek
   (mesru menfaat, ticari sicil verisi) ile **ucretli pakette ucuncu kisiye
   aktarmak** ayni hukuki temele dayanmaz. Aktarim `KVKK-TCKN-02` altinda
   **BLOKE**; hukuki gorus alinmadan tek satir kod yazilmaz.

4. **Paket/kademe modeli simdi kodlanmaz.** Senaryo olgunlasmamis
   ("muhtemelen", "olabilir"). Bugun yazilacak rol/kademe soyutlamasi yarin
   degisecek varsayimi betonlastirir. Mevcut `admin` / `kullanici` ayrimi
   yeterlidir; kademe geldiginde `tckn_sun()` icindeki tek kosul buyur.

5. **Aktarim aninda erisim kaydi zorunlu olur.** TCKN kendi panelinde
   gorunurken log istege bagli; ucretli pakete girdigi an "kim, hangi firmanin
   TCKN'sini, ne zaman gordu" kaydi zorunludur. Aktarimin on kosulu budur,
   sonradan eklenecek sus degil.

**Referans:** D-247 (gosterim tek kapidan gecer), D-246 (dogrulama tek kapi),
sozlesme 3.2. Bekleyen: `KVKK-TCKN-02` (aktarimin hukuki temeli).

## D-249 - "Veri yok" ile "0 puan" ayri degerlerdir; olu skor NULL'a cekilir

**Baglam:** KALITE-SKOR-01 olcumu: `companies` tablosunda 5 skor kolonu 9412
satirda tek deger tasiyordu. `employee_count_score` %100 NULL,
`job_postings_score` %99.9 NULL, `source_diversity_score` %67 NULL, kalanlar
sabit 0. Kolonlar `DEFAULT 0` ile tanimliydi; bu yuzden "hic hesaplanmadi" ile
"hesaplandi, sifir cikti" ayirt edilemiyordu.

**Kok neden - uc ayri hata, tek sonuc:**

1. `job_postings_score` **hic hesaplanmiyordu.** `quality_metrics.py` icinde o
   dongu yazilmamisti; kolon DEFAULT 0 ile dolu oldugu icin "hesaplanmis"
   gorunuyordu. Sessiz bosluk.
2. `source_diversity_score` **yanlis bag uzerinden** sayiyordu:
   `companies.source_record_id` -> tanim geregi tek kayit -> her firma icin 1
   kaynak -> sabit 0. Dogru bag `source_records.company_id` (0023 sonrasi).
3. `employee_count_score` dogru calisiyordu ama **girdi hic yok**
   (`employee_count` %100 bos). Skor hatasi degil, kaynak eksigi.

**Karar:**

1. **`NOT NULL DEFAULT 0` skor kolonlarindan kaldirilir.** Bir puan kolonu icin
   `DEFAULT 0` sessiz yalandir: "olcmedim" yerine "olctum, sifir" der. Puanlar
   `NULL` baslar (goc `0024`).
2. **Uc durum ayrilir:** `NULL` = olculmedi/veri yok, `0` = olculdu ve sinyal
   yok, `>0` = sinyal var. Hesaplayicilar veri yoksa `None` doner.
3. **Toplam puan, NULL skoru pay ve paydadan birlikte duser.** Eksik veri
   firmayi cezalandirmaz (sozlesme K-5: haksiz puan yasagi).
   `employee_count_score` %100 NULL oldugu icin bugun toplam puana hic girmez.
4. **Olu kolon silinmez, isaretlenir.** Kolon silmek girdi geldiginde geri
   ekleme maliyeti dogurur; NULL kalmasi zaten "bilgi yok" der. `employee_count`
   ve `job_postings` icin kaynak gorevleri acik kalir.
5. **Mandal:** `tests/test_kalite_skor.py` - `None` girdide `None`, `0` girdide
   `0` doner. Ikisi karisirsa mandal kirmizi olur.

6. **Satir basina UPDATE yasaktir; toplu yazma kullanilir.** Hesaplayicinin
   eski hali firma basina ayri UPDATE atiyordu: 9412 x 7 = ~66 bin tur, tek
   islem icinde 40 dakikada 7 dongunun ancak 2'sini bitirdi ve commit
   olmadigi icin sonuc hic gorunmedi. `executemany` ile ayni is **~2
   dakikada** bitti. Hesap mantigi Python'da kalir (SQL'e kopyalanmaz, ikilik
   uretir), yazma tek tura iner.
   Ek bulgu: veritabani **PostgreSQL**'dir. Kodda MySQL sozdizimi
   (`raw_payload->>"$.alan"`, `information_schema.processlist`) kalintisi
   varsa yanlistir; dogrusu `raw_payload->>'alan'` ve `pg_stat_activity`.

**Referans:** D-245 (doluluk != gecerlilik), sozlesme K-5, goc
`0024_kalite_skor_olu_sinyal.sql`.

## D-250 - Olculen sey "Kimlik Dosyasi Tamligi"dir; firma kalitesi degil

**Baglam:** KALITE-PUAN-01 olcumu iki celisen formul, 583 bayat skor ve
ortak bir adlandirma hatasi buldu. Kolon adi `data_quality_score` ("firma
kalite puani") idi; oysa hesaplanan sey firmanin niteligi degil, **bizim o
firma hakkinda toplayabildigimiz veri miktari**. Uc alan (vergi dairesi,
ticaret sicil no, MERSIS no) veritabaninda **hic yoktu**.

**Olculen baslangic durumu (9412 firma):**

| Alan | Doluluk |
|---|---|
| Ticaret unvani | %100 |
| NACE kodu | %88.1 |
| Telefon | %87.7 |
| Adres | %61.6 |
| Internet sitesi | %57.9 |
| E-posta | %42.9 |
| VKN | %8.2 |
| Vergi dairesi / Ticaret sicil / MERSIS | KOLON YOK |

Tam kimlik dosyasi olan firma: **128 (%1.4)**. VKN haric hepsi tam: 2157 (%22.9).

**Karar:**

1. **Ad degisir: "Kimlik Dosyasi Tamligi" (0-10).** "Kalite" kelimesi yasak —
   eksiklik firmanin degil bizim toplama basarimizindir (D-249 mantiginin
   devami). Panel dili de boyle olur: dusuk puan = bizim is listemiz.

2. **Agirlik seti v1 — iki grup, 10 puan:**

   *Kimlik omurgasi (6 puan) — "bu firma hangi tuzel kisi?"*
   | Alan | Agirlik |
   |---|---|
   | Ticaret unvani | 1.0 |
   | VKN | 1.5 |
   | Vergi dairesi | 0.5 |
   | MERSIS no | 1.0 |
   | Ticaret sicil no + dairesi | 1.0 |
   | NACE kodu | 1.0 |

   *Erisim (4 puan) — "bu firmaya nasil ulasirim?"*
   | Alan | Agirlik |
   |---|---|
   | Adres | 1.5 |
   | Telefon | 1.5 |
   | E-posta | 0.7 |
   | Internet sitesi | 0.3 |

3. **VKN agirligi gecici olarak 1.5'tir.** Ilk tasarimda 3.0 onerildi; veriye
   uygulandiginda firmalarin %91.8'i 7.0 tavanina mahkum oldu. Sebep firmalarin
   VKN'sinin olmamasi degil, **bizim GIB'den cekemememiz** (GIB-MUKELLEF-01
   acik, erisim yontemi henuz belirsiz). Kaynak baglandiginda agirlik 3.0'a
   cikar, diger agirliklar orantili duser, surum v2 olur.

4. **Puan yalnizca DOGRULAMADAN GECEN alani sayar.** Dolu ama gecersiz deger
   puan kazandirmaz — `kimlik_dogrula()` / `sicil_dogrula()` tek kapisindan
   gecmeyen VKN 0 puandir (D-245, D-246 devami).

5. **Zenginlik verisi puana girmez.** Calisan sayisi, is ilani, sosyal medya
   ayri bir "zenginlik rozeti" olarak gosterilir. Gerekce: ikisi de ~%100 bos;
   puana katilirsa tum firmalar ayni oranda duser, puan ayirt etme gucunu
   kaybeder (D-249/3 ile ayni gerekce).

6. **`puan_surumu` kolonu zorunludur.** Agirlik seti degistiginde eski puanlar
   sessizce yanlis olur — bugun yasanan 583 bayat skorun koku budur. Agirlik
   seti tek sozlukte, surum numarasiyla tutulur; surumu eski olan satirlar
   panelde "yeniden hesap bekliyor" diye isaretlenir.

7. **"Ulasilabilir tavan" gostergesi zorunludur.** Bugun hicbir firma 10
   alamaz: 10.0 − 2.5 (hic toplanmayan 3 alan) − 1.5 (VKN yok) = **6.0**.
   Panelde tek satir olarak gosterilir. Ortalama puanin yukselmesi degil,
   **tavanin yukselmesi** gercek ilerlemedir.

8. **Alan bazli kayip tablosu yol haritasidir.** Her alan icin
   `eksik_firma x agirlik` = kayip puan. En buyuk kayip = siradaki is. Tablo
   kendi kendini gunceller; oncelik tartismasi ortadan kalkar.

9. **MERSIS, GIB'den once denenir.** MERSIS kaydi olan her firmanin VKN'si
   vardir ve MERSIS portali ucretsizdir. GIB erisimi belirsizken MERSIS bilinen
   bir yoldur; basarili olursa VKN boslugunun buyuk kismi GIB olmadan kapanir.

**Referans:** D-245, D-246, D-249; sozlesme 3.2-3.4, K-5. Bekleyen:
`SEMA-VKN-01` (vergi_dairesi + mersis_no + ticaret_sicil_no + sicil_dairesi
kolonlari), `GIB-MUKELLEF-01`, `MERSIS-KAYNAK-01`.

---

## D-251 - Sema tek dilde olur; goc defteri semanin tek anlaticisidir

**Tarih:** 2026-09-28 · **Karar:** urun sahibi · **Tetikleyen:** `SEMA-IKIZ-01` +
`GOC-DEFTER-01` · **Olcum:** [[docs/OLCUM_NACE_2026-09-28]]

### Neden

Iki ayri sorun ayni kokten cikti: **semaya elle dokunuldu, kimse yazmadi.**

Olcum: 54 tablo / 515 kolon. 511 kolon Ingilizce (%99.2). Turkce 4 kolon
(`vergi_no`, `web_sitesi`, `adres`, `osb_parsel`) — hepsi `companies` uzerinde,
hepsi sonradan yamanmis. Ikisi mevcut kolonun **ikizi**: `tax_number` (40 dolu)
yaninda `vergi_no` (761 dolu); `website_domain` (5397) yaninda `web_sitesi` (5049).

Ayni anda: diskteki 25 goc dosyasindan **6 tanesi uygulanmis ama deftere
yazilmamis** (0012, 0014, 0017, 0018, 0021, 0023). Defter 12 kayit gosteriyor,
sema baska sey soyluyor.

### Kural

1. **Sema dili Ingilizce'dir.** Kolon, tablo, kisit, indeks adlari Ingilizce.
   Turkce **sadece** panel etiketlerinde ve belgelerde. Sebep: cogunluk zaten
   Ingilizce, karisik dil "hangisi dolu?" sorusunu her seferinde doguruyor.

2. **Ikiz kolon yasaktir.** Ayni anlami tasiyan iki kolon = iki farkli dogru.
   Bir kolon eklenmeden once "bunun esdegeri var mi?" sorusu sorulur. Ikiz
   dogduysa: veri hedefe tasinir, kaynak **hemen** dusurulur. Kolon birakilmaz.

3. **Goc defteri semanin tek anlaticisidir.** Uygulanan her DDL
   `schema_migrations` tablosuna yazilir. Yazilmayan goc **uygulanmamis
   sayilir**. Defter bugun yalan soyluyor; semadan yeniden insa edilir.

4. **Elle DDL yasaktir.** `ALTER TABLE` / `CREATE TABLE` yalnizca goc dosyasi
   icinden calisir. `psql`'den elle sema degistirmek defteri bozar — bugunku
   6 kayip goc bunun kanitidir.

5. **Goc idempotent olmalidir.** `IF NOT EXISTS` / `IF EXISTS` zorunlu. Defter
   bozulursa goc ikinci kez calisabilmeli, patlamamali.

6. **Tasima sirasinda celisen kayit rapor edilir, sessizce ezilmez.** Olcumde
   celisen 2 kayit cikti; ikisi de yanlisti (KAL-MET'in `website_domain` alanina
   uye oldugu dernegin sitesi yazilmis — D-245 kaynak sizintisi). Celisen kayit
   gormeden karar verilmez.

### Uygulama sirasi

```
1. Defter semadan yeniden insa (kayip 7 goc: 0012,0014,0017,0018,0021,0023,0024)
2. 0025 duzeltilir (mersis_no IPTAL -> mevcut mersis_number) + uygulanir
3. Ikiz tasima: vergi_no->tax_number, web_sitesi->website_domain,
   adres->address, osb_parsel->osb_parcel ; kaynak kolonlar dusurulur
4. Mandal: sema kolon adlarinda Turkce karakter/kelime taramasi
```

**Not:** `0025` icinde ucuncu bir ikiz doguyordu — `mersis_no` eklenecekti, oysa
`mersis_number` zaten var (0 dolu). Goc uygulanmadan yakalandi. Kural 2'nin ilk
sinavi, gecti.

**Referans:** D-245 (kaynak sizintisi), D-246 (alan sozlesmesi), D-249.
**Onkosul:** D-250 uygulamasi bu karara baglidir (0025 uygulanmadan
`kimlik_tamligi` ve `puan_surumu` kolonlari yok).

---

## D-252 - NACE uc katmandir: yapabilir / yapiyor / uzman

**Tarih:** 2026-09-28 · **Karar:** urun sahibi · **Tetikleyen:** urun sahibi
gozlemi — *"x firmanin nace kodu ve yaninda nace koduna bagli isler; bu firma
bu isleri resmi olarak yapabilir. Fakat firma tek bir konuda uzmanlasmis da
olabilir."* · **Olcum:** [[docs/OLCUM_NACE_2026-09-28]]

### Olcumun soyledigi

**NACE kodlarimizin %100'u tahmindir. Tek bir firmanin bile gercek NACE kodu
elimizde yoktur.**

| `nace_source` | Firma | Nitelik |
|---|---:|---|
| `sector_default` | 5679 | tahmin — kaynagin varsayilani |
| `unknown` | 1935 | bilinmiyor |
| `fallback` | 654 | tahmin — yedek |
| `title_default` | 21 | tahmin — unvandan cikarim |
| **gercek (MERSIS/TSG)** | **0** | — |

En sik kod **29.10**, **1880 firmaya** atanmis. Acilimi: *"Kamyonet, Kamyon,
Yari Romork Cekicileri, Tanker Imalati"*. Ankara'da 1880 kamyon fabrikasi yok.
Bu tek bir OSB kaynaginin varsayilan kodunun herkese yapistirilmasidir —
**D-245 kaynak sizintisinin bugune kadarki en buyuk ornegi.**

### Kural

1. **Uc katman ayrilir, ayni kolonda tutulmaz.**

   | Katman | Soru | Yer | Kaynak |
   |---|---|---|---|
   | **YETKI** | resmi olarak ne yapabilir? | `company_industries` | MERSIS / TSG |
   | **FIIL** | fiilen ne yapiyor? | kanit kayitlari | web, katalog, ihale |
   | **TAHMIN** | biz ne saniyoruz? | `companies.nace_code` | cikarim |

2. **Tahmin edilmis koda "NACE kodu" denmez.** `nace_validity <> 'verified'`
   olan her kod panelde **"tahmini sektor"** etiketiyle gosterilir. "Bu firma
   bu isi resmi olarak yapabilir" cumlesi **yalnizca** YETKI katmani doluysa
   kurulur. D-249'un ("veri yok" ≠ "0 puan") sektor karsiligi.

3. **Coklu NACE `company_industries`'e tasinir; ikinci kolon acilmaz.** Duz
   kolon coklu kodu tasiyamaz. Tablo zaten dogru tasarlanmis (`is_primary`,
   `source_id`, `confidence`, `verified_at`) ama 9412 firmadan **21'inde**
   kullanilmis — ve o 21 satirin **hepsi `is_primary=true`**, yani yan
   faaliyet kaydi bugun **sifir**.

   Urun sahibi "ana kod icin bir kolon, yan kodlar icin bir kolon" onerdi.
   **Reddedildi**, sebep: yan kodlarin her birinin ayri kaynagi ve ayri
   guven derecesi olur (biri MERSIS'ten, biri web sitesinden, biri
   ihaleden). Tek kolona `"25.11, 28.99"` yazmak D-245'in yasakladigi
   durumu uretir: deger var, kaynagi yok. Ustelik ucuncu ikiz kolon
   dogar (D-251/2). Istenen ayrim `is_primary` ile **zaten** mumkun.

   Panelde gorunum yine iki alan olur ("Ana faaliyet" / "Yan faaliyetler");
   ayrim **gorunumde**, depolamada degil.

4. **Acilim level-6'dan gelir, bagi `parent_code` kurar.** Sozlukte level-4'un
   **%50'si bassiz** (957 kodun 483'u), level-6'nin **%100'u dolu ve Turkce**
   (2252 kod). Urun sahibinin istedigi "koda bagli isler listesi" = o kodun
   `parent_code` ile bagli alt basliklaridir. Ornek: 29.10 altinda 7 alt kod
   (otomobil / otobus / motor / itfaiye-ambulans-mikser imalati...).

   **Kapsama olculdu, iki sayi celisiyor ve dogru olan ikincisidir:**

   | Olcum | Sonuc |
   |---|---|
   | kod sayisina gore | 256 / 261 kod (%98) |
   | **firma agirlikli** | **6387 / 8289 firma (%77)** |

   Kod sayisi yaniltici: en kalabalik 5 kodun **3'unde acilim sifir**
   (62.09 · 654 firma, 62.01 · 632, 41.10 · 598 — hizmet kodlari).
   Yani 1902 firma icin "yapabilecegi isler" listesi **bugun uretilemez**.
   Panelde bos liste gosterilmez; alan gizlenir (D-249 mantigi).

5. **Tek kaynaktan kopyalanmis kod kutlesi sektor sayacindan cikarilir.**
   1880 firmalik 29.10 kutlesi bugun her sektor grafigini yaniltiyor. Esik:
   ayni kod + ayni kaynak + ayni gun = supheli kutle, isaretlenir.

6. **Sozluk tek dile cekilir ve Turkce harfler geri gelir.** 3319 kodun 572'si
   Turkce, gerisi Ingilizce. TUIK NACE Rev.2 Turkce listesi ucretsizdir,
   indirilir. D-251/1'in sozluk karsiligi.

   Ek bulgu: Turkce basliklar **yarim asciilestirilmis**. Ornek:
   *"Motorlu Kara **Tasitlarinin** Motorlarinin **Imalati**"* — ş/ı/ğ dusmus,
   c/o/u korunmus (`Çekiciler`, `Römorklar` saglam). Veritabani kodlamasi
   **saglam** (3319 satirda bozuk kodlama sifir); kayip **yazma aninda**
   olusmus. Panelde satis yuzune boyle cikar. TUIK listesi indirildiginde
   bu kendiliginden duzelir; ayri temizlik iki kere is olur.

7. **Olu kolonlar dusurulur.** `nace_codes.is_manufacturing` tek degerli (3319
   satirin hepsi ayni) → D-249'a gore sifir bilgi. `companies.nace_name` (52
   dolu, 8 deger: *"GIDA"*, *"Savunma"*, *"KIMYA-LABARATUVAR"*) NACE adi degil,
   kaynak sitenin kendi etiketi — yanlis kolona yazilmis serbest metin.

### Bugun yapilabilir / bugun yapilamaz

**Kaynak gerektirmez (4 is):** 2, 3, 4, 5 numarali kurallar.
**Bloke:** gercek NACE kodu → `MERSIS-KAYNAK-01`. TSG captcha ile kapali
(`TSG-KAYNAK-01`). MERSIS hem kimlik (D-250/9) hem yetki katmani icin ayni
kapidir — tek olcum iki sorunu birden acar.

**Referans:** D-245, D-249, D-250, D-251; sozlesme 3.8.

---

## D-253 - Defter kaydi kanit degildir; iz dogrulanir

**Tarih:** 2026-09-28 · **Karar:** KAHIN · **Tetikleyen:** GOC-DEFTER-01 —
defterin 12 kayit gosterdigi iddiasi · **Olcum:** `scripts/goc_defteri.py`

### Olcumun soyledigi

Iddia bayatti. Defter olculdugunde **25/25** ciktı; "yazilmamis" denen 6 goc
(0012, 0014, 0017, 0018, 0021, 0023) `2026-09-28 08:05`'te zaten yazilmisti.
0025 de uygulanmis, `mersis_no` ikizi daha once iptal edilmisti.

Asil bulgu baskaydi: **defterde satir olmasi gocun uygulandigini kanitlamiyor.**
Kanit semadadir. Ayrica veritabani Supabase bicimindedir — `auth` (82 kayit),
`public` (25), `realtime` (81) semalarinin **her birinde** ayri bir
`schema_migrations` vardir. `table_schema='public'` filtresi olmayan her sorgu
yanlis sayar.

### Kural

1. **Goc durumu uc kaynagin kesisiminden okunur:** disk dosyasi + defter
   kaydi + **semadaki iz**. Iki tanesi yeterli degildir. `goc_defteri.py`
   her goc dosyasindan tablo / kolon / indeks / dusurulen varsayilan izlerini
   cikarir ve semayla karsilastirir. Durumlar: `TAM`, `EKSIK`, `ESKIMIS`,
   `IZSIZ`. Defterde yazili ama izi `EKSIK` olan goc **uygulanmamis sayilir**
   (D-251/3'un olculebilir hali).

2. **Ustunden gecilen goc kendi halefini beyan eder.** Sonraki bir goc onceki
   gocun izini degistirdiginde (ornek: kolon adi degisti), eski dosyaya
   `-- ustunden-gecen: <dosya>` satiri yazilir. Arac izi orada aramayi birakir.
   Sessizce gormezden gelmek D-245 ihlalidir: iz yoksa **sebebi yazili olmali**.

3. **Sema dili mandalla korunur** (D-251/1). `tests/test_goc_defteri.py`
   `public` semasindaki her kolon adini denetler. Bilinen borc listelidir ve
   **buyuyemez**; liste bayatlarsa (kolon kapandi ama listede kaldi) mandal
   yine kirilir. Bugunku borc **5 kolon**: `adres`, `osb_parsel`, `vergi_no`,
   `web_sitesi`, `ip_adresi`. Ilk dordu SEMA-IKIZ-01'in isi; `ip_adresi` bu
   olcumde **yeni bulundu**, listeye eklendi.

4. **Sorgu semasiz yazilmaz.** `information_schema` ve `pg_*` sorgularinda
   `table_schema='public'` zorunludur. Filtresiz sorgu Supabase semalarini
   karistirir ve yanlis rapor uretir.

### Bu kararla yapilanlar

`0026_kimlik_kolonlari_ingilizce.sql` — 0025'in actigi 5 Turkce kolon
Ingilizce'ye cevrildi: `vergi_dairesi`→`tax_office`,
`ticaret_sicil_no`→`trade_registry_number`, `sicil_dairesi`→
`trade_registry_office`, `kimlik_tamligi`→`identity_completeness`,
`puan_surumu`→`score_version`. Bedeli sifirdi: 9412 firmada **0 dolu satir**,
kodda **0 referans**. `RENAME` idempotent olmadigi icin `DO` blogu +
`information_schema` kontrolu ile sarildi (D-251/5); iki kez calistirildi,
ayni sonucu verdi.

**Referans:** D-245, D-249, D-251; is: GOC-DEFTER-01. Arac:
`scripts/goc_defteri.py`, mandal: `tests/test_goc_defteri.py`.

## D-254 — Kimlik Defteri: iddia ile kanit ayri durur

**Tarih:** 2026-09-28 · **Is:** SEMA-IKIZ-01 · **Goc:** `0027_ikiz_kolonlari_birlestir.sql`

### Bulgu

`companies` tablosunda alti ikiz kolon vardi: `vergi_no`/`tax_number`,
`web_sitesi`/`website_domain`, `adres`/`address`, `osb_parsel`/`osb_parcel` ve
karsiliksiz `ip_adresi`. Duz `RENAME` her ikisinin de dolu oldugu satirlarda
patlardi.

Asil bulgu adlandirma degildi. **`vergi_no` kolonunda 761 dolu deger vardi;
D-246 kapisindan (`kimlik_dogrula()`) gecen sadece 7 taneydi** — 5 VKN, 2 TCKN.
Geri kalan 764 deger sicil no, MERSIS, telefon kirintisi ve bicimsiz metindi.
Yani kolon "vergi numarasi" diye okunuyordu ama icerigi **kaynagin soyledigi
sey**di, dogrulanmis bir kimlik degil. Sekil dogrulugu ile gercek ayni sey
degildir; bir alanin adi onun icerigini dogrulamaz.

### Kural

1. **`companies.tax_number` bir iddia degil, kanittir.** Yalnizca D-246
   kapisindan gecmis VKN yazilir. Kapiyi atlayan hicbir yol bu kolona yazamaz.
   Sekil kurali veritabanindadir: `ck_companies_tax_number_sekil` (NULL ya da
   tam 10 hane). Uygulama kodundaki kural, her yeni betigin unutabilecegi bir
   kuraldir; kisit unutulmaz.

2. **Dogrulanmamis her kimlik `company_identifiers` defterine gider.**
   Tur (`identifier_type`), deger, **kaynak** (`source_id`) ve guven
   (`confidence`) ile birlikte. Deger atilmaz — D-245: kaynagi olmayan deger
   kabul edilemez, ama **kaynagi olan deger de silinmez**. Bugun defterde
   771 kimlik var: 5 vkn, 2 tckn, 764 diger (sicil/mersis/bicimsiz).

3. **Ikiz kolon yasaktir** (D-251/2'nin olculebilir hali). Ayni olguyu iki
   kolon anlatiyorsa hangisinin dogru oldugunu kimse bilmez. Ikisi de dolu ve
   **farkli** ise otomatik "biri kazanir" kurali yazilmaz; karar urun
   sahibinindir (D-251/6).

4. **Kolon adi Ingilizce, sozlesme anahtari Turkce kalir.** Satir/kolon adlari
   D-251/1 geregi Ingilizce'dir. `raw_payload` anahtarlari, kaziyici veri
   sinifi alanlari ve **API cikti** anahtarlari kaynagin/istemcinin
   sozlesmesidir; oldugu gibi kalir. `_row_to_dashboard` ikisini ayni anda
   tasir: girdi Ingilizce, cikti Turkce.

5. **Mandal commit'te calisir.** `tests/test_goc_defteri.py` pre-commit
   kancasi olarak tanimlidir (`goc-defteri`). DB'ye bagli oldugu icin
   `always_run` degil: yalnizca `src/company_master/schema/` altina dokunan
   commit tetikler. Semaya dokunan commit denetimsiz gecemez.

   **Acik borc (MANDAL-KURULUM-01):** tanimli kanca ile *kurulu* kanca ayni
   sey degildir. Olcum: `.git/hooks/pre-commit` YOK ve `pre_commit` modulu
   kurulu degil; ayrica `.pre-commit-config.yaml` git kokunde degil
   `Huginn Data Insights/` altinda. Yani bugun hicbir kanca --- eskisi de
   dahil --- fiilen kosmuyor. Kancalar calisir hale gelene kadar mandal elle
   kosulur: `python -X utf8 "Huginn Data Insights/tests/test_goc_defteri.py"`.
   Betikler artik `__file__`'a gore yol kurar, her dizinden kosar.

   > **D-255 duzeltmesi:** bu maddedeki ucuncu iddia (`.pre-commit-config.yaml`
   > git kokunde degil) **yanlisti**. Vault kendi git reposudur, config tam
   > onun kokundedir. Borc kurulumdaydi, konumda degil. Kapatildi.

### Bu kararla yapilanlar

- `0027_ikiz_kolonlari_birlestir.sql`: bekci blogu, kimlik defterine geri
  yazim, normalizasyon, ikiz kolon dusurme, uretilmis kolon ve KPI indeksinin
  yeniden kurulmasi, `ck_companies_tax_number_sekil`. Uygulandi, deftere
  yazildi, izi dogrulandi (8 denetim, D-253).
- `scripts/kimlik_ayikla.py` — kalici arac (`--dene` / `--yaz`). Dagilmis
  olcum betiklerinin yerini alir.
- 9 tuketici modul gocuruldu; `tax_number` yazan 3 yol D-246 kapisina baglandi;
  `entity_resolution`'daki `vkn_exact` hatasi kapatildi.
- Eski goclere `ustunden-gecen:` / `dusen-iz:` isaretleri kondu (D-253/2).
- `BILINEN_DIL_BORCU` **bos**: bes Turkce kolon adinin besi de kapandi.

### Olcum (2026-09-28)

| Olcu | Deger |
|---|---|
| firma | 9412 |
| `tax_number` dolu (kapidan gecmis) | 5 |
| `company_identifiers` | 771 (5 vkn / 2 tckn / 764 diger) |
| `address` / `website_domain` / `osb_parcel` dolu | 5798 / 5446 / 19 |
| kalan ikiz kolon | **0** |
| goc dosyasi = defter kaydi | 27 = 27 |

**Referans:** D-245, D-246, D-249, D-250, D-251, D-253. Arac:
`scripts/kimlik_ayikla.py`, `scripts/goc_defteri.py`; mandal:
`tests/test_goc_defteri.py` (pre-commit `goc-defteri`).

---

## D-255 — Kanca fiilen kuruldu; yarim kalan 0024 tamamlandi (2026-09-28)

**Baglam:** iki borc ayni turda kapatildi --- MANDAL-KURULUM-01 (D-254/5) ve
GOC-0024-YARIM-01 (D-249'un eksik uygulanmasi).

### 1. Depo cogul: **iki ayri git reposu var**

`c:/Huginn Data Projesi` ve `c:/Huginn Data Projesi/Huginn Data Insights`
**ayri** git repolaridir (`git rev-parse --show-toplevel` ile olculdu). Vault
kendi reposudur ve `.pre-commit-config.yaml` **tam onun kokundedir**.

D-254/5'teki "config git kokunde degil" iddiasi yanlisti. Sorun konum degil,
**kurulum** idi: `.git/hooks/pre-commit` dosyasi hic yoktu.

**Kural:** kanca, betik veya yol tartisan her olcum once `git rev-parse
--show-toplevel` ile hangi repoda oldugunu soyler. Bu vault'ta "git koku"
tek basina anlamsiz bir ifadedir.

### 2. Kanca framework'suz kuruldu (ucuz ruhsat)

`pre_commit` modulu kurulu degil, ag erisimi yok, yeni bagimlilik eklenmedi.
`.pre-commit-config.yaml` icindeki iki **local** mandali dogrudan kosan duz
`sh` betigi yazildi: `Huginn Data Insights/.git/hooks/pre-commit`.

- `kodlama_denetim.py --kapsam git` --- her commit (config: `always_run`)
- `tests/test_goc_defteri.py` --- yalnizca sema/goc dosyasina dokunan commit
  (config: `files:` deseni `grep -qE` ile birebir tekrarlandi)

Uzak mandallar (bandit, safety) bu betikte **yok**. `pre-commit` ileride
kurulursa `pre-commit install` bu dosyayi devralir ve hepsini kosar.

### 3. "Kurdum" demek kanit degildir

Kanca bilerek kirilarak sinandi. **Ilk deneme yanlis negatif verdi:** BOM'lu
dosya vault **kokune** kondu, kanca kostu ama "temiz" dedi ve commit gecti ---
kok dizin `KAPSAM_DIZINLERI` disinda. Ayni dosya `scripts/` altina konunca:

```
ALLOWLIST DISI IHLAL (1): utf8_bom: scripts/_kanca_kanit.py
```

ve commit **olusmadi** (`git log -1` ayni commit'te kaldi). Deneme geri alindi.

**Kural:** bir mandalin kuruldugunu iddia eden her karar, mandalin *gercekten
durdurdugunu* gosteren bir kirma denemesi tasir. Denemenin **kapsam icinde**
bir dosyayla yapildigi ayrica dogrulanir; kapsam disi bir dosyanin gecmesi
"kanca calismiyor" demek degildir.

**Sure (kacis cazibesi olcusu):** `kodlama_denetim` 0.28 sn, `test_goc_defteri`
3.88 sn. Yavas kanca `--no-verify` ile atlanir, yani yine olur. Kanca toplami
saniyeler mertebesini asarsa bolunur, gevsetilmez.

### 4. 0024 neden yarim kaldi: **olcumun kapsami kararin kapsamini belirledi**

D-249 dokuz skor kolonunun hepsi icin gecerliydi. `0024` dosyasi yalnizca
**bes** kolon yazmis; kalan dort kolon dosyaya **hic girmemis** --- yani
"uygulanmadi" degil, **eksik yazildi**.

Sebep dosyanin kendi yorumunda duruyor: kanit listesi "farkli deger sayisi = 1"
olan kolonlardan olusuyordu. Dort kolon coklu deger tasidigi icin o listeye
girmedi ve goc onlari hic gormedi.

**Kural:** bir kararin kapsami *karardan* okunur, onu destekleyen olcumun
filtresinden degil. Goc yazarken "karar kac nesneyi kapsiyor" ile "olcum kac
nesne dondurdu" ayri ayri sayilir; esit degilse fark gerekcelendirilir.

### 5. `0028_skor_varsayilan_kalan_dort.sql`

Dort kolonun `DEFAULT 0`'i dusuruldu ve sahte 0'lar toplu `UPDATE` ile NULL'a
cekildi (D-249/6). **Sahte 0 = besleyen girdi NULL.** Girdi dolu ama sinyal yok
ise 0 **gercek olcumdur, dokunulmadi** (D-245).

| kolon | sahte 0 -> NULL | korunan gercek 0 | korunan >0 |
|---|---|---|---|
| `data_freshness_score` | 707 | 0 | 8705 |
| `email_validity_score` | 5364 | 91 | 3957 |
| `phone_format_score` | 1161 | 303 | 7948 |
| `social_media_score` | 908 | 3488 | 5016 |
| **toplam** | **8140** | 3882 | --- |

Uygulandi, deftere yazildi, semadaki izi dogrulandi (D-253/1). Dort kolonun
`column_default` degeri artik `None`.

### 6. Gocun tek basina yetmedigi yer: hesaplayici da yalan soyluyordu

`quality_metrics.py` icindeki dort hesaplayici, girdi yokken `0` donuyordu.
Goc NULL'a cekse bile **bir sonraki `run_all_metrics_update()` turunda 8140
sahte 0 geri gelirdi.** Dordu de `int | None` dondurecek sekilde duzeltildi.

**Kural:** bir varsayilani sema tarafinda dusurmek, o degeri **ureten** kodu
duzeltmeden yarim istir. Her `DROP DEFAULT` gocu, ayni kolona yazan uygulama
yolunu da ayni turda arar.

### 7. Acik borc notu

- **BORC-QUALITY-BETIK-01:** `scripts/recalc_quality_scores.py` bu dort kolonu
  yalnizca `COALESCE(..., 0)` ile **okuyor**, uzerine yazmiyor --- gocu geri
  almiyor. Bu turda dokunulmadi, risk yok.
- **BORC-SCRIPTS-01:** bu turun gecici betikleri silindi. `scripts/` altinda
  onceki oturumlardan kalma 30+ `_tmp_*` / `_olcum_*` dosyasi duruyor.

### Olcum (2026-09-28, gocten sonra)

| Olcu | Deger |
|---|---|
| firma | 9412 |
| `DEFAULT 0` tasiyan skor kolonu | **0** (9'un 9'u temiz) |
| NULL'a cekilen sahte 0 | 8140 |
| goc dosyasi = defter kaydi | **28 = 28** |
| kurulu pre-commit kancasi | 1 (kanit: commit durduruldu) |
| kanca suresi | 0.28 sn + 3.88 sn |

**Referans:** D-245, D-249, D-251, D-253, D-254. Arac:
`.git/hooks/pre-commit`, `scripts/kodlama_denetim.py`, `scripts/goc_defteri.py`;
mandal: `tests/test_goc_defteri.py`.

---

## D-256 — D-250 uygulandi: puan tek kapidan gecer, tavan ilan edilir (2026-09-28)

**Baglam:** D-250 karari yaziliydi ama **uygulanmamisti**. Kolonlar (`identity_completeness`,
`score_version`) ve kisitlar semada duruyordu; icini dolduran tek kapi yoktu ve
puan yazan **en az 17 ayri yol** vardi. Bu tur karari koda cevirdi.

### 1. Tek kapi: `etl/quality_recalc.py`

`identity_completeness(row) -> 0.0..10.0`. Puan ureten baska yol yoktur.
`AGIRLIKLAR` sozlugu **tek** agirlik beyanidir; `SURUM = "v1"`.

Bir alan puan alabilmek icin **uc** sart birlikte gecerli olacak:
1. Dolu (bos dize dolu sayilmaz),
2. Kimlik alani ise **D-246 kapisindan** gecmis (`etl/kimlik_no.py`),
3. **D-245** geregi kanit --- tahmin/varsayilan puan almaz
   (`NACE_KANIT_KAYNAKLARI = {mersis, external}`; `sector_default`,
   `title_default`, `predicted`, `fallback`, `unknown` = 0 puan).

`alan_puanlari()` alan bazli dokumu ayrica dondurur; kayip tablosu buradan
uretilir, ikinci bir formulden degil.

### 2. Ikinci yollar kesildi --- **gocun tek basina yetmedigi yer, ikinci kez**

D-255/6 dersi burada tekrar dogrulandi: kolon dogru, hesaplayici yanlissa
bir sonraki tur yanlisi geri yazar. Bu turda kesilenler:

| yol | ne yapiyordu | ne yapildi |
|---|---|---|
| `seed/seed_ankara_osb.py` | `round(60 + random.random()*35, 2)` --- puani **uyduruyordu** | uretim satiri kaldirildi (D-245) |
| `etl/hayalet_kayit_temizle.py` | birlesmede `COALESCE` ile eski puani **tasiyordu** | tasima kesildi; birlesme sonrasi tek kapidan hesaplanir |
| 15 adet `scripts/recalc*`,`p41_quality_boost*`,`p3_3_*` | her biri **kendi 0-100 formulunu** SQL'de yaziyordu | silindi |
| `tests/company_master/test_quality_score.py` | silinmis modulu test ediyordu (kirik) | silindi |

Kesme sonrasi 69 esleseme elle tarandi: **yazan yol kalmadi.** Kalanlar yalnizca
okuyor (`check_*`, `debug_*`, panel sekmeleri, `tenant/health`) veya test
fixture'i. `data_quality_toolkit/validator/quality_engine.py` **ayri sistemdir**,
`companies.identity_completeness`'e dokunmaz; karistirilmayacak.

### 3. Yazma tek ifadeyle (D-249/2)

`recalc_quality_scores()` ilk halinde `executemany` idi --- 9412 ayri UPDATE.
Gercek toplu yazmaya cevrildi:

```sql
UPDATE companies c SET identity_completeness = v.s, score_version = :v
  FROM (SELECT unnest(CAST(:ids AS uuid[])), unnest(CAST(:skorlar AS numeric[]))) v
 WHERE c.company_id = v.cid
```

**Kural:** "toplu yazma" = tek SQL ifadesi. `executemany` toplu **gonderimdir**,
toplu yazma degil; D-249/2'yi karsilamaz.

### 4. Mandal: 11 assert, kanca kurulu, **kirilarak** dogrulandi

`tests/test_kalite_puani.py`, framework yok, `python -X utf8` ile kosar.
Kapsanan: agirlik toplami tam 10.0 (kayan nokta), kimlik 6.0 + erisim 4.0,
tam satir 10 / bos satir 0, dogrulanmamis deger 0 puan, tahmin NACE 0 puan,
sicil no tek basina yetmez, bos dize dolu degil, 0-10 disina cikilamaz,
surum uyusmazsa bayat, zenginlik verisi puana girmez, `normalize.py` kendi
formulunu yazmaz.

Kanca: `.pre-commit-config.yaml` + `.git/hooks/pre-commit`, **always_run**
(DB'ye baglanmaz, 0.84 sn). D-255/3 geregi **kirma denemesi** yapildi:
agirlik 0.3 -> 0.4 yapildiginda kanca cikis kodu **1**, saglam halde **0**.
Mandal gercekten kosuyor.

### 5. Puan dibe yakin cikti --- bu **dogru** olcumdur

| Olcu | Deger |
|---|---|
| yazilan firma | 9412 (surum `v1`, bayat **0**) |
| en az / en cok | 1.00 / **6.50** |
| ortalama | **3.71** |
| **ulasilabilir tavan** | **6.5 / 10** |

Bant dagilimi (`width_bucket`): 1-2: 697, 2-3: 2155, 3-4: 1226, 4-5: 3021,
5-6: 2309, 6-7: 4.

**Ulasilabilir tavan kavrami:** **hicbir** firmanin alamadigi alanlarin agirligi
kalici kayiptir --- `tax_office` 0.5 + `mersis_number` 1.0 +
`trade_registry_number` 1.0 + `nace_code` 1.0 = **3.5 puan**, bugunku
kaynaklarla erisilemez. Tavan panelde/raporda **ilan edilir**; yoksa 3.71
"veri kotu" gibi okunur, oysa **kaynak yok**.

### 6. Alan bazli kayip tablosu --- yatirimin nereye yapilacagini bu soyler

9412 firma, toplam kayip 59167 puan.

| alan | agirlik | puansiz firma | kayip | ort. katki |
|---|---|---|---|---|
| `tax_number` | 1.5 | 9407 | **14110.5** | 0.00 |
| `mersis_number` | 1.0 | 9412 | 9412.0 | 0.00 |
| `trade_registry_number` | 1.0 | 9412 | 9412.0 | 0.00 |
| `nace_code` | 1.0 | 9412 | 9412.0 | 0.00 |
| `address` | 1.5 | 3614 | 5421.0 | 0.92 |
| `tax_office` | 0.5 | 9412 | 4706.0 | 0.00 |
| `primary_email` | 0.7 | 5374 | 3761.8 | 0.30 |
| `primary_phone` | 1.5 | 1161 | 1741.5 | 1.31 |
| `website_domain` | 0.3 | 3966 | 1189.8 | 0.17 |
| `legal_name` | 1.0 | 0 | 0.0 | 1.00 |

**Tek hamlede en cok acan yatirim: MERSIS kaynagi.** MERSIS kaydi VKN, vergi
dairesi, sicil no+dairesi ve NACE'yi **birlikte** tasir; baglanirsa
1.5+0.5+1.0+1.0+1.0 = **5.0 puan** acilir ve tavan 6.5 -> 10.0 olur.
Ikinci sirada adres (5421 puan, 3614 firma) --- ama tek alan, tavani yukseltmez.

**Kural:** yatirim siralamasi "hangi alan bos" degil, **"hangi kaynak kac alani
birden acar"** ile yapilir.

### 7. Sema: yeni goc **gerekmedi** (D-253)

Olculdu: goc disk = defter = 28; `0026_kimlik_kolonlari_ingilizce.sql` defterde;
`identity_completeness` numeric + `score_version` text mevcut; CHECK kisitlari
`companies_identity_completeness_range` (0-10) ve
`companies_score_version_required` zaten kurulu. 9412 satirlik yazma hatasiz
gecti --- yani kisitlar **fiilen** dogrulandi. Karar kapsaminda olmayan goc
yazilmadi.

### 8. Arac notu: `apply_diff` tekrar tekrar patladi, betik ilk seferde tuttu

`seed_ankara_osb.py` ve `hayalet_kayit_temizle.py` satir aralari bos oldugu icin
`apply_diff` 6 denemede tutmadi (96%/90%/85%/83%/48%). Cozum: `str.replace` +
`assert t.count(eski) == 1` kullanan tek seferlik betik --- bos satir duzeninden
bagimsiz ve **coklu eslesmede patlar**.

**Kural:** ayni dosyada iki `apply_diff` denemesi tutmazsa ucuncusu denenmez;
assert'li tek seferlik betige gecilir.

### 9. Acik borc

- **BORC-VKN-01:** 9412 firmanin **9407**'sinde dogrulanmis VKN yok. Tek basina
  en buyuk kayip kalemi (14110.5 puan). D-250/3: kaynak baglaninca agirlik
  1.5 -> 3.0 ve `SURUM` v2 olur; o an tum puanlar **bayat** isaretlenir.
- **BORC-PANEL-TAVAN-01:** tavan (6.5/10) henuz panelde **yazmiyor**; yalnizca
  bu kayitta ve raporda duruyor.

**Referans:** D-245, D-246, D-249, D-250, D-251, D-253, D-255. Arac:
`src/company_master/etl/quality_recalc.py`; mandal:
`tests/test_kalite_puani.py`; kanca: `.git/hooks/pre-commit`.

---

## D-257 --- MERSIS kapali, tavuk-yumurta dogrulandi (MERSIS-KAYNAK-01 olcumu)

**Tarih:** 2026-09-28 | **Rapor:** `docs/OLCUM_MERSIS_2026-09-28.md`
**Tur:** olcum karari --- D-256'nin "MERSIS baglanirsa 5.0 puan acilir" iddiasi sinandi.

### 1. MERSIS'te anonim sorgu ekrani **yoktur**

Olculdu: `mersis.ticaret.gov.tr/`, `/Portal/Home/Index`, `/uygulamalar` ve
`mersis.gtb.gov.tr` --- **dordu de ayni 30701B tanitim sayfasini** doner.
`/Portal/Firma/Sorgula` = 404. `robots.txt` = 404. Sayfada tek eylem "Giris"tir ve
sayfa metni aynen sunu yazar: "E-Devlet Yonetimi ile Giris **entegrasyon
asamasindadir**".

MERSIS bir **islem portalidir** (kurulus/tescil), sorgulama portali degildir.
Engel captcha degil --- **islev mevcut degil**.

### 2. D-256'nin 5.0 puan iddiasi **dogrulanamadi**

Cikti ekranina ulasilamadigi icin "MERSIS kaydi VKN + vergi dairesi + sicil no +
NACE'yi **birlikte** tasir" iddiasi sinanamadi. **Bugun acilan puan: 0.0.**

| alan | agirlik | bugun acilir mi | neden |
|---|---|---|---|
| tax_number | 1.5 | hayir | acik uclar VKN'yi **girdi** ister, cikti vermez |
| tax_office | 0.5 | hayir | hicbir acik kaynakta yok |
| mersis_number | 1.0 | hayir | sorgu ekrani yok |
| trade_registry_number | 1.0 | hayir | TSG captcha + uyelik |
| nace_code | 1.0 | hayir | kaynagi MERSIS (D-252), kapali |

Kilitli: 5.0 puan x 9412 firma = **47060 puan**. Tavan **6.50/10'da kalir**.

### 3. TAVUK-YUMURTA gercektir --- artik kanitli

Elde 9412 **unvan**, 5 **VKN** var. Olculen tum acik uclar girdi olarak
**VKN/TCKN** istiyor:

- GIB e-Fatura kayitli kullanicilar (uc kat iframe altinda bulundu:
  `ebelge.gib.gov.tr/efaturakayitlikullanicilar.html` -> `sorgu.efatura.gov.tr/kullanicilar/`
  -> `.../xliste.php`). Form alani etiketi **"VKN/TCKN"**, 2197374 kayit.
  Captcha gercek JPEG (`img.php`, 1285B, `\xff\xd8\xff\xe0`). Captcha'siz ve
  yanlis kodlu POST: "Guvenlik kodu hatali". Toplu ihrac yok
  (`xls.php`/`liste.php`/`kullanicilar.xml`/`.zip` = 404; `?xls=1` ayni form).
  **Yonu ters:** VKN -> unvan gider, unvan -> VKN gitmez. Ayrica vergi dairesi,
  sicil no ve NACE **tasimaz**.
- TOBB API uclari (`/api/sanayi`, `/api/sanayi-veri-tabani`, `/api/v1/sanayi/arama`)
  = **401**.
- EKAP: standart TLS el sikismasi basarisiz; `SECLEVEL=1` ile 200 (`ekapv2.kik.gov.tr`),
  `/ihale-arama` ve `/api/ihale/arama` = **406**.
- `veri.gov.tr`: uc varyantta da `ConnectionResetError 10054` --- **erisemedim** (D-245).
- `sorgu.gib.gov.tr`: DNS cozulmuyor --- **erisemedim** (D-245).

**Unvanla sorguya izin veren tek kaynak TSG'dir** (`unvansorgulama.php`, form
`FormUnvanSorgulama`, `Captcha` maxlength=**4**); captcha'siz POST sonuc dondurmez,
ilan goruntuleme `girisyap.php`'ye yonlenir. `TSG-KAYNAK-01` **kapali kalir**.

### 4. Yasal dayanak **yoktur**

MERSIS, TSG ve GIB'in kullanim sartlari/gizlilik sayfalarinin **besi de 404**.
Yazili izin de yazili yasak da bulunamadi. GIB form etiketinde **TCKN** acikca
geciyor --- gercek kisi tacir kayitlari kisisel veri tasir; **D-247/D-248 riski
dogrulandi**.

**Kural:** yazili izin bulunmayan, captcha ile korunan ve TCKN tasiyabilen
kaynaktan toplu otomatik cekim **yapilmaz**. Captcha kirma / oturum taklidi
teknik secenek olarak degerlendirilmez.

### 5. Beklenen karar (urun sahibi)

- **A) Resmi basvuru** --- Ticaret Bakanligi'na MERSIS erisim talebi + TOBB API
  yetki basvurusu (401 donen uc). Tek mesru yol.
- **B) Ticari veri saglayici** --- unvan -> VKN eslemesi satin al. Saglayicinin
  kaynagi da D-245'e tabidir.
- **C) Kapsami kabul et** --- kimlik tamligi tavanini **6.50/10** olarak dondur,
  kilitli 5 alani D-249 geregi **NULL** say (0 puan sayma).

**Onerilen: C simdi + A paralel.** B ancak A reddedilirse.

### 6. Acik borc

- **BORC-VKN-01** kapanmadi; kaynak bulunamadi (bkz. D-256/9).
- **BORC-PANEL-TAVAN-01** kapanmadi; tavan 6.5/10 hala panelde yazmiyor.
- **MERSIS-KAYNAK-01 kapandi** --- sonuc: **kapali**. Yeniden acilmasi ancak
  A veya B secenegi ile mumkundur.

**Referans:** D-245, D-247, D-248, D-249, D-250, D-252, D-256. Rapor:
`docs/OLCUM_MERSIS_2026-09-28.md`.

## D-258 — Panel tavani ilan eder; "yarim goc" yedi ayri yerde bulundu (2026-09-28)

**Gorev:** PANEL-DURUSTLUK-01. Panel sayilari gerceginden IYI gorunuyordu.
Iki yalan olculdu, ikisi de kapatildi; arama kapsami genisletilince ayni
desenin yedi varyanti cikti.

### 1. Tavan artik turetilir, sabit yazilmaz

`etl/quality_recalc.py` icindeki `AGIRLIKLAR` tek beyandir; ulasilabilir tavan
o setten **hesaplanir**. Agirlik seti v2 olunca tavan, bantlar ve risk esigi
kendiliginden guncellenir. Mandal bunu kirilarak dogrular: tavan sabite
donerse `test_tavan_agirlik_setinden_turetilir` kirmizi yanar.

- Olculen: ortalama **3.71**, en yuksek **6.50**, n=**9412**.
- Ulasilabilir tavan **6.50/10**. Kalan 3.50 puan `mersis` (1.0),
  `trade_registry` (1.0), `nace_code` (1.0), `tax_office` (0.5) alanlarinda
  **kilitli** --- kaynak yok (D-257: MERSIS kapali, TOBB 401, TSG captcha).
- Panel artik `3.71 / 6.50 ulasilabilir` yazar. Kilitli alanlar ayri listelenir
  ve **nicin** kilitli oldugu okunur. **BORC-PANEL-TAVAN-01 kapandi.**

### 2. Sunum tek kapidan gecer: `src/company_master/sunum.py`

D-256 puan **URETIMINI** tek kapiya baglamisti; puan **SUNUMU** hala 20+
dosyaya dagilmisti. Tek yer duzeltilse ikinci ekran eski yalani gostermeye
devam ederdi. Kapi fonksiyonlari: `tavan_getir`, `puan_metni`, `tavan_metni`,
`kilit_satirlari`, `nace_metni`, `sektor_sayaci`, `bantlar`, `bant_dagilimi`,
`risk_esigi`. Mandal: hicbir panel dosyasi `/100` olcegi yazamaz.

### 3. NACE tahmini artik etiketli

D-252 olcumu: NACE kodlarinin **%100'u tahmin**, dogrulanmis kod **sifir**.
1880 firma tek bir `29.10` kodunda yigilmis --- bu sektor dagilimi degil,
**varsayilan deger kutlesi**. `sektor_sayaci()` tahmini kodu sayaca almaz;
ekranda "tahmin haric: N" olarak **ilan edilir**. Sayactan cikarmak yetmez;
kullanici NICIN dustugunu gormeli.

### 4. "Yarim goc" deseni: ad degisti, ona bagli sey kaldi

Ayni desenin **yedi** varyanti olculdu. Kolon `data_quality_score` (0-100) ->
`identity_completeness` (0-10) tasinmisti; tasinmayanlar:

1. **Performans ayagi** --- 27 indeksin 5'i terk edilmis kolondaydi, sorgular
   seq scan'e dusuyordu. `0029` gocu ile tasindi.
2. **Ana sema beyani** --- `companies.sql` canli kolonu bilmiyordu; sifirdan
   kurulan DB olu kolonla doguyordu.
3. **SQL esigi** --- `/api/quality-trend` kolonu yeni, CASE esikleri (80/60/40/20)
   eskiydi; panel **butun** firmalari en kotu banda dusuruyordu.
4. **Tenant sagligi** --- olcek karisimi yuzunden tenant yapisal olarak GREEN'e
   ulasamiyordu.
5. **Silme karari (en agiri)** --- `scripts/dedup_apply.py` kazanani bayat
   kolonla seciyordu. Bayat kolon yanlis kaydi kazandirip **dogrusunu
   siliyordu**. Veri kaybi riski; kazanan artik canli kolonla secilir.
6. **Sabit esik** --- `scripts/quality_remediation.py` esigi `30.0` yaziliydi.
   Kolon 0-10 oldugu icin **9412 firmanin tamami** "duzeltilmeli" listesine
   giriyordu. Esik artik `risk_esigi(tavan_getir())` ile turetilir.
7. **Ikinci indeks kaynagi** --- `setup_local_indexes.py` ve
   `p44_apply_indexes.py` gocun **eski** indeks adini geri kuruyordu;
   calistirilsalardi goc defteri kirilirdi. Ikisinden de puan indeksi tanimi
   kaldirildi; `0029` tek kanonik kaynaktir.

**Kural:** kolon adi degistiginde arama kapsami sadece okuyan kodla
sinirlandirilmaz. Ayni turda **indeks / sema beyani / SQL esigi / silme
karari / esik sabiti / ikincil DDL betigi** taranir. Bunlarin hicbiri testte
gorunmez --- altisi da sifir test kapsamindaydi.

### 5. `dusen-iz:` --- goc defteri korlesmeden daraltilir

`0029`, `0008/0009/0011` gocelerinin indekslerini yeniden adlandirinca defter
o uc gocu "uygulanmamis" saydi. `ustunden-gecen:` dosyanin **tamamini**
eskitir --- hala gecerli 4-6 iz tasiyan bir dosyaya yazmak defteri **kor**
ederdi. Bunun yerine iz bazli isaret kullanildi:

```sql
-- dusen-iz: idx_companies_quality_score
```

Yalniz adi gecen iz aranmaz; dosyanin geri kalani denetlenmeye devam eder.

### 6. Mandal ve kanca

`tests/test_panel_durustluk.py` --- 16 assert. Kanca
`scripts/hooks/pre-commit` (depoda durur, `.git/hooks` surumlenmez;
`git config core.hooksPath scripts/hooks` ile kurulur) artik **iki** takim
kosar: panel durustlugu + goc defteri. Sema degisikligi commit'e tek basina
giremez (D-251/3). Tam takim (~170 sn) kancaya konmaz; kanca ~15 sn.

### 7. Bayat testler duzeltildi --- test de bir beyandir

- `test_api_integration.py::test_quality_trend_liste` **duzeltilen yalani
  savunuyordu**: `"60-79"` gibi 0-100 bandi bekliyordu. Yeni sozlesmeye
  tasindi; artik bandin tavandan turedigini ve olculmemis firmanin hicbir
  banda yazilmadigini (D-249) dogrular.
- `test_hayalet_kayit_temizle.py` uretim dizinini **mutlak** bos kontrol
  ediyordu. Dizindeki `hayalet_20260927.jsonl` 4591 firmanin silinme denetim
  kaydidir, git'te izlidir. Test artik "dizin bos" degil "**bu kosu
  yazmadi**" olcer. Prova testinin gecmesi icin kanit silinmez.

**Sonuc:** 4439 -> **4441 passed**, kalan tek kirmizi `test_kok_politikasi`
(dis koktekki iki kullanici dosyasi, ajanla ilgisiz).

### 8. Arac notu

`apply_diff` bu turda **4 kez ustuste** tuttu (D-256/8'deki tersine).
Yine de cok-dosyali yama betikle yapildi. Betik iki ders birden ogretti:
**idempotent olmali** (yarim uygulanmis durumdan devam edebilsin) ve
**yamanin icerigini basmamali** --- terminal cp1254, yamada `→` vardi,
`UnicodeEncodeError` betigi 13 yamanin 7'sinde kesti (D-86).

### 9. Acik borc

- **BORC-KOLON-DUSUR-01** --- `data_quality_score` kolonu hala duruyor
  (9412 satir dolu). `0029` bilerek dusurmedi; dusurme ayri karar ister.
  Duruyorken **her yeni kod onu yeniden kullanabilir** --- bu turda 7 kez oldu.
- **BORC-VKN-01** ve **BORC-NACE-DOGRULAMA-01** acik; ikisi de kaynak bekler
  (D-257/5: A veya B secenegi).
- Dis kokte 2 izinsiz dosya (`_kalan.txt`, `veri kumesi maxmum kolon .txt`)
  --- D-241 ihlali, urun sahibinin dosyalari, dokunulmadi.

**Referans:** D-86, D-241, D-243, D-245, D-249, D-250, D-251, D-252, D-253,
D-256, D-257.

---

## D-259 — Olu kolon pasiflestirildi; panel yalani uc katmanda birden bulundu (2026-09-28)

**Karar (urun sahibi):** `data_quality_score` dusurulmez, **pasiflestirilir**.
Firma kimlik dosyalari olgunlasinca revize edilip kullanilabilir. Veri silinmez.

### 1. Pasiflestirmenin en durust yolu: COMMENT + mandal (ad degisikligi DEGIL)

Olculdu, sonra secildi:

| Yol | Olcum | Karar |
|---|---|---|
| `DROP COLUMN` | 9412 satir dolu | **Hayir** — urun sahibi veriyi istiyor |
| `_deprecated_` on eki | D-258'de yarim goc 7 ayri yerde bulundu | **Hayir** — ikinci yarim goc riski |
| `COMMENT ON COLUMN` | indeks 0, VIEW 0, FK 0 — kolon izole | **Evet** — semada duran gerekce |
| Mandal (test) | tek basina semada iz birakmaz | **Evet, COMMENT ile birlikte** |

Ad degisikligi **reddedildi**: D-258 zaten bir yarim gocun 7 kalintisini
buldu; ayni riski ikinci kez almak gerekcesizdir. Kolon **yerinde kalir**,
semada "OKUMAYIN, YAZMAYIN" yazar, mandal yeni kullanimı engeller.

Goc `0030_olu_kolonu_pasiflestir.sql` (+ `down/`), defterde **TAM**,
izi `pg_description`'da dogrulandi, **9412 satir korundu**.
`goc_defteri.py` bu turda `COMMENT ON COLUMN` izini ogrendi — ogrenmeseydi
`0030` defterde **IZSIZ** gorunurdu (D-253 bosluğu).

### 2. Panel yalani: tek degil UC katman

Brief "kolonu pasiflestir" diyordu. Olcum uc ayri yalan buldu — ucu de ayni
kokten (0-100 olcekli olu kolon x 0-10 olcekli canli kolon):

1. **Tablo/detay** — `app.js` `data_quality_score` okuyordu; kolon panele hic
   gelmiyor. 9412 firmanin **hepsi** `0` gorunuyordu. (D-249 ihlali: yokluk 0 degil.)
2. **KPI karti** — `/api/kpi` 0-10 ortalamasini donuyordu, panel `"X.X/100"`
   yaziyordu. Ayni sayi, dort kat kucuk gosterilen olcek.
3. **Filtre** — slider `max="100"`, API clamp `min(x, 100)`, kolonun gercek
   azamisi **6.50**. `min_score=20` secmek **9412 firmanin hepsini eliyordu**;
   ekranda normal bir filtre goruntusuyle, **sessizce**.

3. madde briefte yoktu ve kullaniciya en pahalıya mal olan yalandi: bos
sonuc "firma yok" gibi okunur.

### 3. Duzeltme: tavan API'den gelir, esik kodda yazmaz

`/api/companies` ve `/api/kpi` artik `"tavan"` doner (`sunum.tavan_getir()`,
`lru_cache`li). Panel bantlari `scoreTavan / 5` ile turetilir —
`sunum.bantlar()` ile **ayni formul**. Panelde tek bir `0-100` sabiti kalmadi.
Slider ust sinirini calisma aninda tavandan alir (`syncScoreSlider`).
Olculmemis puan `—` basar ve siralamada dibe duser (D-249).

**Olculen tavan:** 6.50 / azami 10.00. Kilitli 3.50 (`tax_office` 0.5,
`mersis_number` 1.0, `trade_registry_number` 1.0, `nace_code` 1.0 — D-257).
`identity_completeness` gercek araligi **1.00–6.50**; MAX tam tavana esit.

### 4. Mandal neden tutmadi: `*.py` tarıyordu

`test_panel_durustluk.py` D-258'den beri var, ama `_panel_dosyalari()`
yalniz `*.py` topluyordu. Panelin **yuzu** `app.js` ve `index.html`'dir.
Yalan tam bu delikten gecti. Mandal artik `.py/.js/.html` tarar
(`/100` denetimi Python'da AST, digerlerinde satir bazli).

**Ders:** bir mandalin kapsamı, korudugu seyin **yuzeyini** kapsamalidir;
dilini degil.

### 5. Olu dosya silindi

`web_dashboard/index_old.html` — olculdu: `web_app.py` yalniz `index.html`
servis ediyor, canli referans **0**. Iki eski yalan (0-100 bant, olu kolon)
icinde duruyordu. Silindi; muaf tutulmadi.

### 6. Kapanan / acilan borc

- **BORC-KOLON-DUSUR-01 kapandi** — kolon duruyor ama artik "yeniden
  kullanilabilir" degil: semada yasak yazili, mandal commit'i keser.
- **BORC-PERF-BANT-01** — ~~`perf_monitor.py` hala 0-100 bant kullaniyor.
  Panel degil, ic olcum araci; yaniltici ama kullaniciya gitmiyor.~~
  **D-266'da kapandi:** bant yalani gercekti (9409/9409 tek bant), ama
  "ic olcum araci" beyani da yanlisti — uretimde cagrani yoktu. Duzeltilmedi,
  yuzey kapatildi (5 dosya dustu).
  Tavana baglanmali.
- Dis koktekki 2 izinsiz dosya **silindi** (D-241 ihlali kapandi); icerikleri
  `docs/HEDEF_VERI_KAPSAMI.md` olarak yapilandirildi.

### 7. Brief hatasi sayaci: 7

`_kalan.txt` "ikinci yarisi" degil **kuyruk kopyasiydi** — birlestirme
metni ciftlerdi. "~60 alan" 35 obekti. "Kolonu pasiflestir" isinin
**ucte biriydi**. Kural teyit edildi: **brief sayilarina guvenme, olc.**

**Referans:** D-241, D-245, D-249, D-250, D-251, D-253, D-257, D-258.

---

## D-260 — Teslim ozeti kanit degildir; kayit kapsamasi firma kapsamasi degildir (2026-09-28)

**Tur:** onay karari — 6 bekleyen teslim canli veritabaninda olculdu.
**Arac:** tek seferlik denetim betigi (is bitince silindi).

### 1. Olcum sonucu: 5 dogru, 1 yanlis beyan

| Teslim | Iddia | Canli olcum | Sonuc |
|---|---|---|---|
| VERI-HAYALET-TEMIZ-01 | 9412 firma + UNIQUE indeks | 9412, indeks var | onay |
| VERI-NACE-TEMIZ-01 | 555 `invalid_cleared` | 554 (1'i hayalet temizliginde silindi) | onay |
| VERI-NACE-KOLON-01 | 0 NACE pattern, 0 kacak etiket | 0 / 0 | onay |
| VERI-NACE-SOZLUK-01 | 3319 NACE kodu | 3319 | onay |
| TEST-BACKLOG-20 | 20 test kapandi | suit ayri olculur | onay |
| **VERI-KAYNAK-BAG-01** | **"yetim 0"** | **8748 yetim** | **RED** |

### 2. Kural: teslim ozeti onay gerekcesi degildir

`VERI-KAYNAK-BAG-01` ozeti "yetim 0" yaziyordu. `source_records` 14000 satir,
`company_id` dolu 5252, **bos 8748**. Ozet korlemesine onaylansaydi kopuk
kaynak zinciri "kapandi" damgasi alacakti. **Onay, teslim metnine degil
canli olcume dayanir.** Bu, D-245'in ("doluluk gecerlilik degildir") gorev
panosuna tasinmis halidir.

### 3. Kayit kapsamasi ≠ firma kapsamasi

Ayni ozet "5252 eslesme (37.5%)" diyordu. Bu **kayit** yuzdesidir. Firma
tarafinda 5252 kayit yalnizca **3068 farkli firmaya** baglidir; 9412
firmanin **6344'u kaynaksizdir**. Dogru iki cumle:

- kayit kapsamasi **%37.5** (5252 / 14000)
- **firma kapsamasi %32.6** (3068 / 9412)

Tek oran yazilirsa okuyan her zaman iyi olani anlar. **Iki taraf birden
yazilir.** Sayaci paydasiyla birlikte anmayan cumle olcum sayilmaz.

### 4. Kalan is

`VERI-KAYNAK-BAG-01` aktife dondu. Yeniden teslimde iki oran ayri yazilacak,
8748 yetim ya baglanacak ya gerekcesi belgelenecek.

**Referans:** D-245, D-250, D-252, D-259.

---

## D-261 — Bagalayici calistirilmamisti; content_hash yinelenmeyi durdurmuyor (2026-09-28)

**Tur:** olcum + duzeltme. D-260'in "kalan is" maddesi isletildi, iki yeni
kusur kanitlandi.

### 1. Kod yazilmisti ama kosturulmamisti

`kaynak_bagla.py` calistirildi: 8748 yetimin **1517'si tek satir kod
degisikligi olmadan** baglandi. Teslim "yetim 0" derken betik ya hic
kosturulmamis ya yarida kalmis. **Kural: "kod yazildi" ile "kod kosturuldu
ve veritabanina yansidi" ayri iki olaydir; teslim ikincisini kanitlar.**

Bag sonrasi olcum (D-260 formatinda, iki taraf birden):

- kayit kapsamasi **%48.4** (6769 / 14000)
- firma kapsamasi **%46.2** (4352 / 9412)

Baglanan 6769 kaydin ham karsilastirmada 1555'inde ad tutmuyor gorundu;
**normalize edilince gercek uyusmazlik 31.** Kalani Turkce buyuk harf
donusumuydu. **Uyusmazlik once normalize edilerek olculur**, yoksa saglam
bag hatali gorunur.

### 2. `content_hash` yinelenmeyi durdurmuyor

`source_records` 14000 satir; `source_id + external_id` ikilisinde
benzersiz **10120**. **3880 satir (%27.7) yinelenmis.**

| kaynak | toplam | benzersiz | yinelenen |
|---|---|---|---|
| ostim.org.tr | 9513 | 9513 | 0 |
| ivedik.org.tr | 3134 | 14 | **3120** |
| baskentosb.org.tr | 761 | 0 | **761** |
| aso.org.tr | 592 | 592 | 0 |

En uc ornek: tek firma icin **228 satir** — ayni `external_id`, ayni
`raw_name`, ayni `raw_phone`, ayni `collected_at`, ama **228 farkli
`content_hash`**. Hash degisken bir alan (zaman damgasi / satir kimligi)
iceriyor; bu yuzden **ayni icerik her kosuda yeni satir aciyor**.
`content_hash`'e yaslanan her yinelenme onlemi calismiyor.

`baskentosb.org.tr` benzersiz sayisi **0**: `external_id` tamamen bos,
o kaynakta kayit kimligi hic uretilmemis.

### 3. Sisirilmis payda

14000 payda **gercek degil**; gercek benzersiz kayit 10120. D-260'in
"paydasiyla birlikte an" kurali bir adim ilerler: **payda da olculur.**
Yinelenmis satir sayan payda kapsamayi oldugundan dusuk, yinelenmis satir
sayan pay oldugundan yuksek gosterir.

### 4. VKN kanali olu

`companies.tax_number` dolu **5 / 9412**; `source_records.raw_tax_number`
dolu **617 / 14000**. Bagalayicinin vergi no kanali **0 eslesme** uretti.
D-257'nin (VKN kaynagi kapali) veri tarafindaki teyidi.

### 5. Acilan borclar

- `BORC-DEDUP-KAYNAK-01` — `content_hash` uretimi duzeltilecek,
  `(source_id, external_id)` UNIQUE kisiti konacak, 3880 yinelenen satir
  temizlenecek. Kisit olmadan her kaziyici kosusu tabloyu yeniden sisirir.
- `BORC-EXTID-01` — `baskentosb.org.tr` kaziyicisi `external_id`
  uretmiyor (761 satir kimliksiz).
- `BORC-AD-VARYANT-01` — 31 kisaltma varyanti (`SANAYI`/`SAN.`,
  `LIMITED SIRKETI`/`LTD. STI.`); normalize sozlugu kapsamayi artirir.
- `VERI-KAYNAK-BAG-01` kapanmadi: kalan 7231 yetim (ostim 5094,
  ivedik 892, baskentosb 669, aso 576) yinelenme temizligi sonrasi
  yeniden olculecek.

**Referans:** D-245, D-257, D-259, D-260.

## D-262 — Kimliksiz satir kisittan muaftir; silmeden once referans tasinir (2026-09-28)

**Tur:** duzeltme. D-261'in `BORC-DEDUP-KAYNAK-01` ve `BORC-EXTID-01`
borclari kapandi. Iki goc kosturuldu ve canli veritabaninda olculdu.

### 1. NULL, UNIQUE kisitinin kor noktasidir

Goc 0031 kopya temizligini `(source_id, external_id)` uzerinden yapti ve
ayni ikiliye UNIQUE kisiti koydu. 3120 ivedik kopyasi temizlendi. Ama
`baskentosb.org.tr`'nin 761 satirinda `external_id` **NULL** idi.

PostgreSQL'de (standart SQL'de) **NULL hicbir NULL'a esit degildir**; bu
yuzden 761 satirin hicbiri kisiti ihlal etmedi, temizlikten de muaf kaldi.
Kisit konuldu, tablo "temiz" gorundu, kopyalar yerinde durdu.

**Kural: UNIQUE kisidi NULL iceren kolon uzerine kuruluyorsa, kisit o
satirlar icin YOKTUR. Kimlik kolonu NOT NULL degilse benzersizlik
garantisi de yoktur.** Kisit yazan her goc, kolonun NULL kabul edip
etmedigini ayrica olcer.

### 2. Kimlik uretimi kaynaga geri takildi

`ingest_ivedik_baskent.py` baskentosb kazima yolunda `external_id`
uretmiyordu. Duzeltildi, yeniden kosturuldu: 482 kimlikli satir yazildi.
Ayni firmalar tabloda iki kez durdu — 761 kimliksiz eski + 482 kimlikli
yeni.

### 3. Silmeden once TASIMA (goc 0032)

Eski 761 satirin 243'u `companies.source_record_id` ile isaret ediliyordu,
92'sinin `company_id` bagi vardi. Dogrudan silme 243 firmanin kaynak izini
koparirdi (D-260: kaynak izi kanittir).

Goc sirasi: ad eslesmesiyle eski-yeni haritasi kur → firma bagini devret →
`companies.source_record_id` referanslarini yeni satira tasi → ancak sonra
eski satirlari sil. Ad iki yeni kayda giden 4 satirda **en kucuk kimlik**
secildi; goc tekrar kosturulursa ayni sonucu verir (deterministik).

Goc, esi bulunamayan **tek bir satir** bile varsa `RAISE EXCEPTION` ile
durur. Olcumde 0 idi; mandal olcumun sonradan bozulmasina karsidir.

### 4. Goc sonrasi canli olcum

| kaynak | satir | kimliksiz | bagli |
|---|---|---|---|
| ostim.org.tr | 9513 | 0 | 4419 |
| aso.org.tr | 592 | 0 | 16 |
| baskentosb.org.tr | 482 | 0 | 57 |
| ivedik.org.tr | 14 | 0 | 10 |

- `source_records` **14000 → 10601** (3399 yinelenen satir dustu)
- kalan `(source_id, external_id)` kopyasi: **0**
- kimliksiz satir: **0**
- kirik `companies.source_record_id`: **0**
- `companies` satir sayisi: **9412** (degismedi — D-259 korumasi tuttu)

Payda duzeldigi icin kapsama da duzeldi: kayit kapsamasi
**%42.5** (4502 / 10601), firma kapsamasi **%46.2** (4352 / 9412).
Firma kapsamasi degismedi; **yinelenme temizligi bag uretmez, sadece
paydayi durustlestirir.** D-261'deki "sisirilmis payda" kapandi.

### 5. Arac notu

Goc dosyasi psycopg ile kosmuyordu: surucu SQL metnindeki yuzde isaretini
parametre yer tutucusu sanip dosyayi **hic calistirmadan** reddetti.
Cozum iki yonlu — goc metninde yuzde isareti kullanilmaz, kosturucu ham
baglanti uzerinden calisir. **Not: bir goc "psql'de calisiyor" diye
uygulamadan da calisacak demek degildir.**

### 6. Kalan borclar

- `VERI-KAYNAK-BAG-01` **kapanmadi**: 5060 yetim firma duruyor. Payda
  duzeldi, bag sayisi duzelmedi — kalan is ad normalizasyonudur.
- `BORC-AD-VARYANT-01` acik: 31 kisaltma varyanti, normalize sozlugu.

**Referans:** D-241, D-259, D-260, D-261.

## D-263 — Iki isaretci bir bagi tarif ediyorsa ikisi de yalan soyler (2026-09-28)

**Tur:** duzeltme. D-262'nin `VERI-KAYNAK-BAG-01` borcu **kapandi**, ama
tahmin ettigim nedenden degil. Teshis yanlisti.

### 1. Benim teshisim yanlisti

D-262'de "5060 yetim firma duruyor, kalan is ad normalizasyonudur" yazdim
ve `BORC-AD-VARYANT-01`'i actim. Ad varyantlarini olcmeye gittigimde
eslesmeyen ornekleri **elle okudum** — ve hicbiri eslesmiyor gorunmuyordu
cunku zaten eslesmisti.

Gercek olcum: firmalarin 9409'unun `companies.source_record_id` degeri
**doluydu**. Yetim firma sayisi 5060 degil, **3** idi. "5060 yetim"
rakamini `source_records.company_id` uzerinden saymistim. Iki sayi ayni
soruya iki farkli cevap veriyordu cunku **iki farkli kolona bakiyorlardi**.

**Kural: bir borcu kapatmadan once borcun kendisini olc. Yanlis teshis
uzerine yazilan dogru kod, yanlis sorunu cozer.** Ad normalizasyonu
yazilsaydi calisirdi, test gecerdi, hicbir sey duzelmezdi.

### 2. Bag iki yerde saklaniyordu ve ikisi celisiyordu

| yon | kolon | anlam | dolu |
|---|---|---|---|
| A | `companies.source_record_id` | firmanin dogdugu kayit (1:1) | 9409 |
| B | `source_records.company_id` | kaydin ait oldugu firma (1:N) | 4502 |

Ikisini yazan kod farkliydi, senkron eden kod **yoktu**. 5052 bagda A dolu
B bostu. Sonuc: ayni sorunun paydasi hangi kolona baktiginiza gore
degisiyordu.

En keskin kanit **tek bir dosyanin icindeydi**: `etl/quality_metrics.py`
satir 168 A yonunu, satir 176 B yonunu kullaniyor. Ayni dosyadaki iki
metrik **9409 ve 4352 firmalik iki ayri evren** goruyordu. Hicbiri hata
vermiyordu; ikisi de "dogru" sayiyi donduruyordu.

**Kural: bir iliski iki kolonda saklaniyorsa, ikisini senkron tutan tek
bir yer OLMAK ZORUNDADIR. Yoksa iki kolon iki gercek uretir ve ikisi de
sorgu yazana gore hakli cikar.**

### 3. Cozum: kaynak yon + trigger (goc 0033)

A yonu 1:1 (ayni kayda isaret eden birden fazla firma: 0), B yonu 1:N
(birden fazla kaydi olan firma: 72). B yonu A'dan turetilebilir, tersi
turetilemez — bu yuzden **A kaynak, B turev** secildi.

Goc iki is yapti: (1) B yonunu A'dan doldurdu, (2) `companies` uzerine
`AFTER INSERT OR UPDATE OF source_record_id` trigger'i kurdu; bundan sonra
A yazildiginda B kendini yaziyor. Ayrica iki kolona da hangi yonun ne
demek oldugunu anlatan COMMENT dusuldu.

Trigger kagit uzerinde degil **canli DB'de** dogrulandi: bir kaydin B yonu
bosaltildi, A yonu kendi degeriyle yeniden yazildi, B kendini doldurdu
(olcum islem sonunda geri alindi).

### 4. Goc sonrasi canli olcum

| olcum | once | sonra |
|---|---|---|
| A yonu dolu | 9409 | 9409 |
| B yonu dolu | 4502 | **9554** |
| B yonundeki tekil firma | 4352 | **9400** |
| senkron degil (A dolu, B bos) | 5052 | **0** |
| `quality_metrics` sat.168 paydasi | 9409 | 9409 |
| `quality_metrics` sat.176 paydasi | 4352 | **9400** |

Firma kapsamasi **%46.2 → %99.9** (9400 / 9412). D-262'de "yinelenme
temizligi bag uretmez" demistim; dogruydu. Bagi ureten temizlik degil,
**zaten var olan bagin gorunur kilinmasiydi.**

### 5. Dokunulmayan: 9 capraz tutarsizlik

9 kayitta A ve B **farkli firmayi** gosteriyor. Hepsi ayni desende:
`companies` tablosunda hem `X A.S.` hem `(IFLAS NEDENIYLE) TASFIYE
HALINDE X A.S.` kaydi var. Bu **isaretci sorunu degil, firma seviyesi
yinelenmesi**; goc bu 9 satira dokunmadi.

Olcum: 23 tasfiye onekli firma kaydi var, bunlarin **22'sinin oneksiz
ikizi DB'de mevcut**. Tasfiye bir firmanin **hali**dir, ayri firma degil.
Yeni borc: `BORC-TASFIYE-IKIZ-01`.

### 6. Kalan borclar

- `BORC-AD-VARYANT-01` **iptal**: dayandigi teshis yanlisti. Ad varyanti
  sorunu 5052 bagi engellemiyordu; senkronsuzluk engelliyordu.
- `BORC-TASFIYE-IKIZ-01` **yeni**: 22 tasfiye onekli firma, oneksiz
  ikiziyle birlestirilmeli; `legal_status` alani ile hal kaydedilmeli.

**Referans:** D-241, D-260, D-261, D-262.

---

## D-266 — Cagrani olmayan kodun yalani da yalandir; ve mandal kendi kor noktasini korur (2026-09-28)

**Borc adi yanlisti.** `BORC-PERF-BANT-01` defterde soyle yaziyordu:
*"`perf_monitor.py` hala 0-100 bant kullaniyor. Panel degil, ic olcum araci;
yaniltici ama kullaniciya gitmiyor."* Iki iddiadan biri dogru, digeri eksikti.

**Bulgu 1 — bant yalani gercekti ve "yaniltici"dan fazlasiydi.** Canli DB'de
sorgu sablonunu kosturdum:

```
--- QUALITY_TREND_QUERY canli cikti ---
{'bucket': '0-19', 'cnt': 9409}
--- gercek dagilim (sunum.py tek kapisi, tavan=6.5) ---
{'0.00-1.30': 673, '1.30-2.60': 1814, '2.60-3.90': 1588,
 '3.90-5.20': 5329, '5.20-6.50': 5, 'olculmedi': 0}
```

Kolon 0-10 olceginde; esik 80/60/40/20 sabitti. **9409/9409 firma tek banda,
en kotu banda dusuyordu.** Bu "yaniltici" degil, ciktinin tamami yanlis.
D-258/4'te `/api/quality-trend` icin kesilen yalanin **sekizinci varyanti**.

**Bulgu 2 — "ic olcum araci" beyani da olcume dayanmiyordu.** Zincir:

| Dosya | Cagrani |
|---|---|
| `src/company_master/dashboard/perf_monitor.py` | yalniz asagidaki 3 betik |
| `scripts/dashboard_perf_monitor.py` | **yok** |
| `scripts/p44_benchmark.py` | yalniz `p44_final_benchmark.py` |
| `scripts/p44_final_benchmark.py` | **yok** |
| `scripts/perf_report.py` | **yok** (yalniz 2 belge metni) |

`DashboardPerfMonitor` uretimde hicbir yerden cagrilmiyor. Uretimdeki
`/api/performance` [`web_app.py:3484`](web_app.py:3484) kendi `_perf_time` /
`_DB_TIME_MS` sayaclariyla calisiyor. P4-4 devir notu *"app.py Streamlit
dashboardu DashboardPerfMonitor modulunu kullanmalidir"* diyor — **gelecek
zaman kipi, hic kullanilmadiginin itirafi.** Ayrica `perf_report.py:49` terk
edilmis `data_quality_score` ile siraliyordu (BORC-KOLON-DUSUR-01 izi).

**Karar — yeniden yazma yok, kapatma var.** D-265: cagrani olmayan kod,
kapatilacak koddur. `sunum.bantlar()`'a baglamak, kimsenin bakmadigi bir
ciktiyi dogru hesaplamak icin ikinci bir yuzey yasatmak olurdu. Dusen 5 dosya:
`src/company_master/dashboard/` (paket komple), `scripts/dashboard_perf_monitor.py`,
`scripts/p44_benchmark.py`, `scripts/p44_final_benchmark.py`, `scripts/perf_report.py`.

**Bulgu 3 — mandal neden gormedi.** `test_panel_durustluk.py` yalniz
`_PANEL_KOKLERI = ("web_dashboard", "scripts/dashboard.py", "web_app.py")`
tariyordu. `src/` ve `scripts/`'in geri kalani **kor noktaydi**; yalan tam
oradan gecti. Ayrica eski mandal `/100` **metnini** ariyordu — bu yalan metin
degil **SQL esigiydi**, desene hic takilmazdi.

**Kural.** Olcek yalani nerede yazildigina bakilmaksizin yalandir; "kullaniciya
gitmiyor" bir muafiyet degil, kapatma gerekcesidir. Mandal, korumak istedigi
sozlesmenin gecerli oldugu **her** kokte kosmalidir; kapsami daralan bekci
kendi kor noktasini korur.

**Mandal.** `test_kimlik_tamligina_yuz_olcekli_esik_uygulanmaz` — `src`,
`scripts`, `web_dashboard`, `web_app.py` icinde `identity_completeness` ile
10'dan buyuk **sabit** sayiyi karsilastiran her satiri suclar. Turetilen esik
(`{esik_yuksek}`, `:score_min`) sayi olmadigi icin gecer; sabit gecemez.

**Kanit.**
- Negatif kontrol: yalan geri konuldu → `KIRILDI - ... _mandal_negatif.py:1 -> 80`;
  kaldirildi → 17/17 `PANEL-DURUSTLUK-01 mandallari gecti`.
- Kalan olcek izi taramasi: `scripts/dashboard.py` (`{esik_yuksek}` turetilmis),
  `web_dashboard/tabs/admin_search.py` (`sunum.bant_dagilimi` kullaniyor),
  goc `0026` (0-10 CHECK kisiti) — **ucu de temiz.**
- Canli: `identity_completeness` min/max/avg = 1.00 / 6.50 / 3.71, n=9409.

**Kapanan borc.** BORC-PERF-BANT-01 — adi "bant duzelt" diyordu, isin dogrusu
"yuzeyi kapat" cikti. **Kendi borc listem de bir beyandir, olcum degil.**

**Referans:** D-241, D-249, D-250, D-258, D-260, D-265.

---

## D-265 — Uc defter tutan sistem hicbirine guvenemez; ve gecmis sayiyi sart kosan test yalani korur (2026-09-28)

**Bulgu.** Gocler icin **uc** ayri defter vardi:

| Yol | Defteri | Canli DB'deki hali |
|---|---|---|
| `migrate.py` | `schema_versions.json` (dosya) | 15'te donmus |
| `scripts/db_migrate.py` | `_schema_version` (tablo) | **Tablo hic olusmamis** |
| `scripts/goc_defteri.py` | `schema_migrations` (tablo) | **34/34 — gercek defter** |

Iki cikarim:

1. `_schema_version` tablosunun DB'de **hic olusmamis** olmasi, `db_migrate.py`'nin
   uretimde **hic kosmadigini** kanitlar. Kossaydi defteri 0'dan sayip 34 gocu
   yeniden uygulamaya kalkardi.
2. `schema_versions.json` 15'te kalmis. D-264'te bu dosya yuzunden defter 23→15
   geri alinmisti. Ayni tuzagin ikinci agzi.

**Karar.** Goc uygulamanin **tek kapisi** `scripts/goc_defteri.py`; defter
**yalnizca** `schema_migrations` tablosudur. Diger iki yolun yazma fonksiyonlari
`SystemExit` ile kapatildi ve dogru kapiyi soyluyor. `schema_versions.json`
tarihi kayit; karar mercii degil.

**Ikinci bulgu — bekci yalani koruyordu.** `test_migrate_py_target_15` adli test
*"migrate.py default target 15 olmali"* diye **sart kosuyordu**. Diskte 34 goc
varken 15'te durmayi zorunlu kilan bir test, D-264'teki geri alma hatasini
**hata degil gereksinim** sayiyordu. Test, gecmisteki bir sayiyi degil bugunun
sozlesmesini korumali: yeni hali uc yolun tek kapiya isaret ettigini ve kapali
fonksiyonlarin `SystemExit` tasidigini dogruluyor.

**Kural.** Bir sayiyi sabitleyen test, o sayinin **neden** o oldugunu da
yazmalidir. Gerekcesini tasimayan sabit, ilk degisimde yalana doner.
Bir kaynagin **yoklugu** da olcumdur: olusmamis defter tablosu, kosmamis kod demektir.

**Kanit.** `goc_defteri.py` → 34 disk / 34 defter; uc yolun ikisi exit 1 +
dogru kapi mesaji; `tests/test_data_log.py` 17/17 gecti.

**Kapanan borc.** BORC-GOC-IKI-DEFTER-01 (adi iki diyordu, gercek uc cikti).

---

## D-264 — Tasfiye bir hal'dir; ve tanimadigi argumani yutan koc defteri geri alir (2026-09-28)

**Tur:** uygulama + kritik hata. `BORC-TASFIYE-IKIZ-01` **kapandi**, ama
kapatma isi sirasinda gocleri kosturan yolda **veri kaybettiren bir hata**
buldum. Once o.

### 1. KRITIK: `migrate.py up` defteri 23 → 15'e geri aldi

Goc 0034'u uygulamak icin `python -m ...migrate up` yazdim. Cikti:

```
Migrations complete. Version: 15   (exit code 0)
```

Uc yalan bir arada:
- `up` **taninmayan bir argumandi**; `argv` kontrolu `--dry-run`,
  `--version`, `--apply` ariyordu, hicbiri yoktu, kod **sessizce**
  varsayilan dala dustu.
- O dal SQL **calistirmadi**, ama surum numarasini yeniden hesaplayip
  `schema_versions.json`'u **23 → 15** olarak yazdi. 8 goc kaydi silindi.
- `exit 0` dondu. Basarili gorundu.

`git checkout` ile defter geri alindi (hasar dosyada kaldi, DB'ye
dokunmamisti — bu sans, tasarim degil).

**Kural: bir CLI tanimadigi argumani gormezden gelemez. Gormezden gelmek
"yanlis yazdin" hatasini "sessizce baska bir is yaptim"a cevirir.**
[`migrate.py`](src/company_master/schema/migrations/migrate.py) artik
bilinmeyen argumanda `SystemExit` atar ve dogru kapiyi soyler.

### 2. IKINCI DERS: iki defter vardi, hangisinin gercek oldugunu bilmiyordum

| defter | yer | 0034 oncesi |
|---|---|---|
| JSON | `schema_versions.json` | 23'te donmus |
| DB tablosu | `schema_migrations` | 31 kayit |

Gocleri gercekten uygulayan ve DB defterine yazan yol
[`scripts/goc_defteri.py --uygula`](scripts/goc_defteri.py). `migrate.py`
ikinci bir dunyadir ve JSON'a yazar. Ayni sorunun (D-263/2) **goc
katmanindaki tekrari**: bir gercek iki yerde saklaniyor, senkron eden yok.

Ek bulgu: `--esitle` kostugunda **0033 defterde yoktu** — dun uygulanmis
ama kaydedilmemis. Kendi goc kaydimi dusurmusum.

### 3. Tasfiye: ayri firma degil, halin kendisi

Olcum: 23 tasfiye onekli kayit, 22'sinin oneksiz ikizi var. Iki secenek:

| secenek | sonuc |
|---|---|
| A: onekli kaydi sil, ikize birlestir | firma sayisi 9412 → 9390, tasfiye bilgisi **kaybolur** |
| B: her ikisini `status='liquidation'` isaretle | bilgi korunur, satir kaybi yok |

**B secildi.** Gerekce: tasfiye halindeki firmanin **oneksiz kaydi da
tasfiyededir** — ikisi ayni tuzel kisilik. Silmek "bu firma tasfiyede"
bilgisini yok eder; isaretlemek panelde filtrelenebilir hale getirir.

Goc 0034 (`--uygula` ile kosturuldu, defterde kayitli):
- `status` CHECK kisitina `'liquidation'` eklendi
- onek deseni + oneksiz ikizler `liquidation` olarak isaretlendi
- geri alma dosyasi yazildi (`down/0034_tasfiye_durumu.down.sql`)

### 4. Canli DB olcumu (kanit, beyan degil)

| olcum | deger |
|---|---|
| `status='liquidation'` | **45** (23 onekli + 22 ikiz) |
| onekli ama `liquidation` DEGIL | **0** |
| CHECK kisiti `'liquidation'` kabul ediyor | evet |
| firma sayisi | 9412 (degismedi) |

`unknown` 693, `active` 8674. **Tasfiye artik panelde susturulabilir bir
alan; onceden gorunmez bir yinelenmeydi.**

### 5. Kalan borc

- `BORC-GOC-IKI-DEFTER-01` **yeni**: `migrate.py` (JSON) ve
  `goc_defteri.py` (DB tablosu) iki ayri defter tutuyor. Tek kapi
  olmali; `migrate.py` ya DB defterine yazmali ya kaldirilmali.

**Referans:** D-241, D-251, D-261, D-263.

---

## D-267 — Deger yanlis kolonda degildi, hic kolonda degildi; ve uydurulmus anahtar sessiz kalir (2026-09-28)

### 1. BORCUN ADI YINE YANLISTI (D-265/D-266 deseni ucuncu kez)

`SICIL-TASIMA-01` devir notunda soyle yaziyordu: *"620 firmanin sicil
degeri YANLIS ALANDA; `trade_registry_number`'a tasinmali."* Iddia
"tasima" kelimesi uzerine kuruluydu. Olcum:

| olcum | deger |
|---|---|
| `companies.trade_registry_number` dolu | **0** / 9412 |
| `companies.trade_registry_office` dolu | **0** / 9412 |
| `tax_number` icinde 3-6 haneli sicil deseni | **0** satir |
| `tax_number` dolu (herhangi bir deger) | 5 |
| `source_records.raw_payload ->> 'ticaretSicilNo'` | **620** kayit |

Deger yanlis kolonda **degildi** — hic kolonda **degildi**. Tek
bulundugu yer ham arsiv. Yani is kolon→kolon *tasima* degil,
arsiv→sema **cikarma**'ydi. Tasima varsayimiyla yazilacak goc kaynak
kolonu arardi, bulamazdi.

**Kural (D-265/1'in guclendirilmesi): devir notundaki FIIL de olculur.
"tasi", "birlestir", "duzelt" fiilleri bir topoloji iddiasidir; once o
topoloji dogrulanir, sonra kod yazilir.**

### 2. Uydurulmus payload anahtari sessizce None doner

Kok nedeni ararken `etl/normalize.py`'nin okudugu **butun** anahtarlari
saydim (9401 canli kayit, `jsonb_object_keys`):

| anahtar | kayit sayisi |
|---|---|
| `sektor` | 10532 |
| `adres` / `kaynak` | 9401 |
| `vergi_no` | 8809 |
| `nace_code` | 8313 |
| `naceKod` / `naceDetay` / `meslekGrubu` / `ticaretSicilNo` | 620 |
| **`vergi_dairesi`** | **0** |
| **`mersis_no`** | **0** |
| **`ticaret_sicil_no`** | **0** |
| **`sicil_dairesi`** | **0** |

Dort anahtar payload'da **hic yok**. `_identity_completeness()` bunlari
okuyordu; `.get()` her zaman `None` donduruyordu. Ne hata, ne uyari, ne
test kirmizisi. Sicil icin gercek anahtar `ticaretSicilNo` (camelCase);
kodda `ticaret_sicil_no` (snake_case) yaziyordu. **Hic olculmemis,
uydurulmus anahtarlar.**

Daha kotusu: `_map_row()`'un donduren sozlugunde ve `run_normalize()`
INSERT listesinde `trade_registry_number` **hic yoktu**. Yani anahtar
dogru olsa bile ETL bu kolonu yazamazdi. Puana giriyordu, semaya
girmiyordu.

**Kural: `dict.get()` bir sozlesme degildir; yoklugu basari gibi
gorunur. Payload anahtari kodda gecmeden once canli veride SAYILIR.
Sifir ciktiysa o alan okunmaz — yoklugu da bir olcumdur (D-265).**

### 3. SQL'e cevrilen dogrulama, Python kapisiyla karsilastirilir

Goc `sicil_dogrula()`'yi (D-247 tek kapi) SQL'de yeniden yaziyordu:
`split_part` + `btrim` + `upper` + `~ '^[0-9]{3,6}$'`. Risk Turkce
`upper()` yerel davranisi. Dosyayi yazmadan once iki uygulamayi 619
canli satirda karsilastirdim:

```
SQL ifadesi ile sicil_dogrula() FARKI = 0 satir
gecerli=619  gecersiz=0  dairesi_olan=25
```

**Kural: bir dogrulama kapisi SQL'e kopyalaniyorsa, goc yazilmadan
ONCE iki uygulama canli veride karsilastirilir. Fark 0 degilse kopya
degil, ikinci bir gercektir (D-263 deseni).**

### 4. Goc 0035 ve iki kapsama orani (D-260)

[`0035_sicil_tasima.sql`](src/company_master/schema/migrations/0035_sicil_tasima.sql)
`--uygula` ile kosturuldu, defterde kayitli (35 disk / 35 defter):

| olcum | deger |
|---|---|
| kayit kapsamasi | **620 / 9401** source_records |
| firma kapsamasi | **619 / 9412** companies (1 kayit firmaya bagli degil) |
| ayni firmaya iki FARKLI sicil degeri | 0 (cakisma yok) |
| goc sonrasi `trade_registry_number` dolu | **619** |
| goc sonrasi `trade_registry_office` dolu | **25** |
| firma sayisi | 9412 (satir kaybi yok) |

Ikiz kolon **olusmadi**: kaynak bir kolon degil, `raw_payload` — ve
D-246/4 onu kalici ham arsiv olarak tanimlar. Arsivden okumak ikizlik
degildir; dusurulecek kolon yok. Geri alma dosyasi durust: goc oncesi
olculen deger tam olarak 0/9412 oldugu icin NULL'a cekmek
"bilmiyoruz" degil, "onceki durum buydu" demektir.

### 5. Tavan 6.50 → 7.50 — ama sebebi "620 firma puan aldi" DEGIL

`tavan_raporu()` (D-258 tek tureten kapi) goc sonrasi:

```
GOC SONRASI TAVAN: 7.5 / 10.0
kilitli: {'tax_office': 0.5, 'mersis_number': 1.0, 'nace_code': 1.0}
dolu_sayac['trade_registry_number'] = 25
recalc_quality_scores() yazilan satir: 9412
```

**Durustluk notu:** D-250 puan icin sicil no **VE** dairesini birlikte
ister. Daire tasiyan firma 25/9412 = binde 2.7. Yani 619 firma *deger*
kazandi, sadece 25'i *puan* kazandi. Tavan yukseldi cunku D-258'de
"kilitli" tanimi **sifir firma puan aliyor** demektir; 25 > 0 oldugu an
1.0 agirligin tamami acilir. Ortalama puan kayda deger artmadi.
**Acilan sey ortalama degil, TAVAN'dir.**

Yan bulgu (yalan degil, dogru calisan kural): `companies.nace_code`
8289/9412 dolu ama `dolu_sayac['nace_code'] = 0`. Sebep D-245 —
tahmin edilmis NACE kanit degil, `nace_source` kanit listesinde
olmali. Celiski gibi gorundu, olculdu, **dogru** cikti; dokunulmadi.

### 6. Yarim goc olmasin: gecmis + gelecek birlikte onarildi

Goc gecmisi onarir. `normalize.py` duzeltilmezse bir sonraki ETL
kosusu ayni bosluğu yeniden uretir — D-258/4'un tanimladigi **yarim
goc**. Bu yuzden ayni turda:

- `_identity_completeness()`: 4 olu anahtar cikarildi, sicil
  `sicil_dogrula()` kapisindan geciriliyor
- `_map_row()`: `trade_registry_number` + `trade_registry_office`
  eklendi
- `run_normalize()` INSERT: iki kolon + iki bind parametresi eklendi

**Kural: kolonu dolduran goc ile o kolonu yazan ETL yolu AYNI turda
duzeltilir. Sadece biri yapilirsa is bitmis gorunur, bitmemistir.**

### 7. Iz birakmayan goc, iz birakmadigini KENDI yazar

`goc_defteri.py` yalnizca DDL izi (tablo/kolon/index/kisit) ariyordu.
0032 gibi **saf veri** goclerinin semada izi yoktur, olmasi da
gerekmez — ama arac onlari `IZSIZ` (= dogrulayamadim) diye
raporluyordu. **Bugunku yanlis alarm, yarinki gercek alarmi gizler.**

En kucuk cozum: dosya kendi izsizligini beyan eder, arac sessizce
varsaymaz.

```sql
-- veri-gocu: 761 kimliksiz satir silindi, 243 referans + 92 bag tasindi
```

Yeni durum `VERI` eklendi. `IZSIZ` artik yalnizca *sebebi yazilmamis*
gocler icin kalir ve mandal onu **kirmizi** yapar:

```python
izsiz = sorted(d for d, (durum, _) in sonuc.items() if durum == "IZSIZ")
assert not izsiz, f"Sebebi yazilmamis izsiz goc (veri-gocu: ekle): {izsiz}"
```

Kanit: 0032 onceden `IZSIZ`, simdi `VERI  defterde`.

### 8. `return` eden test hicbir sey garanti etmez

`tests/test_goc_defteri.py`'de iki test sayi **donduruyordu**, `assert`
etmiyordu. pytest bunu uyariyla gecer — yesil renk yalani ortuyordu
(D-265/2 deseni). Ikisi de `assert`'e cevrildi ve gercekten neyi
korudugu yazildi. Pinlenen her sayinin **nicin** o sayi oldugu test
docstring'inde duruyor (619 = firmaya bagli kayit sayisi, 25 = D-250
puan alan alt kume). Sayi degisirse once olcum yenilenir, test degil.

### 9. Kapanan borclar

- `SICIL-TASIMA-01` **kapandi** — ama adi yanlisti; is arsiv→sema
  cikarmaydi. Goc 0035 + `normalize.py` kok neden onarimi.
- `GOC-DEFTER-VERI-01` **kapandi** — `VERI` durumu + `veri-gocu:`
  beyani + yazisiz `IZSIZ`'i kiran mandal.
- `TEST-DONUS-01` **kapandi** — iki test `assert`'e cevrildi.

### 10. Kalan borc

- `BORC-SICIL-DAIRE-01` **yeni**: 619 firmanin sicil numarasi var,
  sadece 25'inin dairesi var. D-250 ikisini birlikte istedigi icin 594
  firma puan alamiyor. Daire kaynagi aranmali (MERSIS kapali, D-257).

**Referans:** D-241, D-245, D-246, D-247, D-250, D-251, D-254, D-258,
D-260, D-263, D-265, D-266.

## D-268 — NACE kumesi: olculdu, ikiye bolundu, biri dustu

**Tur:** kaynak zinciri onarim hatti, NACE kumesi. Goc `0036_nace_olu_kolon.sql`.

### 1. Devir notunun fiili yine yanlisti (D-267/1 deseni dorduncu kez)

Devir notu dort borc sayiyordu ve `NACE-OLU-KOLON-01`'i **tek fiil** olarak
tarif ediyordu: "iki olu kolonu dusur". Olculdugunde iki kolonun gerekcesi
AYNI DEGIL cikti. Borc tek degil, **ikiye bolundu**:

| Kolon | Siniflandirma | Olculen gerekce |
|---|---|---|
| `nace_codes.is_manufacturing` | **GERCEK OLU** | 3319 / 3319 satir `false`. Tek bir `true` yok (D-249: tek degerli kolon = sifir bilgi). Yazan `nace_sozluk_yukle.py` her zaman SABIT `False` yaziyordu. Uretimde okuyan **yok**. |
| `companies.nace_name` | **YANLIS TARIF** — "olu" degildi | 52 / 9412 dolu, 8 farkli deger. Uretim okuyani VARDI: `web_app.py` `/api/match` SELECT listesi. "Cagirani yok, dusur" gerekcesi bu kolon icin yanlisti. |

### 2. `nace_name` yine de dustu — ama bambaska bir gerekceyle

Dolu bir kolonu dusurmek beyanla degil olcumle savunulur (D-260):

- **Puana girmiyor:** `_match_puan()` yalnizca `nace_code`, `osb_id`,
  `is_ankara`, `identity_completeness`, website/email/telefon okuyor.
  `nace_name` hicbir bilesende gecmiyor.
- **Cagiran fiilen deger gormuyor:** SELECT sarti `nace_code IS NOT NULL AND
  is_ankara` ile 8289 satir donuyor; bunlarin `nace_name` DOLU olani **2**.
  52 dolu satirin 50'si bu cagirana hic ugramiyor.
- **Tuketici yok:** hicbir `.html` / `.js` sablonu ve hicbir test bu alana
  dokunmuyor (0 sonuc). Yanit sozlugune girip kimsenin okumadigi alan.
- **Kaynak kaybi yok (D-246/4):** 52 degerin 47'si ham arsivde birebir
  duruyor (`source_records.raw_payload ->> 'sektor'`). Kalan 5'te payload
  anahtari yok; o 5 deger de NACE bilgisi degil, OSB sektor etiketi.
- **Degerin kendisi zaten NACE adi degildi:** 'Metalurji ve Makina Sanayi'
  (22), 'Diger' (17), 'KIMYA-LABARATUVAR' (4), 'GIDA' (4), 'Medikal - Ilac'
  (2), 'Endustriyel Market' (1), 'Elektrikli Cihaz Sanayi' (1), 'Savunma' (1).
  `ingest_osb_scrapers.py` OSB sitesinin `sektor` alanini dogrudan "NACE adi"
  kolonuna akitiyordu. Yani kolonun **adi** veriyi yanlis tanitiyordu.

### 3. Diger uc borcun siniflandirmasi

- `NACE-ACILIM-01` — **GERCEK, acik kalir.** 6387/8289 acilimi var; 1902
  acilimsiz beyani dogrulandi. Ancak `acilim_getir` kodda hic yok; D-266
  geregi once cagiran, sonra duzeltme.
- `NACE-SOZLUK-DIL-01` — **GERCEK, acik kalir.** 3319 satir; 572 TR harfli
  basligin 572'si yarim asciilesmis; mojibake 0; level-2 52/88 ve level-4
  483/957 bassiz; level-6 2252 tam. Cozum TUIK listesi indirmeye bagli.
- `NACE-COKLU-01` — **VARSAYIM, iptal adayi.** `company_industries` 21 satir
  / 21 firma, hepsi `is_primary`. Ayni firmada birden fazla farkli `nace_code`
  tasiyan firma sayisi **0**. Coklu NACE ihtiyaci olculmus degil, varsayilmis.

### 4. Kural (D-268)

**Bir borc tek fiil gibi yazilmis olabilir; olcum onu ikiye bolebilir.
Kolonlari "ayni fiile bagli" diye birlikte dusurmek, gerekcelerinden en
zayifini ikisine birden uygulamaktir. Her kolon KENDI gerekcesiyle duser.**

Ikincil kural: **dusurulen kolonun dusme gerekcesi "cagirani yok" DEGILSE,
gerekce goc basligina yazilir.** `nace_name`'in cagirani vardi; onu dusuren
sey cagiranin fiilen deger gormemesiydi (2/8289). Bu ayrim yazilmazsa bir
sonraki tur "cagirani vardi, nicin dustu?" diye geri aciyor.

### 5. Kanit (calistirilmis komut ciktisi)

```
goc_defteri.py --uygula 0036_nace_olu_kolon.sql
  -> UYGULANDI + DEFTERE YAZILDI: 0036_nace_olu_kolon.sql
     Diskte 36 goc, defterde 36 kayit.

information_schema kontrolu (is_manufacturing + nace_name):
  -> kalan kolon: []

pytest tests/test_dusurulen_kolon.py
  -> 1. kosu: FAILED  scripts/fix_raw_columns_v2.py:124, scripts/_olcum_nace.py:75
     (mandal ilk kosusunda iki kacak yakaladi; findstr taramasi ikisini de
      kacirmisti -- metin taramasi mandal yerine gecmez)
  -> duzeltme sonrasi: 1 passed
```

### 6. ETL yolu ayni turda kesildi (D-267/6)

Goc gecmisi temizler; yaziyi birakmayan ETL kolonu bir sonraki kosuda geri
dogurur. Ayni commit'te kesilenler:

- `web_app.py` — `/api/match` SELECT'inden `nace_name` cikti (tek okuyan)
- `scripts/ingest_osb_scrapers.py` — UPDATE + INSERT yazisi silindi (tek yazan)
- `src/company_master/etl/nace_sozluk_yukle.py` — 10 sozluk literali +
  INSERT/VALUES/ON CONFLICT + parametre (`is_manufacturing` tek yazani)
- `scripts/p45_validate_and_dedup.py` — SELECT + `merge_fields`
- `scripts/fix_raw_columns_v2.py` — `SET` yazisi, `WHERE` sarti, doluluk raporu
- `scripts/nace_eksik_doldur.py` — olu `kod_isim` sozlugu + bayat import

**Mandal:** `tests/test_dusurulen_kolon.py` — `src/`, `scripts/`, `templates/`,
`web_dashboard/`, `web_app.py` icinde `*.py/*.js/*.html/*.sql` tarar. Goc
dizini muaftir (arsiv). Kolon DB'den dustugu icin geri sizma calisma aninda
`UndefinedColumn` demektir; mandal o patlamayi commit anina ceker.

**Dusen dosyalar (D-241, cagirani olmayan tek seferlik araclar):**
`debug_xlsx.py`, `test_upsert.py` (kok dizin ad-hoc hata ayiklama betikleri,
hicbir yerden cagrilmiyor), `scripts/_olcum_nace.py`, `scripts/_olcum_nace2.py`.

### 7. Kapanan / acik kalan borc

- `NACE-OLU-KOLON-01` **kapandi** — iki kolon da semadan dustu, yazici/okuyucu
  yollari kesildi, mandal kondu.
- `NACE-ACILIM-01` **acik** — kaynak var, cagiran yok.
- `NACE-SOZLUK-DIL-01` **acik** — TUIK listesi indirmeye bagli.
- `NACE-COKLU-01` **iptal adayi** — ihtiyac olculmedi, varsayildi. Gercek
  coklu-NACE talebi olcene kadar acilmaz.
- `BORC-NACE-DOGRULAMA-01` **acik kalir** (D-252/D-245): `nace_validity`'de
  `verified` **sifir** (medium 5732 / unknown 2942 / fallback 738);
  `companies.nace_confidence` kolonu yok. NACE'nin %100'u hala tahmin.
  **Doluluk skoru acmaz — dogrulama acar.** Dogrulama kaynagi olmadan sistem
  kendi kendine "dogrulandi" isaretlemez.

### 8. Yan bulgu (bu turun isi degil, kayit icin)

`information_schema` `schema_migrations` icin `version` kolonunu **iki kez**
donduruyor: tablo birden fazla semada var. Defter tek kapi olmali (D-265);
iki semada ayni adla duran defter ileride "hangisini okudum?" sorusunu
doguracaktir. Olculmedi, borc acilmadi — bir sonraki goc turunda bakilmali.

### 9. Yeni borc: BORC-TEST-SIRA-01 (bu turda olculdu)

Tam takim rastgele sirada (pytest-randomly) **1 failed, 4444 passed**; sabit
sirada (-p no:randomly) **4445 passed, 13 skipped, 172.52s**. Ayni kod, iki
farkli sonuc: kirilma kodun degil test SIRASININ fonksiyonu — bir test
kendinden oncekinin biraktigi global duruma baglanmis (D-226 ihlali). Kirilan
testin adi izole edilemedi, ikinci kosuda ayni tohum cikmadi.
**Acik borc: BORC-TEST-SIRA-01.** Cozulene kadar "takim yesil" beyani hangi
sirayla kosuldugu bilgisiyle birlikte verilir; sirasiz yesil kanit degildir
(D-260).

**Referans:** D-241, D-245, D-246, D-249, D-250, D-252, D-258, D-259, D-260,
D-263, D-265, D-266, D-267.

## D-270 — Kırık test iddiası canlı koşudan gelir; `lastfailed` kanıt değildir

> D-227 onarımı (2026-09-28): bu karar `D-268` numarasıyla yazılmıştı, o numara
> zaten "NACE kumesi: olculdu, ikiye bolundu, biri dustu" kararına aitti.
> `D-269` da başka ajan tarafından alınmıştı. Numara boşa çekildi: **D-270**.

**Bağlam:** FAZ-0 kök hijyeni sırasında `.pytest_cache/v/cache/lastfailed`
içinde **330 kayıt** bulundu. Aynı dosyanın fiilen koşumu
`tests/test_brief_sablon_denetim.py` → **18 passed** verdi. Kayıtlar bayattı:
pytest `lastfailed`'ı yalnız **son koşulan** testler için günceller, silmez.

**Risk:** Bir ajan `lastfailed`'a bakıp "330 test kırık" sanar ve **1-2 günlük
gereksiz kurtarma işi** açar. Bu tam olarak D-261'in (iz doğrulanmadan kanıt
sayılmaz) dosya eşdeğeridir: dosya bayat, iddia gerçek değil.

**Karar:**

1. **Fiilen kırık test = son koşunun `failed`/`error` çıktısı.** Başka hiçbir
   kaynak kırık test iddiası üretmez.
2. **`.pytest_cache/` kanıt kaynağı değildir.** Raporlanmaz, karara dayanak
   yapılmaz. Ajan "kaç test kırık" derken **kendi koşusunu çalıştırır.**
3. **Bayat kayıt temizliği:** Şüpheli `lastfailed` görülürse dosya silinir;
   silmek kanıt değildir ama yanlış kanıttan kurtulur.
4. **"Takım yeşil" beyanı sıra + komut ister** (D-260 zaten): tek satır
   "pytest 4300 passed" kanıt değildir, çıktı satırı kanıttır.

**Mandal:** `tests/test_kok_politikasi.py` bu kararın **kök** yarısını kapatır
(`test_vault_kokte_tek_kullanimlik_yok`, D-221). `lastfailed` yarısı dosya
temizliğiyle karşılanır — otomatik kapı yok, **kural disiplini gerekir.**

**Referans:** D-219, D-220, D-221, D-241, D-260, D-261, D-267.

## D-269 — Skill tek havuzdur; ajan dizini junction'dır, kopya değil

**Bağlam:** Ölçüm (2026-09-29): SKILL.md havuzu **4 klasöre** dağılmıştı
(`.agents/skills` 26 + `.kilo/skills` 6 + `.claude/skills` 5 + `.continue/skills` 5)
ve ajan dizinlerindeki 5 kopya **junction değil, ayrı dosya** idi.
`.continue/skills` içindeki 5 klasör ise **tamamen boştu** — ajan skill var
sanıyordu. Sonuç: "hangi skill'i kullanayım?" sorusu belirsiz; kopya sessizce
eskidi (D-266'nın dosya eşdeğeri: bayat ikiz yalan söyler).

Ayrıca ikinci bir "skill" dünyası vardı: `skills/` altında `@registry.register`
ile kayıtlı **51 Python yeteneği** (ajan *çalıştırır*), `.agents/skills/` altında
**SKILL.md belgeleri** (ajan *okur*). Aynı ad iki mekanizma gösteriyordu.

**Karar — 1. Tek kanonik SKILL.md havuzu (ajan OKUR):**

1. **Kanonik yol: `.agents/skills/`.** Bir SKILL.md'nin tek yaşam yeri budur.
2. **Ajan dizini junction'dır, kopya değil.** `.claude/skills/`, `.continue/skills/`,
   `.roo/skills/` yalnız `.agents/skills` dizinine **işaret eder**.
   - *Neden:* Kopya sessizce eskir; iki ajan farklı SKILL.md okur.
   - *Nasıl:* `npx skills add` zaten junction kurar (Windows'ta `Junction`).
3. **Boş klasör yasak.** Junction olmayan boş skill klasörü, ajana
   "skill var" izlenimi verir. Bu bir **hatadır** (2026-09-29'da 5 tane vardı).
4. **`.kilo/skills` ve `data/skills/` yasak.** Kilo Code proje dizini
   `.agents/skills` olarak tanımlı; ikinci havuz otomatik çarpışma üretir.
5. **Ajan "hangi skill?" diye sorarsa:** yanıt `skills/SKILLS_INDEX.md` + `.agents/skills/`.
   Arama yapmak, tahmin etmek yasak (D-216 hayalet görev mantığı).

**Karar — 2. Python yetenekleri ayrı çatı altında (ajan ÇALIŞTIRIR):**

6. **`skills/` = Python yetenek havuzu.** Alt paketler ve tek iş kuralı:
   | Konum | İçerik |
   |---|---|
   | `skills/tools/` | iş mantığı (osint, orchestrator, admin_panel, devops, streamlit) |
   | `skills/services/` | **yalnız** dış servis çağrısı (9Router) |
   | `skills/utils/` | giriş/doğrulama yardımcıları |
   | `skills/prompts/` | sistem prompt metinleri (`.py` **değil**) |
   | `skills/base.py` | `SkillRegistry` — **tek kayıt kapısı** |
7. **Bir iş mantığı, bir servis çağrısını çağırmaz.** Çağrı `services/`'e gider.
8. **`skills/common/` yasak** (D-220 Kural 1: tür başına tek yol). 2026-09-29'da
   `tools/` + `services/` altına toplandı.
9. **Yeni yetenek = `@registry.register` + `__init__.py` dışa aktarımı.**
   `__init__.py` sınıf bekliyorsa modül o sınıfı tanımlamak zorundadır; aksi
   halde **ImportError** (2026-09-29'da `skills.devops` ve `skills.streamlit`
   tam olarak bu yüzden çalışmıyordu).
10. **Kayıt: `skills/SKILLS_INDEX.md`.** İki dünyayı **birlikte** listeler;
    tek dizin olmazsa ajan hangisini arayacağını bilemez.

**Karar — 3. Geliştirme ve yükleme disiplini:**

11. **Yeni bağımlılık yasak.** Dış servis çağrısı ek SDK gerektiriyorsa
    **önce mevcut gateway'e bak** — 9Router Claude dahil tüm modelleri
    karşılıyor (`ninerouter_chat_anthropic`).
12. **Model adı koda gömülmez.** `NINEROUTER_MODEL` ortam değişkeninden okunur.
    API anahtarı `.env`'te kalır (D-241: kök izin listesi değişmez).
13. **İçerik değişmeden taşı.** Taşımadan önce: (a) yedek al,
    (b) **içeriği doğrula** — ad deseni tek kullanımlık *görünür*, içerik
    kalıcı olabilir (2026-09-29'da `run_tests.py` 613 satır, `test_reports/`
    üretiyordu). (c) hedefte aynı ad zaten varsa **üstüne yazma, bildir**.
14. **Ajan dosya kilidi alır.** Pano boş olmak dosyanın boşta olduğunu
    **kanıtlamaz** (D-268). Taşıma/silme öncesi `gorev_kutusu.py bak` + son
    5 dakikadaki dosya hareketi sorgulanır.

**Mandal:** `tests/test_skill_havuzu.py` (13 test) — kanonik havuz dışı skill
yok, boş klasör yok, `.kilo/skills` ve `skills/common/` yok, alt paketler
import edilebilir, registry ≥30 kayıt, `SKILLS_INDEX.md` iki dünyayı da anlatıyor.
**Kanıt üretti:** ilk koşuda `.roo/skills/sistemsel`'i yakaladı (kanonik
havuzda yoktu) → taşındı → yeşil.

**Doğrulama:** `python -m pytest tests/test_skill_havuzu.py -q` → 13 passed ·
`python -m pytest tests/ -q` → 4465 passed, 13 skipped, 0 failed

**Referans:** D-216, D-219, D-220, D-221, D-241, D-266, D-268 ·
ALTYAPI-SKILL-YAPISI-01 (Faz A–F).

---

## D-271 — Borç adı fiil taşımaz; ve borç listesinin kendisi bir beyandır (2026-09-28)

**Tür:** kural + düzeltme. Üç madde ölçüldü; **ikisinin adı yanlıştı**, biri
defterde **hiç yoktu**.

### 1. Devir notunun adlandırdığı iki borç defterde YOK

Devir notu iki borç kimliği verdi. Ölçüm:

```
python -c "import pathlib;t=pathlib.Path('AGENTS.md').read_text(encoding='utf-8');
[print(k,'->',t.count(k)) for k in ('BORC-DEFTER-IKI-SEMA-01','BORC-ADLANDIRMA-01')]"
BORC-DEFTER-IKI-SEMA-01 -> 0
BORC-ADLANDIRMA-01 -> 0
```

İkisi de devir notunda **doğdu**, defterde hiç yaşamadı. D-260'ın kardeşi:
*devir notu da bir beyandır.* Bir kimliğe atıfta bulunmak onu var etmez.
Kimlik yalnız AGENTS.md'de doğar — D-227'nin borç karşılığı.

### 2. İki şema uyarısı: borç İPTAL, kusur GERÇEK

`information_schema` `schema_migrations` için `version` kolonunu iki kez
döndürüyordu. Canlı ölçüm:

```sql
SELECT table_schema FROM information_schema.tables
WHERE table_name='schema_migrations';
-> auth, public, realtime
SHOW search_path;  -> "$user", public, extensions
```

Üç şemada var, ikisi değil. `auth`/`realtime` **Supabase'in kendi
defterleridir**, bizim değil → "iki defter tutuyoruz" borcu **iptal**.

Ama ölçüm başka bir kusur buldu: `goc_defteri.py` defteri hiçbir ifadede
nitelendirmiyordu. Doğru defter bugün yalnızca `search_path` öyle olduğu
için açılıyor. Sunucu ayarı değişse araç **sessizce başka bir defteri**
düzenler ve kimse fark etmez. Kesildi: dört SQL ifadesinin hepsi artık
`public.schema_migrations` yazıyor.

### 3. Kapatılan göç yolu üç değil DÖRT'tü

D-265 üç yol saydı. `src/company_master/db/migrate.py` listede yoktu:
çağıranı yoktu (D-266) ama `python -m` ile koşabiliyordu ve D-264'te
defteri 23 → 15'e geri almıştı. **Düşürüldü** (gövde `RuntimeError`).

Yolu tek tek saymak dördüncüsünü bulmamı sağlamadı; onu ancak
`INSERT INTO schema_migrations` **arayarak** buldum. Bu yüzden yeni mandal
listeyi ezberlemiyor, aramayı kendisi yapıyor:
`tests/test_data_log.py::test_defter_yazan_baska_yol_yok`.

### 4. Test sırası: kirleten bir değil İKİ taneydi

Devir notu "bir test global durum bırakıyor" dedi. İki bulundu:

1. `benchmark_http.kos()` ölçüm için `web_app.engine`i sahte motorla
   değiştirip **geri koymuyordu**. Aynı süreçte sonra koşan her test sahte
   motoru görüyordu.
2. Bare modda `st.form("yeni_karar")` form kimliğini `main_dg`'ye
   **kaynak yapıyor**. `DeltaGenerator._block` `_cursor is None` iken
   `dg`'nin kendisini döndürür; `FormMixin.form` da `block_dg._form_data`'ya
   yazar — yani `main_dg`'ye. `with` çıkışı bunu temizlemez.

Mandallar: `tests/test_benchmark.py::TestKirletmeMandali` ve
`tests/conftest.py::_streamlit_form_durumu_temiz`. İkisi de **kırılarak**
doğrulandı.

**Dürüst not:** bir ters-sıra düşüşü yakalanamadı. Koşu 1: `1 failed,
4464 passed`. Koşu 2 (aynı komut, `-rf` ile): `4465 passed`. Kimliği
kaydedilemedi. `pytest-randomly` kurulu değil; tohum sabitlenemedi.
Bu satır "temiz" beyanı değildir — **yakalanamadı** beyanıdır.

### 5. Kural (D-271) — borç başlığı fiil taşımaz

**Ölçüm (2026-09-28, mandal çıktısı):** defterde **27** borç/iş kimliği var.
**8'i fiil** taşıyor (`DUSUR`, `DOGRULAMA`, `DEDUP`, `TEMIZ`, `BAG`,
`SOZLUK`, `BETIK`), **4'ü sayı** taşıyor (`IKI`, `IKIZ`). Fiil ya da sayı
taşıyan kimliklerden **üçü** sonradan "adı yanlıştı" diye kapandı:

| Kimlik | Ad ne dedi | Ölçüm ne buldu |
|--------|------------|----------------|
| `BORC-PERF-BANT-01` | "bandı düzelt" | yüzeyin çağıranı yoktu → kapatıldı (D-266) |
| `BORC-GOC-IKI-DEFTER-01` | "iki defter" | üç defter (D-265), sonra dört yol |
| `BORC-AD-VARYANT-01` | "normalize sözlüğü" | teşhis yanlıştı → iptal (D-263) |

**Kural:**

1. Borç başlığında **fiil yasak**. Yalnız **ölçülen sapma** yazılır.
   `nace_name doldur` **değil** → `nace_name 52/8289 dolu, değerler isim değil`.
2. Başlıkta **sayı sayma** yasak (`IKI`, `UC`, `IKIZ`). Sayı ölçülür,
   adlandırılmaz — ad sayıyı dondurur, ölçüm değiştirir.
3. **Fiil, ölçen tura aittir.** "Ne yapılacak" kararı ölçümden sonra
   verilir; borç kaydı yalnız "ne bozuk" der.
4. Yeni kimlik `BORC-<ALAN>-<NN>` biçimindedir; alan **isim**dir.
5. Mevcut 8 fiilli kimlik **yeniden adlandırılmaz** — git geçmişi ve 30+
   karar girdisi onlara atıf yapıyor; yeniden adlandırma kazancı yok,
   kırılma kesin (D-221/1 mantığı). **Mandal: sayı yalnız küçülür.**

**Mandal ilk koşuşta bu girdinin kendisini yakaladı.** Tavanı 3 yazmıştım;
ölçüm 4 döndü. Dördüncü kimlik `BORC-DEFTER-IKI-SEMA-01` — §1'de "defterde
yok" diye yazdığım kimlik, **onu yazmakla deftere girdi**. Sayıyı mandala
uydurmak yerine mandalı gerçeğe uydurdum: tavan **4**, dördüncünün iptal
edilmiş bir kimlik olduğu mandalın docstring'inde yazılı.

Ders (D-260'ın üçüncü yüzü): *bir kimliğin yokluğunu deftere yazmak onu var
eder.* Ölçüm, ölçümü kaydetmekle değişir. Bu yüzden tavan sayısı karar
metninden değil **mandal çıktısından** alınır.

### 6. Daha büyük bulgu: borç listesinin kanonik kaydı YOK

Kural yazarken asıl kusur çıktı. Ölçüm:

```
data/orchestrator/gorev_panosu.md -> 0 adet "BORC-"
PLAN_gorev_panosu.md              -> 0 adet "BORC-"
```

Borçların **tek** kaydı 4048 satırlık bu karar metninin içine saçılmış
durumda ve aynı borç çelişik durumlarla geçiyor:

- `BORC-KOLON-DUSUR-01` satır 3037'de "hala duruyor", satır 3121'de
  "kapandı".
- `BORC-PANEL-TAVAN-01` satır 2920'de "kapanmadı", satır 2945'te "kapandı".

D-222 "tek pano" diyor; borçlar panoya **hiç girmemiş**. Bu, D-265'in
aynısıdır bir katman yukarıda: *üç defter tutan sistem hiçbirine
güvenemez* — burada defter **sıfır**, durum anlatıya gömülü.

**Bu turda iki borç ölçümle çürüdü:**

- `BORC-QUALITY-BETIK-01` **iptal**: `scripts/recalc_quality_scores.py`
  **diskte yok** (`pathlib.Path(...).exists() -> False`). Borç var olmayan
  bir dosyayı işaret ediyordu.
- `BORC-SCRIPTS-01` **yanlış sayı**: "30+ `_tmp_*`/`_olcum_*`" dedi;
  ölçüm `_tmp_*` 19 + `_olcum_*` 3 = **22** (toplam `_*` girdi 44).

**Açık kalan borç — `BORC-PANO-BORC-00`:** borçlar tek panoya taşınacak,
her satır kanonik durumunu **kendi** söyleyecek. Bu turda **açıldı, kapanmadı**;
taşıma ayrı ve ölçüm gerektiren bir iştir, kuralla birlikte yapılmaz.

### 7. Araç dersi: kendi aracım hedefini ÜÇÜNCÜ kez bozdu

`D-269` → `D-271` yeniden adlandırmasını tek Python ifadesine sıkıştırdım:

```python
io.open(d,'w',encoding='utf-8').write(io.open(d,encoding='utf-8').read().replace(...))
```

`open(path,'w')` dosyayı **çağrı anında** kırpar — okuma argümanı
değerlendirilmeden önce. Altı kaynak dosya sıfır bayta indi.
`git checkout --` ile `5e2a354`'ten geri alındı (12897/4039/2175/8045/5548/6510
bayt doğrulandı), A maddesi işi tek tek yeniden uygulandı.

**Kural:** yerinde düzenleyen onarım aracı, **hiçbir dosyayı yazmak için
açmadan önce** tüm dosyaları okumuş olmalıdır. D-243'ün ("prova diske
yazmaz") doğrudan torunu. Sayaç: vault kökü yazımı, ters çevrilmiş modül
listesi, şimdi altı kırpılmış dosya → **3**.

Çürütülen iki hipotez de kayda geçer: `context_dg_stack` derinliği ve
`DeltaGeneratorSingleton` kimliği — ikisi de sebep değildi.

### 8. Kapanan / açılan borç

- `BORC-DEFTER-IKI-SEMA-01` — **kimlik yoktu**; uyarı ölçüldü, borç olarak
  **iptal**; gerçek kusur (nitelendirme) kesildi.
- `BORC-ADLANDIRMA-01` — **kimlik yoktu**; kural bu girdide yazıldı (§5).
- `BORC-TEST-SIRA-01` — **kapandı**: iki kirleten kesildi, iki mandal kuruldu.
  Yakalanamayan tek düşüş §4'te dürüstçe yazılı.
- `BORC-QUALITY-BETIK-01` — **iptal** (dosya yok).
- `BORC-PANO-BORC-00` — **yeni, açık**: borçların kanonik kaydı yok.

### 9. Doğrulama

```
python -m pytest tests/test_goc_defteri.py tests/test_data_log.py \
  tests/test_benchmark.py tests/test_migration_0017.py -q
40 passed, 100 warnings in 29.37s
```

Mandal `tests/test_dokuman_politikasi.py::test_d271_borc_adinda_fiil_artmiyor`
kuruldu ve **kırılarak** doğrulandı:

```
python -m pytest tests/test_dokuman_politikasi.py -q
6 passed in 3.39s

# kirma denemesi: FIIL kumesine gecici 'DEFTER' eklendi
AssertionError: D-271/1: fiil tasiyan borc kimligi 10, ust sinir 8.
```

Mandal çıktısı (kanonik sayı buradan alınır, karar metninden değil):
`borç kimliği 27 · fiilli 8/8 · sayılı 4/4`.

### 10. Yetim göç kopyaları — ve metin taramasının kör noktası

Kanonik göç dizini `src/company_master/schema/migrations` (36 dosya,
`scripts/goc_defteri.py::GOC_DIZINI`). Ölçüm iki **yetim kopya** buldu:

| yol | bayt | defterde |
|---|---|---|
| `db/migrations/0007_job_intelligence.sql` | 11252 | **yok** |
| `db/schema/migrations/0013_job_intelligence.sql` | 11256 | yok |
| `schema/migrations/0013_job_intelligence.sql` (kanonik) | 11518 | **var** |

Defter `0013`ü kaydeder, `0007`yi hiç görmemiş; üç dosya birbirinden bayt
olarak farklı. D-211/D-230 gereği ikisi silindi, mandal kuruldu
(`tests/company_master/test_migrate.py::test_tek_goc_dizini_var`),
`9999_kirma_denemesi.sql` ekilerek **kırılarak** doğrulandı.

**Asıl ders — bu kez yanlış ad BENİMDİ.** Silmeden önce "bu dosyalara
kod referansı yok" diye beyan ettim. Dayanağım `db/migrations` /
`db\migrations` metin taramasıydı. Oysa
`tests/test_job_intelligence_dikey.py:30` yolu **parça parça** kuruyordu:

```python
REPO_ROOT / "src" / "company_master" / "db" / "migrations" / "0007_job_intelligence.sql"
```

Ortada eşleşecek bir alt dize yoktu; tarama yapısal olarak kördü. Silme
kararı doğruydu, **kanıtı yanlıştı** — takım `FileNotFoundError` ile düştü.

> **Kural:** metin taraması, parçalardan kurulan bir yolun **yokluğunu**
> kanıtlayamaz. "Referansı yok" beyanı ya takımın yeşil koşusuna ya da
> sembol/AST taramasına dayanır; `grep` çıktısı tek başına yetmez.

Onarımdan önce kanonik dosyanın testin üç iddiasını da karşıladığı ölçüldü
(`DROP TRIGGER IF NOT EXISTS` yok · `job_postings` var · `UNIQUE` var);
test yalnızca **yanlış dosyaya** bakıyormuş — D-258/4 "yarım göç" deseni.

### 11. Sıra bilgisi — devir notunun karşılaştırması bu ortamda üretilemez

Devir notu "rastgele sıra → 1 failed / sabit sıra → 4445 passed" diyordu.
Ölçüm: **bu ortamda sıralama eklentisi hiç kurulu değil.**

```
pytest 9.1.1
{'pytest_randomly': False, 'pytest_reverse': False, 'pytest_random_order': False}
```

Sonuç: `-p no:randomly` bayrağı **etkisizdi**, `--reverse` reddedildi.
Rastgele sıra bu ortamda yeniden üretilemez (D-260: beyan kanıt değildir).
Ters sıra, bağımlılık eklemeden 2 satırlık yerel eklentiyle üretildi.

| sıra | sonuç |
|---|---|
| sabit | `4510 passed, 12 skipped` |
| ters (`items.reverse()`) | `4509 passed, 12 skipped, 1 deselected` |
| rastgele | **üretilemedi** — eklenti yok |

Ters sıradaki tek düşüş `test_vault_kokte_tek_kullanimlik_yok` idi ve
sebebi **kendi ölçüm aracımdı** (`_ters.py` kökte duruyordu) — D-226
bağımlılığı değil. Bu turda mandal ikinci kez kendi turunun artığını
yakaladı (birincisi §5'teki fiil mandalı). Araç D-241 gereği silindi.

**Kayma denetimi (yeni).** Ağaçta eşzamanlı başka ajan çalışıyordu
(`tests/test_ticaret_sicili_kanit.py` koşunun ortasında değişti; toplam
4524 → 4522'ye düştü). Bu yüzden son koşu **öncesi/sonrası toplama
sayımıyla** çerçevelendi: `4522 → koşu → 4522`. Sayı kaymamışsa koşu
geçerlidir; kaymışsa sonuç beyan edilemez.

**Referans:** D-211, D-222, D-226, D-227, D-230, D-241, D-243, D-258,
D-260, D-263, D-265, D-266, D-268.

## D-272 — Defterin kendisi sırasız; borcun son sözü satırda değil D numarasındadır (2026-09-29)

**Tür:** kök neden + uygulama. `BORC-PANO-BORC-00` **kapandı**.

### 1. Altı turun kök nedeni: AGENTS.md kronolojik değil

D-245'ten sonraki başlık dizisi ölçüldü:

```
[245…263, 266, 265, 264, 267, 268, 270, 269, 271]
```

Sırasız geçiş: `(266→265)`, `(265→264)`, `(270→269)`. Yani bir borcun **son sözü
dosyada aşağıda değil**, en büyük D numarasındadır. Her tur satır sırasıyla okudu
ve yanlış okudu — D-265/1, D-266/1, D-267/1, D-268/1, D-271/1 aynı desenin beş
tekrarıdır. Ad yanlıştı diye düzeltilen şey **adlandırma değil, okuma yönüydü**.

### 2. D-271'in "çelişki" iddiası da yanlıştı — çelişki yoktu

D-271/6 iki borcu çelişkili ilan etti. D-numarası atanarak ölçüldüğünde çelişki
yok, **kronoloji var**:

| Borç | D-271'in gördüğü | Gerçek |
|---|---|---|
| `BORC-PANEL-TAVAN-01` | s2920 "kapanmadı" vs s2945 "kapandı" | D-256 kapanmadı → **D-258 kapandı** |
| `BORC-KOLON-DUSUR-01` | s3037 "hâlâ duruyor" vs s3121 "kapandı" | D-258 duruyor → **D-259 kapandı** |

Kendi bulgumu geri alıyorum: bunlar **kapanmış**, açık sanılan iki borçtu — devir
notunun "en tehlikelisi" dediği sınıfın tam örneği. Sayı: **2**.

### 3. Tek kanonik kayıt: `docs/BORC_DEFTERI.md`

18 borç (açık 4, kapandı 10, iptal 4) + 8 kural kimliği tek tabloda. Yeni araç,
şema, tablo **yok** — 30 satırlık liste veritabanı istemez (D-240 mantığı).

Açık kalan dört borç: `BORC-VKN-01`, `BORC-NACE-DOGRULAMA-01`,
`BORC-SICIL-DAIRE-01`, `BORC-SCRIPTS-01`.

### 4. Kural (D-272)

1. Bir D-kaydı borç kapatıyor/iptal ediyorsa **aynı turda** `docs/BORC_DEFTERI.md`
   güncellenir. Deftersiz kapanış kapanış değildir.
2. Borç durumu **satır sırasından okunmaz**; kaynak ve kapanış D numarası yazılır.
3. Devir notu borçları defterden okur, hafızadan değil.
4. Durum dört değer alır: `ACIK` · `KAPANDI` · `IPTAL` · `KURAL`.

**Mandal:** `tests/test_dokuman_politikasi.py::test_d272_borc_defteri_eksiksiz` —
AGENTS.md'de adı geçip defterde olmayan kimlik varsa düşer. Yön tek (AGENTS.md →
defter); tersi denetlenmez, çünkü kapanan borcun D-kaydı silinmez.

### 5. Mandal kendi kör noktasını ilk koşuşta gösterdi — D-270'in aynası

`test_d272` ilk koşuşta kırmızı verdi: `VERI-GORUNURLUK-01` defterde yok. **Böyle
bir kimlik yok.** D-271'in `BORC_KIMLIK` kalıbı `\b` ile başlıyordu; `\b` tireyi
sözcük sınırı sayar, bu yüzden `ALTYAPI-VERI-GORUNURLUK-01` içinden olmayan bir
kimlik uyduruyordu. Kalıp soldan bağlandı:

```python
BORC_KIMLIK = re.compile(r"(?<![A-Z0-9-])(?:BORC|VERI)-[A-Z0-9-]+-\d{2}\b")
```

D-270 metin taramasının **yokluğu** kanıtlayamadığını söylüyordu; bu, aynı kusurun
diğer yüzü: tarama **varlığı** da uydurabilir. Ders: kimlik kalıbı iki uçtan da
bağlanır. D-271'in 8/4 tavanı bu düzeltmeden sonra da tutuyor (uydurma kimlik
`FIIL`/`SAYI` kümelerine girmiyordu).

**Ve sonra mandal ikinci kez kırmızı verdi — sebebi bu paragrafın kendisiydi.**
Kalıp düzeltmesi diskte duruyordu (`tests/test_dokuman_politikasi.py:104`, ölçüldü),
ama yukarıdaki metin `VERI-GORUNURLUK-01` dizesini **tek başına** andığı için hayalet
kimlik artık taranan gövdede **gerçekten** var (`AGENTS.md:4367`). Hayaleti kayda
geçirmek hayaleti var etti. Mandalın gördüğü kimlik sayısı **26 → 27**.

Karar: sayı kılıfına uydurulmadı, gerçeğe çekildi. `VERI-GORUNURLUK-01` deftere
`IPTAL | D-272` olarak girdi — "böyle bir kimlik yok" açıklamasıyla; çıkarmanın tek
yolu bu kaydı silmek olurdu. D-271'in tavanı 3 değil 4 yapmasıyla aynı karar.
Genel ders: **metin tarayan mandalda gözlemci etkisi vardır** — bulguyu yazmak
ölçümü değiştirir; değişikliği mandala değil deftere yazarsın.

**Araç tuzağı (bu turda üçüncü kez):** `apply_diff` `docs/BORC_DEFTERI.md`'de üç kez
tutmadı (%55/%54/%43), ve **çok satırlı `python -c` cmd.exe'de sessizce hiçbir şey
yapmadı** — çıktı yok, çıkış kodu 0, dosya değişmemiş. Yalnız dosyayı sonradan
ölçtüğüm için yakalandı; "komut geçti" ekranı kanıt değildir (D-260). Kural: tek
satır `-c` veya gerçek dosya.

### 6. Rastgele sıra ilk kez ÜRETİLDİ — ve yeşil

`requirements-dev.txt:8` `pytest-randomly>=3.15.0` **beyan ediyordu**, paket
**kurulu değildi** (D-260: beyan kanıt değildir). `TEST-ISO-02` tarihsel olarak
"teslim" sayılmıştı; teslim hiç etki etmemişti. Kuruldu — **yeni bağımlılık
değil**, var olan beyanın karşılığı; üretim bağımlılığı da değil.

| Sıra | Komut | Sonuç |
|---|---|---|
| sabit | `-p no:randomly` | **4511 passed, 12 skipped** (170.87s) |
| rastgele | `-p randomly --randomly-seed=272` | **4511 passed, 12 skipped** (185.94s) |
| rastgele | `-p randomly --randomly-seed=273` | **4511 passed, 12 skipped** (204.21s) |

Üçüncü satır §5'in ek metninden **sonra** koşuldu: bu kararın kendi düzenlemeleri
takımı bozmadı. Tek tohum bir iddiadır, iki tohum bir ölçümdür; bundan sonra
"rastgele sırada yeşil" cümlesi **tohum numarasıyla** yazılır, yoksa beyandır.

Taban 4510 → 4511: fark `test_d272_borc_defteri_eksiksiz`. Toplama sayımı
`4522 → koşu → 4522`, kayma yok.

**Yan bulgu:** kod tabanında **hiçbir config dosyasında `-p no:randomly` yok**
(`pytest.ini` tarandı, 0 eşleşme). Bayraklar yalnız AGENTS.md ve
`docs/plans/TEST-ISO-02_brief.md` metninde yaşıyordu — temizlenecek bayrak yoktu,
temizlenecek **iddia** vardı.

### 7. Eşzamanlı ajan — ölçüldü, karar ürün sahibinde (taşıma YAPILMADI)

| Ölçüm | Kanıt |
|---|---|
| Aynı ağaca yazan ajan | **3** — utku, ihsan, yasu (`data/orchestrator/file_locks.json`, 7 kilit) |
| Commit imzası | tek: `Yasua <yassuacohen@gmail.com>` — imza ayrımı **yok** |
| `.git/index.lock` | ölçüm anında yok |
| `.worktreeinclude` | **ölü** — 73 kural, hepsi `.gitignore`'un (95) içinde; yalnız-kendinde: **0**. Hiçbir kod okumuyor |
| Süper depo worktree | 2 (`master 1c3dd8c`, `.kilo/worktrees/bow-tarsier` detached; alt modül **boş**) |
| `scripts/ajan_cakisma_kilidi.py` | **kilitli ama diskte yok** — çakışma kilidi henüz kurulmamış (`ALTYAPI-AJAN-CAKISMA-01`, ihsan, plan) |

`.worktreeinclude` bir worktree düzeni **değildir**, `.gitignore` kopyasıdır.
"Tasarlanmış düzen var" varsayımı ölçümle çürütüldü.

**Seçenekler (karar ürün sahibinde, D-221/1: yol taşımanın bedeli faydasından
büyük olabilir):**

1. **Sıra düzeni (en ucuz):** tek ajan yazar, diğerleri bekler. Yeni kod 0.
   `file_locks.json` zaten var ve 48 yerden okunuyor — eksik olan **zorlama**.
2. **Kilidi zorla (orta):** `ALTYAPI-AJAN-CAKISMA-01` tamamlanır; yazma öncesi
   kilit kontrolü kapı olur. Ölçülen boşluk: dosya yok, kural kâğıtta.
3. **Ayrı worktree (en pahalı):** her ajan kendi ağacında. Bedel: alt modül her
   ağaçta ayrı doldurulur, `.venv` çoğalır, göç defteri tek canlı DB'ye bakmaya
   devam eder — **izolasyon testte var, veritabanında yok**. `.worktreeinclude`
   silinmeli veya gerçekten kullanılmalı.

Benim önerim **1 + 2**: kilit altyapısı zaten kurulu, eksik olan zorlama; worktree
ise DB'yi ayırmadığı için asıl çakışmayı çözmez.

### 8. Kapanan / iptal / açık borç

- `BORC-PANO-BORC-00` — **kapandı**: `docs/BORC_DEFTERI.md` kuruldu, mandal kırılarak doğrulandı.
- Yeni borç **açılmadı**. Defterin 45 kimliği kapsamayan regexi bilinen kör nokta
  olarak deftere yazıldı; borç değil, ölçülmüş sınır.

### 9. Doğrulama (çalıştırılmış komut)

```cmd
python -m pytest tests/test_dokuman_politikasi.py -q
# 7 passed

# kırma denemesi: defterden BORC-VKN-01 çıkarıldı
# AssertionError: ...olmayan 1 kimlik: ['BORC-VKN-01']  -> 1 failed
# geri alındı -> 7 passed

python -m pytest -p no:randomly -q
# 4511 passed, 12 skipped in 170.87s

python -m pytest -p randomly --randomly-seed=272 -q
# 4511 passed, 12 skipped in 185.94s
```

**Referans:** D-221, D-240, D-241, D-260, D-265, D-266, D-270, D-271.

## D-281 — Diskte yokluk silme değildir; index'te duran kayıt sonraki ajana yalan söyler (2026-09-29)

> Bu kayıt **D-273 olacaktı**. Olamadı: bkz. §5.

### 1. Devir notunun üç iddiası da yanlış çıktı (D-267/1 deseni **beşinci** kez)

| İddia | Ölçüm | Gerçek |
|---|---|---|
| Kökte 41 geçici betik (`check_*.py`, `debug_*.py`) **duruyor** | `dir /b check_*.py` → `File Not Found` | Diskte **yok**; git **index'inde 76 tane var** |
| `scripts/ajan_cakisma_kilidi.py` `.pre-commit-config.yaml`'a kayıtlı ama yok | `findstr` → eşleşme yok | Kayıt `data/orchestrator/file_locks.json`'da; ve **hayalet değil** |
| `.worktreeinclude` ölü | 73 kuralın **73'ü** `.gitignore`'da, okuyan kod 0 | Doğru — **tek doğru iddia** |

### 2. Bulgu: "hayalet" diye tek bir şey yok, **iki** ayrı hal var

| Disk | Index | Anlam |
|---|---|---|
| yok | yok | **Rezervasyon** — henüz yazılmamış dosyanın meşru kilidi (ihsan, `ALTYAPI-AJAN-CAKISMA-01`) |
| yok | **var** | **Index hayaleti** — commit edilmemiş silme; sonraki ajan `git ls-files`'a bakınca "bu dosya var" sanır |

Kilit dosyasındaki 7 kayıttan 2'si rezervasyon, 2'si index hayaleti
(`skills/devops/__init__.py`, `skills/streamlit/__init__.py` — yasu'nun D-269
sırasındaki silmesi), 3'ü diskte.

### 3. Kök neden: D-221 mandalı **yalnız diske bakıyordu**

`tests/test_kok_politikasi.py::_vault_kok_tek_kullanimlik()` `VAULT_KOK.iterdir()`
kullanıyordu. 76 betik diskten silinmiş ama commit edilmemiş olduğu için mandal
**yeşil yanıyordu** — yanlış öncülle. D-270'in ("yokluk metin/disk taramasıyla
kanıtlanmaz") birebir tekrarı; bu kez kanıt aracı mandalın kendisiydi.

### 4. Kural (D-281)

1. **Diskte yokluk silme değildir.** Silme ancak commit edilince biter. Kilit
   sahibi ajan, silmesini commit etmeden işini bitmiş saymaz.
2. Kök temizliği mandalı **disk ∪ index** üzerinden ölçülür. Yalnız diske bakan
   kontrol, kanıt değil beyandır (D-260).
3. Kesilemeyen borç **sıfırlanmaz, tavanlanır**: ölçülen sayı sabit yazılır,
   test yalnız "artmasın" der. Tavan yalnız **küçülür**.

### 5. Karar numarası çatışması — D-227 ve D-272 ihlali (bulgu, düzeltme değil)

Ölçüm: `AGENTS.md` en yüksek D = **272**, `docs/BORC_DEFTERI.md` en yüksek D = **280**.
Defterde **8 karar başlığı** var (D-273…D-280, TOBB/MERSİS/OCR konuları).

- **D-227 ihlali:** karar numarası yalnız `AGENTS.md`'den verilir; defter numara üretemez.
- **D-272 ihlali:** defter **durum** tutar, `AGENTS.md` **gerekçe** tutar; defter karar kaydı barındıramaz.

Başka ajanın işi **sessizce taşınmadı** — bulgu kaydedildi, taşıma kararı ürün
sahibinin. Bu turun kaydı numara çakışmasın diye **D-273 → D-281** olarak kaydırıldı.

### 6. Yapılanlar

- `.worktreeinclude` **düşürüldü** (`git rm`, D-266); tek belge referansı gerekçesiyle düzeltildi.
- `tests/test_kok_politikasi.py`'ye **genel mandal**: `test_d281_kilitli_dosya_index_hayaleti_degil`,
  `test_d281_kokte_index_hayaleti_tek_kullanimlik_yok`. Dosyaya özel değil, **kayıtlı ama yok** desenini yakalar.
- `BORC-SCRIPTS-01` **ölçüldü, kesilmedi**: `scripts/_*` = 41 girdi (29 `.py` **hepsi derlenir**,
  **0 çürük**, 1 dizin, 11 veri), **üretim çağıranı 0** (tüm isabetler belge/rapor).
  Kesme kararı ürün sahibinde — "borcumuz kalsın" kararı `docs/BORC_DEFTERI.md`'de,
  `AGENTS.md`'de ve `git log --all -i --grep` içinde **bulunamadı** (kaynaksız iddia).
  Ağaçta 3 ajanın 94 commit edilmemiş silmesi var; başkasının işini commit etmedim.

### 7. Araç kusuru (kendi engelim, beyan)

`ask_followup_question` **üç** denemede de `Missing value for required parameter 'follow_up'`
ile düştü; parametre her seferinde tamdı. Soruyu kanala soramadığım için
**hiçbir şey silmedim**, soruyu deftere `## Devir` bloğuna yazdım.

### 8. Kapanan / açık borç

- `.worktreeinclude` ölü dosyası — **kapandı** (düşürüldü).
- `BORC-SCRIPTS-01` — **açık**, ölçüldü ve **tavanlandı** (76/2), karar ürün sahibinde.
- Yeni borç: karar numarası çatışması (defterde 8 karar kaydı) — ürün sahibine sunuldu.

### 9. Doğrulama (çalıştırılmış komut)

```cmd
python -m pytest tests/test_kok_politikasi.py -q
# 7 passed in 1.19s

# kırma denemesi: tavanlar 76/2 -> 75/1
# 2 failed, 5 passed in 1.25s   (her iki D-281 testi de düştü)
# geri alındı -> 7 passed in 1.39s

python -m pytest -q -p no:randomly
# 1 failed, 4527 passed, 12 skipped in 215.80s

python -m pytest -q -p randomly --randomly-seed=281
# 1 failed, 4527 passed, 12 skipped in 175.54s
# FAILED tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari
```

Tek kırmızı iki sırada da aynı → sıra bağımlılığı yok, gerçek kusur:
`yasu_project_context.md` 213 satır, D-219 tavanı 200. **Benim dosyam değil, düzeltilmedi**
(başka ajanın açık işi). Mandal doğru çalıştı; kusuru yakalayan mandalın kendisidir.

**Referans:** D-221, D-224, D-227, D-241, D-256, D-260, D-266, D-269, D-270, D-272.

---

## D-286 — Zorlayıcısı olan kilit; ve numara havuzu tek kapıdan verilir (2026-09-29)

### 1. Kilit bir **beyandı** — artık değil

`data/orchestrator/file_locks.json`'u **yazan** var (`task_board._lock_alan`, yalnız görev
açılışında), **okuyan** var (panel, doğrulama betikleri, testler), **zorlayan yoktu**.
`trigger.py` kilide yalnız görev bitince *dokunur* — bırakır (satır 381, 472); hiçbir yazmayı
durdurmaz. Kanca dizininde `file_locks` geçen tek satır yoktu. D-261'e göre bu bir mekanizma
değil **beyandır**.

- **Zorlayıcı:** `scripts/kilit_zorla.py` (~40 satır, stdlib, yeni bağımlılık yok).
  Staged yolları kilit tablosuyla kesiştirir; sahibi ben değilsem `1` döner.
- **Kanca:** `scripts/hooks/pre-commit` (canlı olan bu — `core.hooksPath=scripts/hooks`,
  `.git/hooks/pre-commit` **ölüdür**), testlerden **önce** çağırır.
- **Kimlik:** `AJAN` env değişkeni yok, `huginn.ajan` git config'i yok. Tek kaynak
  `git config user.name` (`Yasua` → `yasu`).
  `ponytail:` kimlik çözülemezse **uyarır ve geçer** — üç ajanı birden bloke etmemek için.
  Yükseltme: her ajan `git config huginn.ajan <ad>` kurduğunda orası `return 1` olur.

### 2. Mekanizmanın **ölçülen tavanı**: rezervasyon zorlanamaz

Kırma provasında utku'nun kilitli dosyasını stage etmeyi denedim:
`fatal: pathspec 'src/company_master/etl/nace_coklu_ata.py' did not match any files`.
Sebep D-281'in kendisi: o kilit bir **rezervasyon** (ne diskte ne index'te). Var olmayan
dosya stage edilemez → **commit anındaki zorlayıcı rezervasyonu asla yakalayamaz.**
Yalnız *var olan* dosyanın kilidini korur. Bu bir kusur değil, ilan edilen sınırdır;
rezervasyonu korumak yazma anında (editör/ajan katmanında) kapı ister — bu turda yapılmadı.

### 3. Üçüncü yol — açıkça beyan

Devir notu `scripts/ajan_cakisma_kilidi.py` için "ya yaz ya kaydı düş, üçüncü yol yok" dedi.
Ölçüm üçüncü bir hâl gösterdi: o yol **ihsan'ın canlı rezervasyonu**
(`ALTYAPI-AJAN-CAKISMA-01`, durum `plan`). Kaydı düşürmek yalan olurdu; oraya yazmak
**tam da zorlamaya çalıştığım kilidi ihlal** ederdi. Zorlayıcıyı **kilitsiz başka bir
dosyaya** (`scripts/kilit_zorla.py`) yazdım. Talimattan sapmadır, gizlemiyorum.

### 4. Numara havuzu tek kapı (BORC-KARAR-NUMARA-01 **yeniden yazıldı**)

Önceki turun teşhisi **yanlıştı**: "defterdeki D-273…D-280 D-227+D-272 ihlalidir" dedi.
Ürün sahibi düzeltti — o kayıtlar **emirle** yazıldı, ihlal değil. Ölçülen gerçek sapma:
numara **iki ayrı dosyadan** tahsis ediliyordu ve çatışma **görünmüyordu**.

D-227 mandalının üç kör noktası (ölçüldü):
1. `KANONIK` regex'i yalnız `(D-NNN — KAH…` biçimini görür; `## D-NNN — …` biçimini görmez.
2. `H1_SAHIPLENME` yalnız `^# ` tarar, `## ` taramaz.
3. `test_kanonik_karar_numaralari_tekil` yalnız `AGENTS.md` okur — defteri hiç görmez.

Sonuç: **D-281 iki ayrı karara birden** verilmiş (AGENTS.md'de bu kayıt; OSTİM tarafında
başka bir karar). Çift anlam **duruyor**; çözümü numara değiştirmek maliyetli
(OSTİM tarafı ~12 referans / 7 betik + 1200 satırlık rapor) → ürün sahibine bırakıldı.

- **Kural:** karar numarası **tek havuzdan** verilir: `python scripts/karar_no.py`.
  Havuz = `AGENTS.md` + `docs/BORC_DEFTERI.md`, iki başlık biçimini de tanır.
- **Ürün sahibinin yetkisi kısıtlanmaz:** karar başka dosyaya yazdırılabilir (D-227 istisnası
  yazıldı). Kısıtlanan tek şey numaranın **kaynağıdır**.
- **Mandal:** `tests/test_karar_numara_tekligi.py` +3 test, `TAVAN_CATISMA = 1`
  (D-220 deseni: ölçülen gerçek tavanlanır, yalnız küçülür).
  `test_havuz_iki_dosyayi_da_gorur` kök nedenin nöbetçisidir — havuzdan defter düşerse
  çatışma yine görünmez olur.

### 5. Araç tuzağı: `%errorlevel%` **yalan söyledi** (yeni D-86 varyantı)

`... & echo EXIT=%errorlevel%` tek satırda `0` yazdı — oysa betik `DURDU` basmıştı.
Sebep: `%errorlevel%` **ayrıştırma anında** genişler, komut çalışmadan önceki değeri basar.
Doğru ölçüm `if errorlevel 1` ile yapılır. Ayrıca çok satırlı komut bu turda **iki kez**
yalnız ilk satırı çalıştırdı; biri tavanı `0`'da bıraktı — `findstr /n` ile yakalandı.
Her yazma ölçümle doğrulanır; kazayı kırma kanıtına çevirdim.
Ek not: `sh` PATH'te **yok**; kancayı elle koşturmak mümkün değil, tek dürüst kanıt
gerçek `git commit` denemesidir.

### 6. Doğrulama (çalıştırılmış komut çıktısı)

```cmd
python scripts\kilit_zorla.py
REM temiz durum -> exit 0

REM KIRMA: sahte kilit (D-243, yol enjekte edilebilir; canlı dosyaya dokunulmadı)
set HUGINN_KILIT_YOL=.kir_kilit.json&& python scripts\kilit_zorla.py
REM [kilit] 0) -> utku (TEST-KIR-01)
REM [kilit] DURDU: 1 dosya yasu disinda bir ajanin kilidinde...
REM if errorlevel 1 -> GERCEK_EXIT=1

REM UÇTAN UCA: gerçek commit denemesi
set HUGINN_KILIT_YOL=.kir_kilit.json&& git commit -m "KIRMA PROVASI"
REM [kilit] DURDU: ... (kanca ateşledi)
git log --oneline -1
REM 6c52bdd   <- commit OLMADI

python -m pytest tests/test_kilit_zorla.py -q -p no:randomly
REM 6 passed in 3.78s

python scripts\karar_no.py
REM CATISMA: ['D-281']
REM AGENTS.md: 103 baslik, max=D-281
REM BORC_DEFTERI.md: 10 baslik, max=D-282
REM sonraki bos numara = D-283  <- BAYATLADI: baska ajan ayni anda defterde
REM D-283'u kullandi; mandal yakaladi, bu kayit D-286'e tasindi (bkz. §8)

python -m pytest tests/test_karar_numara_tekligi.py -q -p no:randomly
REM 9 passed in 1.96s
REM kırma: TAVAN_CATISMA 1 -> 0
REM AssertionError: KARAR NUMARASI CATISMASI ARTTI: ['D-281'] (tavan 0)
REM geri alındı -> 9 passed
```

### 7. Kapanan / açık borç

- `BORC-KARAR-NUMARA-01` — **kapandı** (yeniden adlandırıldı + tek kapı kuruldu).
- Kilidin zorlayıcısızlığı — **kapandı** (var olan dosyalar için).
- `BORC-AJAN-HAFIZA-01` — **açıldı**: `yasu_project_context.md` 213 satır > D-219 tavanı 200.
  **Kesilmedi** — başka ajanın hafıza dosyası; deftere "SAHİBİNDE" yazıldı, sahibine chat açıldı.
- **Açık:** rezervasyon zorlaması (commit anında imkânsız), D-281 çift anlamı,
  `BORC-SCRIPTS-01` 76 hayalet (**donduruldu**, ürün sahibinde), canlı DB ayrımı.

### 8. Ajan chat (D-210/D-217 zorunlu)

```cmd
python scripts/ajan_chat.py bulgula "Karar numarasi tahsisi (D-286)" "..."
python scripts/ajan_chat.py bulgula "Kilit zorlamasi tavani (D-286)" "..."
```

İki bulgu kaydedildi: (1) numara tahsisinde eşzamanlı ajan yarışı, (2) kilit
zorlamasının rezervasyonu kapsamayan tavanı. İkisi de aşağıda açıklanıyor.

Ürün sahibi emriyle **ajanlar arası organizasyon** da chatten kuruldu:

```cmd
python scripts/ajan_chat.py ac yasu  BORC-AJAN-HAFIZA-01       "213>200, SAHIBINDE, kesmedim..."
python scripts/ajan_chat.py ac ihsan ALTYAPI-AJAN-CAKISMA-01   "kilit zorlaniyor; kilit dosyani bitirecek misin..."
```

- **yasu'ya:** hafıza dosyası tavanı (kesim sahibinde) + `scripts/ostim_detay_tamamla.py`
  73/78 girinti hatası (onun açık işi, dokunulmadı).
- **ihsan'a:** kilit artık zorlanıyor; `ajan_cakisma_kilidi.py` **onun canlı rezervasyonu** —
  bitirecek mi yoksa kayıt düşürülecek mi, kararı sahibinde. Numara tek kapı duyurusu.

**Kimlik düzeltmesi (ürün sahibi bildirdi):** orkestratör = **ihsan** = bu ajan. `git config
user.name` `Yasua` döndüğü için `kilit_zorla.ajan_kimligi()` beni `yasu` sanıyor; `ajan_chat.py`
ise `orkestrator` yazıyor. **Üç isim, tek aktör** (D-265'in "üç defter tutan sistem hiçbirine
güvenemez" deseni). `ponytail:` kanonik ad tek kaynağa bağlanmadı; ajan kendi adını kendi
seçemez. Yükseltme: ad netleşince `ajan_kimligi()` `git config huginn.ajan` okur, `user.name`
tahminini bırakır (tek satır).

**Karşılıklı okuma + ihsan kararları (ürün sahibi emri):** `ajan_chat.py oku --son 12` ile
bekleyen talepler okundu ve cevaplandı:

| Kimden | Talep | Karar |
|---|---|---|
| yasu | OSTİM izin adımının sahibi kim? | **ihsan (ben)** — resmî yanıt kurum adına yazılır, hukuki taahhüt ajana devredilmez (D-257 sınırı). Metni yasu hazırladı, ilerletme bende. |
| yasu | Birleştirme sorumluluğu kimde? | **yasu'da kalıyor.** Talimat beklerken tamamlaması **doğru** karardı: boş beklemek iş kaybı, dosya geri alınabilir, veri kaybı riski yoktu. Şart: kolon karışması **assert** ile mandallanır (D-270), prova boş tabloya yazar (D-243). |
| yasu | 3.297 detay taraması izin gelmeden başlatılmadı | **Onaylandı** — "ticari olmayan kullanım" koşuluna saygı; ölçülmüş doğru duruş, kayda geçti. |
| utku | `source_records.company_id` blokajı | **Bayat** — `VERI-KAYNAK-BAG-01` D-263'te kapandı (göç 0033). Blokaj değil. |
| utku | `tender_monitor` tablosu yok | **İtiraz geçerli** ama tablo açmak kapsam kararı — `KAPSAM-HEDEF-01` ürün sahibinde. Kendi göçünü yazma. |

**Karşılıklı okuma (ürün sahibi emri):** `ajan_chat.py oku --son 12` ile diğer ajanların
kayıtları okundu; bekleyen üç talep cevaplandı:

| Kimden | Talep | Cevabım |
|---|---|---|
| ihsan | OSTİM ticari kullanım izni kim ilerletsin? | **KAHİN'in** — hukuki taahhüt, ajan karar veremez (D-257 deseni). Metni hazırla, gönderme. |
| ihsan | Veri birleştirme sahibi kim? | **Sen** — ama kolon karışması metin taramasıyla değil **assert** ile yakalanır (D-270), prova boş tabloda (D-243). |
| ihsan | D-283 numarası | **Sende kalıyor**, itiraz yok; kaydımı D-286'e taşıdım. |
| utku | `source_records.company_id` blokajı | **Bayat** — `VERI-KAYNAK-BAG-01` D-263'te kapandı (göç 0033). Blokaj değil. |
| utku | `tender_monitor` tablosu yok | **İtiraz geçerli** ama tablo açmak kapsam kararı — `KAPSAM-HEDEF-01` ürün sahibinde. Kendi göçünü yazma. |

### 9. Mandal daha mürekkebi kurumadan **kendi yazarını** yakaladı

Bu kaydı `D-283` olarak yazdım; ölçüm (`sonraki bos numara = D-283`) o anda doğruydu.
Yazdıktan sonraki ilk koşuda mandal kırmızı verdi:
`KARAR NUMARASI CATISMASI ARTTI: ['D-281', 'D-283']`. Sebep: **başka bir ajan aynı anda**
deftere `## D-283 — Veri çekme politikası…` yazmıştı (satır 523). Kayıt `D-286`'e taşındı.

Bu, eşzamanlı ajan düzeninin gerçek dersidir: **ölçüm anlıktır, tahsis değildir.**
`karar_no.py` çatışmayı *sonradan* görür, *önceden* rezerve etmez.

### 10. Aynı yarış **ikinci kez** yaşandı — tahsis artık atomik

Tam takım koşusunda ikinci kırmızı: `CATISMA: ['D-281', 'D-284']`. Sebep yine eşzamanlılık —
yasu deftere `## D-284` **ve** `## D-285` yazarken ben AGENTS.md'ye `## D-284` yazmıştım.
§9'da koyduğum yükseltme şartı ("ikinci kez yaşanırsa rezerve eder") **gerçekleşti**, uyguladım:

`karar_no.py --al` numarayı `data/karar_tahsis/D-NNN.txt` dosyasını `O_EXCL` ile açarak
**kapatır**; dosya varsa bir sonrakine geçer. Yarışı kaybeden ajan çakışan numarayı alamaz.
`sonraki()` artık tahsis edilmiş ama henüz belgeye yazılmamış numaraları da sayar.

Kırılarak doğrulandı — iki ardışık tahsis farklı numara verdi:

```
set HUGINN_AJAN=ihsan& python scripts\karar_no.py --al   → TAHSIS EDILDI = D-286
set HUGINN_AJAN=yasu&  python scripts\karar_no.py --al   → TAHSIS EDILDI = D-287
```

Bu kayıt tahsisli **D-286**'ya taşındı (yasu'nun D-284/D-285'ine dokunulmadı); deney artığı
`D-287.txt` düşürüldü. Ölçüm: `CATISMA: ['D-281']` — tavan yine **yükseltilmedi** (D-220).

`ponytail:` tahsis ancak **tüm** ajanlar `--al` kullanırsa tam korur; ajan adı `HUGINN_AJAN`
ortam değişkeninden okunur (tek kaynak değil — bkz. §8 kimlik notu). Yükseltme: karar yazan
her yol bu kapıdan geçirilir, `--al` kancaya bağlanır.

**Referans:** D-220, D-227, D-241, D-243, D-256, D-260, D-261, D-266, D-270, D-272, D-281.

## D-287 — Ayırt etmeyen doğrulama kanıt değildir (2026-09-29)

### Bulgu 1 — `verified` sıfır değil, değer kümesinde yok

`companies.nace_validity`: `medium` 5732 · `unknown` 2942 · `fallback` 738. `verified`
**hiç üretilmiyor**. Kolon `src/` altında hiçbir yerde **okunmuyor**; yalnız yazılıyor ve
`nace_source`'un aynası (`sector_default→medium` 5679, `unknown→unknown` 2388,
`fallback→fallback` 654, `invalid_cleared→unknown` 554). Yani bilgi taşımayan bir kolon
tavanı kilitliyor sanılıyordu; kilidi tutan aslında `nace_source`.

NACE kod doluluğu **8289/9412 = %88,07**; kanıt kaynaklı (`mersis`/`external`) NACE
**0/9412 = %0** (D-260: iki oran birlikte).

### Bulgu 2 — Sözlük var, ama hiçbir şeyi ayırt etmiyor

`nace_codes` **3319** satır, **yetim kod 0** — 8289 kodun tamamı sözlükte. Devir notunun
"en ucuz doğrulama" önerisi (sözlük üyeliği + biçim/uzunluk) **ölçümle reddedildi**:
her firma geçtiği için hiçbir firmayı ayırmaz, puana bağlanırsa 8289 **tahmin** koda 1.0
ağırlık dağıtırdı. Bu, D-245/D-252'nin yasakladığı puan uydurmanın ta kendisidir.

### Karar — ağırlık çekilmedi, kilit dürüst

`nace_code` ağırlığı **1.0'da kaldı**. NACE gerçekten %100 tahmin
([`docs/HEDEF_VERI_KAPSAMI.md`](docs/HEDEF_VERI_KAPSAMI.md) s.190, D-258); sistem "bu firma
eksik" derken doğru söylüyor. Ağırlığı düşürmek tavanı **sahte** yükseltirdi — ölçümü
gerçeğe değil, gerçeği ölçüme uydurmak olurdu. Kilidi ancak kanıt kaynağı açar
(`BORC-VKN-01` / MERSİS); bu tur açılmadı.

### Kural

> **Biçim/sözlük doğrulaması kanıt değildir. Kaynak doğrular, şekil doğrulamaz.**
> Ayırt etmeyen bir kontrol puana bağlanamaz.

Mandallar ([`tests/test_panel_durustluk.py`](tests/test_panel_durustluk.py), kancada):
`test_nace_puani_sozluge_veya_validity_kolonuna_bakmaz` ·
`test_nace_kanit_kaynaklari_tahmin_etiketi_tasimaz`.
**Kırılarak doğrulandı:** `NACE_KANIT_KAYNAKLARI`'ya `sector_default` eklendi → **3 kırmızı**
(yeni iki mandal + mevcut D-252 mandalı), geri alındı → **19 yeşil** (17→19).

### Karar A — `ac` yanlış kapı uyarısı (ürün sahibi onayı)

[`chat.acik_sahipler()`](src/company_master/chat.py:50) aynı `task_id` altında **başka**
ajanın açık kaydını döner; [`cmd_ac`](scripts/ajan_chat.py:34) stderr'e uyarır.
**Engelleme yok** — ürün sahibi kararı: uyarı yeter. Saf fonksiyon, mevcut `oku()`'yu
kullanır; yeni dosya, yeni bağımlılık yok. 6 mandal (15→21), `test_cli_uyariyi_cagirir`
çağıranı zorlar (D-266).

### Karar B — karar numarası mandalı kancaya bağlandı

`karar_no.py` **değiştirilmedi**. Aranan koruma (`TAVAN_CATISMA = 1`,
[`tests/test_karar_numara_tekligi.py`](tests/test_karar_numara_tekligi.py)) zaten vardı;
eksik olan tek şey kancaya bağlı olmamasıydı — gönüllü koruma koruma değildir (D-261).
[`scripts/hooks/pre-commit`](scripts/hooks/pre-commit) **tek satır** genişletildi.
**Kırılarak doğrulandı:** deftere sahte `## D-286` başlığı eklendi → commit **durdu**
(`KARAR NUMARASI CATISMASI ARTTI: ['D-281','D-286']`, `assert 2 <= 1`), geri alındı → yeşil.
Kanca alt kümesinin yeni maliyeti **19,4 sn** (dosyadaki "~15 sn" notu düzeltildi).

### Karar C — yazma kapısı ölçüldü, mimari değişmedi

Canlı-DB ayrımına ürün sahibi **HAYIR** dedi (D-221/1); yerine kapı ölçüldü:

| Ölçüm | Sayı |
|---|---|
| motor çağıran dosya | 163 |
| gerçekten **YAZAN** (SQL + execute) | 70 |
| doğrudan `create_engine` | 25 (24'ü `connection.py`'yi atlıyor) |
| yazan ama motorsuz (gizli üçüncü yol) | **0** |
| dağılım | `src/` 22 · `scripts/` 47 · **`web_dashboard/` 0** |

Okuma: yazma kapısı **tek değil**; ama **panel hiç yazmıyor**, yani ayrımın dayandığı risk
panelde yok. Göç kapısı tekliği (D-269) veri yazma kapısı için geçerli değilmiş.

### Kapanan borç

`BORC-NACE-DOGRULAMA-01` → **KAPANDI** (defterde işlendi, D-272/1).
Ölçüm aracı `scripts/_nace_olcum.py` tek kullanımlıktı, **silindi** (D-241).

**Referans:** D-221, D-241, D-245, D-249, D-252, D-258, D-260, D-261, D-266, D-269, D-272, D-286.

## D-288 — Otomasyon toptan sahneleme yapamaz (2026-09-29)

### Bulgu

Günde iki kez çalışan bir zamanlanmış görev tüm ağacı `git add -A` ile sahneliyordu.

- **Otomasyon:** `scripts/git_auto_push.bat`, Windows Zamanlanmış Görev `\Huginn Git Push`,
  **iki tetik** (00:01 ve 12:01, günlük), ikisi de `2026-09-11`'den beri, kuran `EXCALIBUR\yasin`.
  Son çalışma 29.09.2026 12:01:01, sonraki 30.09.2026 00:01:00.
- **Kaç yol:** kodda **iki** toptan sahneleme noktası — `scripts/git_auto_push.bat:33` ve
  `wiki_automation/run_all.py` `git_commit()`. Diğer Huginn görevleri (DB Backup, Nöbetçi,
  Telegram Bot, TetikSenk, KILO-BackupRotate) commit atmıyor; ölçüldü.
- **Etki:** `Otomatik gunluk commit` başlıklı **64 commit**, **2150 benzersiz dosya**.
  Dağılım: `data_worktree` 507, `data` 349, `scripts` 233, `src` 217,
  `_ARSIV_tek_kullanimlik` 160, `tests` 143, kök 141, `docs` 92, `.claude` 84.
  Yani kod ve test, otomasyon eliyle tarihe girdi.
- **Kural çelişkisi:** kural kitabının kendisi (`AGENTS.md`, D-193 maddesi) ajanlara
  `git add -A && git commit` **emrediyordu**. Zorlayıcı eksik değildi sadece; yazılı kural
  ikiye bölünmüştü. D-261 deseninin daha kötü hali: kural kuralla çelişiyor.

### Sır araması (zorunluydu, yapıldı)

`git log --all --diff-filter=AM` ile `.env`, `*.key`, `*.pem`, `*secret*`, `*token*`,
`*password*`, `*credential*` desenleri tarandı.

- **Otomatik commit'lerin içinde sır YOK.** Çıkan isimler yalnızca sır *aracı*:
  `scripts/rotate_secrets.py`, `tests/test_secrets_rotation.py`, bir kurulum raporu.
- **Ama tarihte gerçek bir özel anahtar var:** `config/certs/selfsigned.key`,
  içeriği `-----BEGIN RSA PRIVATE KEY-----`. Ekleyen commit `90c4702` (2026-09-20).
  HEAD ağacında **yok**, izlenmiyor (`git ls-files` boş) — **ama** `90c4702` HEAD'in
  atası (`git merge-base --is-ancestor` → 0) ve blob ulaşılabilir:
  `216cfdd540712a8c327ceb1cd4bc1ec37c6048fe`. **Otomasyonun ürünü değil, elle girmiş.**
- `workspace/external/cursor_grok/.../leak.py` = `API_KEY = 'secret123'`, kasıtlı sahte fikstür.

**Temizlik YAPILMADI.** Tarih yazmak geri dönüşsüzdür; karar ürün sahibinindir.

### Karar

`git add -A` **beyaz listeye** çevrildi. Otomasyon durdurulmadı (ürün sahibinin kararı).

Ölçülen seçenekler: **(A)** otomasyonu durdur → günlük yedek kaybolur, PO kararı, yapılmadı.
**(B)** beyaz liste → **uygulandı**, en küçük değişiklik, yedek yaşamaya devam eder.
**(C)** `pre-commit`'e bırak → kanca commit **anında** çalışır, `add`'i engellemez; yetmez.

Kapsam: `data docs hubs plans indexes`. `data_worktree` bilerek dışarıda — D-228'de tasfiye
edildi, diskte yok (`git worktree list` tek ağaç gösteriyor).

### Kural

**Hiçbir betik toptan sahneleme yapmaz.** `git add -A`, `git add --all`, `git add .` yasak;
yol vererek sahnele: `git add -- <yol> [<yol>...]`.

Beyaz liste, kara liste değil: kara liste yeni bir dizin açıldığında **sessizce** sızdırır ve
tarihe giren tek bir kimlik dosyası geri alınamaz. Bu bir güvenlik sınırıdır, kolaylık değil.

### Kanıt

Mandal: `tests/test_otomasyon_sahneleme.py` — `git ls-files` üzerinden izlenen yürütülebilir
dosyaları tarar (diske değil), yorum/docstring soyar (kuralı *anlatan* metin ihlal değildir),
kendini muaf tutar.

**Kırarak doğrulandı ve mandal ilk sürümünde YALANCI YEŞİLDİ.** İlk desen düz `git` arıyordu;
`.bat` git'i `"%GIT%"` değişkeniyle çağırdığı için gerçek `"%GIT%" add -A` satırını
**kaçırıyordu**. İlk koşuda gelen kırmızı, çalışan koddan değil kendi gerekçe yorumumdan
geliyordu. Kırma testi olmasaydı bu mandal hiç çalışmadan yeşil duracaktı — D-260'ın
(beyan kanıt değildir) mandallara uygulanmış hâli: **yeşil test de beyandır, kırılana kadar.**
Desen `%GIT%` / `$GIT` biçimlerini kapsayacak şekilde düzeltildi, `.bat` ve `.py` yolları
ayrı ayrı kırılıp kırmızı görüldü, geri alındı.

### Kapanan borç

`_ARSIV_tek_kullanimlik/_pytest_rerun.txt` sahneden çıkarıldı (`git rm --cached`);
`test_zaman_damgali_yedek_git_te_izlenmiyor` yeşil.

`.gitignore` neden tutmadı (ölçüldü): kural eksikliği değil, **kapsam hatası**.
`/_*.txt` baştaki eğik çizgi yüzünden yalnız köke bağlıydı, alt dizine inmiyordu;
`git check-ignore -v` çıkış kodu 1 ve çıktısı boştu — hiçbir desen eşleşmemişti.
`_pytest_rerun*` eklendi, doğrulandı.

**Yan bulgu, kesilmedi:** `_ARSIV_tek_kullanimlik/` altında **~160 izlenen dosya** var
(tek kullanımlık `check_*`, `fix_*`, `run_*` betikleri + `kilo_skills_yedek/`).
`BORC-SCRIPTS-01` DONDURULMUŞ durumda; ölçüldü, rapor edildi, dokunulmadı.

**Referans:** D-193 (düzeltildi), D-226, D-228, D-229, D-241, D-260, D-261, D-267, D-270, D-281, D-286.

## Ilgili Nodlar

- [[docs/BORC_DEFTERI]]
- [[scripts/kilit_zorla]]
- [[scripts/karar_no]]
