[[Huginn Data Insights/data/orchestrator/WORKFLOW_OPTIMIZATION.md]]

# İş Akışı Optimizasyonu — V10

Bağlantılar: [[15_admin_panel_sitemap]] → Admin menü ağacı
             [[16_user_panel_sitemap]] → User Panel menü ağacı
             [[14_po_panel_haritasi]] → Gösterge ve panel haritası
             data/orchestrator/task_board.json → Görev durumu

> **Tarih:** 2026-09-14
> **Amaç:** Tüm görevleri, bağımlılıkları ve öncelikleri sitemap'lerle uyumlu hale getirmek.

---

## 1. Görev İkili Tablosu (Task ↔ Sitemap)

### Admin Panel Görevleri

| Görev | Menü Bölümü | Panel | Öncelik | Durum |
|---|---|---|---|---|
| PO-BACK-01 | 🏠 Ana Sayfa + ⚡ Sistem | Admin | P1 | plan |
| PO-BACK-02 | 👥 Müşteri Yönetimi | Admin | P1 | plan |
| PO-BACK-03 | 📢 Kampanya | Admin | P1 | plan |
| PO-BACK-04 | 📦 Paketler | Admin | P1 | plan |
| PO-BACK-05 | 🔄 Tazelik | Admin | P2 | plan |
| PO-BACK-06 | 🤝 Destek | Admin | P2 | plan |
| PO-BACK-07 | 🛡️ Güvenlik | Admin | P2 | plan |
| PO-BACK-08 | 📊 Executive | Her ikisi | P3 | plan |
| PO-BACK-09 | 🎯 Dedup | Admin | P1 | plan |
| PO-BACK-10 | 🔍 Keşif | Admin | P1 | plan |
| PO-BACK-11 | 📡 Kaynak | Admin | P1 | plan |

### Mevcut Aktif Görevler (Sitemap ile Eşleştirme)

| Mevcut Görev | Sitemap Eşleşmesi | Revize İtirafı |
|---|---|---|
| P7-6 (Kariyer.net) | 🔍 Web Kazıma | blocked → kapsam dışı |
| WK-01/02/03 | 📡 Web Scraping | blocked → kapsam dışı |
| MIM-01/02/03 | 🛡️ Mimari | plan → mimari onay bekliyor |
| CC-01/02/03 | 🤖 AI Kod | plan → Claude Code |
| DEV-01/02/03 | 🔧 Geliştirme | plan → Geliştirici |
| QL-01/02/03 | 🎯 Kalite | plan → Kalite |
| RC-01/02/03 | 📊 Raporlama | plan → Roo Code |
| EA-01/03 | 🌐 Dış API | plan → External Agent |
| ORCH-11/12 | 🔧 Sistem | plan → Orkestratör |

---

## 2. Öncelik Rehberi

| Öncelik | Açıklama | Örnek |
|---|---|---|
| P0 | Zorunlu, blok edici | Veri tabanı, temel şema |
| P1 | Çok değerli, kapsam kritik | Admin ana akışı, Müşteri MVP |
| P2 | İkincil, iyileştirme | Destek merkezi, feature flags |
| P3 | Uzun vadeli, stratejik | Executive dashboard, AI optimizer |

### Sitemap Bazlı Öncelik Kuralları

1. **Ana Sayfa (Dashboard)** görevleri P0-P1 önceliklidir — ilk ekran olmalıdır
2. **Müşteri Yönetimi** görevleri P1 önceliklidir — kullanıcı deneyimi temelidir
3. **Sistem & Altyapı** görevleri P1-P2 önceliklidir — performans kritiktir
4. **Güvenlik & Denetim** görevleri P1 önceliklidir — güvenlik önceliğidir
5. **Raporlama & Export** görevleri P2-P3 önceliklidir — sadece veri mevcut olduğunda
6. **Loading UX** ve **Hata Yönetimi** görevleri P3 önceliklidir — refinement aşamasıdır

