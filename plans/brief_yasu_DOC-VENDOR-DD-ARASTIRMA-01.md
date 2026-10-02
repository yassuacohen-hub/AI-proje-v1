# DOC-VENDOR-DD-ARASTIRMA-01 — Brief (yasu)

**Başlık:** [DOC] Faz 5 tedarikçi denetim kapsamını araştır → docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md (4s)
**Öncelik:** P3 · **Kit:** `ADMIN` (AGENTS.md D-196)
**Kilitli dosya:** `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md`
**Hub:** `hubs/PLAN_STRATEGY_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Bu bir KOD görevi DEĞİL.** Şema yazma, göç yazma, tablo açma, Python yazma — hepsi **kapsam dışı**.
> Çıktı tek bir markdown belgesidir. Sebebi aşağıda `## Neden`'de ölçümle yazılı.

---

## Neden

Ürün Sahibi 6 fazlı yol haritasının **tamamının** kurulmasını istedi. Faz 2 ve Faz 3 için kod brifi
yazıldı (`VERI-RISK-MOTORU-01`, `VERI-ENTITY-GRAPH-01`), çünkü SSOT o fazları **tanımlıyor**.
Faz 5 için aynısını yapamadım. Sebebi ölçüldü:

| Kanıt | `dosya:satır` | Ne yazıyor |
|---|---|---|
| Faz 5'in SSOT'taki tüm içeriği | `yedekler/Huginn Data Insights (HUGIns).txt:867-869` | `Faz 5` + `Vendor Due Diligence Platformu` — **başka hiçbir şey yok** |
| Karşılaştırma: Faz 2'nin içeriği | aynı dosya `791-822` | 8 skorun adı, her biri tarif edilmiş |
| Karşılaştırma: Faz 3'ün içeriği | aynı dosya `760-779` | 10 düğüm türü sayılmış |

**Yani Faz 5'in SSOT'ta tablo adı yok, kolon adı yok, akış yok, ekran yok, hiçbir alt madde yok.**
Buna rağmen kod brifi yazsam tamamını uydurmuş olurdum — bu **D-260 ihlalidir** (kanıt yoksa iddia etme).

Bu yüzden görev şu: **eksik olan tanımı, SSOT'un VAR OLAN parçalarından türet.** Üç dayanağımız var:

1. **Müşterinin 7 sorusu** — `(HUGIns).txt:11-17`
2. **8 müşteri kitlesi** — `(HUGIns).txt:25-32` (Faz 5 bunlardan **"Satın alma"** ve **"Tedarik zinciri"** kitlesinin işi)
3. **Nihai Misyon** — `(HUGIns).txt:875-885`

"Vendor Due Diligence" = **tedarikçi ön denetimi**. Sade hali: bir şirket, mal/hizmet alacağı
firmayı sözleşme imzalamadan önce denetler. Faz 5 bu denetimi platformda **tek ekrana** indirmek demek.

---

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi). Aşağıdaki her madde **brif yazarken sabitlendi**.
> Kodda/dosyada başka bulursan: **dur, chat'e yaz, uydurma.**

- `yedekler/Huginn Data Insights (HUGIns).txt` dosyası var ve 1687 satır varsayıldı. Yoksa **dur**.
- Satır `867-869` Faz 5 başlığını, `11-17` 7 soruyu, `25-32` 8 kitleyi, `875-885` nihai misyonu
  içeriyor varsayıldı. **Satırları kendin aç ve gör** — benim verdiğim numaralara güvenme, teyit et (D-245).
- `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md` dosyası **diskte YOK** varsayıldı. Varsa **dur**, chat'e yaz.
- `hubs/PLAN_STRATEGY_HUB.md` dosyası var varsayıldı. Yoksa **dur**.
- Faz 2'nin 8 skoru (`corporateness_score` … `overall_trust_score`) henüz **tabloda yok**;
  `VERI-RISK-MOTORU-01` görevi onları açacak. Yani Faz 5 **Faz 2'ye bağımlıdır** varsayıldı.
  Bunu belgede açıkça yaz.

---

## Faz A — SSOT'u oku, elimizde NE VAR tablosunu çıkar

**Kök neden:** Faz 5'i tanımlamadan önce platformun bugün neyi cevaplayabildiğini bilmek gerekir.
Olmayan veriyle kapsam yazmak ikinci bir uydurma olur.

**Etkilenen dosya:** yalnız okuma — `yedekler/Huginn Data Insights (HUGIns).txt`

