# 📋 Dağıtım Checklist — Task Board to Telegram/Chat

## 🎯 Dağıtım Rehberi

Bu checklist, task board'daki görevleri UTKU, YASU ve ORCH'ye Telegram ve Chat üzerinden dağıtmak için kullanılır.

---

## 🔴 ADIM 1: UTKU'ya 5 Görev Dağıtma

### Telegram Dağıtımı
- [ ] **UTKU-01** mesaj gönderildi
- [ ] **UTKU-02** mesaj gönderildi
- [ ] **UTKU-03** mesaj gönderildi
- [ ] **UTKU-04** mesaj gönderildi
- [ ] **UTKU-05** mesaj gönderildi

**Kontrol Noktası:**
- [ ] Tüm 5 mesaj Telegram'da gözüküyor (✓ reaksiyonu aldı mı?)
- [ ] Her mesaj formatı doğru (template match)
- [ ] Tüm linkler çalışıyor

### Chat (Internal Board) Dağıtımı
- [ ] UTKU channel'inde thread açıldı
- [ ] Tüm 5 görev görev kartı olarak yapıştırıldı
- [ ] Deadline ve priorityler görünür
- [ ] UTKU @mentioned edildi (notification)

**Zaman Tahmini:** 15-20 dakika

---

## 🟠 ADIM 2: YASU'ya 5 Görev Dağıtma

### Telegram Dağıtımı
- [ ] **YASU-01** mesaj gönderildi
- [ ] **YASU-02** mesaj gönderildi
- [ ] **YASU-03** mesaj gönderildi
- [ ] **YASU-04** mesaj gönderildi
- [ ] **YASU-05** mesaj gönderildi

**Kontrol Noktası:**
- [ ] Tüm 5 mesaj Telegram'da gözüküyor (✓ reaksiyonu aldı mı?)
- [ ] Her mesaj formatı doğru (template match)
- [ ] Tüm linkler çalışıyor

### Chat (Internal Board) Dağıtımı
- [ ] YASU channel'inde thread açıldı
- [ ] Tüm 5 görev görev kartı olarak yapıştırıldı
- [ ] Deadline ve priorityler görünür
- [ ] YASU @mentioned edildi (notification)

**Zaman Tahmini:** 15-20 dakika

---

## 🟡 ADIM 3: ORCH'ye 5 Görev Dağıtma (Internal Board Only)

Orchestrator görevleri sadece internal board'da dağıtılır.

### Internal Board Dağıtımı
- [ ] **ORCH-01** görev kartı oluşturuldu
- [ ] **ORCH-02** görev kartı oluşturuldu
- [ ] **ORCH-03** görev kartı oluşturuldu
- [ ] **ORCH-04** görev kartı oluşturuldu
- [ ] **ORCH-05** görev kartı oluşturuldu

**Kontrol Noktası:**
- [ ] Tüm 5 görev task board'da "Dağıtıldı" durumunda
- [ ] Her görev kartında owner, deadline, priority var
- [ ] Linked resources/dependencies belirtildi
- [ ] ORCH notification panel update edildi

**Zaman Tahmini:** 10-15 dakika

---

## 🟢 ADIM 4: Task Board Status Güncelleme

### Status Markaları
- [ ] UTKU görevleri → Status: "Dağıtıldı" ✓
- [ ] YASU görevleri → Status: "Dağıtıldı" ✓
- [ ] ORCH görevleri → Status: "Dağıtıldı" ✓

### Board Metadata
- [ ] `distribution_timestamp` kaydedildi (ISO 8601)
- [ ] `distributed_by` alanı: [Your Name]
- [ ] `distribution_channel` kaydedildi (Telegram + Chat)

**Zaman Tahmini:** 5 dakika

---

## 📊 ADIM 5: Dağıtım Özeti Oluşturma

- [ ] **Dağıtım Raporu** oluşturuldu:
  - UTKU: 5 görev ✓
  - YASU: 5 görev ✓
  - ORCH: 5 görev ✓
  - **Toplam:** 15 görev

- [ ] **Dağıtım Saati:** [HH:MM, 25.09.2026]
- [ ] **Platformlar:** Telegram + Chat + Internal Board
- [ ] **Durum:** Tamamlandı

**Dosya:** `DISTRIBUTION_REPORT_25_09_2026.md`

---

## ✅ ADIM 6: Onay & Doğrulama

### UTKU Onayı Bekleme
- [ ] UTKU: Mesaj okundu ve 👍 reaksiyonu aldı
- [ ] UTKU: Chat thread'de "Başladım" mesajı attı
- [ ] UTKU: İlk görev (UTKU-01) başlayacak tarih confirm edildi

**Timeout:** 30 dakika

### YASU Onayı Bekleme
- [ ] YASU: Mesaj okundu ve 👍 reaksiyonu aldı
- [ ] YASU: Chat thread'de "Başladım" mesajı attı
- [ ] YASU: İlk görev (YASU-01) başlayacak tarih confirm edildi

**Timeout:** 30 dakika

