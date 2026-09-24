# Süreç Denetim Raporu — Uygulama Turu Öncesi (2026-09-24)

**Kapsam:** `e24b873` · `8bc6a08` · `59075f2` · `0c3f18c` · `1635c78` turları.
**Kısıt:** Denetim turu — kod yazılmadı, denetim dışı dosya değiştirilmedi. Bu rapor tek çıktıdır.
**Sıralama ölçütü:** Her bulgu `sessiz bozulma olasılığı × uygulama turunda temas sayısı × geri alma maliyeti` çarpımına göre sıralandı — hat sırasına göre değil; en tehlikeli üstte.

---

## 0. Süreç Simülasyonu (kuru çalıştırma)

Sonraki üretim turu (`Tur 2026-09-24 / #2`) bugünkü kaynaklarla **elle** çalıştırıldı. Girdi: SSOT §8/§9/§10/§11/§12 + `gorev_taslagi.md` + pano + arşiv. Çıktı:

| Adım | Ne olur | Kanıt | Sonuç |
| --- | --- | --- | --- |
| 1. SSOT tara | §10:364 `EK BULGU-9/10` **P0** okunur | SSOT:364 · §8.4:323-324 | **2 tekrar-üretim adayı** — iş `-01`/`-02` ile bitti (§14:473-474) |
| 2. §11 tara | KK-5 🔴, KK-6 🟡, KK-7 🔴 açık görünür | SSOT:394-396 | **3 aday** — Y2/Y6 zaten yedekte, görünmez |
| 3. §9/§8.1 tara | K2, A5, A6-MFA, K8-LTV açık görünür | SSOT:341, 269, 270, 347 | **4 aday** — Y1/Y3/Y4/Y5 zaten yedekte, görünmez |
| 4. `task_id` ata | Numara `-29`'dan devam eder; sayaç kaynağı yok, defterde elle | `gorev_taslagi.md:51-56` son numara 28 | Numara çakışması elle önlenir |
| 5. `gorev_ekle` | Yalnız **aktif panoda** mükerrer kontrolü yapılır | `task_board.py:257` | Arşivdeki 394 kayıt **görülmez** |
| 6. Brief üret | `plans/` içine yazılır; mevcut brief varlığı kontrol edilmez | `plans/` 88 dosya, 4'ü aynı D-66 konusunda | Dördüncü kopya sessizce oluşur |

**Ölçüm:** Simülasyon **9 tekrar-üretim adayı** çıkardı (2 bayat durum + 7 görünmez yedek). Önceki tur 16 aday üretmişti; aynı hacimde bir turun yarısından fazlası zaten bilinen iş olur. Hiçbir adımda otomatik kapı devreye girmez — hepsi orkestratörün hafızasına bağlı.

**Kanıtlanmış vaka (simülasyon değil, gerçekleşmiş):** `ALTYAPI-D66-BYPASS-TETIKLEME` aktif panoda `durum: plan` (`task_board.json:3`), aynı iş `ALTYAPI-D66-BYPASS-TETIKLEME-01` arşivde `durum: done`, `bitis: 2026-09-24T01:28:33` (`task_board_arsiv_2026-Q3.json:7040-7047`). Tekrar-üretim teorik risk değil; zaten bir kez oldu.

### SSOT yakınlık ölçümü (taban çizgisi)

| Ölçüt | Ham sayaç | Kanıt |
| --- | --- | --- |
| Kapanan görevin SSOT'ta `task_id` ile iz bırakması | **12 / 12** | SSOT:87, 161, 210, 218-219, 241, 266, 303-304, 342-344, 365, 370-372, 419-420, 467-478 |
| Kapanan görevin hub'a iz bırakması | **0 / 12** | `hubs/ADMIN_DASHBOARD_HUB.md` — `*-ADMIN-*-01..12` araması **0 sonuç** |
| Kapanan görevin §7 matrisine iz bırakması | 5 / 12 | SSOT:210, 211, 218, 219, 241 |
| Brief'te SSOT geri yazma adımının yazılı olması | 10 / 10 | `brief_utku_UI-ADMIN-DAU-17.md:31` ve eşleri |
| Brief'te hub geri yazma adımının yazılı olması | **0 / 10** | aynı dosya §Kurallar — hub maddesi yok |

