---
name: code-quality-and-security
description: >-
  Yazılan kodların güvenliğini (OWASP Top 10), tip güvenliğini, hata yönetimini
  ve otomatik birim testlerini (unit testing) denetleyen kalite kontrol becerisi.
---

# Kod Kalitesi, Güvenlik ve Test Becerisi (Code Quality & Security Skill)

Bu beceri, projedeki kodların güvenlik açıklarından arındırılmış, yüksek test kapsamına sahip ve endüstri standartlarında olmasını sağlar.

---

## 1. Güvenlik Kontrol Listesi (OWASP Temelleri)

Kod yazarken veya incelerken şu 5 güvenlik maddesini zorunlu kıl:

1. **SQL / NoSQL Injection Koruması:** Asla SQL sorgularını metin birleştirme (`f"SELECT * FROM users WHERE id = {user_id}"`) ile oluşturma. Parametreli sorgular veya ORM kullan.
2. **Kimlik Doğrulama & Yetkilendirme (Auth & AuthZ):** Hassas endpoint'lerde kullanıcı rol ve yetki kontrollerini eksiksiz sağla. Şifreleri asla düz metin (plain text) saklama; her zaman güvenli hash algoritmaları (bcrypt, argon2) kullan.
3. **Girdi Doğrulama & Sanitizasyon (Input Validation):** Dışarıdan gelen tüm verileri şema doğrulayıcılarla (Pydantic, Zod vb.) filtrele.
4. **Hassas Veri Sızıntısı (Data Leakage):** Hata mesajlarında stack trace veya veritabanı şifrelerini kullanıcıya dönme; genel hata mesajları (`"İşlem sırasında bir hata oluştu"`) döndür.
5. **CORS ve Güvenlik Başlıkları:** API servislerinde güvenli CORS politikaları tanımla.

---

## 2. Test Protokolü (Testing)

Her yeni özellik için:
- **Birim Testleri (Unit Tests):** Fonksiyonların sınır durumlarını (edge cases: boş girdi, geçersiz format, hata durumları) test et.
- **Otomatik Çalıştırma:** Testleri çalıştırmak için terminal komutunu (`pytest`, `npm test` vb.) hazır bulundur ve doğrula.
