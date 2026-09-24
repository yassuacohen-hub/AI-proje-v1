# FAS 4: Risk 2 (Canonical Karar) + Risk 3 (Müşteri Paneli HUB Planı) — 2026-09-21

**Durumu:** ⚠️ PO Kararı — Risk 2/3 Uygulanmaya Hazır

---

## RISK 2: Seçenek A — İkiz Dosya Canonical Seçimi

**Karar:** `AI proje v1/` klasörü `.arsiv/`'a taşınacak (Seçenek A onaylandı).

**ANCAK: Canonical Karar Gerekli** — 50 ikiz dosya grubundan ~11 tanesi gerçek vault'a ait. Her taşıma öncesi canonical belirlenmelidir.

### Gerçek İkiz Dosyalar (Vault Ana + AI proje v1/)

**Taşınacak İçin Canonical Analiz:**

| Dosya Adı | Canonical (Ana Kaynak) | Neden | Nerede Tutulacak |
|-----------|------------------------|----|-------------------|
| `.instructions` | `Huginn Data Insights/.instructions.md` | Hub linkleri var, güncel | Ana vault root |
| `project_roadmap` | `Huginn Data Insights/PROJECT_ROADMAP.md` | Hub linkleri + backlink bölümü var, emoji temizlenmiş | Ana vault root |
| `agent_sync` | `Huginn Data Insights/AGENT_SYNC.md` | Ana sync hub |Ana vault root |
| `agents` | `AGENTS.md` (root) | Root context, tüm projelerin merkezi | Root |
| `ana_kurallar` | `Huginn Data Insights/ANA_KURALLAR.md` | Hub link var | Ana vault root |
| `changelog` | `Huginn Data Insights/CHANGELOG.md` | Mevcut sprint kayıtları | Ana vault root |
| `claude` | `Huginn Data Insights/CLAUDE.md` | Güncel brief | Ana vault root |
| `kimlik_dogrulama_sistemi` | `Huginn Data Insights/Kimlik Doğrulama Sistemi.md` | ADMIN hub link var | Ana vault root |
| `kullanici_yonetimi` | `Huginn Data Insights/Kullanıcı Yönetimi.md` | ADMIN hub link var | Ana vault root |
| `mimari_kararlar` | `Huginn Data Insights/Mimari Kararlar.md` | Hub link var | Ana vault root |
| `readme_arayuz` | `Huginn Data Insights/README_ARAYUZ.md` | Güncel UI docs | Ana vault root |

