# Brif — VERI-SEKTOR-01: Sektör adını kurtar, normalleştir, NACE'nin YANINA koy

**Sahip:** utku · **Öncelik:** P1 · **Süre:** 3s · **Veren:** ihsan
**Önkoşul:** yok (NACE işlerinden **bağımsız** ilerleyebilir)
**Kardeş görevler:** `VERI-NACE-SOZLUK-01`, `VERI-NACE-TEMIZ-01`

---

## 1. Neden bu görev var

`VERI-NACE-TEMIZ-01` ölçümünde baskentosb'un 761 firmasının NACE yerine
sektör adı taşıdığı görüldü. Ürün sahibi kararı: **"atmayalım, sektör adı da
önemli."** Doğru karar — ama ölçünce iş 761 firmadan çok daha büyük çıktı.

## 2. ÖLÇÜM — veri zaten var, tamamı çöpe gidiyor

`source_records.raw_payload` içinde **`sektor` alanı dört kaynağın üçünde
dolu**, ama `companies` tablosunda sektör kolonu **yok**:

| Kaynak | Kayıt | `sektor` dolu | Biçim |
|--------|-------|---------------|-------|
| ostim.org.tr | 9513 | **8336 (%87.6)** | sektör adı (+ sayaç eki) |
| baskentosb.org.tr | 761 | **761 (%100)** | sektör adı |
| aso.org.tr | 592 | **592 (%100)** | "30. MESLEK GRUBU" |
| ivedik.org.tr | 3134 | 0 | — |

**Toplam 9689 kayıt sektör bilgisi taşıyor ve hiçbiri kullanılmıyor.**

`companies` tablosundaki sektör/NACE ilgili kolonlar şunlar — sektör adı için
yer yok:

```
nace_code      8900 dolu
nace_source   14003 dolu
nace_validity 14003 dolu   (içinde NACE kodu var — KOLON-01'in konusu)
nace_name       330 dolu
```

## 3. Normalleştirme ölçüldü — iş küçük, kazanç büyük

Sayaç eki temizliği (`"Otomotiv1163"` → `"Otomotiv"`) + aksan/boşluk
sadeleştirmesi uygulandığında:

| | |
|---|---|
| HAM eşsiz ad | 95 |
| SADE eşsiz ad | **78** |
| Kaynaklar arası **ortak** ad | **51** (2392 firma) |

78 satırlık bir sözlük. Elle yazılır, bir öğleden sonra sürer.

**Varyant örnekleri** (aynı şey, iki yazım — sayaç eki yüzünden):
```
"Çeşitli Ticari Faaliyetler"  /  "Çeşitli Ticari Faaliyetler410"
"Makine ve Makine Ekipmanları" /  "Makine ve Makine Ekipmanları757"
"Tekstil ve Deri"              /  "Tekstil ve Deri71"
```

Bu sayaç ekleri, `nace_code` kolonuna sızan `1163`/`794`/`757` çöpüyle **aynı
kökten**: kazıyıcı sektör sayfasındaki firma sayacını metne yapıştırmış.
TEMIZ-01 bunları `nace_code`'dan siliyor; bu görev `sektor`'den söküyor.

**Ortak adlar köprü kuruyor** — en büyük 6 tanesi:
```
METALURJI VE MAKINA SANAYI  846 firma   [baskentosb + ostim]
DIGER                       453         [baskentosb + ostim]
KIMYA LABARATUVAR           124         [baskentosb + ostim]
GIDA                         73         [baskentosb + ostim]
SAVUNMA                      71         [baskentosb + ostim]
MEDIKAL ILAC                 55         [baskentosb + ostim]
```
İki farklı OSB aynı sektör adını kullanıyor → tek sözlükle ikisi de bağlanır.

## 4. İKİ ANOMALİ — ölçümde çıktı, ayrıca ele alınmalı

### 4a. ASO'nun meslek grubu xlsx ile eşleşmiyor (ama gerek de yok)

Resmi xlsx'in meslek kodu biçimi: `H.14`, `E.07`, `K.09` — **harf.sayı**.
ASO'nun verdiği: `30. MESLEK GRUBU` — **sadece sayı**. 41 eşsiz numaranın
xlsx'te karşılığı **yok** (0 eşleşme).

**Ama bu bir kayıp değil.** ASO zaten firma başına gerçek NACE veriyor:

```
sektor=30. MESLEK GRUBU  naceKod=41.00.01  detay="İkamet amaçlı binaların..."
sektor=39. MESLEK GRUBU  naceKod=35.12.00  detay="Yenilenebilir kaynaklard..."
sektor=18. MESLEK GRUBU  naceKod=25.93.03  detay="Telden yapılan diğer ürü..."
```

**Altı haneli, tanımıyla birlikte.** ASO'nun meslek grubunu NACE'ye çevirmeye
çalışmak gereksiz iş — cevap zaten `naceKod` alanında duruyor.

