# MVP-ADMIN — Admin Panelin Minimum Canlı Sürümü

**Tarih:** 2026-09-15 · **Karar:** Ürün Sahibi ("hedefi küçült, 1 günde çalışır çıktı") · **Orkestratör:** roo

## Kapsam (yalnız 4 ekran)

| # | Ekran | Anahtar | Durum | Görev |
|---|---|---|---|---|
| 1 | Sistem Ana Kontrolü | `ana_kontrol` | ✅ hazır | — (kabul testi) |
| 2 | KPI Görünümü | `kpi` | ✅ hazır | — (kabul testi) |
| 3 | Karar Defteri | `karar_defteri` | ⚠️ ham liste | **MVP-KD-01** |
| 4 | Kullanıcı Ayarları / Yönetimi | `kullanicilar` | ⚠️ salt liste | **MVP-KUL-01** |

Bu 4 ekran "tamamlandı" olmadan başka UI işi açılmaz. Sidebar/topbar süslemeleri (UI-SIDEBAR-02, UI-TOPBAR-02) **ertelendi**.

## Rol dağılımı

- **Üretim:** kilo (tek ajan, iki küçük teslim)
- **Kontrol:** cline (review; kapsam dışı bulguyu düzeltmez, not düşer)
- **Koordinasyon:** roo yalnız onay/ret; plan üretmez

## MVP-KD-01 — Karar Defteri (kilo)

Dosya: `web_dashboard/tabs/admin_panel.py` (`render_decision_tab`), `tests/test_admin_panel.py` (varsa; yoksa `tests/test_karar_defteri.py`)

Yapılacak:
1. `PageHeader("Karar Defteri", ust_etiket="İş · Yönetim", ikon="📒")` + kısa giriş (diğer ekranlardaki kalıp).
2. Filtre satırı: `Karar Veren` (selectbox, "Hepsi" + benzersiz `decider`), `Etiket` (multiselect), `Ara` (title/decision/reason içinde metin).
3. Liste: son 50 kayıt, en yeni üstte; `st.dataframe` (mevcut sütunlar).
4. "➕ Yeni karar" `st.form`: başlık, karar, gerekçe, etiketler (virgül) → `scripts/decision_log.log_decision(...)` (decider = aktif admin e-postası; yoksa "admin"). Kaydedince `st.success` + rerun.
5. Boş durumda `st.info("Henüz karar kaydı yok")` korunur.

**Tamamlandığında ne görünecek:** `/karar_defteri` açılır; üstte başlık + giriş, altında 3 filtre, tablo en yeni kayıtla başlar; "Yeni karar" formu doldurulup kaydedilince kayıt tablonun ilk satırında görünür ve `data/orchestrator/decision_log.jsonl` son satırına eklenmiş olur.

## MVP-KUL-01 — Kullanıcı Yönetimi (kilo)

Dosya: `web_dashboard/tabs/admin_extras.py` (`render_user_management`), `tests/test_admin_extras.py` (yoksa oluştur)

Yapılacak:
1. `st.subheader` kaldır → `PageHeader("Kullanıcı Yönetimi", ust_etiket="İş · Yönetim", ikon="👥")`.
2. **Onay bekleyenler** tablosu: her satır için `Onayla` butonu → `POST /api/admin/approve {user_id}` (`post_api` yardımcısı varsa kullan; yoksa `api_client`'a ekle). Başarıda `st.success` + `st.cache_data.clear()` + rerun; hatada `st.error(mesaj)`.
3. **Son onaylılar** tablosu (mevcut).
4. **Kredi tanımla** küçük form: user_id + miktar → `POST /api/admin/credit`.
5. Token yoksa `st.warning("Lütfen giriş yapın")` korunur (fail-closed).

**Tamamlandığında ne görünecek:** `/kullanicilar` açılır; "Onay Bekleyen" tablosunda bir kullanıcının yanındaki **Onayla** basılınca satır "Son Onaylı" tablosuna geçer; kredi formu gönderilince başarı mesajı görünür. Testler sahte API ile 3 senaryoyu (onay başarı, onay hata, token yok) kapsar.

## Kabul kapısı (cline → roo)

- `python -m pytest tests/ -q --continue-on-collection-errors` yeşil, koleksiyon hatası 0
- `python scripts/kodlama_denetim.py` temiz
- `tests/test_sayfa_iskeleti.py` PageHeader/Section kuralları geçer (MUAF listesine ekleme yapılmaz)
- Ekran görüntüsü yerine: cline her ekranı `streamlit run app.py` ile açıp "tamamlandığında ne görünecek" cümlesini birebir doğrular

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
