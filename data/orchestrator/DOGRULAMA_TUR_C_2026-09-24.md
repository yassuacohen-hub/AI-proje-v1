# TUR-C — Bagimsiz Dogrulama Raporu (2026-09-24)

> **Rol:** denetci. Bu tur kod yazmadi, belge duzeltmedi. Tek istisna: ADIM 2 artik dosya silme.
> **Kanit kurali:** "rapor oyle diyor" delil degildir. `git log`, `git show`, `git ls-files`, dosya icerigi delildir.
> **Kapsam:** TUR-A (`c9a46cc`…`c3d3458`), TUR-B2 (`902c761`…`5bd47e6`), TUR-B (`36d9414`…`2f78507`) iddialarinin dogrulanmasi.
> **Kaynak denetim:** [`DENETIM_SUREC_2026-09-24.md`](DENETIM_SUREC_2026-09-24.md) — 20 bulgu (B-01…B-20).

---

## 1. ADIM 1 — Celiski sorusturmasi

TUR-B raporu B-06/13/15/16/19'u "kapsam disi / acik" yazdi; oysa ayni bulgular daha once kapandi diye raporlanmisti.
Iki olasilik sinandi: **(a)** TUR-B raporu yanlis, **(b)** degisiklikler geri gitti.

| Bulgu | TUR-B iddiasi | Git kaniti | HEAD durumu | Hukum |
|---|---|---|---|---|
| B-06 | `44250b9` ile kapandi | `44250b9` yalniz `gorev_kutusu.py`'ye 46 satir ekledi; pickaxe (`git log -S`) gercek commit'i **`c9a46cc`** gosterdi | Panoda Y1-Y6 `durum: yedek` (`-23`…`-28`) | **Rapor yanlis + hash atfi hatali** |
| B-13 | `c9a46cc` ile kapandi, sonra "acik" | `cmd_bakim()` satir 362-366 `arsiv_cakisma` basiyor | Kod HEAD'de duruyor | **Rapor yanlis — kapali** |
| B-15 | `b9e3ae6` ile kapandi, sonra "acik" | `b9e3ae6`: 3 yedek + `scripts/_clean_dup.py` silinmis; politika [`AGENTS.md:502`](../../AGENTS.md) yazili | Politika var; **disk artiklari duruyordu** | **Kismen acikti → TUR-C ile kapandi** |
| B-16 | `b9e3ae6` ile kapandi, sonra "acik" | diff'te `+ **Zorunlu (cp1254 karsiligi):**` satiri | [`AGENTS.md:95`](../../AGENTS.md) yerinde | **Rapor yanlis — kapali** |
| B-19 | `9f1df85` ile kapandi, sonra "acik" | HDI ici AGENTS.md 1 satir degisti | Kok `AGENTS.md:80` karar araligi guncel | **Rapor yanlis — kapali** |

### Karar

**(a) TUR-B raporu yanlis. Geri gitme (regresyon) YOK.**
Bes bulgudan dordu HEAD'de kapali; B-15 yalniz disk hijyeni yonuyle acikti ve bu turda kapatildi.
Ek olarak **B-06 kapanis commit'i yanlis atfedilmis** — rapor `44250b9` yaziyor, gercegi `c9a46cc`.

---

## 2. ADIM 2 — Artik dosya temizligi

Dayanak: [`AGENTS.md:394`](../../AGENTS.md) (gecici dosyalar `data/_tmp/` veya `_trash/`, is bitince sil) ve [`AGENTS.md:502`](../../AGENTS.md) (yedek saklama politikasi).

### 2.1 Karar tablosu

| Karar | Adet | Yontem | Gerekce |
|---|---|---|---|
| SIL (takipli) | 28 | `git rm` | Gecici cikti / bayat yedek; git gecmisinde geri alinabilir |
| SIL (takipsiz) | 4 | `del` | Tek seferlik betik, hic commit edilmemis |
| KALIR | 1 klasor | — | `_yedek_20260922_131011/` (20 ALARM json) — takipsiz, geri alinamaz, operasyon verisi |

### 2.2 `git rm` ile silinenler (28)

Kok dizin geçici ciktilari:
`gs.txt` · `d1.txt` · `gi.txt` · `mk_test.txt` · `difstat.txt` · `logger.exception'`