Yorum: SSOT'a geri yansıma **çalışıyor** (kuralı brief'te yazılı, 12/12 tuttu). Hub'a geri yansıma **hiç yok** — kuralı yazılı olmadığı için değil, kimse istemediği için. Bu, D-185 "hub-önce okuma" ile çelişir: bir sonraki tur hub'ı okuduğunda kapanan 12 işi göremez.

---

## 1. Bulgular (risk sıralı)

### B-01 · Mükerrer kapısı arşiv-kör
`gorev_ekle()` yalnız aktif panoda `task_id` çakışması arar (`src/company_master/orchestrator/task_board.py:257` — `if any(t.get("task_id") == task_id for t in board)`); `8bc6a08` ile 394 kayıt arşive taşınınca bu kapı fiilen boşaldı — arşivdeki hiçbir `task_id` artık korunmuyor, aynı iş aynı adla ikinci kez eklenebilir ve yalnızca sonek (`-01`) farkıyla yan yana durabilir; kanıt `task_board.json:3` (plan) ↔ `task_board_arsiv_2026-Q3.json:7040` (done). Bozulma **sessiz** — hata vermez, log basmaz, iki kayıt da geçerli görünür; geri alma maliyeti sonradan artar çünkü ikinci kayıt kendi brief'ini, kilidini ve commit'ini üretir. Kategori: **(c) uygulanmış ama kuralı yazılmamış** — arşivleme uygulandı, arşivin mükerrer kapısına dahil edilmesi kuralı yazılmadı.
→ **Öneri:** `task_board.py:257`'deki kontrolü `board + tüm task_board_arsiv_*.json` birleşimine genişlet, `ValueError` mesajına arşiv dosya adını ekle; kuralı `AGENTS.md`'ye **D-198 "Arşiv de mükerrer kapısıdır"** olarak yaz; `tests/test_gorev_mukerrer_arsiv.py` ile tek assert bırak.

### B-02 · Bayat SSOT durum satırları tekrar-üretimi besliyor
SSOT §10:364 `EK BULGU-9/10`'u hâlâ **P0** gösteriyor ve §8.4:323-324 aynı iki maddeyi **P0** tutuyor, oysa §14:473-474 ikisinin de `UI-ADMIN-SAHTE-KPI-01` / `UI-ADMIN-SAHTE-EXEC-02` ile giderildiğini `dosya:satır` kanıtıyla yazıyor; bir sonraki üretim turu SSOT'u tarayınca bu iki satırdan iki yeni P0 görev üretir. Bozulma **sessiz** ve simülasyonda birebir gerçekleşti (bkz. §0 adım 1); maliyet **şimdi** düşük (tek belge düzeltmesi), uygulama turu başladıktan sonra artar çünkü yeni görevler kodu ikinci kez değiştirmeye çalışır. Kategori: **(b) kuralı yazılmış (D-197: çelişkide §7 doğru) ama uygulanmamış**.
→ **Öneri:** `DOC-ADMIN-DURUM-SENKRON-15` görevini uygulama turunun **ilk** işi yap (şu an sırada 3.); kapsamına §10:364 + §8.4:323-324 + §14 çapraz doğrulaması gir, kapanışta `scripts/ssot_durum_denetim.py --kuru` gibi tek bir tarayıcı bırak ki bayatlık bir daha elle yakalanmasın.

### B-03 · Panodaki brief yolu diskte yok, alma komutu kontrol etmiyor
`task_board.json:22` `plans/brief_ihsan_ALTYAPI-D66-BYPASS-TETIKLEME.md` gösteriyor, `plans/` dizininde bu ad **yok** (var olan: `brief_ihsan_ALTYAPI-D66-BYPASS-TETIKLEME-01.md`); `cmd_al()` (`scripts/gorev_kutusu.py:92-106`) yalnız talimat metnini arar, `brief` alanının işaret ettiği dosyanın varlığına bakmaz. Bozulma **sessiz** — ajan görevi alır, brief'i açamaz, ya kendi yorumuyla devam eder ya durur; D-66 "brifsiz atama yasak" kuralı kâğıtta var, kodda yok. Kategori: **(b) kural yazılmış, uygulanmamış**.
→ **Öneri:** `cmd_al()` içine `Path(gorev["brief"]).exists()` kapısı koy, yoksa `exit 2` + tetik raporu (D-65 bypass deseniyle aynı yol); aynı kontrolü `gorev_ekle()`'ye de ekle ki kırık yol panoya hiç girmesin.

