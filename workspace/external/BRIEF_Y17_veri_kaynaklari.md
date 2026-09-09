# Y17 — YENI VERI KAYNAK ARASTIRMASI (sahip: arastirmaci)

## Gorev
Mevcut 6 kaynagin (OSTIM / Ivedik / Baskent / ASO / web / MERSIS) disinda **hukuki ve teknik olarak erisilebilir** yeni firma/istihbarat kaynaklari tespit et. Cikti: kaynak + erisim yontemi + maliyet/KVKK analiz tablosu.

## Aday list (baslangic, genisletilebilir)
| Kaynak | Icerik | On kontrol |
|---|---|---|
| TOBB e-sicil / sanayi sicil | tescil, faaliyet dalı | erisim yontemi? |
| Ihale duyurulari (EKAP, KIK) | tedarikci + sektor + hacim | acik API var mi? |
| KOSGEB / sanayi destek programlari | arge/supported firmalar | listeler acik mi? |
| Il Ozel Idare / OIZ duyurulari | parsel/kullanim | yayin formati? |
| Iskur is ilanlari | isguc sinyali (Y15 ailesiyle bagli) | API/scraper yontemi |
| e-Ihracat / ticaret bakanligi raporlari | ihracatci firmalar | rapor gunceligi |

## KVKK ve hukuki cerceve
- `AI proje v1/V10/09_kurallar_ve_promptlar/03_kvkk_ve_veri_politikasi.md` kurallarina uymayan kaynak ekleme
- Acik kaynak / resmi yayin tercihi; scrape edilenler icin robots.txt notu

## Cikti
`workspace/external/<ajan>/output/Y17_veri_kaynaklari.md` — analiz tablosu (kaynak | veri | erisim | guven | maliyet | KVKK notu) + ilk 3 tavsiye.