---

## 3. Bağımlılık Zinciri

```
Temel (Faz 1)
├── PO-BACK-01 (Tenant Health Score) ← hiçbir bağımlılığı yok
│   └── PO-BACK-08 (Executive) ← PO-BACK-01'den bağımlı
├── PO-BACK-07 (Feature Flags + Auth) ← hiçbir bağımlılığı yok
│   └── MFA (daha sonra) ← PO-BACK-07'den bağımlı
└── PO-BACK-05 (Tazelik Etiketi) ← hiçbir bağımlılığı yok
    └── Tüm seviyedeki tazelik görüntüleme

Güçlendirme (Faz 2)
├── PO-BACK-03 (Kampanya Denetimi) ← bağımsız
├── PO-BACK-04 (Paket Kataloğu) ← bağımsız → PO-BACK-08'den bağımlı
├── PO-BACK-06 (Destek MVP) ← bağımsız → PO-BACK-08'den bağımlı
└── PO-BACK-02 (Segment Eligibility) ← bağımsız → PO-BACK-10'dan bağımlı

Gelişmiş (Faz 3)
├── PO-BACK-09 (Duplicate Rate) ← bağımsız → PO-BACK-01'den bağımlı
├── PO-BACK-10 (Coverage Analytics) ← PO-BACK-02'den bağımlı
├── PO-BACK-11 (Source Reliability) ← bağımsız → PO-BACK-03'den bağımlı
└── PO-BACK-08 (Executive) ← PO-BACK-01 + 02 + 10'dan bağımlı
```

---

## 4. Ajan Sorumluluk Matrisi

| Ajan | Sorumluluk Alanı | Görevler |
|---|---|---|
| Roo Code | Admin Panel menü tasarımı, mimari geri bildirim | PO-BACK-01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11 |
| Kilo | Orkestratör, veri kalitesi denetimi | FIX-ID-01, AGENT_SYNC, task board yönetimi |
| Mimar | Şema, mimari kararlar, denetim | MIM-01, 02, 03, MIMAR-01, 02, 03 |
| Geliştirici | Uygulama geliştirme | DEV-01, 02, 03, P7 serisi |
| Kalite | Test ve kalite güvenliği | QL-01, 02, 03, CL serisi |
| Roo Code | UI/UX tasarım, frontend | P7 serisi, DASH serisi |
| Claude Code | Kod inceleme, refactoring | CC-01, 02, 03 |
| Web Kazıma | Web scraping, veri toplama | WK-01, 02, 03, P7-6 |

---

## 5. Ölçüt ve Kabul Kriterleri

| Ölçüt | Hedef | Ölçüm Yeri |
|---|---|---|
| Test Geçer Oranı | ≥%99 | `python -m pytest tests/ -q` |
| Admin Panel Canlı Menü | 7 ana menü | 15_admin_panel_sitemap.md |
| User Panel Planlanmış Menü | 8 ana menü | 16_user_panel_sitemap.md |
| PO-BACK Tamamlanma | 11/11 görev | task_board.json |
| Doküman Tutarlılığı | Tüm bağıntılar geçerli | V10 belgeleri |
| KPI Tüm Göstergeler | 10/10 ölçülebilir | 14_po_panel_haritasi.md |

---

## 6. Son Kontrol Listesi

- [ ] Admin Panel sitemap belgesi tamamlandı (15_admin_panel_sitemap.md)
- [ ] User Panel sitemap belgesi tamamlandı (16_user_panel_sitemap.md) — TASLAK
- [ ] Admin Panel uygulama planı tamamlandı (17_admin_panel_uyglama.md)
- [ ] Tüm PO-BACK görevleri task board'a kayıtlı
- [ ] Tüm PO-BACK görevleri panel bazlı kategorize edildi
- [ ] Tüm görev bağımlılıkları sitemap'lerle uyumlu
- [ ] Ajan sorumluluk matrisi belirlendi
- [ ] Test stratejisi faz bazlı belirlendi
- [ ] Risk ve mitigasyon listesi oluşturuldu
- [ ] ROO_ELESTIRI_NOTLARI.md O-06 çözüldü

