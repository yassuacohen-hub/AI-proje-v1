# GÖREV BRİFİ: ORCH-10 — Telegram Orkestratör Bot Entegrasyonu

**Hedef Ajan:** `kilo`  
**Öncelik:** `P1`  
**Referanslar:** `AGENTS.md`, `ORCH-08`, `ORCH-09`, `scripts/telegram_polling.py`, `src/company_master/orchestrator/`

---

## Amaç & Vizyon
Kullanıcının bilgisayar başında olmadan, mobil üzerinden **Telegram'ı tam yetkili bir Orkestratör olarak kullanabilmesini** sağlamak.
Komutlar son derece kısa, token/zaman tasarruflu ve insan dostu olmalıdır.

---

## Eklenecek / Güncellenecek Telegram Komutları

| Komut | Parametre | Açıklama |
|---|---|---|
| `/at` | `<task_id> <ajan> <başlık>` | Panoya görev ekler ve ajanın posta kutusuna tetik atar (`gorev_at.py at` benzeri). |
| `/pano` | *(yok)* | Tüm ajanların bekleyen tetiklerini ve onay bekleyen teslimleri özetler. |
| `/onaylar` | *(yok)* | Ajanlar tarafından teslim edilmiş, inceleme (`review`) bekleyen işleri listeler. |
| `/onayla` | `<task_id>` | Teslim edilen görevi `done` yapar ve kilitli dosyaları serbest bırakır. |
| `/reddet` | `<task_id> <neden>` | Görevi reddeder, revizyon için ajanın postasına geri düşürür. |
| `/nobet` | *(yok)* | Manuel nöbetçi turu attırır (`nobet_tut()`), geciken iş varsa anında raporlar/ses/telegram basar. |
| `/nobet_ayar` | `<kademe_sn>` | Nöbetçi alarm süresini saniye cinsinden günceller (örn: `/nobet_ayar 600`). |

---

## Teknik Gereksinimler & Yapılacaklar

1. **`scripts/telegram_polling.py` Güncellemesi:**
   - `src.company_master.orchestrator` altındaki `task_board`, `trigger`, `nobetci` modüllerini entegre et.
   - Yukarıdaki yeni komutları (`/at`, `/pano`, `/onaylar`, `/onayla`, `/reddet`, `/nobet`, `/nobet_ayar`) dispatch tablosuna ve help mesajına ekle.
   - Komut yetkilendirmesini (`is_authorized`) kontrol et; yetkisiz kişilerin görev onaylamasını/atamasını engelle.
   - Çıktıları HTML formatında (`<b>`, `<code>`, `⚠️`, `✅`, `📌` emojileriyle) temiz ve okunabilir yap.

2. **Dokümantasyon:**
   - `V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md` dosyasını yeni komutlarla ve kullanım örnekleriyle güncelle.

3. **Test:**
   - `tests/test_telegram_polling.py` içerisine yeni komutların testlerini ekle ve `pytest` ile doğrula.

---

## Teslim Kriteri
- `pytest tests/test_telegram_polling.py` hatasız geçmelidir.
- Ajan işi bitirdiğinde:
  `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ORCH-10 --ozet "Telegram orkestratör komutları eklendi ve test edildi."`
  komutuyla görevi teslim etmelidir.
