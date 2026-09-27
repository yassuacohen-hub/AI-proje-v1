# Brif — VERI-NACE-KOLON-01: nace_validity kolon karışmasını düzelt → 86 satır

**Başlık:** [VERI] `nace_validity` kolon karışmasını düzelt (86 satır) (1s)
**Öncelik:** P2 · **Kit:** `VERI` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Süre:** 1s · **Veren:** ihsan
**Önkoşul:** yok — bağımsız, tek başına yapılabilir
**Kanıt tabanı:** `plans/brief_utku_VERI-NACE-SOZLUK-01.md` bölüm 1

---

## Neden

Ölçülen hata (canlı Supabase):

`companies.nace_validity` kolonuna **NACE kodu yazılmış**. 86 satır:

```
'41.00.02'   '35.12.00'   ...
```

Bu kolon geçerlilik **etiketi** taşımalı (`unknown`, `medium`, `fallback` gibi),
kod taşımamalı. Kolon karışması — kazıma/yazma sırasında iki alan takas edilmiş.

Doğru değerlerin dağılımı (kalan satırlarda kolon düzgün kullanılmış), yani
kolonun amacı belli; sadece bu 86 satır bozuk.

## Adımlar
1. `nace_validity` içinde NACE kodu deseni (`\d{2}\.\d{2}`) taşıyan satırları bul.
2. Her biri için: `nace_code` boş mu dolu mu **kontrol et**.
   - `nace_code` boşsa → kodu oraya taşı, `nace_validity`'ye uygun etiket yaz
   - `nace_code` doluysa → iki kod çelişiyor mu bak. Çelişiyorsa **karar verme**,
     dök ve rapora yaz. Hangisinin doğru olduğunu uydurmayın.
3. `nace_validity`'yi geçerli etiket kümesine çek. Mevcut kullanılan etiketleri
   önce sorgulayıp öğrenin — yeni etiket icat etmeyin.

## Kabul kriteri
- `nace_validity` içinde NACE kodu deseni taşıyan satır **0**
- `nace_validity` değerlerinin tamamı bilinen etiket kümesinde
- Taşınan / çelişen satır sayıları raporda yazılı

## 4. Neden P2

86 satır — küçük. Ama küçük olduğu için ertelenmemeli: kolon karışması varsa
aynı hatayı üreten kod hâlâ çalışıyor olabilir. Düzeltirken **kaynağını da
bulun**: hangi yazıcı bu iki alanı takas ediyor? Sadece veriyi düzeltip kodu
bırakırsanız 86 satır yarın 200 olur.

---

*ponytail: desen ile bulup taşıma. Skipped: yazıcı kodunda kalıcı kolon
doğrulama (DB CHECK kısıtı), eklenmesi gereken an — aynı karışma ikinci kez
görülürse.*

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- `companies.nace_validity` kolonunda 86 satırda yanlış/karışmış değer varsayıldı. Sayı farklıysa yeniden ölç, brifi güncelle.
- Bu iş **bağımsız** varsayıldı — hiçbir önkoşulu yok, tek başına yapılabilir.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-NACE-KOLON-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-NACE-KOLON-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-NACE-KOLON-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-NACE-KOLON-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
