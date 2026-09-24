# Görev Atama Özet Tablosu

**Sprint Başı Hızlı Başlatma — Her ajan kendi tablosu.**

Ajan başlarken ilgili tabloyu açıp `Başlatma Komutu` sütunundaki komutu **adım adım** çalıştır.

---

## 🔧 UTKU (Üretim/Hacim)

| Görev ID | Başlık | Aciliyet | Durum | Başlatma Komutu |
|----------|--------|---------|-------|-----------------|
| **API-ADMIN-AKTIVITE-YAZ-14** | Giriş/arama/AI olaylarını log'a yaz | P0 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **DOC-ADMIN-DURUM-SENKRON-15** | Bayat durum satırlarını senkronla | P1 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **API-ADMIN-CHURN-3SINYAL-16** | Churn kuralını 3 sinyale genişlet | P1 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **API-ADMIN-KAYNAK-SAGLIK-18** | Kaynak sağlık skorunu ölç | P1 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **UI-ADMIN-CRAWL-KONTROL-19** | Crawl tetikle/durdur aksiyonu | P1 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **UI-ADMIN-ARAMA-BOSLUK-20** | Sonuçsuz arama frekans raporu | P2 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **API-ADMIN-SUPHELI-AKTIVITE-21** | Şüpheli aktivite kuralları | P2 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **UI-ADMIN-UPSELL-22** | Upsell aday listesi | P2 | Bekliyor | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **ALTYAPI-SECRETS-SETUP-01** | Vault kur, .env template | P0 | Plan | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **ALTYAPI-DB-MIGRATION-01** | v0016 → v0017 prod migration | P1 | Plan | `python scripts/gorev_kutusu.py basla --ajan utku` |
| **ALTYAPI-ADMIN-PANO-01** | Task board 4 bölüm | P2 | Plan | `python scripts/gorev_kutusu.py basla --ajan utku` |

---

## 🧪 YASU (Denetim/Review)

| Görev ID | Başlık | Aciliyet | Durum | Başlatma Komutu |
|----------|--------|---------|-------|-----------------|
| **TEST-BLOKE-FAKTOR-ARASTIRMA-01** | Test hazırlık planı araştır | P0 | Plan | `python scripts/gorev_kutusu.py basla --ajan yasu` |

---

## 🎯 İHSAN (Orkestratör)

| Görev ID | Başlık | Aciliyet | Durum | Başlatma Komutu |
|----------|--------|---------|-------|-----------------|
| **ORKESTRA-AI-CHAT-KOORDINASYON-01** | Ajan arası protokol yazı | P1 | Plan | `python scripts/gorev_kutusu.py basla --ajan ihsan` |

---

## 📋 Kısa Komut Şablonları (Copy-Paste)

### Görev Başla (İlk adım — her gün)
```bash
python scripts/gorev_kutusu.py basla --ajan <ad>
```
Yerine koyulan `<ad>`:
- `utku` — Üretim görevleri
- `yasu` — Denetim görevleri
- `ihsan` — Orkestrasyon görevleri

---

### Görev Al (Pano gör → Al)
```bash
python scripts/gorev_kutusu.py al --task-id <TASK-ID> --ajan <ad>
```

Örnek:
```bash
python scripts/gorev_kutusu.py al --task-id API-ADMIN-AKTIVITE-YAZ-14 --ajan utku
```

---

### Görev Teslim
```bash
python scripts/gorev_kutusu.py teslim --task-id <TASK-ID> --ajan <ad>
```

Örnek:
```bash
python scripts/gorev_kutusu.py teslim --task-id API-ADMIN-AKTIVITE-YAZ-14 --ajan utku
```

---

### Posta Kutusu Gözle (Durum kontrol)
```bash
python scripts/gorev_kutusu.py bak --ajan <ad>
```

---

## 📌 Görev Başında Yapılacaklar (D-66, D-197 Kuralı)

Görev panosu açılmadan önce **HER ZAMAN**:

1. **İlgili SSOT'u oku** (bulunursa) — `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (ADMIN-KIT)
2. **Brief dosyasını aç** — `plans/brief_<ajan>_<TASK-ID>.md`
3. **Hub referansını kontrol et** — Brief içinde `**Hub:**` satırı (D-186)
4. **Simulasyon çalıştır** (Plan durumundaysa):
   ```bash
   python scripts/gorev_kutusu.py simulasyon
   ```
   Çıkış kodu:
   - `0` = Temiz, başla
   - `1` = Uyarı var, devam et (notu tur planına yaz)
   - `2` = Hata var, **önce hatayı kapat**

---

## 🔗 İlgili Belgeler

- **AGENTS.md** — Ajan kuralları, yaşam döngüsü, kural referansları
- **PLAN_gorev_panosu.md** — Sprint planlaması
- **docs/AJAN_KOMUT_REHBERI.md** — Komut detaylı açıklaması
- **plans/_brief_sablon.md** — Brief yazma şablonu

---

**Güncellenme:** 2026-09-24  
**Kaynak:** `data/orchestrator/task_board.json`
