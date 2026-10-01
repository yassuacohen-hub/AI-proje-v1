# Orkestratör Durum Özeti — 2026-10-01

**İçin:** KAHİN (Ürün Sahibi)  
**Tarih:** 2026-10-01, 11:37 UTC+3  
**Oturum:** Code Mode — Hızlı eylem kapısı

---

## 📊 Anlık Durum

| Metrik | Değer |
|--------|-------|
| **Pano görev sayısı** | 153 |
| **Aktif görev** | 12 |
| **Review bekleme** | 3 |
| **Planned (hazırlanıyor)** | 2 |
| **Borç defteri** | 36 borç (12 açık / 20 kapalı / 4 erteleme) |

---

## 🎯 Bu Oturumda Yapılanlar

### 1️⃣ **Veri Kalitesi — 3 Review Görev Denetimi**

3 teslim edilmiş görev incelendi:

| Görev | Durum | Ne yapıldı |
|-------|-------|-----------|
| **VERI-TSG-04-YAZICI-01** | review | TSG-04 yazma hattı (company_events) yazıldı; 302 kayıt eklendi. **Bulgu:** 306/326 etikette NULL sonucu — sebep case-mismatch (büyük/küçük harf duyarlılığı). Hata 20 dolu etiketi vuruyor. |
| **VERI-NACE-ACILIM-01** | review | NACE açılım metni gösterimi eklendi (sunum.acilim_getir); 2784/3319 kod açılımlandı. **Bulgu:** Çıplak except, bayat doctest, cache bayatlama. |
| **VERI-NACE-COKLU-01** | aktif | 21/14003 satır işlendi; ön koşul VERI-KAYNAK-BAG-01 kaldırıldı. Başlanabilir. **Bulgu:** Yok. |

---

### 2️⃣ **2 Yeni Görev — Borç Defteri Çözümü**

#### ✅ **VERI-TSG-ESLEME-CASE-01** (planned)
- **Kapsam:** BORC-TSG-ESLEME-CASE-01 (D-260 borcu)
- **Sorun:** 306 boş etiket case-mismatch'den kaynaklanıyor; 20 dolu etiket de büyük/küçük harf tutarsızlığı var
- **Yapılacak:** Normalize et (oday_esle veya ILAN_TURU_ESLEME), canlı DB ölçümü (D-238)
- **Brief:** ✓ Yazıldı — `plans/brief_utku_VERI-TSG-ESLEME-CASE-01.md`
- **Ajan:** UTKU

#### ✅ **VERI-TENDER-KOLON-01** (planned)
- **Kapsam:** BORC-TENDER-KOD-01 (D-308 göçü eksikliği)
- **Sorun:** D-308 göçü ihale_ilanlari'nın 8 Türkçe kolon adını İngilizce'ye çevirdi (0043_tender_sema_cevirisi.sql), ama osb_tender_monitor.py hâlâ eski adları kullanıyor — kod hiçbir zaman çalıştırılmadı
- **Yapılacak:** 8 Türkçe kolon adı → İngilizce (ilan_basligi → tender_title, vb.), test, prova (`--dry-run`)
- **Brief:** ✓ Yazıldı — `plans/brief_utku_VERI-TENDER-KOLON-01.md`
- **Ajan:** UTKU

---

### 3️⃣ **Ajan Haber Sistemi — 3 Chat Satırı**

ajan-chat.jsonl güncelendi — UTKU'ya:
- Yeni görev VERI-TSG-ESLEME-CASE-01 bildirildi
- Yeni görev VERI-TENDER-KOLON-01 bildirildi  
- VERI-TSG-04-YAZICI-01 denetim notu gönderildi

---

## 🔴 Acil Bulgular

| # | Bulgu | Etki | Aksiyonu |
|-|-|-|-|
| 1 | **Case-mismatch**: 306 boş etiket, hata 20'yi vuruyor | Veri kalitesi düşük, sayım tutarsız | VERI-TSG-ESLEME-CASE-01 başlasın (P1) |
| 2 | **Kod-schema tutarsızlığı**: osb_tender_monitor.py D-308'i görmedi | D-308 kilit, pipeline kırılabilir | VERI-TENDER-KOLON-01 başlasın (P1) |

---

## 🟡 Dikkat

| # | Bulgu | Açıklama |
|-|-|-|
| 1 | Bayat doctest (VERI-NACE-ACILIM-01) | Testin eski versiyonu çalışıyor, güncellensin |
| 2 | Canlı ölçüm eksik (VERI-TSG-04-YAZICI-01) | D-238 kuralı: ölçüm DB'den yapılmalı — yapılmadı |

---

## 🟢 Tamam

| # | Durum |
|-|-|
| Pano yapısı tutarlı | ✓ |
| Brief şablonları hazır | ✓ |
| Chat sistemi işletiyor | ✓ |
| Borç defteri güncellendi | ✓ (36 → 38 görev, 2 yeni) |

---

## 🔵 Bilgi & Öneriler

1. **UTKU'ya:** 2 yeni görev (VERI-TSG-ESLEME-CASE-01, VERI-TENDER-KOLON-01) atanmış. Her ikisi P1, ön koşul yok. Paralel çalışabilir.

2. **SALIH'e:** 3 review görev (VERI-TSG-04-YAZICI-01, VERI-NACE-ACILIM-01, VERI-NACE-COKLU-01) varsa kontrol edilsin. DENETIM bulgusu kaydedildi.

3. **Borc defteri:** BORC-TSG-ESLEME-CASE-01 ve BORC-TENDER-KOD-01 açık. Kapanış için görevler başlasın.

4. **Risk:** Eğer UTKU 1 gün içinde başlamazsa, D-288 (zincir testi) ve D-260 (canlı ölçüm) kırılır. Eskalasyon hazır.

---

## 📋 Sonraki Adımlar

1. KAHİN'in onayı → UTKU başlasın (VERI-TSG-ESLEME-CASE-01)
2. KAHİN'in onayı → UTKU başlasın (VERI-TENDER-KOLON-01)
3. SALIH denetim raporlarını kontrol etsin
4. Haftalık özeleştiri (D-67): Pano yapısı, ajan performansı, borç defteri

---

**Orkestratör İmzası:** İHSAN · Tarih: 2026-10-01 11:37 UTC+3
