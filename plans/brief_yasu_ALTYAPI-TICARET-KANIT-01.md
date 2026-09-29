# ALTYAPI-TICARET-KANIT-01 — Brief (yasu)

**Başlık:** [ALTYAPI] Kanıt katmanını yaz → skills/services/ticaret_sicili_kanit.py (2s)
**Öncelik:** P1 · **Kit:** `OSINT-KIT` (AGENTS.md D-196)
**Kilitli dosya:** `skills/services/ticaret_sicili_kanit.py`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

KAHİN'in ekran görüntüleri (2026-09-29) verinin **kendi kalıcı referansı**
taşıdığını gösterdi: `Sayı + Sayfa + içerik_no`. Bu, doğrulanabilir veri demektir.

Ayrıca iki **gerçek hata** ölçüldü ve düzeltildi:
- `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` §9.3 — MERSİS **17** hane
  (`0` + VKN 10 + ek 6), Webtekno'nun "16" iddiası yanlış.
- Aynı dosya — TOBB girişi **ücretsiz**; ilk rapor "ücretli" demişti (varsayım).

Bu görev: ölçülen gerçeği **kodla koruyan** kalıcı katmanı yazar.

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi). Aşağıdakilerin hepsi **ölçülmüştür**.

- `MERSIS = "00120320741000024"` → **17 hane** (gerçek ilan metninden).
  Çözüm: ön eki `0`, VKN `0120320741` (10), ek `000024` (6).
- `KAYNAK_URL = "https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php"`
  → sayfa içeriğinden doğrulandı; giriş **ücretsiz** metni birebir alındı.
- `KANIT_DIZIN = <kok>/data/kanit` → yeni dizin; var **değildi**, oluşturuldu.
- Anahtar biçimi `ilan_sira_no-gazete_sayi-gazete_sayfa` → gerçek kayıtta
  `49136-11649-67`.
- **`?` Windows dosya adında geçersizdir** → `OSError` ile **ölçüldü**;
  eksik alan `E` (empty) üretir.
- Türkçe `ŞUBESİ`.upper() → `ŞUBESİ` kalır (`İ`→`I` dönüşümü `.upper()`'da
  güvenilir değildir) → Unicode **NFKD normalize** gerekir.

> Bu maddelerden biri ölçümle tutmazsa **dur**, panoya sorun aç, uydurma.

## Adımlar

1. `IlanKaniti` dataclass: ilan metnindeki gerçek etiketler. Eksik alan `None`.
2. `dogrula()` kuralları: MERSİS biçimi + çözümü · şube tespiti · zorunlu alanlar ·
   yayın/tescil tarih sırası · alan doluluk.
3. `kanit_anahtari()`: yalnızca alfanümerik; eksik alan `E`.
4. `_asciiye()`: NFKD normalize ile Türkçe → ASCII.
5. `kanit_kaydet` / `kanit_listele` yeteneklerini `registry.register` ile kaydet.
6. `tests/test_ticaret_sicili_kanit.py` yaz: gerçek kayıt + **bilerek bozuk** kayıt.

## Kabul kriteri

- [ ] `kanit_kaydet` gerçek kaydı `gecerli` ile yazar → `data/kanit/49136-11649-67.json`.
- [ ] MERSİS çözümü testte doğrulanır: `VKN=0120320741`, `ek=000024`.
- [ ] Bozuk MERSİS (`"123"`) → `MERSIS_BICIM` + `sonuc == "supheli"`.
- [ ] Yayın, tescilden önceyse → `TARIH_SIRASI` hatası.
- [ ] **Bilinmeyen tarih formatı** kontrolü atlar (uydurulmaz, D-268).
- [ ] Anahtar `49136-E-E` üretir ve dosya **çökmez** (Windows `?` tuzağı).
- [ ] `sirket_tipi`: `ŞUBESİ` → `sube`, `ANONİM ŞİRKET` → `as`.
- [ ] **Şüpheli kanıt silinmez**, `sonuc` alanında işaretlenir (D-216).
- [ ] Bozuk JSON `okunamadi` olarak listelenir, istisna fırlatmaz.
- [ ] `python -m pytest tests/test_ticaret_sicili_kanit.py` → **20 passed**.
- [ ] `python scripts/kodlama_denetim.py` → bu dosyalarda 0 ihlal.
- [ ] `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne satır yazıldı.

## Kurallar (OSINT-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `ALTYAPI-TICARET-KANIT-01` satırı yaz (B-14 kapısı).

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

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01]]

---

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-TICARET-KANIT-01 --ozet "<özet>"
```

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
