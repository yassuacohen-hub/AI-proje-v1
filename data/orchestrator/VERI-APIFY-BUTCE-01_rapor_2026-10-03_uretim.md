# VERI-APIFY-BUTCE-01 — Rapor (Üretim)

**Görev:** `VERI-APIFY-BUTCE-01` · **Ajan:** utku · **Tarih:** 2026-10-03
**Kural:** D-66 (brif varsayımı ölçülür) · D-245/D-249 (beyan değil ölçüm, bilinmeyen 0 yazılmaz) · D-260 (ayar sonrası değer API'den okunur) · D-243 (prova diske yazmaz) · D-318 (bulgu kapısı) · D-210 (chat)

---

## Ne yapıldı

Brif üç madde veriyordu: (1) aylık kullanımı USD olarak ölçen araç, (2) ölçülen
tutar + tarih + tavan + konsol kapatma prosedürünü içeren belge, (3) konsolda 10 USD
tavanı ve ayar sonrası API'den okunan değer.

**1) Ölçüm aracı — `scripts/apify_butce_olc.py`**

| Çıkış | Anlam |
|---|---|
| `0` | Ölçüldü, tavan içinde **ve** platform tavanı yerel tavanı aşmıyor |
| `2` | Tavan aşıldı **veya** platform tavanı yerel tavandan büyük |
| `3` | Ölçülemedi (token yok / ağ / 401 / alan bulunamadı) |

Salt okunur (`GET`); hiçbir yerde limit değiştirme yok. Token stdout'a yazılmaz.
Bilinmeyen değer `0` **yazılmaz** — `rc=3` döner, "ölçülemedi" denir (D-249), böylece
sıfır harcama ile ölçülememe ayırt edilir.

**2) Ölçüm — API'den, ekran görüntüsü değil**

| Ölçüm | Değer | Kaynak |
|---|---|---|
| Aylık harcanan | **0.0000152605 USD** | `GET /v2/users/me/limits` → `data.current.monthlyUsageUsd` |
| Konsolda ayarlı tavan | **10 USD** | aynı yanıt → `data.limits.maxMonthlyUsageUsd` |
| Oran | %0.0002 | ölçüm ÷ 10 |
| Fatura döngüsü | 2026-09-10 → 2026-10-09 | `data.monthlyUsageCycle` |
| Plan | `FREE`, `isPaying: false`, taban ücret 0 USD | `GET /v2/users/me` |
| Aylık ücretsiz kredi | 5 USD | `plan.monthlyUsageCreditsUsd` |
| Çalıştırılmış Actor | 0 | `data.current.actorCount` |

Alan adları **tahmin edilmedi**; canlı yanıt üzerinden okundu. Yedek ölçüm
(`/v2/users/me/usage/monthly` → `totalUsageCreditsUsdAfterVolumeDiscount`) aynı sayıyı
verdi. Harcama **düşen değil, artan** bir sayaçtır: ilk ölçüm `0.0000141192`,
teslim öncesi son ölçüm `0.0000152605` USD — aradaki fark yeni API çağrısından
gelen dış veri transferi, tavanı etkilemiyor. Canlı çıktı:

```
[TARIH]  2026-10-03
[KAYNAK] https://api.apify.com/v2/users/me/limits
[KULLANIM] 0.0000152605 USD / tavan 10 USD = 0.0002%
[PLATFORM TAVANI] 10
[FATURA DONGUSU] 2026-09-10T00:00:00.000Z -> 2026-10-09T23:59:59.999Z
[SONUC]  OK - butce tavani icinde ve platformda da esit
rc=0
```

**3) Belge — `docs/APIFY_BUTCE.md`**

Ölçülen tablo, ölçüm komutu, tavanın 10 USD olarak **zaten** ayarlı olduğunun API
kanıtı, gelecekte değiştirmek için konsol prosedürü, gerçek fatura riskinin **0 USD**
olduğunun üç bağımsız kanıtı ve güvenlik notları.

**4) Kapanış kapıları**

- Kodlama denetimi: kendi dosyalarımda **temiz** (dosya sonu eklendi).
- Bulgu defteri: **5 satır** eklendi (bulgu_defteri.md 133 satır, mojibake 0).
- Hub: B-14 kaydı eklendi (`hubs/PLAN_STRATEGY_HUB.md` 105 satır).
- Chat: `ihsan`'e açıldı (brif varsayımı çürüdüğü için), ölçüm sonucuyla **kapandı**.
- Context: `utku_project_context.md` §KALDIĞIM YER + §Tuzaklar güncellendi.

## Değişen dosyalar

| Dosya | Tür |
|---|---|
| `scripts/apify_butce_olc.py` | **yeni** (kilitli) — ölçüm + tavan kapısı |
| `tests/test_apify_butce_olc.py` | **yeni** — 17 test |
| `docs/APIFY_BUTCE.md` | **yeni** (kilitli) — bütçe belgesi |
| `data/orchestrator/VERI-APIFY-BUTCE-01_rapor_2026-10-03_uretim.md` | **yeni** — bu rapor |
| `hubs/PLAN_STRATEGY_HUB.md` | B-14 satırı eklendi |
| `data/orchestrator/bulgu_defteri.md` | 5 satır eklendi |
| `data/orchestrator/ajan-chat.jsonl` | 1 kayıt açıldı + kapandı |
| `utku_project_context.md` | hafıza güncellendi |

