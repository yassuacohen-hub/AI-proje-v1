# Brief: UI-PROFILMENU-POPOVER-02 — Native Streamlit Popover Ekle

**Görev ID:** UI-PROFILMENU-POPOVER-02  
**Sahip:** UTKU (Üretim/Hacim)  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Dosya:** `src/company_master/ui/components/profil_menu.py` (267 satır)

---

## DURUM
UI-MENUTREE-02 tamamlanacak (zincir bağlı). Başlama koşulu: **UI-MENUTREE-02 done olunca otomatik tetikle** (`gorev_zinciri`).

---

## AMAÇ
**`profil_menu.py`** içinde elle CSS/div ile yapılmış sahte popover'i **Streamlit 1.62+ native `st.popover`** ile değiştir. State mutasyonu, form, emoji gibi eski tasarım sorunları düzelt.

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. st.popover Migrasyonu
- Admin butonu (`harf` avatar) `st.popover` açıcı olsun
- Popover içinde: "Hesap Ayarları", "Şifre Değiştir", "Çıkış Yap" butonları
- Misafir: yalnız "Giriş Yap" butonu görünsün
- Buton metinleri: `rol.capitalize()` (Admin, Moderator vb.)

### 2. State Mutasyonu ÇIKART
- Eski: `st.session_state.get(f"{key}_acik", False)` — manual toggle
- Yeni: `st.popover` kendisi state yönetsin, `session_state` hiç dokunulmaz
- Sonuç: `profil_menu()` pure function olmalı, side-effect yok

### 3. Form / Deep-Link Düzeltme
- Popover içinde `st.form` OLMASIN
- "Hesap Ayarları" tıklaması → `st.switch_page(ayarlar_url)` ile /ayarlar'a git
- "Şifre Değiştir" tıklaması → `st.switch_page(ayarlar_url + "#sifre")`
- "Çıkış Yap" tıklaması → `admin_cikis()` (app.py'de tanımlı)

### 4. Avatar — Emoji Kaldır, Monokrom Tut
- Başharf (İ, U, S, Y vb.) türkçe destekli
- Arka plan: `token("color", "surface-3")`
- Metin: `token("color", "text")`
- **Emoji yok** (👤, 👨 kaldır)
- Dark mode test edilsin

### 5. Pozisyon ve Erişilebilirlik
- Popover sağ-üst oturmalı (z-index 1000+ muhtemelen Streamlit handle eder)
- ARIA label: "Profil menüsü" (a11y)
- Keyboard navigation: Tab + Enter ile açılıp kapanmalı

### 6. Test Dosyası Güncellemesi
- `tests/test_profil_menu.py` — 8 test mevcut, **hepsi yeşil kalmalı**
- Test adları: `test_profil_menu_dosyasi_var`, `test_profil_menu_ast_state_mutasyok_yok`, vb.
- Yeni test varsa: `st.popover` var mı diye kontrol (`AST` taraması)

---

## DOSYALAR
- Düzenle: `src/company_master/ui/components/profil_menu.py`
- Test dosyası (read-only): `tests/test_profil_menu.py`
- Side effect: `app.py` — `_topbar_menu_button()` bu modülü import eder (okuma-only, düzenleme yok)
- UI tokenlar: `src/company_master/ui/tokens.py` (`token("color", ...)` mekanizması)

---

## TEST
```bash
# Unit testler (8 test):
python -X utf8 -m pytest tests/test_profil_menu.py -v

# AST taraması (st.popover var mı?):
python -X utf8 -m pytest tests/test_profil_menu.py::test_profil_menu_ast_state_mutasyok_yok -v

# Kodlama denetimi:
python scripts/kodlama_denetim.py --dosyalar src/company_master/ui/components/profil_menu.py

# UI gözlemli check (varsa):
# - Streamlit uygulamasını çalıştır
# - Sağ-üst köşedeki avatar (baş harfi) bulabilir misin?
# - Tıkla → popover açılsın (Hesap Ayarları / Şifre Değiştir / Çıkış Yap görünsün)
# - Çıkış Yap tıkla → admin_cikis() tetiklensin (logout)
# - Misafir olarak gir → yalnız "Giriş Yap" butonu görünsün
```

---

## TESLIM KONTROL LİSTESİ
- [ ] `st.popover` migration yapıldı, elle CSS popover silindi
- [ ] Avatar: monokrom + başharf, emoji yok
- [ ] State mutasyonu kaldırıldı — `session_state` hiç dokunulmamış
- [ ] Buton aksiyonları (Ayarlar / Şifre / Çıkış / Giriş) çalışıyor
- [ ] `st.switch_page()` with deep-link (#sifre) doğru
- [ ] Dark mode: avatar + metin okunabilir
- [ ] Test geçti: `pytest tests/test_profil_menu.py -v` (8 test ✅)
- [ ] Kodlama denetimi: `kodlama_denetim.py --tam-repo` temiz ✅
- [ ] Dosya UTF-8, BOM yok
- [ ] Teslim özeti: değişen satırlar, test sayısı, eksik varsa yazıldı

---

## KAYNAKLAR
- **Şu an kod:** `src/company_master/ui/components/profil_menu.py` lines 54-267 (profil_menu function)
- **Elle CSS popover:** lines 84-140 (style block, `.{key}-wrapper`, `.{key}-avatar`, vb.)
- **Wireframe:** `docs/UX_PROFILMENU_WIREFRAME_2026-09-18.md` (tasarım +  kabul kriterleri)
- **App.py kullanımı:** `app.py:370-403` → `_topbar_menu_button()` → import + çağrı
- **Token sistem:** `src/company_master/ui/tokens.py` → `token("color", "surface-3")`
- **Streamlit popover:** https://docs.streamlit.io/library/api-reference/widgets/st.popover (1.62+)

---

## ZİNCİR
**Önceki:** UI-MENUTREE-02 (P1, utku) — done olmak gerek  
**Şimdi:** UI-PROFILMENU-POPOVER-02 (P2, utku) — şu an  
**Sonraki:** *(zincir sonu)*

---

**Hazır mısın başlamaya?** Brif sorusu varsa, teslim yazmadan önce yaz.
