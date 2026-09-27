---
baslik: Veri Kaynağı Kuralları — Ne Yaptık, Neden Yaptık
tarih: 2026-09-27
sahip: kahin
durum: yurutmede
ilgili_kararlar: [D-235, D-234]
ilgili_gorevler: [VERI-KAZIYICI-DONGU-01, VERI-KAYNAK-TURU-01, VERI-NACE-TEMIZ-01, VERI-SEKTOR-01]
---

# Veri Kaynağı Kuralları

## Neden döküman yetmez

Bu dökümanın kendisi **kural uygulatmaz**. Kanıt: üç kazıyıcı (`ivedik`,
`ostim`, `ostim_full`) **aynı** sayfalama hatasını **bağımsızca** yaptı; hiçbiri
diğerini okumadı. Bu yüzden her kuralın bir **mandal testi** var — kuralı çiğneyen
kod testi kırar. Mandalı olmayan satır kural değil, tavsiyedir.

| Kural | Ne der | Mandal (testi kim tutuyor) | Durum |
|---|---|---|---|
| **K-1** | Kazıyıcı kendi `while True` sayfalama döngüsünü yazmaz; `sayfa_dongusu()` şablonunu kullanır | [`test_kaziyici_sablon_denetimi.py`](../tests/test_kaziyici_sablon_denetimi.py) + [`test_kaziyici_sayfa_dongusu.py`](../tests/test_kaziyici_sayfa_dongusu.py) | zorlanıyor |
| **K-2** | Kaynak iki kolonla tanımlanır: `kaynak_adi` + `kaynak_turu` (`osb`/`oda`); güven seviyesi türden türetilir | yok — VERI-KAYNAK-TURU-01 ile gelecek | **tavsiye** |
| **K-3** | Ham çıktı `"w"` ile yazılır; `"a"` kipi yalnız tekilleştirmeli resume akışında | [`test_kaziyici_sablon_denetimi.py`](../tests/test_kaziyici_sablon_denetimi.py:64) | zorlanıyor |
| **K-4** | Tur, tekil oran denetimi olmadan başarılı sayılmaz: `tekil/toplam < %95` → tur başarısız | yok — VERI-KAZIYICI-DONGU-01 ile gelecek | **tavsiye** |
| **K-5** | İlk istekte HTTP durumu kontrol edilir; 401/403 sessiz boş dönüş değil **açık hata** | yok — VERI-KAZIYICI-DONGU-01 ile gelecek | **tavsiye** |

"tavsiye" satırları geçici. Mandalı yazılınca "zorlanıyor" olur. Bu tablo
sistemin **kendi kurallarına ne kadar uyabildiğinin** dürüst ölçüsüdür: 5 kuraldan
şu an 2'si makine tarafından korunuyor.

---

## K-1 — Sayfalama "liste boşalınca dur" ile bitmez

Üç koruma **birlikte** gerekir:
1. **Sayfa imzası tekrarı** — sayfadaki ünvanların birleşimi görüldüyse dur.
2. **Tekil ünvan süzgeci** — aynı ünvan ikinci kez yayılmaz.
3. **Sert tavan** (`MAX_SAYFA`) — her şey başarısız olursa yine durur.

Tek uygulama yeri: [`BaseOsfbScraper.sayfa_dongusu()`](../src/company_master/etl/scrapers/base_osfb_scraper.py:100).

**Ödenen bedel — İvedik OSB, ölçüm 2026-09-27:**

| Ölçüm | Değer |
|---|---|
| jsonl satır sayısı | 3375 |
| **tekil firma sayısı** | **14** |
| kopya oranı | **%99.6** |
| tekrar deseni | 15 firma × 224 sayfa |
| DB'ye akan hayalet kayıt | 3134 |

Kök neden: WordPress geçersiz `?page/9999/` isteğine **404 değil sayfa 1** döner.
Kod `if not firmalar: break` bekliyordu — o koşul **asla** gerçekleşmez.

