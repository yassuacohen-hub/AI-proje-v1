# OSB Veri Seti Temizlik Raporu — VERI-OSB-TEMIZLIK-01

**Ajan:** yasu · **Oncelik:** P0 · **Tarih:** 2026-10-01 · **Guncelleme:** 2026-10-02
**Kapsam:** `data/osb/` · **Durum:** **UYGULANDI** (3 karar ihsan onayıyla, 2026-10-02)
**Arac:** `scripts/osb_veri_temizle.py` (kalıcı — R1: geçici script yasak)

> D-260: bu rapor beyan degil, calistirilmis komut ciktisinin kaydidir.

---

## 0. Karar ve sonuc (2026-10-02)

Ihsan 3 karari verdi: **(1)** ayni firmanin iki OSB uyeligi **silinmesin**,
**(2)** bozuk kodlama icin en iyi cozum uygulansin, **(3)** 3. karar 1. karara
benzer — **silmeden** bir yontem.

### Terim sorusu: "bayi mi, buyume mi, coklu merkez mi?"

**Yanit: ucu de degil. Dogru kavram `company_locations.location_type` =
`factory` (tesis).** Gerekce olculdu:

| Aday | SSOT kaniti | Veriye uyar mi? |
|---|---|---|
| `bayi` | `(HUGIns).txt:669` "Bayi sayisi" — sira alani, magaza/sube sayaci | HAYIR — bayi = satis kanali, OSB uyeligi degil |
| `buyume` | 4 gecis, trend gostergesi | HAYIR — olgu degil, yorum |
| `coklu merkez` | `:745` "Merkez varlik", `:913` operasyon merkezi | YANLIS CAGRI — SaaS paneli icin kullanilmis |
| **`factory` (tesis)** | `0002_relations.sql` `company_locations.location_type IN ('headquarters','factory','branch','warehouse','office','workshop','unknown')` | **EVET — zaten semada var** |

**Olcum 1'i kesinlestirdi:** 44 grubun **44'unde de adres BIREBIR AYNI.**
Ornegin `anadolu` ve `ostim` klasorlerinde ayni kayit:
```
KLASOR: anadolu | adres: 'BAGDAT CAD. 396' | slug: anadolu-akaryakit-ve-ticltdsti
KLASOR: ostim   | adres: 'BAGDAT CAD. 396' | slug: anadolu-akaryakit-ve-ticltdsti
```
Yani bunlar "ayni firmanin iki OSB uyeligi" degil, **AYNI FISIKSEL TESISIN
iki klasorde birer kopyasi** — veri hatasi. Bu yuzden **`company_slug`
global tekilligi (company_id) dogru kimliktir**; OSB uyeligi degil.

### Uygulanan kural

`if not kuru:` — varsayilan **KURU** (veriye dokunmaz). Yazmak icin `--yaz`.

1. **Slug kurali (KARAR 2):** Turkce→ASCII, kucult, noktalama SILINIR,
   bosluk→tire. `OSTIM_TEMIZ.jsonl` kaynaginin kuraliyla birebir ayni.
2. **Bozuk kodlama (KARAR 2):** `legal_name` icinde `?` varsa **slug URETILMEZ**;
   `slug_durumu="kaynak_eksik_bozuk_kodlama"` isaretiyle durur (D-260).
3. **Tekillestirme (KARAR 1+3):** ayni slug + **ayni adres** → kopya
   `tekillestirildi` isaretiyle KORUNUR. **Kayit SILINMEZ** (D-262).

---

## 1. Once / Sonra

```
$ python scripts/osb_veri_denetim.py        # ONCE
TOPLAM kayit     : 8987
TEKIL company_slug: 8296
MUKERRER         : 44
KIMLIKSIZ satir  : 647
MOJIBAKE ad      : 0

$ python scripts/osb_veri_denetim.py        # SONRA
TOPLAM kayit     : 8987          <-- DEGISMEDI (kayit silinmedi)
TEKIL company_slug: 8795
MUKERRER         : 48
KIMLIKSIZ satir  : 144          <-- 647 -> 144 (503 uretildi)
MOJIBAKE ad      : 0

$ python scripts/osb_veri_denetim.py --self
self-check OK
```

