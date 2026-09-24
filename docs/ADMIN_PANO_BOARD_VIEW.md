# Admin Panosu — Görev Panosu Gerçek Zamanlı Görünümü

**Versiyon:** 1.0  
**Tarih:** 2026-09-24  
**Ajan:** orkestrator  
**Görev ID:** ALTYAPI-ADMIN-PANO-01

---

## 1. Genel Bakış

Admin panelinin "Görev Panosu" sekmesi, tüm projedeki görevleri **gerçek zamanlı** ve **4 bölüme ayırmış** şekilde gösterir. Filtreleme (ajan, aciliyet, tarih), renk kodlaması ve özet metrikler ile merkezi görev takip imkanı sağlar.

---

## 2. 4 Bölüm Sistemi

Görevler aşağıdaki durumlarına göre otomatik sınıflandırılır:

| Bölüm | Durum | Renk | İkon | Açıklama |
|-------|-------|------|------|----------|
| **Tamamlandı** | `done` | 🟢 Yeşil (#D4F1D4) | ✅ | Tamamlanmış, release edilen görevler |
| **Beklemede** | `aktif`, `review`, `bekliyor` | 🟡 Sarı (#FFF3CD) | ⏳ | Şu anda çalışılan veya incelemede görevler |
| **Yedek** | `plan` | ⚪ Gri (#E8E8E8) | 📋 | Planlanmış, henüz başlanmamış görevler |
| **Değerlendirme** | `blocked`, `reddet`, `iptal` | 🔴 Kırmızı (#FFE5E5) | 🔴 | Engellenmiş, reddedilen veya iptal edilen görevler |

### Durum Döngüsü

```
plan → aktif → review → done
   ↘     ↓       ↓
      blocked ← bekliyor
        ↓
    (reddet/iptal)
```

---

## 3. Filtreleme Kuralları

### 3.1 Ajan Seçimi
- **Hepsi** (varsayılan): Tüm ajanların görevlerini göster
- **İdividual Ajan:** Sadece seçilen ajanın görevlerini göster
  - Örnek: "orkestrator", "utku", "yasu", "salih", "mimir"

```sql
-- Filtre mantığı
SELECT * FROM tasks WHERE sahip = 'selected_ajan' OR sahip IS NULL;
```

### 3.2 Aciliyet Seçimi
- **Hepsi** (varsayılan): Tüm öncelikleri göster
- **P0** (Kritik): Sistemik hata / Prod outage
- **P1** (Yüksek): Önemli feature / Major bug
- **P2** (Orta): Minor feature / Bug fix
- **P3** (Düşük): Belge, refactor, tech debt

```sql
-- Filtre mantığı
SELECT * FROM tasks WHERE oncelik = 'P0' OR oncelik = 'P1';
```

### 3.3 Tarih Aralığı
- **Başlangıç Tarihi:** Görev başlama tarihi (YYYY-MM-DD)
- **Bitiş Tarihi:** Görev bitiş tarihi (YYYY-MM-DD)

```sql
-- Filtre mantığı
SELECT * FROM tasks 
WHERE baslangic >= '2026-09-20' AND bitis <= '2026-09-24';
```

### 3.4 Kombinasyon Filtreleme
Tüm filtreler birlikte çalışır (AND logic):

```python
filtered_tasks = [
    t for t in all_tasks
    if (ajan == "Hepsi" or t["sahip"] == ajan)
    and (aciliyet == "Hepsi" or t["oncelik"] == aciliyet)
    and (not start_date or t["baslangic"][:10] >= str(start_date))
    and (not end_date or t["bitis"][:10] <= str(end_date))
]
```

---

## 4. Tablo Yapısı

Her bölümün altında bir tablo gösterilir:

| Sütun | İçerik | Örnek |
|-------|--------|-------|
| **Görev ID** | Task identifier | `DOC-ADMIN-DURUM-SENKRON-15` |
| **Ajan** | Görevden sorumlu kişi | `orkestrator`, `utku` |
| **Başlık** | Görev başlığı (max 60 char) | `Credential vault kurulumu` |
| **Aciliyet** | Öncelik seviyesi | `P0`, `P1`, `P2`, `P3` |
| **Durum** | Mevcut durum | `done`, `aktif`, `review`, `plan` |
| **Başlangıç** | Başlama tarihi | `2026-09-24` |
| **Bitiş** | Planlanan/Gerçek bitiş | `2026-09-24` veya `-` |
| **Dosyalar** | Değiştirilen dosyalar (ilk 3 + sayaç) | `file1.py, file2.sql +2 daha` |
| **Not** | Açıklama (max 50 char + ...) | `Backup yapıldı, replication test` |

---

## 5. Renk Kodlaması

### Arka Plan Renkleri (16-bit opacity)
```css
/* Tamamlandı */
background-color: #D4F1D422;  /* Yeşil, %13 opacity */

/* Beklemede */
background-color: #FFF3CD22;  /* Sarı, %13 opacity */

/* Yedek */
background-color: #E8E8E822;  /* Gri, %13 opacity */

/* Değerlendirme */
background-color: #FFE5E522;  /* Kırmızı, %13 opacity */
```

### Koşullu Stil Kuralları
```python
def apply_section_style(row: pd.Series, section_color: str) -> list[str]:
    """Her satıra section rengi uygula."""
    return [f"background-color: {section_color}22"] * len(row)

# Kullanım:
df.style.apply(lambda row: apply_section_style(row, "#D4F1D4"), axis=1)
```

---

## 6. Özet Metrikler

Tabloların altında 4 metrik kartı gösterilir:

```
┌─────────────────────────────────────────────────┐
│ ✅ Tamamlandı    │ ⏳ Beklemede    │ 📋 Yedek    │ 🔴 Değerlendirme │
│     12           │      5         │      8      │        3          │
└─────────────────────────────────────────────────┘
```

**Hesaplama:**
```python
metrics = {
    "tamamlandi": len([t for t in filtered if t["durum"] == "done"]),
    "beklemede": len([t for t in filtered if t["durum"] in ["aktif", "review", "bekliyor"]]),
    "yedek": len([t for t in filtered if t["durum"] == "plan"]),
    "degerlendirme": len([t for t in filtered if t["durum"] in ["blocked", "reddet", "iptal"]]),
}
```

---

## 7. Veri Kaynağı

**Dosya:** `data/orchestrator/task_board.json`

### JSON Yapısı
```json
[
  {
    "task_id": "DOC-ADMIN-DURUM-SENKRON-15",
    "baslik": "Admin panel durum senkronizasyonu",
    "durum": "done",
    "oncelik": "P1",
    "sahip": "orkestrator",
    "baslangic": "2026-09-20",
    "bitis": "2026-09-24",
    "dosyalar": [
      "AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md",
      "hubs/ADMIN_DASHBOARD_HUB.md"
    ],
    "not": "SSOT §7 güncellendi, durum etiketleri konsolide edildi"
  }
]
```

### Senkronizasyon
- **Otomatik Yükleme:** Her sayfa açılışında `_gorev_panou_yukle()` fonksiyonu dosyayı okur
- **Caching:** Streamlit caching ile 60 saniye cache
- **Live Update:** Dosya değiştirilmesi = sayfa refresh gerekli

---

## 8. Uygulamada Kullanım

### 8.1 Admin Panelinde Erişim

1. Tarayıcıda `http://localhost:8501` aç
2. Sol sidebar'da "Admin Paneli" seç
3. "Görev Panosu" sekmesine tıkla
4. Filtreler ile görevleri ayarla
5. Tablo ve metrikler otomatik güncellenir

### 8.2 Filtreleme Örneği

**Senaryo:** Orkestrator'un P0/P1 görevlerini 2026-09-20 ile 2026-09-24 arasında görmek

```
Ajan:       orkestrator
Aciliyet:   P1 seç (P0 zaten aktif)
Başlangıç:  2026-09-20
Bitiş:      2026-09-24
```

**Sonuç:**
- Tamamlandı: 2 görev
- Beklemede: 0 görev
- Yedek: 1 görev
- Değerlendirme: 0 görev

---

## 9. Kod Referansı

### Ana Fonksiyon
**Dosya:** `web_dashboard/tabs/admin_panel.py`

```python
def render_task_board_tab() -> None:
    """Admin panelinde görev panosunu 4 bölüm halinde gösterir."""
    # 1. Header ve açıklama
    PageHeader(...).render()
    
    # 2. Veri yükleme
    tum_gorevler = _gorev_panou_yukle()
    
    # 3. Filtre UI
    secilen_ajan = st.selectbox("Ajan", ...)
    secilen_aciliyet = st.selectbox("Aciliyet", ...)
    baslangic_tarihi = st.date_input("Başlangıç", ...)
    bitis_tarihi = st.date_input("Bitiş", ...)
    
    # 4. Filtreleme
    filtrelenmis = tum_gorevler
    if secilen_ajan != "Hepsi":
        filtrelenmis = [g for g in filtrelenmis if g.get("sahip") == secilen_ajan]
    # ... diğer filtreler
    
    # 5. Bölümleme
    bolumler = {"tamamlandi": [], "beklemede": [], ...}
    for g in filtrelenmis:
        bolum = _gorev_bolum_getir(g.get("durum", ""))
        bolumler[bolum].append(g)
    
    # 6. Render
    for bolum_key, bolum_baslik, bolum_aciklama in bolum_bilgileri:
        gorevler = bolumler[bolum_key]
        df = pd.DataFrame(rows)
        st.dataframe(df.style.apply(_bolum_stil, axis=1))
    
    # 7. Metrikler
    st.metric("✅ Tamamlandı", len(bolumler["tamamlandi"]))
    # ... diğer metrikler
```

### Yardımcı Fonksiyonlar

```python
def _gorev_panou_yukle() -> list[dict]:
    """task_board.json yükle."""
    path = Path("data/orchestrator/task_board.json")
    return json.loads(path.read_text(encoding="utf-8"))

def _gorev_bolum_getir(durum: str) -> str:
    """Duruma göre bölüm belirle."""
    if durum == "done":
        return "tamamlandi"
    elif durum in ["aktif", "review", "bekliyor"]:
        return "beklemede"
    elif durum == "plan":
        return "yedek"
    else:  # blocked, reddet, iptal
        return "degerlendirme"

_PANO_BOLUM_RENKLERI: dict[str, str] = {
    "tamamlandi": "#D4F1D4",     # Yeşil
    "beklemede": "#FFF3CD",      # Sarı
    "yedek": "#E8E8E8",          # Gri
    "degerlendirme": "#FFE5E5",  # Kırmızı
}
```

---

## 10. Test Kasları

**Dosya:** `tests/test_admin_pano_board_view.py`

### Kapsam
- ✅ 4 bölüme göre veri hazırlama (4 test)
- ✅ Ajan/aciliyet/tarih filtreleme (4 test)
- ✅ Renk kodlaması (2 test)
- ✅ Metrik hesaplama (2 test)
- ✅ Dosya yönetimi (2 test)
- ✅ Tablo rendering (2 test)
- ✅ Entegrasyon (1 test)

**Sonuç:** 17/17 geçti ✅

---

## 11. Sorun Giderme

### Sıkça Sorulan Sorular

**S: Görevler neden güncellenmemiş?**
- Cevap: Sayfayı refresh et (Ctrl+R) veya Streamlit cache'i temizle
  ```bash
  streamlit cache clear
  ```

**S: Filtreler çalışmıyor mu?**
- Cevap: Filtre değeri "Hepsi"se tümünü göster. "Hepsi" dışı seçilmişse kontrol et:
  - Ajan adı doğru yazıldı mı?
  - Aciliyet formatı P0-P3 arasında mı?

**S: Tablo boş gösteriyor?**
- Cevap: 
  1. `data/orchestrator/task_board.json` var mı?
  2. Filtreler çok kısıtlayıcı mı?
  3. Görev durumları valid mi? (done, aktif, plan, blocked, reddet, iptal)

### Hata Logs'u

Streamlit logs'unda hata görmek:
```bash
tail -f ~/.streamlit/logs/main.log
```

---

## 12. Gelecek Geliştirmeler

- [ ] Real-time WebSocket updates (WebSocket ile live sync)
- [ ] Sprint assignment UI (Sprintte görev atama)
- [ ] Drag & drop status change (Bölüm arası sürükle-bırak)
- [ ] Görev modal (Detaylı görev bilgisi modal'da)
- [ ] Export to CSV/PDF (Rapor ihracı)
- [ ] Gantt chart view (Zaman çizelgesi görünümü)

---

## 13. İlgili Kaynaklar

- [Admin Panel SSOT](../AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md) — Mimari referans
- [Admin Dashboard Hub](../hubs/ADMIN_DASHBOARD_HUB.md) — Görev listesi
- [Task Board JSON](../data/orchestrator/task_board.json) — Veri dosyası
- [Test Suite](../tests/test_admin_pano_board_view.py) — Unit testler

---

**Son Güncelleme:** 2026-09-24  
**Sorumlu:** orkestrator
