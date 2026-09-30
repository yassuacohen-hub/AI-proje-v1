# TSG-PILOT-20 — Brief (yasu)

**Başlık:** [OSINT] Ticaret Sicili Gazetesi 20 firma pilot **ÖLÇÜMÜ** (kod yazma, say)
**Öncelik:** P0 — TSG-04 bu ölçüme kilitli · **Kit:** `OSINT-KIT` (D-196)
**Kilitli dosya:** `plans/rapor_yasu_TSG-PILOT-20.md` (rapor; sen oluşturacaksın)
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın
"Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` **reddedilir**.
**Karar dayanağı:** D-306 · **Ön faz:** `plans/brief_yasu_ALTYAPI-TICARET-KANIT-01.md`

## Neden

TSG olay hattının kod tarafı bitti (D-306): MERSİS kapısı, kanıt katmanı, talep durum
makinesi, rapor üreteci, göçler — hepsi yazıldı, **91 test geçiyor**, göçler defterde.

Hat **tek bir yerde duruyor:** `ILAN_TURU_ESLEME` sözlüğü **boş**. Gazetenin
"İlan Türü" alanında hangi etiketlerin geçtiği **ölçülmedi**. Sözlük tahminle
doldurulmadı (D-268).

Bunun bugünkü somut sonucu: rapor üreteci olumsuz ilan bölümüne "ilan yok" değil
**"ÖLÇÜLEMEZ"** yazıyor. Doğrusu bu — çünkü tek etiket bile eşleşmiyor, "olumsuz
ilan yok" demek müşteriye **yanlış güvence** olurdu.

Bu görev kod yazmaz. **Sayar.** Sözlük senin çıktından dolacak.

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi).

**Ölçülmüş (girdi olarak güvenebilirsin):**
- TOBB ilan görüntüleme girişi **ücretsiz** (sayfa metninden birebir alındı).
- İlan kendi kalıcı referansını taşıyor: `ilan_sira_no-gazete_sayi-gazete_sayfa`
  → gerçek kayıt `49136-11649-67`.
- MERSİS gazetede **17** hane geliyor; kanonik **16**. İndirgeme yalnız
  `etl/kimlik_no.mersis_dogrula()` kapısında (D-306). **Kendi dilimini yazma.**
- Göç defteri **temiz**: 38 göç, 38 kayıt. `0037`/`0038` uygulanmış. Şema hazır —
  önceki turda "migrate.py kapalı, göç uygulanamaz" diye rapor edilmişti, bu
  **yanlıştı**; tek kapı `scripts/goc_defteri.py`. Senin önünde şema engeli yok.

**ÖLÇÜLMEMİŞ (senin işin — hiçbirini tahminle doldurma):**
- İlan türü etiketlerinin listesi.
- CAPTCHA sıklığı, oturum ömrü, firma başına süre.
- 20 firmanın kaçında sicil→VKN kapanıyor.

> Bu maddelerden birinde ölçüm tutmazsa **dur**, panoya sorun aç, uydurma.

## Örnek seçimi — rastgelelik ŞART

```sql
SELECT company_id, company_name, sicil_no
FROM companies
WHERE sicil_no IS NOT NULL AND tax_number IS NULL
  AND company_type <> 'sahis'
ORDER BY random() LIMIT 20;
```

Seçilen 20 firmanın `company_id` listesini rapora **aynen** yaz (tekrar üretilebilirlik).

**Kolay/tanıdık firma seçme.** Tanıdık firma seçilirse süre ve başarı oranı iyimser
ölçülür, üretimde patlar. Zor firma da atlanmaz — bulunamayan firma **bir ölçümdür**,
"0 sonuç" yazılır ve raporda kalır.

## Ölçülecekler — 7 kalem, her biri sayıyla

| # | Ölçüm | Nasıl | Neden |
|---|-------|-------|-------|
| 1 | CAPTCHA sıklığı | Kaç sorguda bir çıktı: `n/20` | 10 dk SLA'nın gerçekçiliği buna bağlı |
| 2 | Oturum ömrü | Kaç dakika **ve/veya** kaç sorgu sonra düştü | Toplu tarama tasarımı |
| 3 | Firma başına duvar saati | Her firma için dk; **min/medyan/maks** | 20 × süre = kapasite |
| 4 | **"İlan Türü" etiketlerinin TAM listesi + frekansı** | Gördüğün her etiketi **ham metniyle**, Türkçe karakterler bozulmadan | `ILAN_TURU_ESLEME` **yalnız** buradan dolar |
| 5 | İcra/iflas kutusu | Var mı; varsa içerik nasıl geliyor (ekran görüntüsü) | Raporun olumsuz ilan satırı |
| 6 | Tarih aralığı sorgusu | Destekleniyor mu; sınırı var mı | Tazeleme stratejisi |
| 7 | sicil→VKN kapanma oranı | `n/20`; kapanmayanların **sebebi** ayrı ayrı | İşin gerçek getirisi |

