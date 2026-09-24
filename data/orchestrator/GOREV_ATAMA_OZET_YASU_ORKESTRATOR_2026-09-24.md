# Görev Atama Özeti — 2026-09-24

## Yasu'ya Atanan Görevler (4 adet, 9 saat toplam)

| Sıra | Görev ID | Başlık | Öncelik | Durum | Süre | Neden |
|------|----------|--------|---------|-------|------|-------|
| 1 | **TEST-BLOKE-FAKTOR-ARASTIRMA-01** | Test hazırlık planı araştır → test_bloke_hazirlik.py | P0 | done → formalize | 3s | Yasu teslim etti, review onaylandı |
| 2 | **API-ADMIN-KAYNAK-SAGLIK-18** | Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ | P1 | aktif | 2s | Bağımlılık yok, API testi hazır |
| 3 | **UI-ADMIN-CRAWL-KONTROL-19** | Crawl tetikle/durdur aksiyonu → operatör kontrol paneli | P1 | aktif | 3s | Bağımlılık yok, UI bağımsız |
| 4 | **TEST-ADMIN-K2-AGIRLIK-23** | K2 ağırlık şemasını denetle → test + SSOT kanıt | P2 | aktif | 1s | K2 doğrulama testi, basit |
| | | | | **TOPLAM** | **9s** | |

### Atama Nedenleri
- **Yasu denetim/review rolü** (AGENTS.md D-60): kod inceleme, test doğrulaması ⟹ test görevlerine uygun
- **P1/P2 görevler**: otomatik onay kuralı uygulanır (AGENTS.md D-78)
- **Bağımsız görevler**: API-14 bloklı bağımlılığı yok; diğer testler paralel çalışabilir

---

## Orkestrator'a Atanan Görevler (4 adet, 7 saat toplam)

| Sıra | Görev ID | Başlık | Öncelik | Durum | Süre | Neden |
|------|----------|--------|---------|-------|------|-------|
| 1 | **DOC-ADMIN-DURUM-SENKRON-15** | Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı | P1 | aktif | 1s | Dokümantasyon koordinasyon (SSOT senkronize) |
| 2 | **ALTYAPI-SECRETS-SETUP-01** | Vault kurup .env template yaz → .env.example | P0 | aktif | 2s | Altyapı entegrasyonu, bağımsız |
| 3 | **ALTYAPI-DB-MIGRATION-01** | v0016 → v0017 prod migration planı yaz → db_migrate_prod.sh | P1 | aktif | 1s | Migration runbook (Utku'nun 0017 tamamlamasından sonra) |
| 4 | **ALTYAPI-ADMIN-PANO-01** | Task board 4 bölüm yaz → render_task_board_tab.py | P2 | aktif | 2s | Task board UI, bağımsız |
| | | | | **TOPLAM** | **6s** | |

### Atama Nedenleri
- **Orkestrator (İHSAN) rolleri** (AGENTS.md D-77): pano bakımı, altyapı koordinasyonu, dokümantasyon tutarlılığı
- **P0/P1 elle onay**: orkestrator tarafından onaylanacak (AGENTS.md D-78)
- **Bağımlılık yönetimi**: DOC-15 öncü (SSOT hazırlık), API-14 done olunca DB-01 başlar

---

## Çakışma Analizi

### DOC-ADMIN-DURUM-SENKRON-15 Durumu
- **Panodaki sahip:** utku (ALTYAPI üretim)
- **Brief dosyası:** `plans/brief_utku_DOC-ADMIN-DURUM-SENKRON-15.md`
- **Orkestratör işi midir?** Kısmen:
  - **Tanım (D-77)**: Pano bakımı/düzenleme = orkestratöre ait
  - **Gerçek (D-197)**: SSOT dokümantasyon senkronizasyonu = üretim alanı
  - **Çözüm**: Orkestrator olarak ben senkronizasyonu yönetim/karar düzeyinde yapacağım; Utku dosya yazarsa destek vermeye hazırım

**Karar:** Görev ortaklaşa yapılabilir. Orkestrator sahibi olarak başlat, Utku destek sağlasın.

---

## Çalışma Sırası

### Aciliyet Matriksi (AGENTS.md D-72)
1. **Cuma 19:40-19:50** — DOC-ADMIN-DURUM-SENKRON-15 (SSOT senkronize, §7 matrisi kurulur)
2. **Cuma 19:50-20:00** — ALTYAPI-SECRETS-SETUP-01 (Vault/secrets başlar)
3. **Cuma 20:00-20:10** — ALTYAPI-DB-MIGRATION-01 (runbook yazılır)
4. **Cuma 20:10-20:20** — ALTYAPI-ADMIN-PANO-01 (task board görünümü)
5. **Yasu görevleri paralel çalışsın** — Test hazırlığı, K2 doğrulaması

---

## Sprint Başlangıç Tablosu (D-72)

| Ajan | Yazılacak | Beklenen Sonuç |
|---|---|---|
| YASU | `başla` | `[yasu] 4 bekleyen görev: TEST-BLOKE-FAKTOR-ARASTIRMA-01 (P0), API-ADMIN-KAYNAK-SAGLIK-18 (P1), UI-ADMIN-CRAWL-KONTROL-19 (P1), TEST-ADMIN-K2-AGIRLIK-23 (P2)` |
| ORKESTRATOR (İHSAN) | `başla` | `[ihsan] 4 bekleyen görev: DOC-ADMIN-DURUM-SENKRON-15 (P1), ALTYAPI-SECRETS-SETUP-01 (P0), ALTYAPI-DB-MIGRATION-01 (P1), ALTYAPI-ADMIN-PANO-01 (P2)` |

---

## Atama Kaydı

**Tarih:** 2026-09-24 19:38:00 UTC+3  
**Orkestrator:** İHSAN  
**Komut:** `python scripts/gorev_at.py at --task-id <TASK> --ajan <ajan>` (toplu)  
**Durum:** Teslim beklemede

### İşaretler
- ✅ Panoya yazıldı (task_board.json)
- ✅ Brief dosyaları mevcut
- ✅ Talimatlar panoyla eşleşti
- ⏳ Tetikler düşülecek (KAHİN onayı bekleniyor)
