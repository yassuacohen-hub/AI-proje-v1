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

### DASH-UX-02a Split: v1 (Dosya) / v2 (SECTIONS) (D-185 — KAHİN kararı 2026-09-21)
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

## Brifsiz Atama Yasak (D-66 — KAHİN kararı 2026-09-20)
- **Kural:** Hiçbir ajan hiçbir görev almaz brifsiz. Brif dosyası **mutlaka** `data/orchestrator/<TASK>_brif_<tarih>_<rol>.md` veya `plans/brief_<ajan>_<TASK>.md` olarak diskte hazır ve **tetik `talimat` alanına path yazılı** olmalıdır.
- **D-80 pekiştirme (KAHİN kararı 2026-09-20): Talimat + brif ikisi de ZORUNLU.** Panoda görev `aktif` olabilmesi için üç şart birlikte sağlanır:
  1. `brief` alanı dolu ve işaret ettiği dosya diskte var.
  2. `talimat` alanı dolu (en az bir cümle; ne yapılacağı + brif referansı).
  3. Tetik `talimat` alanı pano `talimat` alanıyla aynı metni taşır.
  Üçünden biri eksikse atama **yapılmaz**, tetik **düşürülmez**.
- **Kontrolü:** `tetik_ekle(task_id, ajan, talimat="")` argümanı boş stringse, çağrı yapılmaz. Orkestratör brifsiz görev atarsa (tetik hatasız düşerse de) YASU/UTKU teslim TESLİM ETMEYECEKTİR — `"brif yok"` cevabı verir, task stale kalır.
- **Uygulanacak:** Her talimat argument'i yazılırken dosyanın var olduğu doğrulanacak; yoksa `FileNotFoundError` veya benzer hata alınacak ve işlem durdurulacak. Gerekli brief yazılıncaya kadar görevi tekrar tetiklemek yasak.
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
- **`AI proje v1/` submodule DEĞİLDİR.** Submodule kullanımından dönüldü (ürün sahibi beyanı 2026-09-20). Eski sürüm dizinidir; `.gitmodules` kaydı geçersiz, temizlenecek. Vault kapsamı dışında tutulur.
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
  - `backups/` 31.4 MB: pg_dump yedekleri. Politika: son 3 yedek tutma.
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

İki karar **çelişmiyor**, farklı katmanlara ait:

| Karar | Tanım | Katman | Anlamı |
|-------|-------|--------|--------|
| **D-172** | `worktree klasoru/` = yazma otoritesi | **YAZMA / SSOT** | Kod ve doküman **buraya yazılır**. Tüm değişiklik burada yapılır. Git worktree bağlı, orkestratör doğrudan çalışır. |
| **D-177** | GRAPH task ID + field schema = kanonik okuma | **GRAPH / CANONICAL** | Obsidian link çözümlemesi, orphan tespiti, backlink sayımı, task field tanımları **burada** kanonik. Kod dosyaları GRAPH'tan okur. |
| **D-191** | id-migration redirect (eski ID → yeni ID) | **MIGRATION / AUDIT** | Task ID yeniden adlandırılırsa eski ID silinmez; redirect trail + D-60 uyumlu geçiş kuralı uygulanır. |

**Kural:**
- `worktree klasoru/` = **yazma otoritesi (SSOT)** — kod, karar, görev burada değiştirilir.
- `Huginn Data Insights/` = **GRAPH canonical ağaç** — task ID/field schema'nın kanonik kaynağı; link çözümlemesi ve orphan tespiti buraya bağlıdır.
- **id-migration:** Eski task ID → yeni ID yönlendirmesi D-60 (kanonik ad geçişi) + D-189 (kök AGENTS.md kural taşımaz) ile uyumlu.

Pratikte: Kod/görev worktree'ye yazılır, senkronla HDI'a kopyalanır. GRAPH şeması HDI kopyasını esas alır (yazma/denetim için). Task ID değiştiğinde id_migration.py çalıştırılır → eski ID redirect'e çevrilir → wikilink'ler senkron kalır.

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
   - Her görev bitiminde `git add -A && git commit -m "<görev_özeti>"` ile commit et. Push'u tetik sisteminde veya oturum kapatılmadan önce yap.
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
| `ADMIN-KİT` | `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (v2.1) | 6           | §7 matris · §14 revizyon |

**`ADMIN-KİT` bağlı belgeleri (§0.1):** PRD kaynağı `Huginn Data Insights (HUGIns).txt` §889-1687 · V9 bağlam `01_versiyon_9_baglam_dokumani.md` §16.4/§16.5 · `docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md` · `03_mimari/06_muninn_prd_vs_huginn_analiz.md` (bayat) · `CHANGELOG.md` · görev panosu `data/orchestrator/ADMIN_PANEL_PLAN_VE_GOREV_PAKETLERI_2026-09-22.md`

**Yeni kit açma.** SSOT dosyasına statü bloğu + `§0.1` + ajan kuralı satırı yazılır, kısa ad seçilir, bu tabloya satır eklenir. Onay: KAHİN.