### B-04 · On görevin tamamında dosya kilidi boş
TASK 13-22'nin hepsinde `"dosyalar": []` (`task_board.json:34, 51, 68, 85, 102, 119, 136, 153, 170, 187`), oysa her brief kilitlenecek dosyayı yazıyla belirtiyor (ör. `brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md` → `web_app.py`, `-17` → `admin_kpi.py`); `gorev_ekle()` kilidi yalnız `dosyalar` parametresinden alır (`task_board.py:279-281`), dolayısıyla uygulama turunda hiçbir kilit yok. `-14` (`web_app.py`) ile `-21` (`admin_audit.py`) aynı anda açılırsa `orkestrator_kontrol.py:68-72` çakışma sayacı **0** raporlar — ölçüm aracı da kör. Bozulma **sessiz**, paralel çalışmada üst üste yazma riski, geri alma maliyeti commit sonrası yüksek.
→ **Öneri:** Uygulama turu başlamadan brief'lerdeki `**Kilitli dosya:**` satırını panoya taşı (`gorev_guncelle(tid, dosyalar=[...])`); kalıcı çözüm için `gorev_at.py`'ye brief'ten kilit çıkaran tek fonksiyon ekle ve D-66 kapısına bağla — kilitsiz görev panoya giremesin.

### B-05 · KVKK kararı sahipsiz
`-21` (`brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21.md:16`) `-13`'ün şemasına dayanarak IP ve ülke kodunu `detay` JSONB alanında **varsayıyor**, `-13` brief'i bu iki alanı tanımlamıyor, SSOT §9 K10 (`:349`) veri kaynağını `admin_audit` gösteriyor, §11 Karar Kaydı'nda (`:388-398`) KVKK ile ilgili **hiçbir KK-N yok** ve §8.4:318 tablo listesinde yalnız `kvkk_bireysel_email_yedek` geçiyor — yani kişisel veri saklama süresi, anonimleştirme ve silme politikası hiçbir belgede kararlaştırılmamış. Bozulma **sessiz** ve **geri alınamaz**: IP verisi üretime yazıldıktan sonra geriye dönük anonimleştirme ek iş ve hukuki risk üretir; maliyet yalnızca sonradan artar. Kategori: **(a) brief'te tanımsız** + sahipsiz karar.
→ **Öneri:** SSOT §11'e **KK-8 "Aktivite logunda IP/ülke saklama politikası"** satırını aç (sahip: Ürün Sahibi), kararı `-13` başlamadan kapat; `-13` brief'ine saklama süresi + anonimleştirme kolonunu yaz — `-13` migration'ı yazıldıktan sonra şema değişikliği ikinci migration demektir.

### B-06 · Yedek görevler panodan görünmez
`gorev_taslagi.md:51-56` altı yedek görev (Y1-Y6, `-23`…`-28`) tutuyor ama bunlar panoda yok; sonraki tur SSOT'u tarayınca aynı maddeleri (§9:341, §8.1:269-270, §9:347, §11:396, §8.3:309) yeniden bulur ve defterin §2 bölümünü okumazsa yeniden üretir — simülasyonda bu 7 adayın kaynağı tam olarak budur (§0 adım 2-3). Bozulma **sessiz**; maliyet her turda tekrar eder, tek seferlik temizlik çözmez. Kategori: **(c) uygulanmış (yedeğe alma kararı) ama kuralı yazılmamış (yedekler nerede saklanır, üretim turu onları nasıl görür)**.
→ **Öneri:** Yedekleri panoya `durum: "yedek"` ile ekle (mükerrer kapısı otomatik devreye girer, B-01 düzeltmesiyle birlikte), `gorev_kutusu.py bak` çıktısında ayrı blokta göster; alternatif — üretim turunun ilk adımını "defter §2'yi oku" olarak D-198'e yaz. Panoya ekleme yeğlenir: tek kaynak, elle hatırlama yok.

### B-07 · D-197'nin yüzde yasağı, D-197'nin yazıldığı turda ihlal edilmiş
D-197 kural 5 metrikleri ham sayaç olarak ister, ancak SSOT §14:479 aynı turda `kapalı/toplam = 32/65 = **%49** taban çizgisi` yazıyor; §14:459 `%30 → %56`, §14:466 `%56 modül · ≈%30 veri gerçekliği` satırları da duruyor — `1635c78` commit'inin "yanıltıcı yüzdeler kaldırıldı" iddiası §14'te tutmuyor. Bozulma **gürültülü değil, sessiz**: yüzde okuyan bir sonraki tur ilerlemeyi yanlış tartar. Kategori: **(b) kural yazılmış, kendi belgesinde uygulanmamış**.
→ **Öneri:** `-15` kapsamına §14:459/466/479 yüzde temizliğini ekle; kalıcı kapı için `scripts/ssot_durum_denetim.py`'ye `%\d` regex kontrolü koy (D-197 kural 5'in makine karşılığı).

