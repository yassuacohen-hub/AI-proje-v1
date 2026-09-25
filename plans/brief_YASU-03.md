# GÖREV BRIËFI: YASU-03 — Grafiksel Dashboard - Veri Görselleştirme

**Atanan:** yasu  
**Öncelik:** P1  
**Deadline:** 2026-10-02T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
Dashboard sayfasını etkileşimli grafikler ve veri panelleriyle geliştir. Chart.js veya D3.js kullanarak KPI'lar, trend grafikleri, heatmap'ler göster.

## Kabul Kriterleri
1. Minimum 5 grafik türü yazılmalı (frontend/components/dashboard.tsx)
2. Real-time data update yapılmalı
3. Export to PDF/CSV fonksiyonu

## Kaynaklar (SSOT)
- frontend/components/dashboard.tsx
- Data API endpoints

## İmplantasyon Notları
- Recharts veya Victory (React native)
- WebSocket for real-time
- Data aggregation layer

## Proof-of-Work
File/Output: frontend/components/dashboard.tsx + chart components + export tests
