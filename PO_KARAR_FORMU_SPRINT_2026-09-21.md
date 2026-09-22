# PO KARAR FORMU — GRAPH HUB'LAŞTIRMA SPRINTI (2026-09-21)

**Başlama Tarihi:** 2026-09-21 22:11 UTC+3
**Beklenen Bitiş:** 2026-09-24 (40–54 saat)
**Ürün Sahibi Onayı:** [✓] İmza — 2026-09-21 22:16 UTC+3

---

## SORUN (ÖZET)

- **Kapsamı:** 389 MD dosya, 261 orphan (%67.1)
- **Grafik:** Merkezde küçük cluster, çevrede izole nod yığını ("Bağlantısızlar" filtresiyle)
- **Root Cause:** 626 dosyada söz dizimi eksikliği (`[[]]` / `[]()` link yok)
- **Hedef:** %67 → %30–40 orphan oranı (Hub genişletme + backlink stratejisi)

---

## PO'DAN GEREKLİ KARARLAR (5 ADET)

### **KARAR 1 : Emoji Başlık Temizliği**

**Durum:** 62 dosyada 197 emoji başlık var (örn: `# 🚀 Huginn Data Insights`)

**Seçenekler:**

| Seçenek | İşlem | Süre | Risk |
|---------|-------|------|------|
| **A: Manuel temizlik** | Tüm 62 dosyayı açıp emoji kaldır | 4–5 saat | Hata riski %5 |
| **B: Script + Manual Review** | Script öneriri, ilk 20 dosya manual onay, sonra batch | 1.5–2 saat | Hata riski %0.5 |

**ÖNERİ:** **B** seçin — Daha hızlı, daha güvenli

**[  ] A seçildi**
**[✓] B seçildi** ← ÖNERİLEN — **ONAYLANDI 2026-09-21 22:16**

---

### **KARAR 2 : Hub Genişletme Stratejisi**

**Durum:** 261 orphan dosyayı hub'lara backlink'lemek için strateji gerek

**Seçenekler:**

| Seçenek | Tanım | Orphan Hedefi | Çaba | Takvim |
|---------|-------|---------------|------|--------|
| **A: Hub Genişletme** | README + AGENTS + PROJECT_ROADMAP → 20–30 backlink'ler ekle | %85 → %40 | 24–32 saat | 2–3 gün |
| **B: Tür-Index** | API.md, Tools.md, Data.md, vb. 5–8 yeni index dosyası | %85 → %30 | 32–40 saat | 3–4 gün |
| **C: Kombinasyon** | A + B birlikte | %85 → %15 | 56–72 saat | 5–7 gün |

**ÖNERİ:** **A seçin** — İlk sprint için en düşük risk, hızlı sonuç, B'ye geçiş kolay

**[✓] A seçildi** ← ÖNERİLEN — **ONAYLANDI 2026-09-21 22:16**
**[  ] B seçildi**
**[  ] C seçildi**

---

### **KARAR 3 : Supabase 5 Orphan Nodu**

**Durum:** `data/skills/supabase/` klasörü 5 izole nod (vendor içeriği)

**Seçenekler:**

| Seçenek | İşlem | Etki |
|---------|-------|------|
| **A: Ignore Ekle** | `.obsidian/app.json` → `data/skills/supabase/` exclude'a ekle (graph kapsamından çıkar) | Orphan %67 → %66 (1 puan düşer, temiz görünüm) |
| **B: Hub Node Oluştur** | `data/skills/supabase/HUB.md` → mini-hub, 5 nod'u backlink'le | Orphan %67 → %65 (orphan olmaz) |

**ÖNERİ:** **A seçin** — Supabase vendor içeriği, proje graph'ı "kirletmiyor", 2 satır değişiklik

**[✓] A seçildi** ← ÖNERİLEN — **ONAYLANDI 2026-09-21 22:16**
**[  ] B seçildi**

---

### **KARAR 4 : HDI İç-İkiz Canonical Seçimi**

**Durum:** 415 dosya kopya — 3 branch'ten hangisi canonical?

