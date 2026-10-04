# Komut Kurallari (DCG uyumlu calisma)

**Neden bu dosya:** Destructive Command Guard (DCG) bir komutu engelledi.

Sebep yazma isleminin kendisi degil, yolun dinamik olmasiydi.

## 1. ASLA yapma

- Degiskenle yol kurmak (R degiskeni, PWD) -> dinamik, dogrulanamaz
- Ayni komutta yazma + calistirma + silme zinciri
- Uzun icerigi PowerShell kacisiyla tasimak (tek ve cok kez basarisiz oldu)


## 2. Bunun yerine

**Tercih sirasi:**

1. Python pathlib ile goreli yol + sabit isim (DCG dostu)
2. Repo icindeki kalici arac scriptleri (zaten var)
3. Gerekirse once olustur, AYRI komutta calistir

**Kural:** yol sabit ve goreli olsun; bir komutta birden fazla yazma/silme yapma.

## 3. Bu dosya nasil olusturuldu

Bu kuralin kendisi de yeni desenle yazildi: kisa python -c + pathlib + goreli yol,
bolum bolum eklendi. Uzun tek-komut yazimi PowerShell kacisinda basarisiz oldu.

## 4. En sik DCG engeli: redirect zinciri

Sik gelen hata deseni:

    komut > data/tmp.txt 2>&1 + type data/tmp.txt

Uc neden engellenir:

1. > redirect: dosyayi truncate edebilir
2. 2>&1: PowerShellde bu dosyaya yaz demek (grep/head ciktisi DEGIL)
3. Zincir: arka plan isi + tip komutu

AYNI ISI ZATEN EKRANA YAZIYOR. Dogrusu:

    komut

Ciktiyi dosyaya almak gerekiyorsa AYRI komut:

    komut | Out-File data\rapor.txt

Gecici dosyayi silmek de ayri komutta yapilir.

## 5. "Embedded shell launcher cannot be statically verified" (ihsan · 2026-10-03)

Tam hata: *Embedded PowerShell launcher command contains runtime expansion
that dcg cannot statically verify.* DCG komutu **calistirmadan** okur;
calisma aninda genisleyen her sey (degisken, alt-komut, zincir) = engel.

| Yasak desen | Neden | Yerine |
|---|---|---|
| `powershell -Command "... $env:X ..."` | `$env:` calisma aninda genisler | `python -c "import os; print(os.environ['X'])"` |
| `cmd1 && cmd2` / `cmd1 ; cmd2` | zincir = birden fazla etki, tek dogrulama yok | Her komut **ayri** tool cagrisi |
| `$(...)`, `` `...` ``, `%VAR%` | alt-komut / degisken genislemesi | Sabit, goreli yol yaz |
| `powershell -Command "Get-Content ... -Raw; ''; ..."` | PowerShell ici `;` zinciri | `type dosya` veya `python -c "print(open('dosya',encoding='utf-8').read())"` |
| `komut > f 2>&1` + `type f` | redirect + zincir (bkz. §4) | Sadece `komut` |
| `python -c "<200+ karakter>"` | kacis karmasasi; DCG parse edemez | Kalici script: `scripts/<ad>.py`, sonra `python scripts/<ad>.py` |

**Tek kural:** `python scripts/x.py --arg deger` biciminde, zincirsiz,
degiskensiz, 1 komut = 1 cagri. Repo'daki araclar (`gorev_kutusu.py`,
`chat_gonder.py`, `bulgu_defteri.py`, `ajan_chat.py`) bu bicimde cagrilir.

## 6. Zoo Code onay listesi (2026-10-03 · settings.json)

`zoo-code.allowedCommands` 193 tam-komut kaydindan **16 prefix**'e indirildi;
`zoo-code.deniedCommands` **11 yasak** aldi (`--no-verify`, `git reset --hard`,
`git push --force`, `git clean`, `rmdir /s`, `del /s`, `Remove-Item -Recurse` ...).

Izinli prefixler: `python`, `python -m pytest`, `pytest`, `git status/diff/log/show/add/commit`,
`dir`, `findstr`, `type`, `powershell -NoProfile`, `docker compose`, `schtasks`, `set`.

Bu prefixlerle baslayan ve §5'teki desenleri icermeyen komut **onay istemez**.
Arac: `python scripts/zoo_ayar_duzelt.py` (yedek alir, yeniden yazar, dogrular).

## 7. Makine donmasi — olculdu, iki kok neden (ihsan · 2026-10-03 20:52)

| Olcum | Once | Sonra | Duzeltme |
|---|---|---|---|
| Acik `powershell.exe` | **92** (1.38 GB) | 3 | `python scripts/zombi_kabuk_temizle.py` (81 zombi kapatildi) |
| `gorev_kutusu.py bak` suresi | **14.4 s** (14.6 s Notion: 10 HTTP + 4 s sleep) | 0.12 s | `SALT_OKUR_KOMUTLAR`: bak/nobet/ozet... Notion senkron yapmaz |
| `chat_al.py oku` | 0.09 s | 0.09 s | — |

Kok neden 1: Zoo Code her komut icin yeni VS Code terminali aciyor (`-noexit` PowerShell),
hic kapanmiyor; 4 ajan x saatlerce = 90 kabuk. `.vscode/settings.json`:
`defaultProfile=Command Prompt`, `shellIntegration=false`, `persistentSessions=false`.
Kok neden 2: her pano komutu (okuma bile) Notion'a 10 istek atiyordu; 4 ajanin nobet
dongusu = surekli Notion trafigi + CPU.

**Ajan kurallari (donma onleme):**
1. Uzun komut (pytest tum paket, scraper, docker) -> **tek seferde tek ajan**; once
   `python scripts/zombi_kabuk_temizle.py --kuru` ile sayiya bak; 20+ ise temizle.
2. `pytest` daima dosya/klasor hedefli: `python -m pytest tests/test_x.py -q`. Tum paket
   yalnizca teslim oncesi, bir kez.
3. Nobet bekleme `--bekle 120` altina inmez; `--bekle 10` gibi sik yoklama yasak.
4. Terminal sekmesi isi bitince kapanir (`exit`); acik sekme = acik kabuk = bellek.
5. Ayni anda 1 ajan 1 terminal. Paralel pytest/scraper = donma.

**Otomasyon (kapandi · 2026-10-03 21:05, saat guncellendi 2026-10-03 21:10):** Windows Gorev Zamanlayici'na
`HuginnZombiTemizle` eklendi, her gun 15:00'da `zombi_kabuk_temizle.py`
(temizleme modu, `--kuru` degil) calisir. Sahip talebiyle 08:00 -> 15:00 (ogle sonrasi,
gunduz basladigi saate denk) olarak degistirildi: `schtasks /change /TN HuginnZombiTemizle /ST 15:00`.
Dogrulama: `schtasks /query /TN HuginnZombiTemizle /V`.
Bilinen sinir: `Logon Mode: Interactive only` -> bilgisayar kapali/kilitliyse veya
oturum acik degilse o gun calismaz; sahip sabah bilgisayari actiginda manuel
`python scripts/zombi_kabuk_temizle.py --kuru` ile teyit edebilir.
