# Borç Defteri — tek kanonik kayıt (D-272)

**Bu dosya borç listesinin tek kaynağıdır.** Devir notu buradan okunur, hafızadan değil.
`AGENTS.md` kararın *gerekçesini* tutar; bu defter *durumunu* tutar.

**Neden ayrı dosya:** `AGENTS.md` içindeki D-kayıtları kronolojik değil (ölçüm D-272/1:
`[…263, 266, 265, 264, 267, 268, 270, 269, 271]`). Bu yüzden bir borcun son durumu dosyada
**aşağıda** değil, **en büyük D numarasında** yazılıdır. Satır sırasıyla okuyan her tur
yanlış okudu — altı tur üst üste (D-265, D-266, D-267/1, D-268/1, D-271/1).

**Kural (D-272):**
1. Bir D-kaydı borç kapatıyor/iptal ediyorsa **aynı turda** bu defter güncellenir.
2. Durum alanı yalnız şu değerleri alır: `ACIK` · `KAPANDI` · `IPTAL` · `KURAL` (borç değil, kural/görev kimliği).
3. `AGENTS.md`'de adı geçip bu defterde olmayan kimlik testi düşürür:
   [`tests/test_dokuman_politikasi.py::test_d272_borc_defteri_eksiksiz()`](../tests/test_dokuman_politikasi.py).
4. Başlık fiil taşımaz (D-271).

---

## Borçlar

| Kimlik | Ölçülen sapma | Durum | Kaynak D | Kapanış D |
|---|---|---|---|---|
| `BORC-NACE-DOGRULAMA-01` | `nace_validity` alanı kaynaksız | KAPANDI | D-258 | D-287: doğrulama **yapılamaz değil, anlamsız** — sözlük var (3319) ama yetim kod **0**, hiçbir şeyi ayırt etmiyor; `verified` değeri hiç üretilmiyor, kolon `src/`de hiç **okunmuyor**. Ağırlık çekilmedi (kilit dürüst), puan kapısı iki mandalla korundu |
| `BORC-PANO-BORC-00` | borç listesinin kanonik kaydı yok | KAPANDI | D-271 | D-272 |
| `BORC-SCRIPTS-01` | `scripts/` altında 41 `_*` girdi (29 `.py` hepsi derlenir, **0 çürük**, üretim çağıranı **0**); kökte ayrıca **76 index hayaleti** tek kullanımlık betik. D-281'de ölçüldü ve **tavanlandı** (76/2), kesme ürün sahibinde. **D-288 eki:** `_ARSIV_tek_kullanimlik/` altında ayrıca **~160 izlenen dosya** var — aynı sapmanın ikinci yuvası, otomasyonun `git add -A`'sı ile büyümüştü; kapı kapatıldı, mevcut dosyalar **kesilmedi** (sahiplik belirsiz) | ACIK | D-255 | — |
| `BORC-KARAR-NUMARA-01` | karar numarası **iki ayrı dosyadan** tahsis ediliyordu (`AGENTS.md` max D-281, bu defter max D-282); çakışma: **D-281 iki karara birden** verilmiş. D-227 mandalı yalnız `AGENTS.md`'yi ve yalnız `(D-NNN — KAH` biçimini tarıdığı için çatışma görünmezdi | KAPANDI | D-281 | D-286: `scripts/karar_no.py` tek havuz + `TAVAN_CATISMA=1` mandalı (kırılarak doğrulandı; D-283 eşzamanlı ajan yarışında çakıştı, **mandal yakaladı**, kayıt D-286'e taşındı — tavan yükseltilmedi) |
| `BORC-AJAN-HAFIZA-01` | `yasu_project_context.md` **213 satır > 200** (D-219 tavanı); mandal kırmızı: `tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari`. **SAHİBİNDE** — başka ajanın hafıza dosyası, bu turda kesilmedi (D-226/sahiplik) | ACIK | D-286 | — |
| `BORC-SICIL-DAIRE-01` | 619 firmada sicil no var, sicil dairesi yok | ACIK | D-260 | — |
| `BORC-VKN-01` | VKN kanalı ölü, kaynak bulunamadı | ACIK | D-253 | — |
| `BORC-AD-VARYANT-01` | 31 kısaltma varyantı | IPTAL | D-261 | D-263 |
| `BORC-ADLANDIRMA-01` | kimlik hiç açılmamıştı (devir notu uydurdu) | IPTAL | — | D-271 |
| `BORC-DEDUP-KAYNAK-01` | `content_hash` yinelenmeyi durdurmuyor | KAPANDI | D-261 | D-262 |
| `BORC-DEFTER-IKI-SEMA-01` | kimlik hiç açılmamıştı; uyarı gerçek, borç değil | IPTAL | — | D-271 |
| `BORC-EXTID-01` | `baskentosb.org.tr` kazıyıcısı `external_id` üretmiyordu | KAPANDI | D-261 | D-262 |
| `BORC-GOC-IKI-DEFTER-01` | göç defteri iki değil üç, yazan yol dört | KAPANDI | D-264 | D-265 (son yol D-271) |
| `BORC-KOLON-DUSUR-01` | ölü kolon aktif sanılıyordu | KAPANDI | D-258 | D-259 |
| `BORC-PANEL-TAVAN-01` | panel tavanı sabit yazıyordu | KAPANDI | D-253 | D-258 |
| `BORC-PERF-BANT-01` | performans bandı yanlış; yüzeyin çağıranı yoktu | KAPANDI | D-259 | D-266 |
| `BORC-QUALITY-BETIK-01` | adı geçen betik diskte yok | IPTAL | D-255 | D-271 |
| `BORC-TASFIYE-IKIZ-01` | 22 tasfiye önekli firma öneksiziyle ikiz | KAPANDI | D-263 | D-264 |
| `BORC-TEST-SIRA-01` | test sırası bağımlılığı; iki kirleten | KAPANDI | D-267 | D-271 |
| `VERI-KAYNAK-BAG-01` | 5060 yetim firma, kaynak bağı yok | KAPANDI | D-260 | D-263 |

## Borç değil — kural / görev kimlikleri

Mandal `BORC-*` ile `VERI-*` kimliklerini birlikte tarar; aşağıdakiler borç değil, bu
yüzden ayrı bölümde durur. Silinmezler: adları `AGENTS.md`'de geçtiği sürece defterde kalır.

| Kimlik | Ne | Durum | D |
|---|---|---|---|
| `VERI-ETIKET-01` | her blok kaynağını söyler | KURAL | D-213 |
| `VERI-HAYALET-TEMIZ-01` | 9412 firma + UNIQUE indeks, onaylandı | KURAL | D-260 |
| `VERI-KAYNAK-TURU-01` | kaynak türü sözleşmesi | KURAL | D-235 |
| `VERI-KAZIYICI-DONGU-01` | kazıyıcı döngü sözleşmesi | KURAL | D-235 |
| `VERI-KOLON-IKIZ-01` | `companies.vergi_no` ikiz kolon ölçümü | KURAL | D-245 |
| `VERI-NACE-KOLON-01` | 0 kaçak NACE etiketi, onaylandı | KURAL | D-260 |
| `VERI-NACE-SOZLUK-01` | 3319 NACE kodu, onaylandı | KURAL | D-260 |
| `VERI-NACE-TEMIZ-01` | 554 `invalid_cleared`, onaylandı | KURAL | D-260 |
| `VERI-GORUNURLUK-01` | **böyle bir kimlik yok.** D-272/5'in anlattığı hayalet; o metni yazmak hayaleti gerçek bir dizeye çevirdi. Deftere iptal olarak girer, çünkü çıkarmanın yolu kaydı silmek olurdu | IPTAL | D-272 |

## Ölçülmüş sayılar (D-272)

- `AGENTS.md`'de kimlik: **71**. Mandalın gördüğü (`BORC|VERI`): **27**. Dışında kalan: **45**.
- Borç (gerçek): **18** — açık 4, kapandı 10, iptal 4.
- **Kapanmış ama açık/çelişkili sanılan: 2** — `BORC-KOLON-DUSUR-01` ve `BORC-PANEL-TAVAN-01`.
  D-271/6 bunları "çelişki" ilan etti; çelişki yoktu, satır sırası yanlış okundu
  (s2920=D-256 "kapanmadı" → s2945=D-258 "kapandı"; s3037=D-258 → s3121=D-259).
- 45 kimlik mandalın regex kapsamı dışında (`NACE-*`, `KVKK-*`, `GOC-*`, `SEMA-*`…).
  Bu bilinen kör nokta; genişletme ayrı bir tur işi — kapsam büyütmek defteri şişirir,
  fayda ölçülmedi.
