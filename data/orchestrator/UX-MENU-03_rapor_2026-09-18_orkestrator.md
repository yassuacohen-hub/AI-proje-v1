# UX-MENU-03 — Menü ağacı sadeleştirme + Dashboard Overview yeniden düzeni

**Tarih:** 2026-09-18 · **Commit:** `a19151a` · **Dal:** `chore/monorepo-merge`

---

## 1. Ne yapıldı (özet tablo)

| # | İş | Durum | Ölçü |
|---|----|-------|------|
| 1 | Menü ağacı sadeleştirme (E1-E5) | 🟢 tamam | 24 → 16 alt sekme (**%33 azalma**) |
| 2 | 3 seviye derinlik kuralı | 🟢 tamam | Maks grup 5 sekme |
| 3 | Overview aksiyon şeridi | 🟢 tamam | 5 buton, hepsi gerçek iş |
| 4 | Overview giriş kartları | 🟢 tamam | 4 kart, canlı URL |
| 5 | Wireframe §8 belgelendirme | 🟢 tamam | §8.1-§8.5 |
| 6 | Testler | 🟢 tamam | +15 yeni test |

---

## 2. Menü değişimi (gerçek kod sayımı)

| Ölçüt | Önce | Sonra | Fark |
|-------|------|-------|------|
| Üst sayfa | 6 | 6 | — |
| Alt sekme (menüde) | 24 | 16 | **−8 (%33)** |
| Menüsüz sayfa | 0 | 8 | +8 |
| En kalabalık grup | 8 | 5 | **−3 (%38)** |

Yeni ağaç:

| Üst sayfa | Alt sekme sayısı | Sekmeler |
|-----------|-----------------|----------|
| Sistem | 5 | teknik_altyapi · api · hatalar · maliyet · canli_veri |
| Müşteri Yönetimi | 4 | musteriler · kullanicilar · destek · export |
| Proje Yönetimi | 3 | karar_defteri · abrakadabra · denetim |
| Veri & Kalite | 2 | kpi · kalite |
| Müşteri Önizleme | 2 | paketler · pazarlama |

🔵 **Önemli:** Menüden çıkan 8 sayfa **silinmedi**. Sayfa ve adresleri çalışmaya devam ediyor, sadece sol menüde görünmüyor. Eski bağlantılar kırılmadı.

Menüden çıkanlar: executive · arama · performans · webhook · dlq · yenileme · ayarlar · yukleme

---

## 3. Dashboard Overview — 5 aksiyon butonu

| Buton | Rengi | Ne yapar | Sonucu nerede görünür |
|-------|-------|----------|----------------------|
| ⟳ Veriyi Yenile | ana renk (dolu) | Önbelleği temizler, kartları yeniler | Sayfa anında yenilenir |
| ⬇ Veri Güncelle | mavi | Veri çekme hattını çalıştırır (maks 180 sn) | Yeşil/kırmızı kutu + saat |
| ♥ Sağlık Kontrolü | yeşil | API + webhook ayakta mı sorar | 🟢/🔴 rozetli satır |
| ⬆ Dışa Aktar (CSV) | turuncu | Firma listesini CSV'ye çevirir | Satır sayısı + dosya boyutu + indirme düğmesi |
| ✓ Bekleyen Onaylar | kırmızı | Onay bekleyen kullanıcı sayısı | Buton üstünde sayı rozeti |

Kalite çıtası karşılandı:
- 🟢 Her butonda yükleniyor çarkı (spinner)
- 🟢 Sonuç ekranda kalıcı (sayfa yenilense de kaybolmuyor) — saat damgalı
- 🟢 İkon + etiket tutarlı, eşit genişlik
- 🟢 Süs buton yok — 5/5 buton gerçek iş tetikliyor (**%100**)

🔵 Renkler tek kaynaktan (`tokens.py`) geliyor. Bir test bunu kilitliyor: kimse gelişigüzel renk yazamaz.

---

## 4. Giriş kartları (4 adet)

👥 Firmalar · 🧑 Kullanıcılar · ⚠️ Olaylar & Hatalar · 📊 Metrikler

Kartlar sekme kayıt tablosundan adres okuyor. Sekme taşınırsa bağlantı kendiliğinden düzelir — elle bakım yok.

---

## 5. Test sonuçları

| Ölçüt | Değer |
|-------|-------|
| Yeni test | 15 (7 menü + 8 Overview) |
| Tam süit | **3889 geçti · 5 atlandı · 0 hata** |
| Süre | 84 sn |
| Kodlama denetimi | 🟢 temiz |

🟡 **Bilinen istisna:** `tests/test_mcp_transport.py` koşumdan hariç tutuldu.
**Neden:** `mcp` Python paketi ortamda kurulu değil (`ModuleNotFoundError: mcp.server.mcpserver`).
**Bu değişiklikle ilgisi yok** — paket eksikliği önceden vardı. KAHİN kararı: paket sonra kurulacak, takip listesinde.

---

## 6. Dokunulan dosyalar

| Dosya | Ne oldu |
|-------|---------|
| `web_dashboard/tabs/__init__.py` | 8 sekme menüden çıkarıldı |
| `web_dashboard/tabs/ana_kontrol.py` | Aksiyon şeridi + giriş kartları |
| `tests/test_tabs_ia.py` | yeni — menü yapısı kilidi |
| `tests/test_ana_kontrol_overview.py` | yeni — buton davranışı kilidi |
| `tests/test_dashboard_nav.py` | 2 test yeni ağaca hizalandı |
| `tests/test_sayfa_iskeleti.py` | `admin_error_handling` muafiyeti (ekran değil, yardımcı modül) |
| `scripts/onayla_ve_sirala.py` | satır sonu boşlukları temizlendi |
| `docs/UX_MENU_AGACI_WIREFRAME_2026-09-18.md` | §8.1-§8.5 |

---

## 7. Sonraki faz (ertelenen)

🟡 Streamlit'in gezinme API'si 2 seviyeden fazlasını desteklemiyor. 3. seviye gereken maddeler sekme içi bölüm olarak çözülecek — ayrıntı wireframe §8.5.

🔵 Servis durumu: Streamlit yeniden başlatıldı (PID 14652, port 8501, sağlık onaylı).
