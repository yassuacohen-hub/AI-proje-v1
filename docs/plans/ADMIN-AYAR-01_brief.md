# ADMIN-AYAR-01 — Kullanıcı ayarlarını gerçekten tüket (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md`. Zincir halkası 1/4.
> Kaynak bulgular: `docs/ROO_ELESTIRI_NOTLARI.md` K-04 (ayarlar yazılıyor, okunmuyor) + S-08 (herkes `misafir` dosyasını paylaşıyor).

## Kapsam
- `web_dashboard/tabs/admin_auto_refresh.py`, `web_dashboard/tabs/admin_panel.py`,
  `src/company_master/settings/user_settings.py`, `tests/test_admin_panel_tab.py`, `tests/test_admin_auto_refresh.py` (yoksa oluştur).
- DOKUNMA: `web_dashboard/tabs/__init__.py`, `app.py` (cline kilidi / roo).

## İş
1. **S-08 kimlik:** `aktif_kullanici()` (`admin_panel.py:179`) admin oturumu yokken `misafir` dönüyor → ayar sekmesi giriş yapılmamışsa **salt-okunur** olsun: form yerine `st.info("Ayarları kaydetmek için giriş yapın")` + varsayılanlar gösterilir. `misafir.json` artık yazılmaz (`ayarlari_yaz` çağrısı yalnız gerçek kimlikte).
2. **K-04 otomatik yenileme:** `render_auto_refresh()` başlangıç değerlerini `ayarlari_getir(kullanici_id)` → `otomatik_yenileme` / `yenileme_araligi` alanlarından alsın (`REFRESH_INTERVALS` sabiti şemadaki `secenekler` ile tek kaynaktan türetilsin: `_SEMA_HARITASI["yenileme_araligi"].secenekler`). Panelde aralık/aç-kapat değiştirilince `ayar_kaydet` ile diske yaz (yalnız gerçek kimlik).
3. **K-04 KVKK maskeleme:** `kvkk_maskeleme` ayarı için `user_settings.py`'ye yardımcı ekle: `kvkk_maske_acik(kullanici_id) -> bool`. `musteri_yonetimi.py`'de zaten `email_masked` kolonları kullanılıyor; bu görevde yalnız yardımcı + test; tüketim UI-MIMARI-02'de.
4. **Şema temizliği:** hiçbir yerde okunmayan ayarlar (`dil`, `saat_dilimi`, `bildirim_*`, `disa_aktarim_bicimi`, `varsayilan_bolum`, `yogun_mod`, `sayfa_boyutu`, `tema`) SİLİNMEZ; her birinin `aciklama` sonuna `" (henüz uygulanmıyor)"` eklenir ve panelde `st.caption` ile gösterilir. Böylece sahip neyin çalışıp çalışmadığını görür.
5. Testler: kimlik yokken yazma olmaz; aralık şemadan geliyor; ayar → auto_refresh başlangıcı; `kvkk_maske_acik` varsayılan True. `tmp_path` ile, gerçek `data/user_settings/` yazılmaz.

## Teslim kriteri
- Tam süit yeşil; `python scripts/kodlama_denetim.py` temiz; `python scripts/streamlit_restart.py` çalıştırıldı.
- Rapor: `data/orchestrator/ADMIN-AYAR-01_rapor_<tarih>_kilo.md` (hangi ayar artık nerede tüketiliyor tablosu).
