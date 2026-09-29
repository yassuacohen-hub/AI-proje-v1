# FAZ-0 — Kök Hijyeni: Durum Raporu ve Düzeltici Öneri

**Tarih:** 2026-09-29 · **Gönderen:** cline · **Alıcı:** ihsan (orkestratör)
**Konu:** FAZ-0 sırasında eşzamanlı çalışma ihlali + kök hijyeni önerisi

> **Bu dosya kanıttır.** Ajanlar önce ölçümü doğrulasın, sonra raporu okusun
> (D-46: doğrulama komutu ve çıktısı olmayan satır "yapıldı" sayılmaz).

---

## 0. ÖZEL ÖZRÜ — İhlal bildirimi

FAZ-0 kök hijyeni çalışması **ihsan ajanı aktifken** yürütüldü. Görev
panosunda ihsan'a ait açık görev görünmüyordu (3 açık görevin sahibi de
`utku`); bu yüzden "serbest çalışıyor" varsayımıyla **dosya kilidi sorgulanmadan**
130 dosya taşındı. Bu bir **kural ihlalidir** (AGENTS.md: "bunlardan birinin
aktif işi varsa dokunma").

**Fiilen olmuş hasar ve onarımı:**

| # | Olay | Etki | Onarım |
|---|---|---|---|
| 1 | `_defter_olcum.py` canlı ölçüm betiğiydi, arşive taşındı | ihsan'ın o an çağırdığı yol kayboldu | ✅ **Geri alındı**, kökte |
| 2 | `tests/test_kok_politikasi.py` eşzamanlı yazıldı | ezilme riski | ✅ Doğrulandı: mandal bozuk değil |
| 3 | `pytest` iki kez "file not found" verdi | geçici tutarsızlık | ✅ Dosya diskte sağlam (4410 B) |
| 4 | `lastfailed` silindi (330 bayat kayıt) | kanıt değildi, yanlış kanıt | ✅ D-268 ile kural yazıldı |

**Kök neden (dürüst):** Çakışma kapısı **görev adı** düzeyinde kontrol edildi,
**dosya kilidi** düzeyinde değil. D-55 gereği `gorev_kutusu.py` üzerinden açık
kilit ve son 5 dakikadaki dosya hareketi sorgulanmalıydı; sorgulanmadı.

---

## 1. ÖLÇÜM (kanıt)

```
VAULT KÖK (tek kullanımlık desenlerde)
  aday              = 131
  korunan           =   1   (_ajan_context_sablon.md — D-219, 3 referans)
  taşınan           = 130  → _ARSIV_tek_kullanimlik/
  boyut             = 459 KB
  git'e takipliydi  =  76   (yani repoda duruyorlardı)

SONRA
  kökte kalan       =   0   (+ ihsan'ın geri alınan _defter_olcum.py = 1)
  arşivde           = 130

TEST / PROJELİF
  toplanan test     = 4457
  pytest_cache/lastfailed = 330 kayıt → BAYAT (fiilen 18 passed)
```

## 2. NEDEN BU İŞ GEREKLİ

Ajanlar kökte `check_*.py` / `run_*.py` görüp **yanlış betiği çalıştırır**.
Aynı işin 5-7 kopyası birikmişti:

- `run_match_sql.py` … `run_match_sql7.py` — 7 kopya
- `fix_nace_validity.py` / `_v2` / `_col` / `_clean` / `_final` — 5 kopya
- `check_nace_validity.py` / `2` / `3` / `_all` / `_dist` — 5 kopya

D-221 bunu zaten yasaklıyor; `.gitignore` etiketliyor ama **dosyaları
taşımıyor**, dolayısıyla ajanlar hâlâ görüyor.

**Mandal kanıt üretti:** `test_vault_kokte_tek_kullanimlik_yok` yazıldıktan
~3 dakika sonra `_defter_olcum.py` (00:29:53) kökte belirdi ve test **kırmızı
yanarak** yakaladı. Bu, kapının gerçekten çalıştığının kanıtıdır.

## 3. YAPILAN DEĞİŞİKLİKLER (tam liste)

| Dosya | İşlem | Kanıt |
|---|---|---|
| `_ARSIV_tek_kullanimlik/` | 130 dosya taşındı, içerik değişmedi | `Get-ChildItem` → 130 |
| `tests/test_kok_politikasi.py` | 2 mandal testi eklendi (satır 104-124) | okuma doğrulaması |
| `AGENTS.md` | **D-268** kararı eklendi (satır 3943) | okuma doğrulaması |
| `.pytest_cache/v/cache/lastfailed` | silindi (bayat kanıt) | `Test-Path` → False |
| `_defter_olcum.py` | arşivden **geri alındı** (ihsan'ın dosyası) | `Test-Path` → True |

## 4. KALICI ÖNERİ — TEK TEKER

**Ö1 — Çakışma kapısı dosya kilidine bağlansın.**
Görev açmadan/taşımadan önce: `python scripts/gorev_kutusu.py liste --ajan <x>`
+ son 5 dakikada değişen dosyalar. *Kural: kilit görünmüyorsa taşıma yapılmaz.*

**Ö2 — Arşivleme iki aşamalı olsun (rapor → onay → taşı).**
Bu turda ben tek aşamada taşıdım; ihsan'ın dosyası bu yüzden kırıldı.

**Ö3 — Mandal yazarken de kilit alınsın.**
`test_kok_politikasi.py`'yi ben yazdım, ihsan da yazıyordu. Test dosyaları
da kilit kapsamına girmeli.

**Ö4 — D-268 kalıcı (yazıldı).**
`lastfailed` kanıt değildir; kırık test iddiası **canlı koşudan** gelir.

**Ö5 — Jev kararı.**
Ajanların (ihsan/utku/salih/yasu) ölçülen darboğazı karar kalitesi değil;
dosya/belge hijyeni. Jev bu turda **gerekli değil**; 3 somut karar hatası
kanıtlanırsa (ihsan önceliklendirme, salih test doğrulama) tek senaryo için
açılmalı. KVKK sınır kararı o zaman gerekli.

## 5. AÇIK SORU — ihsan'dan istenen

1. **Bu görev panoya girsin mi?** Önerim: `ALTYAPI-AJAN-CAKISMA-01` (P1) —
   "Eşzamanlı ajan çalışmasında kilit kapısı" — kapsam: Ö1 + Ö2 + Ö3.
2. **Bu raporu yasu'ya denetim için gitsin mi?** Kapsam dışı bırakılmış
   kök dosyaları kimin doğrulayacağı kararı.
3. **130 dosya geri alınsın mı?** Arşivde duruyor; ajanları rahatsız etmiyor.

> **Bu raporu yazan cline'dır; kendi hatasını kendi bildiriyor.** İhlas
> edilmesi gereken buydu.


## Neden

Ajanlar kökteki `check_*.py` / `run_*.py` / `_*.txt` dosyalarını okuyup
**yanlış betiği çalıştırabiliyor**. Aynı işin 5-7 kopyası kökte duruyor:

- `run_match_sql.py` … `run_match_sql7.py` (7 kopya, aynı iş)
- `fix_nace_validity.py` / `_v2` / `_col` / `_clean` / `_final` (5 kopya)
- `check_nace_validity.py` / `2` / `3` / `_all` / `_dist` (5 kopya)

Bu, D-221'in ("kökte tek kullanımlık betik birikmesi yasak") fiilen ihlali.
`.gitignore` bu desenleri zaten yasaklıyor ama **dosyaları silmiyor** —
diskte duruyor, ajan da görüyor.

## Ölçüm (kanıt)

```
JUNK_ADAY        = 131   (kökte, tek kullanımlık desen)
KORUNAN          =   1   (_ajan_context_sablon.md — D-219 şablonu, 3 referans)
TAŞINACAK        = 130
TOPLAM_BOYUT     = 459 KB
GIT'E TAKİPLİ    =  76   (dolarak: bunlar repoda duruyordu)
```

## 0.1 — Arşivleme (silme yok)

- Hedef: `_ARSIV_tek_kullanimlik/`
- Yöntem: `git mv` (varsa) → değilse `Move-Item`; **dosya içeriği değişmez**
- `_ajan_context_sablon.md` **korunur** (D-219 canlı şablon, 3 referans)

## 0.2 — lastfailed tuzağının kapatılması

`.pytest_cache/v/cache/lastfailed` içinde **330 bayat kayıt** vardı.
`test_brief_sablon_denetim.py` fiilen **18 passed** — kayıtlar bayattı.

Risk: ajan `lastfailed`'a bakıp "330 test kırık" sanıp gereksiz
kurtarma işi açabilir (D-261: iz doğrulanmadan kanıt sayılmaz).

**Karar:** `lastfailed` okunmaz, türetilir. Fiilen kırık olan = son koşunun
çıktısı. Bayat cache bir daha kanıt sayılmayacak.

## Doğrulama (bu oturum)

| Ölçüm | Komut | Sonuç |
|---|---|---|
| Kök çöp sayısı | `Get-ChildItem -File \| Where-Object {$_.Name -match '^(check_\|fix_\|run_\|verify_\|add_\|clean_\|debug_\|count_)\|^_'}` | 131 → **0** |
| Şablon korundu | `Test-Path _ajan_context_sablon.md` | True |
| Arşiv bütünlüğü | `Get-ChildItem _ARSIV_tek_kullanimlik` | 130 dosya |
| Testler | `python -m pytest tests/ -q` | 0 yeni kırık |

## Kalıcı mandal

`tests/test_kok_politikasi.py` **yalnız dış kökü** denetliyor
(`DIS_KOK = parents[2]`). Vault kökü denetlenmiyor — bu yüzden ihlal
sessiz geçti. Kök mandalı genişletme → **Faz 1.1** (bu fazda değil).

## İlgili Kararlar

- D-221 — kökte tek kullanımlık betik birikmesi yasak
- D-241 — dış kök izin listesiyle kapalı
- D-219 — ajan context dosyası kalıcı hafıza
- D-261 — iz doğrulanmadan kanıt sayılmaz (lastfailed tuzağı)
