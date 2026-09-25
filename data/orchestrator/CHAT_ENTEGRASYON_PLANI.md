# Chat Entegrasyon Plani (2026-09-25)

**Amaç:** Her görev teslimi sonrası chat kanalında bulgular ve raporlar belgelemek  
**Format:** Standardize edilmiş brief şablonu + teslim raporu  
**Kanallar:** Telegram (@KAHİN grubu), Chat, WhatsApp  

---

## 1. Chat Kanal Kurgusu

### 1.1 Telegram @KAHİN Grubu
- **Katılımcılar:** @KAHİN (Ürün Sahibi), @Utku, @Yasu, @Orkestrator, @İhsan, @Mimir
- **Amaç:** Görev tetikleme, bloke bildirimi, teslim onayı
- **Frekans:** Günlük 3 saat (09:00, 14:00, 19:00 Istanbul)

### 1.2 Telegram Bildirim Format
```
[TETIK] Task ID: UTKU-04
├─ Başlık: [UI] LTV/CAC kartlarını yaz -> K8 tamamlama (2s)
├─ Sahip: @Utku
├─ Oncelik: P2
├─ Brief: plans/brief_utku_UI-ADMIN-LTV-CAC-27.md
└─ Deadline: 2026-09-26
```

---

## 2. Bulgu Kayit Sureci

### 2.1 Ajan Teslim Bildirimi (Chat → File)
Her görev teslimi sonrası ajan Telegram'da:
```
[TESLIM] Task ID: UTKU-04
├─ Durum: done / review / bloke
├─ Calisma Ozeti: 
│  └─ LTV/CAC kartları yayınlandı, 8 test geçti
├─ Kabul Kriterleri: 
│  ├─ [x] LTV hesapla (günlük/aylık/yıllık)
│  ├─ [x] CAC hesapla (3 ay / tüm zaman)
│  ├─ [x] Trend çiz (son 30 gün)
│  └─ [x] Tier breakdown
├─ Kaynaklar Kullanıldı:
│  └─ web_app.py (lines 3248-3278), admin_ltv_cac.py
├─ Sonuc: OK / BLOKE / BULGULAR
└─ Bulgular Dosyası: data/orchestrator/{task_id}_bulgular_{date}_{ajan}.md
```

### 2.2 Bulgular Dosyası (.md)
```markdown
# Bulgular: {task_id}

**Tarih:** 2026-09-25  
**Ajan:** @Utku  
**Durum:** done / review / bloke  

## Calismalar Ozeti

- LTV/CAC kartları web_app.py'ye eklendi
- 8/8 test geçti (pytest test_admin_ltv_cac.py)
- admin_ltv_cac.py modülü yazıldı (178 satır)

## Kabul Kriterleri Kontrolu

| Kriter | Durum | Kanit |
|--------|-------|-------|
| LTV hesapla | PASS | lines 3255-3265 |
| CAC hesapla | PASS | lines 3266-3275 |
| Trend (30 gün) | PASS | test: test_ltv_trend |
| Tier breakdown | PASS | test: test_ltv_by_tier |

## Acik Sorular / Blokajlar

- Sorular yok ✓
- Blokaj yok ✓

## Tavsiyeler

1. Sonraki görev (UI-ADMIN-KVKK-MODU-26) başlatılabilir
2. UTKU-05 (API-ADMIN-MFA-26) review'unda, bulgular bekleniyor

## Kod Ornekleri

```python
# web_app.py:3253 - LTV endpoint
def api_admin_ltv_cac(...):
    return {"ltv": 450, "cac": 75, "ratio": 6.0}
```

---

Dosya: `data/orchestrator/UTKU-04_bulgular_2026-09-25_utku.md`
```

---

## 3. Rapor Dosyası (.md)
```markdown
# Rapor: {task_id}

**Tarih:** 2026-09-25 14:30 Istanbul  
**Ajan:** @Utku  
**Teslim Saati:** 14:30  

## Yapilan Degisiklikler

1. **web_app.py** (lines 3248-3278)
   - Yeni endpoint: `/api/admin/ltv-cac`
   - GET method, `require_admin` dependency
   - LTV/CAC calculation, trend, tier breakdown

2. **src/company_master/ltv_cac.py** (NEW)
   - `calculate_ltv()` - müşteri yaşam boyu değer
   - `calculate_cac()` - kazanım maliyeti
   - `ltv_cac_trend()` - 180 gün trend
   - `ltv_cac_by_tier()` - tier breakdown
   
3. **web_dashboard/tabs/admin_panel.py** (lines 3210-3240)
   - `render_ltv_cac_tab()` - UI tab
   - st.metric kartlar (LTV, CAC, Ratio)
   - st.line_chart (trend)
   - st.bar_chart (tier breakdown)

## Test Sonuçlari

```
$ pytest tests/test_admin_ltv_cac.py -v
test_ltv_calculation PASSED
test_cac_calculation PASSED
test_ltv_cac_ratio PASSED
test_ltv_trend PASSED
test_ltv_by_tier PASSED
test_ui_rendering PASSED
test_edge_cases PASSED
test_database_missing PASSED
========== 8 passed in 2.34s ==========
```

## Proof of Work

- **Commit:** abc1234def5678
- **Branch:** chore/monorepo-merge
- **Files Changed:** 3
- **Lines Added:** 287
- **Test Coverage:** 8/8 (100%)

---

Dosya: `data/orchestrator/UTKU-04_rapor_2026-09-25_utku.md`
```

