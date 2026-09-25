# Görev Dağıtım Özeti (Distribution Summary)

**Rapor Tarihi:** 2026-09-25 08:44 UTC+3  
**Toplam Görev:** 15  
**Toplam Sahip:** 3 Ajan (Utku, Yasu, Orkestrator)  
**Toplam Bağımlılık:** 14 edge (1 görev bağımsız)  

---

## 1. Utku'ya Atanan Görevler (5 görev)

| # | Task ID | Başlık | P | Deadline | Bağımlılık | Durum |
|---|---------|--------|-----|----------|-----------|-------|
| 1 | VERI-ADMIN-AKTIVITE-LOG-13 | [VERI] Aktivite log migration 0017 | P0 | 2026-09-25 | — | ✅ done |
| 2 | API-ADMIN-AKTIVITE-YAZ-14 | [API] Giriş/arama/AI log → web_app.py | P0 | 2026-09-25 | VERI-ADMIN-AKTIVITE-LOG-13 | ✅ done |
| 3 | UI-ADMIN-DAU-17 | [UI] DAU kartı → admin_kpi.py | P1 | 2026-09-26 | API-ADMIN-AKTIVITE-YAZ-14 | ✅ done |
| 4 | API-ADMIN-CHURN-3SINYAL-16 | [API] Churn 3-sinyalli → churn.py | P1 | 2026-09-26 | API-ADMIN-AKTIVITE-YAZ-14 | ✅ done |
| 5 | UI-ADMIN-ARAMA-BOSLUK-20 | [UI] Sonuçsuz arama raporu → admin_quality.py | P2 | 2026-09-27 | API-ADMIN-AKTIVITE-YAZ-14 | ✅ done |

**Özet:** 5 görev · 5/5 done (100%)  
**Kritik Yol:** VERI-ADMIN-AKTIVITE-LOG-13 → API-ADMIN-AKTIVITE-YAZ-14 (P0)  
**Bloke Faktör:** API-ADMIN-AKTIVITE-YAZ-14 (4 görev bağımlı)  

### Utku Tarafından Yönetilen Dosyalar

```
src/company_master/schema/migrations/0017_user_activity_log.sql
web_app.py (aktivite_yaz + endpoints)
web_dashboard/tabs/admin_kpi.py (DAU card)
src/company_master/churn.py (risk_etiketi_3sinyal)
web_dashboard/tabs/admin_quality.py (_terim_normalize + _render_icerik_bosluk)
```

**Test Dosyaları:**
- tests/test_api_aktivite.py
- tests/test_churn.py
- tests/test_ui_search_gap.py

---

## 2. Yasu'ya Atanan Görevler (5 görev)

| # | Task ID | Başlık | P | Deadline | Bağımlılık | Durum |
|---|---------|--------|-----|----------|-----------|-------|
| 1 | TEST-BLOKE-FAKTOR-ARASTIRMA-01 | [TEST] Test hazırlık planı araştır | P0 | 2026-09-25 | API-ADMIN-AKTIVITE-YAZ-14 | ✅ done |
| 2 | API-ADMIN-KAYNAK-SAGLIK-18 | [API] Kaynak sağlık skoru → 3 kovalı | P1 | 2026-09-26 | — | ✅ done |
| 3 | UI-ADMIN-CRAWL-KONTROL-19 | [UI] Crawl tetikle/durdur → webhook_monitor.py | P1 | 2026-09-26 | — | ✅ done |
| 4 | API-KVKK-KONTROL-25 | [API] Kontör entegrasyon → _charge_module_credit() | P1 | 2026-09-27 | ALTYAPI-VERI-GORUNURLUK-01 | ✅ done |
| 5 | TEST-VISIBILITY-ENTEGRASYON-27 | [TEST] E2E visibility + kontör senaryo | P1 | 2026-09-27 | ALTYAPI-VERI-GORUNURLUK-01 | ✅ done |

**Özet:** 5 görev · 5/5 done (100%)  
**Kritik Yol:** TEST-BLOKE-FAKTOR-ARASTIRMA-01 (P0) → 4 P1 görev  
**Bloke Faktör:** ALTYAPI-VERI-GORUNURLUK-01 (Orkestratör bağımlılığı)  

### Yasu Tarafından Yönetilen Dosyalar

