# brief_yasu_VERI-SEMA-DOGRULA-02 — Kod Taraması: Eksik Tablolar

## Neden

**SEMA-DENETIM-01 (V21):** `0021_missing_tables.sql` dosyasında 5 tablo belirtildi, fakat kodda 2 tablo hâlâ sorgulanıyor ama şemada yok:
- ❌ `entity_matches` — nerede sorgulanıyor?
- ❌ `api_usage_daily` — nerede sorgulanıyor?

Bu bilgi olmadan SALIH şema tasarım yapamaz. YASU'ya: kod taraması yap, sonuç raporla.

## Doğrulanacak varsayım

1. `entity_matches` tablosu kaç dosyada sorgulanıyor?
2. `api_usage_daily` tablosu kaç dosyada sorgulanıyor?
3. Her sorgu hangi işlemi yapıyor (INSERT, SELECT, COUNT vb.)?
4. İçinde ne veri olması gerekiyor (hangi sütunlar)?

## Adımlar

1. **Kod taraması — entity_matches:**
   ```bash
   # src/ ve scripts/ dizinlerinde arama yap
   grep -r "entity_matches" src/ scripts/ --include="*.py"
   ```
   Her bulgu için: dosya adı, satır numarası, konteksti yaz (çevre 3-5 satır)

2. **Kod taraması — api_usage_daily:**
   ```bash
   grep -r "api_usage_daily" src/ scripts/ --include="*.py"
   ```
   Aynı şekilde: dosya, satır, konteks

3. **İş tanımı:** Her tablo için — ne amaçla sorgulanıyor? Ne veri içermeli?
   - Örnek: "entity_matches: firma A ile kaynak B'nin eşleşip eşleşmediğini kaydeder (match_id, company_id, source_id, confidence_score vb.)"

4. **Rapor yazma:** Sonuç `plans/rapor_yasu_VERI-SEMA-DOGRULA-02.md` dosyasına yaz:
   ```markdown
   # entity_matches
   
   - Sorgulandığı dosyalar: (liste)
   - Kaç yerde: (sayı)
   - Yapılan işlem: INSERT/SELECT/UPDATE
   - Beklenen sütunlar: (liste)
   
   # api_usage_daily
   
   - Sorgulandığı dosyalar: (liste)
   - Kaç yerde: (sayı)
   - Yapılan işlem: (tür)
   - Beklenen sütunlar: (liste)
   ```

5. **Chat bildirimi:** chat_gonder.py ile sonuç gönder

## Kabul kriteri

- [ ] entity_matches için tüm referanslar bulundu (dosya + satır)
- [ ] api_usage_daily için tüm referanslar bulundu
- [ ] Her tablo için beklenen sütun listesi yazıldı
- [ ] Rapor dosyası oluşturuldu (`plans/rapor_yasu_VERI-SEMA-DOGRULA-02.md`)
- [ ] Chat'e bildirim gönderildi

## Kurallar

- **D-260:** Beyan değil, kanıt. grep çıktısı ≠ tahmim. Gerçek satırları kopyala.
- **D-310:** Kod taraması merkezi kaydıdır. Raporun validity'sini sınayan başka dosya yok.

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/chat_gonder.py \
  --ajan yasu \
  --task-id VERI-SEMA-DOGRULA-02 \
  --durum cozuldu \
  --mesaj "Kod taraması tamamlandı. entity_matches: N dosyada N referans. api_usage_daily: N dosyada N referans. Rapor: plans/rapor_yasu_VERI-SEMA-DOGRULA-02.md"
```

## Teslim

- Dosya: `plans/rapor_yasu_VERI-SEMA-DOGRULA-02.md` (grep sonuçları + analiz)
- Chat: Bildirim mesajı
- Bağımlılık: VERI-SEMA-DOGRULA-01 bitikten sonra

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-260, D-310)
- [[Huginn Data Insights/src/company_master/schema/migrations/0021_missing_tables.sql]]
