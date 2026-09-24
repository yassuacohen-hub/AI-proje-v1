# ALTYAPI-ADMIN-PANO-01 — Task Board Gerçek Zamanlı Görünümü

**Ajan:** Utku  
**Aciliyet:** P2 (Sprint 2, admin panel temel shell mevcut)  
**Süre:** 2 saat  
**Tür:** Altyapı (Admin panel bileşen)  
**Kilitli dosya:** `web_dashboard/tabs/admin_panel.py`  
**Bağımlılık:** yok  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
Admin panelde görev panosunun 4 bölüm halinde (Tamamlandı/Beklemede/Yedek/Değerlendirme) gerçek zamanlı görünmesi gerekir. SSOT §8.1 ve D-77 (pano işleri orkestratöre aittir) gerektirir.

## Doğrulanacak varsayım
- Veri kaynağı: `data/orchestrator/task_board.json` (senkronize)
- Skill havuzu entegrasyonu YOK — `.agents/skills/shared/` repo'da hazır
- Admin panel sadece task_board gerçek zamanlı görünüm gösterir
- Filtreleme: ajan / aciliyet / tarih aralığı
- Pano sorgusu: D-77 orta kısım (pano durum eşlemeleri)
- Component fonksiyon: `render_task_board_tab()` → `web_dashboard/tabs/admin_panel.py` veya yeni dosya
- Streamlit form: filtreleme + tablo rengi (bölüme göre)
- Testler: `tests/test_admin_pano_board_view.py` (4 bölüm veri hazırlığı)
- Dok: `docs/ADMIN_PANO_BOARD_VIEW.md` (filtreleme kuralları, durum döngüsü)

## Adımlar
1. `web_dashboard/tabs/admin_panel.py` içinde `render_task_board_tab()` fonksiyonunu yaz
2. 4 bölüm için veri çekme: done / (aktif+review+bekliyor) / plan / (blocked+reddet)
3. Streamlit tablo bileşenleri: st.dataframe veya st.table + filtreleme formu
4. Bölüme göre renk kodlaması (Tamamlandı=yeşil, Beklemede=sarı, Yedek=gri, Değerlendirme=kırmızı)
5. Filtreleme: ajan seçimi (multiselect), aciliyet (P0/P1/P2), tarih aralığı (date_input)
6. Test dosyası yaz: `tests/test_admin_pano_board_view.py` (4 bölüm veri hazırlığı)
7. Dok yaz: `docs/ADMIN_PANO_BOARD_VIEW.md`

## Kabul kriteri
- [ ] `render_task_board_tab()` fonksiyonu çalışıyor ve 4 bölümü gösteriyor
- [ ] Filtreleme (ajan/aciliyet/tarih) çalışıyor
- [ ] Tablo renk kodlaması 4 bölüm için uygulanmış
- [ ] `tests/test_admin_pano_board_view.py` en az 4 test geçiyor
- [ ] `docs/ADMIN_PANO_BOARD_VIEW.md` yazılmış

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-ADMIN-PANO-01 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
- [[hubs/ADMIN_DASHBOARD_HUB]]