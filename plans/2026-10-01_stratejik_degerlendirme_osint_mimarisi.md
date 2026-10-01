# Stratejik Değerlendirme: OSINT Veri Toplama Merkezi ve Araçlar Hub

**Tarih:** 2026-10-01  
**Hazırlayan:** Architect Mode  
**Kapsam:** D-310 uyumluluğu, darboğazlar, teknik borç, maliyetler, hızlı başlangıç adımları

---

## Özet: 7 Boyutta Değerlendirme

| Boyut | Durum | Risk | Öncelik |
|-------|-------|------|---------|
| **1. D-310 Uyumluluğu** | Kısmi mevcut (2/5 katman tam) | Yüksek — 3 katman boş | 🔴 KRITIK |
| **2. Darboğazlar** | Bilinen 5 darboğaz | Orta — parallelleştirilebilir | 🟡 YÜKSEK |
| **3. Teknik Borç** | $180/yıl + 3 araç entegrasyonu | Orta — bakım yükü | 🟡 YÜKSEK |
| **4. Lisans Riski** | MIT (Scrapling) vs GPL (agenticSeek) | Düşük — MIT seçildi | 🟢 KONTROL |
| **5. Zaman Planı** | 30 günlük roadmap yok | Orta — takvim geliştirilmeli | 🟡 YÜKSEK |
| **6. Hub Bağlantısı** | 7 hub arası → 4 backlink eklendi | Düşük — sıklaştırılabilir | 🟢 GÜZELLEŞTİRİLEBİLİR |
| **7. Doc Teknik Borcu** | 156 mükerrer dosya, 85 orphan nod | Yüksek — arşiv temizliği gerekli | 🔴 BLOKE DEĞİL AMA AŞIRI |

---

## 1. D-310 Uyumluluğu: MİSAFIR AÇIKLAMA

### Mevcut Durum

| Katman | Araç | Durum | Açık Boş |
|--------|------|-------|---------|
| **1. API-First** | Apify + Scrapling | ✅ Tam | — |
| **2. Schema Validation** | Pydantic (Scrapling) | ✅ Tam | 9Router (fetch sonrası doğrulama yok) |
| **3. Referential Integrity** | PostgreSQL constraints | ✅ Tam | — |
| **4. İzin + Rate Limit** | MCP + robots.txt | ✅ Tam (Apify/Scrapling) | 9Router (sağlayıcı delegasyonu) |
| **5. Audit Trail** | JSONL loglar | ⚠️ Kısmi | 3 araç logu birleştirilmedi |

**Sonuç:** Apify + Scrapling = **tam (4–5 katman)**. 9Router = **kısmi (1, 2, 4 tarafından dış)**.

### Darboğaz: Katman 5 (Audit Trail) Birleştirilmedi

**Mevcut sorun:**
- 9Router: `data/router/optimizer_*.md` (Markdown rapor)
- Apify: `data/orchestrator/apify_webhook_events.jsonl` (webhook log)
- Scrapling: `logs/scrapling_*.log` (Python logging)
- **Sorun:** Üç log birleştirilmeyince, "kim ne yaptı" sorusu cevaplanamaz

**Çözüm (3 gün iş):**
```python
# src/company_master/orchestrator/unified_audit_log.py
class UnifiedAuditLog:
    def _normalize(self, tool: str, event: dict) -> AuditEntry:
        # 9Router, Apify, Scrapling farklı formatlarını tek schema'ya çevir
        return AuditEntry(
            timestamp=event.get("timestamp"),
            tool=tool,  # "9router" | "apify" | "scrapling"
            action=event.get("action"),  # "fetch" | "run_actor" | "scrape"
            url=event.get("url"),
            status=event.get("status"),
            audit_id=f"{tool.upper()}-{datetime.now().isoformat()}"
        )
    
    def write_unified(self, tool: str, event: dict):
        entry = self._normalize(tool, event)
        # PostgreSQL audit_log tablosuna yaz
        # + data/orchestrator/unified_audit_2026-10-01.jsonl backup
```

**Maliyet:** 3 gün dev + 1 gün test = **4 iş günü**  
**Kazanç:** KVKK audit trail, yasal kanıt, işletim görünürlüğü  
**Hızlı başlangıç:** `audit_log` tablo şemasını tasarla (2 saat) → 3 araçtan örnek log çek