---

## 7. Darboğaz Listesi

Mevcut süreçteki ana darboğazlar ve etkileri:

| # | Darboğaz | Etki | Çözüm |
|---|---|---|---|
| 1 | Görev teslimi doğrudan `done` yapılması | Onaysız tamamlanma, denetim kaybı | `gorev_kutusu.py teslim` zorunlu, `done` YASAK |
| 2 | AST bekçi testi eksikliği | Yasak importlar (streamlit/auth) tenant paketine girebilir | `test_tenant_bekci.py` ile tarama zorunlu |
| 3 | Cache tazeliği testlerde tutarsız | Stale veri ile yanlış test sonuçları | Autouse fixture'da `_CACHE.clear()` |
| 4 | Dosya kilitleme kontrolü eksikliği | Paralel değişiklik çakışması | `gorev_ekle(dosyalar=[...])` ile otomatik kilit |
| 5 | Onay kuyruğu doluluk | Görevler onaysız kalabilir | `onay-bekleyen` periyodik kontrol; `onayla`/`reddet` |

---

## 8. Önerilen Akış

Her görev için zorunlu akış:

```
Tetik → Al → Çalış → Teslim → Onay → Done
```

Aşağıda adım adım detay:

| Adım | Komut | Açıklama |
|---|---|---|
| 1. Tetik | `gorev_at.py at --task-id X` veya otomatik | Görev panoya eklenir, kilit düşer |
| 2. Al | `gorev_kutusu.py al --ajan A --task-id X` | Durum: `aktif` |
| 3. Çalış | (ajen tarafından) | Görevi görerek implementasyon |
| 4. Teslim | `gorev_kutusu.py teslim --ajan A --task-id X --ozet "..."` | Durum: `review` (onay bekliyor) |
| 5. Onay | `gorev_kutusu.py onayla --task-id X --ben orkestrator` | Durum: `done`, kilitler düşer |
| 5b. Reddet | `gorev_kutusu.py reddet --task-id X --neden "..."` | Durum: `aktif` (düzeltme) |

---

## 9. Ölçüm KPI'ları

İş akışı performansını ölçen KPI'lar:

| # | KPI | Tanım | Hedef | Ölçüm Yeri |
|---|---|---|---|---|
| 1 | Ortalama teslim süresi | Görev `al` → `teslim` arası ortalama süre | ≤4 saat | `task_board.json` `baslangic`/`bitis` zamanları |
| 2 | Ret oranı | `reddetilen` / `toplam teslim` oranı | ≤20% | `onay-bekleyen` geçmişi |
| 3 | Onay süreci süresi | `teslim` → `onayla` arası ortalama süre | ≤2 saat | `decision_log.jsonl` zaman damgaları |
| 4 | Test geçer oranı | `pytest` geçen / toplam test oranı | ≥%99 | `python -m pytest tests/ -q` |
| 5 | Bekçi test % kapsamı | AST bekçi testleri ile ele geçen dosya oranı | %100 (tenant/health/aktarım modülleri) | `test_tenant_bekci.py`, `test_i18n_disa_aktar.py` |

**KPI Hesaplama Formülleri:**
- Ortalama teslim süresi = SUM(teslim_tarihi - al_tarihi) / COUNT(gorevler)
- Ret oranı = COUNT(ret_detilenler) / COUNT(teslimler) * 100
- Onay süreci süresi = SUM(onay_tarihi - teslim_tarihi) / COUNT(onaylananlar)
---

*Son güncelleme: 2026-09-14*
*Doküman: data/orchestrator/WORKFLOW_OPTIMIZATION.md*
