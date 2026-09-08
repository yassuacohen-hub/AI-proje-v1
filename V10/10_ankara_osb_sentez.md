# Ankara OSB Ekosistemi â OrkestratÃ¶r Sentez ve Karar



BaÄantÄ±lar: [[00-Home]] Â· [[02_ankara_osb_ekosistemi_arastirma_notu]] Â· [[10_mvp_kapsam]] Â· [[01_sirket_master_ana_belgesi]] Â· [[01_v9_ile_karsilastirma]] Â· [[01_veri_kaynagi_envanteri]] Â· [[project_state]] Â· [[CHANGELOG]] Â· [[TODO]] · [[OSINT_Scraper_Motoru]]



Bu belge, 6 ajanÄ±n Ankara OSB Ekosistemi politika Ã¶nerisine verdikleri yanÄ±tlarÄ±n sentezidir. OrkestratÃ¶r olarak alÄ±nan kararlar ve sonraki adÄ±mlar burada sabitlenir.



## Ajan DeÄerlendirmeleri Ãzeti



### KoordinatÃ¶r Ajan

- 13.500+ rakamÄ± yalnÄ±z 3 OSB ye dayanÄ±yor; diÄer 9 OSB Ã¶ngÃ¶rÃ¼.

- Bilgi grafÄ± hedefi MVP Faz 0 Ä± aÅÄ±yor, Faz 2+ ya ait.

- **Ãneri:** Tek dikey dilim (OSTÄ°M â ASO 1 â Ä°vedik), paralel baÅlama.



### Mimar Ajan

-Ãnerideki hiyerarÅi (OSB â Firma â ... â FÄ±rsatlar) V10 19 tablo yapÄ±sÄ±yla %70 Ã¶rtÃ¼ÅÃ¼yor.

- Eksik tablolar: company_capabilities, certifications, key_personnel, supply_chain.

- **Ãneri:** PostgreSQL de bu tablarÄ± Åimdi ekle, iliÅkileri FK ile tanÄ±mla, veri zenginleÅtikÃ§e graf view larÄ± oluÅtur.



### AraÅtÄ±rmacÄ± Ajan

- 13.500+ rakamÄ±nÄ±n kaynaÄÄ± ã2-49599eã â ham OSB sayfasÄ± mÄ±, rapor mu? NetleÅmedi.

- ÃÃ§ OSB rakamÄ± yuvarlama; gerÃ§ek sayÄ±lar deÄiÅken olabilir.

- **Ãneri:** 1 hafta iÃ§inde OSTÄ°M, ASO 1, Ä°vedik web sitelerinden doÄrula. Source Reliability 0.50â0.65 arasÄ±nda.



### GeliÅtirici Ajan

- 3 OSB web sitesi scraping teknik olarak yapÄ±labilir.

- 13.500+ toplu ingest pipeline Ä± zorlar.

- **Ãneri:** batch_size = 500, her batch sonrasÄ± kalite kontrolÃ¼. Ä°l gerÃ§ek veri **yalnÄ±z OSTÄ°M** ile sÄ±nÄ±rlÄ±, sonra diÄer 2 OSB.



### Kalite Ajan

- 13.500+ ham kayÄ±t kalite riski taÅÄ±r.

- **Ãneri:** Faz 1 in %80 i YÃ¼ksek Kalite seviyesinde olmalÄ±. EÄer %50 den fazlasÄ± DÃ¼ÅÃ¼k Kalite Ã§Ä±karsa scraping durdurulup kaynak zenginleÅtirmesine geÃ§ilmeli.



### Web KazÄ±ma UzmanÄ±

- 3 farklÄ± web sitesi iÃ§in ayrÄ± analiz gerekli.

- **Yasal uyarÄ±:** KiÅisel veri kazÄ±nmaz, yalnÄ±z kurumsal iletiÅim.

- **Ãneri:** 3 OSB iÃ§in 30 dakikalÄ±k masa baÅÄ± analiz (robots.txt, kullanÄ±m ÅartlarÄ±, eriÅim). Bu yapÄ±lmadan ingestion kodu yazÄ±lmaz.



## OrkestratÃ¶r Sentez KararÄ±



### Karar 1: Faz 1 Skopu OnaylandÄ±

- **Kabul:** Faz 1 = OSTÄ°M + ASO 1 + Ä°vedik = 13.500+ iÅletme (doÄranmÄ±Å, kaynak ã2-49599eã).

- **Faz 2 = Anadolu + Uzay/HavacÄ±lÄ±k + BaÅkent** (Faz 1 baÅarÄ±ya u-laÅÄ±nca baÅlar).

- **Faz 3 = TÃ¼m Ankara OSB (13 OSB)** â yalnÄ±z diÄer 9 OSB nin firma sayÄ±larÄ± kamuya aÃ§Ä±klandÄ±ktan sonra skop netleÅir.



