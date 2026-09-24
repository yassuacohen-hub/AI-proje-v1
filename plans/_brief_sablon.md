# <TASK_ID> — Brief (<ajan>)

**Başlık:** [<KIT>] <tek cümlelik iş tanımı> (<tahmini süre>)
**Öncelik:** P0|P1|P2 · **Kit:** `<KIT>` (AGENTS.md D-196)
**Kilitli dosya:** `<yol/dosya.uzanti>`
**Bağımlılık:** `<TASK_ID>` (yoksa satırı sil)
**Hub:** `hubs/<HUB_ADI>.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden
SSOT'taki hangi bulgu/satır bu görevi doğuruyor — `dosya:satır` referansıyla. Kanıtsız gerekçe yasak.

## Doğrulanacak varsayım
> Zorunlu bölüm (D-66 brif sözleşmesi). Brief yazarken **sabitlenen** her tablo adı, kolon adı, fonksiyon imzası,
> satır numarası ve eşik değeri buraya bir madde olarak geçer. Jenerik metin yasak — her brief
> kendi gerçek varsayımlarını taşır.

- `<sema.tablo.kolon>` kolonu var varsayıldı. Yoksa **dur**, panoya sorun aç, uydurma.
- `<modul.py:NN>` satırındaki `<fonksiyon()>` imzası varsayıldı. Farklıysa **dur**, panoya sorun aç.
- `<ESIK_ADI=deger>` eşiği varsayıldı. Kodda başka değer varsa **dur**, KAHİN'e sor.

## Adımlar
1. ...
2. ...

## Kabul kriteri
- [ ] Doğrulanabilir, ölçülebilir çıktı (varsa `dosya:satır` / test adı).
- [ ] ...

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK_ID> --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