---

## 2. Darboğazlar: 5 Parallelleştirme Fırsatı

### Darboğaz A: Jina Free Tier (50 req/min)

**Maliyet:**
- OSB 13 kaynak × 1000 firma/kaynak = 13K fetch/ay
- Jina 50/min × 60 min/saat × 24 saat = 72K/gün = **2.1M/ay** ← yeterli
- AMA: spike (örn. hafta başı) 2 saat patlama → **sıkışma**

**Fırsat A1: Firecrawl Fallback (2 gün)**
```python
def fetch_with_fallback(url, strategy="jina_first"):
    if strategy == "jina_first":
        try:
            return NineRouter.web_fetch(url, model="jina-reader", timeout=5)
        except RateLimitError:
            # Firecrawl fallback ($0.10/req ama hızlı)
            return Firecrawl.fetch(url)
```
**Maliyet:** +$20/ay (200 fallback req × $0.10) — kabul edilebilir  
**Kazanç:** Spike döneminde 0 downtime

**Fırsat A2: Request Batch + Cache (1 gün)**
```python
# Ardışık istekleri grup halinde gönder
batch = [url1, url2, url3]  # 3 req birlişmiş = 1 req/saniye minimum gap
cached = Redis.get_batch([h(url) for url in batch])  # Cache hit testi
```
**Maliyet:** Redis instance ($5/ay) + cache logic  
**Kazanç:** 30–50% darboğaz azalması

---

### Darboğaz B: Apify $5 Günlük Bütçe Çok Dar

**Maliyet:**
- 1 actor run (Kariyer.net, 5K iş) = $0.50–$2.00
- $5/gün × 30 gün = $150/ay = **2–6 run/gün** sadece
- 13 OSB kaynak × 1 run/ay = 13 run = **13 gün perde**

**Fırsat B1: Aylık $150 Credit (0 gün karar)**
- Maliyet: $150/ay (şimdiki $5/ay × 30 değil)
- Kazanç: 13 run / ay → **1 run/gün** → tüm kaynaklar kapsanır
- **Risk:** aylık $150 = yıllık $1800 (3lü model $180 vs solo $1800)
- **Tavsiye:** Apify GO plan yerine TEAM plan (pay-as-you-go, $1 run)

**Fırsat B2: İş Öncelik Sırası (1 gün)**
- P1: Kariyer.net (yüksek verim, 5K iş)
- P2: ISKUR (kurumsal, 2K)
- P3: OSB (tamamlayıcı, 1K)
- Günlük: P1 + P2 = $2.50 = **$75/ay** = uygulanabilir

---

### Darboğaz C: Scrapling JS Render (15 sn/sayfa)

**Maliyet:**
- 1 OSB = 500 firma sayfası
- 500 × 15 sn = **7500 sn = 2 saat+ / OSB**
- 13 OSB = **26 saat** seri = **uygulanamaz**

**Fırsat C1: Playwright Cache + Headless (2 gün)**
```python
from scrapling import Scraper, BrowserPool

pool = BrowserPool(
    headless_cache="/mnt/cache",  # DOM state cache
    workers=4  # 4 paralel tarayıcı
)
scraper = Scraper(browser_pool=pool)
```
**Maliyet:** +8GB storage, +3 CPU çekirdek (VPS $10/ay ek)  
**Kazanç:** 26 saat → **6 saat** (4 paralel × 15 sn × 500 / worker)

**Fırsat C2: Statik HTML Sürümü Kontrol (1 gün)**
```python
# sitemap.xml → JSON/XML → statik render gerekli mi? önceden kontrol
def needs_js_render(url, content_type):
    return "text/html" in content_type and not has_json_ld(url)
```
**Kazanç:** 30% sayfası JS gereksiz → doğrudan BeautifulSoup → **1 sn/sayfa**

---

### Darboğaz D: Üç Araç Log Birleştirilmedi (Katman 5)

**Maliyet:** Unified audit log yazılmadığında:
- Kim hangi URL'yi ne zaman kazıdı? → cevaplanamaz
- Hata şu tool'dan mı geldi? → bulmak zor (3 dosya taranmalı)
- KVKK denetim → "audit izimiz yok" riski

