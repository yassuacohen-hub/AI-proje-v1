# Orkestrasyon / Ajanlar Hub

> Konu-bazli hub (PO karari 2026-09-21): Ajan koordinasyonu, gorev yasam dongusu,
> orkestrator protokolleri, ajan roller tanimi ve task dispatch mekanizmalari tek noktada.
> Yurutme raporlari (data/orchestrator/ORKESTRA-*_rapor*) dahil degildir.

Uretim: Sprint Graf Hub'lastirma FAS-2 (2026-09-21). Bagli dokuman: **22**

Ana baglam: [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/AGENT_SYNC]] · [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] · [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] · [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] · [[Huginn Data Insights/hubs/OSINT_INDEX]] · [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] · [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] · [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] · [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] · [[Huginn Data Insights/PROJECT_ROADMAP]] · [[Huginn Data Insights/hubs/V10_POC_HUB]]

---

## Temel Kurallar / Koordinasyon
- [[Huginn Data Insights/AGENTS]] — Calisma alani kurallarinun temel dokumani; ajan adlari, roller, gorev yasam dongusu
- [[Huginn Data Insights/AGENT_SYNC]] — Ajan senkronizasyon protokolu
- [[Huginn Data Insights/AI proje v1/V10/08-Ajanlar/README]] — Ajan tanimi indeksi

## Ajan Rolleri / Tanim
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/01_koordinator_ajan` — Koordinator ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/02_mimar_ajan` — Mimar ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/03_arastirmaci_ajan` — Arastirmaci ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/04_gelistirici_ajan` — Gelistirici ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/05_kalite_ajan` — Kalite ajan rol tanimi
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/06_web_kazima_uzmani` — Web kazima uzmani ajani
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/09_osint_rol_tanimi` — OSINT rol tanimi

## Harici Ajan Protokolu
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/07_harici_ajan_protokolu` — Harici ajan entegrasyon protokolu
- `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/08_harici_ajan_gorev_onerileri` — Harici ajan gorev onerileri

## MIMIR / Orkestratör Asistanı
- [[Huginn Data Insights/docs/AJAN_DETAY]] — Ajan detay belgesi (rol tanimi, ayirma, MIMIR)

## Orkestrasyon Tasarimi
- `Huginn Data Insights/AI proje v1/V10/11_osint_motoru/Orkestrator` — OSINT orkestratoru tasarimi
- [[Huginn Data Insights/docs/GOREV_PANOSU_KULLANIM_KILAVUZU]] — Gorev panosu kullanim kilavuzu; §10 Proje Saglik Simulasyonu (`gorev_kutusu.py simulasyon`, D-198 zorunlu tur kapisi)
- [[Huginn Data Insights/docs/OPERASYON_KILAVUZU]] — Urun sahibi (KAHIN) el kitabi: vault yapisi, ajan rolleri, gunluk akis (D-223 ile yedekten kurtarildi; olcumleri 2026-09-21 tarihli)
- [[Huginn Data Insights/docs/VAULT_AUTOMATION_TEMPLATE]] — Multi-ajan vault otomasyon sablonu (kok dizinden tasindi 2026-09-24)
- [[Huginn Data Insights/scripts/gorev_analiz]] — Pano gorev analizi betigi (kok `task_analysis.py`, D-183 ile yeniden adlandirildi)
- [[Huginn Data Insights/scripts/vault_bakim]] — Vault bakim olcumu (orphan orani, hub yogunlugu, kirik link)
- [[Huginn Data Insights/scripts/kilo_backup_rotate]] — KILO yedek rotasyon politikasi (D-176)

## Kurallar / Politika
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/01_kasa_kurallari` — Kasa kurallari
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/02_calisma_kurallari` — Calisma kurallari
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/04_token_verimliligi_ve_dil_politikasi` — Token verimliligi politikasi
- `Huginn Data Insights/AI proje v1/V10/09_kurallar_ve_promptlar/03_prompt_kutuphanesi` — Prompt kutuphanesi

## Wiki / Ajan Rehberleri
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/koordinator` — Koordinator wiki
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/mimar` — Mimar wiki
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/arastirmaci` — Arastirmaci wiki
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/gelistirici` — Gelistirici wiki
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/kalite` — Kalite wiki
- `Huginn Data Insights/AI proje v1/V10/wiki/agents/web_kazima` — Web kazima wiki

## Kapanan isler (B-14 · hafiza izi)

> Altyapi/orkestrasyon gorevleri kapaninca buraya bir satir birakir.
> `gorev_kutusu.py teslim` bu izi gormezse teslimi reddeder (B-14 kapisi).
> Asagidaki satirlar TUR-B2 (2026-09-24) ile geriye donuk yazildi.
> Kapi `HAFIZA_KAPISI_YURURLUK = 2026-09-24` esiginden once kapanan isleri tek tek
> aramaz; onlarin karsiligi asagidaki ceyreklik arsiv baglantisidir (D-186, D-198).

| task_id | Ne kapandi | Bitis |
|---------|------------|-------|
| ALTYAPI-MOJIBAKE-BARIYER-01 | Mojibake yazim-oncesi hasar bariyeri | 2026-09-23 |
| ALTYAPI-D182-MIMIR-01 | `mimir` ajani `trigger.AJANLAR`'a eklendi (D-182) | 2026-09-23 |
| ALTYAPI-DURUM-SOZLUK-01 | Gorev durum sozlugu tutarsizligi giderildi → `task_board.py` | 2026-09-23 |
| ALTYAPI-TEST-HERMETIK-01 | Uretim verisine dokunan testler izole edildi | 2026-09-23 |
| GRAPH-CANONICAL-SECER-02 | Canonical graph baglanti guvenligi (D-172/D-191) | 2026-09-23 |
| ALTYAPI-TETIK-ARSIV-01 | Kanonik olmayan tetik dosyalari arsive tasindi | 2026-09-23 |
| AGENTS-MERGE-UU | Kok/vault `AGENTS.md` kopuklugu → tek SSOT (D-189) | 2026-09-24 |
| ALTYAPI-D66-BYPASS-TETIKLEME-01 | `tetik_senk.py` bypass bayragi duzeltildi (D-65) | 2026-09-24 |
| ALTYAPI-GROQ-KEY-DOGRULA-01 | Groq canli anahtar dogrulamasi → `groq_client.chat()` | 2026-09-24 |
| ALTYAPI-MOJIBAKE-DIZIN-01 | `mojibake_onar.py` dizin taramasi | 2026-09-24 |
| ALTYAPI-TETIK-ZAMAN-01 | `tetik_senk.py` zamanlama duzeltmesi | 2026-09-24 |
| ALTYAPI-KILIT-OTOMATIK-01 | Kilit otomatik birakma → `src/company_master/orchestrator` | 2026-09-24 |
| VAULT-CLEANUP-BATCH | Vault alarm/tetik artiklari silindi → temiz kuyruk | 2026-09-24 |
| NINEROUTER-IMAGE-GEN-01 | `ninerouter.py`'ye `ninerouter_image_gen` eklendi | 2026-09-24 |
| TEST-13-PREEXIST-DUZELT-01 | 13 pre-existing test hatasi duzeltildi → `d193_menu_e2e_report.md` | 2026-09-24 |
| TEST-13-PREEXIST-DUZELT-02 | Kalan 7 test hatasi duzeltildi → pytest yesil | 2026-09-24 |

Tam liste ceyreklik arsivde: `data/orchestrator/task_board_arsiv_2026-Q3.json`

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]] (Ust Hub)
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]