### B-08 · SSOT sürüm numarası üç yerde üç farklı
Statü bloğu `Versiyon v2.1 · Tarih 2026-09-22` (SSOT:12-13), revizyon tablosunun son satırı `**v2.5** | **2026-09-24**` (SSOT:479), `AGENTS.md:729` D-196 tablosu da "(v2.1)" diyor; hangi sürümün geçerli olduğu belgeden okunamaz. Bozulma **sessiz** — yanlış sürüme atıf veren brief üretilir; maliyet düşük ama her turda tekrarlar.
→ **Öneri:** `-15` kapsamına al: statü bloğu ve `AGENTS.md:729` §14'ün son satırından türetilsin; kalıcı kapı olarak aynı denetim betiğine "statü sürümü == §14 son satır sürümü" assert'i ekle.

### B-09 · D-197 yazıldı, SSOT'un yedi bölümünde uygulanmadı
Durum/öncelik yalnız §7'de olmalıyken §8.1 (`:265-274` P0/P1/P2 + "✅ KAPANDI"), §8.3 (`:303`, `:304`, `:310`), §8.4 (`:320-324` Öncelik kolonu), §9 (`:338-349` "Hazır mı" kolonu), §10 (`:362-378` Öncelik kolonu), §11 (`:390-398` Durum kolonu), §12 (`:416`, `:419`, `:420`) hâlâ durum taşıyor. Bu B-02'nin kök nedeni: çoklu durum kaynağı olduğu sürece bayatlık kaçınılmaz. Bozulma **sessiz**, maliyet her SSOT güncellemesinde tekrarlar. Kategori: **(b)**.
→ **Öneri:** `-15`'in kabul kriterine "D-197 kural 1-5'in yedi bölümde uygulanması" maddesini ekle ve aynı denetim betiğini kapanış kanıtı yap; el ile tek seferlik temizlik yeterli değil.

### B-10 · §12 G2 bayat, üretilen görevlerle çelişiyor
SSOT §12 G2 (`:415`) hâlâ "Ayrı arama/AI log tablosu **şimdilik atlanır**, tek sinyal (`last_login`) ile başla" diyor, oysa `-13` ve `-14` tam olarak o atlanan tabloyu kuruyor ve `-16` üç sinyale geçiyor; ayrıca `-13`'ün brief'i kaynak olarak §12:415'e atıf veriyor — yani görev, kendisini reddeden satıra dayanıyor. Bozulma **sessiz**: uygulayan ajan §12'yi okursa görevi kapsam dışı sanabilir.
→ **Öneri:** `-15` kapsamına §12 G2'nin yeniden yazımını ekle (atlama kararı `-13`/`-14` ile kalktı, kanıt `§14 v2.5`); brief'lerdeki §12:415 atıfları güncel satıra taşınsın.

### B-11 · K10 veri kaynağı SSOT ile brief arasında çelişiyor
SSOT §9 K10 (`:349`) veri kaynağını `admin_audit` verisi olarak yazıyor, `-21` brief'i (`:16`) `-13`'ün `user_activity_log` şemasına dayanıyor ve IP'yi `detay` JSONB'ye yazacağını varsayıyor; iki farklı tablo, iki farklı sahip. Bozulma **gürültülü olabilir** (sorgu hata verir) ama büyük olasılıkla **sessiz**: ajan bir tablo seçer, diğer taraf bunu fark etmez. Ayrıca `-19` brief'i (`:17`) `admin_audit` altyapısının **doğrulanmadığını** kendi kabul ediyor.
→ **Öneri:** `-13` başlamadan K10'un tek veri kaynağını karara bağla ve SSOT §9:349 ile `-21`/`-19` brief'lerini aynı ada hizala; karar B-05'teki KK-8 ile aynı oturumda alınmalı (ikisi de aynı tabloyu tanımlıyor).

