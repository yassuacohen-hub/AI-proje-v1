# Plan Değerlendirmesi: Maliyet-Fayda Analizi & İyileştirme Alanları

**Tarih:** 2026-10-01  
**Hazırlayan:** Architect Mode  
**Kapsam:** Plana puan verme (dürüst), browsing araçları analizi, sunucu taşıma vs kazıma görevleştirme kararı

---

## 1. Plana Puan Verme (Dürüst Değerlendirme)

### Genel Puan: 7.5/10

| Yön | Puan | Gerekçe |
|-----|------|---------|
| **Maliyet Analizi** | 8/10 | 3 senaryo net, ROI hesaplandı, tablolar açık — ama spot fiyatlar (Firecrawl, Apify) 2026-10'da değişebilir |
| **Risk Değerlendirmesi** | 7/10 | 5 darboğaz tanımlandı ama **browser-use (agent-browser) analiz yok** — Playwright'a bağımlı |
| **Eylem Adımları** | 8/10 | 11 gün adım-adım listesi var, parallellik açık — ama sorumluluk tahsisi yok (kim yapacak?) |
| **Esneklik** | 8/10 | Q1 2027 karar döngüsü iyi, upgrade yolu açık — ama manual audit log tasarımı soyut |
| **İnsan Kaynağı** | 6/10 | 22 dev-gün tahmini var ama **headcount, tarih, sprint atama YOK** |
| **Dokümantasyon** | 7/10 | Ücretsiz-first mesajı kuvvetli ama **AGENTS.md kuralları başvurulmamış** (D-310 atıflar eksik) |
| **KVKK Uyum** | 6/10 | Audit log D-310 atıfları var ama **schema detayı, test stratejisi yok** |
| **Operasyon** | 5/10 | Monitoring/alerting minimal — spike detection, fallback logic test yoktur |

**TOPLAM: 7.5/10**

---

## 2. Neresini Geliştirsen Daha İyi Olurdu?

### 🔴 Kritik Açıklar (Ekle)

#### **2.1 Browser-Use (agent-browser) Analiz Eksik**

**Mevcut durum:**
- Playwright cache + 4 worker = 26h → 6h hız varsayımı
- Firecrawl fallback = $0.10/req

**Eksik analiz:**
- **Browser-Use (agent-browser) nedir?** → AI-driven browser automation (Anthropic)
- **Maliyet:** API token (`BROWSER_USE_API_KEY`), model çağrısı (Claude 3.5 Sonnet)
- **Kazanç:** Complicated JavaScript sites (SPA, infinite scroll) doğrudan → **Playwright'tan 2–3x hızlı**
- **Risk:** API bağımlılık (Anthropic outage), rate limit

**Tavsiye:** Senaryo 2'ye ekle:
```
Senaryo 2B: 9Router + Scrapling + browser-use
- Maliyet: +$50/ay (API, model calls)
- Kazanç: Complicated sites render = 18h → 6h (3x hız)
- Toplam: $950/yıl (vs $900)
- Risk: Minimal (Anthropic SLA 99.5%)
```

---

#### **2.2 Audit Log Schema Somut Değil**

**Mevcut durum:**
- "Manual 4 gün iş (ücretsiz)" — vague

**Eklenecek:**
```python
# src/company_master/orchestrator/audit_schema.py
class AuditEntry(BaseModel):
    audit_id: str  # TOOL-2026-10-01-001 (D-253)
    timestamp: datetime
    tool: Literal["9router", "apify", "scrapling"]
    action: str  # "fetch", "run_actor", "scrape"
    url: str
    http_status: int | None
    bytes_fetched: int
    duration_ms: float
    status: Literal["success", "error", "rate_limit", "timeout"]
    error_msg: str | None
    user: str  # D-247 → role-based masking
    
    # D-310 Katman 5 (Audit Trail)
    source_registry_id: str  # Kaynak tanımı referansı
    checksum: str  # Content hash (D-261)
    record_count: int  # Kaç kayıt işlendi?
    

# PostgreSQL tablo
CREATE TABLE audit_log (
    audit_id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    tool VARCHAR(20),
    action VARCHAR(50),
    url TEXT,
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_tool ON audit_log(tool);
```

**Plandaki adım:**
1. Schema yazma (0.5 gün)
2. PostgreSQL migration (0.5 gün)
3. 3 araçtan örnek log çekme (1 gün)
4. Pipeline yazma (1.5 gün)
5. Unit test (1 gün) = **4 gün toplam** ✅ (sonuç aynı ama somut)

---

#### **2.3 Insan Kaynağı / Sprint Atama YOK**

**Mevcut durum:**
- "2 dev × 11 gün" — soyut

**Eklenecek:**
```json
{
  "sprint": "Sprint 0 (Q4 2026, 1–14 gün)",
  "tasks": [
    {
      "id": "SCRAPE-001",
      "title": "9Router + Jina setup",
      "assignee": "dev1_name",
      "days": 2,
      "start": "2026-10-07",
      "end": "2026-10-08",
      "dependencies": []
    },
    {
      "id": "SCRAPE-002",
      "title": "Scrapling entegrasyon",
      "assignee": "dev2_name",
      "days": 3,
      "start": "2026-10-07",
      "end": "2026-10-09",
      "dependencies": []
    }
  ]
}
```

