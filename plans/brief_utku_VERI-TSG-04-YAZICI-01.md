# VERI-TSG-04-YAZICI-01 — Brief (utku)

**Başlık:** [VERI] TSG-04 yazma hattını yaz → company_events INSERT pipeline'ı (3s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/tsg_yazici.py`
**Bağımlılık:** yok
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

## Neden

Ölçüldü (2026-09-30, yasu): TSG-04 eşleme sözlüğü (`ILAN_TURU_ESLEME`,
[`skills/services/ticaret_sicili_kanit.py:114-180`](skills/services/ticaret_sicili_kanit.py:114))
65/65 etiketle hazır ve mandal testiyle korunuyor
([`tests/test_ticaret_sicili_kanit.py:123-139`](tests/test_ticaret_sicili_kanit.py:123)).
Şema kapıları da açık: [`0037_tsg_olay_hatti.sql`](src/company_master/schema/migrations/0037_tsg_olay_hatti.sql:1)
`company_events.source_guid/event_person/person_role` kolonlarını + `uq_company_events_source_guid`
kısmi indeksini ekledi.

Ama repo genelinde `company_events` tablosuna **yazan hiçbir kod yok** — ne
`INSERT`, ne `.table("company_events")` çağrısı. `olay_esle()`
([`skills/services/ticaret_sicili_kanit.py:183`](skills/services/ticaret_sicili_kanit.py:183))
saf bir eşleme fonksiyonu; tek çağıranı
[`skills/services/tsg_rapor.py:112`](skills/services/tsg_rapor.py:112) de yalnızca
Markdown rapor metni üretiyor, DB'ye dokunmuyor (dosyanın kendi docstring'i
"DB yok, ağ yok" diyor). Yani sözlük + şema var, **pipeline yok** — TSG
akışının sonucu hiçbir satır olarak `company_events`'e düşmüyor.

## Doğrulanacak varsayım

- `company_events` tablosu ve `source_guid`/`event_person`/`person_role`
  kolonları [`0037_tsg_olay_hatti.sql`](src/company_master/schema/migrations/0037_tsg_olay_hatti.sql:1)
  ile şemada var varsaydı. Yoksa **dur**, panoya sorun aç, uydurma.
- `olay_esle(ilan_turu)` [`skills/services/ticaret_sicili_kanit.py:183`](skills/services/ticaret_sicili_kanit.py:183)
  imzası `(event_type, direction)` döndürüyor varsayıldı. Farklıysa **dur**.
- TSG-PILOT-20 ölçümünün kanıt formatı (`IlanKaniti` alanları) tek girdi
  kaynağı varsayıldı. Başka bir kaynak (Düzey_3 XML) varsa **dur**, KAHİN'e sor.

## Adımlar

1. Kaynak kararını netleştir: TSG-PILOT-20'nin `IlanKaniti` çıktısı mı yoksa
   Düzey_3 abonelik XML/TSM akışı mı `company_events`'e yazılacak asıl girdi?
   ([`gazete_ocr.py:1-19`](scripts/gazete_ocr.py:1) D-278 ile OCR'ı pasife aldı,
   Düzey_3'ü öneriyor ama entegrasyon kodu henüz yok). Belirsizse KAHİN'e sor,
   uydurma.
2. `src/company_master/etl/tsg_yazici.py` yaz: `IlanKaniti` (veya seçilen
   kaynak) listesini alır, her kayıt için `olay_esle()` çağırır,
   `source_guid` ile tekillik kontrolü yapar (UNIQUE indeks zaten var —
   çakışan satır atlanır, hata fırlatmaz), `company_events` satırı üretir.
3. `companies.son_teyit_tarihi` kolonunu (aynı migration'da eklendi) TSG
   kaynağından teyit edilen firma için güncelleyen adımı ekle.
4. Testte gerçek DB'ye yazmadan (mock/fixture ile) tekillik + eşleme
   davranışını doğrula.

## Kabul kriteri

- [ ] `tsg_yazici.py` içinde `company_events` satırı üreten fonksiyon var,
      `dosya:satır` ile gösterilebilir.
- [ ] `source_guid` çakışması sessizce atlanıyor (ikinci yazım aynı ilanı
      tekrar eklemez) — test kanıtlı.
- [ ] `companies.son_teyit_tarihi` gerçek TSG teyidinde güncelleniyor.
- [ ] Mevcut mandal testleri (`test_ticaret_sicili_kanit.py`) kırılmıyor.

## Kurallar (VERI-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler"
  bölümüne `VERI-TSG-04-YAZICI-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- Kaynak kararı (Adım 1) belirsizse → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki adıma geç**, zinciri durdurma.
- @mention aldıysan → P1 için 10-15 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac utku VERI-TSG-04-YAZICI-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-TSG-04-YAZICI-01
python scripts/chat_gonder.py --to utku --type hata --task-id VERI-TSG-04-YAZICI-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-TSG-04-YAZICI-01 --ozet "<özet>"
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/_brief_sablon]]
