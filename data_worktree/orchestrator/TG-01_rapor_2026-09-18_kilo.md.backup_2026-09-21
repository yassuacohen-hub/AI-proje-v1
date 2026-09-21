# TG-01 Raporu

**Tarih:** 2026-09-18  
**Ajan:** kilo  
**Görev:** Telegram Bot Gönderim ve Komut Akışını Düzelt  
**Durum:** Teslim edildi, kontrolör onayı bekliyor

## Yapılanlar

- `TELEGRAM_ALLOWED_CHAT_IDS` desteği `.env.example`, ortak Telegram yetkilendirme akışı ve dokümantasyonla tutarlı hale getirildi.
- `/gorev-durum` aliası `/set_task_status` olarak düzeltildi; `/set_status` ile `project_state.md` not ekleme akışından ayrıştırıldı.
- `/help` komutları inline `<code>` / `<i>` etiketleri dışına çıkarıldı; komutlar Telegram bot command olarak seçilebilir ve her komut boş satırla ayrıldı.
- Yetkili komutlar `/help` içinde açık kategoriyle listelendi; `/restart_etl`, `/set_status`, `/set_task_status`, `/gorev-ekle`, `/pano`, `/onaylar`, `/onayla`, `/reddet`, `/teslim`, `/nobet` ve `/nobet-ayar` akışları dokümante edildi.
- `/wiki` OSTİM kalite raporu yerine V10 wiki dizinini ve ilgili wiki sayfalarını listeleyecek şekilde güncellendi.
- Telegram kurulum rehberi ve V10 Telegram bot rehberi güncellendi; ek yetkili chat ID açıklamaları eklendi.
- Telegram yardımcı modülü, canonical polling motoru, servis wrapper ve test dosyaları UTF-8 olarak kontrol edildi.

## Değiştirilen Dosyalar

- `.env.example`
- `scripts/telegram_polling.py`
- `scripts/README_TELEGRAM.md`
- `AI proje v1/V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md`
- `tests/test_telegram_polling.py`

TG-01 kapsamında daha önce değiştirilmiş ve doğrulanan dosyalar:

- `src/company_master/utils/telegram_bot.py`
- `src/company_master/telegram/bot_service.py`
- `scripts/telegram_periodic.py`
- `scripts/test_telegram.py`
- `scripts/test_telegram_simple.py`
- `tests/test_telegram_bot.py`
- `docker-compose.yml`
- `requirements-app.txt`
- `scripts/telegram_bot_task.bat`

## Test Sonuçları

- `pytest -q tests/test_telegram_bot.py tests/test_telegram_polling.py`: **126 passed**
- `python scripts/test_telegram.py`: **9 passed, 0 failed**
- `python scripts/test_telegram_simple.py`: **8/8 passed**
- `python -m py_compile` hedef Python dosyaları: **başarılı**
- `python scripts/kodlama_denetim.py`: **temiz**, BOM/NUL/mojibake/sozdizimi ihlali yok

## Kapsam ve Notlar

- Mock testler ve smoke testler başarılı; gerçek Telegram canlı gönderimi için geçerli token ve chat ID paylaşılmadığından canlı API testi tekrar çalıştırılmadı.
- Streamlit dosyası değiştirilmedi; Streamlit restart gerekmiyor.
- FastAPI dosyası değiştirilmedi; API build/restart gerekmiyor.
- TG-01 teslimi `review` durumuna alınmalı; P0/P1 görevlerinin onayı KAHİN (Ürün Sahibi) / roo tarafından yapılmalıdır.
- Teslim sonrası dosya kilitleri onay aşamasında korunur; `done` onayında otomatik bırakılır.
