# Admin Panel UI Zincir Tasarımı (2026-09-20)

**Hazırlayanı:** Orkestratör İhsan  
**Hedef:** Admin panel işlerine ağırlık; UTKU kodlamaya yüklü; zincir görev kurmak  
**Öncelik:** KAHİN P0/P1 ağırlıklı (menu, profil, logout senkrosu)

---

## 1. Mevcut Durum (Pano + Posta Kutusu Snapshot)

### Tamamlanan Görevler (Admin Panel Bileşenlerinden)
- ✅ **UI-MENUTREE-02** (done, 2026-09-20T08:10:46) — Sol menu ağacı düzeltme
- ✅ **UI-PROFILMENU-POPOVER-02** (done, 2026-09-20T07:37:55) — st.popover geçişi
- ✅ **UI-PROFILMENU-01** (done, 2026-09-20T05:55:02) — Profil menu yazımı
- ✅ **ADMIN-UX-LOGOUT-01** (done, 2026-09-19T16:22:23) — Logout senkronizasyonu

### Açık Posta Kutuları (Bekleyen Görevler)
| Ajan | Task ID | Başlık | P | Durum | Tetik |
|------|---------|--------|---|-------|-------|
| UTKU (Üretim) | ALTYAPI-TEST-FAILURE-FIX-01 | 4 pre-existing test failure düzelt | P1 | plan | data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_brif... |
| SALİH (Test) | TEST-KAPSAM-OLCUM-01 | Mevcut test kapsamını ölç ve raporla | P2 | plan | data/orchestrator/TEST-KAPSAM-OLCUM-01_brif... |
| YASU (Denetim) | ORKESTRA-STALE-TEMIZLIK-01 | Stale görevleri temizle | P1 | **review** | (teslim için onay bekliyor) |
| İHSAN (Orkestratör) | ORKESTRA-VAULT-TEKRAR-01 | Vault isim tekrarlarını denetle | P2 | plan | data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_brif... |

---

## 2. Zincir Tasarımı (Bağımlılık Grafiği + Sıra)

### Kritik Path: Admin Panel UI Serti

```
ALTYAPI-TEST-FAILURE-FIX-01 (UTKU, 2s, P1)
    ↓
UI-MENUTREE-02 (UTKU, 4s, P1) ✅
    ↓
UI-PROFILMENU-POPOVER-02 (UTKU, 2s, P2) ✅
    ↓
ORKESTRA-VAULT-TEKRAR-01 (İHSAN, 2s, P2)
    ↓
ADMIN-UX-LOGOUT-01 (İHSAN + UI senkro, 2s, P0) ✅
```

### Paralel Fırsatlar
- **ALTYAPI-TEST-FAILURE-FIX-01** ← → **Diğer TEST- görevleri**: Bağımlı değil, paralel çalışabilir
- **SALİH TEST-KAPSAM-OLCUM-01:** UTKU işlerine bağımlı değil, hemen başlayabilir
- **YASU inceleme (ORKESTRA-STALE-TEMIZLIK-01):** Onay sonrası raporlama zinciri YASU → İHSAN devam

---

## 3. Detaylı Görev Tanımları (D-57 Kalıbı)

### 3.1 ALTYAPI-TEST-FAILURE-FIX-01
**Başlık (D-57):** `[ALTYAPI] düzelt 4 pre-existing test failure → data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md (2s)`

**Ön Koşul:**
- 4 test failure'ın root cause tespiti (DB şema, app.py eksikliği, vb.)
- Failure listesi: task_board.json 'not' alanında referansi yapılmış

**İş Maddeleri:**
1. Pano'dan 4 failure görev bulundu ve analiz edil
2. Her failure için kök neden raporlandı
3. İlgili dosyalar düzeltildi veya kaydedildi (gerçek fix / çalışabilmek için bypass değil)
4. Tesit suite çalıştırıldı: `pytest tests/ -q` → ≥3970 passed, <5 failed
5. Rapor yazıldı: durum tablosu + before/after metrikleri

**Çıktı:**
- **Dosya:** `data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md`
- **Test Sayısı:** ≥3970 (mevcut 3972)
- **Kod Dosyaları:** Etkilenen modüller (şu an belirlenmemiş)

**Kabul Kriterleri:**
- [ ] Rapor yazıldı, D-67 formatında (Ne yapıldı / Değişen dosyalar / Test sonuçları / Bulgular / Eksik/erteleme)
- [ ] Test suite yeşil
- [ ] Kilit disiplini: değiştirilen dosya bir kilitli mi, değilse notlandırıldı

**Sonraki:** UI-MENUTREE-02 (zincirde 2. halka)

---

### 3.2 UI-MENUTREE-02
**Başlık (D-57):** `[UI] Sol menu ağacı düzelt → web_dashboard/tabs/__init__.py (4s)`

**Durum:** ✅ DONE (2026-09-20T08:10:46)