### Karar 2: MVP Kapsam GÃ¼ncellemesi

- V10/10_mvp_kapsam.md Faz 1 skopu **13.500+ iÅletme** ile gÃ¼ncellenecek.

- YalnÄ±z Ankara + OSB Ã¼yesi kuralÄ± korunur.



### Karar 3: Åema GeniÅletme

- V10 master ÅemasÄ±na aÅaÄÄ±daki tablolar **MVP Faz 1 de** eklenecek:

  - company_capabilities (yetkinlik)

  - certifications (sertifikalar)

  - key_personnel (karar vericiler)

- Ä°lk Ã¼Ã§ tablo MVP de; supply_chain (tedarik zincirleri) Faz 2+ ya ertelenebilir.

- Bu tablolar V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md Â§3 e eklenir.



### Karar 4: Ingestion SÄ±rasÄ±

- **SÄ±ralÄ± ingestion** (paralel deÄil): OSTÄ°M â ASO 1 â Ä°vedik.

- Her OSB de **batch_size = 500**, batch sonrasÄ± data_quality_toolkit.validator ile kalite kontrolÃ¼.

- **30 dakikalÄ±k masa baÅÄ± analiz** (Web KazÄ±ma UzmanÄ±) ingestion kodundan **Ã¶nce** yapÄ±lÄ±r.





### Karar 5: Kabul ÃlÃ§Ã¼tÃ¼ (Kalite Ajan)

- Faz 1 sonunda **toplam kayÄ±tlarÄ±n â¥%60 Ä± YÃ¼ksek Kalite** (LinkedIn + karar verici + ihracat bilgisi olan) olmalÄ±.

- EÄer %50 den fazlasÄ± DÃ¼ÅÃ¼k Kalite Ã§Ä±karsa ingestion durdurulur ve kaynak zenginleÅtirmesine geÃ§ilir.



#### Karar 6 (yeni, 2026-09-01): Ä°letiÅim Bilgisi Kapsam PolitikasÄ±