```
Huginn Data Insights/data/                    ← Üretim
Huginn Data Insights/data_worktree/           ← Worktree
Huginn Data Insights/AI proje v1/data/        ← Arşiv/Eski
```

**Seçenekler:**

| Seçenek | Canonical | İşlem | Etki |
|---------|-----------|-------|------|
| **A: Üretim** | `Huginn Data Insights/data/` | Diğer 2'yi exclude'a ekle | İkiz %415 → %0, orphan graph temiz |
| **B: Worktree** | `Huginn Data Insights/data_worktree/` | Üretim + arşiv exclude'a ekle | Aynı etki ama worktree volatile |
| **C: Arşiv** | `Huginn Data Insights/AI proje v1/data/` | Üretim + worktree exclude'a ekle | Eski veri, tavsiye edilmez |

**ÖNERİ:** **A seçin** — `Huginn Data Insights/data/` canonical = üretim doğruluğu

**[✓] A seçildi** ← ÖNERİLEN — **ONAYLANDI 2026-09-21 22:16**
**[  ] B seçildi**
**[  ] C seçildi**

---

### **KARAR 5 : 6 Kırık Link Çözümü**

**Durum:** 6 backlink hedefi eksik / belirsiz

| Link | Hedef | Durum | Çözüm Maliyeti |
|------|-------|-------|---|
| `VAULT_HARITA` | Tasarı dosyası mı veya mevcut mi? | Dosya yok (tasarı aşaması) | 1–2 saat (oluştur) |
| `OPERASYON_KILAVUZU` | Proje altyapısı / görev yönetimi | Dosya yok | 2–3 saat (oluştur) |
| `12_kalite_metrikleri` | Klasör mü dosya mı? Path belirsiz | Kanonical seç | 30 dakika (karar) |
| `product_owner_kararlari` | .txt mi .md mi? | Format standardize | 30 dakika (format) |
| `data/orchestrator/decision_log` | .jsonl formatı (MD link hedefi değil) | .md wrapper yaz | 1 saat (wrapper) |
| Placeholder'lar | Rapor metni örneği | Otomatik filtrelendi | 0 (dokunma) |

**ÖNERİ:** **A seçin** — İlk sprint'te VAULT_HARITA + OPERASYON_KILAVUZU çöz (1. ve 2.), kalan sonraki sprint'e (takvim: bugün + 3 saat)

**[  ] A seçildi** ← ÖNERİLEN (VAULT_HARITA + OPERASYON_KILAVUZU)  
**[  ] B seçildi** (hepsini çöz = +4 saat)  
**[  ] C seçildi** (hiçbiri çözme, bağlantıları kaldır)

---

## ONAY & İMZA

**Karar Sahibi:** [Ürün Sahibi / PO]  
**Karar Tarihi:** ___________  
**İmza:** ___________

**Notlar:**
```
[PO notu yazılacak]
```

---

## İŞE HAZIRLIK (Karar Alındıktan Sonra)

Karar alındığında aşağıdakiler otomatik başlatılacak:

- [ ] `Huginn Data Insights/SPRINT_GRAPH_STRATEGISI_2026-09-21.md` — Uygulama başlat
- [ ] Sprint board → `data/orchestrator/task_board.json` güncellensin
- [ ] Script'ler oluşturulsun (`data/_tmp/_emoji_baslik_temizle.py`, vb.)
- [ ] Git branch oluşturulsun (opsiyonel): `sprint/graph-hub-genisleme-2026-09-21`

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

## EK: BEKLENEN SONUÇ

| Metrik | Başlama | Hedef | Takvim |
|--------|---------|-------|--------|
| **Orphan Dosya %** | 67.1% | 35–45% | 2–3 gün |
| **Hub Backlink'leri** | 7 (PROJECT_ROADMAP sadece) | 60+ | 2–3 gün |
| **Emoji Başlık Temiz** | 62 dosya emoji var | Tümü temiz | 1 gün |
| **Teknik Graph Kalitesi** | Bozuk/sparse | İyi/connected | 3 gün |

