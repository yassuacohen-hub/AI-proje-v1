# Sentez: Admin Panel Yeniden Yapılandırma — ORCH-13 (00_sentez.md)

> **Kaynak:** [[brif_roo]] + [[brif_kilo]] + [[brif_copilot]] (2026-09-13)
> **Hazırlayan:** orkestratör (SENTEZ-01) · **Durum:** kullanıcı onayı bekliyor
> **Kural:** Bu dosya onaylanana kadar DASH-UX görevleri kapalıdır (blokaj).
> Onaylanınca her ajan ÖNCE burayı okur, sonra işine başlar.

---

## ÖZET (tek paragraf)

Üç ajan da aynı yöne işaret etti: **"ajana değil, kullanıcıya sunulan göreve odaklan"**.
roo — her sekme bir *operasyonel sinyal* sunsun ve ortak sekme kalıbı olsun (başlık+açıklama+yenile+"neden" kutusu). copilot — taşıma işleri *dikey dilimle* yapılsın (veri kaynağı + boş-veri + test aynı dilimde), her sekme için *kabul sözleşmesi* yazılsın. kilo — mevcut altyapı (9Router `/v1/chat/completions`, `api_usage`, PostgreSQL) MVP için yeterli; kritik uyarı: admin+müşteri paneli aynı veritabanı → bağlantı havuzu ayrışmalı (altyazı notu).

## ✅ KABUL EDİLENLER (uygulamaya geçer)

| # | Karar | Nerede uygulanır |
|---|-------|------------------|
| K1 | **Ortak sekme kalıbı:** ikon+başlık + `Son güncelleme: HH:MM` + yenile butonu + "ℹ️ Bu sekme hakkında" (amaç/veri kaynağı/kısıt) | DASH-UX-01 → app.py şablonu; tüm sekmeler |
| K2 | **Boş-veri kuralı:** boş grafik ÇİZİLMEZ → "Veri gelince X burada görünecek" placeholder'ı; spinner öncesi üstte sabit bilgi kutusu (spinner kapanınca bilgi kaybolmasın) | DASH-UX-02a/b (taşınan tüm sekmeler) |
| K3 | **Metrik açıklaması:** her metrik/grafik yanında 1 satır Türkçe "bu neyi gösterir / neye yarar" + operasyonel soru (örn. "QS<30 firma arttı mı?") | tüm DASH-UX görevleri |
| K4 | **7 sekme + blok ayrımı:** müşteri metrikleri ≠ sistem metrikleri (mavi kart = müşteri, turuncu = sistem) — roo'nun Tier fikri 7 sekme içinde kart/blok olarak uygulanır | DASH-UX-01 (ana_kontrol) |
| K5 | **Dikey dilim taşıma:** sekme taşınırken veri kaynağı + empty state + test BİRLİKTE gider; yarım taşınmaz | DASH-UX-02a/b |
| K6 | **AI motor:** 9Router `/v1/chat/completions` (OpenAI formatı) → Abrakadabra bunu kullanır; **fallback provider listesi şart** (uptime garantisi yok) | AI-CHAT-01 |
| K7 | **Demo veri:** `data/demo/` ayrı katman, "DEMO" rozetli, gerçek veriyle karışmaz | DASH-UX-03 |
| K8 | **Denetim izi:** tüm otomatik işlemler JSONL'e atomik tek-yazar ile yazılır + arşivlenir (roo A9 + copilot 3.2 çakışıyor → JSONL kabul, PostgreSQL Faz 2/3) | isbirligi_raporu zaten uyumlu |

## ❌ REDDEDİLENLER / ERTELENENLER (gerekçesiyle)