- **Kural:** Ä°letiÅim bilgileri Master'''Ä±n en kritik verisidir. TÃ¼m telefon, e-posta, web sitesi, adres, sosyal medya, vergi no toplanÄ±r.

- **Toplanacak alanlar:** telefonler[], emailler[], web_sitesi, adres, sosyal_medya{}, vergi_no, osb_parsel, yetkili{}

- **Filtre:** YalnÄ±zca Gmail/Hotmail/Yahoo bireysel email saÄlayÄ±cÄ±larÄ± filtrelenir. Kurumsal emailler (her domain) korunur.

- **Telefon:** ASLA filtrelenmez (GSM dahil tÃ¼mÃ¼).

- **Etkilenen bileÅenler:**

  - \V10/09_kurallar_ve_promptlar/03_kvkk_ve_veri_politikasi.md\ Â§4 yeni eklendi

  - \src/company_master/etl/scrapers/ostim_scraper.py\ â \OstimFirma\ 7 yeni alan, \etch_firmalar()\ parse gÃ¼ncellendi

  - \src/company_master/schema/companies.sql\ â \web_sitesi\, \ergi_no\, \osb_parsel\ sÃ¼tunlarÄ±

- **Onay:** Product Owner (2026-09-01 sÃ¶zlÃ¼)





#### Karar 12 (yeni, 2026-09-01): Veri Kalite Raporu ve Ä°lk CanlÄ± Scrape

- **Tarih:** 2026-09-01

- **Kaynak:** OSTÄ°M /firmalar (1 sayfa)

- **Beklenen:** ~300 firma

- **ÃÄ±ktÄ±:** data/ostim/firmalar_sayfa1.jsonl

- **Rapor:** data/ostim/kalite_raporu.md

- **KullanÄ±lan kalite skoru:** V10/09_kurallar_ve_promptlar/05_acik_veri_ve_kazina_politikasi.md Â§6

- **ArayÃ¼z:** Streamlit (http://localhost:8501) â canlÄ± veri ile baÄlandÄ±

- **Sonraki:** 17 sektÃ¶r Ã 200 sayfa â ~6.500 firma (Faz 1A)





#### Karar 13 (yeni, 2026-09-01): Telegram Bot Entegrasyonu

- **AmaÃ§:** Ajan gÃ¶revlerini ve proje durumunu Telegram'dan anlÄ±k takip etmek.

- **Bot:** [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot)

- **Token:** `TELEGRAM_BOT_TOKEN` â `.env` dosyasÄ±nda saklanÄ±r, `.gitignore`'da gizli

- **Chat ID:** `801855376`

- **BileÅenler:**

  - `src/company_master/utils/telegram_bot.py` â bildirim modÃ¼lÃ¼

  - `scripts/telegram_polling.py` â long polling + komut iÅleyici

  - `V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md` â rehber

- **Komutlar:** `/start`, `/status`, `/gorev`, `/rapor`, `/wiki`, `/help`

- **Otomatik bildirimler:**

  - GÃ¶rev baÅladÄ±: `send_task_started()`

  - GÃ¶rev tamamlandÄ±: `send_task_completed()`

  - Kritik hata: `send_alert()`

  - GÃ¼nlÃ¼k Ã¶zet: `send_daily_summary()`

- **GÃ¼venlik:** Token hiÃ§bir wiki/python dosyasÄ±nda aÃ§Ä±k metin olarak saklanmaz; loglarda maskelenir

- **Onay:** Product Owner (2026-09-01)





#### Karar 14 (yeni, 2026-09-01): VPN KullanÄ±mÄ± ve AÄ Hata YÃ¶netimi
- KullanÄ±cÄ± VPN kullanmaktadÄ±r; aÄ iÅlemlerinde VPN kaynaklÄ± hata olabilir.
- ÅÃ¼pheli durumlarda kullanÄ±cÄ±ya bilgi verilir, gerekirse VPN kapatmasÄ± Ã¶nerilir.
- Kritik iÅlemlerde VPN kapatmadan Ã¶nce kullanÄ±cÄ± onayÄ± alÄ±nÄ±r.
- Kural dosyasÄ±: V10/09_kurallar_ve_promptlar/10_vpn_kurali.md
- Onay: Product Owner (2026-09-01)

## Sonraki AdÄ±mlar (SÄ±ralÄ±)



| # | AdÄ±m | Sahip | Ãncelik |

|---|---|---|---|

| 1 | 3 OSB iÃ§in 30 dakikalÄ±k masa baÅÄ± analiz (robots.txt, eriÅim, KVKK) | Web KazÄ±ma UzmanÄ± | P0 |

| 2 | OSTÄ°M, ASO 1, Ä°vedik web sitelerinden gÃ¼ncel firma sayÄ±sÄ± doÄrulamasÄ± | AraÅtÄ±rmacÄ± Ajan | P0 |

| 3 | Åema geniÅletme (3 yeni tablo) + 01_sirket_master_ana_belgesi.md Â§3 gÃ¼ncelleme | Mimar Ajan | P0 |

| 4 | seed_ankara_osb.py â 200 firma yerine OSTÄ°M den 500 gerÃ§ek Ã¶rneklem (placeholder olarak) | GeliÅtirici Ajan | P1 |

| 5 | etl/pipeline.py ingest_source() implementasyonu | GeliÅtirici Ajan | P0 |

| 6 | Kalite kontrol kurallarÄ± (YÃ¼ksek/Orta/DÃ¼ÅÃ¼k) â data_quality_toolkit.validator extension | Kalite Ajan | P1 |

| 7 | MVP kapsamı gÃ¼ncelleme (13.500+) â V10/10_mvp_kapsam.md | KoordinatÃ¶r Ajan | P0 |



## AÃ§Ä±k Sorular (AraÅtÄ±rmacÄ± Ajan)



- OSTÄ°M gÃ¼ncel firma sayÄ±sÄ± 5.000+ mÄ±, daha fazla mÄ±?

- ASO 1 OSB nin 5.500+ rakamÄ± hangi yÄ±la ait?

- Uzay ve HavacÄ±lÄ±k Ä°htisas OSB â companies.sql OSB master listesinde yok; eklenecek.

- ElmadaÄ MobilyacÄ±lar OSB, ÅereflikoÃ§hisar OSB, Ãubuk Besi OSB â bu OSB ler master listeye eklenecek mi?



## Ä°lgili Wiki SayfalarÄ±



- [[02_ankara_osb_ekosistemi_arastirma_notu]] â L4 kaynak Ã¶zeti

- [[10_mvp_kapsam]] â MVP kapsamı belgesi

- [[01_sirket_master_ana_belgesi]] â Ana Åema belgesi

- [[01_v9_ile_karsilastirma]] â V9 ile V10 karÅÄ±laÅtÄ±rmasÄ±

- [[01_veri_kaynagi_envanteri]] â Kaynak envanteri

- [[08-Ajanlar/README]] â Ajan ekosistemi



## Karar Tarihi



2026-09-01 â ÃrÃ¼n sahibi onayÄ± bekleniyor.


#### Karar 14 (yeni, 2026-09-01): VPN Kullanýmý ve Að Hata Yönetimi
- Kullanýcý VPN kullanmaktadýr; að Ýþlemlerinde VPN kaynaklý hata olabilir.
- Þüpheli durumlarda kullanýcýya bilgi verilir, gerekirse VPN kapatmasý önerilir.
- Kritik Ýþlemlerde VPN kapatmadan önce kullanýcý onayý alýnýr.
- Kural dosyasý: V10/09_kurallar_ve_promptlar/10_vpn_kurali.md
- Onay: Product Owner (2026-09-01)

