# Admin Panel Kullanim Kilavuzu

*Olusturma: 2026-09-13 | Son guncelleme: 2026-09-13*

---

## Genel Bakis

Admin paneli Streamlit uzerinden calisir: `http://localhost:8501`
7 sekme + 1 sidebar navigasyonu var. Her sekme bir metrik kategorisini gosterir.

## Sekmeler ve Ne Isle Yarar

| Sekme | Ne Goruer | Bossta Ne Anlama Gelir |
|---|---|---|
| **Ana Kontrol** | Toplam firma, aktif musteri, sistem sagligi, aylik maliyet | Veri yuklenmiyor — backend endpoint calismiyor olabilir |
| **Musteriler** | Firma listesi, filtre, VKN, kalite skoru | Firma verisi yok — scraper henuz calismadi |
| **Sistem** | API maliyeti, performans, analitik, DLQ, webhook durumu | Hedef sistem veri cekmiyor |
| **Paketler** | Paket CRUD, firma-paket atamasi | Demo veri yuklenmedi |
| **Pazarlama** | Kampanya, capraz satis onerileri | Henuz paket verisi yok |
| **Abrakadabra** | AI chat — sorgu + orkestrator komutlari | 9router baglanti hatasi |
| **Yonetim** | API key, audit log, export | Kurulmamis |

## Navigasyon

- Sol sidebar: sekme gecisi
- Ust: yenile butonu + "Son guncelleme" zamani
- Her kartta hover: detay tooltip

## Metrikler Hakkinda

Her metrik basliginin altinda kisa aciklama yazmal — hangi veriye dayandigini ve neye yararin goster.

## Dikkat Edilenler

- Bos grafik yerine "Veri yuklenince burada..." placeholder goster
- Abrakadabra'daki orkestrator komutlari onayla/reddet tusu olmadan calisir (yalnizca oneri uretir)
- Kota uyarisı: maliyet %80 ustunde ses calar

## Ilgili Sayfalar

- [[00_sentez]] — tasim brifi
- [[brif_roo]] — UX brifi
- [[brif_kilo]] — backend brifi
- [[DASH-UX-01]] — ana tasim grevi

---
*Bu sayfa orkestrator tarafindan otomatik guncellenir.*

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