**İşlem:** 
1. `AI proje v1/<dosya>` silinecek (canonical taşınmıyor — zaten ana vault'da)
2. `.arsiv/` klasöründe "eski versiyon" logu tutulacak
3. Hub backlink script (`_hub_backlink_uygula.py`) yeniden çalışacak — kırık link olması beklenmez (zaten ana vault'ta canonical var)

### Gürültü İkizleri (Taşınacak YOK — Zaten Marketplace/Skills)

264 x `SKILL.md` + 81 x `INDEX.md` + 44 x `README.md` + 19 x `CHANGELOG.md` = **408 dosya**
- `.agents/marketplace/`, `.claude/skills/`, `.agents/skills/`, `.venv/site-packages/` → Temizlik yapılacak değil, kendi dosyası olarak bırakılacak

---

## RISK 3: Müşteri Paneli HUB — Senaryo 1 Uygulaması

**Onaylı Karar:** Senaryo 1 — Müşteri Paneli HUB (sadece) oluştur. **Orphan çözüm: 1107 dosya → ~280 dosya HUB'a dahil olacak, 827 orphan kalacak.**

### HUB İçeriği (5 Kategori)

Mevcut hub formatı takip: başlık + Üretim + Ana bağlam + Kategorize linkler.

#### Kategori 1: Sprint & PO Yönetimi (6 dosya)

- `Huginn Data Insights/SPRINT_BASLATMA_BELGESI_2026-09-21.md` — Sprint başlatma (sistem kural + proje brief)
- `Huginn Data Insights/SPRINT_GRAPH_STRATEGISI_2026-09-21.md` — Graph hub stratejisi
- `Huginn Data Insights/SPRINT_OZET_VE_SONRAKI_ADIMLAR_2026-09-21.md` — Özet + next steps
- `Huginn Data Insights/PO_KARAR_FORMU_SPRINT_2026-09-21.md` — Risk kararları
- `data/orchestrator/SPRINT_KAPANLIS_RAPOR_2026-09-21.md` — Kapanış raporu
- `Huginn Data Insights/system_prompt.md` — Proje sistem prompt

#### Kategori 2: Admin Panel & Kullanıcı Yönetimi (15 dosya)

- [[Huginn Data Insights/docs/ADMIN_UI_SISTEMI]] — Admin UI kod haritası
- [[Huginn Data Insights/docs/TENANT_HAZIRLIK]] — Multi-tenant setup
- [[Huginn Data Insights/Kimlik Doğrulama Sistemi]] — Auth sistemi
- [[Huginn Data Insights/Kullanıcı Yönetimi]] — User management
- [[Huginn Data Insights/docs/ADMIN_AYARLAR_SAYFASI]] — Admin settings
- [[Huginn Data Insights/docs/ADMIN_PROFIL_YONETIMI]] — Profile management
- [[Huginn Data Insights/docs/plans/ADMIN-MUSTERI-02_brief]] — Admin müşteri brief
- [[Huginn Data Insights/data/orchestrator/ADMIN-*_rapor*]] (15 rapor) — Execution reports

#### Kategori 3: UX/Tasarım (8 dosya)

- [[Huginn Data Insights/docs/UX_ADMIN_PANEL_REVIEW_2026-09-14]] — Panel UX audit
- [[Huginn Data Insights/docs/UX_ANA_SAYFA_WIREFRAME_2026-09-18]]
- [[Huginn Data Insights/docs/UX_AYARLAR_SAYFA_WIREFRAME_2026-09-18]]
- [[Huginn Data Insights/docs/UX_MENU_AGACI_WIREFRAME_2026-09-18]]
- [[Huginn Data Insights/docs/UX_PROFILMENU_WIREFRAME_2026-09-18]]
- [[Huginn Data Insights/docs/UI_MODAL_CHART_ARASTIRMA_2026-09-15]]
- [[Huginn Data Insights/docs/UI_STACK_DEGERLENDIRME_2026-09-18]]
- [[Huginn Data Insights/docs/brand/prompts/dashboard]] — Dashboard brand prompt

#### Kategori 4: Abonelik & Faturalama (5 dosya)

- [[Huginn Data Insights/workspace/external/BRIEF_Y18_abonelik_plan]] — Subscription model
- [[Huginn Data Insights/workspace/external/NOTIFICATION_Y21_P75_kariyer_scraper]] — Notification system
- [[Huginn Data Insights/workspace/external/NOTIFICATION_Y21_P75_kazi_scraper]] — Scraper notifications
- [[Huginn Data Insights/docs/plans/BILLING_PLAN_2026-09-18]] (örneği)
- [[Huginn Data Insights/docs/plans/TENANT_PRICING_MODEL]] (örneği)

#### Kategori 5: AI/Ajanlar & Orchestration (10 dosya)

- [[Huginn Data Insights/AGENTS]] — Ajan tanımları
- [[Huginn Data Insights/AGENT_SYNC]] — Ajan sync raporları
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] — Orkestrayon hub
- [[Huginn Data Insights/workspace/external/claude_code/brief_DASHBOARD-01]] — Dashboard ajan brief
- [[Huginn Data Insights/workspace/external/cline/brief_DASHBOARD-01]]
- [[Huginn Data Insights/workspace/external/copilot/brief_DASHBOARD-01]]
- [[Huginn Data Insights/workspace/external/kilo_code/brief_DASHBOARD-01]]
- [[Huginn Data Insights/workspace/external/roo_code/brief_DASHBOARD-01]]
- [[Huginn Data Insights/workspace/external/roo_code/brief_ROO-01]]
- [[Huginn Data Insights/workspace/external/test_agent/roundtrip_brief]] — Test/validation

### İlgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Admin panel (daha dar kapsam, bu hub ile tamamlayıcı)
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] — Orkestrayon (ajan yönetim)
- [[Huginn Data Insights/PROJECT_ROADMAP]] — Proje yol haritası
- [[AGENTS]] — Ajan tanımları

---

## İNSAN ÖNCESİ KONTROL LİSTESİ

### Risk 2: Canonical Seçimi Onay
- [ ] Canonical tablo kullanıcı tarafından incelendi
- [ ] AI proje v1/ klasörü silinecek tarihine karar verildi (T+1 gün = 2026-09-22?)
- [ ] `.arsiv/` directory oluşturuldu ve backlog içeriği taşındı

### Risk 3: Müşteri Paneli HUB Oluşturma
- [ ] HUB dosyası oluşturuldu: `Huginn Data Insights/hubs/MUSTERI_PANELI_HUB.md`
- [ ] 5 kategori (44 link) + ilgili nodlar içeriği yazıldı
- [ ] Hub backlink script çalışacak — 280 dosyadan ~60 yeni backlink eklenmesi bekleniyor
- [ ] Orphan ölçümü: 1120 → 840 (280 dosya HUB'a katılacak)

---

## Sonraki FAS

**FAS 5: Hub İyileştirme + Veri Tabanı HUB (Risk 3 Senaryo 2)**
- Müşteri Paneli HUB kullanılabilirlik auditi
- Database/Sema HUB oluşturma (225 orphan)
- Güvenlik HUB oluşturma (31 orphan)

**Timeline:** 2026-09-22 sabah (Müşteri Paneli HUB backlink mesai saati)

---

**İmza Alanları:**

PO Onay: _________________________ Tarih: _____________

Teknik Yönetici: __________________ Tarih: _____________