Kalan borç: [`ostim_scraper.py:454`](../src/company_master/etl/scrapers/ostim_scraper.py:454),
[`ostim_scraper_full.py:135`](../src/company_master/etl/scrapers/ostim_scraper_full.py:135)
— ikisi de test izin listesinde, VERI-KAZIYICI-DONGU-01 ile şablona taşınacak.

---

## K-2 — Kaynak "türü" ile kaynak "adı" ayrı kolonlardır

| Nitelik | Örnek | Ne söyler |
|---|---|---|
| `kaynak_adi` | `ostim`, `ivedik`, `baskentosb`, `aso` | hangi siteden geldi |
| `kaynak_turu` | `osb`, `oda` | **verinin anlamı ne** |

| Tür | Kayıt niteliği | NACE kalitesi | Türetilen güven |
|---|---|---|---|
| **oda** (ASO) | üyelik/tescil | **6 haneli, resmi** | A |
| **osb** + firma sayfası | coğrafi | firmanın kendi beyanı | B |
| **osb** + sektör menüsü | coğrafi | **varsayılan/çöp** | C |

**Ödenen bedel.** ASO ile OSB'ler aynı tabloya aynı anlamla kondu, ETL ikisine
aynı işlemi uyguladı:

- ASO'nun **6 haneli resmi** NACE'i, OSTİM'in **4 haneli varsayılan** kodu ile
  eşit muamele gördü → 592 resmi kayıt 5705 çöp kaydın içinde kayboldu.
  (A/B/C güven seviyeleri bu ayrımı **geri kurmak** için icat edildi.)
- ASO biçimli 102 kayıt `ostim` kaynağında `kaynak=None` duruyor
  (VERI-KAYNAK-SIZINTI-01) — tür kolonu olsaydı ilk günde yakalanırdı.
- ASO meslek grubu (`30.`) resmi xlsx ile (`H.14`) eşleşmiyor; ama **gereksiz** —
  oda verisinde NACE zaten doğrudan var, meslek grubu köprüsü aramak kayıp emek.

---

## K-3 — Ham dosya "w" ile yazılır

**Ödenen bedel.** İvedik'te `file_mode = "a" if OUTPUT_PATH.exists() else "w"`
vardı; her yeniden deneme kopyaları üst üste yığdı. 3375 satırın hangisi döngüden,
hangisi tekrar çalıştırmadan geldi — artık ayırt edilemiyor.

Aynı desen `baskent_scraper.py`'de de bulundu (test yazıldığı anda yakaladı) ve
düzeltildi; 761 kaydı ikiye katlama riski kapandı.

---

## K-4 — Durum dosyası "iş bitti" kanıtı değildir

**Ödenen bedel.** İvedik `.scrape_state.json` `completed_pages: 225,
total_records: 3375` diyordu — teknik olarak "başarılı". Gerçek 14 firma.
Sayaç doğru sayıyordu, **yanlış şeyi** sayıyordu.

---

## K-5 — Site erişimi her turda yeniden doğrulanır

**Ödenen bedel.** İvedik 2026-09-27 ölçümünde tüm yollara **403** döndü (UA'sız
istekte **401**) — WAF devreye girmiş. Bu durumda kazıyıcı "liste boş, bitti" diye
**başarıyla** sonlanır; elimizdeki bozuk veri "güncel" sanılır.

---

## Bu dökümanın kullanımı

Yeni kazıyıcı veya veri kaynağı eklenirken **önce tabloya** bakılır.
Yeni arıza kök nedene kadar kazılırsa **K-N** olarak eklenir; altına mutlaka
**ölçülmüş sayı**, satırına mutlaka **mandal** yazılır. Sayısı olmayan kural
kural değildir; mandalı olmayan kural uygulanmaz.

## İlgili Nodlar

- [[AGENTS]]
- [[plans/brief_utku_VERI-NACE-TEMIZ-01]]
- [[plans/brief_utku_VERI-KAYNAK-SIZINTI-01]]
