# ADMIN-UX-LOGOUT-01 — Brif

**Görev ID:** ADMIN-UX-LOGOUT-01  
**Sahip:** Üretim/Hacim Utku  
**Öncelik:** P0  
**Tahmini Süre:** 2s  
**Çıktı:** `src/company_master/ui/modals/logout_modal.py` (120 satır, 7 test)

---

## Problem

Admin panel logout işlemi modal diyalog ve toast feedback senkronizasyonu yapılmış, fakat ek test ve robustluk düzeltmesi gerekir:
- Popover içinde logout seçeneği tıklandığında modal açılmalı
- Modal "Çıkmak istediğinize emin misiniz?" sorusu + İptal/Çıkış butonları
- Çıkış butonuna basınca:
  - Session state temizle (auth token, user ID, preferences)
  - Toast mesajı göster ("Başarıyla çıktınız")
  - Ana sayfa'ya yönlendir (Streamlit rerun)
- İptal butonuna basınca modal kapat, prof menüye dön (state değişim yok)

**Tasarım referansı:** `data/orchestrator/ZINCIR-ADMIN-PANEL-UX-TASARIMI_2026-09-20_orkestrator.md` (§ 3.5)

---

## İş Maddeleri

1. **Modal Bileşen Yapısı:**
   - Dosya: `src/company_master/ui/modals/logout_modal.py`
   - Fonksiyon: `def show_logout_modal() -> None`
   - Streamlit `st.modal()` (1.62+) veya `st.info()` + callback pattern kullan
   - Modal title, message, 2 button (İptal/Çıkış)

2. **Logout Flow:**
   - Çıkış butonuna basınca:
     - `session_state.auth_token = None`
     - `session_state.user_id = None`
     - `session_state.current_page = "login"`
     - `st.toast("Başarıyla çıktınız", icon="👋")`
     - `st.rerun()` (login sayfasına geri dön)
   - İptal butonuna basınca:
     - Modal kapat (`session_state.show_logout_modal = False`)
     - Profil menüye dön

3. **Senkronizasyon Kontrol:**
   - Profil menu'den logout seçeneği (`profile_menu_popover.py`) modal tetiklemeli
   - `session_state.show_logout_modal = True` set edilmeli
   - App.py'de `if session_state.show_logout_modal: show_logout_modal()`

4. **Test Yaz (7 case):**
   - Test dosya: `tests/ui/test_logout_modal.py`
   - Case 1: Modal render ve butonlar görünür mü
   - Case 2: Çıkış butonuna basınca session_state temizleniyor mu
   - Case 3: Toast mesajı gösteriliyor mu
   - Case 4: st.rerun() çağrılıyor mu
   - Case 5: İptal butonuna basınca modal kapanıyor mu
   - Case 6: Dark mode stil uyumu
   - Case 7: Regresyon testi — şifreli çıkış veya sistem hatası durumu

5. **İntegrasyon:**
   - app.py'de profile menu'ye logout button eklenmeli
   - Modal conditional render: `if session_state.show_logout_modal: ...`
   - Toast mesajları test edilmeli

6. **Rapor Yaz (D-67 formatı):**
   - **Ne yapıldı:** Logout modal bileşeni + flow senkronizasyonu + test
   - **Değişen dosyalar:** logout_modal.py (yeni), test_logout_modal.py (yeni), app.py (entegrasyon), profile_menu_popover.py (callback)
   - **Test sonuçları:** 7/7 PASSED
   - **Bulgular:** Senkronizasyon sağlam, session state temizliği çalışıyor, UX smooth (🟢)
   - **Eksik/Erteleme:** Varsa yada "Yok"

---

## Kabul Kriterleri

- ✅ Logout modal bileşeni yazılmış, 120 satır
- ✅ Modal açılıp kapanabiliyor, butonlar işlevsel
- ✅ Çıkış: session_state temizleniyor, toast gösteriliyor, ana sayfa yönlendirmesi
- ✅ İptal: modal kapanıyor, state değişim yok
- ✅ 7 test yazılmış ve PASSED
- ✅ Profil menü'den logout → modal tetikleme sağlıyor
- ✅ Kodlama denetim: `python scripts/kodlama_denetim.py` temiz
- ✅ Streamlit restart yapılmış: `python scripts/streamlit_restart.py`
- ✅ Rapor D-67 formatında yazıldı

---

## Kilit Dosyalar

- `src/company_master/ui/modals/logout_modal.py` (yazılacak, 120 satır)
- `tests/ui/test_logout_modal.py` (yazılacak, 7 test)
- `app.py` (değiştirilecek, modal conditional render)
- `profile_menu_popover.py` (değiştirilecek, logout callback)

---

## Ön Koşullar

- UI-MENUTREE-02 + UI-PROFILMENU-POPOVER-02 tamamlanmış
- Streamlit 1.62+ (st.modal/st.toast support)
- `admin_cikis()` fonksiyonu mevcut (session temizliği)

**Zincir Sonu:** Logout modal sonrası admin panel UX zinciri tamamlanır.
