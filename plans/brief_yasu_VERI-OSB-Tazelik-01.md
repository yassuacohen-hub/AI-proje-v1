# VERI-OSB-Tazelik-01 — Brief (yasu)

**Başlık:** [VERI] 13 Ankara OSB'si için ayrı temiz veri seti + Supabase'e tazelik yazımı (2-3 hafta)
**Öncelik:** P0 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `supabase/migrations/20260929_d306_rls_ac_api_kapat.sql`
**Bağımlılık:** `VERI-OSTIM-TAM-TARAMA-01` (tamamlandı)
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14)

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

> **Görev:** `VERI-OSB-Tazelik-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Tarih:** 2026-09-29
> **Kararlar:** D-301, D-303, D-305, **D-306**

## Neden

Kaynak: `C:\Huginn Data Projesi\workflows\huginn-muninn\ankara_osb_listesi.csv` (13 OSB)

KAHİN (2026-09-29):

> "diper osbler bunlar, bunlardan da filtrelenmiş düzgün verileri alıp sonra
> sistemde database'de eksik olanlarla doldurmamız gerekiyor. Temelde amaç
> **veri tazeliliği**. Tüm yazımları orkestrator kontrol yapacak."
>
> "osb'ler için ayrı ayrı tek bir veri seti istiyorum, senden ayrı ayrı veri
> setleri istiyorum osb'leri için, sonra hepsi birleştirilecek."
>
> "yerel db sadece test için, gerçek db supabase'de."

## ⚠️ DÜZELTME: Önceki çıkarımlarım YANLIŞTI

Bu brifin ilk taslağında yerel SQLite'a bakmıştım ve şunları yazdım. **Hatalıydı:**

| ❌ Yanlış çıkarımım | ✅ Gerçek (Supabase, ölçüldü) |
|---|---|
| "Ana DB 0 bayt, gerçek veri yok" | `company_master.db` gerçekten 0 bayt ama **bu sadece test DB'si** |
| "8.313 kayıt var" | Supabase'de **9.412** kayıt |
| "Tüm kayıtlar tek OSB'ye ait" | Yerel yedek için doğruydu, Supabase farklı |
| "osbs tablosu boş" | Supabase'de **9 kayıt** |
| "Yazma imkânsız, DB geri yüklenmeli" | **Gereksiz** — gerçek DB zaten çalışıyor |

> **Kural:** Yerel dosyalara bakarak **çıkarım yapılmaz.** Gerçek veri
> yalnızca Supabase'ten okunur. Bu brifteki her sayı `SELECT` ile ölçülmüştür.

## Doğrulanacak varsayım

| Varsayım | Ölçüm | Durum |
|---|---|---|
| Gerçek DB = Supabase | `DATABASE_URL` → `*.pooler.supabase.com:6543` | ✅ |
| `companies` satır sayısı | `SELECT COUNT(*)` → **9.412** | ✅ |
| Tablo sayısı (public) | **52** | ✅ |
| RLS açık olan tablo | düzeltme öncesi **0/52** | ✅ |
| `anon` GRANT'i olan tablo | düzeltme öncesi **54** | ✅ |
| `osbs` satır | **9** | ✅ |
| `source_records` | **10.601** | ✅ |
| `entity_resolution` | **8.905** | ✅ |
| `nace_codes` | **3.319** | ✅ |
| `kvkk_bireysel_email_yedek` | **270** | ✅ |
| `.env` git'te mi | **HAYIR** (`.gitignore:11`) | ✅ |
| `.env` git geçmişinde mi | **HAYIR** | ✅ |

## ✅ D-306 TAMAMLANDI — Supabase güvenliği

**KAHİN:** "bu sorunu kesin çözelim yoksa api kullanmayacağız"

**Ölçülen tehlike:** 52 tablonun hiçbirinde RLS yoktu, 54 tabloda
`anon` GRANT'ı vardı. Yani Veri API (PostgREST) **anonim erişime açıktı**:
`users.password_hash`, `users.api_key`, `admin_mfa.secret_key`,
`kvkk_bireysel_email_yedek.primary_email` okunabilir durumdaydı.

**Uygulanan çözüm:**

| Önce | Sonra |
|---|---|
| RLS açık: 0/52 | **52/52** |
| `anon` GRANT: 54 tablo | **0** |
| `authenticated` GRANT: 54 tablo | **0** |
| `companies` | 9.412 → **9.412** (korundu) |

- `service_role` **dokunulmadı** → backend/panel çalışmaya devam eder
- Migration: `supabase/migrations/20260929_d306_rls_ac_api_kapat.sql`
- Geri alma: `python scripts/supabase_rls_uygula.py --geri-al`
- Doğrulama: `python scripts/supabase_guvenlik_denetim.py`

**30 Ekim 2026 kuralı:** Yeni tablolara artık GRANT verilmeyecek. Supabase
zaten GRANT'siz yeni tabloları API'ye kapatacak — bu bizim istediğimizle

## ✅ D-307 TAMAMLANDI — Sarı lint uyarıları

KAHİN: "rls hataları çözüldü fakat sarı uyarılar duruyor" (3 uyarı).

| Uyarı | Nesne | Çözüm | Durum |
|---|---|---|---|
| Fonksiyon arama yolu değiştirilebilir | `update_updated_at_column()` | `SET search_path = ''` | ✅ |
| Fonksiyon arama yolu değiştirilebilir | `trg_isaretci_senkron()` | `SET search_path = ''` | ✅ |
| Eklenti public şemada | `pg_trgm` | `extensions` şemasına taşındı | ✅ |

**Ölçüm (taşıma öncesi):** public şemada 33 fonksiyon vardı; **31'i
`pg_trgm` extension'ına aitti**. Bunlara dokunmak extension'ı bozardı —
bu yüzden `pg_depend` filtresiyle yalnız bize ait 2 fonksiyon seçildi.

**Güvenlik onayı:** ikisi de TRIGGER fonksiyonu:
- `trg_isaretci_senkron()` → `companies.companies_isaretci_senkron`
- `update_updated_at_column()` → 3 trigger (job_postings,
  company_intelligence_scores, company_tech_profile)

**Taşıma sonrası doğrulama:**
- trigram indeksleri **4/4 geçerli** (taşıma bozmadı)
- `companies` 9.412 → **9.412** (korundu)
- public fonksiyon 33 → **2**

Migration: `supabase/migrations/20260929_d307_search_path_sabit.sql`
Doğrulama: `python scripts/supabase_lint_coz.py`

aynı sonuç. Gelecek migration'lara GRANT eklenmeyecek.

## ✅ D-308/D-309/D-310 — Köken kuralı artık FİİLEN zorlanıyor

**KAHİN tespiti (doğrulandı):** "her kaydın kökeni yazılır" kuralı
`VERI_YAZMA_KURALLARI.md`'de yazılı, ama `companies` tablosunda
`source` / `collected_at` / `postal_code` **kolonu yok**. Kural beyan
olarak kalıyordu.

**Ayrıca benim işlerimde de sıkıntı vardı (ölçüldü):**
- `OSTIM_TEMIZ`'de `collected_at` **hiç yok** — toplama zamanı tutulmuyor
- `osb/baskent` setinde `source_name`/`source_type` **hiç yok**
- Yazılsaydı tüm köken alanları **kaybolurdu**

**Uygulanan (KAHİN onayıyla, S1):**

| Kolon | Tip | Sonuç |
|---|---|---|
| `collected_at` | timestamptz | **9.412/9.412 dolu** |
| `source_name` | text | **9.409/9.412 dolu** |
| `source_type` | text | eklendi |
| `source_file` | text | eklendi |
| `source_line` | text | eklendi |
| `collected_by` | text | 3 kayıt işaretli |

companies: 49 → **55 kolon** · satır **9.412 → 9.412** (korundu)

**D-310'da yaptığım hatayı da düzelttim:** İlk denemede
`source_name = source_records.raw_website` yazdım — ama `raw_website`
**firmanın kendi sitesidir, kaynak adı değildir.** 5.362 kayıt yanlış
etiketlenmişti. Doğru yol:

```
companies.source_record_id
  -> source_records.source_id
    -> sources.source_name   (ostim.org.tr, aso.org.tr, ...)
