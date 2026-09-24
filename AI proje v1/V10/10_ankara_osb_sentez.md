# Ankara OSB Ekosistemi — Orkestratör Sentez ve Karar



Bağlantılar: [[00-Home]] · [[02_ankara_osb_ekosistemi_arastirma_notu]] · [[10_mvp_kapsam]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]] · [[01_veri_kaynagi_envanteri]] · [[project_state]] · [[CHANGELOG]] · [[TODO]] · [[OSINT_Scraper_Motoru]]



Bu belge, 6 ajanın Ankara OSB Ekosistemi politika önerisine verdikleri yanıtların sentezidir. Orkestratör olarak alınan kararlar ve sonraki adımlar burada sabitlenir.



## Ajan Değerlendirmeleri Özeti



### Koordinatör Ajan

- 13.500+ rakamı yalnız 3 OSB ye dayanıyor; diğer 9 OSB öngörü.

- Bilgi grafı hedefi MVP Faz 0 ı aşıyor, Faz 2+ ya ait.

- **Öneri:** Tek dikey dilim (OSTİM → ASO 1 → İvedik), paralel başlama.



### Mimar Ajan

-Önerideki hiyerarşi (OSB → Firma → ... → Fırsatlar) V10 19 tablo yapısıyla %70 örtüşüyor.

- Eksik tablolar: company_capabilities, certifications, key_personnel, supply_chain.

- **Öneri:** PostgreSQL de bu tabları şimdi ekle, ilişkileri FK ile tanımla, veri zenginleştikçe graf view ları oluştur.



### Araştırmacı Ajan

- 13.500+ rakamının kaynağı 【2-49599e】 — ham OSB sayfası mı, rapor mu? Netleşmedi.

- Üç OSB rakamı yuvarlama; gerçek sayılar değişken olabilir.

- **Öneri:** 1 hafta içinde OSTİM, ASO 1, İvedik web sitelerinden doğrula. Source Reliability 0.50–0.65 arasında.



### Geliştirici Ajan

- 3 OSB web sitesi scraping teknik olarak yapılabilir.

- 13.500+ toplu ingest pipeline ı zorlar.

- **Öneri:** batch_size = 500, her batch sonrası kalite kontrolü. İl gerçek veri **yalnız OSTİM** ile sınırlı, sonra diğer 2 OSB.



### Kalite Ajan

- 13.500+ ham kayıt kalite riski taşır.

- **Öneri:** Faz 1 in %80 i Yüksek Kalite seviyesinde olmalı. Eğer %50 den fazlası Düşük Kalite çıkarsa scraping durdurulup kaynak zenginleştirmesine geçilmeli.



### Web Kazıma Uzmanı

- 3 farklı web sitesi için ayrı analiz gerekli.

- **Yasal uyarı:** Kişisel veri kazınmaz, yalnız kurumsal iletişim.

- **Öneri:** 3 OSB için 30 dakikalık masa başı analiz (robots.txt, kullanım şartları, erişim). Bu yapılmadan ingestion kodu yazılmaz.



## Orkestratör Sentez Kararı



### Karar 1: Faz 1 Skopu Onaylandı

- **Kabul:** Faz 1 = OSTİM + ASO 1 + İvedik = 13.500+ işletme (doğranmış, kaynak 【2-49599e】).

- **Faz 2 = Anadolu + Uzay/Havacılık + Başkent** (Faz 1 başarıya u-laşınca başlar).

- **Faz 3 = Tüm Ankara OSB (13 OSB)** — yalnız diğer 9 OSB nin firma sayıları kamuya açıklandıktan sonra skop netleşir.



### Karar 2: MVP Kapsam Güncellemesi

- V10/10_mvp_kapsam.md Faz 1 skopu **13.500+ işletme** ile güncellenecek.

- Yalnız Ankara + OSB üyesi kuralı korunur.



### Karar 3: Şema Genişletme