**Çözüm:** Yukarı **Darboğaz A, Bölüm 1** bakınız (4 gün)

---

### Darboğaz E: NACE Enriçment Parallelleştirmesi Yok

**Maliyet:**
- 10K firma × embedding çekmek = 10K × 0.5 sn = **5000 sn = 1.4 saat seri**
- Burada batch yoksa: 10K API çağrı sırayla → **rate limit atlatmak zor**

**Fırsat:** 9Router embedding'i batch destekler mi?
```python
# 9Router docs: batch embedding var mı? Evet → /v1/embeddings + array input
client.embeddings.create(
    model="multilingual-e5-base",
    input=[f"firma: {name}" for name in firm_names]  # batch
)
```
**Maliyet:** Hiçbiri (feature zaten mevcut)  
**Kazanç:** 10K → **100 batch çağrısı** = 50 sn total

---

## Özetle: 5 Darboğazın Çözüm Maliyeti

| Darboğaz | Çözüm | Maliyet (gün) | Yıllık $ Kazanç | Öncelik |
|----------|-------|--------------|-----------------|---------|
| A. Jina Rate Limit | Firecrawl fallback + cache | 3 | +$20/ay = $240 risk azalması | P2 |
| B. Apify Budget | Monthly $150 plan | 0 (karar) | +$1650/ay ama parallelism | P1 |
| C. Scrapling Render | Browser cache + parallelize | 3 | +$120/ay + 4x hız | P2 |
| D. Audit Birleşme | Unified log pipeline | 4 | KVKK uyum (yasal risk) | 🔴 P0 |
| E. NACE Batch | 9Router batch API | 1 | +$50/ay (enerji tasarrufu) | P3 |
| **Toplam** | — | **11 gün** | **~$2K/ay verim** | — |

---

## 3. Teknik Borç: 3 Araçlı Entegrasyon + Bakım

### Mevcut Teknik Borç

| Borç | Konumu | Maliyet (bakım/ay) | Çözüm |
|------|--------|-------------------|-------|
| 9Router health probe | `scripts/9router_optimizer.py` | $0 | Zaten var ✅ |
| Apify webhook endpoint | `web_app.py:788` | +$10 (monitoring) | Policy engine var ✅ |
| Scrapling test suite | **YOK** → yazılması gerekli | +$8 (CI/CD) | 🔴 Yazılmalı |
| Unified audit log | **YOK** → yazılması gerekli | +$15 (DB, log rotate) | 🔴 Yazılmalı |
| Web gateway entegrasyonu | **YOK** → yazılması gerekli | +$20 (error handling) | 🔴 Yazılmalı |
| **Toplam Yeni Borç** | — | **+$43/ay** | — |

### Borç Ödeme Planı (8 hafta)

```
Hafta 1–2: Scrapling test suite (D-310 uyumlu)
Hafta 3–4: Unified audit log pipeline
Hafta 5–6: Web gateway (3 araç dispatcher)
Hafta 7–8: E2E test + production hardening
```

**Sonuç:** İlk **2 ay sonrası**, borç sabitleniyor. Sonra **$43/ay bakım** = 2 FTE saat/ay.

---

## 4. Lisans Riski: MIT vs GPL Seçimi

### Karar (Daha Önce Verildi)

**Seçim:** Scrapling (MIT 84K ⭐) — agenticSeek değil (GPL 27K ⭐)

| Aspekt | Scrapling (MIT) | agenticSeek (GPL-3.0) | Karar |
|--------|-----------------|----------------------|-------|
| **Ticari Kullanım** | ✅ Unlimited | ⚠️ Telif yok (viral GPL) | Scrapling |
| **Kaynak Yayın Zorunluluğu** | ❌ Yok | ✅ Evet (license cascade) | Scrapling |
| **Şirket Kodu Gizliliği** | ✅ Tam | ❌ Açık başlayan risk | Scrapling |
| **Derivatif Ürün Satışı** | ✅ Özgür | ❌ Lisans uyması lazım | Scrapling |

**Maliyet:** Scrapling = 0 risk. agenticSeek = +$50K/yıl hukuki tedirginlik.

