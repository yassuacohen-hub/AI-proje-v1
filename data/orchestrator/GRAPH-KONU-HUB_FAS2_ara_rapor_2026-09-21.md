# GRAPH-KONU-HUB — FAS 2 Ara Rapor (2026-09-21)

Sprint: Grafi Hub'lastirma. Faz: FAS 2 — Konu-Bazli Hub Genisletme.
PO karari: "admin dashbord konusunda bir hub olusturuyoruz tum bilgileri ayni hub uzerinde topluyoruz".

## Yapilan Is

| Cikti | Durum | Bagli dokuman |
|---|---|---|
| `hubs/ADMIN_DASHBOARD_HUB.md` | Yeni | 17 |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | Yeni | 18 |
| `hubs/ORKESTRASYON_AJANLAR_HUB.md` | Yeni | 22 |
| `hubs/VERI_KALITESI_HUB.md` | Yeni | 16 |
| `hubs/TECHNICAL_DOCS_HUB.md` | Guncellendi — "Konu Hub'lari" bolumu | +4 |
| `PROJECT_ROADMAP.md` | Guncellendi — "Konu Hub'lari" bolumu | +5 |
| `docs/ADMIN_UI_SISTEMI.md` | Guncellendi — "Ilgili Nodlar" backlink | +3 |

Toplam yeni konu hub: **4**. Kapsanan dokuman: **73** (tekrarlar dahil).

## Mimari Karar — Iki Duzlemli Hub

Mevcut 5 hub **kategori-bazli** (Technical/OSINT/Plan/Tools/Reports) — dosyanin *nerede oldugunu* yansitir.
Yeni 4 hub **konu-bazli** — dosyanin *ne hakkinda oldugunu* yansitir.
Ikisi cakismaz; ayni dosya her iki duzlemden de erisilebilir. Bu, graph'ta cok-yollu baglanti uretir
ve orphan riskini dusurur.

Hub'a yurutme raporlari (`ADMIN-*_rapor*`, `ORKESTRA-*_rapor*`, `TEST-*_rapor*`) **alinmadi** —
gurultu onleme. Bu raporlar `REPORTS_ANALYSIS_HUB` + `rapor_index` kapsaminda kalir.

## Dogrulama

```
python data/_tmp/_hub_link_dogrula.py
TOPLAM_LINK 315
KIRIK_LINK 0
```

Tum hub klasoru wikilink'leri diskte mevcut dosyaya isaret ediyor. Kirik link yok.

```
python data/_tmp/_emoji_baslik_tara.py
TOPLAM_MD 398   (onceki 393, +5 yeni hub/script)
EMOJI_BASLIKLI_SATIR 53
EMOJI_ICEREN_DOSYA 37
```

Yeni uretilen 4 hub'da emoji baslik yok (PO kurali korundu). Sayidaki +1 dosya farki
yeni dosyalardan degil, taramaya giren onceden var olan bir dosyadan geliyor.

## Riskler / Acik Kalanlar

1. **Tek yonlu bag.** Hub'dan hedefe link var; hedeften hub'a backlink yalnizca `ADMIN_UI_SISTEMI.md`'de.
   Kalan 72 hedef dosyaya "Ilgili Nodlar" bolumu eklenmesi FAS 3 isi.
2. **Kapsam disi konular.** Musteri Paneli/Huginn, Guvenlik/Auth, Marka/Brand icin konu hub yok.
   Ikinci dalga gerekebilir.
3. **Ikiz dosyalar.** `AI proje v1/PROJECT_ROADMAP.md` hala emoji baslikli ve canonical degil.
   Canonical `Huginn Data Insights/PROJECT_ROADMAP.md` guncellendi; ikiz senkron disi.

## Sonraki Adim

FAS 3 — Backlink Uygulama: 73 hedef dosyaya toplu "Ilgili Nodlar" bolumu ekle (script ile),
ardindan Obsidian graph'ta final orphan olcumu.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
- [[Huginn Data Insights/PROJECT_ROADMAP]]
