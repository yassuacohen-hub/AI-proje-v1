# Vergi Numarası Sorgulama Stratejisi

## Durum (2026-09-03)
- 8.313 OSTİM firması, vergi no doluluk: %0
- GİB açık veri **mevcut değil** (KVKK nedeniyle)
- e-Fatura kayıtlı kullanıcı listesi / e-Arşiv sorgulama **toplu erişilemez**

## Alternatif Kaynaklar (Sıralı)

### P0 — OSTİM Detay Scrape (Devam Ediyor)
- 1.232+ detay kaydı toplandı (1232/8313, %14.8)
- Adres, web, telefon, parsel alanlarını dolduruyor
- VKN regex fallback (unvan içinde 10-11 hane) → 0 eşleşme

### P1 — MERSİS (Maliye Sicil Bilgi Sistemi)
- URL: `mersis.gov.tr`
- VKN ile tekil sorgulama mümkün, ancak **API erişimi sınırlı**
- Resmi talep: api@mersis.gov.tr (varsayım)

### P2 — Ticaret Sicili (TSB)
- URL: `tsb.gov.tr`
- Şirket adı + unvan eşleşmesi → VKN döndürür
- API erişimi: Sınırlı, rate limiting

### P3 — Oda/Kuruluş Kaynakları
- **OSTİM OSB** → `ostim.org.tr` (devam eden scrape)
- **İvedik OSB** → `ivedik.org.tr` (henüz başlanmadı)
- **ASO 1-3** → `aso.org.tr` (henüz başlanmadı)
- **Başkent OSB** → `baskent.org.tr` (henüz başlanmadı)

### P4 — Web Sitesi Footer Scraping
- VKN genellikle footer'da yer alır
- Pattern: 11 hane rakam
- 554 web sitesi dolu, bu yöntemle VKN extraction mümkün

## Veri Toplama Stratejisi
**Hedef: Tüm Ankara OSB firmalarını temiz dataset haline getirmek**

1. **OSTİM:** 8.313 firma (devam eden scrape)
2. **İvedik OSB:** ~3.000 firma (bekleniyor)
3. **ASO 1-3:** ~5.000 firma (bekleniyor)
4. **Başkent OSB:** ~2.000 firma (bekleniyor)
5. **Anadolu OSB, Dökümcüler, HAB, Polatlı:** ~1.000+ firma (bekleniyor)

**Toplam Hedef:** ~19.000+ Ankara B2B firması

## Teknik Implementasyon

### 1. Detay Scrape (Kilo Code)
- `scripts/ingest_ostim_detail.py` — Batch processing (100'er)
- NULLPool + prepare_threshold=None
- statement_timeout=0

### 2. Web Sitesi Footer Scraping (Yeni)
```python
# scripts/footer_vkn_extractor.py
import re
VKN_PATTERN = re.compile(r'\b\d{10,11}\b')

def extract_vkn_from_footer(html: str) -> str | None:
    # VKN genellikle "Vergi No" veya "VKN" etiketiyle
    # Footer'da yer alır
    pass
```

### 3. Multi-OSB Data Merger (Yeni)
```python
# scripts/multi_osb_merger.py
# Tüm OSB'lerin firmalarını tekilleştir
# Vergi no olmadan fuzzy matching ile
```

## Ajan Görevleri

### Web Kazıma Uzmanı
- OSTİM detay scrape devam (Kilo Code)
- Diğer OSB siteleri için **30 dakikalık masa başı analiz** gerekli
  - robots.txt kontrolü
  - KVKK uyumluluk
  - Rate limit belirleme

### Araştırmacı Ajan
- MERSİS API başvuru yöntemini araştır
- Ticaret Sicili API araştır
- Alternatif açık veri kaynakları (BİST, Oda, vb.)

### Mimar Ajan
- `data/aso1/`, `data/aso23/`, `data/baskent/`, `data/ivedik/` veri şemaları
- Multi-OSB unified şema tasarımı

## Açık Sorular
- MERSİS API başvurusu için gerekli belgeler
- Ticaret Sicili API rate limit
- Footer'da VKN olmayan firmalar için alternatif

## Bağlantılar
- `00-Home` · `01_sirket_master_ana_belgesi` · `02_ankara_osb_ekosistemi_arastirma_notu` · `06_web_kazima_uzmani` · `04_web_kazima_kaynak_arastirmasi`

---

> VKN sorgusu motor kaynaklarina eklenmis politika ile yapilir (GIB domain, [[OSINT_Scraper_Motoru]] registry'de).
