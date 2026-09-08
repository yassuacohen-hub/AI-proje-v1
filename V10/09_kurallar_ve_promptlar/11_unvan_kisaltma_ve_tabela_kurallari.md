# Şirket Ünvanı Kısaltma ve Tabela İsmi Kuralları

Bağlantılar: [[00-Home]] · [[01_sirket_master_ana_belgesi]] · [[10_ankara_osb_sentez]] · [[project_state]]

**Tarih:** 2026-09-02
**Sürüm:** 1.0
**Karar referansı:** [[10_ankara_osb_sentez]] Karar 15

---

## 1. Amaç
Türkiye'deki şirket ünvanlarını standartlaştırmak, kurumsal tabela/marka ismini faaliyet ve şirket türü eklerinden ayrıştırmak ve veritabanında temiz, okunabilir kısa ünvanlar üretmek.

---

## 2. Standart Kısaltmalar Sözlüğü

### 2.1 Şirket Türü Kısaltmaları
| Tam İfade | Standart Kısaltma |
|---|---|
| Anonim Şirket(i) / Anonim Ortaklığı | A.Ş. |
| Limited Şirket(i) | LTD. ŞTİ. |
| Kollektif Şirket(i) | KOL. ŞTİ. |
| Komandit Şirket(i) | KOM. ŞTİ. |
| Adi Ortaklık / Ortaklığı | ORT. |
| Türk Anonim Şirketi / Ortaklığı | TAŞ / TAO |
| Kooperatif | KOOP. |

### 2.2 Sınai ve Ticari Faaliyet Kısaltmaları
| Tam İfade | Standart Kısaltma |
|---|---|
| Sanayi / Sanayii | SAN. |
| Ticaret / Ticareti | TİC. |
| Pazarlama | PAZ. |
| İthalat | İTH. |
| İhracat | İHR. |
| Mühendislik / Mühendis | MÜH. |
| Mimarlık / Mimar | MİM. |
| İnşaat / İnşaatı | İNŞ. |
| Nakliyat / Nakliye / Taşımacılık | NAK. |
| Otomotiv / Otomobil | OTO. |
| Turizm | TUR. |
| Tekstil | TEK. |
| Gıda | GIDA |
| Hizmet / Hizmetleri | HİZM. |
| Tarım / Tarımsal | TAR. |
| Madencilik / Maden | MAD. |
| İmalat | İMAL. |
| Bilişim / Bilgisayar | BİL. |
| Yazılım | YAZ. |
| Makine / Makina | MAK. |
| Mobilya | MOB. |
| Elektrik / Elektronik | ELEK. |
| Kimya / Kimyevi | KİM. |
| Dayanıklı Tüketim Malları | DTM |
| Küçük ve Orta Büyüklükteki İşletme | KOBİ |

### 2.3 Sık Görülen Kombinasyonlar
- SANAYİ VE TİCARET → SAN. VE TİC. (veya SAN. TİC.)
- İTHALAT VE İHRACAT / İHRACAT VE İTHALAT → İTH. İHR.
- İNŞAAT SANAYİ VE TİCARET → İNŞ. SAN. TİC.
- MÜHENDİSLİK MİMARLIK → MÜH. MİM.
- TURİZM VE TİCARET → TUR. TİC.
- GIDA SANAYİ VE TİCARET → GIDA SAN. TİC.
- TEKSTİL SANAYİ VE TİCARET → TEK. SAN. TİC.
- NAKLİYAT VE TİCARET → NAK. TİC.

---

## 3. Ünvan Ayrıştırma Algoritması

1. **Büyük Harf Standartlaşması:** Tüm Türkçe karakterler büyük harfe çevrilir (İ, I, Ş, Ğ, Ü, Ö, Ç).
2. **Uzun İfadeleri Kısaltmaya Dönüştürme:** "SANAYİ VE TİCARET" → "SAN. VE TİC.", "LİMİTED ŞİRKETİ" → "LTD. ŞTİ." vb.
3. **Kuyruk (Suffix) Tespiti:** Sondaki şirket türü ve faaliyet kısaltmaları ayrıştırılır.
4. **Tabela İsmi (Brand/Marka):** Kalan kısmın ilk 2 veya 3 kelimesi tabela ismidir.
5. **Görsel Sunum Kuralı:** Dataframe ve tablolarda Markdown yıldızı (**) KULLANILMAZ; temiz metin olarak gösterilir. Ayrı "Tabela İsmi" sütunu sağlanır.