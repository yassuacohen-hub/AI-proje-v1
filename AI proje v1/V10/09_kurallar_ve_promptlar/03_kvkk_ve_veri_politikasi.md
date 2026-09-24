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



## 4.5 API Dağıtım Katmanı (2026-09-09 Güncelleme, Y7)

**Kapsam:** Veri web'e/istemciye API (`web_app.py`) üzerinden sunulurken uygulanır. Veritabanı saklama katmanı §3 kurallarına tabidir; bu bölüm sunum katmanını düzenler.

### Sunum Katmanı PII Matrisi

| Alan | Varsayılan API | `?mask=1` / `DASH_MASK_PII=1` | Gerekçe |
|---|---|---|---|
| Firma unvanı (legal_name) | Tam | Tam | Kamuya açık (ticaret sicili) |
| Ticaret adı (trade_name) | Tam | Tam | Türetilmiş, kamuya açık |
| Web sitesi | Tam | Tam | Kamuya açık |
| VKN / vergi_no | Tam | Tam | Kamuya açık (GİB sorgulaması) |
| NACE / parsel | Tam | Tam | Kayıt verisi |
| **Telefon** (primary_phone) | Tam | **Maske** `053***67` | Ticari iletişim amaçlı; minimizasyon seçeneği |
| **E-posta** (primary_email) | Tam | **Maske** `ah***@domain.com` | Minimizasyon seçeneği; bireysel sağlayıcılar DB'de zaten NULL (§3.1) |

### Kurallar

1. **Maskeleme iki anahtarlıdır:** `DASH_MASK_PII=1` env'si (tüm istekler, müşteri dağıtım ortamı için) veya istek bazlı `?mask=1` (önizleme/deneme erişimi). İkisinden biri aktifse `apply_kvkk_mask` uygulanır.
2. **Kapsam:** `/api/companies`, `/api/companies/export`, `/api/company/{id}` — telefon ve e-posta maskelenir; unvan/web/VKN dokunulmadan döner (PO kararı §4: bu alanlar kamuya açık).
3. **Önbellek ayrımı:** maske durumu cache anahtarına dahildir (`mask=True/False`); maskeli ve maskesiz yanıtlar karışmaz.
4. **Bireysel e-posta = veri girişi hatası:** DB'de gmail/hotmail/yahoo/yandex/outlook/icloud kalması §3.1 ihlalidir. `scripts/kvkk_email_temizle.py` yedek tablo (`kvkk_bireysel_email_yedek`) alarak temizler; 2026-09-09 çalıştırıldı.
5. **Şahıs adı API'de yoktur:** `company_contacts` yalnızca iletişim kanalı tipi tutar (§3 kural 3 ile uyumlu).
6. **Denetim:** Maskeleme değişikliği ve temizlik koşumları `docs/CALISMA_GUNLUGU.md`'ye işlenir.

### Müşteri Senaryoları

- **Deneme/önizleme müşterisi:** API `?mask=1` ile verilir → veri değerini görür, toplu kazıyamaz (ayrıca rate limit Y6).
- **Ücretli lisans:** `DASH_MASK_PII=0` → tam iletişim verisi.
- **Kurumsal paylaşım:** `DASH_MASK_PII=1` sabitlenmiş dağıtım → içinde yetkili olmayanlara dahi güvenli.




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