---

## 4. Chat Standart Sablonlari

### 4.1 Brief Şablonu (chat_brief_template.md)
```markdown
# Brief: {task_id}

## Ozet
- **Gorev:** {baslik}
- **Sahip:** @{ajan}
- **Oncelik:** {oncelik}
- **Deadline:** {deadline}

## Kabul Kriterleri
- [ ] Kriter 1 kontrol et
- [ ] Kriter 2 kontrol et
- [ ] Kriter 3 kontrol et

## Kaynaklar
- [SSOT] plans/brief_{ajan}_{task_id}.md
- [Kod] {dosya_path}:{line_range}
- [Test] tests/test_{task_area}.py

## Implementasyon Adımlari
1. Adım 1
2. Adım 2
3. Adım 3

## Proof of Work
- Test: pytest geçti (N/N)
- Kod: {N} satır, {M} fonksiyon
- Belge: {dosya_path}

## Chat Kontrol
Teslim sonrası @KAHİN'e:
- [x] Bulgular yazıldı
- [x] Rapor tamamlandı
- [x] Acık sorular cevaplandı
```

### 4.2 Teslim Kontrol Listesi (per-task)
```
[TESLIM KONTROL] {task_id}

Adım 1: Teslim Bildirimi
- [ ] Chat'e @KAHİN mesajı yaz (formatı: 2.2)
- [ ] Bulgular dosyası oluştur

Adım 2: Bulguları Belgelemek
- [ ] {task_id}_bulgular_{date}_{ajan}.md yazıldı
- [ ] Kabul kriterleri tablosu dolduruldu
- [ ] Açık sorular/blokajlar listelenmiş

Adım 3: Rapor Tamamlama
- [ ] {task_id}_rapor_{date}_{ajan}.md yazıldı
- [ ] Test sonuçları kaydedildi
- [ ] Proof of Work (commit/lines/coverage) hazır

Adım 4: Chat Onay
- [ ] KAHİN tarafından okundu (@KAHİN mesajına reply)
- [ ] Sorular varsa cevaplandı
- [ ] Sonraki görev tetiklenme sırası kontrol edildi

Adım 5: task_board.json Guncelleme
- [ ] durum: "done" / "review" / "bloke" güncellendi
- [ ] bitis: ISO timestamp kaydedildi
- [ ] bulgular dosyası yolu eklendi
```

---

## 5. Gunluk Chat Sinkronizasyonu

### 5.1 Sabah Sync (09:00 Istanbul)
```
@KAHİN grubuna:
"Iyi gunler! Gunun hedefleri:
- UTKU-04 (UI-LTV-CAC) baslansin
- YASU-02 (API-KAYNAK-SAGLIK) kontrol edilesin
- Bloke gorevler: Yok

Bugün hedefi: 3 gorev tamamlansin"
```

### 5.2 Midday Check (14:00 Istanbul)
```
"Midway rapor:
- UTKU-04: 60% tamamlanmis
- YASU-02: Acık soru var (Telegram'da sordum)
- ORCH-01: Planında kalıyor

Aksam hedefi: UTKU-04 teslim + YASU-02 cevap"
```

### 5.3 Aksam Kapanisi (19:00 Istanbul)
```
"Gunluk ozet:
- UTKU-04: DONE (bulgular: path)
- YASU-02: DONE (bulgular: path)
- ORCH-01: Devam (bekleniyor)

Yarinki hedefler:
- UTKU-05 (API-MFA) kapat
- ORCH-02 basla"
```

---

## 6. Bloke Gorevler Eskalasyon

### 6.1 Tetik
- **2 saat geçti (P0/P1):** KAHİN'e @mention uyarı
- **4 saat geçti:** Ajan değiştir (fallback agent)
- **8 saat geçti:** Task taşı (archive → backlog)

### 6.2 Bloke Bildirimi Sablonu
```
@KAHİN {task_id} bloke!

Bloke Süresi: 3h 45m
Sebep: API-ADMIN-AKTIVITE-YAZ-14 bitmedi (dependency)
Bağımlılık: UTKU-02 (VERI-ADMIN-AKTIVITE-LOG-13)
Bağımlı Task Durumu: review (bulgular bekleniyor)

Seçenekler:
1. UTKU-02'nin bulgularını sor
2. Görev sirasini değiştir
3. Ajan değiştir (fallback)
```

---

## 7. Implementasyon Checklistesi

- [ ] Brief şablonu (chat_brief_template.md) yazıldı
- [ ] Bulgular şablonu (chat_bulgular_template.md) yazıldı
- [ ] Rapor şablonu (chat_rapor_template.md) yazıldı
- [ ] Teslim kontrol listesi (teslim_kontrol_template.md) yazıldı
- [ ] Günlük sync cron job kuruldu
- [ ] Bloke eskalasyon rules kodlandı (trigger.py)
- [ ] Chat kanalı entegrasyonu test edildi
- [ ] İlk 3 görev chat flow test edildi

---

**Güncelleme:** 2026-09-25 08:59 UTC  
**Sorumlu:** Orkestrator (Bot)  
**Onay:** KAHİN (Ürün Sahibi)