Tek seferlik betikler:
`assign_infra_to_utku.py` · `check_board_structure.py` · `check_tasks_status.py` · `optimize_board.py` · `final_board_optimize.py` · `filter_triggers.ps1` · `fix_roo_lock.bat`

D-192/D-193 test artiklari:
`d192_menu_test_log.md` · `d193_agent_browser_menu_test.bat` · `d193_agent_browser_menu_test.sh` · `d193_errors.jsonl` · `d193_menu_e2e_report.md` · `d193_status.txt`

Zaman damgali yedekler:
`.instructions.md.backup_2026-09-21` · `AGENT_SYNC.md.backup_2026-09-21` · `ANA_KURALLAR.md.backup_2026-09-21` · `CLAUDE.md.backup_2026-09-21` · `gorev_panosu.md.backup_2026-09-21` · `data/orchestrator/AGENT_SYNC.md.backup_2026-09-21` · `data/orchestrator/GIT-HIJYEN-01_rapor_2026-09-17_kilo.md.backup_2026-09-21` · `data/orchestrator/gorev_panosu.md.backup_2026-09-21`

Pano yedekleri + gitignore celiskisi:
`data/orchestrator/task_board_backup_20260911_2106.json` · `data/orchestrator/task_board_backup_20260911_2220_guncel.json` · `data/orchestrator/_p8_read.py` · `data/orchestrator/_p8_dump.txt`

> `_p8_read.py` / `_p8_dump.txt`: `.gitignore:53-54` bunlari zaten disliyor ama dosyalar **takipliydi** — gitignore takipli dosyayi etkilemez. Celiski giderildi.

### 2.3 Backup dosyalarinin HEAD'den farki

Hicbiri birebir kopya degildi (`fc /L` hepsinde FARKLI dedi) — yani "zararsiz kopya" degil, **bayat icerik**:

| Dosya | HEAD satir | backup satir | Fark |
|---|---|---|---|
| `.instructions.md` | 271 | 271 | icerik farkli, satir esit |
| `AGENT_SYNC.md` | 39 | 50 | backup 11 satir fazla (bayat) |
| `ANA_KURALLAR.md` | 264 | 258 | HEAD 6 satir yeni |
| `CLAUDE.md` | 103 | 101 | HEAD 2 satir yeni |
| `gorev_panosu.md` | 30 | 28 | HEAD 2 satir yeni |

### 2.4 `del` ile silinenler (4, takipsiz)

`data/orchestrator/_atama_3_gorev.py` (55 satir) · `_encode_baslik.py` (14) · `_sprint_add.py` (97) · `_test_baslik.py` (26)

### 2.5 Kalanlar ve gerekce

- `data/orchestrator/_yedek_20260922_131011/` — 20 ALARM json. Takipsiz, `.gitignore:64` kapsaminda (repoya girmiyor), **geri alinamaz**. Silme karari KAHIN'e ait, denetciye degil.
- `_tmp_tur_b5_fix.py` — listeden cikarildi: **diskte zaten yok**. VSCode sekmesi bayat gosteriyordu.

### 2.6 `.gitignore` eklemesi

```
# TUR-C Adim 2 (2026-09-24): gecici betik + zaman damgali yedek artiklari (AGENTS.md:394, :502)
_tmp_*
*.backup_*
```

**Commit:** `2583ce2` — 32 dosya.

---

## 3. ADIM 3 — Taze klon provasi

Amac: depo baska bir makineye/dizine tasininca calisir mi?

| Adim | Sonuc |
|---|---|
| `git clone -q --no-hardlinks` → `c:\_KLON_PROVA` | cikis kodu **0**, 88 ust duzey oge |
| Dal | `* chore/monorepo-merge` — checkout gerekmedi |
| `AGENTS.md` | 790 satir, eksiksiz |
| Kilavuz §11 adim 3 (`simulasyon --kuru`) | cikis kodu **0** |
| Kilavuz §11 adim 4 (`bak --ajan utku`) | cikis kodu **0**, 6 yedek gorev listelendi → B-06 kaniti klonda da gecerli |
| Kilavuz §11 adim 5 (`type AGENTS.md`) | calisti |
| `hubs/` | 11 dosya · `task_board.json` var · `plans/brief_*.md` 69 dosya |
| Klon `simulasyon` | cikis kodu **0** — **ama kontrol 5 ve 6 "ATLANDI: 02_admin_panel_hedef_dokumani.md diskte yok"** |
| Klon pytest | **7 failed, 4063 passed, 14 skipped, 16 errors** (129.71s) |
| Temizlik | `KLON-SILINDI` |