### B-12 · Bağımlılık makine-okunur alanda değil
`-14`, `-16`, `-17`, `-19`, `-15` brief'lerinde `**Bağımlılık:**` satırı **yok**; yalnız `-20` (`:6`) ve `-22` (`:6`) yazıyor; panoda bağımlılık serbest metin `not` alanında duruyor ve arşiv şemasında var olan `dependencies` alanı (`task_board_arsiv_2026-Q3.json:1170-1173`) aktif kayıtlarda kullanılmıyor. Bozulma **sessiz** — `-17` `-14`'ten önce alınırsa boş tabloya sorgu yazılır, test yeşil kalır, panel boş gösterir. Kategori: **(c) uygulanmış (sıra defterde doğru) ama makine alanına yazılmamış**.
→ **Öneri:** Pano kayıtlarına `dependencies` alanını doldur (şema zaten destekliyor) ve `cmd_al()`'a "bağımlı görev `done` değilse uyar" kapısı ekle; brief şablonuna `**Bağımlılık:**` satırını zorunlu yap (`_brief_sablon.md`).

### B-13 · `bakim` komutu arşivi okumuyor
`cmd_bakim()` (`scripts/gorev_kutusu.py:271-290`) yalnız `pano_bakim()`/`pano_tarama()` çağırıyor; `8bc6a08` ile gelen arşiv dosyaları bakım taramasının dışında kaldı, dolayısıyla arşivdeki bozuk kayıt, kırık brief yolu veya mükerrer `task_id` hiçbir rutin denetimde görünmüyor. Bozulma **sessiz**; B-01 ile aynı kökten — arşiv birinci sınıf veri olarak tanımlanmadı.
→ **Öneri:** `pano_tarama()`'yı arşiv dosyalarını da okuyacak şekilde genişlet (salt-okunur mod, yalnız rapor); B-01'in D-198 kuralına aynı cümlede bağla.

### B-14 · Hub'a geri yansıma sıfır
Tamamlanan 12 görevin `task_id`'si SSOT'ta 12/12 geçiyor ama `hubs/ADMIN_DASHBOARD_HUB.md` içinde **0 sonuç**; hub yalnız 10 açık brief'in linkini taşıyor (`:52-65`) ve `ALTYAPI-D66-BYPASS-TETIKLEME` hub'da hiç yok. D-185 "hub-önce okuma" gereğince bir sonraki tur önce hub'ı okur ve kapanan 12 işi göremez — bu, B-02 ve B-06 ile birlikte tekrar-üretimin üçüncü kaynağıdır. Kategori: **(a) kural yazılmamış** — brief şablonunun "Kurallar" bölümünde SSOT geri yazma var (`-17:31`), hub geri yazma yok.
→ **Öneri:** `_brief_sablon.md` "Kurallar" bölümüne "görev sonunda hub'ın ilgili satırını `task_id` + kapanış tarihiyle güncelle" maddesini ekle; hub'a "Kapanan işler" tablosu aç ve ilk dolumunu `-15` kapsamına koy.

### B-15 · Geçici dosya kuralı var, `data/orchestrator/` uygulamıyor
`AGENTS.md:393` geçici dosyalar için `data/_tmp/` veya `_trash/` diyor ve "iş bitince sil" emri veriyor; buna rağmen `data/orchestrator/` içinde beş pano yedeği (`task_board_yedek_2026-09-24.json`, `task_board.json.yedek_2026-09-22`, `task_board.json.yedek_20260921_012012`, `task_board_backup_20260911_2106.json`, `task_board_backup_20260911_2220_guncel.json`) ve `_sprint_add.py`, `_atama_3_gorev.py`, `_encode_baslik.py`, `_test_baslik.py` gibi geçici betikler duruyor; `backups/` için yazılı "son 3 yedek" politikası (`AGENTS.md:501`) bu dizini kapsamıyor. Bozulma **gürültülü değil**, ama yanlış yedekten geri yükleme riski üretir. Kategori: **(b) kural yazılmış, uygulanmamış** — ayrıca denetim kapısı yok.
→ **Öneri:** `AGENTS.md:501` politikasını `data/orchestrator/task_board*.yedek*` desenine genişlet ve `cmd_bakim()` içine "3'ten fazla yedek varsa uyar" satırı ekle; geçici betikleri `data/_tmp/`'ye taşı — dizin zaten mevcut ve kullanılıyor.

