# UTKU-01 — Veri Şeması Doğrulama (Core Modülü)

**Ajan:** Utku  
**Aciliyet:** P0 (Production blokaj riski)  
**Süre:** 2 saat  
**Tür:** Veri / Altyapı  
**Kilitli dosya:** `src/company_master/schema/`  
**Bağımlılık:** Yok  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
Production'a çıkış öncesi veri şemasının tutarlılığı, eksik index/constraint'lerin tamamlanması ve migration geçmişinin temizlenmesi zorunlu. Şu an `src/company_master/schema/` altında tablolar, migration'lar ve `company_master/core/` modülleri birbirinden bağımsız doğrulanmamış durumda.

## Doğrulanacak varsayım
- Tüm tablolar `src/company_master/schema/migrations/` altında sıralı migration dosyalarıyla oluşturulmuş
- `company_master/core/models.py` (varsa) veya SQLAlchemy modelleri şemayla birebir uyumlu
- Eksik FK, UNIQUE, CHECK constraint'ler yok
- Migration geçmişinde `down` dosyaları her `up` için mevcut
- `alembic_version` tablosu güncel

## Adımlar
1. `src/company_master/schema/` yapısını tarayıp `migrations/` altındaki `.sql` dosyalarını topla
2. Her `up` migration için karşılık gelen `down` dosyası var mı kontrol et
3. `company_master/core/` modüllerindeki (models, schema) tablo tanımlarıyla migration SQL'ini karşılaştır
4. Eksik FK, UNIQUE, CHECK, INDEX constraint'leri tespit et
4. Eksik `down` migration'ları yaz
5. `alembic` geçmişi ile `src/company_master/schema/migrations/` senkronize mi kontrol et
6. Test dosyası yaz: `tests/test_schema_validation.py` (en az 8 test)

## Kabul kriteri
- [ ] Tüm `up` migration'lar için `down` dosyası var
- [ ] `company_master/core/` modelleri ile migration SQL birebir uyumlu
- [ ] Eksik FK/UNIQUE/CHECK/INDEX tespit edilip eklendi
- [ ] `alembic_version` tablosu güncel
- [ ] `tests/test_schema_validation.py` en az 8 test geçiyor
- [ ] `python scripts/kodlama_denetim.py` temiz

## Kurallar
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id UTKU-01 --ozet "<özet>"`

## Ilgili Nodlar
- [[src/company_master/schema/]]
- [[src/company_master/core/]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/scripts/kodlama_denetim.py]]