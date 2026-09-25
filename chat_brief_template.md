# Chat Brief Template — Standart Format

## 📋 Telegram & Chat Mesaj Şablonu

Aşağıdaki format, görevleri Telegram ve Chat platformlarına standart şekilde dağıtmak için kullanılır.

---

## 🔹 Format 1: Kompakt Versiyon (Telegram)

```
📋 **[ID] — Başlık**
👤 Atanan: [owner]
🎯 Öncelik: [P0/P1/P2]
⏰ Deadline: [Tarih - GG.AA.YYYY]

**Özet:** [2 cümle maksimum]

**Kabul Kriterleri:**
✓ [Kriter 1]
✓ [Kriter 2]
✓ [Kriter 3]

**Kaynaklar:** [Link veya referans]
**Proof:** [Çıktı dosyası / Kontrol noktası]
```

### Örnek — Telegram Kompakt:
```
📋 **UTKU-01 — Kaynak Araştırması: AI Trendleri 2026**
👤 Atanan: UTKU
🎯 Öncelik: P1
⏰ Deadline: 28.09.2026

**Özet:** 2026 AI trendlerini araştır ve en önemli 5 trendi belirle. Sonuçları markdown dosyasına yaz.

**Kabul Kriterleri:**
✓ En az 5 makale/kaynak incelenmiş
✓ Trendler P0/P1 ile sıralandı
✓ Her trend için 1-2 cümle açıklama var

**Kaynaklar:** https://example.com/ai-trends
**Proof:** research_ai_trends_2026.md
```

---

## 🔹 Format 2: Detaylı Versiyon (Chat/Internal)

```
📋 **[ID] — Başlık**

👤 **Atanan:** [owner]
🎯 **Öncelik:** [P0/P1/P2]
⏰ **Deadline:** [Tarih - GG.AA.YYYY]
📍 **Durum:** Yeni

---

## 📄 Özet
[2-3 cümle - görevin amacı ve beklentisi]

---

## ✅ Kabul Kriterleri

1. **Kriter 1 — Açıklama**
   - Alt koşul A
   - Alt koşul B

2. **Kriter 2 — Açıklama**
   - Alt koşul A
   - Alt koşul B

3. **Kriter 3 — Açıklama**
   - Alt koşul A

---

## 🔗 Kaynaklar & Bağlamlar
- [Referans 1](link)
- [Referans 2](link)
- Wiki: [İlgili sayfa](link)

---

## 📦 Beklenen Çıktı

**Dosya:** [output_file_name.ext]
**Format:** [Markdown/JSON/CSV/etc]
**Konum:** [Path veya link]

---

## 📌 Notlar
- [Ek bilgi varsa]
- [Kısıtlamalar varsa]

---

**Başlatılan:** [Tarih]
**Hazırlayan:** [Isim]
```

### Örnek — Chat Detaylı:
```
📋 **YASU-02 — Telegram Menu Optimization**

👤 **Atanan:** YASU
🎯 **Öncelik:** P1
⏰ **Deadline:** 29.09.2026
📍 **Durum:** Yeni

---

## 📄 Özet
Telegram menüsünü optimize et ve yeni kategori yapısı ekle. Kullanıcı navigasyon süresi 30% azalt.

---

## ✅ Kabul Kriterleri

1. **Menu Yapısı Yenilendi**
   - Tüm kategoriler yeniden organize edildi
   - Hızlı erişim linkleri eklendi

2. **Performans Artışı**
   - Navigasyon süresi ölçüldü (baseline)
   - Hedef: 30% azalma doğrulandı

3. **Kullanıcı Testi**
   - 5 test kullanıcısı ile doğrulandı
   - Feedback toplanıp uygulandı

---

## 🔗 Kaynaklar & Bağlamlar
- Current menu: [link to Telegram]
- Design specs: [link to design doc]
- Analytics: [link to metrics]

---

## 📦 Beklenen Çıktı

**Dosya:** telegram_menu_v2.json
**Format:** JSON (Telegram Bot API uyumlu)
**Konum:** Huginn Data Insights/telegram/menus/

---

## 📌 Notlar
- Eski menu geri alınabilir bir backup olarak tutulacak
- Implementasyondan önce staging ortamında test et

---

**Başlatılan:** 25.09.2026
**Hazırlayan:** ORCH
```

---

## 🔹 Format 3: WhatsApp/Direct Message (Minimal)

Hafif bir görev için (çok kısa, acil):

```
✓ **[ID] — Başlık**
👤 [owner] | 🎯 P1 | ⏰ [Tarih]

Özet: [1 cümle]
Kabul: [Ana kriter 1-2]
Proof: [Dosya]

Link: [Ref]
```

### Örnek — WhatsApp Minimal:
```
✓ **ORCH-03 — Bug Fix: Task Status Update**
👤 ORCH | 🎯 P0 | ⏰ 25.09.2026

Özet: task_board.json'da status güncellemede sorun var, onay/reddetme tuşu çalışmıyor.
Kabul: Bug tespit edildi • Fix uygulandı ve doğrulandı
Proof: task_board_status_fix.md

Link: https://github.com/huginn-project/issues/42
```

---

## 📋 Seçim Kılavuzu

| Platform | Format | Ne Zaman Kullan |
|----------|--------|-----------------|
| **Telegram** | Kompakt (Format 1) | Hızlı bilgilendirme, günlük görevler |
| **Chat (Internal)** | Detaylı (Format 2) | Karmaşık görevler, tam bağlam gerekli |
| **WhatsApp/DM** | Minimal (Format 3) | Çok acil, basit görevler (<30 dakika) |

---

## 🔧 Dinamik Alanlar

Şu alanlar her görev için özelleştirilmelidir:

| Alan | Tanım | Örnek |
|------|-------|--------|
| `[ID]` | Görev tanımlayıcısı | `UTKU-01`, `YASU-05`, `ORCH-02` |
| `[owner]` | Sorumlu kişi | `UTKU`, `YASU`, `ORCH` |
| `[P0/P1/P2]` | Öncelik seviyesi | P0=Acil, P1=Yüksek, P2=Orta |
| `[Tarih]` | Teslim tarihi | `28.09.2026` (GG.AA.YYYY) |
| `[Özet]` | 2-3 cümlelik açıklama | İşin amacı ve çıktısı |
| `[Kriter]` | Başarı tanımı | Ölçülebilir, net koşullar |
| `[Kaynaklar]` | İlgili linkler | Referanslar, wiki, spec |
| `[Proof]` | Çıktı dosyası/kontrol | Teslim edilebilir iş kanıtı |

---

## ✨ Best Practices

1. **Açıklık:** Her alan net, muğlak olmayan bilgi içermeli
2. **Ölçülebilirlik:** Kabul kriterleri doğrulanabilir olmalı
3. **Eksiklik:** Gereksiz detay ekleme, esas bilgiyi vur
4. **Deadline:** Her görev net bir tarih içermeli
5. **Bağlam:** Kaynaklar veya öncül görevler linkle
6. **Proof:** Çıktı dosyası, konum, format belirtilmeli

---

## 📝 Not

Bu template, başta Telegram ve Chat'te hızlı dağıtım için optimize edilmiştir. 
Detaylı görevler için Format 2 (Chat), acil görevler için Format 1 (Telegram), 
minimal görevler için Format 3 (WhatsApp) kullan.
