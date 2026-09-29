# DOC-BROWSERUSE-YASALLIK-01 — Brief (yasu)

**Başlık:** [DOC] Browser-Use yasallık raporunu yaz → rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md (2s)
**Öncelik:** P1 · **Kit:** `OSINT-KIT` (AGENTS.md D-196)
**Kilitli dosya:** `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

KAHİN sorusu: *"ticaretsicil.gov.tr üyelik istiyor, veriler geniş — bu mekanizmayı
kullanabilir miyiz?"* D-268 gereği adı doğrulamadan "var" denmedi; **ölçüldü**:

- `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` §2.1 — Browser-Use canlı
  çalıştı: `run_id 5624fb97-0b3b-4523-aa53-09daf8bfb32a`, `status=completed`,
  `0.016522 USD`, 2 dk 5 sn.
- Aynı dosya §2.3 — `robots.txt` ölçümü: TOBB **404** (yok), MERSİS catch-all,
  e-Devlet `Allow: /`.
- Aynı dosya §3.2 — KVKK Kurul **2022/6** kararı, 5174 sayılı Kanun md. 5/2-a
  gerekçesi.

Kanıtsız gerekçe yazılmayacak: yukarıdaki üç kanıt raporun temelidir.

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi). Kullanılan kaynakların gerçek
> referansları aşağıda sabitlenmiştir.

- `browser_use_sdk v3.11.3` kurulu varsayıldı → **doğrulandı** (`pip show`).
- `BROWSER_USE_API_KEY` `.env` içinde 46 karakter, `bu_` prefix → **doğrulandı**
  (değer ekrana basılmadı).
- Hesap **free plan** varsayıldı → **doğrulandı**: HTTP **403**
  `Model 'gpt-6-luna' is not available on the free plan`.
- `client.sessions` kaynağında **`create` metodu yok** varsayıldı → **doğrulandı**
  (`dir()` çıktısı: `get/get_message/list/purge/queue/remove_message/send_message`).
- MERSİS numarası 16 haneli, A.Ş./Ltd. Şti. için `0` ile başlar → kaynak:
  Webtekno, MERSİS sorgulama. **Resmî belgeyle teyit edilmedi**; kod yazılırsa
  format varsayımı olarak işaretlenmeli.
- e-Devlet `gtb-ticari-isletme-ve-sirket-sorgulama` **ücretsiz** ve login
  gerektirir varsayıldı → sayfa içeriğiyle doğrulandı, **fiyat/limit teyidi
  edilmedi**.

> Bu maddelerden biri kod/teyit ile tutmazsa **dur**, panoya sorun aç, uydurma.

## Adımlar

1. Raporu `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` konumuna yaz
   (8 bölüm: kanıt, yasal çerçeve, kaynak karşılaştırması, mimari, aksiyon,
   risk, sonuç).
2. Her iddiayı **kaynak bağlantısıyla** destekle; kanıtsız satır yazma.
3. "Yasal" ifadesi kullanmadan önce: kaynak metin mi, yorum mu ayır
   (**"bu rapor hukuki görüş değildir"** ibaresi zorunlu).
4. `python scripts/kodlama_denetim.py` → 0 ihlal.
5. Bu brifi `## İlgili Nodlar` ile çift yön bağla.

## Kabul kriteri

- [ ] Rapor `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` konumunda var.
- [ ] Browser-Use kanıtı: `run_id`, `status`, `cost`, `model` **gerçek değerlerle** yazılmış.
- [ ] `robots.txt` ölçümü üç site için de tablo hâlinde.
- [ ] Yasal dayanaklar: KVKK Kurul **2022/6**, FSEK **Ek md. 8**, TTK **md. 54-55**, Yargıtay 11. HD **E.2023/499, K.2024/8878**.
- [ ] Kaynak karşılaştırması tablosu: e-Devlet ⭐ / MERSİS ⭐ / TOBB ⛔.
- [ ] **"Hukuki görüş değildir"** ibaresi mevcut.
- [ ] `python scripts/kodlama_denetim.py` → bu dosya için 0 ihlal.
- [ ] `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne satır yazıldı.

## Kurallar (OSINT-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `DOC-BROWSERUSE-YASALLIK-01` satırı yaz (B-14 kapısı).

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
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id DOC-BROWSERUSE-YASALLIK-01 --ozet "<özet>"
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01]]
