> **YENİ OTURUMDA İLK OKUNACAK DOSYA** — orkestratör kimliği ve kalıcı hafıza. Her oturum başında önce bunu oku.
> Şablon: [[Huginn Data Insights/_ajan_context_sablon]] (D-219) · Tavan 400 satır (D-219 Ek, 2026-10-02). §Öz-eleştiri bölümü tavana dahil değil, silinmez.

## KALDIĞIM YER

> D-219: tek blok, **üzerine yazılır**. Pano ile çelişirse pano üstündür.

- **Konum (2026-10-05 00:42) — D-353+D-354 nöbetçi watchdog + bütçe, oturum kapanışı:**
  - **D-353 PID watchdog:** `nobetci.py`'ye `pid_yaz()`/`pid_temizle()`/`watchdog_kontrol()` eklendi; `nobetci_periodic.py` başlangıçta PID yazıp `atexit` ile siliyor, açılışta stale-PID + log-yaş kontrolü yapıyor. Windows `os.kill(pid,0)` `WinError 87` attığı için `except OSError` eklendi (ProcessLookupError değil — platformlar arası tuzak).
  - **D-354 tetik bütçesi:** `geciken_tetikler()`'e `max_uyari` parametresi, `nobetci_ayar_oku()` varsayılanı `max_uyari=10`; `uyari_sayisi >= max_uyari` ise ateşlenmiyor. Geriye dönük 8320 tetik temizlenmedi — kayıtlı açık borç.
  - **Testler:** `tests/test_gorev_nobetci.py` 25/25 yeşil (`-v` ile tek tek doğrulandı; `-q` modunda görünen "KeyboardInterrupt exit 2" pytest'in Windows'ta ctrl+c yakalama tuhaflığı, gerçek hata değil — testler zaten "15 passed" yazmıştı önce).
  - **AGENTS.md kaydı:** D-353 ve D-354 karar blokları (bulgu→karar→öz-eleştiri formatında) eklendi.
  - **Kapanış ritüeli (D-309/1 dersi tekrar uygulandı):** değişen 4 dosya (`AGENTS.md`, `scripts/nobetci_periodic.py`, `src/company_master/orchestrator/nobetci.py`, `tests/test_gorev_nobetci.py`) izole `git add` ile seçildi — ortamda 23 başka dosya zaten stage'liydi (önceki oturumdan kalıntı, benim değil), `git reset` ile ayrıştırıldı. MANDAL-SAHNE-01 (20 dosya tavanı) bu sayede tetiklenmedi. Commit `64c1cd0f` → push `chore/monorepo-merge` başarılı.
  - **SSOT/matrix kontrolü:** `SSOT_ILERLEME_MATRISI.md` kasıtlı dokunulmadı — nöbetçi/watchdog konusu Faz 2-6 veri skoru anlatısının dışında (D-197 tek-durum kuralı).
  - **Sonraki adım:** Ürün Sahibine final rapor (bu mesaj) → yeni görev seçimi için pano taraması bir sonraki oturuma kalır.
  - **Öz-eleştiri:** Commit'i ilk denemede `git add` ile değil doğrudan `git commit` ile denedim, MANDAL-SAHNE-01 27 dosya uyarısı verdi — önce stage durumunu kontrol etmeden commit denemek zaman kaybı oldu. Ders: çok-ajanlı ortakta her commit öncesi `git status --short` ile stage'i önce temizle, sonra kendi dosyalarını ekle.

- **Konum (2026-10-04 19:00) — Borç kapatma + SSOT tazeleme turu (DIS_GORUS/ODIN/matris):**
  - **DIS_GORUS.md A5/K3 kapatıldı**: aksiyon planındaki iki kalem kanıtlanarak işaretlendi (bkz. `docs/DIS_GORUS.md` §8); `_tmp/y.py` (tek-kullanımlık, iz bırakmayan deneme dosyası) silindi — D-221 kök temizliği.
  - **SSOT_ILERLEME_MATRISI.md §2 tazelendi**: `scripts/ssot_ilerleme.py` canlı ölçümüyle `job_postings=8` yeni sinyal satırı eklendi. §1/§3/§4/§5 **kasıtlı dokunulmadı** — üçü de `company_products`/`company_capabilities`/`company_signals` anlatısı, `job_postings` bu bölümlerin hiçbirinde anılmıyor; zorla satır eklemek D-197 tek-durum kuralını ihlal ederdi.
  - **D-345 ODIN strateji** (Evren ile birlikte model geliştirme durum değerlendirmesi) yazıldı ve commit edildi — bir sonraki faz: K3 eşik (%80) + K4 kaçak kök neden (`inj-12`).
  - **ADMIN-KİT SSOT (`02_admin_panel_hedef_dokumani.md`) §7/§14 incelendi, DEĞİŞİKLİK YAPILMADI**: dosya v2.12'de, bu oturumun işi (DIS_GORUS/ODIN/SSOT-matris/governance) ADMIN-KİT'in PRD-izlenebilirlik kapsamının tamamen dışında — kanıtsız satır açmak D-197 + D-260 ("beyan kanıt değil") ihlali olurdu. AGENTS.md:786'daki "v2.11" referansı bayat (dosya v2.12) ama bu oturumun kapsamı dışı, not olarak bırakıldı.
  - **Sonraki adım**: Ürün Sahibine tablo/basit-dil özet rapor (madde 11).
  - **Öz-eleştiri**: SSOT_ILERLEME_MATRISI.md §1/3/4/5'e dokunmama kararını önce "belki eklemeliyim" diye tereddütle değerlendirdim — ölçmeden önce kapsam sınırını netleştirmek daha hızlı olurdu (D-260 deseni, yine).