| Olcu | Once | Sonra | Yorum |
|---|---|---|---|
| TOPLAM kayit | 8987 | **8987** | silme yok — D-262 |
| KIMLIKSIZ | 647 | **144** | 503 slug uretildi |
| TEKIL slug | 8296 | 8795 | +499 |
| MUKERRER | 44 | **48** | +4 yeni cakisma, hepsi KORUNDU |

**Kabul kriteri `KIMLIKSIZ: 0` saglanmadi** — 144 satir bilerek birakildi.
Gerekce: bu satirlar bozuk kodlama tasiyor; kanitsiz slug yazmak kalici
kimligi bozardi (D-260). Brif bu olasiligi ongormemis; kural "N" rapora yazilir.

---

## 2. Bozuk kodlama: 144 satir (KARAR 2)

Olcum: `legal_name` icinde `?` tasiyan **144** satir, hepsi
`aso_full_clean.jsonl` kaynakli. Dagilim: `kazan_hab` 91, `anadolu` 25,
`aso` 16, `polatli` 7, `cubuk` 3, `aso2` 1, `dokumcu` 1.

Ornek:
```
(?FLAS NEDEN?YLE) TASF?YE HAL?NDE ANADOLU ELEKTR?K SANAY? VE T?CARET L?M?TED ??RKET?
```

**Uygulanan en iyi cozum:** slug uretilmedi, kayit isaretlendi:
```json
"slug_durumu": "kaynak_eksik_bozuk_kodlama",
"slug_notu": "legal_name icinde '?' var: kaynak kodlamasi bozuk (D-260)"
```

**Neden kaynak duzeltilmedi:** `aso_full_clean.jsonl` tekrar kazima
gerektirir; bu brifin kapsami disi ve kaynak site erisimi ayrica karar ister.

**Denetim koru noktasi (KRITIK):** `osb_veri_denetim.py:44` yalnizca
`\ufffd` arar. Bu satirlarda `?` vardir, `\ufffd` YOKTUR — bu yuzden cikti
`MOJIBAKE: 0` diyor ve **kabul kriteri bu 144 satiri kor geciyordu.**

---

## 3. Ayni tesis: 44 kopya (KARAR 1)

44 grubun 44'u de ayni adresli, iki OSB klasorunde. OSB ciftleri:
`anadolu<->ostim` 23, `kazan_hab<->ostim` 20, `elmadag<->ostim` 1.

**Kayit SILINMEDI.** Her kopya su isareti tasir:
```json
"tekillestirildi": {
  "slug": "anadolu-akaryakit-ve-ticltdsti",
  "korunan_osb": "anadolu",
  "korunan_dosya": "anadolu",
  "gerekce": "ayni adres + ayni slug; ayni fiziksel tesis"
}
```
Korunan kayit `osb_slug` alfabetik ilk olan (deterministik — her kosuda ayni).

**Neden bu dogru:** silme 8987→8943 dusururdu, `MUKERRER: 0` cikardi — ama
OSB komsulugu kaybolurdu. **Kriter yesile cevirir, veriyi bozardi.**

---

## 4. Korunan cakismalar: 7 kayit / 4 slug (KARAR 3)

Yeni uretilen slug'lardan 4'u mevcut slug ile cakisti:

| Cakisan slug | Durum |
|---|---|
| `ankara-rakor-hidrolik-makine-ltd-sti` | baskent ↔ ostim, **farkli adres** |
| `orka-mekatronik-insaat-sanayi-ve-ticaret-ltd-sti` | baskent ↔ ostim, **farkli adres** |
| `erdogan-saglamcubukcu` | cubuk ↔ ostim, **ayni adres** → kopyalanmis tesis |
| `yurtici-kargo-servisi-as` | coklu OSB |
| `roketsan-roket-sanayi-ve-ticaret-as` | coklu OSB |

