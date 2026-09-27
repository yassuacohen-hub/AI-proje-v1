---
tur: plan-notu
durum: not-alindi
tarih: 2026-09-27
kaynak: urun-sahibi
bagimlilik: VERI-HAYALET-TEMIZ-01, VERI-IVEDIK-YENIDEN-01
---

# Genişleme Notu — Ankara Kaynak Evreni

> **Ürün sahibi talebi (2026-09-27):** "Bu iş bitince genişleme lazım — önce Ankara tüm OSB'ler, ATO ve diğer teknokentler, TTO ve kuluçka merkezleri."

## Şu anki kapsam (4 kaynak)

| kaynak | satır | durum |
|--------|-------|-------|
| ostim.org.tr | 9513 | çekiliyor |
| ivedik.org.tr | 3134 | hayalet, yeniden çekilecek |
| baskentosb.org.tr | 761 | çekiliyor |
| aso.org.tr | 592 | çekiliyor |

## Hedef kapsam — dört kuşak

Aşağıdaki liste **doğrulanmamış aday listesidir**. Her satır için site varlığı, firma dizini varlığı ve çekilebilirlik ayrı keşifle ölçülecek. Hiçbiri "kaynak var" sayılmayacak, ölçülmeden.

### 1. Kuşak — OSB'ler (organize sanayi bölgeleri)

Ankara'da OSB sayısı 10'un üzerinde. Adaylar: ASO 1. OSB (Sincan), ASO 2. ve 3. OSB (Temelli), Anadolu OSB, Ankara Dökümcüler OSB, Polatlı OSB, Çubuk OSB, Akyurt OSB, Ankara Mobilyacılar (Siteler) OSB, Uzay-Havacılık İhtisas OSB (Kahramankazan), OSTİM Medikal İhtisas OSB.

**Tek doğru kaynak:** Sanayi ve Teknoloji Bakanlığı / OSBÜK resmi OSB sicili. Aday listesi elle yazılmayacak, **resmi sicilden çekilecek** — D-234'teki "resmi liste ana kaynak" ilkesinin aynısı.

### 2. Kuşak — Odalar

- **ATO** (Ankara Ticaret Odası) — üye sayısı OSB'lerin toplamından büyük olabilir; ölçek riski var.
- ASO — zaten var (592).
- Ankara Ticaret Borsası, Esnaf ve Sanatkârlar Odaları Birliği (ANKESOB) — ikinci dalga.

### 3. Kuşak — Teknokentler (TGB)

Adaylar: ODTÜ Teknokent, Bilkent CYBERPARK, Hacettepe Teknokent, Gazi Teknopark, Ankara Üniversitesi Teknokent, ASO Teknopark, OSTİM Teknopark.

**Tek doğru kaynak:** Sanayi ve Teknoloji Bakanlığı TGB resmi listesi.

### 4. Kuşak — TTO ve kuluçka/hızlandırıcı

TTO'lar üniversite bağlı (ODTÜ, Hacettepe, Bilkent, Gazi, AÜ, TOBB ETÜ, Atılım…). Kuluçka tarafında KOSGEB TEKMER'leri ve teknokent kuluçka programları.

**Uyarı:** Bu kuşak firma dizini değil **proje/girişim** dizini. Veri modeli farklı — girişim ≠ tescilli firma. Ayrı tablo mu, `companies`'e tür alanı mı — karar gerekli.

## Genişlemeden ÖNCE kapatılması gereken borçlar

Kaynak sayısını 4'ten 25'e çıkarmak, mevcut kusurları 6 katına çıkarır. Sıra:

1. **VERI-HAYALET-TEMIZ-01** — sayfalama hayaletleri temizlenmeli, yoksa her yeni kaynak aynı hatayı üretir.
2. **VERI-KAYNAK-BAG-01** — `source_records.company_id` yok; 25 kaynakta hangi bilginin nereden geldiği izlenemez hâle gelir.
3. **VERI-NACE-SOZLUK-01 / SEKTOR-01** — sektör sınıflaması oturmadan yeni kaynak eklemek, kirliliği çoğaltır.
4. **Kazıyıcı kalıbı** — [`base_osfb_scraper`](../src/company_master/etl/scrapers/base_osfb_scraper.py) WordPress OSB siteleri için çalışıyor. 25 sitenin hepsi WordPress değil; kalıp genelleştirilmeden tek tek kazıyıcı yazmak 25 kez aynı hatayı yapmak olur.

## İtiraz / risk

- **Ölçek:** ATO üye dizini tek başına mevcut 14003 satırı geçebilir. Kontör/görünürlük katmanı ve tekilleştirme bu hacimde test edilmedi.
- **Çakışma:** Aynı firma hem ASO hem ATO hem OSB üyesi olabilir. Tekilleştirme anahtarı ünvan değil **vergi no** olmalı — ama şu an sadece 774 kayıtta vergi no var (%5.5). Genişleme öncesi vergi no kapsama oranı yükseltilmeli, yoksa aynı firma 5 kez girer.
- **Hukuk:** Oda üye dizinleri KVKK açısından OSB dizinlerinden farklı olabilir; robots.txt ve kullanım şartları kaynak başına ayrı ölçülecek.

## Karar bekleyen sorular (ürün sahibi)

1. Sıra: OSB'ler önce mi, ATO önce mi? (ATO hacim olarak en büyük, en riskli)
2. Teknokent/TTO/kuluçka verisi `companies`'e mi girecek, ayrı `ventures` tablosuna mı?
3. Vergi no kapsamı %5.5 — genişleme öncesi bu yükseltilsin mi, yoksa ünvan tekilleştirmesiyle devam mı?

## İlgili Nodlar

- [[AGENTS]]
- [[plans/brief_utku_VERI-HAYALET-TEMIZ-01]]
- [[plans/brief_utku_VERI-IVEDIK-YENIDEN-01]]
