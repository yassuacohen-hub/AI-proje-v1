[[Huginn Data Insights/data/orchestrator/PO-01_urun_vizyonu_ve_kararlar.md]]

# Huginn Data Insights — Ürün Vizyonu ve Ürün Sahibi Kararları

**Doküman:** PO-01 (AR-03 benzeri ürün-vizyon raporu)
**Tarih:** 2026-09-14
**Rol:** Ürün Sahibi bakış açısı — vizyon, karar kayıtları, kapsam ve yol haritası.
**Girdi:** `Muninn SUPER ADMIN PANEL PRD V1.txt` (20 bölüm, Faz 1 + Faz 2), pano durumu (174 görev: 134 done, 33 plan, 4 blocked, 0 review), AR-01/AR-02/AR-03 analizleri.
**Not:** `Product Owner kararları.txt` boş (0 bayt) bulundu; bu rapor, PRD + pano + AR serisini tek ürün-karar belgesinde birleştirir ve dosyanın yerini tutar.

## 1. Ürün Vizyonu

**Huginn Data Insights**, Ankara OSB firmalarına satış zekâsı sunan B2B SaaS platformudur.
**Muninn Super Admin Panel** ise bu SaaS işletmesinin operasyon merkezidir: müşteri, gelir,
veri kalitesi, AI maliyeti, güvenlik ve sistem sağlığı tek panelden yönetilir.

**Vizyon cümlesi:** *"Veriden gelire — tüm operasyon tek panelde."*

**Ürün ilkeleri:**
1. Operasyon merkezi önceliği: CRUD değil; müşteri operasyonu, platform sağlığı, gelir takibi.
2. Ölçülebilir her karar: KPI, eşik, sorumlu ve tarih olmadan karar kayıtlara geçmez.
3. Veri kalitesi ürün kapısıdır: eksik/yanlış veri panele skor ve aksiyonla girer.
4. AI maliyeti görünür olmadan AI özelliği açılmaz (token, maliyet, model kullanımı).
5. Güvenlik ve audit varsayılandır: her işlem kayıtlı, her rol en-az-yetkili.

## 2. Karar Kayıtları (Decision Log)

