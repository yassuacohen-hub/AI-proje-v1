# ADMIN-MODAL-STIL-01 — Admin modal: blur backdrop + marka kimliği (P1)

## Sorun (KAHİN bulgusu, 2026-09-18)
Modal backdrop açık (arka plan gözüküyor), marka kimliği yansımıyor, başka yerlerde yeniden kullanılamayacak durumdadır.

Ekran görseli:
- Admin Girişi modal'ı açılıyor
- Arkasında Ana Kontrol sayfası okunuyor
- Stil: siyah/gri, tutarsız
- Kullanılabilirlik: düşük odaklanma, marka olmayan alan

## Yapılacaklar
1. Modal wrapper bileşeni oluştur: [`web_dashboard/components/modal_dialog.py`](../../web_dashboard/components/modal_dialog.py) (yeni)
   - `backdrop_blur(blur_px: int = 10)` → CSS `backdrop-filter: blur(10px)`
   - Marka rengi: `--huginn-indigo: #6366f1` (D-45 design tokens)
   - Arka plan: `rgba(0, 0, 0, 0.5)` semi-transparent
   - Border: Indigo 1px
   - Font: Streamlit dark tema ile uyumlu

2. [`web_dashboard/tabs/admin_auth.py`](../../web_dashboard/tabs/admin_auth.py) `render_admin_login()` refactor:
   - `st.form()` yerine custom modal wrapper kullan
   - Modal başlığa Huginn 🦅 ikon + "Admin Girişi" (marka kimliği)
   - CSS class: `admin-modal`
   - Footer: "Şifre mi unuttunuz?" bağlantısı (ADMIN-SIFRE-RESET-FLOW-01 ile entegre)

3. Test: [`tests/test_admin_modal_stil.py`](../../tests/test_admin_modal_stil.py) (yeni)
   - CSS backdrop-filter parse test
   - Color token (#6366f1) validation
   - Reusable modal bileşeni bootstrap test

## Kilitli dosyalar
- `web_dashboard/tabs/admin_auth.py`
- `web_dashboard/components/modal_dialog.py` (yeni)
- `tests/test_admin_modal_stil.py` (yeni)

## Kurallar
- UI dosya → teslimden ÖNCE `python scripts/streamlit_restart.py`
- `python scripts/kodlama_denetim.py` + `python scripts/marka_denetim.py` temiz olmadan teslim yok
- D-55: rapor adında ajan adı yok → `data/orchestrator/ADMIN-MODAL-STIL-01_rapor_2026-09-18_uretim.md`
- Başka modal'lar (şifre reset, tenant, etc.) için reusable component

## Teslim
`python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-MODAL-STIL-01 --ozet "..."`
P1 → orkestratör elle onaylar (S-07).