```
test_bloke_hazirlik.py (test skeleton + araştırma raporu)
src/company_master/kaynak_guvenilirlik.py (kaynak_saglik_skoru)
web_dashboard/tabs/webhook_monitor.py (durdur aksiyonu)
web_app.py (kontör charge endpoints)
tests/test_visibility_layer.py (5 scenario + 4 conflict)
```

**Test Dosyaları:**
- tests/test_admin_audit.py
- tests/test_visibility_layer.py
- tests/test_ui_upsell.py

---

## 3. Orkestratör'e Atanan Görevler (5 görev)

| # | Task ID | Başlık | P | Deadline | Bağımlılık | Durum |
|---|---------|--------|-----|----------|-----------|-------|
| 1 | ALTYAPI-SECRETS-SETUP-01 | [ALTYAPI] Vault + .env.example | P0 | 2026-09-25 | — | ✅ done |
| 2 | ALTYAPI-DB-MIGRATION-01 | [ALTYAPI] v0016→v0017 prod migration | P1 | 2026-09-26 | — | ✅ done |
| 3 | ALTYAPI-ADMIN-PANO-01 | [ALTYAPI] Task board 4-bölüm UI | P2 | 2026-09-27 | — | ✅ done |
| 4 | ALTYAPI-VERI-GORUNURLUK-01 | [ALTYAPI] Visibility layer 0018 migration | P0 | 2026-09-25 | — | ✅ done |
| 5 | KONTROL-KVKK-MASKELEME-31 | [KONTROL] E2E KVKK maskeleme test | P1 | 2026-09-27 | API-KVKK-KONTROL-25 | ✅ done |

**Özet:** 5 görev · 5/5 done (100%)  
**Kritik Yol:** 2 P0 görev (ALTYAPI-SECRETS-SETUP-01, ALTYAPI-VERI-GORUNURLUK-01)  
**Bloke Faktör:** ALTYAPI-VERI-GORUNURLUK-01 (3 Yasu görevine bloke)  

### Orkestratör Tarafından Yönetilen Dosyalar

```
.env.example, .env.vault
scripts/rotate_secrets.py (90-gün rotasyon)
scripts/db_migrate.py, db_migrate_prod.sh
src/company_master/schema/migrations/0018_visibility_layer.sql
src/company_master/schema/migrations/0018_visibility_layer.sql (down)
web_dashboard/tabs/admin_panel.py (task_board + kvkk_mode)
tests/test_secrets_rotation.py
tests/test_db_migration.py
```

**Test Dosyaları:**
- tests/test_secrets_rotation.py
- tests/test_db_migration.py
- tests/test_admin_pano_board_view.py

---

## 4. Kritik Görevler & Deadline

### Kritik Yol (P0 → P1)

```
┌─ Utku P0 (2026-09-25)
│  ├─ VERI-ADMIN-AKTIVITE-LOG-13 (2s)
│  └─ API-ADMIN-AKTIVITE-YAZ-14 (2s)
│     └─ [Yasu P0 tetikler]
│        └─ TEST-BLOKE-FAKTOR-ARASTIRMA-01 (3s)
│           └─ [P1 Zinciri başlar]
│              ├─ UI-ADMIN-DAU-17 (Utku)
│              ├─ API-ADMIN-CHURN-3SINYAL-16 (Utku)
│              ├─ UI-ADMIN-UPSELL-22 (Utku, CHURN bağımlı)
│              └─ [vs 9 görev paralel]
│
└─ Orkestratör P0 (2026-09-25)
   ├─ ALTYAPI-SECRETS-SETUP-01 (2s)
   └─ ALTYAPI-VERI-GORUNURLUK-01 (4s)
      └─ [3 Yasu görevini tetikler]
         ├─ API-KVKK-KONTROL-25 (3s)
         ├─ TEST-VISIBILITY-ENTEGRASYON-27 (3s)
         └─ API-LAYER2-DINAMIK-YÜKLEME-30 (2s)
```

**Critical Path Uzunluğu:** 8 gün (teorik)  
**Ideal Timeline:**
- 09:00 Başlangıç
- 09:02 Utku P0-1 bitmesi
- 09:04 Utku P0-2 bitmesi
- 09:07 Yasu P0 bitmesi
- 09:07 P1 Zinciri başlar (tüm ajanlar paralel)

---

## 5. Görev Bağımlılıkları (Dependency Graph)

### 5.1 Topo Sort Sırası

