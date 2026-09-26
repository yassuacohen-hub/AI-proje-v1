# <TASK_ID> — Brief (<ajan>)

**Başlık:** [<KIT>] <tek cümlelik iş tanımı> (<tahmini süre>)
**Öncelik:** P0|P1|P2 · **Kit:** `<KIT>` (AGENTS.md D-196)
**Kilitli dosya:** `<yol/dosya.uzanti>`
**Bağımlılık:** `<TASK_ID>` (yoksa satırı sil)
**Hub:** `hubs/<HUB_ADI>.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

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
> Tek fazlı işte düz numaralı liste. **Toplu işte** bunun yerine `## Faz A — <ad>`,
> `## Faz B — <ad>` başlıkları kullan; her fazda kök neden + etkilenen dosya + o fazın
> doğrulama komutu yazılı olsun. Fazlar sırayla yapılır, en riskli faz ilk sırada.

1. ...
2. ...

## Kabul kriteri
- [ ] Doğrulanabilir, ölçülebilir çıktı (varsa `dosya:satır` / test adı).
- [ ] Toplu işte her faz için ayrı satır + sonda bütünün tek doğrulaması.
- [ ] ...

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**, brifi yeniden okuyup beklemek değil:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac <ajan> <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id <TASK_ID>
python scripts/chat_gonder.py --to <ajan> --type hata --task-id <TASK_ID> --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK_ID> --ozet "<özet>"
```

## Ilgili Nodlar
> **Zorunlu (D-218).** Obsidyen proje hafızasıdır. Linksiz doküman grafikten kopuk kalır ve
> ajan onu bulmak için tüm repoyu tarar — token ve süre maliyeti. **En az 2 wikilink.**
> Göreve dokunan her yeni/değişen dokümanı da buraya bağla, ayrıca o dokümanın kendi
> `## Ilgili Nodlar` bölümünden bu brife geri link ver (çift yön).

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