- V10 master şemasına aşağıdaki tablolar **MVP Faz 1 de** eklenecek:

  - company_capabilities (yetkinlik)

  - certifications (sertifikalar)

  - key_personnel (karar vericiler)

- İlk üç tablo MVP de; supply_chain (tedarik zincirleri) Faz 2+ ya ertelenebilir.

- Bu tablolar V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3 e eklenir.



### Karar 4: Ingestion Sırası

- **Sıralı ingestion** (paralel değil): OSTİM → ASO 1 → İvedik.

- Her OSB de **batch_size = 500**, batch sonrası data_quality_toolkit.validator ile kalite kontrolü.

- **30 dakikalık masa başı analiz** (Web Kazıma Uzmanı) ingestion kodundan **önce** yapılır.





### Karar 5: Kabul Ölçütü (Kalite Ajan)

- Faz 1 sonunda **toplam kayıtların ≥%60 ı Yüksek Kalite** (LinkedIn + karar verici + ihracat bilgisi olan) olmalı.

- Eğer %50 den fazlası Düşük Kalite çıkarsa ingestion durdurulur ve kaynak zenginleştirmesine geçilir.



#### Karar 6 (yeni, 2026-09-01): İletişim Bilgisi Kapsam Politikası

- **Kural:** İletişim bilgileri Master'''ın en kritik verisidir. Tüm telefon, e-posta, web sitesi, adres, sosyal medya, vergi no toplanır.

- **Toplanacak alanlar:** telefonler[], emailler[], web_sitesi, adres, sosyal_medya{}, vergi_no, osb_parsel, yetkili{}

- **Filtre:** Yalnızca Gmail/Hotmail/Yahoo bireysel email sağlayıcıları filtrelenir. Kurumsal emailler (her domain) korunur.

- **Telefon:** ASLA filtrelenmez (GSM dahil tümü).

- **Etkilenen bileşenler:**

  - \V10/09_kurallar_ve_promptlar/03_kvkk_ve_veri_politikasi.md\ §4 yeni eklendi

  - \src/company_master/etl/scrapers/ostim_scraper.py\ — \OstimFirma\ 7 yeni alan, \etch_firmalar()\ parse güncellendi

  - \src/company_master/schema/companies.sql\ — \web_sitesi\, \ergi_no\, \osb_parsel\ sütunları

- **Onay:** Product Owner (2026-09-01 sözlü)





#### Karar 12 (yeni, 2026-09-01): Veri Kalite Raporu ve İlk Canlı Scrape

- **Tarih:** 2026-09-01

- **Kaynak:** OSTİM /firmalar (1 sayfa)

- **Beklenen:** ~300 firma

- **Çıktı:** data/ostim/firmalar_sayfa1.jsonl

- **Rapor:** data/ostim/kalite_raporu.md

- **Kullanılan kalite skoru:** V10/09_kurallar_ve_promptlar/05_acik_veri_ve_kazina_politikasi.md §6

- **Arayüz:** Streamlit (http://localhost:8501) — canlı veri ile bağlandı

- **Sonraki:** 17 sektör × 200 sayfa → ~6.500 firma (Faz 1A)





#### Karar 13 (yeni, 2026-09-01): Telegram Bot Entegrasyonu

- **Amaç:** Ajan görevlerini ve proje durumunu Telegram'dan anlık takip etmek.

- **Bot:** [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot)

- **Token:** `TELEGRAM_BOT_TOKEN` → `.env` dosyasında saklanır, `.gitignore`'da gizli

- **Chat ID:** `801855376`

- **Bileşenler:**

  - `src/company_master/utils/telegram_bot.py` — bildirim modülü

  - `scripts/telegram_polling.py` — long polling + komut işleyici

  - `V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md` — rehber

- **Komutlar:** `/start`, `/status`, `/gorev`, `/rapor`, `/wiki`, `/help`

- **Otomatik bildirimler:**

  - Görev başladı: `send_task_started()`

  - Görev tamamlandı: `send_task_completed()`

  - Kritik hata: `send_alert()`

  - Günlük özet: `send_daily_summary()`

- **Güvenlik:** Token hiçbir wiki/python dosyasında açık metin olarak saklanmaz; loglarda maskelenir

- **Onay:** Product Owner (2026-09-01)





#### Karar 14 (yeni, 2026-09-01): VPN Kullanımı ve Ağ Hata Yönetimi
- Kullanıcı VPN kullanmaktadır; ağ işlemlerinde VPN kaynaklı hata olabilir.
- Şüpheli durumlarda kullanıcıya bilgi verilir, gerekirse VPN kapatması önerilir.
- Kritik işlemlerde VPN kapatmadan önce kullanıcı onayı alınır.
- Kural dosyası: V10/09_kurallar_ve_promptlar/10_vpn_kurali.md
- Onay: Product Owner (2026-09-01)

## Sonraki Adımlar (Sıralı)



| # | Adım | Sahip | Öncelik |

|---|---|---|---|

| 1 | 3 OSB için 30 dakikalık masa başı analiz (robots.txt, erişim, KVKK) | Web Kazıma Uzmanı | P0 |

| 2 | OSTİM, ASO 1, İvedik web sitelerinden güncel firma sayısı doğrulaması | Araştırmacı Ajan | P0 |

| 3 | Şema genişletme (3 yeni tablo) + 01_sirket_master_ana_belgesi.md §3 güncelleme | Mimar Ajan | P0 |

| 4 | seed_ankara_osb.py → 200 firma yerine OSTİM den 500 gerçek örneklem (placeholder olarak) | Geliştirici Ajan | P1 |

| 5 | etl/pipeline.py ingest_source() implementasyonu | Geliştirici Ajan | P0 |

| 6 | Kalite kontrol kuralları (Yüksek/Orta/Düşük) → data_quality_toolkit.validator extension | Kalite Ajan | P1 |

| 7 | MVP kapsamı güncelleme (13.500+) → V10/10_mvp_kapsam.md | Koordinatör Ajan | P0 |



## Açık Sorular (Araştırmacı Ajan)



- OSTİM güncel firma sayısı 5.000+ mı, daha fazla mı?

- ASO 1 OSB nin 5.500+ rakamı hangi yıla ait?

- Uzay ve Havacılık İhtisas OSB — companies.sql OSB master listesinde yok; eklenecek.

- Elmadağ Mobilyacılar OSB, Şereflikoçhisar OSB, Çubuk Besi OSB — bu OSB ler master listeye eklenecek mi?



## İlgili Wiki Sayfaları



- [[02_ankara_osb_ekosistemi_arastirma_notu]] — L4 kaynak özeti

- [[10_mvp_kapsam]] — MVP kapsamı belgesi

- [[01_sirket_master_ana_belgesi]] — Ana şema belgesi

- [[01_v9_ile_karsilastirma]] — V9 ile V10 karşılaştırması

- [[01_veri_kaynagi_envanteri]] — Kaynak envanteri

- [[08-Ajanlar/README]] — Ajan ekosistemi



## Karar Tarihi



2026-09-01 — Ürün sahibi onayı bekleniyor.


#### Karar 14 (yeni, 2026-09-01): VPN Kullanımı ve Ağ Hata Yönetimi
- Kullanıcı VPN kullanmaktadır; ağ İşlemlerinde VPN kaynaklı hata olabilir.
- Şüpheli durumlarda kullanıcıya bilgi verilir, gerekirse VPN kapatması önerilir.
- Kritik İşlemlerde VPN kapatmadan önce kullanıcı onayı alınır.
- Kural dosyası: V10/09_kurallar_ve_promptlar/10_vpn_kurali.md
- Onay: Product Owner (2026-09-01)

