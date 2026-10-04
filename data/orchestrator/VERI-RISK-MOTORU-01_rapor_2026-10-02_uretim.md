# VERI-RISK-MOTORU-01 — Üretim Raporu

**Tarih:** 2026-10-02 · **Ajan:** Üretim/Hacim UTKU · **Görev:** `VERI-RISK-MOTORU-01`
**Kilitli dosya:** `src/company_master/schema/migrations/0046_risk_skorlari.sql`

> Bu iş **zaten uygulanmış ve test edilmiş** durumdaydı; eksik olan teslim
> zinciriydi. Rapor, ölçülmüş kanıtı topluyor (D-260).

## Ne yapıldı

Sekiz risk skoru tablosu (`company_risk_scores`) + geri alma dosyası
diskte, canlı şemada ve defterde.

| Skor kolonu | SSOT satırı (COMMENT) |
|---|---|
| `corporateness_score` | SSOT:792 |
| `reliability_score` | SSOT:796 |
| `reputation_score` | SSOT:800 |
| `cyber_security_score` | SSOT:804 |
| `operational_power_score` | SSOT:808 |
| `transparency_score` | SSOT:812 |
| `fraud_risk_score` | SSOT:816 |
| `overall_trust_score` | SSOT:820 |
| `recommendation_tier` (türetilmiş) | SSOT:824-849 |

Hesaplayıcı: `src/company_master/risk/skorlar.py` — tek yazma kapısı
`risk_recalc()`. Taban dosya `0046_risk_skorlari.sql` (92 satır, 1 tablo).

## Değişen dosyalar

Bu teslim turunda **yeni kod yazılmadı**. Eksik olan kanıt zinciri kapatıldı:

| Dosya | İş |
|---|---|
| `src/company_master/schema/migrations/0046_risk_skorlari.sql` | (yok — hash ile doğrulandı, değişmedi) |
| `hubs/VERI_KALITESI_HUB.md` | B-14 hafıza kaydı |
| `data/orchestrator/VERI-RISK-MOTORU-01_rapor_2026-10-02_uretim.md` | bu rapor |

## Test sonuçları

```
python -X utf8 -m pytest tests\test_schema_validation.py tests\test_risk_skorlari.py -q
19 passed in 4.39s        (kabul kriteri 2)
```

### Kırılarak doğrulama (kabul kriteri 6) — D-256/4

Kırmızı çıktı teslim özetine yazıldı. Yöntem: `0046_risk_skorlari.sql`
sha256 ile yedeklendi → `corporateness_score NUMERIC(5,2)` satırına
`DEFAULT 0` eklendi (D-249 ihlali) → mandal çalıştırıldı:

```
__________________ test_hicbir_skor_kolonunda_default_0_yok ___________________
>       assert "DEFAULT 0" not in icerik, (
E       AssertionError: goc dosyasinda 'DEFAULT 0' var — olculmemis skor 0 sayilir (D-249)
```

Geri alındı, hash birebir eşitliği doğrulandı
(`5FF9B16D…DF85A3` → `5FF9B16D…DF85A3`), tekrar koşum **19 passed**.

Mandal gerçekten durduruyor — "yeşil test yeşildir" beyanı değil.

## Bulgular

| # | Bulgu | Kanıt |
|---|---|---|
| 🟡 | **Kabul kriteri 1'in bir parçası artık geçersiz:** "`schema_versions.json` güncel" isteniyordu. Dosya **23'te donmuş** (son kayıt `0023_source_records_company_id.sql`, 2026-09-27). D-265 bu dosyayı üç ayrı göç defterinden biri olması nedeniyle **kullanılamaz** ilan etti; D-265 gereği tek kapı `scripts/goc_defteri.py` → `schema_migrations` tablosu. D-309 da 0046-0049'un bu dosyayı güncellemediğini kaydetti. **Kriter sonraki kararlarla geçersizleşti; bu görevde güncellemedim** (dosya tarihsel kayıt, D-319 #22 açık borç). | dosya sonu: `"version": 23` |
| 🟢 | Gerçek defter **`schema_migrations`** tablosu: `scripts/goc_defteri.py` → `0046_risk_skorlari.sql **TAM** defterde`; 49 goc / 49 kayıt. Yani göç gerçekten uygulanmış, sadece dosya yazılmış değil. | `python scripts/goc_defteri.py` |
| 🟢 | Tek yazıcı doğrulandı (kabul kriteri 5): `corporateness_score` yazan **tek** dosya `src/company_master/risk/skorlar.py`. `scripts/` altında ikinci yazıcı yok. | `Select-String` taraması |
| 🟢 | `DEFAULT 0` yok (kabul kriteri 4) — ve kırılarak kanıtlandı, yalnız okunmadı. | negatif kontrol |
| 🔵 | **Göç numarası çakışması (ileride SCRAPE işlerini etkiler):** kazıma planı `0046_scrape_audit_log.sql` yazmayı öngörüyor, ama **0046 tüketilmiş** — diskte `0046_risk_skorlari.sql` var ve numaralar 0049'a kadar dolu. `SCRAPE-002/003/004/005` bu plana dayanıyor. | `migrations/0046…0049` |

## Eksik / erteleme

1. **Hesaplama bu görevde çalıştırılmadı** — brifin kendi kuralı: "canlı DB'ye
   veri yazmak ayrı görevdir (D-238)". Bu görev şema + fonksiyon + mandal ile biter.
   Dolayısıyla `company_risk_scores` tablosu şemada var, satırı boş olabilir.
2. `schema_versions.json` güncellenmedi (yukarıdaki gerekçe) — D-319 #22 borcunun parçası.
3. `recommendation_tier` `overall_trust_score`'tan **türetilmiş** bir alan; skora
   bağlı kural SSOT:824-849'da, kodda türetiliyor mu ayrıca doğrulanmadı.

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]] · [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]] · [[plans/brief_utku_VERI-RISK-MOTORU-01]]