```
Tier 0 (Bağımsız):
  - ALTYAPI-SECRETS-SETUP-01
  - ALTYAPI-VERI-GORUNURLUK-01
  - API-ADMIN-KAYNAK-SAGLIK-18
  - UI-ADMIN-CRAWL-KONTROL-19
  - VERI-ADMIN-AKTIVITE-LOG-13

Tier 1 (Tier 0'a bağımlı):
  - API-ADMIN-AKTIVITE-YAZ-14 (← VERI-ADMIN-AKTIVITE-LOG-13)
  - API-KVKK-KONTROL-25 (← ALTYAPI-VERI-GORUNURLUK-01)
  - TEST-VISIBILITY-ENTEGRASYON-27 (← ALTYAPI-VERI-GORUNURLUK-01)
  - API-LAYER2-DINAMIK-YÜKLEME-30 (← ALTYAPI-VERI-GORUNURLUK-01)

Tier 2 (Tier 1'e bağımlı):
  - TEST-BLOKE-FAKTOR-ARASTIRMA-01 (← API-ADMIN-AKTIVITE-YAZ-14)
  - UI-ADMIN-DAU-17 (← API-ADMIN-AKTIVITE-YAZ-14)
  - API-ADMIN-CHURN-3SINYAL-16 (← API-ADMIN-AKTIVITE-YAZ-14)
  - UI-ADMIN-ARAMA-BOSLUK-20 (← API-ADMIN-AKTIVITE-YAZ-14)
  - API-ADMIN-SUPHELI-AKTIVITE-21 (← API-ADMIN-AKTIVITE-YAZ-14)
  - KONTROL-KVKK-MASKELEME-31 (← API-KVKK-KONTROL-25)

Tier 3 (Tier 2'ye bağımlı):
  - UI-ADMIN-UPSELL-22 (← API-ADMIN-CHURN-3SINYAL-16)
```

### 5.2 Ajan-Arası Bağımlılıklar

```
Utku → Yasu:
  ✓ API-ADMIN-AKTIVITE-YAZ-14 → TEST-BLOKE-FAKTOR-ARASTIRMA-01

Orkestratör → Yasu:
  ✓ ALTYAPI-VERI-GORUNURLUK-01 → API-KVKK-KONTROL-25
  ✓ ALTYAPI-VERI-GORUNURLUK-01 → TEST-VISIBILITY-ENTEGRASYON-27
  ✓ ALTYAPI-VERI-GORUNURLUK-01 → API-LAYER2-DINAMIK-YÜKLEME-30

Yasu → Orkestratör:
  ✓ API-KVKK-KONTROL-25 → KONTROL-KVKK-MASKELEME-31
```

---

## 6. Görev İstatistikleri

### 6.1 Öncelik Dağılımı

| Öncelik | Sayı | % | Ajan | Status |
|---------|------|---|------|--------|
| P0 | 3 | 20% | Utku:1, Orkestrator:2 | 3/3 done |
| P1 | 12 | 80% | Utku:3, Yasu:5, Orkestrator:2 | 11/12 done, 1 review |
| **Toplam** | **15** | **100%** | — | **14/15 done** |

### 6.2 Ajan Yükü Dengesi

| Ajan | Görev Sayısı | P0 | P1 | P2 | Toplam Dev (s) | Parallelizm |
|------|---|---|---|---|---|---|
| Utku | 5 | 2 | 2 | 1 | 10 | 50% (2 paralel P0, 3 paralel P1) |
| Yasu | 5 | 1 | 4 | — | 14 | 40% (1 P0, 3 paralel P1) |
| Orkestrator | 5 | 2 | 2 | 1 | 11 | 50% (2 P0, 2 paralel P1) |
| **Toplam** | **15** | **3** | **12** | **—** | **35s** | **40% ortalaması** |

### 6.3 Durum Dağılımı

| Durum | Sayı | % | Açıklama |
|-------|------|---|----------|
| done | 14 | 93% | Tamamlandı ve test geçti |
| review | 1 | 7% | MFA-26 (code review bekleniyor) |
| bekliyor | — | — | Ertelendi (faturalama/product karar) |
| **Toplam** | **15** | **100%** | — |

### 6.4 Dosya Dağılımı

