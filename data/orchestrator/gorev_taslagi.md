# Görev Taslağı — Kalıcı Üretim Defteri

> **Bu dosya silinmez, yalnızca güncellenir.** Her görev üretim turu buraya yazılır.
> Kaynak SSOT: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (ADMIN-KİT, D-196)
> Pano: `data/orchestrator/task_board.json` · Brief dizini: `plans/brief_utku_*.md`

---

## 0. İlerleme Bloğu

**Hesaplama yöntemi (her tur aynı formül):**
`yüzde = kapalı_madde / toplam_madde`; toplam_madde = SSOT'ta sayılabilir madde kalemlerinin toplamı = §8.1 (A1-A10 = 10) + §8.3 (C1-C8 = 8) + §8.4 (EK BULGU-8/9/10 = 3) + §9 (K1-K10 = 10) + §10 (sıra 1-15 = 15) + §11 (KK-1…KK-9 = 9) + §12 (G0-G9 = 10) = **65**. Bir madde yalnızca ✅/karara bağlanmış/kapandı ise kapalı sayılır; 🟡 kısmi ve 🔴 açık = **açık**. Tahmin yok, satır sayımı var.

| Ölçüm | Değer |
| --- | --- |
| Toplam SSOT maddesi | 65 |
| Kapalı | 32 |
| Açık | 33 |
| **İlerleme** | **%49** |
| Karşılaştırma | — → **%49** (ilk ölçüm, taban çizgisi) |

**Kapalı madde dağılımı (sayım kanıtı):** §8.1 → 1 (A2) · §8.3 → 6 (C1,C2,C3,C4,C6,C8) · §8.4 → 2 (EK BULGU-9,10) · §9 → 4 (K2,K3,K5,K6) · §10 → 6 (sıra 1,2,4,7,8,9) · §11 → 7 (KK-1,2,3,4,6,8,9) · §12 → 6 (G0,G1,G3,G5,G6,G7).

**Görev panosu durumu:** toplam üretilen admin görevi 22 · tamamlanan 12 (`-01`…`-12`) · devam eden 0 · bekleyen 10 (`-13`…`-22`) → **pano tamamlanma %55**.

---

## 1. Ana Görevler (Tur 2 denetiminden geçti, bağımlılık sırası ile)

| # | task_id | Başlık | Sahip | Öncelik | Durum | Kaynak (SSOT satır) | Bağımlılık | Seçim gerekçesi | Üretim |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `VERI-ADMIN-AKTIVITE-LOG-13` | [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s) | utku | P0 | bekliyor | §8.4:322 · §10:366 · §12:415 | — | Tek eksik 3 maddeyi (K1 tam churn, K9, G4 DAU) aynı anda açıyor; en yüksek blokaj kaldırma | 2026-09-24 |
| 2 | `API-ADMIN-AKTIVITE-YAZ-14` | [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s) | utku | P0 | bekliyor | §8.4:322 · §9:340 | `-13` | Boş tablo değer üretmez; veri akışı olmadan sonraki 4 görev ölü doğar | 2026-09-24 |
| 3 | `DOC-ADMIN-DURUM-SENKRON-15` | [DOC] Bayat durum satırlarını senkronla → §8.4/§10 kanıtlı (1s) | utku | P1 | bekliyor | §8.4:322-324 · §10:364-366 | — | §10 satır 1 hâlâ P0 gösteriyor ama EK BULGU-9/10 kapandı; ölçüm kendini yanıltıyor, S efor | 2026-09-24 |
| 4 | `API-ADMIN-CHURN-3SINYAL-16` | [API] Churn kuralını 3 sinyale genişlet → churn.py tam formül (2s) | utku | P1 | bekliyor | §9:340 · §10:368 · §12:415 | `-14` | K1 PRD'de P0; şu an tek sinyalle çalışıyor, formülün 2/3'ü eksik | 2026-09-24 |
| 5 | `UI-ADMIN-DAU-17` | [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s) | utku | P1 | bekliyor | §8.1:273 · §10:369 · §12:417 | `-14` | G4 blokajı `-13/-14` ile kalkıyor; MAU var, DAU yok — yarım metrik yanıltıcı | 2026-09-24 |
| 6 | `API-ADMIN-KAYNAK-SAGLIK-18` | [API] Kaynak sağlık skorunu tamamla → kaynak_guvenilirlik.py formül (2s) | utku | P1 | bekliyor | §9:343 | — | K4 girdisi (`source_records`) DB'de MEVCUT; bloklu değil, hemen kapanabilir | 2026-09-24 |
| 7 | `UI-ADMIN-CRAWL-KONTROL-19` | [UI] Crawl tetikle/durdur aksiyonunu yaz → webhook_monitor.py (3s) | utku | P1 | bekliyor | §8.1:272 · §10:373 · §12:421 | — | A8/G8 tek açık P1 operasyon aracı; yönetici müdahale yeteneği yok | 2026-09-24 |
| 8 | `UI-ADMIN-ARAMA-BOSLUK-20` | [UI] Arama boşluğu panelini yaz → K9 frekans analizi (2s) | utku | P2 | bekliyor | §9:348 · §10:375 | `-14` | K9 çıktısı doğrudan veri toplama backlog'u üretir — ürün değeri yüksek | 2026-09-24 |
| 9 | `API-ADMIN-SUPHELI-AKTIVITE-21` | [API] Şüpheli aktivite eşik kurallarını yaz → admin_audit.py (3s) | utku | P2 | bekliyor | §9:349 · §10:374 · §12:422 | `-14` | K10/G9 güvenlik alarmı yok; A6'nın kural-tabanlı, ML'siz parçası | 2026-09-24 |
| 10 | `UI-ADMIN-UPSELL-22` | [UI] Upsell aday listesini yaz → K7 doygunluk kuralı (2s) | utku | P2 | bekliyor | §9:346 | `-16` | K7 girdisi `credit_ledger` DB'de MEVCUT; churn etiketi `-16` ile tamamlanınca gelir etkisi doğrudan | 2026-09-24 |

