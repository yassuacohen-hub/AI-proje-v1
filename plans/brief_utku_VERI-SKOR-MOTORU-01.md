# VERI-SKOR-MOTORU-01 — Brief (utku)

**Başlık:** [VERI] Need/Fit/Timing/Ensemble dört skor tablosu → 0049_firsat_skorlari.sql (5-10g)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/schema/migrations/0049_firsat_skorlari.sql`
**Bağımlılık:** F3 (L1 tamamlama — company_capabilities/certifications/key_personnel ETL doldurması, henüz bitmedi — aşağıda açık)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Fazlar aşağıda `## Faz A/B/C` olarak yazılı.

## Neden

D-319 kararı (KAHİN onayı): K4 (V9 bağlam dokümanı) Three-Score System resmi skor seti
olarak kabul edildi — K-B açık sorusu kapandı. SSOT yol haritasının **F5 — L2 skor motoru**
adımı bu dört skoru `intelligence/` altında uygulamaya koyar.

| Kanıt | Yer |
|---|---|
| Three-Score System (Need/Fit/Timing/Ensemble, 0.0-1.0) | `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md:229-240` |
| Opportunity Gates (need≥0.25, fit≥0.30, evidence≥0.20, timing≥0.30) | aynı dosya:215-228 |
| Ensemble formülü (ağırlık: need 0.30, fit 0.35, timing 0.20, evidence 0.15 + bonus) | aynı dosya:241-266 |
| F5 satırı — bağımlılık F3, kritik yol F0→F1→F3→F5 | `docs/HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md:60-77` |

**Skor adları SSOT'tan birebir alınacak — yeni ad uydurma yasak (D-260):**

| # | Skor adı (SSOT verbatim) | Kolon adı | SSOT satırı |
|---|---|---|---|
| 1 | İhtiyaç Olasılığı (Need Score) | `need_score` | 231 |
| 2 | Ürün Uyumu (Fit Score) | `fit_score` | 234 |
| 3 | Zamanlama (Timing Score) | `timing_score` | 237 |
| 4 | Birleşik Skor (Ensemble Score) | `ensemble_score` | 240 |

### ⚠️ Bilinen sınırlama — F3 bağımlılığı (açık, gizlenmiyor)

`company_capabilities`, `certifications`, `key_personnel` tabloları **şema olarak var**
(`0004_faz_1_2.sql`), ama ETL doldurması henüz yapılmadı (F3 bitmedi, "8313 firmada dolum
oranı ölçülür" kriteri karşılanmadı). Bu demektir ki **Fit skoru bugün hesaplanırsa çoğunlukla
NULL/sparse çıkar** — bu kabul edilebilir bir durumdur, hata değildir. D-249 deseni (NULL
paydadan düşer, 0 sayılmaz) burada da geçerli. F3 bitince aynı kod gerçek veriyle çalışacak.

## Doğrulanacak varsayım

- Son göç `0048_firma_turu_etiketi.sql` varsayıldı → yeni göç numarası **0049**. Diskte 0049 varsa **dur**, `ajan_chat.py ac` ile sorun aç.
- `schema_versions.json`'a **satır eklenmeyecek** — 46/47/48 göçlerinde de eklenmedi (dosya D-265 ile 23'te donuk, tarihi kayıt). Bu brif o adımı atlar, önceki brif şablonundan kasıtlı sapma.
- `companies` tablosunda birincil anahtar `company_id` varsayıldı (0046 ile aynı). Farklıysa **dur**.
- Skor tipi `NUMERIC(5,2)` ve **varsayılan NULL** varsayıldı. `DEFAULT 0` yazmak **yasaktır** (D-249).
- Yeni modül `src/company_master/intelligence/skor_motoru.py` varsayıldı (dizin boş, başka dosya adıyla çakışma yok). Farklı isim istersen görevi alırken serbestsin, ama tek dosya olmalı.
- Tek yazma kapısı deseni `risk_recalc()` (0046/VERI-RISK-MOTORU-01) ile aynı olacak: `firsat_recalc()`.

## Faz A — Şema (en riskli, ilk sırada)

