# KVKK ve Veri Politikas`````

Bu belge, Huginn Data Insights projesinde KVKK (Kişisel Verilerin Korunması Kanunu) kapsamında uygulanan veri filtreleme ve politikalarını tanımlar. Kaynak: [[10_ankara_osb_sentez]], [[01_sirket_master_ana_belgesi]].

## 1. Amaç

Şirket/kişi verisi toplarken KVKK Madde 5/6 "açık rıza" ve "işleme şartları"na uyumlu davranmak; bireysel verileri en aza indirirken iş süreçleri için gerekli kurumsal iletişimi korumak.

## 2. Kapsam

- Web scraping (OSTİM, ASO 1, İvedik)
- Manuel veri girişi (admin panel)
- Üçüncü parti veri entegrasyonu (KOSGEB, TOBB, MERSİS)
- API uç noktaları (public + authenticated)

## 3. Filtreleme Kuralları (Genel)

1. **Bireysel e-posta filtrelenir:** Kişisel Gmail/Hotmail/Yandex adresleri (örn. `ahmet@gmail.com`) veri tabanına yazılmaz; `NULL` yapılır veya maskelenir.
2. **Kurumsal e-posta korunur:** `info@`, `iletisim@`, `contact@`, `kurumsal@`, `satis@`, `destek@` önekli adresler kabul edilir.
3. **Şahıs adı kaldırılır:** "Ahmet Bey", "Mehmet Hanım" gibi contact person ibareleri `key_personnel` tablosuna alınmaz; yalnızca unvan/rol alınır.
4. **Adres maskeleme (opsiyonel):** Tam adres gerektiğinde il/ilçe seviyesine indirgenebilir.

## 3.1 GSM Telefon Politikası (2026-09-01 Güncelleme)

**Kural:** Tüm telefon numaraları (GSM + sabit) alınır, filtrelenmez.

**Gerekçe (Product Owner):** İşletmenin tüm telefonları değerlidir. Çoklu telefon desteği zorunludur (ör. 1 GSM + 1 sabit). KVKK riski düşüktür çünkü:
- İşletme telefonu "kişisel veri" değil, "ticari iletişim" sayılır.
- Şahıs adı yoksa (info@, kurumsal@) GSM de alınabilir.
- Sorumluluk işletme sahibine aittir; biz aracıyız.

**Veri yapısı:** `telefonler TEXT[]` veya `telefonler JSON` (çoklu alan).

**Hariç tutulanlar:**
- Şahıs isimleri (Ahmet Bey, Mehmet Hanım) → contact person alanına düşmez.
- info@ olmayan bireysel e-postalar (örn. ahmet@gmail.com) → filtrelenir.

**İlgili karar:** [[10_ankara_osb_sentez]] Karar 4 (revize)

## 4. İletişim Bilgisi Kapsam Politikası (2026-09-01 Güncelleme)

**Kural:** İletişim bilgileri Master`````ın en kritik verisidir. Mümkün olan HER alan toplanır, hiçbiri atlanmaz.

**Toplanacak Alanlar (zorunlu):**

| # | Alan | Veri Tipi | Öncelik | KVKK |
|---|---|---|---|---|
| 1 | Telefon (GSM + sabit) | `telefonler: list[str]` | Kritik | Hariç (işletme iletişimi) |
| 2 | E-posta (kurumsal) | `emailler: list[str]` | Kritik | Hariç (kurumsal) |
| 3 | Web sitesi | `web_sitesi: str | None` | Yüksek | Hariç (kamuya açık) |
| 4 | Adres (fiziksel) | `adres: str | None` | Yüksek | Hariç (işyeri adresi) |
| 5 | Sosyal medya | `sosyal_medya: dict[str, str]` | Orta | Hariç (kamuya açık) |
| 6 | Yetkili kişi | `yetkili: dict | None` | Orta | KVKK riskli — UNKNOWN prensibi |
| 7 | Vergi numarası | `vergi_no: str | None` | Yüksek | Hariç (kamuya açık) |

**Filtreleme YAPILMAYACAK alanlar:**
- Telefonlar (GSM dahil tümü)
- Web sitesi
- Adres
- Vergi numarası
- Sosyal medya linkleri

**Filtreleme YAPILACAK alanlar (hafif):**
- E-posta: yalnızca Gmail/Hotmail/Yahoo gibi bireysel sağlayıcılar filtrelenir; kurumsal emailler (herhangi bir şirket domain'i) korunur.
- Yetkili kişi: ad-soyad varsa ama ünvan yoksa → ünvan UNKNOWN yapılır (Master §6 Lint).

**Gerekçe (Product Owner):**
- Müşteri doğrudan iletişime geçebilmeli.
- B2B süreçlerde telefon + e-posta + web sitesi üçlüsü zorunlu.
- Sosyal medya, marka görünürlüğü için ek sinyal.
- Vergi numarası ile diğer kaynaklarla çapraz doğrulama mümkündür.

**İlgili karar:** [[10_ankara_osb_sentez]] Karar 6 (yeni, 2026-09-01)

## 5. Veri Saklama Süreleri

| Veri Türü | Saklama | Silme |
|---|---|---|
| Şirket unvanı, adres, telefon | 5 yıl | Manuel silme |
| Bireysel email (yanlışlıkla girdiyse) | Hemen | Otomatik NULL |
| Şahıs adı (contact person) | Alınmaz | — |
| Log (KVKK ihlal tespiti için) | 2 yıl | Otomatik |

## 6. KVKK İhlal Bildirimi

Veri ihlali tespit edilerse 72 saat içinde KVKK Kurulu'na bildirim yapılır. İhlal logları `audit_log` tablosuna yazılır.

## 7. Onay ve İmza

| Rol | Ad | Tarih |
|---|---|---|
| Product Owner | — | 2026-09-01 (sözlü onay) |
| Veri Sorumlusu | — | (atanacak) |
| Teknik Sorumlu | — | (atanacak) |
