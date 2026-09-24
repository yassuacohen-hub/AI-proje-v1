# 00-Home

Bu vault, proje bağlamı, mimari, özellikler, kararlar, hata notları, araştırma, görevler ve ajan yapısını tek bir merkezden yönetmek için oluşturulmuştur.

## Ana bölümler

- 00_ana_belgeler — [[01_sirket_master_ana_belgesi]]
  - Marka konumlandırma — [[03_marka_konumlandirma_ve_kapsam]] · Huginn/Muninn/Odin kimliği, sloganlar, görsel kimlik
- 01_gereksinimler — [[01_mvp_gereksinimleri]]
- 02_is_modeli — [[01_veri_toplama_modeli]]
- 03_mimari — [[01_etl_mimarisi]] · [[02_muninn_super_admin_panel_prd_ve_yol_haritasi]] · [[06_muninn_prd_vs_huginn_analiz]]
- Ürün yüzeyleri (sitemap) — [[14_urun_yuzeyleri_sitemap]] · Huginn (8000, müşteri) + Muninn (8501, iç ekip) menü ağacı
- 04_karşılaştırmalar — [[01_v9_ile_karsilastirma]]
- 05_versiyonlar — [[01_versiyon_6_baglam_dokumani]] · [[01_versiyon_7_baglam_dokumani]] · [[01_versiyon_8_baglam_dokumani]] · [[01_versiyon_9_baglam_dokumani]]
- 06_arsiv — [[06_arsiv/README]]
- 07_referanslar — [[01_veri_kaynagi_envanteri]] · [[02_ankara_osb_erisim_planlari]] · [[06_nvidia_skills_arastirmasi]] · [[10_apify_entegrasyon_arastirmasi_20260910]] · [[vkn_bulma_stratejisi]] · [[09_proje_denetimi_2026-09-09]]
- 08-Ajanlar — [[08-Ajanlar/README]]
- 09_kurallar_ve_promptlar — [[09_kurallar_ve_promptlar/README]] · [[01_kasa_kurallari]] · [[02_calisma_kurallari]] · [[03_prompt_kutuphanesi]] · [[04_token_verimliligi_ve_dil_politikasi]] · [[09_telegram_bot_rehberi]] · [[10_vpn_kurali]] · [[11_unvan_kisaltma_ve_tabela_kurallari]]
- 11_osint_motoru — [[OSINT_Scraper_Motoru]] · [[Orkestrator]]
- 12_kalite_metrikleri — [[01_kalite_skoru_ek_metrikleri]]
- Ana belgeler — [[README]] · [[01_sirket_master_ana_belgesi]] · [[02_hugins_master_kaynak_dokumani]]
- Hafıza katmanı — [[project_state]] · [[TODO]] · [[CHANGELOG]]
- MVP kapsamı — [[10_mvp_kapsam]]

## Rapor Hub'ları

Proje raporları, denetim çıktıları, metrikler ve analiz dokümantasyonu merkezi noktalardan yönetilir:

- **[[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB|Reports & Analysis Hub]]** — Görev raporları, denetim çıktıları, metrikleri ve analiz dokümantasyonun ana merkezi. Proje durumu, sprint bulguları, kalite raporları ve performans metrikleri burada bağlıdır.
- **[[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB|Technical Docs Hub]]** — Teknik dokümantasyon, mimari kararlar, kod yapısı rehberleri ve geliştirme standartları. Teknik derinlik ve referans materyali buradan ulaşılır.
- **[[Huginn Data Insights/hubs/VERI_KALITESI_HUB|Veri Kalitesi Hub]]** — Veri doğrulama, kalite metrikleri, veri enrichment prosedürleri ve kalite kontrol görevleri.
- **[[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB|Plan & Strategy Hub]]** — Proje yol haritası, stratejik kararlar, sprint planlama ve ürün vizyonu.
- **[[Huginn Data Insights/hubs/OSINT_INDEX|OSINT & Data Hub]]** — Veri kaynağı envanteri, OSINT stratejileri, veri toplama araçları ve entegrasyon kılavuzları.
- **[[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB|Tools & Scripts Hub]]** — Otomasyon araçları, yardımcı scriptler, konfigürasyon rehberleri ve sistem araçları.
- **[[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB|Admin Dashboard Hub]]** — Yönetim paneli tasarımı, UX akışları ve kontrol yüzeyleri belgelendirmesi.
- **[[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB|Orkestrasyon Ajanları Hub]]** — Ajan koordinasyonu, workflow tanımları, görev orkestrasyon ve multi-agent sistemleri.
- **[[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB|Müşteri Paneli Hub]]** — Müşteri arayüzü: sprint & PO yönetimi, admin panel, UX tasarımı, abonelik & faturalama raporları.
- **[[Huginn Data Insights/indexes/rapor_index|Rapor Index]]** · **[[Huginn Data Insights/indexes/teknik_index|Teknik Index]]** — Tüm rapor ve teknik dokümanların tam dosya envanteri. Hub konuya göre gruplar, indeks eksiksiz listeyi verir.

Tüm hub'lar mesh topolojisinde bağlıdır; herhangi bir rapor veya dokümana diğer hub'lardan ulaşılabilir.

### Çalışmaya başlamadan önce

- **[[Huginn Data Insights/docs/ROO_ELESTIRI_NOTLARI|Eleştiri & Risk Defteri]]** — Tüm ajanların ortak defteri. Sorun çıkınca **ilk buraya bakılır**: bilinen tuzaklar, çözülmüş hatalar ve açık riskler K-/M-/V-/S-/O-/D- önekleriyle listelidir. Yeni bir bulgu çıkarsa aynı deftere yazılır.

## Şablonlar

- templates — [[ADR-template]] · [[Bug-template]] · [[Spec-template]]

## Proje kuralları

- Proje anayasası: `AGENTS.md` (proje kökü)
- AI kılavuzu: `CLAUDE.md` (proje kökü)

## Not

Bu düzen, hem belge yönetimi hem de ajan koordinasyonu için tasarlanmıştır.
