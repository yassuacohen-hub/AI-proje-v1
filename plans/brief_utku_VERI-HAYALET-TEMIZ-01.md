# Brif — VERI-HAYALET-TEMIZ-01 (P0)

**Başlık:** [VERI] Hayalet firma kayıtlarını temizle (canlı DB kirli, kod güvende) (3s)
**Öncelik:** P0 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/hayalet_kayit_temizle.py`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Mod:** code · **Süre:** 3s · **Kaynak:** ihsan (KAHİN denetimi 2026-09-27)

## Neden
`companies` tablosunda **14003 satır var, gerçek tekil firma 9412**. Aradaki **4591 satır hayalet** — kazıyıcı aynı firmayı defalarca yazmış.

### Kanıt (canlı Supabase, ölçüldü)

```
companies toplam      : 14003
companies tekil ad    :  9412
tekrarli ad grubu     :   494
fazlalik satir        :  4591   <-- silinecek
vergi_no dolu         :   774
ivedik kayitli firma  :  3134
```

Kaynak bazında:

| kaynak | satır | tekil | oran |
|--------|-------|-------|------|
| ostim.org.tr | 9513 | 8740 | %91.9 |
| **ivedik.org.tr** | **3134** | **14** | **%0.4** |
| baskentosb.org.tr | 761 | 481 | %63.2 |
| aso.org.tr | 592 | 592 | %100 |

İvedik'te 14 firma **224'er kez** yazılmış:

```
228 x FATIH BAĞBAŞI
224 x EGEMEN PANO
224 x ARAD BRANDING
224 x ALİ EŞREF ERKANİ
... (14 ünvan, her biri ~224 kopya)
```

## Kök neden — ZATEN DÜZELTİLDİ

WordPress tabanlı OSB siteleri geçersiz `?page/N/` isteğine **sayfa 1'i** döndürür. Eski kazıyıcıdaki "liste boşalınca dur" koşulu hiç gerçekleşmez → sonsuz döngü.

Koruma [`base_osfb_scraper.sayfa_dongusu()`](../src/company_master/etl/scrapers/base_osfb_scraper.py:101) içinde mevcut (D-235): `MAX_SAYFA=500` sert tavan + `TEKRAR_TOLERANSI=2` imza karşılaştırması + ünvan tekilleştirme. 14 test yeşil.

**Yani kod güvende — kirli olan sadece veritabanı.**

## Adımlar
`src/company_master/etl/hayalet_kayit_temizle.py`

1. **Önce yedek**: silinecek satırları `data/backup/hayalet_YYYYMMDD.jsonl`'e yaz.
2. Aynı `legal_name` grubunda **hangi satırın kalacağını** şu sıraya göre seç:
   - `vergi_no`/`tax_number` dolu olan öncelikli (774 satır bu bilgiye sahip),
   - sonra en çok alanı dolu olan,
   - eşitlikte en küçük `company_id`.
3. Kalan satırın eksik alanlarını kopyalardan **birleştir** — veri kaybı olmasın (telefon, e-posta, adres, web sitesi).
4. Silmeden önce bağlı satırları kalan kayda taşı: `company_industries`, `nace_validity`, `source_records` bağları.
5. Sil.
6. Tekrar oluşmasın diye: `companies.legal_name` üzerine **UNIQUE kısıt** ekle (migration).

## Kabul kriteri
- `select count(*) from companies` = `select count(distinct legal_name) from companies`
- Silmeden önceki vergi numarası dolu sayısı korunur: **774** (düşerse iş reddedilir)
  — dikkat: bu sayı `vergi_no` **ve** `tax_number` kolonlarının birleşimidir (D-244, kolon ikizi)
- Yedek dosyası mevcut ve satır sayısı = silinen satır sayısı
- UNIQUE kısıt migration dosyası var
- Test: `tests/test_hayalet_kayit_temizle.py` — sahte veriyle birleştirme + seçim sırası doğrulanır

## KAHİN ölçümü — 2026-09-27 21:30 (canlı Supabase)

Bu iş `review`a taşınmıştı; ölçüm sonucu **kapatılamaz** durumda:

| kriter | beklenen | ölçülen | sonuç |
|--------|----------|---------|-------|
| `count(*)` = `count(distinct legal_name)` | eşit | 9412 = 9412, fazlalık **0** | ✅ |
| UNIQUE kısıt | var | `uq_companies_legal_name` mevcut | ✅ |
| `vergi_no` dolu | 774 | **761** | ⚠️ kriter hatalı (aşağıda) |
| yedek dosyası = silinen satır | 4591 satır | **yedek yok** — `yedekler/` dizini hiç oluşmamış | ❌ |

### 13 satırlık fark: veri kaybı değil, kriter hatası

Yukarıdaki **774** sayısı bu brifin "Kanıt" bölümünde, **14003 satırlık kirli
tabloda** ölçülmüştü. Aynı ünvanın iki kaydında da vergi numarası varsa
tekilleştirmede sayaç bir düşer — 494 tekrarlı grupta bu 13 kez olmuş.
Beklenen davranış: `hayalet_kayit_temizle.py` zaten "vergi numarası dolu olanı
tut" sıralamasıyla çalışıyor ve hiçbir numarayı silmiyor, yalnız mükerrer
sayım eriyor. Kriter `count(*)` yerine `count(distinct vergi_no)` yazılmalıydı.
Kural: **D-244 dördüncü madde**.

### Gerçek kusur: yedek alınmamış

Silme yapılmış ama `yedekler/` dizini hiç oluşmamış. 4591 satır geri
getirilemiyor: ham kazı dosyalarının hiçbirinde vergi numarası yok (`data/aso`
0, `data/baskent` 0, `data/ivedik` 0, `data/merged/multi_osb_merged.jsonl` 0).
Veri kaybı tespit edilmedi (13 fark açıklandı), ama **kanıtlanamıyor** da.

Alınan önlem: `yedekler/companies_20260927_2124.jsonl` (9412 satır) — silme
sonrası ilk gerçek yedek, bundan sonraki işler için taban. Kural D-244.

### Karar (ürün sahibi, 2026-09-27)

İş **kapatıldı**. Fark açıklandı, kovalanacak veri yok. Yedeksiz silme kusuru
D-244 olarak kurala çevrildi. Kolon ikizi (`tax_number`/`vergi_no`,
`website_domain`/`web_sitesi`) ayrı iş: `VERI-KOLON-IKIZ-01`.

## Uyarı

Bu iş **geri alınamaz**. Yedek yazılmadan tek satır silinmeyecek. Adım 3 (birleştirme) atlanırsa kopyalarda duran iletişim bilgisi kaybolur — silme değil, **toplama** işi bu.

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- Kök neden **zaten düzeltildi** varsayıldı — kod güvende, kirli olan yalnızca veritabanı. Kod tekrar üretiyorsa **dur**, KAHİN'e sor.
- `companies.legal_name` alanında hayalet (boş/kukla) kayıt olduğu varsayıldı; sayı canlı Supabase ölçümünden alınacak.
- Silme öncesi `data/backup/hayalet_YYYYMMDD.jsonl` yedeği **zorunlu** varsayıldı. Yedek yazılamıyorsa silme yapılmaz.
- `company_industries` ve `source_records` üzerinde bağlı kayıt olabileceği varsayıldı — yetim satır bırakılmayacak.
- `tests/test_hayalet_kayit_temizle.py` testi yazılacak varsayıldı.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-HAYALET-TEMIZ-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-HAYALET-TEMIZ-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-HAYALET-TEMIZ-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-HAYALET-TEMIZ-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