| # | Öneri | Karar | Gerekçe |
|---|-------|-------|---------|
| R1 | roo: "17 sekme → 4 Tier'lık sidebar navigasyonu" | **KABUL (kullanıcı onayı 2026-09-13)** | Kullanıcı: "hemen sidebar yapalım" — 7 sekme SOL SİDEBAR'dan, 2 kategorili (İş / Sistem). Tier kavramı kategori olarak sidebar'a girer. Bkz. kararlar bölümü. |
| R2 | copilot: "st.tabs'ı büyütme, hemen sidebar" | **KABUL (kullanıcı onayı)** | Sidebar şimdi geliyor; eşik beklenmedi. |
| R3 | kilo: "migration 0012-0018 Faz 3 admin için şart" | **KABUL ama kapsam dışı** | Bu sprint demo veri + mevcut tablolar; migration'lar DASH-UX-03'ün notuna işlendi (senaryo değişirse). |
| R4 | roo: "P7-32 api_usage in-memory → api_usage_daily tablosu" | **Faz 2** | Bu sprint: sekme sunumunda "veri restart'ta sıfırlanır" notu yeterli. |
| R5 | copilot: "Playwright e2e test suite" | **BEKLEMEDE** | Kullanıcı kararı gerek (aşağıda BK2). Kritik sekmeler için ayrı görev açılır. |
| R6 | kilo: "admin panelden müşteri paneli ayrı PG bağlantı havuzu" | **NOT, kod gerektirmez** | Altyapı notu olarak DASH-UX-03 tA limatına eklendi. |

## ⏳ BEKLEYEN KARARLAR (sana sorulacak)

| Kod | Soru | Önerim |
|-----|------|--------|
| BK1 | **8. sekme "Uyarılar"** ekleyelim mi? (roo Tier-1'de önerdi; spike/anomali/maliyet uyarıları tek yerde) | **Evet** — ana_kontrol'ün "uyarı şeridi" dolu olursa bölünür. Ama önce 7 sekme otursun, 8.'yi DASH-UX-01 sonunda açalım. |
| BK2 | **Playwright e2e** bu sprint'e mi girecek? | Şimdilik HAYIR; unit + render contract yeterli. e2e Faz 2'ye (kota ile). |
| BK3 | Sekme adları: **Ana Kontrol · Müşteriler · Sistem · Paketler · Pazarlama · Abrakadabra · Yönetim** | Onayın gerekli. |
| BK4 | Abrakadabra modeli: 9router'dan **ucuz/hızlı** (örn. `gpt-4o-mini` sınıfı) — repo'da `scripts/9router_optimizer.py` ayarından seçilecek | Onayın gerekli. |

## ✅ KULLANICI KARARLARI (2026-09-13 — onaylandı)

| Kod | Karar | Not |
|-----|-------|-----|
| BK1 | 8. "Uyarılar" sekmesi | ŞİMDİLİK HAYIR — 7 sekme oturunca değerlendirilir |
| BK2 | Playwright e2e | Faz 2'ye bırakıldı; bu sprint unit + render contract |
| BK3 | Sekme adları | **Ana Kontrol · Müşteriler · Sistem · Paketler · Pazarlama · Abrakadabra · Yönetim** — ONAYLI |
| BK4 | Abrakadabra modeli | 9router'dan ucuz/hızlı (mini/haiku sınıfı) — ONAYLI |
| BK5 | **Navigasyon: SIDEBAR ŞİMDİ** | Sol sidebar, 2 kategori: **İş** (Ana Kontrol / Müşteriler / Paketler / Pazarlama / Abrakadabra) · **Sistem** (Sistem / Yönetim). `st.sidebar` + radio/selectbox; üst `st.tabs` kapısı yok. DASH-UX-01 (roo) tarafından uygulanır. |

```
ONAY → SENTEZ-01 done → blokajlar açılır:
  copilot:  DASH-UX-02a → 02b   (Sistem + Yönetim konsolidasyonu, dilim dilim)
  kilo:     DASH-UX-03 → AI-CHAT-01  (Paket backend → Abrakadabra)
  roo:      DASH-UX-01 → DASH-UX-04  (Ana Tasarım → Paket/Pazarlama UI)
BEN: WIKI-01 (kullanım kılavuzu) — yapı oturunca, sentez onayını takiben başlar.
```

---
**İlişkili:** [[00_sablon]] · [[06_muninn_prd_vs_huginn_analiz]] · [[02_muninn_super_admin_panel_prd_ve_yol_haritasi]]
