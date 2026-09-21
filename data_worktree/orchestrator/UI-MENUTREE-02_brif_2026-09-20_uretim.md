# UI-MENUTREE-02 — Brif

**Görev ID:** UI-MENUTREE-02  
**Sahip:** Üretim/Hacim Utku  
**Öncelik:** P1  
**Tahmini Süre:** 3s  
**Çıktı:** `src/company_master/ui/components/admin_menu_tree.py` (170 satır, 8 test)

---

## Problem

Admin panel sol menüsü ağacı (menu tree) tekrardan düzeltilmesi gerekir:
- Ayarlar sekmesi ana menüden ayrılarak profil menüsüne taşınmış
- Menu yapısı 6 üst kategori + 16 alt bölüm (tasarımda sınırlı)
- 8 sekme menüsüz (arama, executive, performans, webhook, dlq, yenileme, ayarlar, yükleme)
- Tüm sekme tanımları gerçek dosyalara işaret etmeli, orphan link kalmaması

**Tasarım referansı:** `data/orchestrator/ZINCIR-ADMIN-PANEL-UX-TASARIMI_2026-09-20_orkestrator.md` (§ 3.2)

---

## İş Maddeleri

1. **Menu Ağacı Yapısı Oluştur:**
   - Admin panel sol menü (Streamlit `st.selectbox` / `st.radio` vb.) için ağaç JSON/Python yapısı kur
   - 6 ana kategori: Dashboard, İstatistik, Ayarlar, Raporlar, Sistem, Konfigürasyon (tasarımdan oku)
   - Her alt sekme (`tabs.py`) içindeki `TAB_DEFINITIONS` ile senkronize et

2. **Sekme Linklerini Doğrula:**
   - Tüm 16 alt sekme gerçekten `web_dashboard/tabs/` içinde `.py` dosyası olarak var mı?
   - Dosya adı vs menu label eşleşmesi kontrol et
   - Orphan/broken link var mı (menu'de var ama dosya yok) test et

3. **Menüsüz Sekmeleri İşle:**
   - 8 sekme (arama, executive, vb.) menü ağacında görünmeyecek; neden (ön koşul, geliştirme devam, vb.) açıkla
   - Koda yorum yaz (her bölüm için `# Neden menüsüz` bloğu)

4. **Bileşen Yaz:**
   - Dosya: `src/company_master/ui/components/admin_menu_tree.py`
   - Fonksiyon: `def render_menu_tree(session_state) -> str` (seçilen sekme ID döner)
   - Streamlit yerleşik widget'ları kullan (st.selectbox, st.columns, vb.)
   - CSS/HTML hardcode yok (Streamlit native)
   - Dark mode uyumlu, responsive

5. **Test Yaz (8 case):**
   - Test dosya: `tests/ui/test_admin_menu_tree.py`
   - Case 1-3: Ağaç yapısı load ve yapı (6 kategori, 16 alt)
   - Case 4-6: Link doğrulama (orphan link yok, tüm dosyalar var)
   - Case 7: Dark mode stil uyumu
   - Case 8: Session state alınıp döndürme

6. **İntegrasyon Test:**
   - `app.py` içinde menu_tree render'ını yerleştir (admin panel layout'unda)
   - Streamlit run ettiğinde menü görünsün, tıklanabilir olsun

7. **Rapor Yaz (D-67 formatı):**
   - **Ne yapıldı:** Menu ağacı tasarımı + bileşen + testler
   - **Değişen dosyalar:** admin_menu_tree.py (yeni), test_admin_menu_tree.py (yeni), app.py (entegrasyon)
   - **Test sonuçları:** 8/8 PASSED
   - **Bulgular:** Yapı sağlam, link validasyonu çalışıyor, responsive (🟢)
   - **Eksik/Erteleme:** Varsa yada "Yok"

---

## Kabul Kriterleri

- ✅ Menu ağacı bileşeni yazılmış ve 170 satır
- ✅ 6 ana kategori + 16 alt sekme doğru yapılandırılmış
- ✅ 8 menüsüz sekme tanımlanmış, neden açıklanmış
- ✅ Tüm sekme dosyaları gerçekten var (orphan link yok)
- ✅ 8 test yazılmış ve PASSED
- ✅ App.py'de menü render edilmiş
- ✅ Kodlama denetim: `python scripts/kodlama_denetim.py` temiz
- ✅ Streamlit restart yapılmış: `python scripts/streamlit_restart.py`
- ✅ Rapor D-67 formatında yazıldı

---

## Kilit Dosyalar

- `src/company_master/ui/components/admin_menu_tree.py` (yazılacak, 170 satır)
- `tests/ui/test_admin_menu_tree.py` (yazılacak, 8 test)
- `app.py` (değiştirilecek, menu entegrasyonu)

---

## Ön Koşullar

- Altyapı-TEST-FAILURE-FIX-01 tamamlanmış (test suite temiz)
- Streamlit 1.62+ yüklü (st.selectbox/st.radio yönetimi)
- web_dashboard/tabs/ dizini hazır, TAB_DEFINITIONS mevcut

**Sonraki:** UI-PROFILMENU-POPOVER-02 başlayabilir