### ORCH Onayı Bekleme
- [ ] ORCH: Board'da tüm görevleri görüyor (offline kontrol)
- [ ] ORCH: Status "Dağıtıldı" → "İşlemde" geçmeye hazır
- [ ] ORCH: Dependencies ve blockers tespit edildi

**Timeout:** Gerçek zamanlı (senkron)

---

## 🔴 Sorun Giderim Checklist

Eğer mesaj gönderilmezse:

- [ ] Telegram API token doğrulanıyor
- [ ] Chat endpoint aktif mi? Test et
- [ ] Rate limiting var mı? (60 mesaj/dakika limit)
- [ ] Mesaj formatı valid JSON/Markdown mi?
- [ ] Owner handles (UTKU, YASU, ORCH) sistemde kayıtlı mı?

Eğer onay gelmezse:

- [ ] Notification settings kontrol et
- [ ] Mesaj mute edilmiş mi? (unmute)
- [ ] Network latency? (wait 5 min, retry)
- [ ] Owner offline mu? (fallback: email notice)

---

## 📝 Dağıtım Log Şablonu

Her dağıtımdan sonra aşağıdakileri kaydet:

```markdown
## 📅 Dağıtım: 25.09.2026

**Başlangıç:** 11:00 (Istanbul Time)
**Bitiş:** 11:45

### Dağıtımlar
- ✅ UTKU: 5 görev (UTKU-01 → UTKU-05)
- ✅ YASU: 5 görev (YASU-01 → YASU-05)
- ✅ ORCH: 5 görev (ORCH-01 → ORCH-05)

### Onaylar
- ✅ UTKU: Confirmed @ 11:25
- ✅ YASU: Confirmed @ 11:30
- ✅ ORCH: Confirmed @ 11:35

### Sorunlar
- [Varsa yaz, yoksa "Yok"]

### Sonraki Adım
[Aşama veya görev]
```

---

## 🎯 Görev Dağıtım Şablonları

### 📌 UTKU Görevleri (Araştırma & Analiz)

**UTKU-01:** Kaynak Araştırması
- Platform: Telegram + Chat
- Format: Kompakt (Telegram) + Detaylı (Chat)
- Priority: P1
- Deadline: [+3 gün]

**UTKU-02:** Market Analiz
**UTKU-03:** Kompetitor Karşılaştırması
**UTKU-04:** Trend Raporlaması
**UTKU-05:** Veri Toplamı

---

### 📌 YASU Görevleri (Uygulama & Yapılandırma)

**YASU-01:** Telegram Menu Optimize
- Platform: Telegram + Chat
- Format: Kompakt (Telegram) + Detaylı (Chat)
- Priority: P1
- Deadline: [+2 gün]

**YASU-02:** Chat Interface Fix
**YASU-03:** Bot Configuration Update
**YASU-04:** User Onboarding Flow
**YASU-05:** Analytics Integration

---

### 📌 ORCH Görevleri (Koordinasyon & Kontrol)

**ORCH-01:** Task Board Status Sync
- Platform: Internal Board (async)
- Format: JSON + Status card
- Priority: P0
- Deadline: [Immediate]

**ORCH-02:** Performance Monitoring
**ORCH-03:** Bug Triage & Assignment
**ORCH-04:** Weekly Report Generation
**ORCH-05:** Bottleneck Analysis

---

## ⏱️ Zaman Çizelgesi

```
11:00 — UTKU dağıtımı başlat
11:20 — YASU dağıtımı başlat
11:40 — ORCH dağıtımı (board) başlat
11:50 — Board status güncelleme
12:00 — Onay bekle (UTKU & YASU)
12:30 — Tüm onaylar alındı → Dağıtım tamamlandı
```

---

## 📊 Metrikler & Takip

Dağıtımdan sonra bunları kaydet:

| Metrik | Değer | Hedef |
|--------|-------|-------|
| Dağıtılan Görev | 15 | ≥15 |
| Platform Etkinliği | Telegram + Chat + Board | ✓ |
| Onay Süresi (UTKU) | [XX dakika] | <30 min |
| Onay Süresi (YASU) | [XX dakika] | <30 min |
| Onay Süresi (ORCH) | [XX dakika] | <15 min |
| Toplam Zaman | [XX dakika] | ~45 min |

---

## 🔒 Güvenlik & Uyumluluk

- [ ] Tüm linkler sanitize edildi (SQL injection yok)
- [ ] Sensitive data (API keys, passwords) gizlendi
- [ ] KVKK: Kişisel veriler korumalı
- [ ] Mesajlar audit log'a kaydedildi
- [ ] Encryption: TLS/SSL üzerinden gönderiliyor

---

## ✨ Notlar

1. **Mesaj Formatı:** `chat_brief_template.md` referans al
2. **Timeout:** 30+ dakika sonrası timeout, retry et
3. **Fallback:** Mesaj geçmezse email + ping at
4. **Log:** Tüm dağıtımları `distribution_log.md`'de tut
5. **Sonraki:** Completion reports beklemeye başla

---

**Son Güncelleme:** 25.09.2026
**Hazırlayan:** ORCH / AI Agent
