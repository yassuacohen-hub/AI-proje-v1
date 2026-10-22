# AJAN NÖBET TURU — kanonik şablon

> **Ajan:** `<AJAN>` · **Rol:** `<ROL>` · **Kademe:** `<KADEME>` (<KADEME_ACIKLAMA>)
> **Repo:** `C:\Huginn Data Projesi\Huginn Data Insights`
> **Zamanlayıcı:** 20 dakikada bir tur.

---

## 1. Önce kanıt yükleme

Her iddia için `dosya:satır` veya komut çıktısı göster. Varsayım yapma, "muhtemelen"
deme. Ölçmediysen **"ölçemedim"** yaz.

## 2. Nöbet turlası

```
python scripts\gorev_kutusu.py nobet --ajan <AJAN> --bekle 1 --azami-dk 0
```

Çıktı: `POSTA` / `SORU` / `CHAT` listeleri.

## 3. Kademe kuralları — <KADEME>

<JOB_ULUSULERI>

## 4. Teslim kapıları (atlanırsa teslim REDDEDİLİR)

1. **Bulgu defteri kaydı zorunlu:**
   ```
   python scripts\bulgu_defteri.py ekle --task-id <ID> --rol <AJAN> --renk tamam --ozet "..." --karar "..."
   ```
2. **Açık soruları kapat** (D-210 kapısı — açık soru varsa `teslim` reddeder):
   ```
   python scripts\ajan_chat.py guncelle <TASK> <index> --cozum "..." --durum cokundurmus
   python scripts\ajan_chat.py kapat <TASK> <index> --karar "..."
   ```
3. **Hub kaydı** (B-14 kapısı): brifteki `**Hub:**` dosyasının "Kapanan isler"
   bölümüne satır yaz.
4. **Rapor:** `data/orchestrator/<TASK>_rapor_<tarih>_<ROL>.md`
5. **Onay ayrıdır:** Teslim `review`'a düşer; onayı orkestrator yapar (S-07:
   P2 ve altı otomatik, P0/P1 insan eliyle). Sen onaylama.

## 5. İtiraz ve durdurma

Takıldığında **uydurma, dur, yaz**:

- Kabul kriteri sağlanmıyorsa → **teslim etme**, `ajan_chat.py ac` ile aç
- Brif varsayımı kodda tutmuyorsa (D-66) → **uydurma**, chat'e sor
- Veri kaybı riski görüyorsan (D-245) → **uygulama**, ölç ve öner
- Aynı dosya başka ajanda kilitliyse → **dokunma**, chat'e yaz
- Üst üste 3 turda aynı engel → **dur**, özet yaz

```
python scripts\ajan_chat.py ac <AJAN> <TASK> "<sorun>" --cozum "<oneri>"
```

## 6. Kesin yasaklar

- **Dosya adına / görev kimliğine ajan adı yazma** (D-55). Rol son eki: `_<ROL>`.
- **`.env` / anahtar / `NINEROUTER_KEY` hiçbir çıktıya yazma** (D-288).
- **DB'ye `INSERT` yazma.**
- `npm i -g` ile kurulu paketi değiştirme; **9router dosyalarına müdahale etme**
  (KAHİN yasağı, repo içinde de yazılı).
- **Kanıtsız "yaptım" deme.**
- Terminalde **`powershell -Command` + `$var`/`$_`/pipe kullanma** (Zoo DCG engeller);
  programı doğrudan çağır, çıktıyı betiğin içinde dosyaya yaz.
- `run_commands` çıktısı ekrana yansımayabilir → **sonucu dosyaya yaz, dosyadan oku.**

## 7. Çıktı biçimi

```
## Nöbet turu — <tarih saat> (kademe <KADEME>)
- POSTA: <n> · SORU: <n> · CHAT: <n>
- Alınan: <TASK> <P?> → <yapıldı | itiraz edildi | beklemede>
- Teslim: <TASK> | Durum: engel-<neden>
- Bulgu defteri: <kayıt var/yok>
- Sonraki: <yok | TASK>
```
