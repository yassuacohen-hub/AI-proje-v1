# ORKESTRA-KIMLIK-ZINCIRI-01 — Brief (ihsan)

**Başlık:** [ORKESTRA] Kimlik zinciri kaydını düzelt → plans/brief_ihsan_ORKESTRA-KIMLIK-ZINCIRI-01.md (1s)
**Öncelik:** P1 · **Kilitli dosya:** `scripts/ajan_chat.py`, `scripts/gorev_kutusu.py`
**Hub:** `hubs/ORKESTRASYON_AJANLAR_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.
**Önceki kimlik:** `ORCH-KIMLIK-ZINCIRI-01` (yasu'nun chat bulgusu, `ajan-chat.jsonl` kaydı #1) — **panoda hiçbir yerde yok**. D-222 Kural 4 gereği devralınan görev kanonik kimlik alır; `ORCH` D-57 kanonik ALAN listesinde yok. Redirect izi: `scripts/id_migration.py` (D-191).

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

## Neden

SSOT'taki iki ölçülmüş bulgu bu görevi doğuruyor:

1. **Bulgu kaydı kanonik görev değildir.** `ORCH-KIMLIK-ZINCIRI-01` yalnız
   `data/orchestrator/ajan-chat.jsonl` içinde bir chat kaydı olarak duruyor. Ölçüm
   (2026-10-04): `task_board.json` 144 kayıt, `task_board_arsiv_2026-Q3.json` ve
   `task_board_arsiv_2026-Q4.json` → **üçünde de 0 eşleşme**. Yani bulgu "görüldü"
   diye kaydedildi, kapanış kaydı hiç açılmadı.
2. **Kod düzeltmesi kanonik teslim kaydı olmadan yapıldı.** D-336 (`AGENTS.md`)
   `ajan_chat.py cmd_ac` içindeki sabit `"orkestrator"` yazımını kimlik zincirine
   bağladı ve `gorev_kutusu.py`'ye ikinci chat dosyasını okuyan `_mesaj_kontrol_et`
   ekledi. Ölçülen satırlar: `scripts/ajan_chat.py:45` (`cmd_ac`), `:50` (kimlik
   zinciri) · `scripts/gorev_kutusu.py:277` (`cmd_basla`), `:315`
   (`_chat_yeni_mesajlar(ajan, "")` KAPISI 1), `:370` (`_mesaj_kontrol_et`),
   `:419` (KAPISI 2 çağrısı).

Sonuç: **düzeltilmiş kod, kapısı olmayan bir teslimde duruyor.** Aynı desen
D-309/1'in kendi hatasıdır ("dört kapı: kod + kanıt + defter + karar").

**Yan bulgu (bu işin değil, kayıt için):** `AGENTS.md` D-336 satır
referansları bayat — `ajan_chat.py:46` yazıyor (ölçülen `:45`), `gorev_kutusu.py:308`
yazıyor (ölçülen `:277`). Bu brif **ölçülen** satırları kullanır. D-224 gereği
`dosya:satır` tahmin edilmez.

## Doğrulanacak varsayım

- `scripts/ajan_chat.py:50` satırında `(args.kimden or "").strip() or (chat_gonder.ajan_kimligi() or "")` ifadesi var. Yoksa **dur**, panoya sorun aç, uydurma.
- `scripts/gorev_kutusu.py:370` satırında `def _mesaj_kontrol_et(task_id: str)` tanımı var. Yoksa **dur**, panoya sorun aç, uydurma.
- `scripts/gorev_kutusu.py:315` satırında `_chat_yeni_mesajlar(ajan, "")` çağrısı `cmd_basla` içinde. Yoksa **dur**, panoya sorun aç, uydurma.
- `gorev_at.ALANLAR` = `('UI', 'API', 'VERI', 'TEST', 'DOC', 'ALTYAPI', 'ORKESTRA')`; `gorev_at._d57_dogrula('ORKESTRA-KIMLIK-ZINCIRI-01', <D-57 başlığı>, 'ihsan')` → `None` dönmeli. Dönmüyorsa **dur**, panoya sorun aç, uydurma.
- `ALANLAR` içinde `ORCH` **yok**. Eklendiyse D-225 ihlali — **dur**, panoya sorun aç, uydurma.
- `ESIK: kimlik çözülemeyen kayıt sayisi = 0`. `ajan_chat.py ac` komutu `HUGINN_AJAN` boşken hata verip **YAZMAMALI** (D-306 deseni). Yazıyorsa **dur**, panoya sorun aç, uydurma.

## Adımlar

1. **Kanonik kaydı aç.** `python scripts/gorev_at.py at --task-id ORKESTRA-KIMLIK-ZINCIRI-01 --baslik "<D-57 başlığı>" --ajan ihsan --oncelik P1 --dosya scripts/ajan_chat.py,scripts/gorev_kutusu.py --talimat "<brif yolu + ne yapılacak>" --cagiran ihsan`
   (brief bu dosya; D-66/D-80 üç şart: `brief` dolu + dosyada var, `talimat` dolu, tetik metni panoyla aynı).
2. **Kimlik zincirini iki ajanla doğrula.** `set HUGINN_AJAN=yasu` ve `set HUGINN_AJAN=utku` ile `ajan_chat.py ac` çalıştır; JSONL'de `"kimden"` alanı sırasıyla `yasu` / `utku` olmalı — `"orkestrator"` **değil**. Sonra `HUGINN_AJAN` **temizlenmiş** ortamda çalıştır: kayıt **yazılmamalı**, hata vermeli.
3. **İki kapıyı da kır.** KAPISI 1 (`basla`) ve KAPISI 2 (`teslim`) `messages.jsonl` içine `yanıt_alındı=false`, `task_id` eşleşen bir kayıt yaz → ikisi de **reddetmeli**. Sonra kaydı sil, yeşil doğrula (D-256/4: mandal kırılarak kanıtlanır).
4. **Bulgu kaydını karara bağla.** `ajan_chat.py kapat ORCH-KIMLIK-ZINCIRI-01 0 --karar "D-336 kodu düzeltti; kanonik görev ORKESTRA-KIMLIK-ZINCIRI-01 (D-222 Kural 4, D-57 ORCH reddi ölçüldü). Ölçüm: panoda 0 kayıt → 1 kayıt."`
5. **Bulgu defterine yaz** (D-67): `data/orchestrator/bulgu_defteri.md` → `[ihsan] [2026-10-04] [ORKESTRA-KIMLIK-ZINCIRI-01] [🟡] AGENTS.md D-336 satır referansları bayat (ajan_chat.py:46→:45, gorev_kutusu.py:308→:277) | karar: geriye dönük düzeltme yapılmaz, kanonik yol görev brifidir`.
6. **Hub'a yaz** (B-14): `hubs/ORKESTRASYON_AJANLAR_HUB.md` → "Kapanan işler" bölümüne `ORKESTRA-KIMLIK-ZINCIRI-01` satırı.

## Kabul kriteri

- [ ] `gorev_at.py pano` çıktısında `ORKESTRA-KIMLIK-ZINCIRI-01` **bir kez** görünüyor (D-222 mükerrer kapısı); arşivlerde hâlâ 0.
- [ ] `set HUGINN_AJAN=yasu` → `ajan_chat.py ac` → JSONL'de `"kimden":"yasu"`. Aynı `utku` için. Boş env → **kayıt yazılmıyor**.
- [ ] Kırılan iki kapı: `basla` ve `teslim`, `messages.jsonl`'deki eşleşen cevapsız kayıtta **reddetme sebebi** basıyor (kapı 4.1/4.2 kanıtı).
- [ ] `pytest tests/test_ajan_chat.py tests/test_gorev_kutusu_cli.py tests/test_brief_sablon_denetim.py -q` → bu değişiklikten **kaynaklanan 0 kırmızı**. Önceden gelen kırmızılar (bu brifi yazan gün: `test_brief_sablon_denetim.py` 6 kırmızı, hepsi başka ajanların eski brifinde) raporda **açıkça listelenir** — D-66 teslim kontrol listesi madde 2.
- [ ] `python scripts/kodlama_denetim.py` → bu iki script temiz.
- [ ] Chat kaydı `ORCH-KIMLIK-ZINCIRI-01#1` `cozuldu`, karar metninde kanonik görev kimliği geçiyor.

