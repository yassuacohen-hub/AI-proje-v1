# ADMIN-UX-SIDEBAR-TAB: Sidebar Tab Seçim Durumu Saklama + Aktif Tab Vurgusu

- **Sahip:** Utku
- **Öncelik:** P1
- **Task ID:** `ADMIN-UX-SIDEBAR-TAB` (tetikteki `ADMIN-UI-SIDEBAR` öneki hatalıydı — D-57)
- **Brif tarihi:** 2026-09-23
- **Yazan:** İhsan (orkestratör devralma, D-58) — D-66 ihlali kapatma

## 0. Neden bu brif sonradan yazıldı

Tetik `plans/brief_utku_ADMIN-UX-SIDEBAR-TAB.md` yolunu gösteriyordu ama dosya diskte yoktu;
panodaki `brief` alanı da boştu. Utku görevi `al` ile aldı ve brifsiz çalışmaya başladı.
Bu **D-66 (Brifsiz Atama Yasak)** ihlalidir. Bulgu `ORKESTRA-GOREV-KAPI-01` görevine dönüştürüldü.

## 1. Mevcut Durum (kod okundu — varsayım yok)

| Parça | Yer | Durum |
|---|---|---|
| `SECTIONS` navigasyon SSOT | [`web_dashboard/tabs/__init__.py`](../web_dashboard/tabs/__init__.py:1) | var |
| Sidebar çizimi | [`app.py`](../app.py:402) `render_sidebar()` | var |
| Aktif tab vurgusu | [`app.py`](../app.py:468) `type="primary" if aktif else "secondary"` + `disabled=aktif` | **zaten var** |
| Alt sekme aktif vurgusu | [`app.py`](../app.py:494) `alt_aktif` | **zaten var** |
| Oturum içi seçim | [`app.py`](../app.py:103) `st.session_state["current_section"]` | var |
| URL derin bağlantı | [`app.py`](../app.py:123) `st.query_params` | var |
| **Oturumlar arası kalıcılık** | — | **YOK ← gerçek eksik** |
| `varsayilan_bolum` ayarı | [`src/company_master/settings/user_settings.py`](../src/company_master/settings/user_settings.py:104) | var, sabit değer |

**Sonuç:** "aktif tab vurgusu" maddesi büyük ölçüde tamamlanmış. Asıl iş
**"tab seçim durumu saklama"**: tarayıcı kapanıp açılınca kullanıcı son gezdiği bölüme değil,
`SECTIONS[0]`'a düşüyor (`varsayilan_tab()`).

## 2. İş Maddeleri

1. **`tabs/__init__.py`** — iki ince fonksiyon ekle, saf/test edilebilir tut:
   - `son_bolum_kaydet(kullanici_id: str, anahtar: str) -> None`
   - `son_bolum_getir(kullanici_id: str) -> str | None`
   - Depolama: **yeni store açma.** Mevcut `company_master.settings` kullanıcı ayar deposunu kullan
     (`otomatik_yenileme` / `admin_auto_refresh.py` deseninin aynısı — K-04 kaydet deseni).
   - `SECTIONS` saf veri kalacak: bu fonksiyonlar `SECTIONS`'ı **değiştirmez**, modül seviyesinde
     Streamlit çağrısı yapmaz (modül docstring'indeki "Saf veri" kararı korunur).
2. **`user_settings.py`** — `varsayilan_bolum` seçeneklerine `"son_ziyaret"` değerini ekle.
   Varsayılan davranış değişmez; kullanıcı açıkça seçerse kalıcılık devreye girer.
   (Her tab geçişinde `varsayilan_bolum`'u sessizce ezme — kullanıcının açık tercihini yok eder.)
3. **`app.py`** — `bolum_sec()` içinde geçiş sonrası `son_bolum_kaydet(...)`; açılışta
   `varsayilan_tab()` yerine ayar `son_ziyaret` ise `son_bolum_getir()` → `tab_getir()` → yoksa
   `varsayilan_tab()` fallback.
4. **Misafir/anon:** `kullanici_id` yoksa veya `MISAFIR_KIMLIK` ise yazma yapma, sessizce geç
   (`admin_panel.py:284` misafir deseni). Yazma hatası paneli düşürmemeli.
5. **Yetki (U-10):** Kaydedilen anahtar artık rolün göremediği bir bölüme aitse
   (`erisebilir()` False) → `varsayilan_tab()`'a düş. Yetkisiz sayfaya derin bağlantı açma.

## 3. Dosyalar

- `web_dashboard/tabs/__init__.py` (birincil çıktı)
- `app.py`
- `src/company_master/settings/user_settings.py`
- `tests/test_dashboard_nav.py` veya `tests/test_web_dashboard_tabs.py` (yeni test)

## 4. Testler

```bash
cd "Huginn Data Insights"
pytest tests/test_web_dashboard_tabs.py tests/test_dashboard_nav.py tests/test_nav_ia04.py tests/test_app_nav_tek_tik.py -q
pytest tests/ -q
```

Yeni test en az şunları kapsasın:

- `son_bolum_kaydet` → `son_bolum_getir` gidiş-dönüş
- Bilinmeyen/silinmiş anahtar → `None`/fallback
- Yetkisiz rol için kayıtlı bölüm → `varsayilan_tab()`
- Misafir kimlikte yazma denemesi patlamaz

## 5. Kurallar

- **D-55:** Rapor 5 başlık zorunlu
- **D-183:** Dosya adı `_utku` sonekli
- **D-184:** Raporda `[[ADMIN-UX-SIDEBAR-TAB]]`, `[[D-66]]`, `[[web_dashboard/tabs/__init__.py]]` wikilink'leri
- **D-186:** Yeni belge = hub'a bağlantı
- **D-86:** Windows'ta çok satırlı `python -c` kullanma; geçici betik yaz
- Streamlit çağrısı `tabs/__init__.py` modül gövdesine **girmeyecek**

## 6. Teslim

```bash
python scripts/gorev_kutusu.py teslim ^
  --ajan utku ^
  --task-id ADMIN-UX-SIDEBAR-TAB ^
  --ozet "Sidebar tab kaliciligi: son_bolum_kaydet/getir + varsayilan_bolum=son_ziyaret. Aktif vurgu dogrulandi (zaten vardi). Rol/misafir fallback. Testler yesil." ^
  --cikti "web_dashboard/tabs/__init__.py"
```

## 7. Süre Tahmini

2 saat (kalıcılık + fallback + test)

## Ilgili Nodlar

- [[AGENTS]]
- [[ADMIN_DASHBOARD_HUB]]
- [[brief_utku_DASH-UX-02a-v2]]
- [[brief_utku_UI-ADOPT-01]]