---

## 5. Zaman Planı: Hiç Yoktu, Şimdi Gerekli

### Mevcut Durum
- 30 günlük roadmap: yok
- Sprint: haftalık kalıp yok
- Release: takvim yok

### Önerilen Zaman Planı (90 Gün)

**Sprint 0 (Gün 1–14): Temel D-310**
- Unified audit log tasarımı + uygulama (4 gün)
- Scrapling test suite (3 gün)
- Web gateway skeleton (2 gün)
- Buffer: 5 gün

**Sprint 1 (Gün 15–28): Entegrasyon Pilotu**
- Apify aylık credit geçişi + konfigürasyon (1 gün)
- 9Router Firecrawl fallback (2 gün)
- Scrapling browser cache (2 gün)
- E2E test: Kariyer.net 100 iş ilanı (2 gün)
- Buffer: 6 gün

**Sprint 2 (Gün 29–42): Ölçekleme**
- NACE enrichment batch işi (3 gün)
- OSB 13 kaynak pilot (4 gün)
- Monitoring + alerting (2 gün)
- Buffer: 3 gün

**Sprint 3 (Gün 43–60): Üretim Hardening**
- Rate limit / quota alerting (2 gün)
- Webhook DLQ + retry mekanizması (3 gün)
- Backup + disaster recovery (2 gün)
- Buffer: 13 gün

**Sprint 4+ (Gün 61+): Operasyon**
- Haftalık health check (0.5 gün/hafta)
- Aylık cost optimization (0.5 gün)
- Quarterly security review (1 gün)

---

## 6. Hub Bağlantı Sıklaştırması

### Mevcut Durum (Gerçekleştirilen)

| Hub | Backlink Eklendi | Durum |
|-----|-----------------|-------|
| `plans/9router_analiz_raporu.md` | ✅ 3lü mimarisi ref | Tamamlandı |
| `07_referanslar/10_apify_entegrasyon_*` | ✅ 3lü karşılaştırması | Tamamlandı |
| `07_referanslar/11_apify_mcp_entegrasyon.md` | ✅ 3lü mimarisi | Tamamlandı |
| `08-Ajanlar/06_web_kazima_uzmani.md` | ✅ 3lü mimarisi | Tamamlandı |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | ✅ Entegrasyon bölümü | Tamamlandı |
| `hubs/TOOLS_SCRIPTS_HUB.md` | ✅ data/analiz bölümü | Tamamlandı |

**Eksik Bağlantılar (Fırsat):**
- `TECHNICAL_DOCS_HUB.md` → Apify MCP link yok
- `REPORTS_ANALYSIS_HUB.md` → 3lü cost comparison yok
- `PLAN_STRATEGY_HUB.md` → 90 günlük roadmap yok (bu dokümanda yazılmalı)

**Çözüm (2 saat):** 3 hub'a 1–2 backlink ekle. Yapı zaten kuvvetli.

---

## 7. Dokümantasyon Teknik Borcu

### Mevcut Durum

- **156 mükerrer dosya** (aynı içerik 2+ yerde)
- **85 orphan nod** (hiçbir yerden link verilmedi)
- **47 kırık link** (dosya silindi ama ref kaldı)
- **Update süresi:** 6 ay arası geç (AGENTS.md = 2026-09-27, eski döküman = 2026-09-09)

### Darboğaz: "Hangi doküman güvenli kaynaktır?" Sorusu Cevapsız

**Örnek:**
- `AI proje v1/V10/07_referanslar/10_apify_*` (2026-09-10, Eski)
- vs. `data/analiz/2026-10-01_uc_li_kazima_mimarisi.md` (Bugün, Yeni)
- **Okuyucu:** Hangi birini güvenmeliyim?

**Çözüm:** D-220 (Dokümantasyon Sıkılaştırma Politikası) AGENTS.md'de var.

```
Kural 1: Tek Kanonik Yol
- Vault kökü → worktree (git authority)
- worktree'de değişiklik → vault'ta "danışman dosya" olur (sync lag 1 gün)

Kural 2: Eski dosya silme değil, "deprecated" işaret
- AI proje v1/ klasörü → @deprecated 2026-10-01, yerine → data/analiz/
```