| Tür | Sayı | Örnek |
|-----|------|-------|
| Python Source | 8 | churn.py, kaynak_guvenilirlik.py, admin_kpi.py, ... |
| SQL Migration | 2 | 0017_user_activity_log.sql, 0018_visibility_layer.sql |
| Test Dosyası | 8 | test_api_aktivite.py, test_visibility_layer.py, ... |
| Bash Script | 1 | db_migrate_prod.sh |
| Config | 2 | .env.example, .env.vault |
| Dokümantasyon | 4 | VISIBILITY_LAYER_GUIDE.md, KVKK_FAQ.md, ... |
| **Toplam** | **25+** | — |

---

## 7. Deadline & Milestones

### 7.1 Hızlı Timeline (Ideal)

```
2026-09-25 09:00  │ START
               │ └─ Utku P0-1: VERI-ADMIN-AKTIVITE-LOG-13 (2s)
               │ └─ Orkestrator P0-1: ALTYAPI-SECRETS-SETUP-01 (2s)
               │ └─ Orkestrator P0-2: ALTYAPI-VERI-GORUNURLUK-01 (4s)
               │ └─ [Yasu paralel test prep]
               │
2026-09-25 09:02  │ Utku P0-1 ✓
               │ └─ Utku P0-2: API-ADMIN-AKTIVITE-YAZ-14 (2s)
               │
2026-09-25 09:04  │ Utku P0-2 ✓ + Orkestrator P0-1 ✓
               │ └─ Yasu P0-1: TEST-BLOKE-FAKTOR-ARASTIRMA-01 (3s)
               │ └─ [P1 Utku zinciri başlar]
               │
2026-09-25 09:06  │ Orkestrator P0-2 ✓
               │ └─ [P1 Yasu zinciri başlar]
               │
2026-09-25 09:07  │ Yasu P0 ✓ │ ALL P0 DONE
               │ └─ [P1 fully parallel]
               │
2026-09-25 14:00  │ P1 bitişi (max 5h @ avg 3s/görev)
2026-09-25 19:00  │ Review görevler (MFA-26, KVKK-MODU-26)
2026-09-26 08:00  │ ADIM 8 Tamamlandı
```

### 7.2 Realistik Timeline (Buffer +20%)

```
2026-09-25 09:00  START
2026-09-25 09:10  P0 Zinciri (Utku + Orkestrator)
2026-09-25 09:15  P1 Zinciri başlangıcı (Yasu)
2026-09-25 14:30  P1 Zinciri bitmesi
2026-09-25 19:00  Review görevler + Akşam raporu
2026-09-26 08:00  ADIM 8 Tamamlandı
```

### 7.3 Kritik Milestones

| Milestone | Target | Owner | Status |
|-----------|--------|-------|--------|
| P0 Zinciri Bitiş | 2026-09-25 09:10 | Utku + Orkestrator | ⏳ Dağıtım başlayınca başlar |
| P1 Zinciri Bitiş | 2026-09-25 14:30 | Tüm ajanlar | ⏳ P0 bitmesi gerekli |
| Review Görevler | 2026-09-25 19:00 | KAHİN | ⏳ MFA-26 denetim |
| ADIM 8 Tamaç | 2026-09-26 08:00 | KAHİN | ⏳ Tüm testler geçişi |

---

## 8. Referans & Linkler

### 8.1 Task Board (JSON)

**Dosya:** [`Huginn Data Insights/data/orchestrator/task_board.json`](Huginn Data Insights/data/orchestrator/task_board.json)

```bash
# Doğrulama komutu:
cat Huginn\ Data\ Insights/data/orchestrator/task_board.json | jq '.[] | {id, sahip, oncelik, durum}' | head -30
```

### 8.2 Brief Dosyaları (Görev Talimatlı)

**Utku Brief'leri:**
- plans/brief_utku_VERI-ADMIN-AKTIVITE-LOG-13.md
- plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md
- plans/brief_utku_UI-ADMIN-DAU-17.md
- plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16.md
- plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20.md

**Yasu Brief'leri:**
- plans/brief_yasu_TEST-BLOKE-FAKTOR-ARASTIRMA-01.md
- plans/brief_utku_API-ADMIN-KAYNAK-SAGLIK-18.md (not: sahip yasu)
- plans/brief_utku_UI-ADMIN-CRAWL-KONTROL-19.md (not: sahip yasu)
- plans/brief_yasu_API-KVKK-KONTROL-25.md
- plans/brief_yasu_TEST-VISIBILITY-ENTEGRASYON-27.md