### 3.1 Klon test hatalarinin ayrimi

Ayni testler **ana depoda 4/4 passed**. Yani hatalarin hicbiri regresyon degil, **ortam kaynakli**:

| Test | Klon | Ana depo | Sebep |
|---|---|---|---|
| `test_pano_yolu_kanonik` | FAIL — `PANO_DOSYA kanonik yolda degil: C:\_KLON_PROVA\data\orchestrator\task_board.json` | PASS | Test **dizin adina bagimli** — yalniz `Huginn Data Insights` adli klasorde geciyor |
| `test_cmd_teslim_basarili` | FAIL — `HATA: T-01 hafiza izi yok` | PASS | Hub dosyasi klonda farkli durumda (B-14 kapisi) |
| `test_find_root_finds_env` | FAIL | PASS | Klonda `.env` yok |
| `test_api_companies.py` (3F + 16E) | FAIL/ERROR | — | DB baglantisi + `.env` yok |
| `test_metrics_prometheus_metni` | FAIL | PASS | Ayni sebep |

> **Kritik gozlem:** Klonda `simulasyon` **cikis kodu 0 verdi** ama iki kontrol sessizce atlandi. Yani gecerli bir "temiz" sinyali, aslinda eksik denetimi ortuyor. Kok neden bolum 5'te.

---

## 4. ADIM 4 — HEAD durum kontrolu

### 4.1 Sekiz kontrol (ana depo `simulasyon`)

**Cikis kodu 0 — 8/8 OK.**

| # | Kontrol | Bulgu | Sonuc |
|---|---|---|---|
| 1 | Pano ↔ arsiv cakisma | B-01 | OK |
| 2 | Brief varligi | B-03 | OK |
| 3 | Dosya kilidi | B-04 | OK |
| 4 | Kirik bagimlilik | B-12 | OK |
| 5 | Yuzde yasagi (D-197) | B-07 | OK (14 harici) |
| 6 | D-197 durum etiketi | B-09 | OK |
| 7 | Brief sablon uyumu | B-17 | OK |
| 8 | Hafiza izi (B-14) | B-14 | OK |

### 4.2 Pano durumu

`gorev_kutusu.py bak --ajan <ad>` (parametre **zorunlu** — kilavuz §11 dogru yazmis):

| Olcu | Deger |
|---|---|
| Toplam gorev | 17 |
| `bekliyor` | 10 |
| `yedek` | 6 |
| `iptal` | 1 |

### 4.3 Git durumu

`git status --porcelain` — **10 modified, takipsiz dosya YOK**. Hepsi calisma zamani durumu (trigger/log/ledger), kaynak kod degil:

```
 M .agents/marketplace
 M "AI proje v1"
 M data/errors/error_log.jsonl
 M data/orchestrator/apify_webhook_dlq.jsonl
 M data/orchestrator/benchmark/CL-02_benchmark_raporu.json
 M data/orchestrator/trigger_log.jsonl
 M data/orchestrator/triggers/mimar.ALARM.json
 M data/orchestrator/triggers/mimar.jsonl
 M tests/_tmp_onem_test/ajan-chat.jsonl
 M workspace/.error_ledger.json
```

### 4.4 Push durumu

- `git log --oneline 8bc6a08..HEAD` → **18 commit**: `2583ce2` `2f78507` `dd6f1f9` `bb794b1` `1e24bec` `36d9414` `5bd47e6` `e0f3c5a` `9f1df85` `7a9ff2c` `902c761` `c3d3458` `b9e3ae6` `44250b9` `c9a46cc` `1635c78` `0c3f18c` `59075f2`
- `git log origin/chore/monorepo-merge..HEAD` → **yalniz `2583ce2`** push edilmemis.

### 4.5 Yirmi bulgunun HEAD dogrulamasi

