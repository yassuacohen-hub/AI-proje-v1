# ALTYAPI-MIMIR-HABER-KUSU-01 — Haber Kuşu Kaynak Haritası

- **Ajan:** utku
- **Tarih:** 2026-10-03
- **Durum:** `review` (onay bekliyor)
- **Kilitli dosyalar:** `src/company_master/odin_ai/arac_dongusu.py`, `tests/test_arac_dongusu_kaynak.py`
- **Brief:** `plans/brief_utku_ALTYAPI-MIMIR-HABER-KUSU-01.md`
- **Ölçüm kanıtı:** `docs/HABER_KUSU_KAYNAK_OLCUMU.md`

## 1. Sonuç (tek cümle)

Haber kuşu kaynak haritası 3 adresten **7 gerçek- içerik dönen adrese** çıkarıldı, `PAKET_KAYNAKLARI` ile bağlantı `KAYNAK_PAKET_ADI` köprüsüyle kuruldu, 42 test yeşil.

## 2. Ne yapıldı

| Adım | Yapılan | Kanıt |
|---|---|---|
| Ölçüm | 38 aday adres, 3 tur (HTTP durumu + gövde içeriği) | `docs/HABER_KUSU_KAYNAK_OLCUMU.md` |
| Harita | `KAYNAK_HARITASI` 3 → 7 | `arac_dongusu.py` |
| Köprü | `KAYNAK_PAKET_ADI` (etiket → paket kodu), `__all__` ile dışa açıldı | `tests/test_arac_dongusu_kaynak.py` |
| Test | 4 yeni test + 38 mevcut | 42 passed in 1.47s |
| Hub | B-14 kapanış kaydı | `hubs/TOOLS_SCRIPTS_HUB.md:131` |

**Kabul edilen 7 adres:** dmo 2 · Resmî Gazete 2 · TÜRKPATENT 1 · Eleman.net 1 · Google News RSS 1

## 3. Reddedilen adresler (gerçek içerik dönmedi)

| Aday | Sonuç | Gerekçe |
|---|---|---|
| LinkedIn | Elendi | Giriş duvarı / bot koruması |
| Instagram | Elendi | JS kabuğu, HTML'de veri yok |
| Facebook | Elendi | HTTP 400 |
| TÜRKPATENT `/Tarama/`, `/Basvuru/` | Elendi | Sahte HTTP 200, gövde `Hata 404` |
| KAP / TOBB / SPK | Eklendi ama **haritada yok** | 200 dönüyor ama `PAKET_KAYNAKLARI`'nda karşılığı yok → **uydurulmadı**, chat'e yazıldı |
| EKAP / Apify | Dokunulmadı | Görev kapsamı dışı |

## 4. Varsayım kırılması (D-217)

**Varsayım:** `KAYNAK_HARITASI` anahtarları `PAKET_KAYNAKLARI` kaynak adlarıyla eşleşir.

**Gerçek:** 3 harita anahtarı Türkçe etiket; `paketler.PAKET_KAYNAKLARI` 8 kısa kod (`dmo`, `rg`, `google_news`, `linkedin`, `patent`, `instagram`, `facebook`, `is_ilani`). Kesişim = **0**.

**Çözüm:** İkinci kaynak listesi açmak D-211 ikiz yapı yasağı. Bunun yerine `arac_dongusu.py` içine `KAYNAK_PAKET_ADI` köprü noktası eklendi; testler bu köprünün boş olmadığını ve harita anahtarlarıyla tutarlı olduğunu doğruluyor. Alternatif (KAP/TOBB'yi `PAKET_KAYNAKLARI`'na eklemek) KAHİN kararı gerektirdiği için uygulanmadı, `ihsan` ajanına chat kaydı açıldı.

## 5. Çalışmayan / sınırlı olan

- **Ölçüm tek seferlik:** 38 adres canlı HTTP ile ölçüldü, kayıt `docs/HABER_KUSU_KAYNAK_OLCUMU.md` içinde. Otomatik yeniden ölçüm (CI/smoke) yok; adresler zamanla bozulabilir.
- **Köprü runtime'a tam bağlı değil:** `KAYNAK_PAKET_ADI` doğrulama ve test düzeyinde. Haber kuşunun üretim akışında paket koduna göre adres seçimi yapan bir tüketici yok; harita tek noktadan (`getir_izni` → `KAYNAK_HARITASI`) besleniyor. Brief'in "her anahtar bir paket kaynağı olmalı" kabulü bu nedenle **yapısal olarak sağlanmıyor**, yalnızca köprü ile belgeleniyor.
- **Paket dışı kaynaklar:** KAP/TOBB/SPK 200 dönse de haritaya alınmadı; bu, kapsam kaybıdır, karar KAHİN'e bırakıldı.

## 6. Test

```
python -m pytest tests/test_arac_dongusu_kaynak.py tests/test_arac_dongusu.py -q
42 passed in 1.47s
```

## 7. Öz-eleştiri

| Yapmadığım / eksik bıraktığım | Neden |
|---|---|
| KAP/TOBB/SPK'yi haritaya eklemedim | `PAKET_KAYNAKLARI`'nda karşılıkları yok; uydurma kaynak yazmak D-256 mantığına aykırı. KAHİN kararına bağladım. |
| Köprüyü üretim akışına bağlamadım | Kilitli dosya kapsamı dışında; ayrı görev gerekir. |
| Adres sağlığı için smoke test yazmadım | Brief kapsamı dışı. |
| Ölçümü 3 turda yaptım ama tekrar edilebilir script bırakmadım | Betikler `KAP` kapısına takılır; kanıt dokümana yazıldı. |

## 8. Öneri (KAHİN kararı)

`PAKET_KAYNAZLARI` ile haber haritası arasındaki etiket/kod uyumsuzluğu kalıcı. Öneri: `KAYNAK_PAKET_ADI` köprüsü SSOT olsun, `PAKET_KAYNAZLARI` yalnızca izin listesi olarak kalsın — böylece ikinci kaynak listesi açılmaz.