- **26 → 27:** D-272/5 metni hayalet kimliği tek başına andığı için mandalın gördüğü kimlik
  bir arttı. Kayıt tutmanın kendisi ölçümü değiştirdi; sayı kılıfına uydurulmadı, gerçeğe
  çekildi (D-271'in tavanı 3 değil 4 yapmasıyla aynı karar).

## Devir — sonraki oturum (D-288 sonrası)

Bu turda otomasyonun git kapısı daraltıldı. Aşağıdaki D-287 bölümü **tarihî kayıttır**,
güncel durum bu başlığın altındadır.

### Bu turda bitenler (D-288)

| İş | Sonuç | Kanıt |
|---|---|---|
| Otomasyon nerede yaşıyor | `scripts/git_auto_push.bat`, Zamanlanmış Görev `\Huginn Git Push`, **iki tetik** (00:01 + 12:01, günlük), 2026-09-11'den beri, kuran `EXCALIBUR\yasin` | `schtasks /query /xml ONE` → `<Command>…git_auto_push.bat</Command>`, iki `<StartBoundary>` |
| Kaç yol var | **2** toptan sahneleme: `git_auto_push.bat:33` + `wiki_automation/run_all.py::git_commit` | `git grep -n -E "git add (-A\|--all\|\.)"` |
| Tarih etkisi | **64** otomatik commit, **2150** benzersiz dosya (`src/` 217, `tests/` 143, `scripts/` 233, `_ARSIV…` 160) | `git log --name-only --grep=…` + Counter |
| Kapı daraltıldı | her iki yolda beyaz liste: `data docs hubs plans indexes` | docstring/REM gerekçe (D-267) |
| Mandal | `tests/test_otomasyon_sahneleme.py` (2 test) | **kırarak** doğrulandı, aşağıya bak |
| Yeni kırmızı kesildi | `_ARSIV_tek_kullanimlik/_pytest_rerun.txt` → `git rm --cached` | `test_zaman_damgali_yedek_git_te_izlenmiyor` **1 passed** |
| Kural çelişkisi | `AGENTS.md` D-193 maddesi ajanlara `git add -A` **emrediyordu** → düzeltildi | AGENTS.md:751 |

### ⚠ MANDAL İLK SÜRÜMÜNDE YALANCI YEŞİLDİ — kendi hatam, beyan ediyorum

Mandalın ilk deseni düz `git` arıyordu. `.bat` git'i `"%GIT%"` değişkeniyle çağırdığı için
gerçek `"%GIT%" add -A` satırını **kaçırdı**. İlk koşuda gelen kırmızı, çalışan koddan değil
benim yazdığım **gerekçe yorumundan** geliyordu — yorumu soyunca test yeşile döndü ve
"tamam" görünüyordu. Kırma testi yapılmasaydı bu mandal **hiç çalışmadan** yeşil duracaktı.

**Ders (D-260'ın mandala uygulanışı): yeşil test de bir beyandır, kırılana kadar kanıt değildir.**
Desen `%GIT%` / `$GIT` biçimlerini kapsayacak şekilde düzeltildi; `.bat` ve `.py` yolları
**ayrı ayrı** kırılıp kırmızı görüldü, sonra geri alındı.

### 🔴 ÜRÜN SAHİBİNE — TARİHTE GERÇEK ÖZEL ANAHTAR VAR (temizlik YAPILMADI)

Zorunlu sır araması yapıldı. İki ayrı sonuç:

1. **Otomatik commit'lerin içinde sır YOK.** Çıkan isimler yalnızca sır *aracı*
   (`rotate_secrets.py`, `test_secrets_rotation.py`, bir kurulum raporu). Bu iyi haber.
2. **Ama tarihte elle girmiş gerçek bir anahtar var:** `config/certs/selfsigned.key`,
   içeriği `-----BEGIN RSA PRIVATE KEY-----`.

| Ölçüm | Sonuç |
|---|---|
| Ekleyen commit | `90c4702` (2026-09-20) — **otomasyonun ürünü değil, elle** |
| HEAD ağacında mı | **Hayır** (`git ls-tree -r HEAD` boş) |
| İzleniyor mu | **Hayır** (`git ls-files -- config/certs/` boş) |
| Commit HEAD'in atası mı | **EVET** (`git merge-base --is-ancestor` → 0) |
| Blob ulaşılabilir mi | **EVET** — `216cfdd540712a8c327ceb1cd4bc1ec37c6048fe` |

Yani dosya çalışma ağacından kalkmış ama **tarihten kalkmamış**; depoyu klonlayan herkes
`git show 90c4702:config/certs/selfsigned.key` ile anahtarı okuyabilir.

**Hiçbir şey temizlenmedi.** Tarih yazmak geri dönüşsüzdür, karar sizindir. Seçenekler:
**(A)** anahtarı **döndür** (yenisini üret, eskisini iptal et) — tarihi hiç ellemez, en güvenli,
self-signed sertifika için genelde yeterli. **(B)** `git filter-repo` ile tarihten sök — tüm
commit karmaları değişir, üç ajanın ağacı ve üst depo işaretçisi bozulur, **ağır**.
**Önerim A**, çünkü depo şu an özel ve anahtar self-signed; ama depo bir gün herkese açılırsa
B kaçınılmaz olur.

Ek not: `workspace/external/cursor_grok/.../leak.py` içindeki `API_KEY = 'secret123'`
**kasıtlı sahte fikstürdür**, zarar yok.

### Otomasyon: durdurulmadı, daraltıldı

Ölçülen seçenekler — **(A)** durdur: günlük yedek kaybolur, **sizin kararınız**, yapılmadı.
**(B)** beyaz liste: **uygulandı**. **(C)** `pre-commit`'e bırak: kanca commit anında çalışır,
`add`'i engellemez, yetmez.

Otomasyon artık yalnız `data docs hubs plans indexes` sahneliyor. Kod, test, betik ve
`_ARSIV_tek_kullanimlik` **otomasyonun işi değil** — ajanlar tek tek sahneler.
`data_worktree` bilerek dışarıda: D-228'de tasfiye edildi, diskte yok.

### `.gitignore` neden tutmadı (ölçüldü)

Kural eksikliği değil, **kapsam hatası**: `/_*.txt` baştaki eğik çizgi yüzünden yalnız köke
bağlıydı, alt dizine hiç inmiyordu. `git check-ignore -v` çıkış kodu **1**, çıktı **boş** —
hiçbir desen eşleşmemişti. `_pytest_rerun*` eklendi; tekrar ölçüldü, artık eşleşiyor
(`.gitignore:148`).

**Yan bulgu, kesilmedi:** `_ARSIV_tek_kullanimlik/` altında **~160 izlenen dosya** var.
`BORC-SCRIPTS-01` DONDURULMUŞ; ölçüldü, rapor edildi, dokunulmadı.

### Tam takım (D-288 kapanışı)

Sabit sıra `4 failed, 4580 passed, 12 skipped — 202,13 sn`; rastgele sıra **aynı 4 kırmızı**
(`203,25 sn` koşusunda 5'ti, beşinci benim çöpümdü, aşağıda). **Sıra bağımlılığı yok.**
Taban 4562 → +18 geçen (D-288 mandalı 2, kalan 16 başka ajanların bu turdaki testleri).

| Kırmızı | Sahibi | Bu turda kesildi mi |
|---|---|---|
| `test_kok_izin_listesi::test_zaman_damgali_yedek_git_te_izlenmiyor` | **benim** (`_pytest_rerun.txt`) | **EVET** — `git rm --cached` + `.gitignore` kapsam düzeltmesi |
| `test_kok_politikasi::test_vault_kokte_tek_kullanimlik_yok` | **benim** (`_k.tmp`, `_oc.tmp`, `_oc2.tmp`, `_sir_taramasi.txt`) | **EVET** — D-241, silindi, mandal yeşile döndü |
| `test_dokuman_politikasi::test_d219_ajan_context_dosyalari` | yasu (`yasu_project_context.md` 213>200) | hayır — `BORC-AJAN-HAFIZA-01`, D-226/sahiplik |
| `test_brief_sablon_denetim::…[brief_yasu_VERI-OSTIM-TAM-TARAMA-01.md]` | yasu | hayır — brief 11 zorunlu bölümün **hiçbirini** taşımıyor (D-217) |
| `test_naming_audit::test_acik_gorevlerde_yeni_d57_ihlali_yok` | yasu | hayır — aynı görev, başlık D-57 kalıbına uymuyor |
| `test_pano_d57_kalici::test_aktif_gorevler_d57_gecer` | yasu | hayır — aynı görev, aynı sebep |

**Ölçülen not:** son üç kırmızı **tek kaynak** — `VERI-OSTIM-TAM-TARAMA-01` görevi bu tur
açıldı ve üç ayrı mandalı birden kırdı. Üçü tek düzeltmeyle (başlığı D-57 kalıbına çekip
brief'i `plans/_brief_sablon.md`'ye uydurmak) kapanır; sahibi yasu, kesme bende değil.

### Sonraki tura

- Anahtar kararı (A döndür / B tarih temizliği) — **bekliyor**.
- Otomasyonun beyaz listesi doğru kapsamda mı, ilk gerçek koşudan sonra
  `git log -1 --name-only` ile **ölçülmeli** (bu tur çalışmadı; sonraki tetik 00:01).
- `data/` altına sır düşerse otomasyon yine alır. Beyaz liste kod sızmasını kesti,
  **veri sızmasını kesmedi**. Gerekirse `data/` için ayrı bir desen mandalı.

---

## Devir — D-287 turu (tarihî kayıt)

Bu bölüm devir notunun kaynağıdır (D-219 mantığı). Ajan hafıza dosyasına yazılmadı: ölçüldü,
dört `*_project_context.md` dosyasında bu hattın hiçbir izi yok — hat panoya bağlı değil,
doğrudan ürün sahibiyle yürüyor.

### Bu turda bitenler (D-287)

| İş | Sonuç | Kanıt |
|---|---|---|
| Karar A — `ac` yanlış kapı uyarısı | `chat.acik_sahipler()` + `cmd_ac` stderr uyarısı, **engelleme yok** | `tests/test_ajan_chat.py` 21 geçti (15→21) |
| Karar B — karar numarası kancaya | `test_karar_numara_tekligi.py` pre-commit'e eklendi; `karar_no.py` **değişmedi** (mandal zaten vardı) | Sahte D-286 başlığı → commit **durdu** (`2 <= 1` düştü), geri alındı → yeşil. Kanca yeni maliyet **19,4 sn** |
| Karar C — yazma kapısı ölçümü | motor çağıran **163**, gerçekten YAZAN **70**, doğrudan `create_engine` **25**, motorsuz yazan **0**; dağılım `src/` 22, `scripts/` 47, **`web_dashboard/` 0** | mimari **değiştirilmedi** (ürün sahibi kararı) |
| NACE doğrulama | doğrulama **reddedildi**, ağırlık **çekilmedi**, iki mandal kondu | `tests/test_panel_durustluk.py` 19 geçti (17→19), kırarak doğrulandı |

**Karar C okuması (ürün sahibine):** yazma kapısı **tek değil** — 25 dosya `create_engine`'i
doğrudan çağırıyor, 24'ü `connection.py`'yi atlıyor. Ama panel **hiç yazmıyor** (0), yani
canlı-DB ayrımının dayandığı risk panelde yok. Motorsuz gizli yazma yolu da yok (0).

**NACE okuması:** `verified` sıfır değil, değer kümesinde **yok** (`medium` 5732 / `unknown`
2942 / `fallback` 738). Kod doluluğu 8289/9412 = **%88,07**, kanıt kaynaklı NACE **0/9412 = %0**.
Sözlüğü puana bağlamak 8289 **tahmin** koda 1.0 dağıtırdı — puan uydurmanın ta kendisi.
Tavan kilidi (7,5/10) **dürüst**, bu yüzden ağırlık gerçeğe çekilmedi; kilit kaldıracak olan
şey kanıt kaynağıdır (`BORC-VKN-01` / MERSİS), bu tur açılmadı.

### Tam takım (D-287 kapanışı)

Sabit sıra `2 failed, 4562 passed, 12 skipped — 190,29 sn`; rastgele sıra `2 failed, 4562 passed,
12 skipped — 176,88 sn`. **Sıra bağımlılığı yok.** Taban 4555 geçti → +7: Karar A 6 mandal +
NACE 2 mandal − aşağıdaki yeni kırmızı 1.

| Kırmızı | Sahip | Sebep | Karar |
|---|---|---|---|
| `test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari` | yasu | `yasu_project_context.md` 213 > 200 satır | **Kesilmedi** (D-226), bilinen kırmızı |
| `test_kok_izin_listesi.py::test_zaman_damgali_yedek_git_te_izlenmiyor` | Yasin (otomasyon) | `_ARSIV_tek_kullanimlik/_pytest_rerun.txt` git'e **izlendi** → `1 <= 0` düştü | **Kesilmedi** — benim dosyam değil, ürün sahibi kararı bekliyor (`git rm --cached`) |

### ⚠ Yeni tehlike — otomatik günlük commit tüm ağacı süpürüyor

`dfc5f0a Yasin — Otomatik gunluk commit (29.09.2026 12:01)`: **352 dosya, 41619 ekleme**.
Bu commit tur ortasında çalıştı ve **uçuştaki dosyalarımı** (`src/company_master/chat.py`,
`scripts/ajan_chat.py`, `tests/test_ajan_chat.py`, `tests/test_panel_durustluk.py`,
`scripts/hooks/pre-commit`, hatta D-241 gereği sonradan sildiğim `scripts/_nace_olcum.py`)
tarihe soktu. Yedek dosyasını izleyen de aynı commit.

**Sonuç:** "tek tek sahnele, `git add -A` yasak" kuralı üç ajan için geçerli ama otomasyon bu
kuralın dışında ve kuralı **fiilen geçersiz kılıyor**. HEAD artık `38ad9f7` değil `dfc5f0a`.
Karar ürün sahibinin: otomasyon ya durdurulmalı ya da `git add -A` yerine beyaz liste ile
çalışmalı. Ölçüldü, kesilmedi, bekliyor.

### ÜRÜN SAHİBİNE SORU — `BORC-SCRIPTS-01` (cevapsız silme YOK)

`ask_followup_question` aracı üç denemede de düştü; soru kanala sorulamadı, buraya yazıldı.
**Ölçüm bitti, kesme kararı sizde.** Ölçülen tablo:

| Yer | Ne | Sayı | Durum |
|---|---|---|---|
| `scripts/_*` | girdi | 41 | 29 `.py` **hepsi derlenir**, **0 çürük**, 1 dizin (`_arsiv`), 11 veri |
| `scripts/_*` | üretim çağıranı | **0** | tüm isabetler belge/rapor (D-270 uygulandı) |
| Kök | index hayaleti tek kullanımlık betik | **76** | diskte YOK, git index'inde VAR (check 42, run 16, debug 8, verify 6, clean 2, add 1, count 1) |
| Kök | bozuk-kabuk çöpü | 2 | `0)`, `{t.get('assignee')` — 0 bayt, D-221 ihlali |
| Ağaç | başka ajanların commit edilmemiş silmesi | 94 | utku/ihsan/yasu aktif — **dokunulmadı** |

Devir notunun dayandığı **"borcumuz kalsın" kararı kaynaksızdır**: bu defterde,
`AGENTS.md`'de ve `git log --all -i --grep="borcumuz"` içinde **yok**.

Üç seçenek:
1. **Borç kalsın** — ölçüm tablosu yeterli teslimdir, tavan (76/2) artmayı engeller.
2. **Yalnız çöpü kes** — 2 bozuk-kabuk dosyası silinir (D-221), gerisi durur.
3. **Hepsini kes** — 76 index hayaleti commit'lenir, `scripts/_*` tasfiye edilir.
   Dikkat: bu, başka ajanların açık işiyle aynı ağaçta olur.

Seçim yapılmadan **hiçbir silme yapılmadı**.

- **Kaldığım yer:** D-286 yazıldı. **Hash yazılmıyor:** bu satıra hash yazan commit hash'i
  değiştirir (sonsuz gerileme). Konum dalın tepesidir: alt depo `chore/monorepo-merge`,
  üst depo `master`; `git log --oneline -3` ile okunur.
- **TEŞHİS DÜZELTİLDİ (D-286):** D-281'in "D-273…D-280 D-227+D-272 ihlalidir" iddiası
  **yanlıştı**. Ürün sahibi bildirdi: o kayıtlar **emirle** yazıldı, ihlal değil, ajan
  suçlu değil. Ölçülen gerçek sapma: numara **iki ayrı dosyadan** tahsis ediliyordu ve
  D-227 mandalı çatışmayı **göremiyordu** (yalnız `AGENTS.md`'yi, yalnız `(D-NNN — KAH`
  biçimini tarıyordu). Çözüm: `python scripts/karar_no.py` — **tek havuz**.
  D-227'ye ürün sahibi istisnası eklendi: kayıt başka dosyada durabilir, **numaranın
  kaynağı** tektir.
- **Eşzamanlı ajan yarışı CANLI ve İKİ KEZ yaşandı:** kaydı önce `D-283` yazdım, yazarken
  başka ajan aynı numarayı deftere verdi → `D-284`'e taşıdım; tam takım koşusunda
  **ikinci kırmızı** geldi (`CATISMA: ['D-281','D-284']`), çünkü yasu deftere `## D-284`
  **ve** `## D-285` yazmıştı. **Ölçüm anlıktır, tahsis değildir.**
- **TAHSİS ARTIK ATOMİK (D-286):** `python scripts/karar_no.py --al` numarayı
  `data/karar_tahsis/D-NNN.txt` dosyasını `O_EXCL` ile açarak **kapatır**; dosya varsa bir
  sonrakine geçer. Kırılarak doğrulandı: ardışık iki tahsis `D-286` ve `D-287` verdi.
  Kayıt tahsisli **D-286**'ya taşındı (yasu'nun D-284/D-285'ine dokunulmadı), deney artığı
  `D-287.txt` düşürüldü. Düz `karar_no.py` yalnız **ölçer**, tahsis etmez.
- **Test tabanı yeni: 4555 passed, 12 skipped, 1 FAILED.** Sabit sıra (`-p no:randomly`)
  ve rastgele (`--randomly-seed=286`, 269.26s) **aynı** sonucu verdi → sıra bağımlılığı yok.
  4527 → 4555: +1 benim tahsis mandalım, +27 başka ajanların yeni testleri
  (yasu'nun `test_ostim_birlestirme_kalite.py` 18 test dahil).
- **AÇIK KIRMIZI — benim işim değil, düzeltilmedi:**
  `tests/test_dokuman_politikasi.py::test_d219_ajan_context_dosyalari` —
  `yasu_project_context.md` **213 satır**, D-219 tavanı **200**. Dosya yasu'nun açık işi
  (oturum sırasında düzenleniyordu); başka ajanın hafıza dosyasını kesmem D-219'un sahipliğini
  bozar. Çözüm sahibinde: eski oturum bloklarını `archive/yasu_context_<YYYYMM>.md`'ye taşı.
  Mandal doğru çalıştı — kusuru **ben yazmadım, mandal yakaladı**.
- **Yeni ayrım (D-281, ezberlenecek):** diskte yok + index'te yok = **rezervasyon** (meşru);
  diskte yok + index'te **var** = **index hayaleti** (commit edilmemiş silme). Kilit
  dosyasındaki `scripts/ajan_cakisma_kilidi.py` **hayalet değil**, ihsan'ın rezervasyonu.
- **KİLİT ARTIK ZORLANIYOR (D-286):** `scripts/kilit_zorla.py` + `scripts/hooks/pre-commit`.
  Gerçek commit denemesiyle **kırılarak** doğrulandı: kanca ateşledi, `DURDU` bastı,
  `git log` `6c52bdd`'de kaldı — commit olmadı. **Ölçülen tavan:** rezervasyon
  (ne diskte ne index'te) **stage edilemez**, bu yüzden commit anındaki zorlayıcı
  rezervasyonu asla yakalayamaz. Yalnız var olan dosyayı korur.
- **Kimlik:** `AJAN` env yok, `huginn.ajan` git config yok; tek kaynak `git config user.name`.
  Her ajan `git config huginn.ajan <ad>` kurarsa zorlayıcı kimliksiz halde de durur.
- **Ürün sahibi kararı bekliyor (taşıma YAPILMADI):** eşzamanlı ajan izolasyonu, D-272/7'deki
  üç seçenek. Önerim 1+2 (sıra düzeni + var olan kilidi zorlamak); ayrı worktree canlı
  veritabanını ayırmadığı için tek başına yetmez. **Canlı DB ölçümü:** üç ajan da aynı
  Supabase Postgres'e yazıyor (~80 betik + ~20 modül `get_engine` çağırıyor), göç kapısı tek.
- **Açık 4 borç, öncelik ürün sahibinde:** `BORC-VKN-01` (kaynak yok, MERSIS A/B kararına
  bağlı), `BORC-NACE-DOGRULAMA-01`, `BORC-SICIL-DAIRE-01` (§5 saklı karar),
  `BORC-SCRIPTS-01` (76 hayalet **donduruldu**, ürün sahibi kararı). `BORC-KARAR-NUMARA-01`
  **kapandı**.
- **Araç tuzağı:** çok satırlı `python -c` cmd.exe'de **sessizce hiçbir şey yapmaz** —
  çıktı yok, çıkış kodu 0. Tek satır `-c` veya gerçek dosya kullan; "komut geçti" ekranı
  kanıt değil (D-260). `ask_followup_question` bu turda **üç kez** kusurla düştü.
- **Bir sonraki turda ilk iş:** bu defteri oku, `AGENTS.md`'yi baştan tarama. Borcun son sözü
  **en yüksek D numarasında**dır, dosyadaki son satırda değil. Ve devir notunun her fiilini
  ölç: **beş turdur devir notunun adlandırdığı borç yanlış çıkıyor** (D-267/1 deseni).

## Ilgili Nodlar

- [[AGENTS]]
- [[docs/HEDEF_VERI_KAPSAMI]]

---

## D-273 — TOBB üyelik erişimi: düz HTTP kanıt almaz (2026-09-29)

**Gözlem (ölçüldü):** `httpx.get(".../goster.php?Guid=...")` → **HTTP 200** ama
**gövde boş**. Sebep: içerik JavaScript ile yükleniyor + oturum şart.

**Karar:** Düz HTTP ile tarama **YAPILMAZ**. Kanıt katmanı oturum üzerinden
alınır. Kanıt dosyası kendi verisiyle birlikte saklanır (D-216 uyum).

## D-274 — MERSİS: 17 hane mi 16 hane mi?

**Gözlem (ölçüldü):** Ekranda 17 haneli `0012032074100024`; ilk 10 hane
`0120320741` geçerli VKN. Kanonik biçim **16 hane** (`0120320741000024`);
baştaki sıfır bozukluk/alan hizası artığıdır.

**Karar:** Kaynak **kanonikleştirme** tabakasından geçer: 17 hane + başta `0`
ise ilk hane düşürülür. VKN doğrulaması **yalnız** `kimlik_no.py`
üzerinden yapılır (K-1: tek kapı). Alan boşsa `None` yazılır, tahmin edilmez.

## D-275 — VKN doğrulaması ikinci algoritma yazılmaz

`ticaret_sicili_kanit.py` ilk halinde **kendi VKN algoritmasını** yazıyor ve
gerçek VKN'leri reddediyordu (ikiz mantık riski). Bağlayıcı tek kapı:
`src/company_master/etl/kimlik_no.py::vkn_gecerli`.

**Karar:** İkinci uygulama yasak. Bkz. K-1.

## D-276 — TOBB girişi: `multipart/form-data` kök nedeni (2026-09-29)

**Gözlem (ölçüldü):** Doğru e-posta/şifre ile giriş yine başarısız, sunucu
tam olarak `0` dönüyor. Sayfa kaynağında form `enctype="multipart/form-data"`
ve JS `new FormData(this)` ile POST ediyor.

**Karar:** `httpx` `data=` yerine **`files=`** kullanılır
(`{"Alan": (None, deger)}`). Başarıda sunucu **tam olarak `"1"`** döner.
Doğrudan TOBB hesabı kullanılır — **e-Devlet sorgu geçmişi oluşmaz**.

**Yan ölçüm:** oturum ömrü **~2-3 dakika**; sunucu tek çerez veriyor
(`atrsrv-*`). Çerez diske yazılıp geri yükleniyor (`cookie_kaydet/yukle`).

## D-277 — "Tüm Ankara tek seferde" önerisi: ÖLÇÜLDÜ, MÜMKÜN DEĞİL

KAHİN'in önerisi canlı denendi:
`POST /view/hizlierisim/ilangoruntuleme_ok.php` + `SicilMudurluguId=18` +
tarih aralığı → sunucu **reddediyor**:
*"Sicil No veya En Az 5 Karakter Ticaret Unvanı Giriniz"*.

**Karar:** İl+tarih tek başına sonuç vermez. Gerçek toplu yol
`TicaretUnvani` (ölçüldü: `AKANA` → **71 ilan tek istekte**, sayfalama yok).
14.000 firma = 14.000 unvan/sicil sorgusu; "fırsat" değil, aynı yük.

## D-278 — OCR GEREKMEZ; TOBB abonelik verisi XML'dir (KAHİN düzeltmesi)

**Tetikleyici:** KAHİN "gövdeler XML/ham metin olarak iletilir, PDF'e gerek
yok" dedi. Benim önceki "PDF scan → OCR şart" kararım **gerekçesizdi**.

**Doğrulama (ölçüldü):** resmî Abonelik sayfasının tablosunda 3. sütun
**"HİZMET SUNUŞ ŞEKLİ"** ve üç seviyenin de hizmeti **"WEB SERVİS"**.

| Düzey | Aranabilirlik | 2026 | Birim |
|---|---|---|---|
| Düzey_1 | **Aranamaz (non-searchable)** PDF | 484.932 TL | 0,521 TL/ilan |
| Düzey_2 | Aranabilir | 951.792 TL | 1,023 TL/ilan |
| **Düzey_3** | **Aranabilir** | **1.427.688 TL** | **1,535 TL/ilan** |

**Kararlar:**
1. **OCR hattı pasife alındı, SİLİNMEDİ.** `OCR_ETKIN=False` +
   `OcrPasifHatasi` kapısı + `--aktif` / `--durum`. Kapalıyken **HTTP atılmaz**
   (`tests/test_gazete_ocr_pasif.py`). Yeniden lazım olabilir.
2. **Ayrım kanıta bağlandı:** *ücretsiz üye PDF'i* gerçekten scan (ölçüldü:
   `font=0`, `Tj=0`, `ToUnicode=0`, 3 görsel XObject, A4@200DPI) → o yol
   OCR'a muhtaç. *Abonelik verisi* ise makine-okunur → OCR gerektirmez.
3. **Düzey_3 alan listesi** projenin tam boşluklarını kapatıyor: NACE ana+alt,
   **Vergi No**, Vergi Dairesi, UAVT Adres Kodu, Ortaklar (sermaye dahil),
   Temsilciler, Amaç Konu, Müfterek Listesi (JSON).
4. **Yasal uyarı (sayfada yazılı):** *"Gazetede yayımlanan ilan metni esas
   kabul edilmeli."* Ham veri **kaynak değil, aday**; `IlanKaniti` kapısından
   geçmeden `company_master`'a girmez.
5. **Satın alma kararı KAHİN'inkidir** (1.427.688 TL). Öneri: önce
   **MERSİS merkezî** sorguyu değerlendir (ücretsiz olabilir).

**Genel ders:** kütüphane "boş döndü" dedi → **scan mı metin katmanı mı
ayırt edilmeden karar verilmez**; `scripts/pdf_kanit_analiz.py` ile ölçülür.
Kullanıcının alan bilgisi **reddedilmez, doğrulanır** — burada doğrulanınca
iki günlük OCR işi boşa çıktı.

## D-279 — Abonelik 1 aylık DEĞİLDİR, ama KAPSAM TESPİTİ DOĞRU (KAHİN itirazı)

**KAHİN'in itirazı:** *"1 aylık ücret ödemekle firma bilgilerini tam toplanmaz;
ücret sadece o ayın şirket bilgilerini gösterir, açılış kapanış vs; aradığımız
veri orada değil."*

İki ayrı iddia var; ikisi de ölçüldü.

### 1. "1 aylık" → **YANLIŞ** (sayfada yazılı)

| Kanıt | Alıntı |
|---|---|
| Süre | **"(Yıllık)"** — üç seviyenin de satırında |
| Hesap | *"2026 yılında **251 iş günü** vardır. (251 x 1.932) = 484.932 TL"* |
| Günlük ayrı ürün | *"2026 yılı bir günlük gazete ücreti **2.730 ₺**"* |

→ Abonelik **yıllık**, 251 iş gününün tamamı. Aylık değil.

### 2. "Sadece o dönemin verisi / aradığımız veri orada değil" → **DOĞRU**

Empirik ölçüm — `448217` (AKANA) üzerinde **4 ilan** bulundu:

| Yayın yılı | İlan türü |
|---|---|
| 2026 | ŞUBE (ADRES DEĞİŞİKLİĞİ) |
| 2026 | ŞUBE (YÖNETİM - TEMSİL) |
| **2025** | ŞUBE (YÖNETİM - TEMSİL) |
| **2020** | ŞUBE AÇILIŞ |

> **2026 aboneliği bu 4 ilanın yalnızca 2'sini kapsar → %50.**
> Geçmiş yıllar ayrı alınır; "fihrist" ilan türlerini içerir, **firma
> sicil kaydının tamamını değil**.

Kanıt: `scripts/abonelik_kapsam_olcer.py` → `data/kesif_abonelik_kapsam.json`

### Karar

1. **TOBB aboneliği 14.000 firmanın TAM sicil verisini vermez.** Kullanıcının
   çekincesi ölçümle doğrulandı. 1.427.688 TL **bu iş için harcanmaz.**
2. **Düzey_3'ün gerçek değeri:** *zaman-serisi*. Tek bir firmanın yıllar boyu
   tüm ilan hareketi (kuruluş, adres, temsilci, sermaye) → **büyüme/çöküş
   sinyali**. 14.000 firma × 1 anlık görüntü değil, **birden çok yılın
   farkı**. Sektör analizi ve OSINT zenginliği için değerlidir — ama
   "firma master verisi" işini **çözmez.**
3. **Firma master verisi (adres, ortak, temsilci, VKN, NACE) MERSİS veya
   Ticaret Sicili Müdürlüklerinden gelir.** TOBB = türetilmiş/ikincil kaynak.
4. **D-278'in satın alma önerisi GERİ ÇEKİLDİ.** Düzey_3 alınmayacak.

> **Net sonuç:** TOBB kanıt katmanı **tekil doğrulama + değişim tespiti** için
> kalır (ücretsiz, kanıtlı). 14.000'lik ana veri → **MERSİS merkezî**.

## D-280 — OCR "daha ucuz" DEĞİLDİR; erişim ve doğruluk darboğaz (KAHİN)

**KAHİN'in yönlendirmesi:** *"Düzey_3 (1.427.688 TL) OCR ile taramak daha ucuz...
abonelik sonraki süreçte yapılabilir."* → Doğru yön, **gerekçesi ölçüldü ve
kısmen çürütüldü.** Tahmin yapılmadı: `scripts/ocr_maliyet_olcer.py` çalıştırıldı
(7 model denendi, 1 sayfa canlı).

### 1. Erişim: 7 modelden **1'i** çalışıyor

| Model | Sonuç |
|---|---|
| `openai/gpt-4o-mini` | ✅ **TAMAM** |
| `gc/gemini-2.5-flash-lite` | ❌ 403 (yetki yok) |
| `bzl/gemini-3.1-pro-preview` | ❌ 402 (kredi yok) |
| `cl/openai/gpt-4o` | ❌ 402 (kredi yok) |
| `ag/gemini-3.5-flash-low` | ❌ boş cevap |
| `ag/gemini-3.6-flash-low` | ❌ boş cevap |
| `gemini/gemini-3.5-flash-lite` | ❌ boş cevap |

→ **Erişim tek darboğaz.** Yedek model havuzu yok; 1 sağlayıcı çökerse hatt durur.

### 2. D-280 KÖK NEDEN (yeni bulgu): cevap ayrıştırma hatası

`openai/gpt-4o-mini` **HTTP 200** döndü ama `r.json()` patladı:
`JSONDecodeError: Extra data: line 37`. Gövdenin sonu: `data: [DONE]`
— **SSE kalıntısı JSON'a eklenmiş**. Model cevabı **geçerliydi**, ayrıştırma
başarısızdı.

**Çözüm:** `_cevap_ayikla()` — önce `r.json()`, hata olursa `data:` kalıntısı
kesilip elle ayrıştırılır.

> Ders: "OCR çalışmıyor" sandım; aslında **istemci hatalıydı**.

### 3. Ölçülen maliyet ve süre (tek sayfa, gerçek)

| Ölçüm | Değer |
|---|---|
| Model | `openai/gpt-4o-mini` |
| Süre | **5,89 sn** |
| Token | **49.146** |
| Çıkarılan alan | 9 |

**Projeksiyon (ölçümden türetildi, varsayım yok):**

| Kapsam | Token | Süre |
|---|---|---|
| 14.000 firma | 688 milyon | **~23 saat** |
| 930.000 ilan (tam yıl) | 45,7 milyar | **~63 gün** |

> **D-280 KARARI:** "OCR daha ucuz" **DOĞRULANMADI.** Düzey_3 (yıllık
> 1.427.688 TL) karşısında OCR'ın avantajı **belirsiz**: 14.000 ölçekte
> makul, 930.000'lik tam yıllık kapsamda **63 gün** sürer.

### 4. Doğruluk: OCR **MERSİS'te hata yaptı** (kritik)

| | Değer | Hane |
|---|---|---|
| Ekrandaki gerçek | `0012032074100024` | 17 |
| OCR çıktısı | `001203074100024` | **15** |

`2074` → `0741`: **kayıp hane.** Yani OCR **sessizce bozuk** veri üretti.

**D-274 kanonik kapısı bunu YAKALADI:** 15 hane → `mersis_kanonik_16 = None`
(reddedildi), 17 hane → kanonikleştirildi. *Kanonik kapı olmasaydı bu bozuk
değer `company_master`'a girerdi.*

### 5. Karar

1. **OCR tek başına 14.000 ölçekte denenebilir** (~23 saat, erişim çalışırken)
   — ama **çıktı zorunlu olarak kanonik kapıdan geçmeli** (D-274).
2. **930.000'lik tam yıl kapsamı OCR ile pratik DEĞİLDİR** (63 gün + tek
   sağlayıcı riski) → ileride abonelik buysa **Düzey_3 makul**.
3. **Abonelik kararı KAHİN'inkidir; bu ölçüm kararın girdisidir.** Şimdilik
   alınmaz — kabul edildi.
4. **OCR hattı PASIF kalır** (D-278). Maliyet ölçümü `--aktif` ile yapıldı.

> **Genel ders:** "X daha ucuz" iddiası, **ölçülmeden kabul edilmez.**
> Buradaki gerçek darboğaz fiyat değil, **erişim ve doğruluk** oldu.

## D-281 — e-Devletsiz kaynak araştırması: OSTİM = 8.473 firma, ücretsiz, yasal

**Soru:** e-Devlet kullanmadan 14.000 firmanın verisi toplanabilir mi?
**Yöntem:** Tahmin değil, ölçüm. `scripts/osb_kaynak_olcer.py`,
`osb_veri_yapisi_olcer.py`, `osb_api_avla.py`, `ostim_detay_olcer.py` (canlı).

### 1. MERSİS ve Bakanlık hizmetleri → **e-Devlet zorunlu** (ölçüldü)

| Kaynak | Bulgu |
|---|---|
| `mersis.gtb.gov.tr` / `mersis.ticaret.gov.tr` | *"E-Devlet Yönetimi ile Giriş entegrasyon aşamasındadır"* |
| `turkiye.gov.tr/gtb-ticari-isletme-ve-sirket-sorgulama` | Giriş: e-Devlet şifresi / e-İmza / TCKK / İnternet bankacılığı |
| `ticaret.gov.tr/…/e-devlet-hizmetlerimiz` | "Ticari İşletme ve Şirket Sorgulama" **e-Devlet** altında |

> **Sonuç:** e-Devletsiz **resmî merkezî** yol **yoktur**. D-279'daki
> "MERSİS merkezî" önerisi bu nedenle **e-Devlet'e bağımlı** çıktı.

### 2. Alternatif kaynaklar → **8/8 erişilebilir** (ölçüldü)

`ostim.org.tr` (200) · `atonet.org.tr` (200) · `atb.org.tr` (200) ·
`aso.org.tr` (200) · `gib.gov.tr` (200) · `ticaret.gov.tr` (200)

**Yasal kapı açık** (`robots.txt` ölçüldü):
- `ostim.org.tr` → yalnız `/admin/`, `/portal/`, `/auth/` yasak
- `atb.org.tr` → `Allow:` (tümü serbest) · `aso.org.tr`, `atonet.org.tr` → engel yok

→ `/firmalar` taraması **robots.txt'e aykırı DEĞİLDİR.**

### 3. ⭐ OSTİM: 8.473 firma, sayfalama ile TAM toplanabilir

Sayfa metninde **ölçüldü**: `Toplam 8473 sonuç bulundu`

| Ölçüm | Değer |
|---|---|
| Toplam firma | **8.473** (sayfada yazılı) |
| Sayfa başına | 300 |
| Sayfa sayısı | **29** |
| Doğrulama | sayfa 1+2+29 → 300+300+**73** = 673 ✓ (son sayfa 73) |
| Sayfa 30 | 0 sonuç → sınır doğru |

> **8.473 = 14.000 hedefinin %61'i, ücretsiz, yasal, kalıcı adresli.**

### 4. Alan eksikliği — OSTİM tek başına YETMEZ (ölçüldü)

Detay sayfası alan taraması (**11 alan denendi, 6 bulundu**):

| Alan | Durum |
|---|---|
| unvan · adres · telefon · e-posta · web · faaliyet · sektör | ✅ |
| **NACE** · **VKN** · **ticaret sicil no** · yetkili/ortak | ❌ **YOK** |

> **Karar:** OSTİM = **kimlik + iletişim** kaynağı (VKN olmadan join
> kurulamaz). Eksik alanlar **GIB VKN** ve **Ticaret Sicili** ile
> tamamlanmalı. OSTİM tek başına master veri **DEĞİLDİR** (D-216).

### 5. Karar

1. **MERSİS önerisi D-281 ile düzeltildi:** e-Devlet zorunlu → kullanıcının
   istemediği yol. **Ana kaynak olarak düşüldü.**
2. **OSTİM 8.473 firma** → ücretsiz temel küme olarak alınabilir
   (izinli, kalıcı adresli, sayfalama ölçülmüş).
3. **Entegrasyon zorunlu:** OSTİM (unvan/adres) → **GIB VKN** →
   **Ticaret Sicili/MERSİS**. Her biri kendi kapısından geçer.
4. **Bu bir araştırma turudur; toplu indirme BAŞLATILMADI.** Ölçek işi için
   ayrı görev + KAHİN onayı gerekir (bir önceki borçta açık kalan madde).
5. **VATAN/Hukuk onayı:** ticari amaçlı toplu derleme için kaynak kurumların
   kullanım şartları ayrıca doğrulanmalıdır. `robots.txt` izni hukuki
   izin **değildir.**

> **Genel ders:** "e-Devlet gerekir" önyargısı ölçümle çürütüldü; resmî
> merkezî yol kapandı ama **8.473 firma ücretsiz ve yasal** bulundu.

## D-282 — Hukuk + VKN araştırması: iki ÖNEMLİ bulgu (KAHİN)

KAHİN iki konuyu birden istedi: (1) hukuki uygunluk, (2) GİB VKN yolu.
İkisi de **ölçüldü**. Birincisi **kritik engel**, ikincisi **zaten yapılmış iş**.

### 1. ⛔ OSTİM Kullanım Koşulu — ticari kullanımı açıkça yasaklıyor

**Alıntı** (`ostim.org.tr/kurumsal/gizlilik-politikasi` → "Kullanım Koşulları"):
> *"Bu web sitesi sadece **bilgi amaçlı ve ticari olmayan** kullanım için
> hazırlanmıştır."*

Aynı politikanın diğer hükümleri:

| Hüküm | Alıntı |
|---|---|
| Üçüncü tarafa aktarım | *"elde edilen veriler belirlenen amaçlar ve kapsam dışında **üçüncü kişilere açıklanmayacaktır**"* |
| Ziyaretçi verisi | *"ziyaretçilerin kişisel verilerini **toplamaz** ve herhangi bir üçüncü tarafa **vermez**"* |
| Gerekçe | *"gizli bilginin tamamının veya herhangi bir kısmının **kamu alanına girmesini**… engellemek için tüm tedbirleri alma"* |

> **D-282 KARARI:** OSTİM 8.473 firma listesi **ticari amaçlı ürün verisi
> olarak kullanılamaz.** D-281'deki "8.473 ücretsiz ve yasal" ifadesi
> **DÜZELTİLDİ**: teknik olarak erişilebilir, ama **ticari kullanım
> koşulu bunu yasaklıyor.**
>
> Bu, 14.000'lık hedef için ciddi darboğazdır. Karar **KAHİN'in.**

### 2. ✅ GİB VKN yolu: e-Devlet zorunlu

| Kaynak | Bulgu |
|---|---|
| `turkiye.gov.tr/gib-intvrg-vergi-kimlik-numarasi-sorgulama` | e-Devlet şifresi / e-İmza / TCKK / bankacılık |
| `gib.gov.tr/…/vergi-kimlik-numarasi-sorgulama` | HTTP 200 ama **içerik boş** (JS-rendered) |
| `gib.gov.tr/e-hizmetler`, `/acik-veri` | **404** — yayımlanmıyor |
| `gib.gov.tr/…/VERI_PAYLASIMI.pdf` | **404** |

> Projenin kendi notu (`vkn_bulma_stratejisi.md` §7) bunu zaten yazmıştı:
> *"GİB VKN Doğrulama (vkn.gov.tr) — sorgu servisi **captcha/bot korumalı**;
> tekil doğrulama için uygun, **toplu kazımaya uygun değil**."*
> Ölçüm bunu **doğruladı**. GİB'de e-Devletsiz toplu yol **yok**.

### 3. ⭐ En önemli bulgu: VKN işi **zaten denenmiş ve başarısız olmuş**

Projede mevcut çıktı ölçüldü — `data/ostim/firmalar_vkn_ekli.jsonl`:

| Ölçüm | Değer |
|---|---|
| Toplam kayıt | **5.040** |
| unvan · adres · sektor · slug | **%100** |
| telefon | %92 · e-posta %48 · web %100 |
| **`vergi_no`** | **%0 — 5.040/5.040 boş** |

**Neden başarısız olduğu loglarda yazılı** (`logs/vkn_extractor_v2.log`):
> `İşlenen: 5485/5485, **VKN bulundu: 3**, Atlanan placeholder: **2.646**,
> Çekim hatası: 774`

> Yani 5.485 denemenin **5.482'si (%99,9) sonuç vermedi.**
> Web kazıması da (`vkn_web_run2.log`): *"Taranan site: 30, **VKN bulunan: 0**"*.

**Kök neden (yeni):** OSTİM detay sayfası **VKN'yi hiç yayımlamıyor**
(ölçüldü: 11 alan denendi, `vergi_no` **yok** — D-281). Yani web kazıması
hedefi **kaynağın vermediği** bir alandaydı.

### 4. Bağımlılık tuzağı (D-282 kuralı)

`data/ostim/firmalar_vkn_ekli.jsonl` 5.040 satır, `web_sitesi` %100 dolu —
ancak bunlar **OSTİM'ın kendi listelediği** alanlar. Proje kaydı bunları
"kaynak" sanıyor. Oysa:
- OSTİM → unvan/adres/telefon/e-posta (VKN **yok**)
- Web → site var ama içinde VKN çıkmadı (%0)
- GİB → e-Devlet

> **Sonuç: VKN eksikliği OSTİM kaynaklı DEĞİLDİR; proje içi bir
> varsayımdan kaynaklanmıştır.** Yeniden denemek aynı sonucu verir.

### 5. Karar tablosu

| Alan | Durum |
|---|---|
| OSTİM 8.473 (ticari) | ⛔ **Koşulla yasak** (D-282 §1) |
| GİB VKN e-Devletsiz | ❌ **Yok** (ölçüldü) |
| Web kazıması VKN | ❌ **Zaten denendi: %0** |
| MERSİS | ❌ e-Devlet |
| TOBB Düzey_3 | ❌ Kapsam yetersiz (D-279) |

> **Açık kalan tek yasal yol: e-Devlet (KAHİN'in önceki tercihi) veya
> OSTİM'den resmî yazılı izin.** Her ikisi de KAHİN'in kararıdır.

> **Genel ders:** "VKN web'den bulunur" varsayımı **3 kez ölçüldü** ve
> 3'ünde de başarısız çıktı. Var olmayan alanı kazımak boşa çalışmaktır;
> **önce kaynağın alanı var mı diye bak.**

## D-283 — Veri çekme politikası + KIYASLAMA cevabı (KAHİN onayı)

> KAHİN: *"veriyi ticari kullanılacak şekilde çek, kolon kolon, tane tane,
> doluluk oranları ile referansla, kolonları karıştırma. Politikamız var,
> listeyi yap. Sonra ihsan'a gönder."*

### 1. Kaynak adresleri (ölçülmüş)

| # | Adres | Doğrulama |
|---|---|---|
| 1 | `https://ostim.org.tr/firmalar` | `Toplam 8473 sonuç` |
| 2 | `https://ostim.org.tr/firmalar?page=N` | 300+300+73 ✓, sayfa 30 boş |
| 3 | `https://ostim.org.tr/firmalar/<slug>` | HTTP 200, 78.554 bayt |
| 4 | `https://ostim.org.tr/sitemap.xml` | 10 URL — **firmaları içermez** |
| 5 | `https://ostim.org.tr/robots.txt` | `/admin/`, `/portal/`, `/auth/` yasak |

### 2. Çekme politikası P-1..P-10 (KAHİN onayladı: 2026-09-29)

| # | Kural | Uygulama | Dayanak |
|---|---|---|---|
| P-1 | Sahte UA yok | Sabit gerçek UA | politika |
| P-2 | Sayfa başına 1 istek | 1 liste + 1 detay | ölçüm |
| P-3 | Nazik gecikme | **2 sn** | nazik kazıma |
| P-4 | Gece vardiyası yok | 3.297 firma ≈ **1,8 saat** | hesap |
| P-5 | 403/401 = **açık hata** | boş liste sayılmaz | **K-5** |
| P-6 | `tekil/toplam < %95` → **başarısız** | tur reddi | **K-4** |
| P-7 | Ham dosya `"w"` | kopyalamaz | **K-3** |
| P-8 | Sayfa imzası tekrarında dur | 3 koruma | **K-1** |
| P-9 | Yeniden çalıştırılabilir | durum dosyası | **K-1** |
| P-10 | Maskeli alan kopyalanmaz | KVKK | — |

### 3. Filtreleme — kolonlar KARIŞTIRILMAZ (K-2)

| Kolon | Kural |
|---|---|
| `unvan` | Asla normalize/kısaltma edilmez (D-11) |
| `adres`·`telefon`·`emailler` | **Yalnız OSTİM detay sayfasından** |
| `nace_code` | `nace_source` ile birlikte; tahmin ≠ resmi |
| `nace_confidence` | high=resmi · medium=türetilmiş · none=yok |
| `vergi_no` | Yalnız doğrulanmış; tahmin yasak (D-274) |
| `kaynak_adi` / `kaynak_turu` | `ostim` / `osb` (K-2 zorunlu kolon) |

> **Ölçülen K-2 riski:** `firmalar_full.jsonl` NACE'leri **4 haneli ve
> `sektor_reverse`** (türetilmiş tahmin) — 7.047 kayıt. ASO'nun resmi 6
> haneli NACE'i ile **aynı güvenle karıştırılmamalı.**

### 4. ⭐ KIYASLAMA CEVABI (KAHİN'in asıl sorusu)

`scripts/veri_karsilastir.py` → `data/karsilastirma_raporu.json`

| Set | Kayıt | adres | web | sosyal | sektor | NACE |
|---|---|---|---|---|---|---|
| `firmalar_full` | 8.313 | ⛔ %0 | ⛔ %0 | ⛔ %0 | %69,4 | %84,8 (4 hane, türetilmiş) |
| `firmalar_vkn_ekli` | 5.040 | ✅ %100 | ✅ %100 | ✅ %100 | ✅ %100 | — |

| Ölçüm | Değer |
|---|---|
| Ortak unvan | 4.954 (%60,0) |
| **`b` ile yeni unvan** | **0** |
| `a` ile kalan (detaysız) | **3.297** |

**Zenginleştirme katkısı** (eşleşen 4.954): `adres` +4.952 · `web_sitesi`
+4.952 · `sosyal_medya` +4.952 · `sektor` +1.398 · `vergi_no` **0**

> **CEVAP: EVET zenginleştirir** — ama **3 kolonda**, ve yeni firma
> getirmez. Asıl kazanç: **3.297 firmanın adres/web/sosyal medya alanı.**
> `vergi_no` sorunu çözülmez (D-282: hiçbir kaynakta yok).

**KAHİN ONAYI (2026-09-29):** Politika P-1..P-10 uygulanacak; 3.297 eksik
detay taranacak; ardından ihsan'a teslim.

## D-284 — Organize hareket + izin dilekcesi + birlestirme (D-283 devam)

KAHİN: *"ihsan ajanı ile organize hareket edin… problem varsa ihsan
ajanına chat'ten yaz, bekliyorum."*

### 1. İhsan'a yazıldı (ajan chat D-210 — zorunlu kanal)

`data/orchestrator/ajan-chat.jsonl` → **3 kayıt** bu görevde:

| Önem | Konu |
|---|---|
| kritik | OSTIM detay sayfası **K-2 ihlali** (kolon karışması) + düzeltme |
| yuksek | **Kıyaslama sonucu** (zenginleşme ölçümü) |
| yuksek | **Görüşme talebi** (2 karar: izin adımı + birlestirme sahipliği) |

Ayrıca `chat_gonder.py` ile **2 mesaj** (`data/orchestrator/chat/messages.jsonl`).

### 2. ⛔ K-2 İHLALİ — tarama sırasında yakalandı ve düzeltildi

KAHİN'in uyarısı üzerine kolonlar tek tek denetlendi. İlk pilot çıktısı
**kullanılamazdı**:

| Kolon | Çıkan (YANLIŞ) | Neden |
|---|---|---|
| `web_sitesi` | `htk.org.tr` | fuar sitesi, firma değil |
| `sosyal_medya` | `ostim-osb` | **sitenin kendi** sosyal hesabı |
| `adres` | boş | etiket `<strong>` ile geliyordu |

**Kök neden:** Sayfada iki ayrı blok var — (1) firma bilgi kutuları,
(2) site menüleri/footer. İlk sürüm bunları **ayırmıyordu**.

**Düzeltme:** `_bilgi_kutulari()` yalnız
`<p bg-secondary fw-bold>Başlık</p><div bg-light>…</div>` kutularını okur;
anahtar `bölüm:etiket` olur (`Merkez:Telefon`).

**Doğrulama (gerçek çıktı):**
```
Merkez:Telefon → +90 552 005 29 35
Merkez:Adres   → AHIT EVRAN CAD. 63
Merkez:E-Posta → mehmetcantugay1@gmail.com
```
Pilot: **5/5 başarılı**, P-6 tekil oranı **%100**, 0 hata.

### 3. İzin dilekçesi taslağı hazırlandı

`scripts/ostim_izin_dilekcesi.py` → `plans/OSTIM-izin-dilekcesi-taslagi.md`
(2.606 karakter). Kapsam dışı bırakılanlar **yazılı**: VKN, ortak, temsilci
kimlik bilgisi, mali tablo. Teknik taahhütler: robots.txt, 2 sn bekleme,
sahte UA yok, günlük limit.

> **Gönderimi KAHİN yapar** (resmî yanıt kurumun adına yazılmalı).

### 4. Birlestirme hazır (kuru çalışma ölçüldü)

`scripts/ostim_set_birlestir.py --kuru`:

| Ölçüm | Değer |
|---|---|
| liste | 8.313 |
| detay | 5.045 |
| **çıkış** | **8.313** (artış yok — doğru) |
| unvan eşleşmesi | 5.002 |

**Doldurulan alanlar:** `web_sitesi` +5.000 · `sosyal_medya` +5.000 ·
`adres` +4.997 · `sektor` +1.410 · `emailler` +9 · `telefonler` +2

**Doluluk değişimi:**

| Kolon | Önce | Sonra |
|---|---|---|
| **adres** | %0,0 | ✅ **%60,1** |
| **web_sitesi** | %0,0 | ✅ **%60,1** |
| **sosyal_medya** | %0,0 | ✅ **%60,1** |
| sektor | %69,4 | ✅ %86,4 |
| `vergi_no` | %0,0 | %0,0 (değişmedi — kaynak yok) |

**K-2 uyum ölçüldü:** `kaynak_adi` + `kaynak_turu` her kayıtta ✓ ·
`vergi_no` yalnız doğrulanmış ✓ · NACE tahmini `nace_source` ile işaretli ✓

### 5. Karar

1. **Birlestirme kodu hazır ve kuru çalışmada doğrulandı** — dosyaya
   yazılmadı (`--kuru`), çünkü ihsan'ın yönlendirmesi bekleniyor.
2. **Detay taraması** (3.297) izin sonrası başlayacak.
3. **ihsan'dan beklenen:** (a) izin adımının sahibi, (b) birlestirme
   sorumluluğu.
## D-285 — OSTİM birleştirmesi kalite denetimi: kirp ölçüldü, 10.002 → 0

**Tarih:** 2026-09-29 · **Ajan:** yasu · **Görev:** ALTYAPI-TICARET-KANIT-01

### 1. Bağlam

D-283'te parser düzeltmesi sonrası "site/footer verileri firma kolonlarına
karışmış" uyarısı vardı ama **ölçülmemişti**. D-285 bu iddiayı ölçer ve
kanıtlanan kısımları düzeltir.

### 2. Karar

1. **Birleştirme çıktısı kalite denetiminden geçmeden teslim edilemez.**
   Araç: `scripts/birlestirme_kalite_kontrol.py` · Rapor:
   `data/birlestirme_kalite_raporu.json`.
2. **"Aynı değer binlerce firmada" ölçümü zorunlu kuraldır.** Tekil oranı
   %50'nin altına düşen kolon kirp sayılır ve teslim edilmez.
3. **Filtre listeleri tahminle değil ÖLÇÜMLE yazılır.** Ölçüm bir
   domain'de/numarada tekrar göstermiyorsa liste **boş bırakılır** —
   doğru veriyi silmemek, kirli veriyi tutmaktan önce gelir.
4. **Dolgu metni alan bazlı uygulanır.** `-` ve `n/a` yalnız serbest metin
   alanlarında geçersizdir; URL ve telefon alanlarında aranmaz.
5. **Birlestirme temizdir** (K-2 kaçış = 0). Detay taraması yazılı izin
   olmadan başlatılmaz (D-281 borcu).

### 3. Ölçülen bulgular

| # | Kolon | Kirp | Adet |
|---|-------|------|------|
| 1 | `sosyal_medya` | OSTİM'in kendi hesapları (`OstimOSB`, `ostim-osb`, `x.com/ostimosb`) | **5.000** |
| 2 | `web_sitesi` | `isim.org.tr` (OSB altyapısı) | **2.155** |
| 3 | `web_sitesi` | `ostimistihdam.com` (iş başvuru portalı) | **475** |
| 4 | `web_sitesi` | `htk.org.tr` (fuar/organizasyon domain'i) | 2 |
| 5 | `adres` | `"Adres bilgisi girilmemistir"` dolgu metni | 87 |

**Toplam K-2 kaçışı: 10.002 → 0.**
Web tekillleşme oranı: **%46,7 → %97,7.**

### 4. Telefon taraması — boş sonuç dürüstçe kaydedildi

Varsayım: "OSTİM merkez telefonu her firmada tekrar ediyor" → sabit numara
listesi yazıldı. **Ölçüm bunu çürüttü:** en çok tekrar eden numara 5 kez
(`903124397800`). Yani merkez numara veriye *bulaşmamış*. Liste
`frozenset()` olarak **boş bırakıldı**; tahminle iyi telefon numaraları
silinmedi. Regresyon testi buna karşı koruma içerir.

### 5. Regresyon testi iki gerçek hatayı yakaladı

## D-289 — İzin taslağı hazır; kazıyıcı politikaya uyduruldu

**Tarih:** 2026-09-29 · **Ajan:** yasu · **Görev:** ALTYAPI-TICARET-KANIT-01
**KAHİN kararı:** izin başvurusunun sahibi **KAHİN**; yasu izinli olarak
devam edecek.

### 1. Dilekçe — iki hata düzeltildi

`plans/OSTIM-izin-dilekcesi-taslagi.md` yeniden üretildi
(`scripts/ostim_izin_dilekcesi.py`).

1. **Yanlış kanıt dosyası atfı.** Eski taslak
   `data/ostim_kaynak_olcumu.json` dosyasına atıf yapıyordu; **dosya
   yoktu**. Yerine gerçekten var olan kanıtlar yazıldı.
2. **8.473 iddiası ölçümle çelişiyordu.** Site "Toplam 8473 sonuç"
   diyor, elimizdeki liste 8.313 (8.313 benzersiz slug, tekrar yok).
   Fark **ölçüldü**: liste 28-29. sayfalarında 13 yeni firma var —
   liste tarama sırasında güncellenmiş. Dilekçe artık iki sayıyı da
   ayrı ayrı veriyor ve farkın kaynağını belirtiyor.
   Kanıt: `data/ostim/kapsam_dogrulama.json`.

Ayrıca politika metni **canlı olarak yeniden okundu**; dosyadaki kopya
bozuktu (HTML entity kaçışları çözülmemiş: `G├╝ZL├╝L├╝K`). Birebir
alıntı: *"Bu web sitesi sadece bilgi amaçlı olarak ticari olmayan kullanım
için hazırlanmıştır"*. `robots.txt` birebir doğrulandı (`/firmalar/`
**serbest**).

### 2. Kazıyıcı — 4 politika maddesi kodda DEĞİLDİ

D-283'te yazılan politika P-1..P-10'un dördü hiç uygulanmamıştı:

| Politika | Durum | Düzeltme |
|---|---|---|
| P-3 2 sn gecikme | `time.sleep` **hiç çağrılmamıştı** (beyaz satır) | `if i > 1: time.sleep(GECIKME)` |
| P-8 sayfa imzası | fonksiyon yoktu | `imza()` + tekrarında kayıt **atlanır** |
| P-1/P-2 robots.txt | `robots_kontrol` parametresi **hiç tanımlı değildi** | `robots_uyumlu_mu()`, varsayılan **açık** |
| P-9 güvenli resume | dosya `"w"` ile **yeniden yazılıyordu** | mevcut kayıtlar okunur, slug ile birleştirilir |

P-9 bulgusu en ciddisiydi: 3.297 kayıt `--limit 500` ile 7 parçaya
bölünseydi, **her parçada önceki 6 parçanın verisi silinirdi**.

### 3. Pilot — "5/5" yetmezdi, satır denetimi gerekti

İlk pilot K-2 açısından temizdi (0/5 kirp) ama sosyal medyada
`{"instagram": "accounts"}` vardı. Bu bir hesap değil, sayfadaki geçici
login linkinin (`/accounts/login/?next=`) son parçasıydı.

**Ders: regex doğru olsa bile sahte hesap üretebilir.** `_gercek_hesap_mi()`
eklendi; düzeltilmiş parser ile pilot tekrar koşuldu:

- 5/5 başarılı, 0 hata, P-3 uygulandı (11,1 sn = 2 sn × 5)
- `accounts` sahtesi **gitti**, gerçek `333Reklam` hesapları **korundu**
- K-2 kaçış **0/5**

### 4. Doğrulama

```bash
python -m pytest tests/test_ostim_detay_parser.py -q        # 17/17
python -m pytest tests/test_ostim_birlestirme_kalite.py -q  # 18/18
python -m pytest tests/test_ostim_detay_parser.py \
  tests/test_ostim_birlestirme_kalite.py -q                # 35/35
```

### 5. Karar

1. **Detay taraması izin gelene kadar başlatılmaz.** (D-281 borcu)
2. İzin geldiğinde hattın tümü hazırdır: P-1..P-10 uygulanmış, 35 test
   yeşil, kalite denetimi mevcut.
3. Eksik detay sayısı 3.297 değil **3.339** — liste güncellendiği için
   arttı (D-286 ölçümü).

### 6. Güvenlik borcu (açık)

- TOBB parolası sohbette açığa paylaşıldı ve `.env`'e yazıldı —
  **çıkış sonrası parola değiştirilmeli**
- `data/tobb_cookie.json` canlı oturum çerezidir; paylaşılmamalı


1. `_DOLGU_METIN` içindeki `-` **her alanda** aranıyordu. `sosyal_medya`
   bir dict olduğu için `str(dict)` üzerinde arama yapılıyor ve URL'li
   **her** hesap reddediliyordu — düzeltme, kirp veriyi temizlerken iyi
   veriyi de siliyordu. Alan bazlı düzeltme yapıldı (`_METIN_ALAN`).
2. `tests/test_ostim_detay_parser.py` fixture'ı gerçek sayfa yapısını
   yansıtmıyordu; parser'ın doğru olduğu ortaya çıktı.

### 6. Teslim edilen çıktı

- 8.313 kayıt, 8.275 tekil unvan, 19 kolon
- `kaynak_adi` / `kaynak_turu` %100 dolu
- NACE güven: `medium` 7.047 / `none` 1.266 — OSTİM resmî NACE
  yayımlamaz, sektörden türetilir (K-2)
- `vergi_no` 0 dolu — OSTİM'de VKN yoktur; bu kaynakla zenginleştirilemez

### 7. Ölçüm aracı

```bash
python scripts/birlestirme_kalite_kontrol.py   # statik denetim
python -m pytest tests/test_ostim_birlestirme_kalite.py -q   # 18/18
```