**Kural:** adres farkliysa kayit KALIR ve `slug_cakismasi` isareti tasir:
```json
"slug_cakismasi": {"slug": "...", "adres_sayisi": 2, "osb_sayisi": 2,
  "cozum": "ayri adres -> ayri kayit korunur; slug farklidir"}
```
Adres ayniysa kopya isaretlenir (bolum 3). **Hicbir kayit silinmedi.**


## 5. Yapilan isler

| Adim | Durum | Kanit |
|---|---|---|
| Slug kurali cikarildi | YAPILDI | `osb_veri_temizle.py:slug_uret` — kaynak `OSTIM_TEMIZ.jsonl` kuraliyla birebir |
| 503 slug uretildi | YAPILDI | `KIMLIKSIZ 647 → 144` |
| 144 bozuk satir isaretlendi | YAPILDI | `slug_durumu` kolonu, slug URETILMEDI |
| 44 kopya isaretlendi | YAPILDI | `tekillestirildi` kolonu, kayit SILINMEDI |
| 7 cakisma korundu | YAPILDI | `slug_cakismasi` kolonu |
| `osb_veri_denetim.py --self` | GECTI | `self-check OK` |
| Hub "Kapanan isler" | YAZILDI | `hubs/OSINT_VERI_TOPLAMA_HUB.md` |
| Supabase yazimi | **YAPILMADI** | brif kapsam disi — ihsan'in |

**SILINEN KAYIT: 0.** D-262 geregi hicbir kayit dusurulmedi; yalniz kimlik
tekillestirildi ve kopyalar isaretlendi. `TOPLAM kayit` 8987'de sabit kaldi.

### Arac

`scripts/osb_veri_temizle.py` — **kalicidir** (R1: gecici script yasak).
`data/osb/` her `osb_veri_seti_uret.py` kosusunda yeniden uretilir; gecici bir
betikle temizlik bir sonraki uretimde kaybolurdu.

**Varsayilan KURU calisir** (veriye dokunmaz). Yazmak icin `--yaz`.
Bu bir kaza ile kesinlestirildi: ilk kosuda varsayilan YAZIYORDU, 12 dosya
degisti; `git checkout` ile geri alindi ve `if kuru:` → `if not kuru:`
duzeltildi. Kural: **veri degistiren aracin varsayilani yazmamalidir (D-244).**

### Tekrar calistirilabilir mi

Evet — ayni girdide ayni sonucu verir (deterministik):
- kopya secimi `osb_slug` alfabetik sirasiyla yapilir
- slug kurali saf fonksiyondur
- `ON CONFLICT` benzeri **yok**: dosya satiri **guncellenir**, cogaltilmaz

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] — gorev kapanis kaydi (B-14)
- [[Huginn Data Insights/AGENTS]] — D-218 · D-245 · D-249 · D-260 · D-262 · D-244 · D-312
- `scripts/osb_veri_temizle.py` — bu gorevin kalici araci
- `scripts/osb_veri_denetim.py` — olcum kapisi (kabul kriteri)
- [[Huginn Data Insights/data/orchestrator/osb_rapor_2026-09-29]] — onceki gorev
- [[Huginn Data Insights/plans/brief_yasu_VERI-OSB-TEMIZLIK-01]] — bu raporun brifi
- [[Huginn Data Insights/plans/brief_yasu_VERI-OSB-Tazelik-01]] — bagli gorev
- [[Huginn Data Insights/plans/brief_yasu_VERI-ENTITY-GRAPH-01]] — ayni tekillik sorusu
- [[Huginn Data Insights/docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM]] — cevapsiz sorular
- [[Huginn Data Insights/docs/BORC_DEFTERI]] — kalan borclar

---