## 2. Yedek Görevler (denetimde elendi, sıradaki tur adayı)

| # | task_id | Başlık | Sahip | Öncelik | Durum | Kaynak (SSOT satır) | Eleme nedeni |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Y1 | `TEST-ADMIN-K2-AGIRLIK-23` | [TEST] K2 ağırlık şemasını doğrula → test + SSOT kanıt (1s) | utku | P2 | yedek | §9:341 | Etki düşük; K2 zaten ✅ çalışıyor, yalnız doğrulama borcu |
| Y2 | `DOC-ADMIN-V9-KUTUCUK-24` | [DOC] V9 §16.5 kutucuklarını güncelle → 6 madde ✅ (1s) | utku | P2 | onay-bloklu | §8.3 C7:309 · §11 KK-5:394 | **KK-5 🔴 Ürün Sahibi onayı bekliyor** — onaysız yazılamaz |
| Y3 | `UI-ADMIN-FEATURE-FLAG-25` | [UI] Feature flag yönetim ekranını yaz → A5 MVP (3s) | utku | P2 | yedek | §8.1:269 · §10:376 | §10'da etki "Düşük", etki/efor "Düşük" — merdivenin en altı |
| Y4 | `API-ADMIN-MFA-26` | [API] MFA + hesap kilidi akışını yaz → A6 auth (4s) | utku | P2 | yedek | §8.1:270 · §10:374 | L efor; ayrıca `-21` A6'nın yüksek değerli parçasını zaten kapsıyor |
| Y5 | `UI-ADMIN-LTV-CAC-27` | [UI] LTV/CAC kartlarını yaz → K8 tamamlama (2s) | utku | P3 | bloklu | §9:347 · §10:379 · §13:435 | Faturalama ertelendi (P3), Stripe yok — girdi kaynağı mevcut değil |
| Y6 | `DOC-ADMIN-MULTITENANT-KARAR-28` | [DOC] Multi-tenant kararını kapat → KK-7 (1s) | utku | P3 | karar-bloklu | §11 KK-7:396 · §13:434 | Teknik görev değil, ürün kararı; KAHİN yanıtı olmadan içerik üretilemez |

---

## 3. Tur Kaydı

### Tur 2026-09-24 / #1

- **Tur 1 (üretim):** SSOT §8/§9/§10/§11/§12 tarandı, 33 açık maddeden **16 aday görev** çıkarıldı.
- **Tur 2 (denetim):** 6 aday elendi/yedeğe alındı —
  - `DOC-ADMIN-V9-KUTUCUK` → KK-5 onay bloklu (kural: onaysız iş yazılmaz).
  - `API-ADMIN-MFA` → `API-ADMIN-SUPHELI-AKTIVITE-21` ile kapsam örtüşmesi + L efor.
  - `UI-ADMIN-FEATURE-FLAG` → SSOT §10'da etki/efor "Düşük".
  - `UI-ADMIN-LTV-CAC`, `DOC-ADMIN-MULTITENANT-KARAR` → P3, girdi/karar bloklu.
  - `TEST-ADMIN-K2-AGIRLIK` → ana listeyi 10'a indirmek için en düşük etkili kalem olarak yedeğe.
  - **Birleştirme kararı:** `-13` (migration) ile `-14` (yazma) **ayrı tutuldu** — `-04`/`-05` çiftindeki kanıtlanmış desen; tek görevde birleştirmek 4 saat kuralını (D-57) zorlar.
  - **Sıra düzeltmesi:** `DOC-ADMIN-DURUM-SENKRON-15` denetimde 10. sıradan 3. sıraya yükseltildi — bayat durum satırları ilerleme ölçümünü bozuyor, S efor.
- **Sonuç:** 10 ana + 6 yedek.
- **İlerleme:** — → **%49** (taban çizgisi).

---

## 4. Üretilen Brief'ler (D-186 — yeni belge = yeni bağlantı)

- [[Huginn Data Insights/plans/brief_utku_VERI-ADMIN-AKTIVITE-LOG-13]]
- [[Huginn Data Insights/plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14]]
- [[Huginn Data Insights/plans/brief_utku_DOC-ADMIN-DURUM-SENKRON-15]]
- [[Huginn Data Insights/plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-DAU-17]]
- [[Huginn Data Insights/plans/brief_utku_API-ADMIN-KAYNAK-SAGLIK-18]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-KONTROL-19]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20]]
- [[Huginn Data Insights/plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21]]
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-UPSELL-22]]

## 5. Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/AGENTS]]
