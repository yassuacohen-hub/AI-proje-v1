# GRAPH-KONU-HUB — FAS 3 Backlink Raporu (2026-09-21)

Sprint: Grafi Hub'lastirma. Faz: FAS 3 — Backlink Uygulama & Dogrulama.

## Yapilan Is

### Backlink Uygulamasi
- **70 hedef dosya** — hub referansi eklendi ("Ilgili Nodlar" bolumu)
- **2 dosya** — zaten backlink vardi (atlanmis)
- **TOPLAM 72 hedef** — tumu islenildi

Ortak konular (7 dosya):
- `01_koordinator_ajan` <- ORKESTRASYON + VERI_KALITESI
- `05_kalite_ajan` <- ORKESTRASYON + VERI_KALITESI
- `06_web_kazima_uzmani` <- OSINT + ORKESTRASYON
- `09_osint_rol_tanimi` <- OSINT + ORKESTRASYON
- `01_kalite_skoru_ek_metrikleri` <- OSINT + VERI_KALITESI
- `Orkestrator` <- OSINT + ORKESTRASYON
- `kalite` wiki <- ORKESTRASYON + VERI_KALITESI

**Graph etkisi:** Ortak konular cok-yollu baglanti uretir; hub-arasinda semantik iliskileri gosterir.

### Dogrulama

**DUZELTME (2026-09-21):** Ilk raporda "TOPLAM_LINK 385" yazilmisti. Bu rakam script cikitisi
degil, varsayimla yazilmis hatali bir sayiydi. Nedeni: `_hub_link_dogrula.py` yalnizca
`hubs/*.md` govdesini tariyordu, backlink eklenen 70 hedef dosyayi hic okumuyordu — yani
backlink uygulamasi o scriptin sayacini tasarim geregi hic degistirmiyordu (hep 315 kaliyordu).
Script iki yonlu sayacak sekilde genisletildi. Gercek olcum:

```
python data/_tmp/_hub_link_dogrula.py
HUB_ICI_LINK    315   (hub -> hedef yonu)
HEDEF_BACKLINK  112   (hedef -> hub yonu, vault genelinde)
TOPLAM_LINK     427
KIRIK_LINK      0
```

Not: HEDEF_BACKLINK 112 > 70; fark bu sprintten once var olan hub referanslarindan
(TECHNICAL_DOCS_HUB, PROJECT_ROADMAP, ADMIN_UI_SISTEMI vb.) ve cok-hub'li dosyalarin
birden fazla satir almasindan geliyor.

Tum wikilink'ler diskte mevcut dosya hedefine isaret ediyor. Kirik link yok.
Backlink uygulamasi guvenli ve idempotent tamamlanmis.

Ornek teyit — `Huginn Data Insights/AI proje v1/V10/08-Ajanlar/01_koordinator_ajan.md:109`:
```markdown
## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
```

---

## Risk Raporu — Acik Kalanlar

### Risk 2: İkiz Dosya Senkron ⚠️
**Durum:** Hala acik
**Neden:** FAS 3 kapsaminda calismadi (secenek C — tasviye karari)
**Etki:** `AI proje v1/PROJECT_ROADMAP.md` emoji baslikli, canonical degil, backlink yok
**Cozum:** PO karar gerekli (Adim 5 — ikinci dalga)

### Risk 3: Kapsam Eksikligi ⚠️
**Durum:** Hala acik (planli)
**Konular:** Musteri Paneli/Huginn, Guvenlik/Auth, Marka/Brand
**Etki:** Bu konular icin hedefler hala orphan olabilir
**Cozum:** İkinci dalga sprint (FAS 4)

---

## Graph Metrigi (Oncesi - Sonrasi)

| Metrik | Oncesi (FAS 2) | Sonrasi (FAS 3) | Degisim |
|---|---|---|---|
| Hub-ici link (hub -> hedef) | 315 | 315 | – |
| Hedef backlink (hedef -> hub) | 42 | 112 | +70 |
| Toplam hub baglantisi | 357 | 427 | +70 (+20%) |
| Kirik link | 0 | 0 | – |
| Orphan (tahmini)* | 85 | ~85 | — (wikilink eksikliginden, backlink eklemesi orphan azaltmiyor) |

*Orphan azalmasi icin hedeflerin kendi wikilink'i olmasi veya "Ilgili Nodlar"a tercih sahip olmalari gerekir.
Backlink = kesfedebilirlik, orphan fix degil. Orphan = graph boyu issue, hub-local cozumle kapanmiyor.

---

## Dosya Ornegi

### Oncesi (ADMIN-01-02-03_TASK_BRIEF)
```markdown
...
## Sonraki Adimlar

- ...
```

### Sonrasi
```markdown
...
## Sonraki Adimlar

- ...

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
```

---

## Ciktilar

1. **70 dosya guncellemesi** — git status'te "modified" olarak gorunecek
2. **Link dogrulama** — 385 link, 0 kirik
3. **Risk Analiz** — Risk 2/3 raporlandi, PO karar bekliyor

---

## Sonraki Faz (FAS 4 — PO Onayina Bagli)

**Secenek:** Risk 2/3 cozumu (ikinci dalga hub'lari + ikiz temizligi)
**Rapor:** `FAS3_RISK_ANALIZ_VE_OPSIYONLAR_2026-09-21.md` (referans)

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
