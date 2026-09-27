# Brief: UI-MENUTREE-02 — Sol Menu Ağacı Düzelt

**Görev ID:** UI-MENUTREE-02  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P1  
**Tahmini Süre:** 4s  
**Dosya:** `web_dashboard/tabs/__init__.py` (682 satır)

---

## DURUM
UI-AYARLAR-SAYFA-02 ✅ tamamlandı ve onaylandı (review → done).  
Bu görev zincirin **ikinci halkası**. Başlama koşulu: **aktif**.

---

## AMAÇ
**`web_dashboard/tabs/__init__.py`** içindeki `SECTIONS` demeti ve navigasyon kaydı **eksik/tutarsız yapıları düzelt**, sol menü ağacında kolay gezinti sağla.

---

## BRİF MADDELERİ

### 1. SECTIONS Tutarlılığı
- `SECTIONS` tuple'ında her `TabTanimi` öğesinin `anahtar`, `baslik`, `url_path`, `min_rol`, `ikonu` alanları tam ve tekrarsız olmalı
- Sidebar navigasyonunun bu SSOT'tan otomatik türetildiğini doğrula (lazy import + `gorunur_bolumler(rol)`)

### 2. Rol Filtresi Doğruluğu (U-10)
- `ROLE_HIERARCHY` ile `min_rol` değerleri **tutarlı** olmalı
- Test: `test_dashboard_nav` geçerse, rol seviyeleri doğru

### 3. URL Bağlantıları
- Tüm `url_path` değerleri regex `^/[a-z_-]+/?$` ile eşleşmeli
- Tekrarlayan path yok
- Sidebar butonları + derin bağlantılar (`?url=...`) doğru çalışmalı

### 4. İkon Tutarlılığı
- Sidebar'daki her sekme ikonu `SECTIONS.ikonu` ile eşleşmeli
- Stale/yanlış emoji yok
- Darkmode'da ikon okunabilirliği check edilmeli (test yaparsanız `test_icons_dark_mode` yazın)

### 5. Tembel (Lazy) Import Doğruluğu
- Her sekme modülü yalnızca `st.write(secim_sayfasi())` çağrısında import edilmeli
- `app.py` başlangıçta tüm modülleri import **etmemeli**
- Measure: ilk sayfa yükleme süresi < 3s

---

## DOSYALAR
- Düzenle: `web_dashboard/tabs/__init__.py`
- Test dosyaları (varsa): `tests/test_dashboard_nav.py`, `tests/test_icons_*.py`
- Side effect: `app.py` —`render_sidebar()` ve `_sayfa_cizici()` bu kaydı kullanır (okuma-only, düzenleme yok)

---

## TEST
```bash
# Yapısal test:
python -X utf8 -m pytest tests/test_dashboard_nav.py -v

# Rol filtresi:
python -X utf8 -m pytest tests/test_*.py -k "role" -v

# Kodlama:
python scripts/kodlama_denetim.py --dosyalar web_dashboard/tabs/__init__.py

# UI gözlemli check (varsa):
# - Streamlit uygulamasını çalıştır, sidebar'da tüm sekmeler görünsün
# - Rol düşürüp tekrar giriş yap → min_rol filtresi uygulandı mı?
```

---

## TESLIM KONTROL LİSTESİ (EXCELLİ)
- [ ] `SECTIONS` tutarlılığı doğrulandı (tutarsızlık varsa fix edildi)
- [ ] `ROLE_HIERARCHY` vs `min_rol` uyum kontrolü yapıldı
- [ ] URL path regex `^/[a-z_-]+/?$` ve tekrar check edildi
- [ ] İkon tutarlılığı (sidebar + SECTIONS eşleştirmesi)
- [ ] Tembel import doğruluğu (app.py başlangıcında import modülü sayısı azaldı veya aynı kaldı)
- [ ] Test geçti: `pytest tests/test_dashboard_nav.py -v` ✅
- [ ] Kodlama denetimi: `kodlama_denetim.py --tam-repo` temiz ✅
- [ ] Dosya UTF-8, BOM yok
- [ ] Teslim özeti: değişen satır numaraları, test sayısı, eksik varsa yazıldı

---

## KAYNAKLAR
- **Tasarım:** `web_dashboard/tabs/__init__.py` başındaki docstring (lazi import, SSOT, rol filtresi)
- **Rol seviyeleri:** `src/company_master/auth/rbac.py` → `ROLE_HIERARCHY`
- **Sidebar render:** `app.py:406-531` → `render_sidebar(secili: TabTanimi)`
- **Url param:** `app.py:174-191` → `_url_param_oku()` / `_url_param_yaz()`

---

## ZİNCİR
**Onceki:** UI-AYARLAR-SAYFA-02 (done ✅)  
**Şimdi:** UI-MENUTREE-02 (aktif)  
**Sonraki:** UI-PROFILMENU-POPOVER-02 (P2, utku) — native `st.popover` ekle

---

**Hazır mısın başlamaya?** Brif sorusu varsa, teslim yazmadan önce yaz.
