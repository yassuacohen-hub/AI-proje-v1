# VERI-TENDER-KOLON-01 — Brief (utku)

**Başlık:** [VERI] D-308 tender sema kolon çevirisi → osb_tender_monitor.py uyumlu hale getir (1s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/osb_tender_monitor.py`
**Bağımlılık:** VERI-02 (D-308 göçü) — öncesinde başlanabilir ama D-308 göçü yürümüş olması şart
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

## Neden

Ölçüldü (2026-09-30, orkestrator): D-308 **göçü** (migration `0043_tender_sema_cevirisi.sql`) ihale_ilanlari tablosunun kolon adlarını **Türkçe→İngilizce** çevirdi:

| Eski (Türkçe) | Yeni (İngilizce) |
|---------------|-----------------|
| `ilan_basligi` | `tender_title` |
| `ilan_turu` | `tender_type` |
| `osb_adi` | `osb_name` |
| `tahmini_maliyet` | `estimated_cost` |
| `birim` | `unit` |
| `aciklama` | `description` |
| `belge_url` | `document_url` |
| `il` | `province` |

Ama [`src/company_master/etl/osb_tender_monitor.py`](src/company_master/etl/osb_tender_monitor.py:1) **hiçbir zaman çalıştırılmadı** (D-309: "Kod yazılmıştı ama koşturulmamıştı"). Dosya **hala eski Türkçe kolon adlarını** kullanıyor (ilan_basligi, ilan_turu, osb_adi, ...). Sonuç: D-308 göçü uygulanırsa kod **KeyError** ya da **NULL tutanlar** ile patlar.

**BORC-TENDER-KOD-01** (D-308 borcu): osb_tender_monitor.py'yi İngilizce kolon adlarıyla uyumlu hale getir, test yaz, prova (`--dry-run`) çalıştır.

## Doğrulanacak varsayım

- `ihale_ilanlari` tablosunun kolon adları D-308 göçünde [`src/company_master/schema/migrations/0043_tender_sema_cevirisi.sql`](src/company_master/schema/migrations/0043_tender_sema_cevirisi.sql:1) ile Türkçe→İngilizce çevrildiği varsayıldı. Göç dosyası yoksa **dur**, panoya sorun aç.
- osb_tender_monitor.py tek çağrı noktası varsayıldı. Başka dosya `ihale_ilanlari`'nı okuyor/yazıyorsa **dur**, gerçek kaynakları panoya listeleve sorun aç.
- 8 kolon adının tamamı koddaki değişkenleri/sorgularda kullanılıyor varsayıldı. Bazıları dead code ise kaldırmak uygun.

## Adımlar

1. **Kolon adları listesini doğrula:** [`src/company_master/schema/migrations/0043_tender_sema_cevirisi.sql`](src/company_master/schema/migrations/0043_tender_sema_cevirisi.sql:1) açıp RENAME COLUMN satırlarını oku, yukarıdaki tablonun doğru olduğunu onaylı (8 kolon).

2. **osb_tender_monitor.py güncelle:** 8 Türkçe kolon adı → 8 İngilizce kolon adı. Örn:
   ```python
   # Eski
   r['ilan_basligi']
   # Yeni
   r['tender_title']
   ```
   Değiştir (tüm 8 kolon referansı).

3. **Test yaz:** 13 uyumsuzluk tespit etmeli (kolon adı değişikliği tamamlandı vb.):
   ```python
   def test_osb_tender_kolon_cevirisi():
       # Eski kolon adları KeyError veya None döner
       # Yeni kolon adları doğru veriyi alır
       assert osb_tender_monitor.extract_from_record(...)['tender_title'] == "..."
   ```

4. **Prova (`--dry-run`) çalıştır:** D-308 göçü uygulanmış test DB'de veya fixture ile çalıştır. Hata yok mu kontrol et.

5. **Bağımlılık zinciri (D-288):** VERI-02 ile DAG uyumlu olup olmadığı kontrol et. VERI-02 sonra bu görev başlasın.

## Kabul kriteri

- [ ] 8 Türkçe kolon adı → 8 İngilizce kolon adı değiştirildi, dosya:satır gösterilebiliyor.
- [ ] Test yaz, 13 uyumsuzluk başlık vardır, pytest yeşil.
- [ ] `--dry-run` modu çalıştırıldı, hata yok.
- [ ] Mevcut mandal testleri (regression) kırılmıyor.
- [ ] VERI-02 ile DAG bağımlılığı kontrol edildi.

## Kurallar (VERI-KİT · D-196)

- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne `VERI-TENDER-KOLON-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- D-308 göçü dosyası yoksa veya kolon adları farklıysa → `ac` ile sorun aç, **uydurma, durma**.
- Prova hatası verirse → sorun aç, **durma**.
- DAG bağımlılığı kırılıyorsa → sorun aç, **durma**.

```bash
python scripts/ajan_chat.py ac utku VERI-TENDER-KOLON-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-TENDER-KOLON-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-TENDER-KOLON-01 --ozet "<özet>"
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/data/orchestrator/onay_kuyrugu]] (BORC-TENDER-KOD-01)
- [[plans/_brief_sablon]]
