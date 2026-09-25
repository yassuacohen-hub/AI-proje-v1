# Ajan Telegram İletişim Rehberi

## 1. Bot'u Başlat

Telegram'da **`@Huginn_Insights_Bot`** araması yap veya linki aç:
```
https://t.me/Huginn_Insights_Bot
```

## 2. Kendini Kaydet

Bot'a şu komutu gönder:
```
/register İhsan
```

**Beklenen yanıt:**
```
✅ İhsan başarıyla kaydedildi.
Chat ID: 123456789
```

> **Not:** Sadece bir kez yapman gerekir. Sistem senin chat_id'ni hatırlar.

## 3. KAHİN (Sahip) Sana Mesaj Atarsa

KAHİN sana Telegram üzerinden mesaj atacak:
```
📬 KAHİN Mesajı (Önem: critical)

Projeyi bitir lütfen
```

**Sen ne yapacaksın:**
- Mesajı oku
- Görev yap
- Tamamlandığında bot'a bildir

## 4. Geri Mesaj Gönder

Bot'ta `/mesaj` veya `Mesaj` butonuna tıkla:
```
Görev tamamlandı, hazırım
```

Sistem:
1. Mesajı **chat.json**'e kaydeder (KAHİN görsün)
2. Seni log dosyasında tutar

## 5. Durum Kontrolü

Bot'ta `Pano` → `Aktif` → Görevleri kontrol et.

---

## Teknik Bilgi (Opsiyonel)

- **Chat ID nedir?** Telegram seni tanımak için kullandığı benzersiz numara.
- **chat.json:** KAHİN'in tüm gelen mesajlarının kütüphanesi.
- **agent_responses.json:** Ajanların tüm geri mesajlarının logu.

---

## Problemi Varsa

1. `/register İhsan` tekrar çalıştır
2. Bot'a `/help` yaz
3. KAHİN'e bildir

**İletişim kuruldu!** 🚀