**Teslim Özeti (UTKU):**
> Menu ağacı yeniden yapılandırıldı: 6 üst/16 alt sekme (sınırda), 8 sekme menüsüz (arama/executive/performans/webhook/dlq/yenileme/ayarlar/yukleme), ayarlar profil menüsüne taşınmış. Tüm TabTamin gerçek dosyalara işaret ediyor. test_sekme_kapsama 65 PASSED, test_dashboard_nav+test_tabs_ia 103 PASSED, test_nav_ia04 güncellendi 8 PASSED. Kodlama denetim temiz, streamlit_restart yapıldı.

**Test Sonuçları:**
- test_sekme_kapsama: 65 PASSED
- test_dashboard_nav: *
- test_tabs_ia: * | toplam 103 PASSED
- test_nav_ia04: 8 PASSED
- **Toplam:** 176 PASSED

**Sonraki:** UI-PROFILMENU-POPOVER-02

---

### 3.3 UI-PROFILMENU-POPOVER-02
**Başlık (D-57):** `[UI] native st.popover'a taşı → src/company_master/ui/components/profil_menu.py (2s)`

**Durum:** ✅ DONE (2026-09-20T07:37:55)

**Teslim Özeti (UTKU):**
> profil_menu.py: CSS/div popover yerine Streamlit 1.62+ st.popover kullanıldı. session_state yazılmaz, form girdi yok, avatar monokrom baş harf (emoji yok), dark-mode uyumlu. 8/8 test PASSED. Kodlama denetim temiz. Streamlit restart yapıldı. Full suite: 3910 passed, 8 pre-existing failure, 16 pre-existing error (companies table / app.py eksiklikleri — ilgisi yok).

**Test Sonuçları:**
- Profil menu kompabilitesi: 8 PASSED

**Sonraki:** ORKESTRA-VAULT-TEKRAR-01

---

### 3.4 ORKESTRA-VAULT-TEKRAR-01
**Başlık (D-57):** `[ORKESTRA] denetle vault isim tekrarları → data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-20_orkestrator.md (2s)`

**Ön Koşul:**
- 3 dosyada isim tekrarları tespit (AGENTS.md, ANA_KURALLAR.md, AGENT_SYNC.md)
- Root worktree vs AI proje v1/ vault tekrarı

**İş Maddeleri:**
1. Vault dosyaları listele ve root dosyalarla karşılaştır
2. İçerik aynı mı, stale mi, bağımsız mı analiz et
3. Kök neden: niye çoğaldı (vault → root, root → vault, mirror?)
4. Karar: single-source-of-truth (root SSOT veya vault SSOT?)
5. Rapor yaz: karar tablosu + hazırlık notları

**Çıktı:**
- **Dosya:** `data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-20_orkestrator.md`
- **Test Sayısı:** Dosya-hash karşılaştırma (manual, otomatik test değil)

**Kabul Kriterleri:**
- [ ] 3 dosya bulundu ve içeriği kıyaslandı
- [ ] Kök neden tanımlandı
- [ ] Karar yazıldı: root SSOT veya vault SSOT
- [ ] Rapor D-67 formatında

**Sonraki:** ADMIN-UX-LOGOUT-01 (ortak iş)

---

### 3.5 ADMIN-UX-LOGOUT-01
**Başlık (D-57):** `[ORKESTRA] çıkış/oturum senkronizasyonu: logout anında UI yenilenmeli (2s)`

**Durum:** ✅ DONE (2026-09-19T16:22:23)

**Teslim Özeti (İHSAN):**
> Oturum kapatma işlemi düzeltildi, admin_cikis() fonksiyonu kullanılarak popover içinde doğru oturum kapatma sağlandı. Regresyon testi yazıldı ve tüm testler yeşil (1 passed). Ek temizlik: MUAF kaydı silindi, 3 dosyaya newline eklendi. Rapor: data/orchestrator/ADMIN-UX-LOGOUT-01_rapor_2026-09-19_ihsan.md

**Test Sonuçları:**
- Regresyon testi: 1 PASSED

**Terminal:** Zincir tamamlandı ✅

---

## 4. Zincir Özeti Tablosu

| # | Task ID | Başlık | Ajan | P | Durum | Saat | Test | Kilit Dosya |
|---|---------|--------|------|---|-------|------|------|-------------|
| 1 | ALTYAPI-TEST-FAILURE-FIX-01 | [ALTYAPI] düzelt 4 failure → rapor | **Üretim UTKU** | P1 | plan | 2s | ≥3970 | (TBD) |
| 2 | UI-MENUTREE-02 | [UI] Menu ağacı → __init__.py | **Üretim UTKU** | P1 | ✅ done | 4s | 176 | web_dashboard/tabs/__init__.py |
| 3 | UI-PROFILMENU-POPOVER-02 | [UI] st.popover → profil_menu.py | **Üretim UTKU** | P2 | ✅ done | 2s | 8 | profil_menu.py |
| 4 | ORKESTRA-VAULT-TEKRAR-01 | [ORKESTRA] vault tekrar → rapor | **Orkestratör İHSAN** | P2 | plan | 2s | hash | (manifest) |
| 5 | ADMIN-UX-LOGOUT-01 | [ORKESTRA] logout senkro → app.py | **Orkestratör İHSAN** | P0 | ✅ done | 2s | 1 | app.py |