**Yapılacak:**
1. SSOT'ta `11-17` satırlarını oku, 7 soruyu **verbatim** kopyala.
2. `25-32` satırlarını oku, 8 kitleyi kopyala. **"Satın alma"** ve **"Tedarik zinciri"** satırlarını işaretle.
3. `791-822`'yi oku, 8 skorun adını al.
4. Belgeye şu tabloyu yaz (ilk 2 satır örnek, kalanını sen doldur):

| Müşterinin sorusu (SSOT satırı) | Bugün cevaplayabiliyor muyuz? | Hangi veriyle | Eksik olan |
|---|---|---|---|
| Gerçek bir şirket mi? (`:11`) | kısmen | `companies` + OSB dosyaları | MERSIS kapalı (D-257) |
| Dolandırıcılık riski var mı? (`:13`) | **hayır** | — | `fraud_risk_score` tablosu yok (Faz 2 açacak) |

**Doğrulama komutu (bu fazın sonunda çalıştır):**
```bash
python -c "import pathlib; p=pathlib.Path('../yedekler/Huginn Data Insights (HUGIns).txt'); print(len(p.read_text(encoding='utf-8').splitlines()))"
```
Çıkan sayı belgeye "SSOT satır sayısı (ölçüldü): N" olarak yazılır. Dosya bulunamazsa yolu düzelt, **uydurmadan** chat'e yaz.

---

## Faz B — "Tedarikçi denetimi" ne demek: 6 soruluk iskeleti yaz

**Kök neden:** Faz 5'in adı var, içeriği yok. İçeriği 7 sorudan **satın alma gözüyle** türeteceksin.

**Yapılacak:** Belgeye `## Tedarikçi Denetim Soruları` başlığı aç ve **en az 6 madde** yaz.
Her madde şu üç parçayı taşımak zorunda:

```
### S1 — <soru, sade Türkçe, tek cümle>
- **Neden önemli:** <satın almacı için hangi zararı önler>
- **Hangi veriyle cevaplanır:** <mevcut tablo/kolon adı VEYA "veri yok">
- **SSOT dayanağı:** `(HUGIns).txt:NN`
```

Örnek — birinci maddeyi ben yazdım, kalan beşini sen yazacaksın:

```
### S1 — Bu tedarikçi gerçekten var mı, kayıtlı mı?
- **Neden önemli:** Olmayan firmaya avans ödemesi en sık görülen tedarik zinciri zararıdır.
- **Hangi veriyle cevaplanır:** `companies.vkn` + `companies.legal_name` (var); MERSIS teyidi (D-257: kapalı, YOK).
- **SSOT dayanağı:** `(HUGIns).txt:11`
```

**Kural:** "Hangi veriyle cevaplanır" satırına **var olmayan bir tablo adı yazamazsın.**
Veri yoksa açıkça **"veri yok"** yaz (D-249: "veri yok" ile "0" ayrı şeylerdir).

**Doğrulama:** Belgedeki her `**Hangi veriyle cevaplanır:**` satırında geçen tablo/kolon adını
`src/company_master/schema/migrations/` içinde ara. Bulamadıysan satırı "veri yok" yap.
```bash
findstr /S /I /C:"<aradigin_kolon>" src\company_master\schema\migrations\*.sql
```

---

## Faz C — Eksik veri kaynakları listesi (en değerli çıktı)

