# UI-ADMIN-LTV-CAC-27 — LTV/CAC Analiz Panosu

**Sahip:** utku (ihsan)  
**Öncelik:** P2  
**Durum:** 🟡 Başlama Öncesi  
**Tarih Oluşturuldu:** 2026-09-24  

---

## 🎯 Amaç

Admin paneline müşteri yaşam döngüsü metriklerini gösterecek analiz sekmesi ekle:
- **LTV (Lifetime Value):** Ortalama müşteri değeri
- **CAC (Customer Acquisition Cost):** Kazanım maliyeti
- **LTV/CAC Ratio:** Profitabilite göstergesi (≥3 ideal)
- Zaman serisi grafik (30/90/180 gün trend)
- Tier breakdown (Terminal/Strategic/Enterprise)

---

## 📋 Adımlar

1. Veritabanı query yaz (`web_app.py`'ye ekle):
   ```python
   def _calculate_ltv(days=30) -> dict:
       # users table: joined_at, credit_balance, tier
       # credit_ledger: user_id, amount, reason, created_at
       # LTV = avg(total_revenue_per_user) over last N days
   
   def _calculate_cac(days=30) -> dict:
       # admin_approvals: user_id, created_at
       # CAC = marketing_spend / new_users (env: MARKETING_SPEND_MONTHLY)
   
   def _ltv_cac_trend(days=180) -> list[dict]:
       # Her gün için [date, LTV, CAC, ratio]
   ```

2. Endpoint yaz: `GET /api/admin/ltv-cac`
   - Query params: `days=30|90|180`
   - Response:
   ```json
   {
     "ltv": 12500.50,
     "cac": 850.00,
     "ratio": 14.7,
     "trend": [
       {"date": "2026-09-24", "ltv": 12400, "cac": 860, "ratio": 14.4},
       ...
     ],
     "by_tier": {
       "terminal": {"ltv": 500, "cac": 200, "ratio": 2.5},
       "strategic": {"ltv": 5000, "cac": 800, "ratio": 6.25},
       "enterprise": {"ltv": 50000, "cac": 1500, "ratio": 33.3}
     }
   }
   ```

3. UI ekle (`web_dashboard/tabs/admin_panel.py`):
   - "💰 LTV/CAC Analiz" sekmesi
   - KPI kartları: LTV, CAC, Ratio (renkli göstergeler)
   - 3 tab: 30 gün | 90 gün | 180 gün
   - Line chart: LTV vs CAC trend
   - Stacked bar chart: Tier breakdown
   - Açıklama: "Ratio ≥3 sağlıklı, <1 zarar"

4. Cache ekle (ttl=3600, günlük reset)

5. Test: `tests/test_admin_ltv_cac.py`
   - LTV calculation accuracy
   - CAC with marketing_spend env
   - Trend data ordering
   - Tier breakdown sum validation

---

## ✅ Kabul Kriteri

- [ ] `/api/admin/ltv-cac` endpoint çalışıyor
- [ ] Sorgu `days` parametresini kabul ediyor (30/90/180)
- [ ] LTV, CAC, ratio doğru hesaplanıyor
- [ ] Trend verisi 30+ gün için döndürüyor
- [ ] Tier breakdown tutarlı (sum = total)
- [ ] UI 3 tab gösteriyor
- [ ] Line chart LTV vs CAC trend çiziyor
- [ ] Stacked bar tier breakdown gösteriyor
- [ ] Cache ttl=3600
- [ ] Testler geçiyor: 8/8 test passed

---

## 📌 İlgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Admin analytics hub
- [[Huginn Data Insights/web_app.py#557-584]] — KPI endpoint pattern
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py]] — Analytics tab
- [[Huginn Data Insights/AI proje v1/V10/02_is_akisi_ve_moduller/08_analitik_sistem.md]] — Analitik yapısı

---

**Ponytail:** MARKETING_SPEND_MONTHLY env varsayılan 50000 TRY. CAC formülü basitleştirildi (aylık ortam malı ÷ yeni user). Prod'da kanal-bazlı CAC (Google Ads, LinkedIn vb.) eklenebilir.

**Uyarı:** LTV hesabı credit_ledger üzerinden revenue approx. yapıyor. Gerçek revenue tablo (transactions) gerekirse güncelle.

**Karar Referansı:** [[Huginn Data Insights/AGENTS.md#D-204]] — Analytics KPI framework.
