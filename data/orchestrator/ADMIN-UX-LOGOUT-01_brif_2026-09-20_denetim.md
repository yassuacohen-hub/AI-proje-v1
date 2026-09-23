# ADMIN-UX-LOGOUT-01 Briefi

## GÖREV TANIMI
Admin panel logout akışı: profil menü popover'ından tetiklenen logout onay modalı ve toast feedback senkronizasyonu. Detaylı brif: `data_worktree/orchestrator/ADMIN-UX-LOGOUT-01_brif_2026-09-20_uretim.md`.

## İŞ MADDELERİ
1. `src/company_master/ui/modals/logout_modal.py` — `show_logout_modal()` bileşeni (İptal/Çıkış butonları)
2. Çıkış akışı: session_state temizle (auth_token, user_id, current_page="login") + `st.toast("Başarıyla çıktınız")` + `st.rerun()`
3. İptal akışı: modal kapat, state değişimi yok
4. `profile_menu_popover.py` callback + `app.py` conditional render entegrasyonu
5. `tests/ui/test_logout_modal.py` — 7 test case
6. D-67 formatında rapor yaz

## KENDİ-KONTROL
- [ ] İş tamamlandı
- [ ] 7/7 test PASSED
- [ ] `python scripts/kodlama_denetim.py` temiz