**Kök neden:** Ürün Sahibi "eksik yerlerin kaydını tutalım" dedi (emir #39). Bu faz onun karşılığıdır.

**Yapılacak:** `## Eksik Veri Kaynakları` başlığı altında tablo:

| Eksik | Kimin işi | Nasıl elde edilir | Engel | Tahmini değer |
|---|---|---|---|---|
| Ticaret sicil teyidi | — | MERSIS | **kapalı** (D-257) | yüksek |
| Vergi borcu durumu | — | ? | araştırılacak | yüksek |

Her satırda **"Engel"** kolonu doldurulmak zorunda. "Bilmiyorum" geçerli bir cevaptır ve yazılır;
boş bırakmak geçerli değildir.

---

## Faz D — Üç yol önerisi + senin önerin

**Kök neden:** R3/alternatif kuralı — tek seçenek sunmak yasak.

**Yapılacak:** `## Yol Önerileri` başlığı, **3 seçenek**, her birinde artı/eksi ve **senin işaretli önerin**:

| Yol | Ne yapar | Artısı | Eksisi | Süre |
|---|---|---|---|---|
| A | Yalnız mevcut 8 skoru tek "tedarikçi karnesi" ekranında topla | en hızlı, yeni veri gerekmez | yeni bilgi üretmez | ? |
| B | 6 soruyu ayrı ayrı cevaplayan modül, eksikleri "ölçülmedi" yaz | dürüst, Faz 5'i gerçekten kurar | Faz 2 bitmeden başlamaz | ? |
| C | Harici veri satın al (ticaret sicil sağlayıcı) | boşluğu kapatır | maliyet + sözleşme | ? |

Süre kolonunu **sen tahmin et ve tahmin olduğunu yaz.** Önerini `← ÖNERİM` ile işaretle ve
**neden** onu seçtiğini 2 cümleyle yaz.

---

## Faz E — Öz-eleştiri satırı

Belgenin sonuna `## Öz-eleştiri` başlığı ve **en az 1 madde**: bu araştırmanın en zayıf yeri nedir?
Örnek kalıp: *"Faz 5'i satın alma gözüyle türettim; tedarik zinciri kitlesinin ihtiyacı farklı olabilir, ölçmedim."*

---

## Kabul kriteri

- [ ] `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md` oluşturuldu.
- [ ] **Faz A:** "elimizde ne var" tablosu ≥ 7 satır (7 sorunun her biri bir satır), her satırda SSOT satır numarası.
- [ ] **Faz B:** ≥ 6 denetim sorusu, her birinde üç alt madde (neden/hangi veri/SSOT dayanağı) dolu.
- [ ] **Faz B kapısı:** belgede geçen her tablo/kolon adı `migrations/*.sql` içinde **bulundu**; bulunmayanlar "veri yok" yazıldı.
- [ ] **Faz C:** eksik veri kaynakları tablosu ≥ 5 satır, "Engel" kolonunda boş hücre yok.
- [ ] **Faz D:** 3 yol önerisi + 1'i `← ÖNERİM` ile işaretli + gerekçesi yazılı.
- [ ] **Faz E:** öz-eleştiri ≥ 1 madde.
- [ ] Belgede ≥ 2 Obsidyen wikilink `[[...]]` (D-218).
- [ ] `hubs/PLAN_STRATEGY_HUB.md` "Kapanan işler"e `DOC-VENDOR-DD-ARASTIRMA-01` satırı yazıldı (B-14).

---

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kod yazmak YASAK.** Göç dosyası, tablo, Python modülü, test — hiçbiri bu görevde üretilmez.
  Kod gerektiğini düşündüğün yeri belgede **"ayrı görev gerekir"** diye not et.
- **Kanıtsız cümle yasak (D-260).** Her iddia `dosya:satır` gösterir. Göstermiyorsa cümleyi
  "bu ölçülmedi" diye yaz; silmek de uydurmak kadar yanlıştır.
- "Veri yok" ile "0" karıştırılmaz (D-249).
- Yeni bağımlılık ekleme; yeni dosya açma (tek çıktı dosyası dışında).
- **Teslimden önce** `hubs/PLAN_STRATEGY_HUB.md` "Kapanan işler" bölümüne satır yaz (B-14 kapısı).

---

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**, brifi yeniden okuyup beklemek değil:

- SSOT satır numaraları tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac yasu DOC-VENDOR-DD-ARASTIRMA-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id DOC-VENDOR-DD-ARASTIRMA-01
python scripts/chat_gonder.py --to ihsan --type soru --task-id DOC-VENDOR-DD-ARASTIRMA-01 --mesaj "<metin>"
```

---

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id DOC-VENDOR-DD-ARASTIRMA-01 --ozet "<özet>"
```

Teslim özetinde **şu üç sayı** olmak zorunda: kaç denetim sorusu yazıldı · kaç eksik veri kaynağı bulundu ·
kaç iddia `dosya:satır` ile kanıtlandı.

**Teslimden sonra DURMAK YASAK (D-312).** İnsan tetiği bekleme; posta + chat kontrolü zorunlu:

```bash
python scripts/gorev_kutusu.py bak --ajan yasu      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10            # chat: cevap bekleyen mesaj var mi?
```

- Mesaj varsa → **cevapla**.
- Yeni görev varsa → `al` ile al, baştan başla.
- İkisi de boşsa → `basla --ajan yasu` ile zinciri yeniden yokla.
- Döngü sonsuzdur: iş bitti demek "bekle" demek değildir.

---

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[hubs/PLAN_STRATEGY_HUB]]
- [[plans/brief_utku_VERI-RISK-MOTORU-01]]
- [[plans/_brief_sablon]]