**4. kalem en kritiği.** Diğer altısı olmadan hat yine yürür; 4 olmadan yürümez.
Etiketi yorumlamadan, gördüğün gibi yaz — "sanırım tasfiye demek istiyor" değil,
ekrandaki harfler.

## Adımlar

1. Örneği çek (yukarıdaki SQL, `ORDER BY random()`), 20 `company_id`'yi **önce** rapora yaz —
   sonra ölçmeye başla. Sonradan yazmak, kötü giden firmayı listeden düşürme kapısını açar.
2. İlk 3 firmayı ölç ve **dur, bak**: 1-3. kalemler (CAPTCHA, oturum, süre) 10 dk SLA'yı
   imkânsız gösteriyorsa aşağıdaki **Durma kuralı** işler; kalan 17 firmayı boşuna koşma.
3. Kalan firmaları ölç. Her firma için: ilan türü etiketi **ham metniyle**, sicil→VKN sonucu,
   duvar saati süresi, kanıt dosyası (`data/kanit/`, anahtar `kanit_anahtari()` üretimi).
4. 5. ve 6. kalemleri (icra/iflas kutusu, tarih aralığı) arayüzde **bir kez** yokla — bunlar
   firma başına değil, kaynak özelliği.
5. 4. kalemi topla: etiket → frekans tablosu. Aynı anlama gelen iki yazım varsa **ikisini de**
   yaz, birleştirme; birleştirme kararı TSG-04'ün işi.
6. Raporu yaz: `plans/rapor_yasu_TSG-PILOT-20.md`. Ölçülemeyen kalem **"bilinmiyor"**.
7. Hub'a kapanış satırı (B-14), sonra `teslim`.

## Durma kuralı

1-3 arası ölçümler **10 dk SLA'yı imkânsız** gösteriyorsa: **dur**, raporu yaz,
SLA'yı ürün sahibine geri götür. Kod yazıp SLA'yı sonra sessizce esnetmek **yasak** (D-268).

Aynı şekilde: CAPTCHA her sorguda çıkıyorsa otomasyon kararı ürün sahibinindir,
senin değil. Ölç, bildir, bekle.

## Kabul kriteri

- [ ] `plans/rapor_yasu_TSG-PILOT-20.md` oluştu.
- [ ] Seçilen 20 `company_id` raporda aynen var.
- [ ] 7 ölçümün **7'si** sayıyla dolu. Ölçülemeyen kalem **"bilinmiyor"** yazılır —
      tahminle **doldurulmaz**, satır **silinmez**.
- [ ] 4. kalem: etiket listesi **ham metinle**, frekansıyla.
- [ ] Kapanmayan sicil→VKN vakalarının sebebi tek tek yazılı ("bulunamadı" yeterli değil;
      *ilan yok* mu, *MERSİS alanı boş* mu, *sağlama tutmadı* mı).
- [ ] Kanıt dosyaları `data/kanit/` altında, anahtar biçimi `kanit_anahtari()` üretimi.
- [ ] **Kod değişmedi.** `ILAN_TURU_ESLEME` bu görevde **doldurulmaz** — ölçüm ve
      yazma ayrı turlar (sözlüğü doldurmak TSG-04'ün işi, mandal testi bunu koruyor).
- [ ] `python -m pytest tests/test_ticaret_sicili_kanit.py tests/test_tsg_rapor.py -q`
      → **91 passed** (bozulmadığının kanıtı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Bu görev **ölçüm** görevi olduğu için özellikle kritik: ölçüm
tutmadığında susmak, ölçümü uydurmakla aynı sonucu verir.

- Brifteki bir varsayım tutmuyorsa (SQL boş dönerse, sayfa yapısı değiştiyse) → `ac` ile
  sorun aç, **uydurma**.
- CAPTCHA/oturum ölçümü SLA'yı imkânsız gösterirse → sorun aç, ürün sahibi kararını bekle.
- @mention aldıysan P0: **5-10 dk** içinde cevap zorunlu.

```bash
python scripts/ajan_chat.py ac yasu TSG-PILOT-20 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id TSG-PILOT-20
python scripts/chat_gonder.py --to orkestrator --type hata --task-id TSG-PILOT-20 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id TSG-PILOT-20 --ozet "<özet>" --cikti plans/rapor_yasu_TSG-PILOT-20.md
```

Özet **sayı** içerecek. "Pilot yapıldı, iyi gitti" reddedilir.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[plans/brief_yasu_ALTYAPI-TICARET-KANIT-01]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[docs/BORC_DEFTERI]]