### B-16 · cp1254 kalıcı kurala bağlanmamış
Denetim turunda cp1254 kodlama hatası üç kez çarptı; `gorev_kutusu.py:25-31` kendi içinde `reconfigure` yapıyor ama `AGENTS.md` içinde `PYTHONIOENCODING` araması **0 sonuç** veriyor — yani çözüm betik başına kopyalanıyor, kural olarak yazılmamış. D-86 "Windows cmd.exe Kuralı" (`AGENTS.md:88-95`) var ama bu maddeyi içermiyor. Bozulma **gürültülü** (hata görünür) ama her yeni betikte tekrar eder; maliyet her turda sabit şekilde artar. Kategori: **(c) uygulanmış ama kuralı yazılmamış**.
→ **Öneri:** D-86 maddesine "Python çağrıları `PYTHONIOENCODING=utf-8` ile; yeni betikler `sys.stdout.reconfigure(encoding='utf-8')` satırıyla başlar" cümlesini ekle — yeni dosya açmaya gerek yok, mevcut karar genişletilir.

### B-17 · Brief "Kit" alanı şablondan sapmış
`_brief_sablon.md:4` `**Kit:** \`ADMIN-KİT\` (AGENTS.md D-196)` biçimini tanımlıyor; `-14`/`-16`/`-17` buna uyuyor, `-18`/`-19`/`-20`/`-22` ise `**Kit:** ADMIN-KİT (\`AI proje v1/.../02_admin_panel_hedef_dokumani.md\`)` yazıyor. Bozulma yok, ama şablon zorlanmadığı için sapma sessizce çoğalır — `59075f2` turunun şablon kazanımı kısmen erimiş.
→ **Öneri:** Kit satırını `-15` ile tek biçime çek; şablon uyumunu `scripts/ssot_durum_denetim.py`'nin brief kontrol bloğuna ekle (ayrı betik açma).

### B-18 · Kapalı madde sayacı şişmiş olabilir
`gorev_taslagi.md:24` §11 için "7 kapalı (KK-1,2,3,4,6,8,9)" diyor, ancak KK-6 SSOT:395'te 🟡 "Varsayılan: reddedildi" durumunda — onay kaydı yok, yalnız varsayılan; bu satır kapalı sayılırsa `32/65` taban çizgisi bir fazla gösterir. Bozulma **sessiz** ve doğrudan ilerleme ölçümünü etkiler.
→ **Öneri:** KK-6'yı ya Ürün Sahibi onayıyla kapat ya açık say; taban çizgisini buna göre düzelt ve "varsayılan = kapalı değildir" kuralını D-197'nin sayaç maddesine ekle.

### B-19 · Kök `AGENTS.md` karar aralığı bayat
`AGENTS.md:80` vault SSOT'unu "D-48…D-188 tüm karar kaydı" diye tanıtıyor; gerçekte D-197'ye kadar karar var. D-189 uyumu açısından dosya **temiz** (kural kopyası yok, satır 78 ve 86 doğru), yalnız bu aralık ifadesi bayat.
→ **Öneri:** `D-48…D-188` ifadesini "D-48'den itibaren tüm karar kaydı" olarak değiştir — sayı yazmayan biçim bir daha bayatlamaz.

### B-20 · §8.3 C8 "düzeltildi" beyanı eksik
SSOT §8.3 C8 (`:310`) kırık linkin `2026-09-22` tarihinde düzeltildiğini yazıyor, ancak `plans/muninn_prn_vs_huginn_analiz.md` (yazım hatalı ad) dizinde hâlâ duruyor; doğru dosya `AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz.md` olarak ayrıca mevcut. Kapanış beyanı ile disk durumu örtüşmüyor. Düşük risk, ama D-197'nin "kanıtsız durum beyanı yasak" ilkesinin ihlali.
→ **Öneri:** `-15` kapsamında `plans/muninn_prn_vs_huginn_analiz.md`'nin akıbetini karara bağla (sil ya da arşiv uyarısı ekle) ve C8 satırına `dosya:satır` kanıtı yaz.

### Bulgu yok (temiz çıkan hatlar)
- Kök `AGENTS.md` D-189 uyumu: kural kopyası yok, işaretçi doğru (`AGENTS.md:76-88`) — B-19 dışında temiz.
- Arşivde açık/bağımlılık taşıyan kayıt: `durum != done|iptal` taraması **0 sonuç** — 394 kaydın tamamı terminal durumda, aktif bağımlılık sızıntısı yok.
- `cmd_arsivle()` idempotentliği: `gorev_kutusu.py:345-348` aynı `task_id`'yi ikinci kez yazmıyor, `--kuru` modu var — tasarım doğru.
- D-196 ↔ D-197 çakışması: ikisi farklı katmanı düzenliyor (kit kapsamı ↔ durum tekliği), çelişki **bulunamadı**.
- `arsivle` ↔ `bakim` çakışması: ikisi farklı dosyalara yazıyor, veri yarışı **bulunamadı** — ancak B-13 kapsama boşluğu ayrı bir konudur.

