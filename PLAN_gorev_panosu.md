# Plan: Görev Panosu Yönetimi ve İş Emirleri

> **Tarih:** 2026-09-03  
> **Durum:** Plan Aşaması

## 1. Mevcut Durum Analizi

### Görev Paneli Özeti
| Kategori | Sayı |
|----------|------|
| Toplam Görev | 22 |
| Plan Aşaması | 17 |
| Tamamlanan (done) | 6 |

### İç Ajan Dağılımı (Plan Aşaması)
| Ajan | Görev Sayısı | Örnek Görevler |
|------|--------------|----------------|
| gelistirici | 10 | T1, P0-2, P1-1...P2-5 |
| arastirmaci | 3 | T2, P1-5, P2-1 |
| mimar | 1 | T3 |
| web_kazima | 2 | P0-1, P2-3 |
| kalite | 2 | P0-3, P2-4 |

## 2. Önceliklendirme Önerisi

### P0 (Kritik - Hemen)
- T1: Ivedik scraper implementasyonu

### P1 (Yüksek)
- P0-1: OSTİM detay scrape (~1961/8313)
- P0-2: Scrape ingest → VKN → kalite
- P1-1: İvedik OSB scraper
- P1-2: Başkent OSB scraper
- P1-3: ASO veri ingest (488KB)
- P1-4: Multi-OSB merger (~19.000)

### P2 (Orta)
- P0-3: Kalite skoru 6.53 → 50+
- P2-4: Entity resolution optimizasyonu
- P2-5: İç ajan otomatik atama

## 3. İşbölümü Planı

### Ajana Göre Gruplama

**Gelistirici (10 görev):**
- T1, P0-2, P1-1, P1-2, P1-3, P1-4, P1-6, P2-2, P2-5

**Arastirmaci (3 görev):**
- T2, P1-5, P2-1

**Mimar (1 görev):**
- T3, T3b

**Web Kazıma (2 görev):**
- P0-1, P2-3

**Kalite (2 görev):**
- P0-3, P2-4

## 4. Uygulama Adımları

### Adım 1: Görev Paneli Güncelleme
```python
# task_board.py kullanarak:
# - Tüm plan görevlerini "aktif" durumuna geçir
# - Sahip bilgilerini state.json'a kaydet
```

### Adım 2: Paralel Çalışma Düzeni
```
Ajan: Geliştirici  → T1, P0-2, P1-1 (paralel chunk)
Ajan: Araştırmacı  → T2, P1-5, P2-1 (seri)
Ajan: Mimar         → T3, T3b
Ajan: Web Kazıma   → P0-1, P2-3
Ajan: Kalite       → P0-3, P2-4
```

### Adım 3: Handoff Mekanizması
- Her görev tamamlandığında `handoff_yaz()` çağır
- Sonraki ajana bağlam devri

## 5. Kritik Dosyalar

| Dosya | Rol |
|-------|-----|
| `data/orchestrator/task_board.json` | Ana görev veritabanı |
| `data/orchestrator/state.json` | Orkestrator durumu |
| `src/company_master/orchestrator/task_board.py` | API modülü |
| `src/company_master/orchestrator/internal.py` | Ajan tanımları |

## 6. Doğrulama

```bash
# Görev listesini kontrol et
python -c "from company_master.orchestrator import task_board; print(task_board.gorev_listesi())"

# Markdown panosunu görüntüle
cat data/orchestrator/gorev_panosu.md
```

## 7. Sonraki Adımlar

1. Act moduna geç
2. Görevleri "aktif" durumuna güncelle
3. Handoff mekanizmasını test et
4. Tamamlanan görevleri "done" işaretle
