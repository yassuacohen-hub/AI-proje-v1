# 🤖 Telegram Bot Kullanım Rehberi

**Bot:** `@Huginn_Insights_Bot`  
**Amaç:** Huginn Data Insights — Ankara B2B Company Master projesinin takibi ve yönetimi

---

## 🔐 Güvenlik

Bot, **yalnızca senin Telegram ID'n** (`TELEGRAM_CHAT_ID`) ile etkileşime geçer.  
Diğer kullanıcilar her komutta `🚫 Yetkisiz erişim.` alır.

---

## 📋 Komut Listesi

### `/start`
- **İşlev:** Bot'u tanıştırır, merhaba mesajı gönderir.
- **Kullanım:** Herhangi bir zamanda, ilk kez kullanırken.
- **Örnek:** `/start`

### `/help`
- **İşlev:** Tüm komutları açıklamalarıyla listeler (ne işe yarar, örnek senaryo ile).
- **Kullanım:** Hangi komutu ne zaman kullanacağını hatırlamak için — zaman zaman `/help` yazman yeterli.
- **Örnek:** `/help`

### `/status`
- **İşlev:** Proje durumunu özetler — firma sayısı, son güncellemeler.
- **Kullanım:** Hızlı bir durum kontrolü yapmak için.
- **Örnek:** `/status`

### `/gorev`
- **İşlev:** Aktif ve bekleyen görevleri gösterir.
- **Kullanım:** Ne yapıldı, ne bekliyor göstermek için.
- **Örnek:** `/gorev`

### `/rapor`
- **İşlev:** Son veri kalite raporunu özetler.
- **Kullanım:** Veri kalitesi durumunu kontrol etmek için.
- **Örnek:** `/rapor`

### `/wiki`
- **İşlev:** Önemli wiki sayfalarının linklerini gösterir.
- **Kullanım:** Dokümanlara hızlı erişmek için.
- **Örnek:** `/wiki`

### `/degisiklik`
- **İşlev:** Son izleme kontrolünden beri değişenleri gösterir — yeni firmalar + kalite skoru ±10 ve üzeri değişenler.
- **Kullanım:** Gece ingest/backup sonrası "sabah ne değişti?" sorusuna tek bakışta cevap.
- **Örnek:** `/degisiklik` → "🔔 Değişiklik: +3 yeni firma, 1 skor artışı" ya da "Değişiklik yok."
- **Not:** Her sabah 08:00'deki otomatik bildirim de aynı motordur (değişiklik yoksa sessiz kalır).

### `/gunluk`
- **İşlev:** Günlük özet kartı gönderir — toplam firma, kayıt sayısı, ortalama kalite, kalite dağılımı.
- **Kullanım:** 09:00 otomatik raporunu beklemeden manuel özet almak istersen.
- **Örnek:** `/gunluk` → "📊 Günlük Özet: 9.227 firma, ort. kalite 62.4/100..."

### `/izleme`
- **İşlev:** Değişiklik izleme durumunu gösterir — kaç firma izleniyor, son kontrol ne zaman yapıldı.
- **Kullanım:** Bildirimlerin çalışıp çalışmadığından şüphelenirsen ilk bakılacak yer.
- **Örnek:** `/izleme` → "İzleme aktif. İzlenen firma: 9.227. Son kontrol: 08.09.2026 22:31"

### `/restart_etl`
- **İşlev:** ETL pipeline'ını yeniden başlatır (~9 bin firma yeniden işlenir).
- **Kullanım:** Veri yenileme, hata düzeltme, yeni veri ekleme sonrası.
- **⚠️ Dikkat:** İşlem 2-3 saniye sürer, arka planda çalışır.
- **Örnek:** `/restart_etl`

### `/set_status <mesaj>`
- **İşlev:** `project_state.md` dosyasına not ekler.
- **Kullanım:** Proje durumunu Telegram'dan güncellemek için.
- **Örnek:** `/set_status Entity resolution entegrasyonu tamamlandı.`

---

## ⏰ Otomatik Rapor (Cron)

Bot, her sabah **09:00**'da otomatik olarak bir rapor gönderir:
- Toplam firma sayısı
- Kayıt sayısı (source_records)
- Entity resolution sayısı
- Sürüm ve son güncellemeler

Bu raporu almak için bot'un açık olması gerekir (arka plan servisi).

---

## 🚀 Bot'u Başlatma

```bash
# PowerShell'den:
.\scripts\start_bot.ps1

# Veya doğrudan:
python scripts\telegram_polling.py
```

Gerekli ortam değişkenleri `.env` dosyasında olmalıdır:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

## 📊 Örnek Akış

1. **Sabah 09:00** → Otomatik daily report gelir
2. **`/status`** → Proje durumunu kontrol eder
3. **`/restart_etl`** → Yeni veri ekleme sonrası yeniden yükleme
4. **`/set_status Yeni veri seti eklendi`** → project_state.md'ye not ekler
5. **`/gorev`** → Ne görevler bekliyor görür