Geçici probe betikleri (`_tmp_apify_alan_ara.py`, `_tmp_apify_hesap.py`,
`_tmp_kayit_ekle.py`) çalıştırılıp **silindi**.

## Test sonuçları

```
python -m pytest tests/test_apify_butce_olc.py -q   -> 17 passed
python -X utf8 scripts/apify_butce_olc.py --tavan 10 -> rc=0
python -X utf8 scripts/kodlama_denetim.py             -> apify/buce bulgusu 0
```

Kapsam: `/v2` yol birleştirme (5 parametrik durum), `.env` ayrıştırma (tırnak, yorum,
boş değer, dosya yok), token sızıntısı, ölçülememe durumları (token yok / 401 /
200-ama-alan-yok), tavan aşımı, **platform tavanı > yerel tavan** güvenlik açığı,
`usage/monthly` yedeğine düşme, metin ve JSON çıktı.

## Bulgular

- 🔴 **BRIF VARSAYIMI YANLIŞTI (D-66/D-260).** Brif "Apify konsolunda aylık limiti
  10 USD olarak ayarla" diyordu; ölçüm `maxMonthlyUsageUsd = 10` döndü — tavan
  **zaten** 10. Ayar gereksizdi, konsola **hiç müdahale edilmedi**, "ayarladım" diye
  ekran görüntüsü uydurulmadı. Belgede prosedür olarak yazıldı.
- 🔴 **`/v2/v2` YOL TUZAĞI — kırmızı sonuç yanıltıcıydı (D-309/3).** `.env` içindeki
  `APIFY_API_BASE_URL` `.../v2` ile bitiyor; buna bir de `/v2` eklenince istek
  `/v2/v2/...` oldu ve Apify **404** döndürdü. İlk ölçüm "ölçülemedi" görünüyordu ama
  sebep endpoint ya da token değil **yol birleştirme** hatasıydı. Alan adları tahmin
  edilseydi bu sessizce "ölçülemedi" yazılır, tavan kontrolü yapılmamış sayılırdı.
- 🟡 **ÖLÇÜM BİLİMSEL GÖSTERİMDE ÇIKIYORDU.** Gerçek harcama `1.41192e-05` USD;
  float repr bütçe belgesinde okunmuyor. **Test bunu yakaladı** (beklenen
  `0.0000141`, gelen `1.41192e-05`) → `Decimal` sabit nokta biçimlendirme.
- 🟡 **YEREL BÜTÇE PLATFORMDA KORUNMAYABİLİR.** Kullanım 0 olsa bile konsoldaki
  `maxMonthlyUsageUsd` yerel `--tavan`dan büyükse 10 USD kuralı fiilen geçersizdir.
  Araç bunu ayrı kapı olarak denetler.
- 🟡 **ÜCRETSİZ PLANDA 10 USD GERÇEK TAVAN DEĞİL.** `plan.id=FREE`,
  `isPaying=false`, taban ücret 0, aylık kredi **5 USD**. Ücretsiz planda platform
  10 USD'ye değil kredi bitiminde durur; ücret kesilme riski **0 USD**. 10 USD tavanı
  **yükseltme sonrası** güvenlik sınırıdır.
- 🔵 **`ajan_chat.py oku --task-id` bayat doküman.** AGENTS.md bu bayrağı gösteriyor,
  CLI reddediyor (`unrecognized arguments`). Etkilemedi; tek doğrulama yolu `oku`
  çıktısından filtrelemek oldu. Ayrı borç, dokunulmadı.
- 🔵 **Fatura döngüsü takvim ayı değil.** `2026-09-10 → 2026-10-09` — hesap açılışına
  sabitlenmiş. Belgede yazılı; bütçe takibi ay bazında yapılırken yanlış gün sayılır.

## Eksik / erteleme

- **Yok: bilinmeyen ölçüm.** Token ve endpoint erişilebilir, alan adları canlıdan
  okundu, tavan geri okundu. Tahminle doldurulan tek sayı yok.
- **Ertelenen:** konsolda tavan değişikliği **gerekmedi** (zaten 10). İleride bir
  değişiklik yapılacaksa `docs/APIFY_BUTCE.md` §2'deki prosedür izlenir.
- **Ertelenen (pano kararı gerekir):** ücretli plana geçişte (`plan.id != FREE`)
  belge güncellenir. Araç planı **sorgulamaz**; `rc=2` yalnız **ölçülen** durumda
  gelir — tavan aşılırsa ya da platform tavanı yerel tavandan büyükse. Plan değişimi
  tek başına `rc=2` üretmez, bu yüzden belge güncellemesi elle yapılır. Pano bakımı
  D-77 gereği orkestratörde; ben görev açmadım, bulgu defterine yazdım.
- **Bilinen kapsam dışı:** tam repo baseline'ında önceden var olan kodlama ihlalleri
  (`scripts/ninerouter_anahtar_guncelle.py:60`, `tests/test_mojibake_bariyer.py:48`
  + 36 mojibake kaydı) duruyor. 9Router dosyalarına dokunulmaz kuralı gereği
  dokunulmadı; bu görevin kapsamı dışında.

## İlgili Nodlar

- [[Huginn Data Insights/docs/APIFY_BUTCE]] — bütçe belgesi
- [[Huginn Data Insights/scripts/apify_butce_olc]] — ölçüm aracı
- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] — B-14 kaydı
- [[Huginn Data Insights/AGENTS]] · [[D-260]] · [[D-249]] · [[D-243]]