**Bileşim:**
- **Toplam Görev:** 5
- **Tamamlanan:** 3 (60%) ✅
- **Yapılacak:** 2 (40%)
- **Toplam Saat:** 12s (seri), optimize 10s (paralel)
- **Kritik Path:** ALTYAPI → UI-MENUTREE → UI-POPOVER → VAULT → LOGOUT

**Ajan Dağılımı:**
- **Üretim UTKU:** 3 görev (2+4+2 = 8s kodlama + 3s = 11s)
- **Orkestratör İHSAN:** 2 görev (2+2 = 4s orkestra)
- **Test Danışman SALİH:** 0 (TEST-KAPSAM-OLCUM-01 paralel backlog)
- **Denetim YASU:** 0 (ORKESTRA-STALE-TEMIZLIK-01 review'da)

---

## 5. Bağımlılıklar ve Kilit Yönetimi

### Kilitli Dosyalar (Zincir Süresi Boyunca)
| Dosya | Görev | Ajan | Durumu |
|-------|-------|------|--------|
| web_dashboard/tabs/__init__.py | UI-MENUTREE-02 | UTKU | ✅ release |
| profil_menu.py | UI-PROFILMENU-POPOVER-02 | UTKU | ✅ release |
| app.py | ADMIN-UX-LOGOUT-01 | İHSAN | ✅ release |
| (manifest) | ORKESTRA-VAULT-TEKRAR-01 | İHSAN | **AKTIF** |
| (TBD) | ALTYAPI-TEST-FAILURE-FIX-01 | UTKU | **AKTIF** |

### Zincir Blokaları (Risk)
- ✅ **UI-MENUTREE-02 → UI-POPOVER:** Tamamlandı, bağımlılık çözüldü
- ✅ **UI-POPOVER → VAULT:** Tamamlandı
- ⚠️ **ALTYAPI-TEST-FAILURE-FIX-01 → UI-MENUTREE-02:** Paralel çalışabilir (bağımlı değil)
- ⚠️ **VAULT-TEKRAR → LOGOUT:** Hazırlık görev (seri, geri dönüş riski yok)

---

## 6. Brifleri Yazma (İHSAN'ın Sorumluluğu)

Şu an brifleri yazma işi **İHSAN'a** devredilmiştir. Zincir tasarımında şu görevler için brif yazılması gerekir:

1. **ALTYAPI-TEST-FAILURE-FIX-01** — Brif path: `data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_brif_2026-09-20_uretim.md`
2. **ORKESTRA-VAULT-TEKRAR-01** — Brif path: `data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_brif_2026-09-20_orkestrator.md` (mevcut)

Diğer 3 görev (UI-MENUTREE-02, UI-POPOVER, LOGOUT) zaten **done** durumunda, brif yazılmış ve tetiklenmiş.

---

## 7. Karar ve Öneriler

### Tasarım Onayları
- ✅ **Zincir sırası:** Doğru (bağımlılıklar tutarlı)
- ✅ **Ajan dağılımı:** UTKU ağır (11s), İHSAN ortak (4s) — KAHİN'in talimatı uyumlu
- ✅ **Paralel fırsat:** ALTYAPI-TEST vs UI- görevleri aynı anda başlayabilir
- ⚠️ **Test kapsamı:** SALİH'in TEST-KAPSAM-OLCUM-01 (P2) hâlâ backlog — YASU'nun review'ı bittikten sonra başlatabilir

### Sonraki Adımlar (İHSAN tarafından)
1. ALTYAPI-TEST-FAILURE-FIX-01 brifiniz yazın (belirtilen path)
2. ORKESTRA-VAULT-TEKRAR-01 brifiniz zaten var, gözden geçirin
3. Tetik görev atayın (abrakadabra veya elle): `python scripts/gorev_at.py at --ajan utku --task-id ALTYAPI-TEST-FAILURE-FIX-01`
4. UTKU'ya "ALTYAPI-TEST-FAILURE-FIX-01'yi başla" mesnesi gönderin
5. Paralel: SALİH'i TEST-KAPSAM-OLCUM-01 başlatmaya hazırlayın

---

## 8. Şüphe Maddeleri (Bulgu)

🟡 **Test Kapsamı:** SALİH'in TEST-KAPSAM-OLCUM-01 brifiniz mevcut, ama task_board'da "plan" durumunda. Blokaj riski yok (UTKU işlerine bağımlı değil), hemen başlatabilir.

🟡 **ALTYAPI-TEST-FAILURE-FIX-01 Belirsizliği:** Task_board'da failure tanımı "4 pre-existing test failure" yazılı ama konkret test ID'leri veya failure dosya path'i belirtilmemiş. Brif yazarken clarify gerekebilir.

🟢 **Logout Senkrosu:** P0 görev, zaten tamamlandı. Admin panel workflow kritik yolu açık.

---

**Tasarım Raporu Bitiş Tarihi:** 2026-09-20T13:11  
**Durumu:** Brifleri yazma ve tetikleme untuk İHSAN  
**Onay Bekliyorum:** KAHİN
