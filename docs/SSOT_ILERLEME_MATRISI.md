# SSOT İlerleme Matrisi — Vaat ↔ Tablo ↔ Canlı Sayım

**Tek amaç:** Master Kaynak Dokümanı'nın (`yedekler/Huginn Data Insights (HUGIns).txt`) her
vaadi için "tablo var mı / dolu mu / kim sorumlu" sorusunu **beyana değil ölçüme** bağlamak
(D-224: ölçülmeden görev kapanmaz · D-238: ölçüm canlı veritabanında yapılır).

> Bu dosya **el ile güncellenmez**. Sayım kolonu aşağıdaki komutun çıktısıdır; her
> güncellemede komut yeniden koşulur ve tarih yazılır.

## Ölçüm komutu (tek kaynak)

```bash
cd "Huginn Data Insights" & python scripts/ssot_ilerleme.py
```

---

## 1. Müşteri soru envanteri → karşılığı (SSOT satır 11-17)

| # | Müşteri sorusu | Hangi tablo cevaplar | Durum |
|---|---|---|---|
| 1 | Gerçek bir şirket mi? | `companies` · `company_identifiers` | 🟢 |
| 2 | Yasal yükümlülüklerini yapıyor mu? | `company_events` (TSG ilanları) | 🟡 407 kayıt |
| 3 | Dolandırıcılık riski var mı? | `company_intelligence_scores.risk_score` | 🔴 boş |
| 4 | Ayakta kalır mı? | `company_signals` (growth) · `momentum_snapshot` | 🔴 boş |
| 5 | Sahibi kim, şeffaf mı? | `key_personnel` | 🔴 boş |
| 6 | Dijital güvenliği sağlam mı? | `company_tech_profile` | 🔴 boş |
| 7 | İtibarı nasıl? | `company_signals` (reputation) | 🔴 boş |

## 2. Altı faz → canlı durum

| Faz | SSOT vaadi | Taşıyıcı tablo | Sayım (2026-10-01) | Durum | Sorumlu |
|---|---|---|---|---|---|
| 1 | OSINT + Şirket Doğrulama | `companies` | **9.412** | 🟢 | utku |
| 1 | — kimlik eşleştirme | `entity_resolution` | **8.905** | 🟢 | utku |
| 1 | — ne iş yapar (NACE) | `company_industries` | **6.788** | 🟢 | utku |
| 2 | **Risk Motoru** (8 skor) | `company_intelligence_scores` | **0** | 🔴 | — |
| 2 | — sinyal kaydı | `company_signals` | **0** | 🔴 | — |
| 3 | **Entity Graph / ilişki ağı** | `company_signals` (geo/küme) | **0** | 🔴 | **utku (AG-01)** |
| 4 | **AI Analyst** (MİMİR/ODIN) | prompt + RAG | prompt **v4 hazır** | 🟡 | salih |
| 5 | Vendor Due Diligence | — | — | 🔴 | — |
| 6 | Global Intelligence Network | — | — | 🔴 | — |

## 3. Fırsat eşleşmesi (Ürün Sahibi talebi, 2026-10-01)

Ürün Sahibi'nin istediği dört sinyal türü ve yakıt durumu:

| Fırsat sinyali | Gereken veri | Bugün | Yapılabilir mi |
|---|---|---|---|
| Aynı kümelenmede kim var | `osbs` + `company_locations` | 🟢 dolu | **bugün** |
| NACE tamamlayıcılığı (x → y'yi besler) | `company_industries` | 🟢 6.788 | **bugün** |
| "Ürünüm var / senin ihtiyacın" | `company_products` | 🔴 **0** | yakıt yok |
| "Atıl kapasitem var" | `company_capabilities` | 🔴 **0** | yakıt yok |
| Müşteri ilan girer → sinyal | ekran + `company_signals` | 🔴 yok | Faz 5 |

**Karar:** Risk ve fırsat **aynı motorun iki yönüdür** — ikisi de `company_signals` +
`company_intelligence_scores` tablolarına yazar. `signal_type` kolonu zaten
`growth · risk · tech_transformation · investment · geo_expansion · org_change`
değerlerini kabul ediyor. Ayrı motor kurulmayacak.

## 4. Eksik kaydı (yakıtı olmayan vaatler)

| Eksik | Neden boş | Açılacak görev |
|---|---|---|
| `company_products` | ürün toplayıcı yazılmadı | Faz 4 (2 hafta) |
| `company_capabilities` | kapasite verisi kaynağı yok | Faz 4 |
| `key_personnel` | TSG kişi ayrıştırıcı var, yazıcı yok | Faz 2 eki |
| `company_tech_profile` | siber tarama betiği yok | Faz 2 |
| `evidence` | kanıt yazıcısı bağlanmadı | Faz 2 |
| `company_state` | hesaplayıcı yok | Faz 2 |

## 5. Önceki yanlış beyan (öz-eleştiri kaydı)

2026-10-01 raporunda *"`company_scores` tablosu yok"* yazıldı. **Yanlıştı.**
Tablo adı `company_intelligence_scores` ve göç `0013_job_intelligence.sql` ile
**kurulmuş**. Hata sebebi: tablo adı ölçülmeden varsayıldı. Bu dosya o hatanın
tekrarını engellemek için var — kolon ve sayım artık komuttan gelir.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/prompts/mimir_sistem_promptu]]
