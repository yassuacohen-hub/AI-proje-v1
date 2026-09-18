# ADMIN-LOGIN-FIX-01 — Admin giriş: bağlantı hatası ile 401 ayrımı (P0)

## Sorun (teşhis tamam, 2026-09-18)
KAHİN bildirdi: misafir girişi çalışıyor, admin girişi çalışmıyor.

Teşhis zinciri:

| Katman | Durum | Kanıt |
|---|---|---|
| Şifre / DB eşleşmesi | ✅ sağlam | `admin_env_eslesme.py` → `DB kaydi=True eslesme=True`, `toplam cift=1 eslesen=1` |
| 2. admin hesabı | ✅ DB'de var | `admin_kimlik_kontrol.py` → `('yassuacohen@gmail.com', 'admin', 'onayli', True)` |
| FastAPI 8000 | ❌ kapalı | curl exit 7 (connection refused) |
| Docker Desktop | ❌ kapalı | `npipe:////./pipe/dockerDesktopLinuxEngine ... cannot find the file specified` |

**Kök neden:** Docker kapalı → FastAPI 8000 ayakta değil → `post_api("/api/admin/login")` bağlanamıyor →
`APIError` → UI "Giriş başarısız: e-posta/şifre kontrol ediniz." diyor. **Mesaj yanıltıcı.**
Misafir görünümü API çağırmadığı için etkilenmiyor.

## Yapılacaklar
1. [`web_dashboard/tabs/admin_auth.py`](../../web_dashboard/tabs/admin_auth.py) `render_admin_login()` içindeki
   `except APIError` dalını üçe ayır:
   - **bağlantı hatası** (connection refused / timeout / `ConnectionError`) →
     `st.error("API servisi yanıt vermiyor (port 8000).")` + `st.caption("Docker Desktop'ı başlatın, sonra: docker compose up -d --build api")`
   - **401** → mevcut kimlik ipucu (değişmez, SEC-AUTH-01 Y-2 gereği sunucu detayı sızdırılmaz)
   - **diğer** → genel hata + durum kodu
2. Aynı ayrımı `render_sifre_degistir()` içinde de uygula (varsa).
3. Test: `tests/test_admin_auth_hata_ayrimi.py` — bağlantı hatası ve 401 ayrı mesaj üretiyor (monkeypatch `post_api`).

## Kilitli dosyalar
- `web_dashboard/tabs/admin_auth.py`
- `tests/test_admin_auth_hata_ayrimi.py` (yeni)

## Kurallar
- UI dosyasına dokunuldu → teslimden ÖNCE `python scripts/streamlit_restart.py`.
- `python scripts/kodlama_denetim.py` + `python scripts/marka_denetim.py` temiz olmadan teslim yok.
- D-55: rapor adında ajan adı yok → `data/orchestrator/ADMIN-LOGIN-FIX-01_rapor_2026-09-18_uretim.md`

## Teslim
`python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-LOGIN-FIX-01 --ozet "..."`
P0 → otomatik onay YOK, orkestratör elle onaylar (S-07/D-46).
