---
name: enterprise-data-classification
description: >-
  Kurumsal büyük verilerde hassas veri tespiti (PII / DLP), veri profilleme,
  gizlilik etiketlemesi (Confidential/Restricted/Public) ve şema çıkarımı becerisi.
---

# Kurumsal Veri Sınıflandırma ve DLP Becerisi (Data Classification Skill)

Bu beceri, kurumsal veri ambarlarındaki (Data Warehouse) veya veri göllerindeki (Data Lake) yapısal ve yarı-yapısal verileri otomatik olarak tarar, hassas bilgileri tespit eder ve güvenlik seviyelerine göre etiketler.

---

## 1. Hassas Veri Tespiti (PII Patterns & Checksums)

Aşağıdaki veri türlerini hem regex hem de matematiksel kontrol algoritmalarıyla denetle:

1. **T.C. Kimlik Numarası (TCKN):** 11 haneli, ilk hane sıfır olamaz, 10. ve 11. hane özel doğrulama formülüne uymalıdır.
2. **Kredi Kartı Numarası:** 13-19 haneli, **Luhn Algoritması (Mod 10)** kontrolü sağlanmalıdır.
3. **IBAN Numarası:** `TR` ile başlayan 26 haneli format doğrulaması.
4. **İletişim Bilgileri:** Uluslararası ve yerel telefon numaraları (`+90...`), RFC 5322 uyumlu e-posta adresleri.
5. **Finansal & Sağlık Verileri:** Maaş, bakiye, tanı/teşhis kodları.

---

## 2. Güvenlik Sınıflandırma Seviyeleri

* **Seviye 4 (Restricted / Çok Gizli):** Kredi kartı CVV/PAN, şifreler, biyometrik veriler.
* **Seviye 3 (Confidential / Gizli):** TCKN, IBAN, maaş/gelir bilgileri, sağlık verileri.
* **Seviye 2 (Internal / Kurum İçi):** Müşteri adı-soyadı, e-posta, telefon, sipariş geçmişi.
* **Seviye 1 (Public / Genel):** Ürün isimleri, kategori listeleri, genel istatistikler.