> **D-234 kontrolü gerekli:** ASO 6 hane veriyor (`41.00.01`), `companies`'te
> 4 hane duruyor (`41.10`). Seviye kısaltılmış → D-234 ihlali. Bu SOZLUK-01'in
> kapsamında, burada sadece işaret ediyorum.

### 4b. ostim kaynağında ASO biçimli veri var — 102 kayıt

```
2SSOFT YAZILIM BİLİŞİM A.Ş.        | 35. MESLEK GRUBU | kaynak=None
5S OTOMOTİV İMALAT SAN. TİC. A.Ş.  | 24. MESLEK GRUBU | kaynak=None
AKKOR ISIL İŞLEM ÇELİK İMALAT      | 38. MESLEK GRUBU | kaynak=None
```

OSTİM bir OSB, ASO bir oda. OSTİM sayfasında "35. MESLEK GRUBU" yazmaz.
`raw_payload.kaynak` alanı da `None` — normalde kaynak adı yazar.

İki olasılık: (a) ASO kaydı yanlış `source_id` ile yazılmış, (b) firma iki
kaynakta birden var ve birleştirme sırasında payload karışmış.

**Ayrı görev açılacak: `VERI-KAYNAK-SIZINTI-01`.** 102 kayıt küçük ama
sebebi önemli — aynı hata sessizce daha büyük ölçekte olabilir.

## 5. Yapılacak

### 5.1 Sözlük dosyası: `data/sektor/sektor_sozluk.json`

78 sade adı içeren, elle bakımlı dosya. Her satır:

```json
{
  "sade": "METALURJI VE MAKINA SANAYI",
  "gosterim": "Metalurji ve Makina Sanayi",
  "varyantlar": ["Metalurji ve Makina Sanayi"],
  "kaynaklar": ["ostim.org.tr", "baskentosb.org.tr"],
  "nace_ipucu": ["24", "25", "28"]
}
```

`nace_ipucu` **kesin eşleme değil**, NACE bölüm (2 hane) düzeyinde daraltma.
"Metalurji ve Makina" → 24/25/28 bölümleri. Ünvan kesişimi (D-234) bu
ipucunu **filtre** olarak kullanır, cevap olarak değil.

### 5.2 Şema: `companies` tablosuna iki kolon

```sql
alter table companies add column sector_name    text;  -- gösterim adı
alter table companies add column sector_source  text;  -- hangi kaynaktan
```

`sector_name` **NACE'nin yerine geçmez, yanında durur.** İkisi farklı şey:
NACE resmi sınıflama, sektör adı OSB'nin kendi ticari segmenti. İkisi de
ayrı değer taşıyor.

### 5.3 Doldurma

`raw_payload.sektor` → sadeleştir → sözlükten `gosterim` al → yaz.
`sector_source` = kaynak adı.

ASO'nun `N. MESLEK GRUBU` değeri **sektör adı değildir** — `sector_name`'e
yazılmaz. `sector_source='aso_meslek_grubu'` ile numara ayrı tutulur veya
tamamen atlanır (ASO'nun gerçek NACE'si zaten var).

## 6. Kabul ölçütü (test)

- `data/sektor/sektor_sozluk.json` 78 satır, her satırda `sade`+`gosterim`
- Sadeleştirme fonksiyonu için test: `"Otomotiv1163"` → `"OTOMOTIV"`,
  `"Tekstil ve Deri71"` → `"TEKSTIL VE DERI"`
- Doldurma sonrası `sector_name` dolu firma sayısı raporda yazılı
- **Eşleşmeyen sektör adı sayısı 0** — 78'in tamamı sözlükte olmalı
- `nace_code` kolonu **değişmemiş** (bu görev NACE'ye dokunmaz)

## 7. İtirazlar / sınırlar

**"Diğer" 453 firma taşıyor.** Bu bir sektör adı değil, bilgi yokluğu.
Sözlüğe alınmalı ama `nace_ipucu` boş bırakılmalı — yoksa 453 firmayı yanlış
yöne süreriz.

**İvedik 3134 kayıtla en büyük ikinci kaynak ve sektör bilgisi sıfır.**
Bu görevin kapsamı dışında ama not: ivedik'te sektör verisi sitede var mı,
yoksa kazıyıcı mı almıyor — ayrı keşif konusu.

**9689 kayıt ≠ 9689 firma.** Aynı firma birden çok kaynakta olabilir. Firma
bazında gerçek kapsam doldurma sonrası ölçülecek; şimdiden oran vaat etmiyorum.

---

*ponytail: 78 satırlık elle sözlük + iki kolon. Skipped: otomatik sektör
sınıflandırma, sektör hiyerarşisi (üst/alt sektör) — 78 ad için gereksiz.
Add when: kaynak sayısı artıp eşsiz ad 200'ü geçerse.*
