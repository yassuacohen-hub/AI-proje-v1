# VERI-TSG-ESLEME-CASE-01 — Brief (utku)

**Başlık:** [VERI] TSG ilan türü eşlemesini düzelt → olay_esle normalize + canlı unknown ölçümü (1s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/etl/tsg_yazici.py`, `skills/services/ticaret_sicili_kanit.py`
**Bağımlılık:** VERI-TSG-04-YAZICI-01 (kapanmış)
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

## Neden

Ölçüldü (2026-09-30 / 2026-10-01, orkestrator): VERI-TSG-04-YAZICI-01 teslimi kontrol edildiğinde [`skills/services/ticaret_sicili_kanit.py:183-192`](skills/services/ticaret_sicili_kanit.py:183) `olay_esle()` fonksiyonu büyük/küçük harf duyarlı **case-sensitive** çalışıyor. Ama `ILAN_TURU_ESLEME` sözlüğü [`skills/services/ticaret_sicili_kanit.py:114-180`](skills/services/ticaret_sicili_kanit.py:114) karışık harfle (örn: `"Tespit edilen husus"`, `"IPTAL"`, `"Tasfiye"`) tanımlanmış. Sonuç:

- **306/326** kanıt kaydında `event_type=NULL` (boş etiket) — **çünkü eşleşme başarısız**
- **20/326** kayıtta eşleşme oldu (doğru)
- Hata **yalnız dolu 20 etiketi vuruyor**, 306 boşa "beklenen davranış" deniyor

**BORC-TSG-ESLEME-CASE-01** (D-260 borcu): Dolu 20 etiketi de tutarlı normalize etmeliyiz. Seçenekler:

1. **ILAN_TURU_ESLEME sözlüğü normalize** → `.upper()` + girdiler tutarlı hale getiril
2. **oday_esle girişi normalize** → `ilan_turu.upper()` ile sözlüğe gitmeden önce
3. **İkisi de** — tercih edilen (D-288: zincir testi)

Ek sorun (D-260): canlı `company_events` tablosundaki unknown sayısı **hiç ölçülmedi** (D-238 kuralı — veri ölçüsü canlı DB'den).

## Doğrulanacak varsayım

- `olay_esle(ilan_turu)` [`skills/services/ticaret_sicili_kanit.py:183`](skills/services/ticaret_sicili_kanit.py:183) fonksiyonu ve `ILAN_TURU_ESLEME` sözlüğü [`skills/services/ticaret_sicili_kanit.py:114-180`](skills/services/ticaret_sicili_kanit.py:114) tek kaynaklar varsayıldı. Başka eşleme yeri varsa **dur**, panoya sorun aç.
- `company_events` tablosu `event_type` kolonu barındırıyor varsayıldı (migration `0037_tsg_olay_hatti.sql`). Yoksa **dur**.
- Canlı kaydı (örn: SELECT COUNT(*) FROM company_events WHERE event_type IS NULL) yapabilirim varsayıldı. Yoksa **dur**, DB bağlantı sorunu panoya not düş.

## Adımlar

1. **Normalize seçeneğini seç:**
   - (A) ILAN_TURU_ESLEME sözlüğünü `.upper()` ile kalıcı normalize et (80 satırı dokunmayan)
   - (B) oday_esle fonksiyonunun girişi normalize et (1 satır `.upper()` ekle)
   - (C) İkisi de (tercih: D-288 zincir koruması)
   - Seçim kararını chat'e yaz (sorun aç, **uydurma değil**)

2. **Normalize kodu yaz:** Seçilen yolu uygula.

3. **Canlı ölçüm (D-238, D-260):**
   ```sql
   SELECT event_type, COUNT(*) FROM company_events GROUP BY event_type ORDER BY COUNT(*) DESC;
   ```
   Sonuç ekran kapta: `unknown/NULL` satır sayısı ve dolu satır sayısı (beklenti: 306→0 veya ilerleme, 20→artış).

4. **Zincir test (D-288):** tsg_yazici pipeline'ı çalıştırıp (--dry-run) kanıt dosyalarından başlayıp `company_events`'e yazılan kaydı izle.

5. **Mevcut testler:** test_ticaret_sicili_kanit.py kırılmıyor (regresyon).

## Kabul kriteri

- [ ] `oday_esle()` veya `ILAN_TURU_ESLEME` normalize uygulandı, seçim kaydedildi.
- [ ] Canlı COUNT sorgusu çalıştırıldı, sonuç brifin sonunda yazıldı.
- [ ] test_ticaret_sicili_kanit.py yeşil kalıyor (regresyon yok).
- [ ] Zincir test: kanıt dosyası → tsg_yazici → company_events yazımı izlenebiliyor.

## Kurallar (VERI-KİT · D-196)

- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne `VERI-TSG-ESLEME-CASE-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- Normalize seçeneği belirsizse → `ac` ile sorun aç, **uydurma, durma**.
- Canlı DB sorgusu başarısızsa → sorun aç, **durma**.
- Zincir testinde bağlantı kırılıyorsa → sorun aç, **durma**.

```bash
python scripts/ajan_chat.py ac utku VERI-TSG-ESLEME-CASE-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-TSG-ESLEME-CASE-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-TSG-ESLEME-CASE-01 --ozet "<özet>"
```

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/data/orchestrator/onay_kuyrugu]] (BORC-TSG-ESLEME-CASE-01)
- [[plans/_brief_sablon]]