```

Düzeltme sonrası `source_name` **5.362 → 9.409**.

**Kalan 3 kayıt:** `source_record_id`'si hiç yok — köken bulunamıyor.
Uydurmadım; `collected_by = 'migration:source_record_id_bos'` ile
**açıkça işaretlendi**.

Migration: `supabase/migrations/20260929_d30{9,10b}*.sql`
Denetim: `python scripts/kopen_denetim.py`



## ✅ D-305 — 13 OSB için ayrı veri setleri

KAHİN: "osb'ler için ayrı ayrı tek bir veri seti istiyorum, senden ayrı ayrı
veri setleri istiyorum osb'leri için, sonra hepsi birleştirilecek."

Üretilen: `data/osb/<slug>/firmalar.jsonl` + `meta.json`

| OSB slug | Kayıt | Adres | Telefon | Not |
|---|---|---|---|---|
| `ostim` | **8.296** | %97 | %88 | OSTIM_TEMIZ kaynağı |
| `baskent` | 481 | %100 | %0 | |
| `kazan_hab` | 111 | %100 | %17 | |
| `anadolu` | 48 | %100 | %45 | |
| `aso` | 16 | %100 | %0 | |
| `polatli` | 13 | %100 | %0 | |
| `cubuk` | 7 | %100 | %0 | |
| `aso2` | 3 | %100 | %0 | ⚠️ ayrım doğrulanmalı |
| `dokumcu` | 2 | %100 | %0 | |
| `elmadag` | 1 | %100 | %100 | ⚠️ çok az |
| `sereflikochisar` | 1 | %100 | %0 | ⚠️ çok az |
| `ivedik` | **0** | — | — | D-301 kaynak düşürüldü |
| `polatli_ticaret` | **0** | — | — | kaynak yok, tarama gerekli |
| **TOPLAM** | **8.979** | | | |

Doğrulama: 13 klasör, her birinde `company_slug` tekil, `osb_slug` doğru.

Kurallar: kaynak dosyalara dokunulmadı · hiçbir kayıt silinmedi ·
**birleştirme yapılmadı** (KAHİN talebi) · yazım atomik (K-3)

## Adımlar

### Faz A — Supabase OSB kaydı (KAHİN onayı bekler)
1. `osbs` tablosundaki 9 kaydı CSV 13 OSB ile karşılaştır
2. Eksik OSB'ler için `osbs` kaydı ekle
3. `companies.osb_id` dağılımını ölç

### Faz B — Eksik OSB'ler için tarama
4. `polatli_ticaret` (kaynak yok) — CSV'deki web sitesinden tara
5. `elmadag`, `sereflikochisar`, `dokumcu` — doğrula
6. `aso2` ayrımı — kaynakta net "2. OSB" işareti var mı bul
7. Politika P-1..P-10, **500 kayıt/gün** tavanı

### Faz C — Birleştirme (KAHİN talebi)
8. 13 veri setini tek havuzda birleştir
9. Çapraz mükerrer: slug + normalize unvan + telefon
10. Mükerrer grupları **raporla, silme** — karar KAHİN'e ait

### Faz D — Supabase yazımı
11. **Yazma öncesi orkestrator onayı.** yasu doğrudan yazmaz
12. Atomik yazım (K-3): tek transaction
13. Yazım sonrası `supabase_guvenlik_denetim.py` tekrar çalıştır
14. `companies` satır sayısı raporla (9.412 → ?)

## Kabul kriteri

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- **Teslimden önce** `**Hub:**` dosyasının "Kapanan işler" bölümüne yaz (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**
- Bir faz tıkandıysa → sorun aç, sonraki faza geç
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap

```bash
python scripts/ajan_chat.py ac yasu VERI-OSB-Tazelik-01 "<sorun>" --cozum "<öneri>"
python scripts/ajan_chat.py oku --task-id VERI-OSB-Tazelik-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-OSB-Tazelik-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-OSB-Tazelik-01 --ozet "<özet>"
```

## Önce oku

- `supabase/migrations/20260929_d306_rls_ac_api_kapat.sql` → API kapatma
- `supabase/migrations/20260929_d307_search_path_sabit.sql` → lint düzeltme
- `scripts/supabase_guvenlik_denetim.py` → ölçüm (salt okunur)
- `scripts/supabase_lint_coz.py` → sarı uyarı ölçüm + düzeltme
- `scripts/osb_veri_seti_uret.py` → OSB veri seti üretici
- `data/osb/*/meta.json` → üretilen envanter
- `docs/BORC_DEFTERI.md` → D-283, D-301, D-303

## Ilgili Nodlar
> **Zorunlu (D-218).** En az 2 wikilink. Goreve dokunan her dokumani bagla.

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]


## İlgili Nodlar
> **Zorunlu (D-218).** En az 2 wikilink. Göreve dokunan her dokümanı bağla.

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]

- [x] RLS 52/52 açık, `anon`/`authenticated` GRANT 0
- [x] search_path uyarısı 0, `pg_trgm` `extensions` şemasında
- [x] trigram indeksleri 4/4 geçerli
- [x] `companies` 9.412 korundu
- [x] 13 OSB için ayrı veri seti üretildi
- [x] `company_slug` her dosyada tekil
- [ ] `osbs` tablosu 13 OSB'yi kapsıyor
- [ ] `polatli_ticaret` tarandı
- [ ] `aso2` ayrımı doğrulandı
- [ ] Birleştirme yapıldı (KAHİN onayıyla)
- [ ] Supabase'e yazıldı (KAHİN onayıyla)

## ⚠️ Riskler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | **Yerel DB'den çıkarım** | Yanlış karar (oldu!) | Yalnız Supabase ölçümü |
| R2 | Supabase parolası sızarsa | Tam veri kaybı | RLS + GRANT kapalı (D-306) |
| R3 | Yazma sırasında transaction kopması | Kısmi veri | Tek transaction (K-3) |
| R4 | `aso2` ayrımı yanlış | Yanlış OSB ataması | Doğrulama (Faz B) |
| R5 | Çok kaynaklı mükerrer | Bozuk veri | Faz C raporu, silme yok |
| R6 | 500/gün tavanı aşılır | Dilekçe ihlali | `time.sleep` zorunlu |
| R7 | İvedik kaynak düşürüldü (D-301) | 1 OSB eksik | KAHİN kararı |
| R8 | Extension taşınca arama bozulur mu | Panel araması | 4/4 indeks geçerli ✅ |
| R9 | 30 Ekim sonrası yeni tablo erişilemez | Migration hatası | GRANT eklenmeyecek (kasıtlı) |
