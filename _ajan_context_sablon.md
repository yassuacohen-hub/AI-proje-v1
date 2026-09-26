# `<ajan>_project_context.md` — Oturum Hafızası Şablonu (D-219)

> **Ne işe yarar:** Oturum kapanınca bağlam sıfırlanır. Bu dosya olmadan sonraki oturum aynı
> keşfi baştan yapar — kalıcı token + süre maliyeti. Bu dosya ajanın **kalıcı hafızası**dır.
>
> **Kullanım:** `<ajan>_project_context.md` adıyla kopyala (örn. `utku_project_context.md`).
> Oturum **başında oku**, oturum **sonunda yaz**. Kanonik örnek: [[Huginn Data Insights/ihsan_project_context]].
>
> **Boyut tavanı 200 satır.** Aşınca en eski oturum bloklarını
> `archive/<ajan>_context_<YYYYMM>.md`'ye taşı. Şişmiş context her oturumda okunur; maliyeti kalıcıdır.
> **Bölüm sırası sabittir** — ajan aynı yerde aynı bilgiyi bulur, arama yapmaz.

## KALDIĞIM YER

> **Dosyanın en üstünde, tek blok, her oturum sonunda ÜZERİNE YAZILIR** (biriktirilmez —
> biriken liste okunmaz). Ajan oturuma bu 4 satırla başlar; devamı gerekirse aşağı iner.
> Bu bölüm boşsa aktif iş yok demektir; **uydurma**, panodan görev al.
>
> Slash komutuyla üretilmez: komut bunu ancak tahmin eder, tahmin hayalet görev doğurur (D-216).
> Yazılı olan tek güvenilir hafızadır.

- **Konum:** <hangi dosyanın hangi fonksiyonunda kaldın — `dosya:satır`>
- **Yapılanlar:** <bu görevde tamamlanan somut şey>
- **Kritik bağlam:** <SADECE şu dosyaları baz al: `a.py`, `b.py`> ← en pahalı satır, dar tut
- **Sonraki adım:** <tek cümle, doğrudan eyleme geçilebilir>
- **Görev:** `<TASK_ID>` · **Son okunan karar:** `D-<NN>`

## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki 4 satır. Genelde tek ihtiyacın bu.
2. **§Tuzaklar** + **§Sabitler** — en pahalı bilgi; okumazsan aynı hatayı tekrar ödersin.
3. `python scripts/gorev_kutusu.py liste --ajan <ajan>` → aktif görev pano ile tutuyor mu?
4. `python scripts/ajan_chat.py oku --ajan <ajan>` → cevap bekleyen @mention var mı (D-210)?
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ yukarıdaki **Son okunan karar** ise aradakileri oku (D-168).
6. Brif varsa oku; **§Doğrulanacak varsayım** maddelerini koda karşı doğrula.

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür** — context bayat olabilir, pano canlıdır.

## Kimlik

- **Ajan:** `<ajan>` (araç: `<kilo|cline|roo|continue>`)
- **Rol:** <tek cümle — AGENTS.md §Ajanlar ve Roller ile birebir>
- **Kit:** `<KIT>` (D-196)
- **Mülkü:** <dizin/dosya kalıpları — burada yazarım>
- **Mülkü değil:** <başka ajanın alanı — dokunmam, chat ile isterim>
- **Rapor hattı:** <kime teslim eder / kim onaylar>

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **son bilinen: `<N passed / M failed>`** (`<tarih>`)
- **Uygulama:** `<çalıştırma komutu>`

## Sabitler (doğrulanmış gerçekler)

> Oturumlar arası **değişmeyen** gerçekler. Her satır `dosya:satır` kanıtı taşır.
> Varsayım buraya yazılmaz — yalnız gözle doğrulanmış gerçek. Yanlış sabit, yanlış kod üretir.

- `<sema.tablo.kolon>` mevcut — `<dosya:satır>`
- `<fonksiyon()>` imzası `<...>` — `<dosya:satır>`

## Tuzaklar (aynı hatayı iki kez yapma)

> **Bu dosyanın en değerli bölümü.** Her oturumda düşülen tuzak buraya bir satır yazılır:
> *belirti → kök neden → çözüm*. Tuzak yazılmazsa gelecek oturum aynı bedeli tekrar öder.

- <belirti> → <kök neden> → <çözüm> (`<dosya:satır>`)

## Bilinen Açıklar (kapsam dışı backlog)

- <kısa tanım> — görev: `<TASK_ID>` (hayalet mi diye D-216 usulü çapraz kontrol et)

## Sık Komutlar

```bash
python scripts/gorev_kutusu.py liste --ajan <ajan>
python scripts/gorev_kutusu.py al --ajan <ajan> --task-id <TASK_ID>
python scripts/ajan_chat.py ac <ajan> <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK_ID> --ozet "<özet>"
```

## Oturum Günlüğü

> Oturum sonunda **bir blok**, en yeni üstte. Boş laf yasak: ne yapıldı, hangi commit,
> hangi doğrulama. Doğrulama komutu ve çıktısı olmayan satır "yapıldı" sayılmaz (D-46 ruhu).

### `<YYYY-MM-DD>` — <oturum konusu>

- **Görev:** `<TASK_ID>`
- **Yapılan:** <madde madde, `dosya:satır` referanslı>
- **Doğrulama:** `<komut>` → `<sonuç>`
- **Commit:** `<sha>`
- **Kalan / bloke:** <yoksa "yok">
- **Öğrenilen tuzak:** <varsa yukarı §Tuzaklar'a da ekle>

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle (üzerine yaz) + **Son okunan karar** no'yu tazele.
> Bu iki adım atlanırsa sonraki oturum sıfırdan keşif yapar; dosyanın tüm faydası kaybolur.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/ihsan_project_context]]
- [[plans/_brief_sablon]]