| # | Bulgu | HEAD kaniti | Durum |
|---|---|---|---|
| B-01 | Mukerrer kapisi arsiv-kor | `task_board.py:132-144` `arsivde_bul()`; `:302-306` ekleme yolunda cagriliyor (D-198) | **Kapali** |
| B-02 | Bayat SSOT durum satirlari | `bb794b1` ile duzeltildi; §14 ile §8.4/§10 uyumlu | **Kapali** |
| B-03 | Panodaki brief yolu diskte yok | Pano taramasi: **brief-yok = 0**; `task_board.py:307` D-66 kod karsiligi eklenmis | **Kapali** |
| B-04 | On gorevde `"dosyalar": []` | 17 gorevin **6**'sinda bos — kalanlar `yedek` durumunda, henuz dosya atanmamis (beklenen) | **Kapali** |
| B-05 | KVKK karari sahipsiz | SSOT `:408` KK-8 satiri mevcut; `:478` "KK-2/KK-3/KK-8 cevaplandi" | **Kapali** |
| B-06 | Yedek gorevler gorunmez | Pano: `TEST-ADMIN-K2-AGIRLIK-23`, `DOC-ADMIN-V9-KUTUCUK-24`, `UI-ADMIN-FEATURE-FLAG-25`, `API-ADMIN-MFA-26`, `UI-ADMIN-LTV-CAC-27`, `DOC-ADMIN-MULTITENANT-KARAR-28` → hepsi `durum: yedek`, `bak` ile listeleniyor | **Kapali** (gercek commit `c9a46cc`) |
| B-07 | Yuzde yasagi ihlali | SSOT'ta tek regex eslesmesi `:28` — o da URL-encode (`%20`), yuzde degeri degil. Simulasyon kontrol 5 OK | **Kapali** |
| B-08 | SSOT surumu uc yerde farkli | `:12` `v2.5` tek dogru deger; `:468-478` surum gecmisi tablosu (tarihsel kayit, celiski degil) | **Kapali** |
| B-09 | D-197 yedi bolumde uygulanmamis | Simulasyon kontrol 6 OK; `bb794b1` | **Kapali** |
| B-10 | §12 G2 bayat | `bb794b1`; hub `ADMIN_DASHBOARD_HUB.md:53-54` `-13`/`-14` gorevlerini §12 G2'ye bagliyor | **Kapali** |
| B-11 | K10 veri kaynagi celiskisi | SSOT `:434` G9 satiri `admin_audit.py` diyor, `:355` K10 tanimiyla uyumlu; tek kaynak secilmis | **Kapali** |
| B-12 | Bagimlilik makine-okunur degil | 17 gorevin **16**'sinda `dependencies` alani var; simulasyon kontrol 4 OK; `dd6f1f9` | **Kapali** |
| B-13 | `bakim` arsivi okumuyor | `cmd_bakim()` `:362-366` `arsiv_cakisma` basiyor | **Kapali** |
| B-14 | Hub'a geri yansima sifir | `ORKESTRASYON_AJANLAR_HUB.md:56-60` + `ADMIN_DASHBOARD_HUB.md:66-71` "Kapanan isler (B-14 · hafiza izi)" bolumu; `teslim` kapisi calisiyor (`1e24bec`) | **Kapali** |
| B-15 | Gecici dosya kurali uygulanmiyor | Politika `AGENTS.md:502`; disk artiklari **bu turda** temizlendi (`2583ce2`), `.gitignore` kapsam genisletildi | **Kapali** (TUR-C) |
| B-16 | cp1254 kurala baglanmamis | `AGENTS.md:95` zorunlu kural satiri | **Kapali** |
| B-17 | Brief "Kit" alani sapmis | Simulasyon kontrol 7 OK; `dd6f1f9` | **Kapali** |
| B-18 | Kapali madde sayaci sismis | `bb794b1` | **Kapali** |
| B-19 | Kok `AGENTS.md:80` bayat | Kok `AGENTS.md:80` karar araligi guncel (`D-48'den itibaren`) | **Kapali** |
| B-20 | §8.3 C8 beyani eksik | `bb794b1`; `plans/muninn_prd_vs_huginn_analiz.md` yerinde | **Kapali** |