1. `0049_firsat_skorlari.sql` zaten yazıldı (orkestratör tarafından) — oku, doğrula, gerekirse düzelt: `company_opportunity_scores` tablosu — `company_id` FK + 4 skor kolonu + `calculated_at` + `score_version`.
2. Her kolona `COMMENT` var mı kontrol et: SSOT satır numarası + Türkçe resmî ad.
3. `down/0049_firsat_skorlari.down.sql` geri alma dosyası var mı kontrol et (`test_migration_down_files_content` bunu arar).
4. `schema_versions.json`'a **dokunma** (yukarıdaki varsayım).

## Faz B — Hesaplayıcı iskeleti

5. `src/company_master/intelligence/skor_motoru.py` yaz: `need_score`, `fit_score`, `timing_score` için ayrı fonksiyon, **girdisi yoksa `None` döner** (0 dönmez).
6. `compute_ensemble_score(need, fit, timing, evidence, weights=None)` — SSOT:241-266'daki formülü birebir uygula (ağırlık need 0.30/fit 0.35/timing 0.20/evidence 0.15, field_bonus 0.05, signal_bonus 0.03, clamp 0.0-1.0).
7. Tek yazma kapısı: `firsat_recalc()` — tabloya yazan **tek** fonksiyon. İkinci `UPDATE` yazmak yasak.
8. `fit_score` hesaplayan fonksiyon `company_capabilities`/`certifications`/`key_personnel` tablolarını okur; bu tablolar boşsa (F3 bitmediği için) **None döner**, hata fırlatmaz.

## Faz C — Mandal (D-256/4: kırılarak doğrulanır)

9. `tests/test_firsat_skorlari.py` yaz. En az şu 5 assert:
   - 4 kolonun tamamı göç dosyasında geçiyor (ad kontrolü).
   - `DEFAULT 0` dizgisi göç dosyasında **yok**.
   - girdisi boş firma → her skor `None`.
   - `compute_ensemble_score` SSOT formülüyle elle hesaplanan bir örnekle birebir eşleşiyor (en az 2 senaryo: bonuslu/bonussuz).
   - `company_capabilities` boş tablo verince `fit_score` `None` döner, hata fırlatmaz (F3 gap senaryosu).
10. Mandalı **kır**: bir assert'i geçici ters çevir, kırmızı gördüğünü teslim özetine yaz. Yeşili geri al.

## Kabul kriteri

- [ ] `0049_firsat_skorlari.sql` + `down/0049_firsat_skorlari.down.sql` diskte.
- [ ] `python -m pytest tests/test_schema_validation.py tests/test_firsat_skorlari.py` yeşil.
- [ ] 4 kolon adı SSOT satır numarasıyla birlikte COMMENT'te yazılı.
- [ ] Hiçbir skor kolonunda `DEFAULT 0` yok (D-249).
- [ ] Tabloya yazan tek fonksiyon `firsat_recalc()`; grep ile ikinci yazıcı yok (D-256/2).
- [ ] F3 gap senaryosu (boş capability tablosu → `fit_score=None`) test edildi.
- [ ] Mandal kırılarak doğrulandı; kırmızı çıktı teslim özetinde.

## Kurallar (VERI-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md:215-266`.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir (D-260).
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Hesaplama bu görevde çalıştırılmaz** — canlı DB'ye veri yazmak ayrı görevdir (D-238). Bu iş şema + fonksiyon + mandal ile biter.
- **F3 bitmeden gerçek Fit skorları beklenmez** — bu bilinen ve kabul edilen bir sınırlamadır, görev bunu teslim özetinde tekrar belirtir.
- **Teslimden önce** `hubs/VERI_KALITESI_HUB.md` "Kapanan işler" bölümüne `VERI-SKOR-MOTORU-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmazsa **uydurma, durma — yaz**:

```bash
python scripts/ajan_chat.py ac utku VERI-SKOR-MOTORU-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-SKOR-MOTORU-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-SKOR-MOTORU-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-SKOR-MOTORU-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312).**

```bash
python scripts/gorev_kutusu.py bak --ajan utku
python scripts/ajan_chat.py oku --son 10
```

- Mesaj varsa → cevapla. Yeni görev varsa → `al` ile al. İkisi de boşsa → `basla --ajan utku`.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-249, D-256, D-260, D-319)
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/plans/brief_utku_VERI-RISK-MOTORU-01]]
- [[plans/_brief_sablon]]