### Kapanış durumu (TUR-B, 2026-09-24)

Turun kapsamı B-02, B-07, B-08, B-09, B-10, B-17, B-18, B-20 idi. Kapsam dışı bulgulara dokunulmadı — aşağıda açık olarak işaretlendi. Kanıt: `python scripts/gorev_kutusu.py simulasyon` → sekiz kontrol `OK`, çıkış kodu **0**.

| Bulgu | Durum | Commit | Kanıt |
| --- | --- | --- | --- |
| B-01 | Kapalı | önceki tur (D-198) | `simulasyon` kontrol 1 OK |
| B-02 | Kapalı | `bb794b1` | SSOT §10 ve §8.4 öncelik kolonları kaldırıldı; durum yalnız §7'de |
| B-03 | Kapalı | önceki tur | `simulasyon` kontrol 2 OK |
| B-04 | Kapalı | önceki tur | `simulasyon` kontrol 3 OK |
| B-05 | **Açık** | — | KVKK IP/ülke saklama politikası — ⏳ Ürün Sahibi kararı gerekir (kapsam dışı) |
| B-06 | Kapalı | `c9a46cc` | Yedek görevler Y1-Y6 panoda `durum: yedek` — kanıt: [`DOGRULAMA_TUR_C_2026-09-24.md:187`](DOGRULAMA_TUR_C_2026-09-24.md). Önceki `44250b9` atfı hatalıydı (pickaxe ile düzeltildi, TUR-D2/YA-04) |
| B-07 | Kapalı | `bb794b1` | `simulasyon` kontrol 5 OK — §14 dışında yüzde satırı yok |
| B-08 | Kapalı | `bb794b1` | SSOT §0 `v2.5` · §14 son satır `v2.5` · `AGENTS.md:731` `(v2.5)` |
| B-09 | Kapalı | `bb794b1` | `simulasyon` kontrol 6 OK — §8-§12'de durum/öncelik etiketi yok |
| B-10 | Kapalı | `bb794b1` | SSOT §12 G2 "Yapılan / Kalan" ayrımıyla yeniden yazıldı |
| B-11 | **Açık** | — | K10 veri kaynağı (`user_activity_log` mi `admin_audit` mi) — ⏳ KAHİN onayı (kapsam dışı) |
| B-12 | Kapalı | `dd6f1f9` | `simulasyon` kontrol 4 OK — kapsam kırık bağımlılığa daraltıldı |
| B-13 | **Açık** | — | `cmd_bakim()` arşivi okumuyor (kapsam dışı) |
| B-14 | Kapalı | `1e24bec` | `simulasyon` kontrol 8 OK — yürürlük eşiği `2026-09-24` + iki hub arşiv özeti |
| B-15 | **Açık** | — | `data/orchestrator/` yedek/geçici dosya temizliği (kapsam dışı) |
| B-16 | **Açık** | — | cp1254 — D-86 metnine cümle eklemek yeni karar açma yasağıyla sınırda; ⏳ KAHİN onayı |
| B-17 | Kapalı | `dd6f1f9` | `simulasyon` kontrol 7 OK — aktif 10 brief şablona uyumlu, kapsam aktif panoya sınırlandı |
| B-18 | Kapalı | `bb794b1` | KK-6 açık sayıldı; `gorev_taslagi.md` sayacı 32/33 → 31/34 |
| B-19 | **Açık** | — | Kök `AGENTS.md:80` karar aralığı ifadesi (kapsam dışı) |
| B-20 | Kapalı | `bb794b1` | §8.3 C8 — `plans/muninn_prn_vs_huginn_analiz.md:1-12` zaten D-186 yönlendirme stub'ı; kanıt satıra yazıldı |

Ayrıca `36d9414` altı kırmızı testi yeşile aldı (bulgu numarası yok; D-198 kapısının ön şartıydı). Tur sonu: `pytest tests/ -q` → **4092 passed, 12 skipped, 0 failed**.

