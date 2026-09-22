# ADMIN-UX-LOGOUT-01 — Teslim Raporu

- **Tarih:** 2026-09-18
- **Öncelik:** P0
- **Durum:** review (onay bekliyor)
- **Başlık:** Çıkış/oturum senkronizasyonu — logout anında UI yenilenmeli

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]


- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

## 1. Sorun (sade dil)

Sağ üstteki hesap kartından "Çıkış" düğmesine basınca **oturum kapanmıyordu**.
Düğmeye basınca ekranda ikinci bir "Çıkış" düğmesi beliriyordu. Kullanıcı hâlâ içerideydi.

## 2. Kök neden

`app.py` içindeki hesap kartı, yanlış fonksiyonu çağırıyordu.

| Çağrılan | Ne yapar |
|---|---|
| `render_admin_cikis()` (yanlış) | Ekrana **düğme çizer**. Oturumu kapatmaz. |
| `admin_cikis()` (doğru) | Oturumu **gerçekten kapatır** ve mesajı gösterir. |

Tek satırlık yanlış çağrı. Etkisi: çıkış özelliği **%100 çalışmıyordu**.

## 3. Yapılan düzeltme

- `app.py` → hesap kartı artık `admin_cikis()` çağırıyor. Değişen satır sayısı: **3**.
- Yeni koruma testi eklendi: `tests/test_nav_ia04.py::test_popover_cikis_gercekten_oturum_kapatir`.
  Bu test, aynı hatanın ileride tekrar yazılmasını engeller.

## 4. Yol üstünde bulunan ek temizlik

Bu görevden kaynaklanmayan, ama süiti kırık tutan 2 sorun kapatıldı:

| Bulgu | Durum |
|---|---|
| `tests/test_sekme_kapsama.py` içinde artık var olmayan bir fonksiyona ait ölü kayıt | Silindi 🟢 |
| 3 dosyada eksik satır sonu / bozuk bayt (kodlama denetimi ihlali) | Temizlendi 🟢 |

## 5. Doğrulama (tekrarlanabilir)

```
python scripts/kodlama_denetim.py
  -> temiz: kodlama ihlali yok

python -m pytest -q --no-header -p no:cacheprovider
  -> 3905 passed, 4 skipped, 127 warnings in 78.87s

python scripts/streamlit_restart.py
  -> BASLADI: PID 7932 -> http://127.0.0.1:8501 (saglik ok)
```

### Test tablosu

| Ölçüm | Önce | Sonra | Değişim |
|---|---|---|---|
| Başarısız test | 4 | **0** | **%100 düzeldi** 🟢 |
| Geçen test | 3899 | **3905** | +6 (+%0,15) |
| Atlanan | 4 | 4 | — |
| Kodlama ihlali | 3 | **0** | **%100 temiz** 🟢 |

## 6. Bilinen durumlar

| Konu | Açıklama | Aksiyon |
|---|---|---|
| 127 uyarı | Eskiden beri var. 126 tanesi Python'un eski tarih fonksiyonu uyarısı, 1 tanesi ayar kütüphanesi uyarısı. | Bu görevin kapsamı dışı. Ayrı temizlik görevi açılabilir. |
| Manuel UI testi | Panel yeniden başlatıldı, sağlık kontrolü geçti. Tarayıcıdan gözle çıkış denemesi KAHİN'e bırakıldı. | Onay sırasında bakılabilir. |

## 7. Değişen dosyalar

| Dosya | Neden |
|---|---|
| `app.py` | Kök neden düzeltmesi |
| `tests/test_nav_ia04.py` | Yeni koruma testi |
| `tests/test_sekme_kapsama.py` | Ölü kayıt silindi |
| `tests/test_admin_errors.py` | Kodlama temizliği |
| `src/company_master/logging/error_logger.py` | Satır sonu düzeltmesi |
| `web_dashboard/tabs/admin_errors.py` | Satır sonu düzeltmesi |
| `data/orchestrator/task_board.json` | Pano güncellemesi |

## 8. Özet

🟢 Çıkış düğmesi çalışıyor.
🟢 Süit tamamen yeşil (3905/3905).
🟢 Kodlama denetimi temiz.
🔵 2 ek hijyen sorunu bedavaya kapandı.