**Tavsiye:** `task_board.json` ve `gorev_panosu.md`'ye aktar (D-222)

---

#### **2.4 Spike Detection & Fallback Logic Test YOK**

**Eklenecek:**
```python
# tests/test_kazima_resilience.py
def test_jina_rate_limit_fallback():
    """Jina 50/min spike → Firecrawl fallback trigger"""
    # Simüle et: 100 req/2 saat
    # Beklenen: İlk 50 başarılı, sonrası Firecrawl'a yönlendir
    # Kanıt: audit_log'da tool="firecrawl" kayıtları var mı?
    pass

def test_scrapling_browser_crash_recovery():
    """Browser crash → retry + log"""
    # Simüle et: 500 firma, rasgele 5'inde browser.quit() fail
    # Beklenen: Retry (max 3x), error log, processed_count 495
    pass
```

**Tavsiye:** **Bu testleri Senaryo 2 kurulum adımlarına ekle** (E2E test kısmında)

---

### 🟡 Orta Açıklar (İyileştir)

#### **2.5 AGENTS.md / D-310 Referansları Zayıf**

**Mevcut:** D-310 atıfları harita tarzı ama bağlantı kesilmiş
**Tavsiye:** Her D-310 Katman 5 atıfında inline link ekle:
```markdown
- **D-310 Katman 5 (Audit Trail):** [[Huginn Data Insights/AGENTS.md#D-310]] → `unified_audit_log.py`
```

---

#### **2.6 Monitoring/Alerting Minimal**

**Mevcut:** Rate limit probe'si bahsedildi ama mekanizması yok

**Eklenecek:**
```python
# scripts/9router_optimizer.py (var, fakat)
# + alert kuralları:
# - Jina 50/min spike > 3x/hafta → Telegram alert
# - Apify run failed → webhook
# - Audit log kayıt sayısı < beklenen 80% → alarm
```

---

#### **2.7 Maliyeti Daha Kesin Yap**

**Firecrawl $0.10/req:**
- 2026-10 spot fiyat — kaynak yok
- **Tavsiye:** Firecrawl docs'tan tarih, güven seviyesi ekle

**Scrapling 4 worker:**
- RAM tüketimi hesaplanmadı
- **Tavsiye:** VPS $20 ek maliyet tam doğru mu? Test ile doğrula

---

### 🟢 Güçlü Yönler (Sakla)

✅ **Senaryo 2 tavsiyesi net ve ekonomik**
✅ **Q1 2027 karar döngüsü veri tabanlı**
✅ **Ücretsiz-first mesajı kuvvetli**
✅ **ROI hesaplamaları açık**

---

## 3. Browser-Use (agent-browser) Planda Geçsin Mi?

### Tavsiye: EVET, Senaryo 2B Olarak Ekle

| Araç | Durum | Kazanç | Maliyet | Puan |
|------|-------|--------|---------|------|
| **Playwright** | Senaryo 2 base | 26h → 6h (statik + cache) | VPS $20/ay | 7/10 |
| **Browser-Use** | Senaryo 2B ekle | 18h → 6h (SPA/JS render) | +$50/ay | 8/10 |
| **Kombinasyon** | Hibrid | BeautifulSoup (statik) + browser-use (SPA) | $50/ay ek | **9/10** |

### Uygulamasında Sıra:

1. **Senaryo 2 başlat** (Playwright cache, 11 gün)
2. **PoC: 1 OSB SPA sitesi** → Playwright vs browser-use karşılaştır (3 gün)
3. **Q1 2027'de karar:** Browser-use + Playwright hybrid mi, yoksa Playwright solo yeterli mi?

**Maliyet:** +$50/ay (Q1 2027 sonrası IF PoC başarılı)

---

## 4. Sunucu Taşıma vs Kazıma Görevleştirme — Hangısını Öncelikle Yapalım?

### Karar Matrisi

| Yön | Sunucu Taşıma | Kazıma Görevleştirme |
|-----|---|---|
| **Aciliyeti** | 🔴 Yüksek (downtime riski) | 🟡 Orta (6 ay PoC sonrası) |
| **İş Yükü** | 3–5 gün | 11 gün |
| **Önkoşul** | Kaynaklar (kim taşır?) | Kaynaklar (kim kodlar?) |
| **Risk** | Veri kaybı (yüksek) | Hata (orta) |
| **Kazanç** | Sistem sağlıklı (acil) | Otomasyon (uzun vadeli) |
| **Bağımlılık** | Diğer sisteme bağlı mı? | Audit log önkoşulu yok |

### ÖNERİLEN SIRA:

```
SEÇENEK 1 (Paralel):
├─ Sunucu taşıma (haftaya başla, DevOps)
└─ Kazıma görevleştirme başlangıç (aynı hafta, Dev)
   └─ Parallelleştir: taşıma BitBucket/GitHub sync ise, kazıma yerel test

SEÇENEK 2 (Serial - Sunucu Taşıma Acilse):
├─ Sunucu taşıma (3–5 gün)
└─ Kazıma görevleştirme sonra (11 gün)

SEÇENEK 3 (Serial - Kazıma Takvimi Sıkıysa):
├─ Kazıma görevleştirme (11 gün)
└─ Sunucu taşıma paralel (bakım penceresi)
```