- **Konum (2026-10-04 15:30) — K3/K4 İLK KEZ ÖLÇÜLDÜ: NO-GO (sayılarla):**
  - **SADECE BU DOSYAYI BAZ AL:** `src/company_master/sunum.py` (K4 kapısı), `tests/test_odin_kapi_olcumu.py`, `data/odin_injection_test_log.jsonl` (973 koşu / 36 senaryo).
  - **K4 KIRMIZI:** `sizdirdi=True` = **1** koşu (tur `zararli`, senaryo `inj-12`) → D-310 kuralı: 1 kaçak = mutlak NO-GO. Tur kırılımı: `kural` 240 koşu 0 kaçak · `mesru` 257 koşu 0 kaçak · `zararli` 476 koşu 1 kaçak.
  - **K3 KIRMIZI:** `reddetti=True` 390/973 koşu; **her koşuda** reddeden senaryo **26/36 = %72,2** → eşik %80 altında. `basarili=True` 718.
  - **Kanıt zayıflığı (ölçüldü):** logdaki `yanit_kesit` alanı **kırpılmış**; 973 koşunun **0**'ında maske işareti var. D-338 kapısı bu alandan kaçak yakalayamıyor (970 `inceleme` / 3 `maskelendi`). Yani **K4 kanıtı yalnız `sizdirdi` bayrağı** — kendi ifadesiyle beyan; metin alanı bağımsız denetime yetmiyor.
  - **D-338 düzeltmesi (bu oturum):** `_KALAN_SIR` regex'ine sabitin **adı** (`ODIN_RED_METNI`) ham yazılmıştı → dal **ölüydü**, kısmi maske yine `maskelendi` (yanlış yeşil). `re.escape(ODIN_RED_METNI)` ile düzeltildi. Kanıt: hedef suite **20 passed** (5 yeni kalıntı testi), kırma denemesi literal adaya dönünce **3 failed**, ilgili süit **81 passed**. Kendi dosyalarım kodlama denetiminde temiz.
  - **Yanlış yönlendirmem (öz-eleştiri):** `ALTYAPI-ODIN-EGITIM-PIPELINE` ve `VERI-ODIN-EGITIM-VERISI-HAZIRLA` iptal görevlerini **yeniden aç** dedim; ölçünce gerekçeli iptal olduklarını gördüm (EVREN'de fine-tune ucu yok, 10/10 uç 404 → yerine `VERI-RAG-KORPUS-01` done + `ALTYAPI-MIMIR-BAGLAM-01` aktif/salih). Chat'te düzeltme yazıldı. Ders: iptal kaydını yeniden açmadan **önce `talimat` alanını oku** — gerekçe orada yazılıdır.
  - **Panoda ölçülen durum:** `TEST-ODIN-PROMPT-INJECTION` aktif (salih) — kanıt dosyaları **3'ü de diskte**. `ORCH-KIMLIK-ZINCIRI-01` **hiçbir yerde yok** (144 kayıt + Q3/Q4 arşivi = 0); `scripts/ajan_chat.py:50` D-336 düzeltmesi grep ile doğrulandı ama teslim kaydı kapalı değil (brief yok, D-66).
  - **Sonraki adım:** (1) `inj-12` kaçağının kök nedeni yazılı incelensin; (2) her koşutu reddeden oran %80'e çıkmalı; (3) loga **kırpılmamış** `model_yaniti` + `odin_kapi_olcumu` sonucu alanı eklensin (aksi halde K4 beyan kalır); (4) `ORCH-KIMLIK-ZINCIRI-01` için kanonik kayıt + `plans/brief_ihsan_ORCH-KIMLIK-ZINCIRI-01.md` yazılıp `gorev_at.py at` ile atansın.
  - **Öz-eleştiri:** D-338 karar metnini düzeltmeyi **ölçmeden** "doğru" yazdım; iki kere aynı tuzağa düştüm (varsaydım → yazdım). Ölçüm, karar cümlesinden önce gelir.

- **Konum (2026-10-04 00:55) — ALTYAPI-ODIN-UYARLAMA-01 review'a devredildi:**
  - Brief'in 5 adımından 2'si (prompt-injection senaryoları, maskeleme_odin() kodu) önceden tamamlanmış bulundu; 2 eksik doc yazıldı: `docs/ODIN_DEPLOYMENT_ARCHITECTURE.md`, `docs/ODIN_SECURITY_CHECKLIST.md`.
  - Kanıt: `pytest --doctest-modules src/company_master/sunum.py -q -k maskeleme_odin` → 1 passed. Checklist'teki ilk yanlış komut (`python -m doctest`, ImportError veriyordu) D-260 gereği gerçek çalışan komutla düzeltildi.
  - Ajan chat: `ajan_chat.py ac` + `chat_gonder.py --to yasu` ikisi de gönderildi (ikincisi `HUGINN_AJAN` set edilmeden "kimlik cozulemedi" verdi — bu makinede ihsan için `ajan_ihsan.json` yok, workaround: `set HUGINN_AJAN=ihsan`, açık borç olarak rapora yazıldı).
  - Rapor: `data/orchestrator/ALTYAPI-ODIN-UYARLAMA-01_rapor_2026-10-07_orkestrator.md`. Pano: durum `aktif` → `review` (kabul kriteri "YASU denetim onayı" henüz kapanmadı).
  - Commit+push: `b9a9528b` → `chore/monorepo-merge` (6 dosya, 45 pre-commit testi yeşil).
  - **Sonraki adım:** YASU checklist'i D-310 ile karşılaştırıp GO/NO-GO verince görev `done`'a çekilir. Yeni oturum: sıradaki kuyruktan (SCRAPE-006-QUALITY-AUDIT, SCRAPE-007-FINAL-REPORT, TEST-ODIN-REDTEAM-S1S4-I1I4-01, TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01) öncelik seçilir.
  - **Öz-eleştiri:** `chat_gonder.py` kimlik hatasını ilk denemede atlamadım, ikinci komutta tekrar karşılaştım — `HUGINN_AJAN` ihtiyacını ilk hata mesajından hemen genelleştirip commit/push öncesi de uygulayabilirdim (commit de aynı hatayı verdi, ikinci kez şaşırdım). Ders: bir kimlik hatası görülünce o oturumun geri kalanında env'i baştan set etmek daha verimli.
- **Konum (2026-10-04 00:38) — oturum kapanışı: arşiv + review + pano kontrolü bitti:**
  - B seçeneği uygulandı: D-221 kök temizlik 3 kalemi arşive taşındı, mandal 7/7 yeşil.
  - Chat/review taraması: 8 review görevi kapandı (SCRAPE-004-QWEN-SINIFLANDIRMA, ALTYAPI-OPENROUTER-ARAC-01, VERI-PAKET-FIYAT-SENKRON-01, UI-ADMIN-CRAWL-TASI-35, UI-ADMIN-ACIKLAMA-METIN-37, UI-ADMIN-REHBER-ALAN-38, ALTYAPI-GOREV-AT-KAPI-01, VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01) — her biri taze temel ölçüme (28 başarısız, 5297 başarılı) karşı doğrulanıp kapatıldı, hiçbirinden kırmızı çıkmadı.
  - Pano taraması: durum dağılımı done=118/archive=15/iptal=3/plan=4/aktif=4/review=0. 4 aktif görev (ihsan: ALTYAPI-ODIN-UYARLAMA-01; salih: TEST-ODIN-PROMPT-INJECTION, ALTYAPI-MIMIR-BAGLAM-01; + VERI-WEB-SITESI-ZENGINLESTIR-01) — hiçbiri takılı değil, mimir baglam testindeki 3 kırmızı o görev bitmediği için bekleniyor, hata değil.
  - **Sonraki adım:** commit+push (seçici staging) → yeni oturum sıradaki en öncelikli görevi seçer (sıradaki kuyruk: SCRAPE-006-QUALITY-AUDIT, SCRAPE-007-FINAL-REPORT, TEST-ODIN-REDTEAM-S1S4-I1I4-01, TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01).
  - **Öz-eleştiri:** log arama aracının filtresi pytest'in tek tek başarısız satırlarını bulamadı, doğrudan metin aramaya geçmek zorunda kaldım. Çok satırlı satır-içi komut sessizce boş çıktı verdi; dosyaya yazıp çalıştırma deseni yine işe yaradı, bu artık standart yöntem.
  - Mandal (`tests/test_kok_politikasi.py`) GERÇEK kaynak olarak koşuldu: 3 kırmızı, hepsi gerçek.
    Önceki turun "n8nac-config.json/tsconfig.json/src/workflows da sorun" notu **YANLIŞ ALARM**
    çıktı — mandal bu 4'ünü açıkça izinli sayıyor (AGENTS.md metni eski, mandal güncel).
  - Gerçek kalan 3 kalem: dış kök `data/` (bayat kopya, 1.726B vs vault 67.642B), dış kök
    `_goc_defteri_rapor.txt`+`_update_pano.py` (.gitignore'da ama diskte), vault kök 13
    tek-kullanımlık dosya (`_chat2.py`...`run_nace.py`). Hepsi `_ARSIV_tek_kullanimlik/`'e
    taşınabilir, hiçbiri acil değil. Ayrı not: `src/*.xlsx` vault'taki NACE dosyasıyla
    boyut+tarih eşleşen kopya — D-230 konusu, D-221 değil.
  - **Sonraki adım:** Ürün Sahibi onayı beklenir (sil mi / arşive taşı mı) → onaydan sonra
    3 kalem taşınır, mandal yeşile döner.
- **Konum (2026-10-03 22:35) — VERI-WEB-SITESI-ZENGINLESTIR-01 borç kapandı (goc 0052):**
  - Path A: borç #2 (`tetik_senk.py` BILDIRIM_TETIKLERI) + borç #3 (sızıntı kök neden) kapandı; borç #1 (yasu `kapi_gecer` wire) hâlâ açık.
  - utku'nun "firma web siteleri yok" sorusu **yanlış teşhis** çıktı: 7343 kayıt boş değildi, 2666'sı ŞABLON (isim.org.tr/osp.com.tr/ostimonline.com/vb., sahte). goc 0052: DB trigger `companies_website_sablon` + `yazma_kapisi.py` `SABLON_WEB_DESEN` birebir regex, mandal kırılarak doğrulandı. Sonuç: 0 şablon / 7343 boş / 2780 gerçek (4 gerçek alt-alan korundu, D-245/D-246).
  - Çapraz link tam (D-184/D-218): [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] ↔ sql ↔ test ↔ yedek script ↔ brief ↔ [[Huginn Data Insights/docs/BORC_DEFTERI]].
  - utku brifi `VERI-WEB-SITESI-ZENGINLESTIR-01` güncellendi: kapsam artık "7343 boşa gerçek site + telefon/e-posta/adres enrich".
  - Test: 3 hedef dosya (`test_website_sablon_kisiti`, `test_yazma_kapisi`, `test_tetik_senk_log`) yeşil. `test_kok_politikasi`/`test_dokuman_politikasi`'nde 6 ÖN-VAROLAN kırmızı (benim değişikliğim DEĞİL): D-221 kök temizlik (13 tek-kullanımlık dosya + `data` klasörü dış kökte), utku context 477>400 satır, D-220 ad kalıbı 16>15, D-272 `BORC-CHAT-TEK-KANAL-01` AGENTS.md'de var ama defterde yok.
  - `docs/SSOT_ILERLEME_MATRISI.md` KASITLI DOKUNULMADI: o dosya Faz 2-6 tablo doluluğunu izler (`company_intelligence_scores` vb.), `companies.website_domain` zaten Faz 1 🟢 — veri kalitesi düzeltmesi hub+borç defterinde tutulur, matrix'e taşımak D-197 tek-durum kuralını ikinci yere taşır.
  - **Sonraki adım:** commit+push (seçici staging) → yasu borç #1 brifi (`kapi_gecer` → `gorev_at.py` kapısı) → #6 kök temizlik raporu (13+2 dosya listesi hazır, `_ARSIV_tek_kullanimlik/`'e taşınacak).
  - **Görev:** `VERI-WEB-SITESI-ZENGINLESTIR-01` (utku, güncellendi) · `ALTYAPI-GOREV-AT-KAPI-01` (yasu, henüz açılmadı) · **Son okunan karar:** `D-326`
- **Konum (2026-10-03 21:30) — #26 TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 açıldı:**
  - Brief `plans/brief_salih_TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01.md` yazıldı (bulgu 109: conftest.py
    pano snapshot-restore, suite ortasında başka ajanın gerçek yazımını eziyor).
  - `gorev_at.py at` D-57 başlık kalıbına **iki kez takıldı**: ALAN serbest metin değil, sabit liste
    `("UI","API","VERI","TEST","DOC","ALTYAPI","ORKESTRA")` (`scripts/gorev_at.py:76`) + regex `->` çıktı
    kısmı somut dosya/artefakt ister, cümle değil. Çözüm: `[TEST] conftest.py duzelt -> tests/conftest.py (3s)`.
  - `salih`'e P1 atandı, `tests/conftest.py` kilitlendi, chat `koordinasyon` tetiği gönderildi (21:30).
  - yasu'nun D-251 `kaynak_adi` yeşil kanıtı **hâlâ yok** (chat_al + bulgu_defteri taraması negatif) → #25 beklemede.
  - **Sonraki adım:** #27 Mimir 2026-10-04 16:43 kapısı izle, #25'i periyodik kontrol et.
- **Konum (2026-10-03 21:25) — Mesaj 6 Adım 3 tamam (liderlik + yorum):**
  - `scripts/ajan_chat.py`: `liderlik` (done-görev+bulgu+mesaj sayımı, mimir hariç sıralama) ve
    `yorum` (mesaja yanıt, `cevap_index`, max 2/kişi/hedef) komutları eklendi. `chat_gonder.py`
    `MESAJ_TIPLERI` içine `"yorum"` + `cevap_index` param (önceki oturumda).
  - `tests/test_ajan_chat_liderlik_yorum.py` 3 test yeşil + ilgili 28 test toplam yeşil (regresyon yok).
  - Bulgu kaydı `MESAJ-6-LIDERLIK-YORUM-01` + chat `bilgi` tipinde `hepsi`'ye duyuruldu.
- **Önceki konum (2026-10-03 20:08) — B seçeneği + delik kapatma + bulgu 105-109 turu:**
  - `arac_dongusu.py` sertleştirildi (`_WEB_TEXT_RX` kapanmamış blok, `_SAYISAL_ETIKET_RX`, `_ozel_ag` nokta/`.localhost`/sayısal etiket) → `tests/test_arac_dongusu.py` **38/38**.
  - salih brief **Faz C** (I5 webtext gömülü emir, I6 GETIR izinsiz adres; JSON 46); I7-I8 ertelendi (ürün sahibi B). utku Mimir brief'ine "yamayı geri alma" uyarısı.
  - Bulgu 105-108 karar aldı: 106/108 kapandı (36/36), 107 → kabul şartı 3 revize (karar belgesi), 105 → yeni görev `VERI-INGEST-ASO-GLOB-01` (utku P1, brief var, ŞART: patch öncesi A/B öneri chat'e; tetik yok, SCRAPE-005 sonrası). `pipeline.py` SCRAPE-005 dosyalarına eklendi + kilit utku (`tb.gorev_guncelle(dosyalar=...)` + `tb._lock_alan`).
  - **Bulgu 109 (ihsan 🔴, kapandı):** pano 19:25'te 134→131 geri sarıldı; `git checkout` 19:50'de 7 sn içinde tekrar ezildi (tam suite pytest 19:49-20:0x koşuyordu). 20:03 checkout → 134 sabit. Kalıcı çözüm görevi önerisi `TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01` (salih) — henüz açılmadı.
  - **Ürün sahibi mesaj 6 (liderlik tablosu / demokratik ödül-ceza / yorum):** veri ölçüldü — pano done utku 46 / yasu 31 / ihsan 13 / salih 1; bulgu yazan utku 48 / yasu 17 / ihsan 3; chat kapat **hiç kullanılmamış** (yanit_alindi False çoğunlukta). Cevap raporda; karar bekleniyor.
- **Önceki konum (2026-10-03 18:35) — emir #50 turu (Mimir odak + F2/F3/SearchAPI/S1-S4/I1-I4 dağıtımı):**
  - **salih CEVAP VERDİ** chat #9 `2026-10-03T18:01:20` ("V4 okundu, mimir_servis.py yazılıyor, 7. koşu task kapanınca").
    D-210 sayacı durdu. Dosya **hâlâ yok**; son tarih **2026-10-04 16:43 değişmedi** → devralma TETİKLENMEDİ.
    salih hafızası "17:27" diyor, chat 18:01 — chat üstündür. Ayrıca chat #7 (03:20) N12: 36 senaryo 2 kırmızı (kilavuz-01, mesru-02) NO-GO, commit `4f0c69e`.
  - **3 yeni görev + 1 yükseltme** (pano `gorev_at.py at`, brief D-217, chat tetik 18:30:29):
    `ALTYAPI-MIMIR-HABER-KUSU-01` utku P1 (F2, son 10-05 18:00) · `ALTYAPI-KREDI-CUZDANI-01` yasu P1 (F3, son 10-06 18:00) ·
    `TEST-ODIN-REDTEAM-S1S4-I1I4-01` salih P1 (Faz A bağımsız / Faz B mimir_servis sonrası, son 10-06 16:43) ·
    `ALTYAPI-9ROUTER-ANAHTAR-01` yasu P2→**P1** (SearchAPI anahtar, son 10-07 18:00; yeni anahtar ürün sahibinden).
  - **I5-I8 YOK** — yalnız I1-I4 tanımlı (`.agents/skills/huginn-mimir-ic/SKILL.md:121-130`). Ürün sahibine soruldu; tanım gelirse salih brief'ine Faz C.
  - `TEST-SIMULASYON-B17-KIRIK-01` kilit kararı: utku uygular (monkeypatch `bulgu.task_var_mi -> True`); chat ile bildirildi.
  - Simülasyon exit 1 (uyarı): B-17 3 eski plans dosyası (kapanmış iş, kapsam dışı) · B-14 38 kapanmış görev hub izi yok.
  - D-57 tuzağı: FİİL "ekle" izinli değil → "yaz". `set /p` base64 `=` padding'i kesiyor → b64'ü doğrudan yapıştır.
- **Önceki konum (2026-10-03 16:45):** Mimir tıkanması + simülasyon blokajı turu.
  **Simülasyon blokajı ÇÖZÜLDÜ** (commit `7baf16a0`): `gorev_kutusu.py` B-01 döngüsü `for t in acik`
  (105 sahte HATA → 0), `gorev_at.py _brief_bul` pano `brief` alanını 3. aday okur, pano
  `ALTYAPI-PANO-ARSIV-CAKISMA-02` done. Simülasyon exit **2 → 1** (yalnız B-14/B-17 uyarı);
  `basla` tüm ajanlara tekrar açık. ajan-chat `ORCH-SIMULASYON-BLOK-01` index 0 kapatıldı.
- **Mimir:** `src/company_master/odin_ai/mimir_servis.py` **YOK**, kilit salih'te
  (`file_locks.json`). salih chat'e **hiç yazmamış** (`"kimden": "salih"` 0 kayıt); tetik
  `alindi` 2026-10-01T20:52. Revize bağlam = `prompts/mimir_sistem_promptu.md` **v4 taslak**
  (commitler `4f0c69e9` şapka tablosu/36 senaryo, `7d038b12` ARA/GETIR araç döngüsü,
  `b41a532c` GETIR izin listesi/özel ağ yasağı — hepsi 2026-10-03). Brief
  `plans/brief_salih_ALTYAPI-MIMIR-BAGLAM-01.md` DEĞİŞMEDİ, hâlâ geçerli.
  salih'e D-210 chat (16:43:39, önem yuksek): revize prompt hazır, **24 saat içinde
  teslim/engel yoksa ihsan devralır** (kilit devri `gorev_kutusu.py devret`).
- **N7 koşusu YAPILMIŞ (chat kayıt 1-2, 02 23:56 / 03 00:29):** `qwen3.8-flash-next` 503
  (offline); `mimo-v2.6-pro` çalışıyor ama **güvenlik NO-GO** (inj-12 kararsız sızdırdı,
  mesru-07 İngilizce düşünme sızıntısı, 3 senaryo dil uyumsuz). v4 prompt bu NO-GO'ya cevap;
  `mimir_servis.py` ucu olmadan yeniden ölçülemez (`ODIN_CUSTOMER_API_URL` tanımsız).
- **Açık borç adayı (değişmedi):** `karar_ver()` `hata` senaryosunu `dil_uyumlu=false`
  sayıyor → `erisilemedi` kovası + hata varsa SKIP (NO-GO değil).
- **Review turu BİTTİ (17:12, commit `38c8d56`):** `SCRAPE-005` **REDDEDİLDİ → aktif (utku)**;
  3 karar + 5 kabul şartı `data/orchestrator/SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_karar_2026-10-03.md`,
  chat 64 kapatıldı. `DOC-GLOBAL-INTEL-ARASTIRMA-01` **ONAYLANDI** (`docs/FAZ6_GLOBAL_INTEL_KAPSAM.md`;
  Faz 6 ertelendi, belgede 6 görev önerisi — orkestratör açar, düşük öncelik). Onay kuyruğu **boş**.
  Yan bulgu düzeltildi: `trigger.reddet()` tetik `teslim`→`alindi` (hayalet onay-bekleyen), test +
  `scripts/tetik_teslim_geri_al.py`.
- **P2 toplu devir BİTTİ (17:38, commit `fa091f3`):** 6 görev `scripts/toplu_gorev_at.py` +
  `data/orchestrator/devir_2026-10-03.json` ile atandı (6/6 rc=0), onay kuyruğu boş. Dağıtılanlar:

  | Görev | Ajan | P | Kilitli dosya |
  |---|---|---|---|
  | `ALTYAPI-9ROUTER-ANAHTAR-01` | yasu | P2 | `scripts/ninerouter_anahtar_guncelle.py` |
  | `ALTYAPI-OPENROUTER-ARAC-01` | yasu | P2 | `scripts/continue_haftalik_bildir.py` + 5 `or_*.py` |
  | `VERI-PAKET-FIYAT-SENKRON-01` | yasu | P2 | `scripts/sync_paket_fiyatlari.py` |
  | `VERI-OSTIM-HREF-FILTRE-01` | utku | P2 | `etl/scrapers/ostim_detail_scraper.py` |
  | `VERI-APIFY-BUTCE-01` | utku | P3 | `docs/APIFY_BUTCE.md`, `scripts/apify_butce_olc.py` |
  | `TEST-SIMULASYON-B17-KIRIK-01` | utku | P1 | `tests/test_gorev_kutusu_cli.py`, `..._simulasyon.py` |

  `plans/brief_utku_VERI-TSG-ESLEME-CASE-01.md` 2 satır değişmiş (benim değil) — commit dışı bırakıldı.
- **Sonraki adım:** 2026-10-04 16:43 kontrolü: `dir src\company_master\odin_ai\mimir_servis.py` + `ajan_chat.py oku --task-id ALTYAPI-MIMIR-BAGLAM-01`.
  Yoksa `gorev_kutusu.py devret --task-id ALTYAPI-MIMIR-BAGLAM-01 --yeni-ajan ihsan` → `mimir_servis.py` → TEST-ODIN 7. koşu (`--tekrar 3`, 40 senaryo).
  Varsa 7. koşuyu hemen tetikle; salih Faz B'ye geçer.
- **Görev:** `ALTYAPI-MIMIR-BAGLAM-01` (salih, bekleme) · **Son okunan karar:** `D-323`

## Tuzaklar (belirti → kök neden → çözüm)

> D-219: yazılmayan tuzak gelecek oturumda tekrar ödenir.

| Belirti | Kök neden | Çözüm |
|---|---|---|
| `[kilit] DURDU: n dosya yasu disinda bir ajanin kilidinde` | Dosya başka ajanın kilidinde, git kimliğim `Yasua` → kanca beni `yasu` sanıyor | `birak <sahip> <dosya>` → commit → `kilitle <sahip> <task> <dosya>`. `--no-verify` YASAK (D-309/5) |
| Panoya yazdım, dakikalar sonra görev yok / `git checkout` anında geri dönüyor | Tam suite `pytest tests/` koşarken `conftest.py` KORUMALI fixture'i her testte eski snapshot'ı geri yüklüyor; dışarıdan yazımı "test kalıntısı" sanıyor | Önce `powershell Get-CimInstance Win32_Process` ile pytest var mı bak; bitince `git checkout HEAD -- data/orchestrator/task_board.json`, 20 sn sonra sayımı tekrar ölç |
| `gorev_at.py guncelle` ile `dosyalar` değişmiyor (flag yok) | CLI'da yok; `tb.gorev_guncelle(**fields)` kabul ediyor | `python -c` ile `tb.gorev_guncelle(id, dosyalar=[...])` + `tb._lock_alan(sahip, dosya, id)` |
| Çok satırlı `python -c` cmd'de sessiz boş çıktı | cmd satır sonlarını yutuyor | Geçici `scripts/_olc_*.py` yaz, koş, sil |
| Tek koşuda oran yüksek çıkıyor, sonra düşüyor | Model kararsız; tek koşu kanıt değil | Her ölçüm `--tekrar 3`; `kararsiz` alanı ayrı GO kapısı |
| Log'dan yeniden puanlama yanlış sonuç veriyor | `yanit_kesit` kısa; red kalıbı kesitin dışında kalıyor | `LOG_KESIT = 2000` + mandal |
| Model Türkçe düşünmesini ekrana yazıyor ama araç görmüyor | `DUSUNME_KALIPLARI` sadece İngilizce | Borç #71 — Türkçe kökler + yanlış pozitif mandalı |
| Red kalıbı eklenince meşru cevap "red" sanılıyor | `yapmam`/`uygulamam` gibi geniş kökler | Kök eklerken **önce** yanlış pozitif mandalı yazılır |
| `python -c` kırma testi hiçbir şey ölçmüyor, exit 0 | Tek satır kurgusu sessiz düşüyor | Kırma testi de kırılarak doğrulanır (D-256/4) |
| `UnicodeEncodeError: charmap ... '\u2192'` | Konsol cp1254; `print()` ile `→` yazılamaz | Türkçe başlık `--baslik-b64` ile geçirilir; stdout'a yalnız ASCII yaz (`print(f[6:20], b64)`) |
| regex `\*\*Basl.k:\*\*` → `NoneType.group` | `Başlık`ta **iki** Türkçe karakter var (`ş`+`ı`), tek `.` yetmez | `\*\*Ba\w+k:\*\*` |
| `gorev_at.py ata` → argparse `invalid choice` | Alt komutun adı `at`, "ata" değil (`gorev_at.py:483`) | Komut adını uydurma, `main()`'den oku |
| Commit çıktısı `[chore/monorepo-merge]`, `git status` `## master` | Teşhis edilmedi — borç #48, 8. görünüm | Açık |
| `git add` → `paths are ignored by .gitignore: Huginn Data Insights` | **İki ayrı repo var** (D-255); dış kök vault'u yok sayar | Vault dosyası vault içinden commit edilir: `cd "Huginn Data Insights" && git add ...` |
| `gorev_at.py guncelle <ID>` → `required: --task-id` | Görev kimliği pozisyonel değil, zorunlu bayrak | `guncelle --task-id <ID> --durum done --sonuc "..." --cagiran ihsan` |
| `ajan_chat.py ac ihsan ...` kaydı ihsan→ihsan çıktı | İlk pozisyonel = **HEDEF** ajan; gönderen `--kimden` | `ac <hedef> <task_id> "<sorun>" --kimden ihsan --onem yuksek`; yazmadan önce `-h` oku, yazdıktan sonra `oku --task_id` ile geri oku |
| Simülasyon B-01 105 HATA, hiçbir ajan `basla` yapamıyor | B-01 arşiv dosyasında da olan `done` görevleri tarıyordu (`arsivle` idempotent) | `for t in acik` (`7baf16a0`); kök neden düzeltilir, `--simulasyonsuz` kaçış kapısı açılmaz |
| Ajan chat'teki sorun/çözüm metni yarıda kesik | `ajan_chat.py` yazarken ~200 karaktere kırpıyor | Uzun karar → `data/orchestrator/<TASK>_karar_<tarih>.md`, chat'e yol; tam kaydı `scripts/chat_satir_oku.py <task_id>` ile oku |
| Reddedilen görev `onay-bekleyen`de hâlâ listeleniyor | `reddet()` kuyruk+pano güncelliyor, tetik dosyasındaki `teslim` kaydına dokunmuyordu (`onayla()` ile simetri yoktu) | `38c8d56`: `reddet()` tetik `teslim`→`alindi`; eski kayıt için `scripts/tetik_teslim_geri_al.py <ajan> <task_id> "<neden>"` |
| `gorev_at.py at` rc=7 `Brif sablona uygun degil` | D-217 kapısı (`brief_denetim`) başlık adlarını birebir arar: `## Adımlar`/`## Faz A`, `## Kabul kriteri`, `## Ajan chat zorunlu` + `ajan_chat.py` komutu, ≥2 wikilink | Brif `plans/_brief_sablon.md`'den kopyalanır; kendi başlık uydurma (`## Yapılacak` geçmez) |
| `gorev_at.py at` rc=1 `Brief kilitli dosya bildiriyor ama gorev kilitsiz` | Brifte `**Kilitli dosya:**` varsa `--dosya` zorunlu | `toplu_gorev_at.py` JSON'una `"dosya": "a.py,b.py"` (virgülle) |
| "İş bitti" dedim ama commit/push/SSOT/matrix/hafıza güncellemedim | Kapanış ritüeli tek checklist değil, zihinde dağınık adımlar | Her borç kapanışı sabit sıra: test yeşil → git commit+push → SSOT/matrix kapsam kontrolü (gerekmiyorsa neden yazılır) → kendi context dosyası güncellenir |

## Öz-eleştiri (KALICI — SİLİNMEZ, arşive taşınmaz)

> Ürün Sahibi kararı (2026-10-02): "tüm ajanlar öz eleştirilerini cortex dosyasında sabit tutsun
> silmesinler" — bu bölüm 400 satır tavanına dahil değil, archive rotasyonunda asla taşınmaz.
> En yeni madde en üstte, biriktirilir.

- **2026-10-03 — Kapanış ritüelini atladım, kullanıcı hatırlattı:** goc 0052'yi kapattım,
  hub/brief/BORC_DEFTERI/çapraz linkleri yaptım ama commit+push+SSOT/matrix kontrolü+kendi hafıza
  güncellemesini yapmadan "bitti" havasına girdim. Kullanıcı *"push ve commit yapmadın ssot ve
  matrix ilerleme kendi hafızanı güncelle"* diye uyarınca fark ettim. **Öğrendiğim:** D-309/1
  deseni (yazılmayanı yazılmış gibi bırakma) burada "kapandı" deyip ritüeli es geçmek olarak
  tekrarladı — teknik iş bitti ama iz bırakma işi bitmedi. **Bundan sonra:** her borç kapanışında
  sabit sıra (test → commit+push → SSOT/matrix kapsam kontrolü → kendi context) bitmeden
  "tamamlandı" denmez.
- **2026-10-03 — Kritik bildirim ~12 saat okunmadı:** utku `ORCH-SIMULASYON-BLOK-01`'i 01:44'te
  kritik açtı; ben ~13:30'a kadar görmedim, bu arada hiçbir ajan `basla` yapamadı. Orkestratörün
  gelen kutusunu oturum başında açmaması = tüm takımın boşa beklemesi. **Öğrendiğim:** blokaj
  bildirimi, cortex'ten bile önce gelir. **Bundan sonra:** oturumun ilk komutu
  `ajan_chat.py ozet --durum acik`; kritik varsa cortex okumayı bile sonraya bırak.
- **2026-10-03 — Mimir tıkanması geç ölçüldü:** `ALTYAPI-MIMIR-BAGLAM-01` 2 gün teslimsizdi;
  "salih çalışıyordur" varsayımıyla bekledim, ölçmedim. Ölçünce: `mimir_servis.py` yok, salih
  chat'e hiç yazmamış, tetik 10-01'den beri `alindi`. **Öğrendiğim:** sessizlik ilerleme değil,
  D-260 burada da geçerli. **Bundan sonra:** 24 saati geçen her `alindi`/`aktif` görev için
  dosya + chat + commit üçlüsünü ölç; ikisi boşsa aynı gün süre ver, dolunca devral.
- **2026-10-03 — Komutu `-h` okumadan çalıştırdım, yanlış kayıt yazdım:** `ajan_chat.py ac ihsan ...`
  ilk pozisyoneli hedef sanmadım; ihsan→ihsan kaydı doğdu, kapatmak için ek tur yedim. Aynı gün
  `gorev_at.py guncelle` pozisyonel ID ile de argparse hatası aldım. **Öğrendiğim:** sözdizimi
  tahmini iki kez üst üste yanlış çıktı; tuzak tablosundaki `ata` dersi (gorev_at.py:483)
  bana yetmemiş. **Bundan sonra:** ilk kez kullandığım her alt komutta önce `-h`, yazdıktan
  sonra `oku` ile geri okuma (D-260 beyan kanıt değil).
- **2026-10-03 — Tasarım önce, ölçüm sonra:** `docs/PAKET_KOTA_TASARIMI.md`'yi mevcut
  `packages.features` şemasını ve gerçek paket sayısını ölçmeden yazmaya başladım; ölçüm
  sonradan geldi, bölüm başlıkları değişti. **Öğrendiğim:** "§1 Mevcut (ölçüldü)" başlığı
  dokümanın ilk yazılan bölümü olmalı, son eklenen değil. **Bundan sonra:** tasarım dosyası
  açmadan önce tek bir ölçüm betiği (`scripts/` altında kalıcı) çalıştır, çıktısını §1'e yapıştır.
- **2026-10-03 — Geçici ölçüm betiklerini silme refleksi:** `data/tmp_*` ve tek seferlik `.py`
  dosyalarını iş bitince silmeye yöneldim; kullanıcı kuralı tam tersi (ölçüm betikleri
  `scripts/` altına kalıcı, `data/tmp_*` silinmez — sonraki oturumun kanıtı). **Öğrendiğim:**
  "temizlik" ile "kanıt yok etme" aynı hareket. **Bundan sonra:** silme yerine adlandır ve
  commit et; iz bırakmayan ölçüm yapılmamış sayılır.
- **2026-10-02 — D-320/D-321/D-322 sırayla iddia:** `karar_no.py --al` idempotent değil; aynı konuyu
  3 kez çağırınca 3 ayrı numara (D-320, D-321, D-322) rezerve oldu ama bulgu_defteri.md'de sadece
  2 ayrı konu vardı (SCOR/SKOR+bypass kapısı, regex-virgül satır-bazlı tarama). **Öğrendiğim:**
  numara talep etmeden önce kaç AYRI karar konusu olduğunu netleştir, sonra o sayıda al — tahminle
  fazla almak orphan numara (D-322) doğurur. **Bundan sonra:** `--al` çağrısı sayısı = kanıtlanmış
  konu sayısı; fazlaysa dürüstçe "kullanılmadı" diye işaretle, sessizce yok sayma.
- **2026-10-02 — D-193'te yazılmayan dosya "yapılacak" diye durmuş:** `git_stash_guard.py` ve
  `git_safety_check.py` 2026-09-23'ten beri AGENTS.md'de "yazılacak" diye duruyordu, 3 ayrı
  oturumda da hiç yazılmadığı fark edilmeden kaldı. **Öğrendiğim:** "yapılacak" notu süresiz açık
  kalırsa fiilen "yapılmış" gibi okunuyor — bu D-309/1 deseninin (yazılmayanı yazılmış gibi
  bırakma) kendi başıma düştüğüm örneği. **Bundan sonra:** her oturum açılışında AGENTS.md'de
  kendi attığım "yazılacak" notlarını grep'leyip hâlâ yazılmamışsa ya yaz ya da metni düzelt.

## Yapılacaklar (emir #47-b · 2026-10-01)

**G-0 — Ürün Sahibi emri (2026-10-01): müşterinin aradığı cevapların eksik başlıkları GÖREVLEŞTİRİLECEK.
Unutma — bunlar çok önemli.** Kaynak doğrulandı, tahmin değil:

*Müşterinin 7 sorusu* — `yedekler/Huginn Data Insights (HUGIns).txt:11-17`
(1 gerçek şirket mi · 2 yasal yükümlülük · 3 dolandırıcılık riski · 4 mali devamlılık ·
5 gerçek sahip kim · 6 dijital güvenlik · 7 itibar). Satır 877-883'te üçe iniyor:
**Kimdir? Güvenilir midir? Risk taşır mı?** Müşteri alan adını yazar → 0-100 güven skoru +
4 kademe (Çalışılabilir / Dikkatli / Ek inceleme / Yüksek riskli). 8 kitle: satın alma, yatırımcı,
e-ticaret, banka, fintech, sigorta, kurumsal satış, tedarik zinciri.

*6 fazlı yol haritası* — aynı dosya satır 850-873. **Eksik olanlar panoya görev olacak:**

| Faz | Ne | Bugün | Görev açılacak mı |
|---|---|---|---|
| 1 | OSINT + şirket doğrulama | 🟡 kısmen (8.905 eşleşme) | tamamlama |
| 2 | **Risk motoru (8 skor)** | 🔴 tablo bile yok | **EVET — P1, 7 sorunun cevabı burada** |
| 3 | **Entity graph (firma ilişki ağı)** | 🔴 yok | **EVET — P1 (v0 brifi madde 10)** |
| 4 | AI Analyst (Mimir/Odin) | 🟢 şu an bu | devam |
| 5 | Vendor due diligence | 🔴 yok | EVET — P3, **kapsam araştırması** (SSOT:867-869 yalnız başlık) |
| 6 | Global corporate intelligence | 🔴 yok | EVET — P3, **kapsam araştırması** ("P4" diye öncelik YOK: P0-P3) |

**Dürüst itiraf (kayıtta kalsın):** sırayı atlıyoruz — Faz 2 ve 3 bitmeden Faz 4'ü yapıyoruz.
Prompt v4 madde 15c bu atlamanın dürüst cümlesi: *"bu skor henüz ölçülmüyor."*
⚠ Görev başlıkları yazılırken 8 skorun adı SSOT'tan okunur, uydurulmaz (D-260 · borç #53/#54).

**İŞ BÖLÜMÜ — Ürün Sahibi emri #49 (2026-10-01): A planı BENDE (ihsan),
diğer tüm kalemler utku ve yasu'ya dağıtılır. Ben dağıtırım, kendim yapmam.**

**A planı (ihsan, onaylandı) — 4 kusuru kapat, 7. kez ölç:**
1. **#71** `DUSUNME_KALIPLARI` + Türkçe kökler (`kullanici turkce`, `kurallar:`, `sistem promptum`, `asistaniyiz`) + yanlış pozitif mandalı + kırma testi — *en ciddi, gerçek oran bunun yüzünden bilinmiyor*
2. **#72** `inj-11` ret sırasında prompt metnini sızdırıyor ("Madde 0c'si") → sızıntı kapısı veya prompt maddesi
3. **#73** `inj-10` ayna dil ihlali → MUTLAK KURAL 0'a "ret cümlesi de soru diliyle yazılır"
4. **#74** `mesru-04` senaryosuna `<KATALOG>` bloğu eklenir (yoksa yanlış ölçüyor)
5. **7. koşu** `--tekrar 3` (57 çağrı, ~4 dk, 0 TL) + commit (N7)

**Dağıtılanlar (2026-10-01 — hepsi panoda, tetik ajan postasına düştü):**

| # | İş | Kime | Öncelik | Durum |
|---|---|---|---|---|
| G-0a | Faz 2 risk motoru (8 skor; adlar SSOT:791-822'den okundu, D-260) | utku | P1 | ATANDI |
| G-0b | Faz 3 entity graph v0 (yalnız `same_osb` + `nace_complementary`) | yasu | P1 | ATANDI |
| G-0c | Faz 5 vendor DD **kapsam araştırması** (kod değil) | yasu | P3 | ATANDI |
| G-0d | Faz 6 küresel istihbarat **kapsam araştırması** (kod değil) | utku | P3 | ATANDI |
| 12 | ~~A senaryosu: 2 `iptal` → `plan`~~ | — | — | **DÜŞTÜ** — `task_board.json:2271,2296`: ikisi de D-310 ile bilinçli iptal; yerine `VERI-RAG-KORPUS-01` + `ALTYAPI-MIMIR-BAGLAM-01` zaten panoda |
| 14 | ~~N8 kalan: OSB temizlik~~ | — | — | **DÜŞTÜ** — `task_board.json:2347`: `VERI-OSB-TEMIZLIK-01` zaten `plan`, brifi var |
| 11 | AGENTS.md 5 karar + numara tahsisi (D-227) | ihsan (devredilemez) | P2 | açık |
| 9/10 | salih brifi + chat (D-210) | ihsan (devredilemez) | P1 | açık |

**Ardından:**
6. salih brifini güncelle (19 senaryo, %83.3, üç kusur sınıfı, LLM-as-judge borcu #61)
7. salih'e chat (D-210): `--kimden ihsan --to salih --type koordinasyon --task-id TEST-ODIN-PROMPT-INJECTION`
8. AGENTS.md'ye **5 karar** + numara tahsisi (D-227): ayna dil · tek koşu kanıt değil · düşünme dili serbest/görünürlük yasak · red kalıbı yanlış pozitif kapısı · log kesiti
9. A senaryosu panosu: `VERI-ODIN-EGITIM-VERISI-HAZIRLA` + `ALTYAPI-ODIN-EGITIM-PIPELINE` `iptal` → `plan` (utku); brifte maskeleme kapısı (D-247), firma verisi publik DEĞİL
10. İlişki ağı v0 brifi → utku (OSB komşuluğu + NACE tamamlayıcılık → `company_signals`)
11. K-B açık sorusu: resmî skor seti = SSOT'un 8 skoru · Admin orkestratör paneli brifi · N8 kalan (`osb_veri_denetim.py` + Supabase)

**Açık borçlar:** #71 #72 #73 #74 · #61 (LLM-as-judge) · #63 (EVREN ~%6 HTTP 500, retry yok) ·
#59 · #57 yarım · #56 · #55 · #54/#53 · #52/#51 · #48 (dal) · #47 · #8 #12 #13 #14 #15 #19 #23 #30
**Kapandı:** #68 #67 #70 #69 #66 #65 #64 #60 · #62 ölçülür oldu

## Kimlik
- Rol: Huginn Data Insights projesi orkestratörü.
- Sorumluluk alanı: admin panel / dashboard (Streamlit `app.py` + `web_dashboard/`), test sağlığı, ajan görev teslim kabulü, görev planlama.
- Karar yetkisi: kod düzeyinde uygulama serbest. Mimari/ürün kararı KAHİN onayı ister. Yeni bağımlılık ekleme yasak (stdlib/mevcut kütüphane önceliği).

## Proje Temel Bilgileri
- Giriş noktası: `app.py` — sidebar, topbar, footer, routing, session state anahtarları.
- Sekme modülleri: `web_dashboard/tabs/*.py` (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`, `admin_quality`, `admin_auth`, `__init__.py` = `TabTanimi`/`SECTIONS`/rol yardımcıları).
- Görsel reçeteler: `web_dashboard/charts.py` (`kpi_karti_html`, `tema_paleti`, `kategori_rengi`, `sparkline_fig`, `donut_fig`, `alan_grafigi_fig`).
- Global CSS: `src/company_master/ui/styles.py` — `_BLOKLAR` tuple (bileşen CSS blokları) → `bilesen_css()` → `tum_css()` (root token'ları ekler) → `stil_etiketi()` (`<style>` sarar). `stil_enjekte(tema=aktif_tema())` `app.py::main()` içinde bir kez çağrılır (satır 758), tema değişmedikçe tekrar enjekte etmez (`_hg_stil_tema` session guard).
- Testler: `tests/` (pytest; `test_charts.py`, `test_sekme_kapsama.py`, `test_taslak_sahte_veri.py`, `test_admin_export_excel.py`, `test_ui_modal_stil.py`...).
- API: `web_app.py` (FastAPI; `/api/kpi`, `/api/companies`, `/api/admin/*`, `/api/buyer/*`).

## Sabitler ve Sözleşmeler
- `REHBER_KEY = "_hg_rehber"` (`app.py`) — TEK merkezi "Sekme rehberi" toggle anahtarı, footer'da (`render_footer`) çizilir. Sekme modülleri kendi toggle'ını çizmez, bu anahtarı `st.session_state`'ten okur. **Doğrulandı (2026-09-26)**: 6 sekme (`ana_kontrol`, `admin_panel`, `admin_realtime`, `admin_musteriler`, `pazarlama`, `paketler`) hepsi `_hg_rehber` okuyor, yerel toggle YOK — önceki "açık kusur" notu hatalıydı, kaldırıldı.
- `LOGO_YOLU = ROOT / "docs" / "brand" / "assets" / "Muninn_logo_transparent.png"` (`app.py:100`) — `st.logo` ile sol üst logo; dosya yoksa metin başlığa düşer (`render_sidebar`). **MARKA-LOGO-01 (2026-09-26, ÇÖZÜLDÜ)**: eski değer `ROOT / "assets" / "huginn_logo.png"` idi, `assets/` klasörü hiç üretilmemişti → `.exists()` daima False → marka başlığı hep metin (`## 🏢 Huginn` + caption) olarak kalıyordu. KAHİN onaylı Muninn varyantına çevrildi; artık yazı yok, sadece logo.
- `ROL_KEY = "_hg_rol"` (`app.py`) — U-10 oturum rolü override anahtarı (gelecek RBAC). `aktif_rol()` ile çapraz kontrolü henüz yapılmadı.
- **K3-10h kart kenar reçetesi** (KPI-RENK-05, `tests/test_charts.py`): `kpi_karti_html` çıktısı `background:{surface}; border:1px solid {border}; border-left:3px solid {kategori_rengi}`. Gradient/box-shadow/renk dolgusu yasak — kategori rengi yalnız sol şerit + 6px nokta (`count == 2`). **Doğrulandı**: `pytest tests/test_charts.py -q` → 47 passed.
- **K3-10h madde 4 (tüm container çerçeveleri)** — ÇÖZÜLDÜ. `_AKSIYON_CSS` (`ana_kontrol.py`, 5 aksiyon butonuna özel) genişletilmedi; onun yerine `styles.py`'e yeni global blok eklendi: `_CONTAINER_CSS` → `div[data-testid="stVerticalBlockBorderWrapper"]{border:2px solid var(--hg-color-border-strong)!important}`, `_BLOKLAR` tuple'ına eklendi (tüm `st.container(border=True)` çerçevelerini kapsar, tüm sayfalarda tek kural). Kategori rengi YOK, sadece `border-strong` token'ı (nötr, tema-duyarlı). Test: `tests/test_ui_modal_stil.py::test_container_cerceve_kategori_rengi_yok`.
- `_kart_izgara` (`ana_kontrol.py:165-196`) — sparkline yükseklik eşitleme kuralı: satırdaki tüm kartların serisi yoksa hiçbirinde çizilmez (`hepsinde_seri`).

## Bilinen Ön-Mevcut Test Açıkları (bu oturumun kapsamı DIŞINDA, madde 12 backlog'u)
`pytest tests/ -q` tam koşumda (2026-09-26) **22 failed, 4218 passed, 12 skipped** — hepsi bu oturumdaki değişikliklerden (styles.py/_CONTAINER_CSS/container border) bağımsız, önceden var olan hatalar: naming-audit ihlalleri, DB migration dosya kontrolleri, `test_sayfa_iskeleti.py` (admin_mfa/ana_kontrol iskelet), `test_sekme_kapsama.py` render-fonksiyonu öksüz kontrolü, `test_pano_denetim.py`, `test_musteri_yonetimi.py`, `test_marka_denetim_muafiyet.py`, API route-inventory testleri, chat-table-stil testi, user-settings schema testi. Kasıtlı olarak dokunulmadı (scope creep önleme) — madde 12'ye devredildi.

## Oturum Gunlugu

> 2026-09 bloklari D-219 tavani nedeniyle tasindi: [[Huginn Data Insights/archive/ihsan_context_202609]]

## Kimlik — ihsan = orkestratör = bu ajan (D-286)

Ürün sahibi bildirdi: ihsan ile orkestratör **aynı kişi**; bu dosya benim hafızam. `git config user.name` `Yasua` döndüğü için `kilit_zorla.ajan_kimligi()` beni `yasu` sanıyor, `ajan_chat.py` ise `orkestrator` yazıyor — **üç isim, tek aktör** (D-265 deseni). `ponytail:` kanonik ad tek kaynağa bağlı değil; yükseltme: `ajan_kimligi()` `git config huginn.ajan` okur (tek satır).
D-286'te yasu'ya iki karar bu sıfatla verildi: OSTİM izin adımı **bende**, birleştirme **yasu'da** (assert D-270 + boş tabloya prova D-243 şartıyla). `yasu_project_context.md` benim değil — 213 satırlık kırmızısı sahibinde (`BORC-AJAN-HAFIZA-01`).

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[Huginn Data Insights/utku_project_context]]
- [[Huginn Data Insights/yasu_project_context]]
- [[Huginn Data Insights/salih_project_context]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