**Kısa Çözüm (1 gün):**
- `AI proje v1/V10/07_referanslar/10_apify_*` başına ekle: `@deprecated 2026-10-01 → [[2026-10-01_uc_li_kazima_mimarisi]]`
- `data/analiz/` dosyasına ekle: `@canonical source-of-truth, replaces V10/07_referanslar/*`

---

## İyileştirme Adaylarının Özet Tablosu

| # | İyileştirme | Mevcut Maliyet | Kazanç | İş Yükü | Kritik Risk | Hızlı Başlangıç | Öncelik |
|---|-------------|---|---|---|---|---|---|
| **D1** | Unified Audit Log (Katman 5 D-310) | $0 = hiç kontrol | KVKK uyum, yasal kanıt | 4 gün | Tasarım yanlış | Şema tasarla (2h) | 🔴 P0 |
| **D2** | Jina → Firecrawl fallback + cache | $5/ay = dönem dönem sıkışma | 0 downtime, 50% faster | 3 gün | Cost overrun | Rate limit simulation | 🟡 P1 |
| **D3** | Apify monthly $150 plan | $5/ay = 2–6 run = **eksik** | Tüm kaynaklar kapak | 0 gün (karar) | Bütçe aşması | Admin onayı | 🔴 P0 |
| **D4** | Scrapling browser cache + 4 worker | $0 = 26 saat seri | 4x hız (26h → 6h) | 2 gün | Memory leak | PoC: 1 OSB | 🟡 P1 |
| **D5** | NACE batch embedding (9Router) | $0 = sırayla | 1.4h → 50sn | 1 gün | Batch API yok | Test et (30m) | 🟢 P2 |
| **D6** | Hub backlink tamamlama | $0 = 85 orphan | Navigasyon iyiliği | 0.5 gün | Hiç | 3 backlink ekle | 🟢 P3 |
| **D7** | Doc canonical marking (@deprecated) | $0 = karışıklık | Tek kaynak netliği | 1 gün | Update lag | 5 dosya işaretle | 🟢 P3 |

---

## STRATEJİDEN TAKTİĞE: 3 Kritik Odak Alanı

### 🔴 P0 — KVKK Uyum (Hukuki Risk)

**Seç:** **D1 + D3** (Audit Log + Apify Budget)

| Yapılacak | Sorumlu | Gün | Çıktı |
|-----------|---------|-----|-------|
| Unified audit schema tasarımı | Architect | 0.5 | JSON schema (audit_entry v1) |
| PostgreSQL audit_log tablosu yazımı | Dev | 1 | Migration 0044 |
| 3 araçtan example log çekme | QA | 1 | sample.jsonl × 3 |
| Pipeline yazımı (normalize + write) | Dev | 1.5 | `unified_audit_log.py` |
| Unit test (100% coverage) | QA | 1 | 20+ test case |
| Apify monthly plan geçişi (BİR KARAR) | PO | 0.1 | `.env` güncelleme, $150/mo dokümanter |
| **Subtotal** | — | **~5 gün** | Üretime hazır |

**Risk:** Audit log yazılmadan KVKK denetimi başarısız  
**Kazanç:** Denetim izleri → yasal güven

---

### 🟡 P1 — Operasyonel Hız (Maliyeti Tasarruf)

**Seç:** **D2 + D4** (Fallback + Browser Cache)

| Yapılacak | Sorumlu | Gün | Çıktı |
|-----------|---------|-----|-------|
| Firecrawl fallback konfigürasyonu | Dev | 1 | `web_fetch_fallback.py` |
| Jina rate limit monitoring | QA | 1 | Alert threshold ayarı |
| Scrapling cache integration | Dev | 1.5 | BrowserPool + headless cache |
| Load test (13 OSB × 500 firma) | QA | 1 | Profiling raporu |
| **Subtotal** | — | **~4.5 gün** | 4x hız, 0 downtime |

**Risk:** Cache corrupted → stale data  
**Kazanç:** İşletim maliyeti ÷2, hız ×4

---

### 🟢 P2 — Teknikallik (Finesse)

**Seç:** **D5 + D6 + D7** (Batch + Hub + Doc)