---

## 2. Orkestratör Özeleştirisi

**Artık dosyalar.** `scripts/_metrik_sayac_gecici.py` diskte **yok** (okuma denemesi ENOENT) — temizlenmiş; `data/orchestrator/task_board_yedek_2026-09-24.json` **duruyor**. Kritik olan: geçici dosya kuralı `AGENTS.md:393`'te **yazılıydı** ve `data/_tmp/` dizini **zaten kullanılıyor**; yani bu bir kural eksikliği değil, kuralı yazan tarafın kendi kuralını uygulamamasıdır. Orkestratör yeni kural üretirken mevcut kuralı okumadı — bu, B-09'daki D-197 ihlaliyle aynı desendir: kural yazma refleksi güçlü, kural uygulama refleksi zayıf.

**cp1254.** Üç kez aynı hataya çarpıldı, üçünde de yerel çözümle geçildi, hiçbirinde kurala bağlanmadı (B-16). Aynı hatanın üçüncü tekrarı, kuralın yazılmaması gerektiğinin değil, tam tersinin kanıtıdır. Bu turda kaybedilen süre küçük; on görevlik uygulama turunda betik sayısı arttıkça doğrusal büyür.

**`apply_diff` reddi.** `gorev_taslagi.md` ve SSOT üzerinde üç kez %91-99 benzerlikle reddedildi; neden görünmez karakter/boşluk farkı. Bu tekrar eden maliyettir ama **tek seferlik normalize etmek yanlış çözüm olurdu** — normalize eden bir tur, `git diff`'i şişirip gerçek değişikliği gizlerdi. Doğru davranış her seferinde `read_file` ile tam satırı doğrulamaktı; yapıldı, ama maliyeti raporlanmadı. Eksik: bu belgelerin satır sonu/kodlama politikası `.gitattributes`'te tanımlı değil.

**Delegasyon verimliliği.** Denetim turu dört madde (A/B/C/D) tek oturumda yürütüldü. Bölmek **yanlış** olurdu: B/2 bulgusu (arşiv mükerreri) yalnız A/1 (pano) ve D/1 (simülasyon) aynı bağlamdayken görülebildi — ayrı alt-görevlerde her biri kendi dosyasını temiz bulur, çapraz vakayı kimse yakalamazdı. Ancak asıl eksik şudur: **üretim turu (`e24b873`) ile denetim turu ayrı oturumlar olmalıydı ve olmadı.** Kendi ürettiği on görevi aynı bağlamda denetleyen taraf, B-04 (kilit yok) ve B-12 (bağımlılık alanı yok) gibi kendi çıktısındaki boşlukları ancak üçüncü okumada gördü. Kayırma riski yapısal olarak vardı.

**Özet borç:** Bu turda üretilen dört süreç kuralından (arşivleme, brief şablonu, D-197, sayaç) **üçü kendi belgesinde tam uygulanmadı** (B-01 arşiv kapısı, B-09 D-197, B-07 yüzde). Kural üretim hızı, kural uygulama kapasitesini aştı.

---

## 3. Sonraki Adım

Yukarıdaki bulgular dört kümeye ayrılıyor; sıralama size ait.

1. **Tekrar-üretim kapısını kapat** (B-01 + B-06 + B-13) — ilk adım: `task_board.py:257` kontrolünü arşive genişlet, `AGENTS.md`'ye D-198 yaz, `tests/test_gorev_mukerrer_arsiv.py` ile tek assert bırak.
2. **SSOT'u gerçeğe hizala** (B-02 + B-07 + B-08 + B-09 + B-10 + B-20) — ilk adım: `DOC-ADMIN-DURUM-SENKRON-15`'i sıranın başına al ve kapsamını bu altı maddeyle genişlet.
3. **Uygulama turunu güvene al** (B-03 + B-04 + B-12) — ilk adım: on görevin `dosyalar` ve `dependencies` alanlarını brief'lerden doldur, `cmd_al()`'a brief-var-mı kapısı ekle.
4. **KVKK kararını kapat** (B-05 + B-11) — ilk adım: SSOT §11'e KK-8 satırını aç, aktivite logunda IP/ülke saklama süresini ve tek veri kaynağını (`user_activity_log` mı `admin_audit` mi) karara bağla; `-13` bu karar olmadan başlamasın.

**Hangisinden başlayalım?**

---

## 4. Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/data/orchestrator/gorev_taslagi]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
