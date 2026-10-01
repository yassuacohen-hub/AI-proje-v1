# ALTYAPI-ODIN-DENETIM-RAPORU — Denetim Checklist

**Tarih:** 2026-10-01 · **Denetleyen:** yasu · **Karar:** 🔴 NO-GO

---

## A. Ön Koşul

| # | Kontrol | Sonuç | Kanıt |
|---|---|---|---|
| A1 | Ön görevler tamamlanmış mı (5 görev) | ❌ | 5/5 `plan` |
| A2 | Eğitim veri seti mevcut | ❌ | `data/odin_training_data.*` yok |
| A3 | Eğitim pipeline mevcut | ❌ | `scripts/odin_training_pipeline.py` yok |
| A4 | Prompt-injection sonuç dosyası | ❌ | yok |
| A5 | Metrik dosyası | ❌ | `data/**/*metric*` = 0 |
| A6 | Odin kodu mevcut | ✅ | `rag.py` 3.143 B |
| A7 | Odin testleri geçiyor | ✅ | 19/19, 1.49 sn |
| A8 | ML kütüphanesi kurulu | ❌ | torch/transformers/peft/sklearn **yok** |

## B. KAPİ 1 — Veri (D-248, D-252)

| # | Kontrol | Sonuç | Kanıt |
|---|---|---|---|
| B1 | Eğitim seti satır sayısı | ⚫ | Set yok |
| B2 | Örnek çeşitliliği | ⚫ | Set yok |
| B3 | TCKN taraması (eğitim seti) | ⚫ | Set yok |
| B4 | Genel `data/` KVKK taraması | 🟡 | 748 dosya; 10-11 hane 47 dosya, IBAN 2 (TR5100 kamu) |
| B5 | Maskelenmemiş kişisel veri (K5) | 🔴 | Set yok — **0 kanıtlanamadı** |
| B6 | Kaynak kısıtı (company_master only) | ⚫ | Set yok |
| B7 | D-248 kişisel veri ayrımı | ⚫ | Set yok |
| B8 | D-252 NACE 3 katman | ⚫ | Set yok |

## C. KAPİ 2 — Güvenlik (D-310, D-224)

| # | Kontrol | Sonuç | Kanıt |
|---|---|---|---|
| C1 | Prompt-injection senaryoları (K3) | 🔴 **KRİMİZAL** | Çalıştırılmadı |
| C2 | `__İÇ_RAPOR_VER__` kaçak testi (K4) | 🔴 **KRİMİZAL** | Çalıştırılmadı |
| C3 | İç/müşteri endpoint ayrımı | ⚪ | Endpoint yok |
| C4 | Ayrı auth anahtarı | ⚪ | Yok |
| C5 | Maskeleme kapısı (D-247) | ✅ | `python scripts/_kontrol_tckn_dugme.py` → **6/6** |
| C6 | Varsayılan maskeli | ✅ | Mandal 1 |
| C7 | Admin istisnası role bağlı | ✅ | Mandal 2 |
| C8 | Düğme aç/kapa | ✅ | Mandal 3 |
| C9 | Boş değer maskeye dönmez | ✅ | Mandal 4 |
| C10 | Auth anahtarı `.env`'de | ✅ | `.env:79`, kodda secret yok |
| C11 | Model çıktısı maskelemesi | ❌ | Model yok |

## D. KAPİ 3 — Kalite (K1, K2)

| # | Kontrol | Eşik | Sonuç |
|---|---|---|---|
| D1 | Sınıflandırma doğruluğu (K1) | ≥ %70 | ⚫ Ölçülemedi |
| D2 | Gecikme p95 (K2) | < 500 ms | ⚫ Ölçülemedi |
| D3 | Aşırı fit (train vs val) | < %15 fark | ⚫ Ölçülemedi |
| D4 | Çeşitlilik | — | ⚫ Ölçülemedi |
| D5 | Embedder anlamsal mı | — | ❌ SHA-256 hash, 16 boyut |

## E. KAPİ 4 — Ücretsiz dönem (K6)

| # | Kontrol | Sonuç | Kanıt |
|---|---|---|---|
| E1 | EVREN katalog erişimi | ✅ | 13 model canlı |
| E2 | Fiyat | ✅ | 0.0 CR, `free_until: 2026-11-01` |
| E3 | **Fine-tune / eğitim ucu** | ❌ | **Katalogda yok** |
| E4 | Bugünkü tüketim | ✅ | ~30 çağrı, 0 CR |
| E5 | 1 Kasım sonrası maliyet | ⚫ | Eğitim ucu olmadan hesaplanamaz |
| E6 | Kaldırılacak model | 🟡 | `deepseek-v4-flash` (1 Kasım) |

## F. Karar

| Kriter | Eşik | Sonuç |
|---|---|---|
| K1 | ≥ %70 | ⚫ Ölçülemedi |
| K2 | < 500 ms | ⚫ Ölçülemedi |
| **K3** | **≥ 8/10** | 🔴 **Çalıştırılmadı** |
| **K4** | **0 kaçak** | 🔴 **Çalıştırılmadı** |
| K5 | 0 satır | 🔴 Set yok |
| K6 | 01.11.2026 | 🟡 Eğitim ucu yok |

# 🔴 **NO-GO**

---

## Doğrulama Özeti

| Kategori | ✅ | 🟡 | 🔴 | ⚫ |
|---|---|---|---|---|
| Ön koşul | 2 | 0 | 5 | 1 |
| Veri | 0 | 1 | 1 | 6 |
| Güvenlik | 6 | 0 | 3 | 2 |
| Kalite | 0 | 0 | 1 | 4 |
| Ücretsiz dönem | 3 | 1 | 1 | 1 |
| **Toplam** | **11** | **2** | **11** | **14** |

**11 doğrulandı · 2 uyarı · 11 başarısız · 14 ölçülemedi**
