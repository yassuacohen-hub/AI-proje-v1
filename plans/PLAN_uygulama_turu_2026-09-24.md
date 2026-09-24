# Uygulama Turu Planı — 2026-09-24

**Durum:** `-13` KVKK şeması teslim edildi (`review`). Uygulama turuna hazır, iki görev sıralı.

---

## Görev 1: API-ADMIN-AKTIVITE-YAZ-14 (P0, 2s)

**Brief:** [`plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md`](Huginn Data Insights/plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md)

**Kapı:** `-13` migration `user_activity_log` tablosu + approval.

### İş Taşı

| # | Adım | Kapsam | Doğrulama |
|---|---|---|---|
| 1 | `aktivite_yaz()` yardımcı | `web_app.py` içinde: `aktivite_yaz(user_id, olay_tipi, detay=None, basarili=True)` | giriş noktası `:2232` + fallback `:2246` — satır numaraları brief ile eşleşiyor mu? |
| 2 | Giriş olay yazma | `olay_tipi='giris'` INSERT, aynı iki noktaya | CHECK: `giris`/`arama`/`ai_kullanim` değerleri kabul ediliyor |
| 3 | Arama olay yazma | Arama ucu: `olay_tipi='arama'`, `detay={'terim': ..., 'sonuc_adedi': N}`, `basarili = sonuc_adedi > 0` | tek merkezi uç var mı, yoksa dağınık mı? |
| 4 | AI/MIMIR olay yazma | `olay_tipi='ai_kullanim'` | INSERT fail → logla, ana akış **düşmez** (try/except) |
| 5 | Test | assert: başarılı yazma + DB hatası sessiz geçiş + tablo yok durumu | 3+ test geçiyor |
| 6 | Teslim | SSOT §7 (İzlenebilirlik) + §14 (Revizyon) satır ekleme, hub izi (B-14), `gorev_kutusu.py teslim` | KAHİN onayı |

### DUR Kapıları

- Brief `:13` "Doğrulanacak varsayım" — eğer kalkarsa DUR et.
- Log yazımı main akışı kesilirse **dur**, kapı ihlali.
- `-14-LASTLOGIN-YAZ-05` deseni yoksa **dur**, panoya sorun aç.

### Çıktı

- `aktivite_yaz()` imzası (bağımlı `-15`/`-20`/`-21` tüketecek).
- Giriş/arama/AI/MIMIR olayları tabloya yazılıyor.
- Test + SSOT + hub izi.

---

## Görev 2: UI-ADMIN-DAU-17 (P1, 2s)

**Brief:** [`plans/brief_utku_UI-ADMIN-DAU-17.md`](Huginn Data Insights/plans/brief_utku_UI-ADMIN-DAU-17.md)

**Kapı:** `-14` aktivite yazma + son 24 saat verileri.

### İş Taşı

| # | Adım | Kapsam | Doğrulama |
|---|---|---|---|
| 1 | DAU sorgusu | `load_admin_kpi_summary()` (`admin_kpi.py:41`): son 24h `user_activity_log` distinct `user_id` | satır numarası doğru mu? Başka KPI üretim noktası var mı? |
| 2 | DAU/MAU oranı | hesapla, MAU=0 kenar durumu (bölme) | null/boş, hata yok |
| 3 | Tablo yok durumu | `tablo_var_mi()` ile kontrol ([`_db_yardim.py`](Huginn Data Insights/web_dashboard/tabs/_db_yardim.py)), "veri kaynağı yok" rozeti, `0` değil | sahte KPI deseni ([`admin_kpi.py:102-115`](Huginn Data Insights/web_dashboard/tabs/admin_kpi.py:102-115), `:399-402`) |
| 4 | MAU değeri | **değiştirme**, varsa gerçek kalmaz | mevcut yazı adım 1 |
| 5 | Test | assert: normal durum + tablo yok + MAU=0 | 3+ test geçiyor |
| 6 | Teslim | SSOT §7 + §14 satır, hub izi (B-14), `gorev_kutusu.py teslim` | KAHİN onayı |

### DUR Kapıları

- `load_admin_kpi_summary()` fonksiyon adı değişmişse **dur**.
- `_db_yardim.tablo_var_mi()` yoksa **dur**, kendi kontrol uydurma.
- `-13` tablo yok durumunda DAU **0 yapılmaz**, "veri kaynağı yok" gösterilir.

### Çıktı

- DAU kartı + DAU/MAU oranı.
- Tablo yok durumunda uygun rozet.
- Test + SSOT + hub izi.

---

## Sıralama & Bağımlılıklar

```
-13 (migration şeması, review)
  ↓
-14 (API yazma) — giriş/arama/AI olay INSERT
  ↓
-15 (UI DAU) — son 24h distinct user sorgusunda veri var
```

**Blokaj:** `-14` bitmeden `-15` boş sonuç döner (tablo var ama veri yok). İş hala tamamlanabilir, sonrası.

---

## Yeni Görev Üretimi Yasağı (D-198)

Sonraki görevler (`-20`, `-21`) **planlama turunda açılır**, şu turda YAPILMAZ.

---

## Risk & Sorun Kapıları

| Risk | Olasılık | Hareket |
|---|---|---|
| Brief satır numaraları kayabilir (`:2232`, `:2246`) | Orta | `-14` başında "Doğrulanacak varsayım" adımı kontrol et |
| Arama/AI uçları dağınık (merkezi değil) | Orta | Brief `:15` "kapsamı KAHİN'e taşı" — panoya sorun aç |
| `_db_yardim.tablo_var_mi()` yoksa | Düşük | Dosya mevcut (VS Code'da açık), test et |
| `-13` approval gecikmesi | Düşük | `-14` brieffin hazır, kapı noktasında DUR et |

---

## Onay Sorgusu

✓ Planlama kabul ediliyor mi?
- [ ] Evet, `-14` brieffini `code` moduna delegeye et (karar: KAHİN onayı sonrası).
- [ ] Revizyon gerekli: [revizyon notu]

