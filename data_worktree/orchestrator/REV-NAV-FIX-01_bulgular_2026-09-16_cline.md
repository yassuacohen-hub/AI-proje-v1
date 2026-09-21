[[Huginn Data Insights/data/orchestrator/REV-NAV-FIX-01_bulgular_2026-09-16_cline.md]]

# REV-NAV-FIX-01 — NAV-FIX-01 Çapraz İnceleme (kilo teslimi, commit 90d9bc7)

**İnceleyen:** cline · **Tarih:** 2026-09-16 · **Sonuç: ✅ ONAY** (engelleyici bulgu yok)

## Kapsam (90d9bc7)
`app.py` (±42 satır) · `tests/test_app_nav_tek_tik.py` (yeni, 85 satır) · `tests/test_ajan_normalize.py` (yeni, D-33) · `scripts/gorev_at.py`/`gorev_kutusu.py` (D-33 ajan normalize ekleri)

## Doğrulanan Kanıtlar
1. **page_icon düzeltmesi:** `app.py` L68 `page_icon="🦅"` ✓ (önceki bozuk sekans kaldırıldı).
2. **NAV-FIX-01 tek tık geçiş:** `render_sidebar` selectbox'a `on_change=_hizli_gecis_onchange` eklendi; callback `st.session_state["nav_hizli_gecis"]` okuyup `bolum_sec(secim)` çağırıyor — "widget oluştuktan sonra session_state yazılamaz" kısıtı callback'e taşımayla doğru çözülmüş. Eski çift-tık akışındaki `if secim.anahtar != secili.anahtar` koşullu `bolum_sec` kaldırıldı.
3. **Arama sorgu temizleme:** tek eşleşmeden sonra `st.session_state[ARAMA_KEY] = ""` — bu sefer widget iç state'i değil ayrı bir anahtar yazıldığı için `StreamlitAPIException` yok; eşleşmeyen sorgu caption'ı `'…'` olarak sadeleşmiş. Testi `test_app_nav_tek_tik.py`'de.
4. **NAV-FIX-03 (aynı commit):** menü tooltip'leri varsayılan KAPALI — `_nav_ipucu` `IPUCU_KEY` kapalıyken `None` döner → `help=None` ile tooltip render edilmez; sidebar'da "Menü ipuçlarını göster" toggle'ı eklendi. Sahip bulgusuyla (tooltip butonlara biniyor) uyumlu; IA/tooltip davranışı isteğe bağlı geri açılabilir.
5. **Kodlama sağlığı (byte-düzey):** `app.py`, `admin_panel.py`, `test_app_nav_tek_tik.py`, `test_ajan_normalize.py` — hepsi strict UTF-8 OK, BOM yok, NUL yok, `ast.parse` OK, mojibake göstergesi yok. `admin_panel.py` L250-256 (teslim notundaki şüphe bölgesi) temiz ✓.
6. **Hedefli testler (ölçülen):** `test_dashboard_nav + test_app_menu_rol + test_web_dashboard_tabs + test_app_nav_tek_tik` = **98 passed, 1 skipped** (0 hata). Kilo'nun "184 test" sayısı farklı toplam/koleksiyon; engel değil — mevcut durum yeşil. Tam regresyon kilo'da 3480 passed / 5 failed (önceden var olan, NAV-FIX-01 dışı) — teyit: bu 5'in listesi roo'nun regresyon notuyla uyumlu kapsam dışı küme.

## Notlar / Kapsam Dışı Gözlemler (engel değil)
- Commit, sözleşme dışı işleri de taşıyor: NAV-FIX-03 (tooltip toggle — NAV-FIX-01 notuyla uyumlu) ve D-33 ajan normalize (`gorev_at.py`/`gorev_kutusu.py` + 64 satır test). Görev kutusu koduna müdahale dikkat gerektirir ama testle gelirli; davranış bozulması görülmedi (bak/ozet/teslim akışları bu inceleme sırasında sorunsuz çalıştı).
- Commitlenmemiş plan dokümanları repo'da untracked bekliyor: `docs/plans/NAV-FIX-02_brief.md`, `docs/plans/NAV-PLAN-01_v4.md`, `plans/brief_kilo_NAV-FIX-01.md` — kilo'nun commit edeceği iş; unutulmasın.
- `app.py` KAPSAM_DIZINLERI (src/tests/web_dashboard/scripts) dışında kökte olduğu için standart kodlama taramasına girmiyor; byte-düzey kontrol bu boşluğu bu incelemede kapattı. GUARD-ENC-01 sonrası `--kapsam git` modu kök dosyaları da yakalar.

**Öneri:** `NAV-FIX-01` → **onayla**. Streamlit UI el kontrolü (tooltip konumu, hızlı geçiş UX) sahibin günlük kullanımında teyit edilebilir.
