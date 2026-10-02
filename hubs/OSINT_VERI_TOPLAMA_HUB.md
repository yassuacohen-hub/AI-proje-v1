# OSINT / Veri Toplama Hub

> Konu-bazli hub (PO karari 2026-09-21): Veri kaynagi kesfi, scraping motoru, OSINT
> arastirmalari ve toplama politikalari tek noktada. Yurutme raporlari dahil degildir —
> yalnizca kaynak/mimari/arastirma/politika seviyesi belgeler secildi.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **18**

Ana baglam: [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---

## Motor / Sistem Referansi
- [[Huginn Data Insights/docs/OSINT_SCRAPER_MOTORU]] — Ana referans: scraper motoru mimarisi
- `Huginn Data Insights/AI proje v1/V10/11_osint_motoru/OSINT_Scraper_Motoru` — V10 motor tasarimi
- `Huginn Data Insights/AI proje v1/V10/11_osint_motoru/Orkestrator` — OSINT orkestratoru
- [[Huginn Data Insights/docs/v10_OSINT_YETENEK_KATALOGU]] — Yetenek katalogu

## Veri Kaynaklari / Envanter
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/01_veri_kaynagi_envanteri` — Kaynak envanteri
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/04_web_kazima_kaynak_arastirmasi` — Web kazima kaynaklari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/08_gib_vergino_sorgu_stratejisi` — GIB vergi no sorgu stratejisi
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/vkn_bulma_stratejisi` — VKN bulma stratejisi
- [[Huginn Data Insights/docs/P7-6_kariyernet_arastirma]] — Kariyer.net kaynak arastirmasi

## OSB / Saha Arastirmalari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/02_ankara_osb_ekosistemi_arastirma_notu` — Ankara OSB ekosistemi
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/02_ankara_osb_erisim_planlari` — OSB erisim planlari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/03_osb_masa_basi_analizi` — OSB masa basi analizi

## Entegrasyon / Arac Arastirmalari
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/10_apify_entegrasyon_arastirmasi_20260910` — Apify entegrasyonu
- `Huginn Data Insights/AI proje v1/V10/07_referanslar/11_apify_mcp_entegrasyon` — Apify MCP entegrasyonu
- [[Huginn Data Insights/docs/P2-3_zamanli_scrape]] — Zamanli scrape tasarimi

## Politika / Rol / Kalite
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/05_acik_veri_ve_kazina_politikasi` — Acik veri ve kazima politikasi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/09_osint_rol_tanimi` — OSINT rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/06_web_kazima_uzmani` — Web kazima uzmani ajani
- `Huginn Data Insights/AI proje v1/V10/12_kalite_metrikleri/01_kalite_skoru_ek_metrikleri` — Kalite skoru metrikleri

---

## Ticaret Sicili / Kanit Katmani
- `Huginn Data Insights/plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` — TOBB kanit arastirmasi (EK-1 §16-23 canli dogrulama, EK-2 §24-28 Duzey_3)
- `Huginn Data Insights/skills/services/ticaret_sicili_kanit.py` — IlanKaniti kanit kapisi (MERSIS->VKN tek kapı: `kimlik_no.py`)
- `Huginn Data Insights/scripts/tobb_oturum.py` — Dogrudan TOBB oturumu (e-Devlet yok, multipart login D-276)
- `Huginn Data Insights/scripts/pdf_kanit_analiz.py` — PDF scan mı metin katmanı mı ayırt eder (D-277/D-278)
- `Huginn Data Insights/scripts/gazete_ocr.py` — **PASIF** (D-278): vision-LLM OCR, silinmedi, `--aktif` ile açılır
- `Huginn Data Insights/data/pdf_analiz.json` — Ölçüm kanıtı (font=0, Tj=0, 3 gorsel XObject)

**Kaynak farkı (ölçülmüş):** TOBB *ücretsiz üye PDF'i* taranmış görsel (OCR şart);
*abonelik verisi* (Düzey_2/3) **WEB SERVİS / TSM-XML** makine-okunur (OCR gerekmez).
Düzey_3 = 1.427.688 TL/yıl; NACE + Vergi No + Ortaklar + Temsilciler kapsar.

## Kapanan isler

| TASK_ID | Sonuc | Tarih |
|---|---|---|
| VERI-OSB-TEMIZLIK-01 | **OSB veri seti temizlendi (3 karar ihsan onayıyla 2026-10-02).** `KIMLIKSIZ 647 → 144` (503 slug üretildi), **SILINEN KAYIT 0** (D-262), `TOPLAM kayit` 8987 sabit. **TERİM SORUSU ÇÖZÜLDÜ:** "bayi/büyüme/çoklu merkez" üçü de değil — doğru kavram **`company_locations.location_type` = `factory` (tesis)**; zaten şemada var (`0002_relations.sql`). SSOT kanıtı: `bayi`=`(HUGIns).txt:669` mağaza/şube sayacı, `merkez`=`:745/:913` SaaS paneli, `büyüme`=trend göstergesi — **üçü de OSB üyeliğini tanımlamıyor.** **ÖLÇÜM KARAR DÜZELTTİ:** 44 grubun 44'ünde de adres **birebir aynı** (`anadolu`+`ostim` → ikisi de 'BAĞDAT CAD. 396') → bunlar "iki OSB üyeliği" değil, **aynı fiziksel tesisin iki klasörde kopyası** (veri hatası). Bu yüzden `company_slug` global tekillik **doğru** kimliktir, OSB üyeliği değil. Uygulama: aynı slug+aynı adres → kopya `tekillestirildi` ile **KORUNDU** (silinmedi); farklı adres → `slug_cakismasi` ile **KORUNDU** (7 kayıt/4 slug); 144 bozuk kodlamalı satır (`aso_full_clean.jsonl`, `?` içeren) → slug **ÜRETİLMEDİ**, `slug_durumu` ile işaretlendi. **DENETİM KÖR NOKTASI:** `osb_veri_denetim.py:44` yalnız `\ufffd` arıyor, bu satırlarda `?` var → `MOJIBAKE: 0` deyip 144 satırı kör geçiyordu. **Kaza kaydı (D-244):** aracın varsayılanı yazıyordu, 12 dosya değişti; `git checkout` ile geri alındı, varsayılan KURU yapıldı (`--yaz` ile yazılır). `--self` → `self-check OK`. Kalıcı araç: `scripts/osb_veri_temizle.py` (R1). **Kabul kriteri `KIMLIKSIZ: 0` sağlanmadı** — 144 satır gerekçeli bırakıldı. Rapor: `data/orchestrator/osb_temizlik_raporu_2026-10-01.md` | 2026-10-02 |
| VERI-OSB-Tazelik-01 | 13 Ankara OSB icin ayri veri seti uretildi: 8.987 kayit (data/osb/). Polatli Ticaret tarandi (+8 firma). Supabase YAZILMADI - onay bekliyor. 3 site DNS cozulmuyor, Sereflikochisar liste yayinlamiyor. Rapor: data/orchestrator/osb_rapor_2026-09-29.md | 2026-09-29 |
| VERI-TOBB2B-KESISIM-01 | SANAYI/TOBB2B degerlendirmesi genisletildi. **lonca.gov.tr eklendi:** Sanayi Sicil Belgesi Sorgulama (ihracatci katalog). GET 7/7 acik ama **POST 3/3 WAF reddi** -> tarama YAPILAMAZ; ayrica bize unvan/vergi/mersis/sicil vermiyor. Degeri: **254 NACE alt-bolum kodu / 30 bolum, GET ile ACIK** (`lonca_nace_kodlari.json`). Pilot dogrulandi: 11 eslesen teklifin bolumlerinin hepsi var, 9 eslesmeyenin 15 bolumu hic yok -> eslesmemeler imalat disi, bagimsiz devlet kaynagiyla teyit edildi. sanayi.org.tr: 28 API 401 -> kamuya acik veri YOK. tobb2b.org.tr: SSL gecersiz ama http:// 200, teklif_goster.php acik. PILOT: 20 teklif, 11/20 eslesti, 1.575 firma. **NACE kodu %0.1 dolu** -> eslestirme metinle kurulur. Cikti: data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json | 2026-09-30 |
| TSG-PILOT-20 | **7 kalemin 7si sayiyla doldu.** 20/20 firma, 320 ilan, 0 hata. 1) CAPTCHA 1/1 (GIRIS basina zorunlu, sorgu basina degil). 2) Oturum 9,9 sn / 20 sorgu dustu. 3) Sure min 0,29 / medyan 0,37 / maks 1,54 sn -> 10 dk SLA'da ~1.600 firma. 4) **ILAN TURU ETIKETLERI: 65 cesit / 320 adet** (ILAN_TURU_ESLEME buradan dolar; 3 yazim bicimi var, birlestirme TSG-04'e kalmali). 5) **Icra/iflas ayri kutu YOK** - sadece etiket icinde. 6) Tarih araligi DESTEKLENIYOR (Tarih1/Tarih2), siniri bilinmiyor. 7) **sicil->VKN 0/20 (%0)** - ucretsiz katmanda VKN/MERSIS sutunu YOK, yapisal olarak kapanmiyor. Yan bulgu: sunucu CAPTCHA'yi 'Content-Type: text/html' gonderiyor ama govde gercek PNG. Test 65 passed 0 failed. Kanit 320 dosya. Rapor: plans/rapor_yasu_TSG-PILOT-20.md | 2026-09-30 |
| VERI-LONCA-FIRMA-01 | **KAHIN ekran goruntusu tespitimi DOGRULADI: /FirmaBilgisi?Id= ucu GET ile veri veriyor** (onceki "tarama yapilamaz" tespiti eksikti - o uc hic denenmemisti). TAM Id ile HTTP 200, 94.090 bayt, 0,38 sn; **7 alanin 6si doldu** (unvan, il, adres, telefon, faks, eposta) - sayfanin id etiketleriyle (#firmaAdi, #ilAdi, #firmaAdresi, #firmaTel, #firmaFaks). web alani YANLIS: www.w3.org (meta'dan yakalanmis, duzeltilmedi). Urun katalogu 9 satir ama bunlar URETIM URUNLERI, NACE degil - sayfada NACE kodu YOK. POST /Ara WAF 3/3 red. **NACE BULGUSU: eski kayit BAYAT - nace_code 8.289/9.412 = %88,1 dolu (261 cesit); gelistirmek gerekmiyor.** AMA KALITE: sector_default 5.679 (%60,3 kanit DEGIL) + unknown 2.504 (%26,6) = 3.158 firma %33,5 kanitsiz, olculmus ~%66. Lonca 254 NACE kodu/30 bolum (bizim 261 koddan 171'i kapsamda) dogrulama sozlugu olarak ise yarar. Rapor: plans/rapor_yasu_VERI-LONCA-FIRMA-01.md | 2026-09-30 |
| VERI-RAG-KORPUS-01 | Firma satirlari aranabilir metne cevrildi. **9412 kayit / 9412 tekil firma** uretildi (canli Supabase olcumu, D-238); **hata 0**. Metin uzunlugu **ortanca 213 karakter** (50 orneklemde 215; esik >= 80). **Kisisel veri sizintisi 0** — 9412 metnin tamami TCKN/telefon/e-posta deseniyle tarandi, 0 eslesme. Chunk **gerekmiyor**: medyan 213 olsa da **maksimum 306 karakter**; embedder penceresi (448) icin **0 / 9412** kayit asilir. Brief'in 200 karakter isareti sorusu "%67,6 gecer" der ama karar veren esik embedder penceresidir, keyfi bir isaret degil. Beyaz liste 10 kolon (siyah liste yok); `description` cikarildi (632 dolunun 624'u adres deseni), `sector_name` kullanildi (7595 dolu, adres deseni 0). Her metin kaynak kunyesi tasiyor (firma_id + kaynak + tarih) — kunyesiz kayit uretilemiyor. Mandal 57 test, **iki kez kirilarak dogrulandi**: kunye kaldirilunca 8, beyaz listeye `primary_email` eklenince 1 test kirmizi. Chunk basina tekil: kaynak_kaydi. Rapor: data/orchestrator/VERI-RAG-KORPUS-01_rapor_2026-10-02_uretim.md | 2026-10-02 |
| VERI-TSG-ESLEME-CASE-01 | **Varsayim olculdu ve yanlis bulundu; canli tablo geri dolduruldu.** Brif'in `306/326 NULL` iddiasinin gercek sebebi eslesme basarisizligi degil, **306 kanit dosyasinin `il_turu` alaninin bos olmasi**; bu kayitlarda etiketlenecek metin yok. Eski katlama turkce harfleri (`ı ş ğ ü ö ç`) sessizce yutuyordu: `Artirimı`->`ARTRM`, `Sube Acilis`->`SUBE ACLS`. `_TR_ASCII` harf eslemeleri duzeltildi, `ILAN_TURU_ESLEME` **olculmus 17 tam `il_turu` degeriyle** tanimlandi. Kanitta etiketlenen 13 -> **20** (+7). **Ikinci katman (D-261: kod yazildi != kosturuldu):** eski esleme canli `company_events` tablosuna yazilmisti; `tsg_yazici` `source_guid`'i mevcut sayip atladigi icin (407/407) yeniden kosmak **hicbir sey duzeltmezdi**. Olcum: **19 satiri** duzeltilecek, yedek `yedekler/company_events_esleme_20261002.jsonl` (19 satir) alindi, sonra uygulandi: `event_type IS NULL` **404 -> 387**. Bos `il_turu` kayitlari dogru olarak NULL kaldi. Idempotency kaniti: ikinci kosu **0 yazilacak**. Zincir kaniti: 326 kanit dosyasi -> 0 hata. Test **75 passed** (5 yeni mandal: geri dosyasi degeri gozlemez, prova yazmaz). Kanit dosyalari: `scripts/tsg_esleme_geri_doldurma_olcumu.py`, `scripts/tsg_esleme_geri_doldur.py`, `scripts/tsg_esleme_mandal_kirma_denemesi.py`. | 2026-10-02 |

## Ilgili Nodlar (Ust Hub)
- [[Huginn Data Insights/hubs/OSINT_INDEX]]
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]

## Düşürülen Kaynaklar
| Kaynak | Karar | Neden | Tarih |
|---|---|---|---|
| IVEDIK | **KAYNAK LİSTESİNDEN DÜŞÜRÜLDÜ** | Site bot koruması arkasında; 4 yöntem denendi (D-299), hiçbiri açmadı. Elidedeki veri 14 tekil firma + %0 alan = kullanılamaz. Yeni çekim yapılmayacak. Kayıt: `data/ivedik/kaynaktan_dusuruldu.json` | 2026-09-29 |