## Kurallar (D-224 · D-260 · D-266)

- **Her sayı ölçülür.** "Kapalar", "düzelir", "doğru" yazma; komut çıktısı yapıştır.
- **Kırmadan yeşil kanıt değildir.** Her düzeltme için bir kırma denemesi yap ve geri al (D-256/4).
- **Kanıtsız durum beyanı yasak:** her "yapıldı" satırı `dosya:satır` gösterir.
- **Panoya elle yazma** — yalnız `scripts/gorev_at.py` (D-225/D-77).
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz (D-235).
- Kapsam dışı bulguyu **düzeltme**; bulgu defterine yaz (D-67, cline kuralı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**, brifi yeniden okuyup beklemek değil:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir adım tıkandıysa → sorun aç, **sonraki adıma geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac <ajan> <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id <TASK_ID>
python scripts/chat_gonder.py --to <ajan> --type hata --task-id <TASK_ID> --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan ihsan --task-id ORKESTRA-KIMLIK-ZINCIRI-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).** İnsan tetiği bekleme; tek komutla nöbete gir:

```bash
python scripts/gorev_kutusu.py nobet --ajan ihsan
```

- Çıkış `0` = **İŞ VAR** → hemen yap.
- Çıkış `3` = 60 dk iş gelmedi → kısa rapor yaz, kapat.
- ⚠️ `nobet` **gömülü araç terminalinde çalıştırılmaz** (D-337): bloklayan komut, bağımsız terminalde ya da arka planda.

## Ilgili Nodlar

> **Zorunlu (D-218).** En az 2 wikilink. Göreve dokunan her yeni/değişen doküman buraya bağlanır, o dokümanın kendi `## Ilgili Nodlar` bölümünden bu brife geri link ver (çift yön).

- [[Huginn Data Insights/AGENTS]] — D-210 · D-217 · D-218 · D-222 · D-224 · D-225 · D-336 · D-337
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/scripts/ajan_chat]]
- [[Huginn Data Insights/scripts/gorev_kutusu]]