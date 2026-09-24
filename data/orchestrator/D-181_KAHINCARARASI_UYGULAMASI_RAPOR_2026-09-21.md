# D-181: KAHİN Kararları Uygulaması — Rapor

**Tarih:** 2026-09-21  
**Karar:** D-181 (D-59 + abrakadabra + OPERASYON_KILAVUZU uygulaması)  
**Orkestratör:** İHSAN  
**Durum:** ✅ Tamamlandı

---

## Hedef

KAHİN kararlarını (D-181) uygulamak:
1. **D-59 salih rolü:** "QA/Release Engineer" → "Test Danışman" (mekanik görevler, İK dinamikliği)
2. **abrakadabra:** İki mekanizmayı dokümante etmek (çakışma yok)
3. **OPERASYON_KILAVUZU.md:** abrakadabra ritüeli bölümü eklemek (PO anlatımı)

---

## Yapılan İşler

### 1. D-59 salih Rolü Hizalama

**Dosyalar:**
- `worktree klasoru/AGENTS.md` (satır 324-330)
- `Huginn Data Insights/AGENTS.md` (satır 124-131)

**Değişiklikler:**
- **Başlık:** "QA/Release Engineer" → "Test Danışman" (İK modeline uygun)
- **Konsept:** Sert kod kuralı yerine esnek persona sistemi (SSOT: `docs/ajanlar/salih.md`)
- **Raporlama:** SALİH plan sunar → **YASU teslim eder** (`rapor_olustur.py --ajan yasu`)
- **Persona blend:** Release Authority/NO GO tavsiye niteliğinde, nihai onay orkestratöre
- **D-181 karar numarası eklendi** başlık seriesine

**Sözlük satırları hizalandı:**
- Satır 28 (roller özeti)
- Satır 338 / 295 (Kanonik Ad tablosu)
- Satır 383 / 340 (Sözlük tanımı)

---

### 2. abrakadabra Mekanizması

**İki sistem, bir hedef:**

| Mekanizma | Dosya | Görev |
|-----------|-------|-------|
| **Kapı (D-58)** | `scripts/gorev_at.py abrakadabra` | HMAC doğrulama, `orchestrator.json` güncelle, anahtar asla log'a girmez |
| **Ritüel (D-73/74)** | `scripts/orkestrator_rotasyon.py` | `abrakadabra` sözcüğü, karar defterine kayıt, CHANGELOG nota yazma |
| **Sohbet kilidi (S11)** | `ai_chat.py` / `web_dashboard/tabs/abrakadabra.py` | MIMIR kilit sözü (farklı domain, çakışma yok) |

**Anahtar kuralları:**
1. Sadece aktif orkestratör sahip olur
2. Tek seferlik (rotasyon protokolü)
3. Asla loglanmaz, sadece sha256 parmak izi

---

### 3. OPERASYON_KILAVUZU.md — abrakadabra Bölümü

**Yeni Bölüm: 6. ABRAKADABRA RİTÜELİ** (satır ~580)

**İçerik:**
- **6.1 Nedir?** — Güvenlik parolası, KAHİN'in orkestratör devir yetkisi
- **6.2 İki mekanizma tablosu** — Kapı vs. ritüel farkı açıklandı
- **6.3 Nasıl kullanılır?** — CLI komutları (`--kim`, `--kelime`, `--gerekce`)
- **6.4 Anahtar kuralları** — D-73/74 gereği: sahiplik, tek seferlik, log koruması
- **6.5 MIMIR karıştırması** — Sohbet kilidi ≠ orkestratör devri

**Dosya listesi güncellendi:**
- `scripts/orkestrator_rotasyon.py`
- `scripts/gorev_at.py`

---

### 4. decision_log.jsonl — D-181 Kaydı

**Dosya:** `worktree klasoru/data/orchestrator/decision_log.jsonl` (satır 85)

**Kaydın içeriği:**
```json
{
  "id": "D-181",
  "tarih": "2026-09-21",
  "baslik": "salih rolu Test Danisman olarak netlestirildi; abrakadabra ikili mekanizma dokumana islendi",
  "karar": "[Tam açıklama: D-59 uygulanması, SALİH/YASU raporlama akışı, abrakadabra dokümantasyonu]",
  "karar_veren": "KAHIN",
  "kaynak": "AGENTS.md (worktree+HDI) + OPERASYON_KILAVUZU.md + docs/ajanlar/salih.md",
  "ilgili_kararlar": ["D-59", "D-58", "D-63", "D-172"]
}
```

**D-172 gereği sinkronize:**
- worktree klasoru/ → yazma otoritesi (SSOT)
- Huginn Data Insights/ → otomatik sinkronize

---

## Özet Tablosu

| Madde | Dosya | Satırlar | Durum |
|-------|-------|---------|-------|
| D-59 salih rolü | worktree AGENTS.md | 324-330 | ✅ |
| Sözlük (roller) | worktree AGENTS.md | 28, 338, 383 | ✅ |
| D-59 salih rolü | HDI AGENTS.md | 124-131 | ✅ |
| Sözlük (roller) | HDI AGENTS.md | 28, 295, 340 | ✅ |
| SALİH tanımı | OPERASYON_KILAVUZU.md | 85 | ✅ |
| abrakadabra bölümü | OPERASYON_KILAVUZU.md | ~580-650 | ✅ |
| Dosya listesi | OPERASYON_KILAVUZU.md | ~610 | ✅ |
| D-181 kaydı | decision_log.jsonl | 85 | ✅ |
| Sinkronizasyon | HDI decision_log.jsonl | — | ✅ |

---

## Doğrulama Noktaları

1. ✅ **İK Dinamikliği:** D-59 "ajan personaları CV benzeri" yapılı, sert kodlamadan kurtarıldı
2. ✅ **abrakadabra Açıklığı:** İki mekanizmayı ayrı ayrı tanımladı, karışıklık giderildi
3. ✅ **YASU Raporlama:** SALİH → YASU akışı tüm dokümanlara yayıldı
4. ✅ **Persona SSOT:** `docs/ajanlar/salih.md` bağlayıcı referans, Release Authority tavsiye
5. ✅ **D-172 Uyumu:** worktree önce, HDI sinkronize

---

## Uyarılar / Ileri Adımlar

- **docs/ajanlar/salih.md** Release Authority/NO GO tabloları (satır 91-109) — tavsiyelendirmeli olduğu açıklandı, nihai karar orkestratöre
- **Rotasyon protokolü (D-73)** — anahtar yenileme prosedürü operasyonun arkasında kalmıştır; KAHİN ihtiyaç duydukça çalıştırılabilir
- **MIMIR kilit sözü** — `ai_chat.py` + `web_dashboard/tabs/abrakadabra.py` — S11 kararı, bu raporda kapsam dışı (dokümante edilmiş)

---

**Rapor Hazırlayan:** İHSAN (Orkestratör)  
**Durum:** ✅ TAMAMLANDI  
**Sonraki İşler:** Rutin operasyon + ihtiyaca göre persona dosyası güncellemeleri

