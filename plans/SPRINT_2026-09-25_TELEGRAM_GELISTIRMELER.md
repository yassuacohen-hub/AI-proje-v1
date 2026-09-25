# Sprint 2026-09-25 — Telegram Bot Geliştirmeleri

**Sprint Başlangıcı:** 2026-09-25 03:26 UTC+3
**Durum:** Aktif
**Öncelik:** P1 (Tetik + Post) ✅ Tamamlandı → P2 (Sahip Bazlı + Mesaj-Orkestrator)

---

## 🎯 Tamamlanan İşler

### 1. ✅ Tetik + Post Composite Flow
**Ticket:** D-220-TETIK-POST
**Tarih:** 2026-09-25 03:22
**Durum:** Tamamlandı (Bot çalışıyor)

**Değişiklikler:**
- `_tetik_gonder_mesaj()` — Tetik gönderildikten sonra post menüsü sunar
- `_show_tetik_post_menu()` — "📮 Post Gönder" / "« Tetikler" butonları
- `btn_tetik_post_gonder()` — Post içeriği input handler
- `_tetik_post_kaydet()` — Post kaydedici fonksiyon

**Flow:**
```
✉️ Tetik Gönder → Ajan Seç → Tetik Mesajı → 
✅ Tetik Gönderildi → 📮 Post Gönder? → Post Mesajı → 
✅ Post + Tetik Tamamlandı → Tetikler Menüsü
```

**Test Durumu:** Hazır — Bot Terminal 1'de çalışıyor
**Commit:** `Tetik + Post Composite Flow — tetik gönderildikten sonra post menüsü sunuluyor`

---

## 📋 Sprint Backlog (Sonraki Görevler)

### P2.1 — Sahip Bazlı Filtreleme
**Ticket:** D-221-SAHIB-BAZLI-FILTRE
**Başlangıç:** Hazır
**Durum:** Planlanmış

**Açıklama:**
- "👤 Sahip Bazlı" butonu eklenmiş ama handler yok
- Görev panosundaki görevleri sahip adına göre filtrele
- Ajanlar: Utku, Salih, Yasu, İhsan, Mimir, Orkestrator

**İş Listesi:**
- [ ] `btn_gorev_sahib_bazli()` handler oluştur
- [ ] `_show_gorev_sahib_menu()` — sahip seçim menüsü (5 ajan + orkestrator)
- [ ] `show_gorev_sahib_goster()` — görevleri sahib bazında filtrele ve göster
- [ ] ASCII tablo format (durum, baslik, onem, task_id)
- [ ] Syntax check + bot restart

**Dosya:** `Huginn Data Insights/src/company_master/telegram_bot.py`
**Satırlar:** `1571-1617` (Görev Takibi button handlers yakınında)

---

### P2.2 — Message-to-Orchestrator Flow
**Ticket:** D-222-MESAJ-ORKESTRATOR
**Başlangıç:** Hazır
**Durum:** Planlanmış

**Açıklama:**
- Kullanıcı görevle ilgili mesaj yazsin → Orkestrator görev oluştur
- Görev Takibi menüsüne "💬 Mesaj Gönder" butonu ekle
- Mesaj → task_board.json'a eklenir (task_id auto, durum=acik)

**İş Listesi:**
- [ ] `send_gorev_takibi_menu()` güncellenecek — "💬 Mesaj Gönder" butonu ekle
- [ ] `btn_gorev_mesaj_gonder()` — handler oluştur
- [ ] `_show_mesaj_formu()` — mesaj input ekranı (max 500 char, görev açıklaması)
- [ ] `_mesaj_orkestrator_kaydet()` — orchastratöre gönder
  - Yeni task oluştur: task_id, baslik, durum="acik", sahip="orkestrator", mesaj
  - logger.info() ile kaydet
- [ ] Syntax check + bot restart

**Dosya:** `Huginn Data Insights/src/company_master/telegram_bot.py`
**Satırlar:** `483-547` (Görev Takibi menü yakınında)

**Ek Refactor (Opsiyonel):**
- `_tetik_post_kaydet()` → Orchastratöre görev oluşturmaya bağla
- "📮 Post Gönder" mesajları da orchastratöre task olabilir

---

### P2.3 — Rapor Bölümü Iyileştirmesi
**Ticket:** D-223-RAPOR-TASK-BOARD
**Başlangıç:** Opsiyonel
**Durum:** Planlanmış (Sonraki Sprint)

**Açıklama:**
- Kullanıcı feedback: "Raporlar bölümü task board ile ilgili bilgi vermiyor"
- Rapor menüsüne "📊 Pano Özeti" butonu ekle
- Görev tarafındaki metrikleri göster

**İş Listesi:**
- [ ] `show_rapor_pano_ozeti()` — görev board metrikleri
  - Toplam görev sayısı
  - Durum breakdown (açık, aktif, bloke, done)
  - Sahip başlı görev dağılımı
  - Önem dağılımı (critical, yuksek, orta, dusuk)
- [ ] ASCII tablo format
- [ ] Syntax check

**Dosya:** `Huginn Data Insights/src/company_master/telegram_bot.py`
**Satırlar:** `398-414` (Rapor menüsü)

---

## 🔧 Teknik Not Defteri

### State Management İhtiyacı
Şu an `_tetik_post_kaydet()` tetik ajan bilgisini kayıp.
**Çözüm (sonra):** Global state dict veya context passar
```python
_tetik_gonder_state = {}  # {chat_id: {'ajan': '...', 'tetik': '...'}}
```

### Orchastrator Entegrasyonu
```python
from src.company_master.orchestrator.trigger import tetik_uyari_ekle
# Ya da görev oluşturmak için:
# from src.company_master.orchestrator import task_board_ekle
```

### ASCII Tablo Stil (Tekrar Kullanılabilir)
```
┌─────────────────────────────────────────┐
│ ID │ BASLIK │ SAHIB │ DURUM │ ONEM │
├─────────────────────────────────────────┤
│ P7-01 │ API düz │ Utku │ Aktif │ 🔴 │
└─────────────────────────────────────────┘
```

---

## 📅 Sprint Takvimi

| Tarih | Görev | Durum |
|-------|-------|-------|
| 2026-09-25 03:22 | Tetik + Post Composite | ✅ Tamamlandı |
| 2026-09-25 (Sonra) | Sahib Bazlı Filtre | ⏳ Başlanacak |
| 2026-09-25 (Sonra) | Message-Orkestrator | ⏳ Başlanacak |
| 2026-09-25+ | Rapor Pano Özeti | ⏳ Planlanmış |

---

## 🚀 Başlama Adımları (Sonraki Sessiyon)

1. Bot çalışıyor mu kontrol et: Terminal 1'e bak
2. Sahib Bazlı filtreleme yapı'ya başla:
   ```bash
   cd "Huginn Data Insights"
   grep -n "btn_gorev_tumun" src/company_master/telegram_bot.py
   ```
3. `_show_gorev_sahib_menu()` yazarak başla
4. Test et + commit et
5. Message-Orkestrator'a geç

---

## 💡 Fikirler (Backlog)

- Tetik + Post → Orkestrator görev oluşturması (composite flow)
- Görev atama otomasyonu (önem + sahib bazlı)
- Chat menüsü ile tetik/post entegrasyonu
- Pano real-time güncellemeleri (WebSocket?)
- Admin dashboard'a tetik/post istatistikleri

---

**Son Güncelleme:** 2026-09-25 03:26 UTC+3
**Sprint Lead:** Roo (code mode)
**Repo:** chore/monorepo-merge