| ID | Karar | Gerekçe | Durum |
|---|---|---|---|
| PO-D01 | Super Admin Panel = SaaS operasyon merkezi (tek panel) | PRD §1: müşteri+gelir+veri+AI+güvenlik tek çatı | Onaylı |
| PO-D02 | Geliştirme önceliği P0→P3 sırası korunur | PRD "GELİŞTİRME ÖNCELİĞİ" P0 maddesi | Onaylı |
| PO-D03 | Ödeme entegrasyonu (Stripe) şimdilik kapsam dışı | Operasyonel karar 2026-09-14 | Onaylı |
| PO-D04 | Web-kazıma işleri (WK-01/02/03) yarına ertelendi, blocked tutulur | Operasyonel karar 2026-09-14 | Onaylı — 2026-09-15 |
| PO-D05 | Copilot + cursor_grok kadrodan çıkarıldı | Operasyonel karar 2026-09-14 | Onaylı |
| PO-D06 | Paket fiyat kataloğu tek kaynaktan yönetilir (Temel 499 / Standart 2.999 / Profesyonel 7.999 / Kurumsal 19.999 TL) | AR-03 §1: demo katalogda Temel 999 TL + "Değer" 499 TL çakışması | Açık — PO-BACK-04 |
| PO-D07 | Segment eligibility skoru ürün kapısı olur (5 segmentin 3'ünde uyumsuzluk) | AR-03 §7-F1 | Açık — PO-BACK-02 |
| PO-D08 | Kampanya durum makinesi otomatik denetlenir (bitişi geçen aktif, sıfır teslimatlı taslak) | AR-03 §1: CMP-004 bitişi geçmiş hâlâ aktif; CMP-003 taslak | Açık — PO-BACK-03 |
| PO-D09 | Cache güven unsuru olur: tazelik etiketi + manuel yenileme karar ekranlarında | AR-03 §5/§7-F7 (TTL 30–300 sn) | Açık — PO-BACK-05 |
| PO-D10 | Pano `id=None` tutarsızlığı ayrı görev olarak izlenir (FIX-ID-01) | Operasyonel karar 2026-09-14 | İzleniyor (kilo) |

## 3. Kapsam Haritası — PRD → Mevcut Durum

| PRD Bölümü | Öncelik | Durum | Kanıt |
|---|---|---|---|
| Dashboard (KPI, büyüme, gelir, kullanım, veri kalitesi) | P0 | Kısmen canlı | `/api/kpi`, `/api/dashboard`, tabs/admin_kpi.py; UX-01/02/03 done |
| Tenant Yönetimi (liste, detay, aktif/pasif) | P0 | Kısmen canlı | admin_musteriler.py, admin_yonetim.py |
| Kullanıcı Yönetimi (roller, davet, şifre sıfırlama) | P0 | Kısmen canlı | P7-46 done; roller PRD §16'da tanımlı |
| Kullanım Analitiği (arama/AI/API/export) | P0 | Kısmen canlı | admin_api_analytics.py, admin_cost.py |
| AI Operasyonları (prompt, token, maliyet, model) | P1 | Kısmen canlı | admin_cost.py; CL-01 suite |
| Veri Operasyonları (kaynak, kalite, crawl, güncellik) | P1 | Kısmen canlı | admin_quality.py; WK blocked (yarın) |
| Güvenlik + Audit Log | P1 | Temel canlı | SEC-01/SEC-02, CL-03 taraması; MFA henüz yok |
| Faturalama + Abonelik | P2 | Kapsam dışı (şimdilik) | PO-D03: ödeme kapalı |
| API Yönetimi (anahtar, limit, webhook) | P2 | Kısmen canlı | API-key modu, webhook_monitor.py |
| Destek Merkezi (ticket) | P2 | Yok | PO-BACK-06'ya bağlandı |
| Feature Flags (tenant bazlı) | P2 | Yok | PO-BACK-07'ye bağlandı |
| Faz 2 (churn/upsell, cost optimizer, health score, executive dashboard, cohort, forecast, anomali) | P3 | Yok | PO-BACK-08'e bağlandı (sıralı) |
## 4. Ürün Backlog'u (Yeni Görevler — Panoya Eklendi)

| Görev | Başlık | Öncelik | PRD/AR Bağı | Kabul Kriteri |
|---|---|---|---|---|
| PO-BACK-01 | Tenant Health Score v1 | P1 | PRD Faz 2 | Skor formülü + eşik dokümanı + dashboard kartı; 3 tenant'ta doğrulanır |
| PO-BACK-02 | Segment eligibility skoru + onay akışı | P1 | AR-03 F1, PO-D07 | 5 segmentte %95+ uygunluk; eksik-alan açıklaması UI'da |
| PO-BACK-03 | Kampanya durum-makinesi otomatik denetimi | P1 | AR-03 §1, PO-D08 | Bitişi geçen aktif → uyarı; sıfır teslimatlı taslak → pilot önerisi; testli |
| PO-BACK-04 | Paket fiyat kataloğu tekilleştirme | P1 | AR-03 §1, PO-D06 | Tek fiyat kaynağı; 4 tier (Temel 499 TL); demo çakışması giderilir |
| PO-BACK-05 | Karar ekranlarında veri-tazelik etiketi + manuel yenileme | P2 | AR-03 F7, PO-D09 | "Son güncelleme" + yenile butonu; invalidation görünür |
| PO-BACK-06 | Destek Merkezi MVP (open/pending/closed + ata/kapat/eskale) | P2 | PRD §15 | Ticket CRUD + durum makinesi + test; admin sekmeye eklenir |
| PO-BACK-07 | Feature Flags MVP (AI Assistant, Excel/PDF Export, API Access) | P2 | PRD §19 | Flag CRUD + tenant eşleme + guard; testli |
| PO-BACK-08 | Executive Dashboard v1 (MRR/ARR/churn + health özeti) | P3 | PRD Faz 2 | MRR/ARR trend + churn + health dağılımı; kaynak dokümante |

**Dağıtım notu:** ajan-başı max 3 iş kuralı gereği görevler `plan` durumunda sahipsiz
bırakıldı; `gorev_at.py at --task-id <ID> --ajan <AJAN>` ile dağıtılır.
Öneri: PO-BACK-04 → kilo, PO-BACK-03/05 → roo, PO-BACK-06/07 → gelistirici,
PO-BACK-01/08 → mimar, PO-BACK-02 → kilo.

## 5. 90 Günlük Hedefler (AR-03 §7-F8 ile hizalı)

- Segment uygunluğu doğrulama %95+ (PO-BACK-02)
- İlk 7 gün aktivasyon %70+, 30 gün elde tutma %80+
- Aktif kampanya dönüşüm oranı %3,5+
- Kurumsal/Profesyonel genişleme MRR'si pozitif
- Kritik güvenlik bulgusu 0 (CL-03 taraması yeşil tutulur)
- Pano disiplini: review kuyruğu 0, blocked ≤ 2

## 6. Riskler ve Açık Sorular

1. **Fiyat kataloğu çakışması** (Temel 999 vs 499 TL) — PO-BACK-04 kapanmadan fatura kararı verilmez.
2. **Segment uyumsuzluğu** (3/5 segment) — PO-BACK-02 öncesi ticari rapor güven vermez.
3. **Kampanya durum güveni** (CMP-004/003/005) — PO-BACK-03 öncesi pazarlama metrikleri şüpheli.
4. **Ödeme kapsam dışı** — MRR takibi manuel kalır; abonelik PRD maddeleri Faz 2 sonrasına sarkar.
5. **WK blocked** — veri tazeliği yarınki web-kazıma turuna bağlı.

## 7. Kaynaklar ve İzlenebilirlik

- `Product Owner kararları.txt` — boş bulundu; bu dosya (PO-01) onun yerine geçer.
- `Muninn SUPER ADMIN PANEL PRD V1.txt` — 20 bölüm + Faz 2 + P0–P3 öncelikler.
- `data/orchestrator/AR-03_kullanici_persona_yol_haritasi.md` — persona, metrik, 8 büyüme fırsatı.
- `data/orchestrator/AR-01_pazar_egilim_analizi_Q3_2026.md`, `AR-02_rekabet_analizi.md`.
- `data/orchestrator/task_board.json` — 174 görev (134 done / 33 plan / 4 blocked / 0 review).
- `web_dashboard/tabs/` — admin_kpi, admin_musteriler, admin_quality, admin_cost, webhook_monitor.