**Ozet: 20/20 kapali.** Regresyon tespit edilmedi.

---

## 5. Yeni acik

Bu turda **ilk kez** ortaya cikan, onceki hicbir denetimde gorulmemis bulgular.

### YA-01 — `AI proje v1` gitlink kayitli, `.gitmodules` eslemesi yok (P0) — **KAPANDI (TUR-D1, 2026-09-24)**

**Kanit zinciri:**

```
git ls-files -s "AI proje v1"
  160000 5d3d700959a6dae031196c62d828cd55f75b4c87 0   AI proje v1
        ^^^^^^ gitlink (submodule kaydi)

git config -f .gitmodules --get-regexp path
  submodule.kilo-market.path .agents/marketplace     <- tek kayit, "AI proje v1" YOK

git submodule status
  fatal: no submodule mapping found in .gitmodules for path 'AI proje v1'
```

**Kok neden (git gecmisi):**

| Commit | Tarih | Ne oldu |
|---|---|---|
| `770fed2` | — | Vault pinli submodule olarak eklendi (gitlink `536d4e1`) + AGENTS.md submodule kurali |
| `b62b2cb` | 21.09 11:29 | "GIT-CLEANUP-01: AI proje v1 submodule kaydi temizle" — `.gitmodules` 3 satir **silindi**, gitlink 1 satir **silindi** |
| `5d38f58` | 21.09 12:01 | **`git add -A` otomatik gunluk commit** — dizin icinde `.git` klasoru duruyordu, git onu tekrar **gitlink olarak ekledi**; `.gitmodules` bu kez yazilmadi |

Yani `b62b2cb` temizligi **yarim kaldi**: `.gitmodules` kaydi ve indeks girdisi silindi ama **calisma agacindaki `.git` klasoru birakildi**. 32 dakika sonra `scripts/git_auto_push.bat` icindeki `git add -A` gitlink'i geri getirdi.

**Alt depo gercegi:**

```
git -C "AI proje v1" remote -v
  origin  https://github.com/yassuacohen-hub/AI-proje-v1.git

git -C "AI proje v1" rev-parse HEAD   → 5d3d7009...  (indeksteki hash ile AYNI)
git -C "AI proje v1" branch -r --contains HEAD → origin/main  (uzakta MEVCUT)
git -C "AI proje v1" rev-list --count origin/main..HEAD → 0  (push edilmis)
```

**Sonuc:** Icerik uzakta duruyor, veri kaybi yok. Sorun **yalniz esleme eksikligi**.

**Etki zinciri:**
1. Taze klonda `AI proje v1` **bos dizin** gelir (`dir /b` → 0 oge).
2. SSOT belgesi `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (507 satir) **gelmez**.
3. `simulasyon` kontrol 5 (yuzde yasagi) ve kontrol 6 (D-197 durum etiketi) **sessizce ATLANIR**.
4. `simulasyon` yine de **cikis kodu 0** doner → D-198 tur kapisi "temiz" der.
5. Bu makinede calisiyor cunku alt depo **yerel diskte** duruyor. Baska makinede SSOT denetimi **hic calismaz**.

**Ikinci derece bulgu:** Ana depo `git status` ciktisindaki ` M "AI proje v1"` satiri, alt depodaki **182 degismis dosyadan** geliyor — bunlar ana depo icin gorunmez.

**Uc secenek (KAHIN karari gerekir — bu tur uygulamadi):**

| # | Secenek | Islem | Sonuc |
|---|---|---|---|
| A | Gercek submodule yap | `.gitmodules`'a `AI proje v1` kaydi ekle, gitlink'i pinle | Klon `--recurse-submodules` ile SSOT gelir; iki depo ayri kalir |
| B | Ana depoya goml | Alt `.git` klasorunu kaldir, dosyalari normal olarak commit et | SSOT her klonda gelir; alt depo gecmisi kaybolur |
| C | Disari cikar | Dizini ana depo disina tasi, SSOT yolunu yeniden baglama | Ana depo temizlenir; yol referanslari guncellenmeli |

---

#### Kapanis — KAHIN karari: **Secenek B** (TUR-D1, 2026-09-24, utku)

Uzak alt depo (`https://github.com/yassuacohen-hub/AI-proje-v1.git`) **silinmedi**, referans olarak duruyor.