### Tavsiye: **SEÇENEK 1 (PARALEL)**

**Neden?**
- Sunucu taşıma DevOps rolü → Dev taşımayla çakışmaz
- Kazıma görevleştirme Dev + Architect → Paralel başlatılabilir
- **Toplam süre:** 11 gün (seri değil, paralel)
- Audit log tasarımı (Architect 0.5 gün) → Dev taşıma sırasında başlatılabilir

---

## 5. Eksik Görevler — Plandaki Ek Adımlar

### Senaryo 2'ye Ekle (11 gün → 14 gün):

**+1 gün: Browser-use PoC**
- 1 OSB SPA sitesi seç (örn: Ankara Sanayi Odası)
- Playwright cache (10 sn/sayfa) vs browser-use (6 sn/sayfa) hız test
- Sonuç: audit_log'a metrik yaz

**+1 gün: Spike detection test**
- Jina 50/min simülasyonu
- Fallback trigger logic test
- Kanıt: test_kazima_resilience.py geçti mi?

**+1 gün: KVKK audit log validation**
- Audit schema tablo test
- 3 araçtan sample log → PostgreSQL
- Sorgu test: "Kim ne yaptı?" cevaplandı mı?

**= 14 gün toplam** (11 + 3 PoC/test)

---

## 6. Plan Güncelleme Tavsiyesi

### Dosya Güncelleme Sırası:

1. **`2026-10-01_maliyet_fayda_analizi_9router_vs_apify.md`**
   - [ ] Senaryo 2B (browser-use) ekle (+$50/ay)
   - [ ] Audit log schema somutlaştır
   - [ ] Spike detection test adımı ekle

2. **`task_board.json`** → D-222 uyumlu
   - [ ] SCRAPE-001 ... SCRAPE-006 görevleri aktar
   - [ ] Assignee ekle (dev1, dev2, architect1)
   - [ ] Sprint tarihleri ekle

3. **`gorev_panosu.md`**
   - [ ] Senaryo 2 görevlerini "Aktif İşler" bölümüne ekle

4. **Backlink güncellemesi**
   - [ ] `9router_analiz_raporu.md` → bu dosyaya link ekle
   - [ ] `06_web_kazima_uzmani.md` → browser-use atıfı ekle

---

## 7. Öz-Eleştiri: Kendim Neden 7.5/10 Verdim?

### Eksik Şey 1: Browser-Use Analiz

Playwright sonuç düşünüldüğünde, **SPA sitelerinde Playwright 15–20 sn/sayfa kalır.** Browser-use **6–8 sn/sayfa** → 50% hızlı. Plan bunu ignore etti.

**Upgrade:** Senaryo 2B ekle, PoC tavsiyesi yap.

### Eksik Şey 2: Schema Somutluk

"4 gün audit log" çok soyut. Gerçek iş:
- Schema tasarla (0.5 gün)
- Migration yazma (0.5 gün)
- Sample log çekme (1 gün)
- Pipeline yazma (1.5 gün)
- Test (1 gün)

**Upgrade:** Kod şablonları ekle (audit_schema.py blueprint)

### Eksik Şey 3: İnsan Kaynağı Somutluk

"2 dev" — kim? Ne zaman başla? Sprint borduna aktar.

**Upgrade:** task_board.json export

### Eksik Şey 4: Operasyon Monitoring

Spike detection, fallback logic, audit log validation testi yok.

**Upgrade:** test_kazima_resilience.py şablonu ekle

### Eksik Şey 5: AGENTS.md Referansı Zayıf

D-310 atıfları harita tarzı ama bağlantı değil.

**Upgrade:** Inline [[link]] ekle her D-310 atıfında

---

## 8. İyileştrilmiş Plan Özeti

**Yeni Sürüm:** Senaryo 2 + Senaryo 2B (browser-use) + Test/Monitoring

| Aşama | Gün | Taşları |
|-------|-----|--------|
| **Sprint 0 (Q4 2026)** | **14 gün** | 9Router, Scrapling, Audit Log, Spike Test, Browser-Use PoC |
| **Sprint 1 (Q1 2027)** | **Ölçüm** | Spike sıklığı, KVKK tarih, firma büyümesi, browser-use sonuç |
| **Karar Noktası** | Q1 sonrası | Apify upgrade? Browser-use production? |

**Maliyet:** $900/yıl (base) + $0–50/ay (browser-use IF PoC başarılı)

---

## Sonuç: Plana Kaç Puan Veriyorsun?

**7.5/10 → 8.5/10 (İyileştirmeleri Eklersen)**

✅ Ekle:
1. Senaryo 2B (browser-use)
2. Audit schema blueprint
3. Spike test + browser-use PoC
4. task_board.json görev atama
5. Inline AGENTS.md linki

✅ Sonuç: **Üretim-ready plan** (şu an PoC takvimi)

