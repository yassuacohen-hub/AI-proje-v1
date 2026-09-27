# UI-PROFILMENU-POPOVER-02 — Brif

**Görev ID:** UI-PROFILMENU-POPOVER-02  
**Sahip:** Üretim/Hacim Utku  
**Öncelik:** P2  
**Tahmini Süre:** 2s  
**Çıktı:** `src/company_master/ui/components/profile_menu_popover.py` (95 satır, 6 test)

---

## Problem

Profil menüsü şu anki CSS/div popover'ı yerine Streamlit native `st.popover` (1.62+) kullanmaya çevrilecek:
- Eski kod: HTML/CSS hardcode, session_state yazılı, form input ile karmaşa
- Yeni tasarım: Streamlit widget'ları (st.popover, st.button), session_state temiz, form girdi yok
- Avatar: Monokrom baş harf emoji (renkli emoji değil)
- Dark mode uyumlu, responsive

**Tasarım referansı:** `data/orchestrator/ZINCIR-ADMIN-PANEL-UX-TASARIMI_2026-09-20_orkestrator.md` (§ 3.3)

---

## İş Maddeleri

1. **st.popover Yapısı Kur:**
   - `st.popover("👤 Profil")` widget'ı oluştur (admin panel başlığında)
   - Popover açılınca içerik: Kullanıcı adı, avatar, 3 seçenek (Ayarlar, Yardım, Çıkış)
   - Form tag, input field, state saklaması yok (Streamlit state management yeterli)

2. **Avatar Render:**
   - Kullanıcı ismi ilk harfi (monokrom, emoji değil): "A" → "🅰️" şeklinde symbol veya basit text
   - Dark mode: Arka plan kontrastlı, metin okunabilir
   - Responsive: Mobil ekranda tıklanabilir kalacak

3. **Popover Seçenekleri:**
   - **Ayarlar:** st.button, tıklanınca ayarlar sayfasına link / state geçişi
   - **Yardım:** Dokümantasyon linkine yönlendirme
   - **Çıkış:** admin_cikis() fonksiyonunu çağır, oturum temizle, ana sayfa'ya yönlendir

4. **Session State Yönetimi:**
   - `st.session_state.current_page` değişkeni (Ayarlar > state > rerender)
   - Logout: session_state temiz (auth token, user bilgi)
   - State değişimi Streamlit rerun tetiklerse sorun değil (native flow)

5. **Bileşen Yaz:**
   - Dosya: `src/company_master/ui/components/profile_menu_popover.py`
   - Fonksiyon: `def render_profile_menu_popover(username: str, avatar_initial: str) -> None`
   - Streamlit widget'ları kullan, hardcode HTML/CSS yok
   - Type hint: username, avatar_initial string, return None

6. **Test Yaz (6 case):**
   - Test dosya: `tests/ui/test_profile_menu_popover.py`
   - Case 1: Popover render ve açılma
   - Case 2-3: Avatar baş harf doğru render
   - Case 4: Ayarlar seçeneği > page geçişi
   - Case 5: Çıkış seçeneği > session_state temizliği
   - Case 6: Dark mode stil uyumu

7. **İntegrasyon:**
   - app.py başlığında profil menüsü render'ını yerleştir
   - Logout flow (admin_cikis + toast message) eklenmiş (Streamlit rerun + ana sayfa)

8. **Rapor Yaz (D-67 formatı):**
   - **Ne yapıldı:** st.popover geçişi, bileşen yaz, testler
   - **Değişen dosyalar:** profile_menu_popover.py (yeni), test_profile_menu_popover.py (yeni), app.py (entegrasyon)
   - **Test sonuçları:** 6/6 PASSED
   - **Bulgular:** Streamlit native, state temiz, logout akış sağlam (🟢)
   - **Eksik/Erteleme:** Varsa yada "Yok"

---

## Kabul Kriterleri

- ✅ Profile menüsü st.popover ile yazılmış, 95 satır
- ✅ Avatar baş harf (monokrom) render edilmiş
- ✅ 3 seçenek (Ayarlar, Yardım, Çıkış) fonksiyonel
- ✅ Logout session_state temizliyor, ana sayfa yönlendiriyor
- ✅ 6 test yazılmış ve PASSED
- ✅ App.py'de popover entegre edilmiş
- ✅ Kodlama denetim: `python scripts/kodlama_denetim.py` temiz
- ✅ Streamlit restart yapılmış: `python scripts/streamlit_restart.py`
- ✅ Rapor D-67 formatında yazıldı

---

## Kilit Dosyalar

- `src/company_master/ui/components/profile_menu_popover.py` (yazılacak, 95 satır)
- `tests/ui/test_profile_menu_popover.py` (yazılacak, 6 test)
- `app.py` (değiştirilecek, popover entegrasyon)

---

## Ön Koşullar

- UI-MENUTREE-02 tamamlanmış
- Streamlit 1.62+ (st.popover support)
- admin_cikis() fonksiyonu mevcut

**Sonraki:** ORKESTRA-VAULT-TEKRAR-01 başlayabilir