**ADIM 0 — veri kaybi onleme (alt depo senkron degildi).** Guvenlik kapisi ilk gecişte FAIL verdi:
`git status --porcelain` 752 satir. Kural geregi hicbir sey silinmedi, KAHIN'e rapor edildi.
Karar: once alt depoda commit + push.

```
alt depo eski HEAD : 5d3d700959a6dae031196c62d828cd55f75b4c87
alt depo yeni HEAD : 3a9db07a497ab1276ae47d9325abe0d841bd0a98   (443 dosya)
push               : 5d3d700..3a9db07  HEAD -> main
83 adet `*.backup_*` artigi `git clean -f -q -- "*.backup_*"` ile temizlendi (AGENTS.md:502)
```

**ADIM 1 — guvenlik kapisi (2. gecis, TEMIZ).**

```
git -C "AI proje v1" rev-list --count origin/main..HEAD → 0
git -C "AI proje v1" status --porcelain                 → BOS
robocopy ... c:\_AI_PROJE_V1_YEDEK_2026-09-24 /MIR /XD .git → 862 dosya, FAILED=0
```

**ADIM 2 — gitlink kaldirildi (commit `84d9e6c`).**

```
git rm --cached "AI proje v1"
rmdir /S /Q "...\AI proje v1\.git"
git add "AI proje v1"
git ls-files -s "AI proje v1" | findstr /B "160000" → BOS  (mode 160000 = 0)
git ls-files --error-unmatch "AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md" → OK
```

Indekse **739** dosya girdi; diskteki 862 ile arasindaki **123** dosyalik fark tamami
onceden var olan mesru ignore kurallarindan: `.env` (sir), `__pycache__/*.pyc`,
`.pytest_cache/`, `.vscode/`, `.obsidian/workspace.json`, `.agents/skills/*`,
`cop_kutusu_2026_09_09/*`, `test_reports/*`.

**Tikanma ve cozumu:** ilk `git add` SSOT'u indekse almadi.
`git check-ignore -v` kok nedeni gosterdi: `.gitignore:44:V10/`. Kural kok dizindeki
(var olmayan) `V10/` icin yazilmis ama dizin-adi kurali oldugu icin kasa agacindaki
`AI proje v1/V10/` agacini da vuruyordu. Tek satirlik negasyon eklendi:

```gitignore
V10/
# YA-01: kasa V10 agaci SSOT icerir (02_admin_panel_hedef_dokumani.md), depoda TUTULUR
!AI proje v1/V10/
```

**ADIM 3 — tekrari onleme (commit `10c1a9e`).**
Kok neden `scripts/git_auto_push.bat` icindeki `git add -A` idi. Ayni dosyaya,
`add -A` satirindan hemen sonra kapi eklendi (yeni arac/soyutlama uretilmedi):

```bat
"%GIT%" submodule status >nul 2>>%LOG%
if errorlevel 1 (
    echo [%DATE% %TIME%] ESLEMESIZ GITLINK: commit iptal, elle temizle ^(YA-01^) >> %LOG%
    "%GIT%" reset >> %LOG% 2>&1
    exit /b 2
)
```

Eslemesiz gitlink varsa `git submodule status` `fatal: no submodule mapping found` verir
ve errorlevel 1 doner; o durumda commit **yapilmaz**, indeks geri alinir.
Mevcut `tests/test_naming_audit.py` dosyasina tek test eklendi:
`test_eslemesiz_gitlink_yok` — `git ls-files -s` mode 160000 girdilerini `.gitmodules`
`path` kayitlariyla karsilastirir. Sonuc: **9 passed in 0.32s**.

**ADIM 4 — taze klon provasi (bilincli olarak `--recurse-submodules` OLMADAN).**

```
git clone --branch chore/monorepo-merge --single-branch <ana depo> c:\_KLON_PROVA_2026-09-24
  Updating files: 100% (2931/2931), done.

klonda SSOT var mi                                  → VAR
klonda SSOT satir sayisi                            → 507        (beklenen 507)
klonda git ls-files "AI proje v1" | find /C /V ""   → 739        (ana indeksle ayni)
klonda git ls-files -s | findstr /B "160000"        → yalniz .agents/marketplace (eslemesi VAR)
klonda gorev_kutusu.py simulasyon                   → 8/8 OK, EXIT=0
```

