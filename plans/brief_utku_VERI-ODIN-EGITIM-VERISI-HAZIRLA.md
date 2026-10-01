# VERI-ODIN-EGITIM-VERISI-HAZIRLA — Brief (utku)

**Başlık:** [VERI] Odin eğitim veri setini yaz → data/odin_training_data.csv (7d)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır.

## Neden

Odin modelini eğitmek için 500-2000 adet eğitim örneği (input-output çift) gerekir. Bu örnekler:
- **Kaynağı:** Huginn Insights'ın kendi firma veritabanı (`company_master`), müşteri verisi değil (D-310, D-247, D-248 uyumu).
- **Etiket:** Sınıflandırma (NACE codes), özet üretimi, kalite tagging — mevcut pipeline'dan (D-252 NACE üç katman) çıkarılan gerçek çıktılar.
- **Format:** CSV veya JSONL — EVREN private eğitim API'nin beklediği formatta (ALTYAPI-EVREN-PRIVATE-DOGRULAMA görevinden çıkacak).

Bu görev: veritabanından 500-2000 örneği çıkart, doğrula, format'la.

## Doğrulanacak varsayım

- `company_master` tablosunda minimum 500 kayıt var ve kalitesi eğitim için yeterli (NULL/hatalı/bayat data <5%).
- NACE etiketleri (D-252 kapsamında) güvenilir kaynak: `company_nace_predictions` tablosu veya `nace_codes` referanslı.
- Veri sızıntısı riski minimal: hiçbir müşteri/üçüncü taraf verisi girmez (TCKN, gerçek kişi adı, şirket sırrı gibi).

## Adımlar

1. **Veri çekme (1s):** `company_master` → şirketi, sektörü, işletme türü, NACE kodu, `company_descriptions` özeti. SQL query:
   ```sql
   SELECT 
     id, unvan, sektor, isletme_tipi, nace_code, nace_name, 
     LEFT(description, 500) AS summary
   FROM company_master
   WHERE status = 'aktif' 
     AND nace_code IS NOT NULL
     AND LENGTH(description) > 50
   ORDER BY RAND()
   LIMIT 2000;
   ```

2. **Temizlik (1s):** 
   - Boş/NULL alanları işle (sil veya varsayılan yaz)
   - TCKN / şahıs kimliği varsa sil
   - HTML/Unicode temizlik (CP1254 → UTF-8)
   - Uzunluk doğrulaması (input max 1000 char, output max 500 char)

3. **Etiketleme (2s):**
   - Sınıflandırma örneği: `{"input": "Makine imalatı, Export, 120 çalışan", "output": "NACE: 28.11"}`
   - Özet örneği: `{"input": "Şirket X...", "output": "Kısa özet"}`
   - Kalite örneği: `{"input": "Veri", "output": "puanı: 8/10, nedenler: [...]"}`

4. **Oran doğrulaması (30d):**
   - Sınıflandırma: 50% (250-1000 örnek)
   - Özet: 30% (150-600 örnek)
   - Kalite: 20% (100-400 örnek)

5. **Format dönüşümü (30d):** 
   - Eğer EVREN CSV isterse: CSV (header + 500-2000 satır, UTF-8 BOM'suz)
   - Eğer JSONL isterse: JSONL (`{"input": "...", "output": "..."}\n` × 500-2000)

6. **Doğrulama (30d):**
   - Python script: dosya format'ı, encoding, satır sayısı, JSON/CSV schema (hata <5)
   - Test: 10 random örneği oku, human review (mantıklı mı?)

## Kabul kriteri

- [ ] `data/odin_training_data.csv` veya `.jsonl` (500-2000 satır) oluşturulmuş
- [ ] UTF-8 encoding, BOM yok, geçerli format (CSV header veya JSONL valid)
- [ ] Oran doğrulaması (sınıf/özet/kalite 50/30/20 ±5%)
- [ ] Hiçbir TCKN / müşteri verisi yok (regex scan)
- [ ] 10 örnek manuel review geçmiş (mantıklı input→output)
- [ ] YASU denetim: veri kaynağı canonical, NACE etiketler D-252 uyumlu

## Kurallar (VERI-KİT · D-196)

- Veri **mülkiyet:** Huginn'in kendi firma verisi, müşteri veri tabanı değil (D-248).
- Etiket **kaynağı:** Mevcut pipeline'dan (rule-based NACE, döküman özet fonksiyon, scoring), insan girdisi değil (ölçümü canlandır, beyan değil).
- Format: ALTYAPI-EVREN-PRIVATE-DOGRULAMA'dan çıkacak spesifikasyonu takip et.

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac utku VERI-ODIN-EGITIM-VERISI-HAZIRLA "<sorun>" --cozum "<oneri>"
python scripts/chat_gonder.py --to yasu --type rapor --task-id VERI-ODIN-EGITIM-VERISI-HAZIRLA --mesaj "<metin>"
```

- Başlangıç: "UTKU eğitim verisi hazırlamaya başlıyor; 2000 örneğin temizliği/etiketlemesi 14 Ekim'de bitmeli"
- Sonuç: "Veri hazır: [SIFLA COUNT] sınıflandırma, [OO COUNT] özet, [OOO COUNT] kalite örneği, TCKN/müşteri verisi taraması temiz"

## Teslim

- `data/odin_training_data.csv` (main) veya `data/odin_training_data.jsonl`
- `scripts/odin_veri_hazirla.py` (extraction + validation script)
- `data/odin_veri_dogrulama_raporu.md` (format + oran + sample check)
- `data/orchestrator/VERI-ODIN-EGITIM-VERISI-HAZIRLA_rapor_2026-10-14_uretim.md`

## Ilgili Nodlar

- [[D-310]] — Model Eğitim Güvenlik Sınırı
- [[D-252]] — NACE Üç Katman (etiket kaynağı)
- [[D-248]] — Kişisel Veri Saklılığı
- [[D-247]] — Veri Gösterimi Role Göre Ayrılır