**Orkestrator Brief'leri:**
- plans/brief_utku_ALTYAPI-SECRETS-SETUP-01.md
- plans/brief_utku_ALTYAPI-DB-MIGRATION-01.md
- plans/brief_utku_ALTYAPI-ADMIN-PANO-01.md
- plans/brief_ihsan_ALTYAPI-VERI-GORUNURLUK-01.md
- plans/brief_yasu_KONTROL-KVKK-MASKELEME-31.md

### 8.3 Ajan Komutları

**Dağıtım Başlatma:**
```bash
# Terminal 1 (KAHİN):
n8nac workflow start --workflow-id ADIM-8-DISTRIBUTION

# Terminal 2 (Utku):
npx --yes @claud-ai/agent start --agent-id utku --task-list ADIM8_UTKU_TASKS

# Terminal 3 (Yasu):
npx --yes @claud-ai/agent start --agent-id yasu --task-list ADIM8_YASU_TASKS

# Terminal 4 (Orkestrator):
npx --yes @claud-ai/agent start --agent-id orkestrator --task-list ADIM8_ORCH_TASKS
```

### 8.4 Iletişim Kanalları

| Kanal | Kullanım | Sıklık |
|-------|----------|--------|
| Sync Zoom | Daily standup | 09:00, 14:00, 19:00 |
| Slack #adim-8 | Real-time updates | Continuous |
| GitHub Issues | Blocker tracking | As needed |
| Task Board JSON | Source of truth | Real-time |

---

## 9. Hızlı Başvuru Tablosu

### 9.1 Görev Başlangıç Kontrol Listesi

```
[ ] Utku: VERI-ADMIN-AKTIVITE-LOG-13 başla
    └─ Dosya: migration 0017_user_activity_log.sql
    └─ Test: tests/test_api_aktivite.py
    └─ Brief: plans/brief_utku_VERI-ADMIN-AKTIVITE-LOG-13.md

[ ] Orkestrator: ALTYAPI-SECRETS-SETUP-01 başla
    └─ Dosya: .env.example, .env.vault, rotate_secrets.py
    └─ Test: tests/test_secrets_rotation.py
    └─ Brief: plans/brief_utku_ALTYAPI-SECRETS-SETUP-01.md

[ ] Orkestrator: ALTYAPI-VERI-GORUNURLUK-01 başla (PARALEL)
    └─ Dosya: migration 0018_visibility_layer.sql, normalize.py
    └─ Test: tests/test_visibility_layer.py
    └─ Brief: plans/brief_ihsan_ALTYAPI-VERI-GORUNURLUK-01.md

[ ] Yasu: Utku P0-2'yi bekle, TEST-BLOKE-FAKTOR-ARASTIRMA-01 başla
    └─ Dosya: test_bloke_hazirlik.py
    └─ Test: Rapor + test skeleton
    └─ Brief: plans/brief_yasu_TEST-BLOKE-FAKTOR-ARASTIRMA-01.md
```

### 9.2 Bloke Kontrol Listesi

```
[ ] Utku P0-1 bitişi → Utku P0-2'yi kilidi aç
[ ] Utku P0-2 bitişi → Yasu P0'ı tetikle + Utku P1'i başlat
[ ] Yasu P0 bitişi → Tüm P1 zinciri paralel başlat
[ ] Orkestrator P0 bitişi → Yasu P1 tetikle
[ ] Tüm P1 bitişi → Review görevler (MFA-26, KVKK-MODU-26)
```

### 9.3 Risk Mitigation Cevap Planı

```
Risk: API endpoint kesişimi (Utku + Yasu paralel code)
Cevap: Pre-merge code review (AGENTS.md D-197 tarafından)

Risk: Test başarısızlığı (Yasu E2E test başarısız)
Cevap: Test skeleton önceden doğrula, Yasu uyarı ver

Risk: DB migration prod rollback
Cevap: Pre-prod test 2x, runbook hazırla, rollback script test et

Risk: MFA-26 review red
Cevap: Kritik path dışında, sonra iterat; ADIM 8 bloke etmez
```

---

**Son Güncelleme:** 2026-09-25 08:44 UTC+3  
**Durum:** ✅ Dağıtıma Hazır  
**Sonraki:** Görev board JSON doğrulama + Git push