Ana depo ayni komutlar: `simulasyon` 8/8 OK, EXIT=0 · `pytest -q` **4093 passed, 12 skipped**.

**Cikti farki (beklenen, gerekcesi):** klonda `pytest -q` → *6 failed, 4065 passed, 14 skipped, 16 errors*.
Ayni dosyalar ana depoda kosuldugunda **116 passed** (0 hata). Fark tamami ortam kaynakli,
`AI proje v1` icerigiyle **ilgisiz**:

| Kirilan | Gerekce |
|---|---|
| `test_api_companies.py` (3 fail + 16 error), `test_api_integration.py`, `company_master/test_connection.py` | Klonda `.env` YOK (sir, dogru sekilde ignore) ve `data\company_master.db` YOK (ignore). Dogrulandi: `ENV-YOK` / `DB-YOK`. |
| `test_pano_denetim.py::test_pano_yolu_kanonik` | Bilinen **YA-03**: test mutlak dizin adina bagimli. Hata metni: `PANO_DOSYA kanonik yolda degil: C:\_KLON_PROVA_2026-09-24\...`. Bu bulgu zaten acik, kapsam disi. |

Prova dizini silindi (`PROVA-SILINDI`).

**Sonuc:** Taze klon artik SSOT'u 507 satirla getiriyor; `simulasyon` kontrol 5 ve 6 baska
makinede de calisir. YA-01'in etki zinciri (madde 1-5) tamamen kirildi.
Kapanis commit'leri: `84d9e6c` (gomme) · `10c1a9e` (koruma + test).

### YA-02 — `simulasyon` eksik denetimi cikis kodu 0 ile ortuyor (P1)

Kontrol 5 ve 6, hedef dosya bulunamayinca **"ATLANDI" yazip gecer** ama cikis kodunu etkilemez.
D-198 "0 = temiz, tur baslayabilir" diyor. Dolayisiyla SSOT dosyasi olmayan bir ortamda tur, **iki kontrol hic calismadan** baslar.
Beklenen davranis: atlanmis kontrol **en az uyari (1)** uretmeli.

### YA-03 — Testler dizin adina bagimli (P2)

`tests/test_pano_denetim.py::test_pano_yolu_kanonik` yalnizca depo `Huginn Data Insights` adli bir dizinde duruyorsa geciyor.
Farkli ada klonlanan her kopyada kiriliyor. Kanonik yol kontrolu **mutlak dizin adi** yerine depo koku goreli olmali.

### YA-04 — TUR-B raporunda hash atfi hatasi (P2)

B-06 kapanisi `44250b9`'a atfedilmis; pickaxe gercek commit'in **`c9a46cc`** oldugunu gosterdi.
Rapor hash'leri dogrulanmadan yazilmis — bu, denetim izinin guvenilirligini dusuruyor.

---

## 6. Kapanan / Acik kalan

**Kapanan:** 20 denetim bulgusunun tamami (B-01…B-20) HEAD'de kapali dogrulandi; B-15 disk hijyeni yonuyle bu turda kapatildi (`2583ce2`, 32 dosya). Ana depo `simulasyon` 8/8 OK, cikis kodu 0. Regresyon yok — TUR-B raporunun "acik" dedigi bes bulgudan dordu zaten kapaliydi, rapor yanlisti.

**Acik kalan:** **YA-01 KAPANDI** (TUR-D1, 2026-09-24 — KAHIN Secenek B; `84d9e6c` + `10c1a9e`; taze klon SSOT'u 507 satirla getiriyor). Uc acik kaldi — **YA-02** `simulasyon` atlanmis kontrolu cikis kodu 0 ile ortuyor (P1) · **YA-03** `test_pano_yolu_kanonik` dizin adina bagimli (P2; TUR-D1 klon provasinda tekrar gorundu) · **YA-04** TUR-B raporunda B-06 hash atfi hatali (P2).

---

## Ilgili Nodlar

- [[Huginn Data Insights/data/orchestrator/DENETIM_SUREC_2026-09-24]]
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/docs/GOREV_PANOSU_KULLANIM_KILAVUZU]]
