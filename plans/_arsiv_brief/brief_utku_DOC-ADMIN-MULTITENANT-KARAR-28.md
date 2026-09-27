# DOC-ADMIN-MULTITENANT-KARAR-28 — Multi-Tenant Mimarı Karar Belgesi

**Sahip:** utku (ihsan)  
**Öncelik:** P2  
**Durum:** 🟡 Başlama Öncesi  
**Tarih Oluşturuldu:** 2026-09-24  

---

## 🎯 Amaç

Multi-tenant mimarisi için karar belgesini yaz. İçeriği:
1. Tenant modeli (Row-Level Security vs Schema Separation)
2. Data isolation stratejisi
3. Billing & credit per-tenant
4. Admin & permission model
5. Migration path (single → multi)
6. Security checklist

Çıktı: `docs/MULTITENANT_ARCHITECTURE_DECISION.md` (karar matris + tradeoff analiz)

---

## 📋 Adımlar

1. Tenant modelleri araştır (3 seçenek analizi):
   ```
   A) Row-Level Security (RLS):
      - Pros: Single DB, simple schema
      - Cons: Query complexity, performance overhead
   
   B) Schema Separation:
      - Pros: Complete isolation, per-tenant optimization
      - Cons: Migration complexity, schema sync
   
   C) Dedicated DBs:
      - Pros: Full isolation, scaling
      - Cons: operational cost, management overhead
   ```

2. Karar matrisi yaz:
   - Criteria: isolation, cost, complexity, performance, operational load
   - Her model için skor (1-5)
   - Tavsiye: **B (Schema Sep)** mid-term, sonra C (Dedicated) scale-up

3. İmplementasyon spec yaz:
   - tenant_id field'ı tüm tablolara (nullable=False)
   - Unique constraint: (tenant_id, identifier) combos
   - Admin tenant ('_admin') sistem bilgileri için
   - Buyer tier, credit pool tenant-scoped

4. Migration path:
   ```
   Phase 0 (Current): Single tenant (default tenant_id='0')
   Phase 1 (Q4 2026): Schema separation ready (app.py env)
   Phase 2 (Q1 2027): Multi-tenant UI (tenant create/manage)
   Phase 3 (Q2 2027): Per-tenant billing
   ```

5. Security audit checklist:
   - [ ] tenant_id filter tüm queries'de
   - [ ] API endpoints tenant check yapıyor
   - [ ] Audit log tenant_id kayıt ediyor
   - [ ] Cross-tenant data leak testleri
   - [ ] Admin tenant isolation

6. Belgeye kod örnekleri ekle:
   - Schema migration (add tenant_id)
   - SQLAlchemy query wrapper
   - API endpoint tenant filter

---

## ✅ Kabul Kriteri

- [ ] `MULTITENANT_ARCHITECTURE_DECISION.md` yazıldı
- [ ] 3 model karşılaştırması yapıldı (karar matrisi)
- [ ] Seçilen model gerekçelendirildi
- [ ] Migration path (4 phase) tanımlandı
- [ ] Security checklist 8+ item
- [ ] Kod örn. (migration, query wrapper, API) include
- [ ] Timeline (Q4/Q1/Q2) belirtildi
- [ ] Karar referansı: AGENTS.md D-xxx bağlantısı

---

## 📌 İlgili Nodlar

- [[Huginn Data Insights/AGENTS.md]] — D-xxx (karar matris pattern)
- [[Huginn Data Insights/Huginn Data Insights/README.md]] — Sistem mimarisi
- [[Huginn Data Insights/src/company_master]] — Current single-tenant schema
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Multi-tenant admin control

---

**Ponytail:** Şu an single-tenant. Multi-tenant geçişi 6-9 ay operasyonel efor. Recommendation: Phase 0→1 (schema ready) devam et, Phase 2+ opsiyonel; customer demand ve operational maturity'ye bağlı.

**Uyarı:** Cross-tenant data leak kritik risk. Belgeye 10+ security test case'i eklenecek (prod'da penetration test gerekebilir).

**Karar Referansı:** [[Huginn Data Insights/AGENTS.md#D-209]] — Architecture decision log (yeni D-xxx karar buraya eklenecek).
