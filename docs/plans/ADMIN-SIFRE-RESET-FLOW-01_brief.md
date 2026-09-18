# ADMIN-SIFRE-RESET-FLOW-01 — Şifre unuttum akışı: email gönder → link → sifre sifirla (P2)

## Sorun (KAHİN gözlemi, ekranda görüldü)
"Şifremi unuttum" düğmesi kırık hale — `POST /api/admin/reset-request` çalışmıyor.
API 8000 kapalı (Docker Desktop kapalı) → bağlantı hatası → yanıltıcı "e-posta/şifre kontrol ediniz" mesajı.

## Ayrıntı
1. **UI öğesi mevcut mi?** Kod taraması gerekli (modal içinde "Şifremi unuttum?" bağlantısı olması lazım)
2. **API endpoint'ler tanımlı mı?** FastAPI `web_app.py`:
   - `POST /api/admin/reset-request` (email gir → token + email gönder)
   - `POST /api/admin/reset` (token + yeni_sifre → DB güncelle)
3. **Email gönderme:** SMTP ayarlanmış mı?
4. **Token geçerlilik:** TTL, JWT, secure linking?

## Yapılacaklar
1. Modal içinde "Şifremi unuttum?" bağlantısı opsiyonu:
   - Button/link → modal açır → email giriş formu
   - Gönder → POST `/api/admin/reset-request` (email)
   - Yanıt: "Sıfırlama e-postası gönderildi" + sonraki adım açıklaması

2. Reset bağlantısı (e-postada) → `/kimlik?reset_token=XYZ` sayfasına gider
   - URL parametresini parse et
   - Yeni şifre formu + Gönder
   - POST `/api/admin/reset` (token + password)
   - Başarı: admin paneline yönlendir

3. UI hata ayrımı (ADMIN-LOGIN-FIX-01 ile koordine):
   - Bağlantı hatası (API kapalı) → "API servisi yanıt vermiyor"
   - 400/422 (geçersiz email) → "E-posta sistemde bulunamadı"
   - 200 (başarı) → "E-posta gönderildi, 10 dk içinde bağlantıyı kontrol edin"

4. Test: [`tests/test_admin_sifre_reset_flow.py`](../../tests/test_admin_sifre_reset_flow.py) (yeni)
   - Bağlantı hatası tespit
   - Email doğrulama
   - Token TTL ve güvenlik

## Kilitli dosyalar
- `web_dashboard/tabs/admin_auth.py`
- `tests/test_admin_sifre_reset_flow.py` (yeni)
- `web_app.py` (FastAPI, gerekirse — kurulum kontrolü)

## Kurallar
- UI dosya → `python scripts/streamlit_restart.py` teslimden ÖNCE
- `python scripts/kodlama_denetim.py` + `python scripts/marka_denetim.py` temiz olmadan teslim yok
- D-55: rapor adında ajan adı yok
- SMTP ayarı eksikse: `docs/plans/ADMIN-SIFRE-SMTP-SETUP-01_brief.md` önerisi

## Bağımlılık
`ADMIN-LOGIN-FIX-01` → tamamlandığında (hata ayrımı) reset flow'un hata mesajları tutarlı olur.

## Teslim
`python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-SIFRE-RESET-FLOW-01 --ozet "..."`
P2 → orkestratör elle onaylar.