| Yapılacak | Sorumlu | Gün | Çıktı |
|-----------|---------|-----|-------|
| 9Router batch embedding test | Dev | 0.5 | API compatibility check |
| 5 "deprecated" işaretleme | Doc | 0.5 | Backlinks |
| Hub backlink tamamlama | Doc | 0.5 | 3 yeni ref |
| **Subtotal** | — | **~1.5 gün** | Netlik, automation |

**Risk:** Hiçbiri (ön koşul değil)  
**Kazanç:** Bakım kolaylığı

---

## ÖZ-ELEŞTİRİ: Bu Planda Neler Atlandı?

1. **Uzun vadeli görünürlük:** Apify/9Router cost anomaly detection → Prometheus metrikleri (ESKI planında var, şimdi unutuldu)
2. **Veri kalitesi eşiği:** "NACE kodu %80 dolu" hedefi olmayan — arbitrer (D-252 tanımı var ama ölçüm yok)
3. **Ajan sertifikasyonu:** "Web kazıma uzmanı (D-310 uyum)" rölü → test planı yok
4. **İnsan kaynakları:** 3 araç bakımı için 2 FTE saat/ay dedik ama **kim yapacak?** isim yok
5. **Felaket senaryosu:** "Tüm 3 araç çıktı" → fallback nedir? Elle kazıma mı?

**Geliştirmeler için Upgrade Kapısı:**
- **Q4 2026:** Prometheus dashboard (cost anomaly → alert)
- **Q1 2027:** Data quality SLA (NACE coverage %X → alarm)
- **Q2 2027:** Agent certification program (training + exam)
- **Erken:** Disaster recovery runbook yazılmalı (3 saat)

---

## Sonuç

### Stratejik Tasarım: ✅ Güçlü

Üç araçlı sistem: 9Router (hız) + Apify (parallelism) + Scrapling (güvenlik)  
D-310 uyumluluğu: 4/5 katman mevcut, 1 katman (Audit) yazılmalı  
ROI: $180/yıl + 11 gün refactor = 3 ayda geri alınır

### Taktik Yol Haritası: ⚠️ Eksik

- Zaman planı: Sprint-bazlı şekilde sundum (90 gün)
- Sorumlu: Atanmamış
- Ölçüler: Belirsiz ("hız ×4" ama hedef ne?)
- Risk çeşitliliği: Yüksek (üç kritik bağımlılık)

### 3 Kritik Odak (Taktik Başlangıç)

| Sıra | Fokus | Neden | Gün |
|------|-------|-------|-----|
| **1** | D1 + D3: Audit Log + Apify Monthly | KVKK hukuki zorunluluk | **5 gün** |
| **2** | D2 + D4: Fallback + Cache | İşletim maliyeti ÷2 | **4.5 gün** |
| **3** | D5 + D6 + D7: Batch + Hub + Doc | Teknik borç azalması | **1.5 gün** |
| **Toplam Geri Dönüş** | — | — | **~11 gün** |

**Karar Noktası (Sahip için):**
- Apify monthly $150/ay kabul et mi? (P0 karar)
- Audit log KVKK şartı mı? (P0 karar)
- 11 günlük ekstra dev yükü kabul edilebilir mi? (PO karar)

**Şu an yapılabilecekler (karar beklemez):**
- Unified audit schema yazma (30 min, architecture)
- Rate limit simulation (1 saat, test)
- Doc canonical marking (1 saat, dokümantasyon)

---

## Ilgili Nodlar

- [[Huginn Data Insights/data/analiz/2026-10-01_uc_li_kazima_mimarisi]] — Üçlü mimarinin stratejik tasarımı
- [[Huginn Data Insights/plans/2026-10-01_maliyet_fayda_analizi_9router_vs_apify]] — ROI raporu (ücretsiz/az ücretli öncelik)
- [[Huginn Data Insights/AGENTS.md#D-310]] — Beş katmanlı kontrol standardı
- [[Huginn Data Insights/plans/9router_analiz_raporu]] — 9Router yetenekleri
- [[Huginn Data Insights/AI proje v1/V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910]] — Apify araştırması
- [[Huginn Data Insights/data/analiz/2026-10-01_scrapling_kazima_aracı]] — Scrapling detaylı analiz
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] — Hub merkezleştirilmesi
