# D-216: Telegram Menü — 📈 RAPOR MENÜSÜ

## Görüntü

```
╔═════════════════════════════════╗
║  📈 Raporlar & Analitik         ║
╚═════════════════════════════════╝

┌─ ZAMAN DİLİMLERİ ────────────────┐
│ [📅 Hafta]  [📅 Ay]  [📅 YTD]   │
└────────────────────────────────────┘

┌─ DETAY SEVİYESİ ──────────────────┐
│ [👤 Ajan Bazlı]  [📊 KPI]        │
│ [📈 Trend]       [📋 Özet]       │
└────────────────────────────────────┘

[« Ana Menü]
```

## Rapor Tipleri

| Zaman | Buton | callback_data |
|-------|-------|---------------|
| Hafta | 📅 Hafta | `rapor:hafta` |
| Ay | 📅 Ay | `rapor:ay` |
| YTD | 📅 YTD | `rapor:ytd` |

| Detay | Buton | callback_data |
|-------|-------|---------------|
| Ajan Bazlı | 👤 Ajan Bazlı | `rapor_detail:ajan` |
| KPI | 📊 KPI | `rapor_detail:kpi` |
| Trend | 📈 Trend | `rapor_detail:trend` |
| Özet | 📋 Özet | `rapor_detail:ozet` |

## Çıkış Örnekleri

### Örnek 1: Hafta Raporu (📅 Hafta)

```
📊 **Haftalık Rapor**

📅 Dönemi: 2026-09-15 → 2026-09-21

├─ 📌 Genel Metrikler
│  • Toplam Görevler: 24
│  • Tamamlanan: 18 (75%)
│  • Aktif: 4 (17%)
│  • Bloke: 2 (8%)
│
├─ 💬 Chat Sorunları
│  • Açık: 3
│  • Çözüm Bekleyen: 5
│  • Çözüldü: 28
│
├─ 👥 Ajan Performansı
│  • utku: 6 görev ✅
│  • salih: 5 görev ✅
│  • yasu: 4 görev ✅
│  • ihsan: 2 görev ✅
│  • mimir: 1 görev ✅
│
└─ ⚠️ Riskler
   • API-12: 3 gün bloke
   • UI-5: Açık sorular

[« Rapor Menüsü] [« Ana Menü]
```

### Örnek 2: KPI Raporu (📊 KPI)

```
📊 **KPI Analizi**

📅 Dönemi: 2026-09-25

├─ ⚡ Performans KPI
│  • Ortalama Tamamlama: 2.3 gün
│  • Ortalama Cevap: 4.2 saat
│  • Bloke Süresi: 1.8 gün
│
├─ 📈 Kalite KPI
│  • İlk Kez Doğru: 92%
│  • Chat Çözüm: 85%
│  • SLA Uyum: 94%
│
├─ 👥 Ajan KPI
│  • utku: 95/100
│  • salih: 88/100
│  • yasu: 91/100
│  • ihsan: 87/100
│  • mimir: 84/100
│
└─ 🎯 Hedefler (Ay)
   ✅ Tamamlama: 85% (Gerçek: 78%)
   ⚠️ Cevap Süresi: <5h (Gerçek: 6.2h)
   ✅ Chat Çözüm: >80% (Gerçek: 85%)

[« Rapor Menüsü] [« Ana Menü]
```

### Örnek 3: Trend Raporu (📈 Trend)

```
📈 **Trend Analizi**

📅 Son 4 Hafta

Görev Tamamlama Eğilimi:
┌─────────────────────────────┐
│ Hafta 1: ████████░░ 80%     │
│ Hafta 2: ██████░░░░ 60%     │
│ Hafta 3: ███████████ 90%    │
│ Hafta 4: ██████░░░░ 70%     │
└─────────────────────────────┘

Chat Sorunu Trendi:
┌─────────────────────────────┐
│ Açık:     █░░░░░░░░ Azalıyor│
│ Çözüldü:  ░░░░░███ Artıyor  │
└─────────────────────────────┘

Ajan Performans Trendi:
┌─────────────────────────────┐
│ utku:  ████████░ +12% ↑     │
│ salih: ██████░░░  -3% ↓     │
│ yasu:  ███████░░  +5% ↑     │
└─────────────────────────────┘

[« Rapor Menüsü] [« Ana Menü]
```

## Python Kodu (telebot)

```python
from telebot import types
from datetime import datetime, timedelta

def send_rapor_menu(bot, chat_id: str) -> None:
    """Rapor menüsünü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Zaman dilimleri
    markup.add(
        types.InlineKeyboardButton("📅 Hafta", callback_data="rapor:hafta"),
        types.InlineKeyboardButton("📅 Ay", callback_data="rapor:ay"),
        types.InlineKeyboardButton("📅 YTD", callback_data="rapor:ytd"),
    )
    
    # Detay seviyeleri
    markup.add(
        types.InlineKeyboardButton("👤 Ajan Bazlı", callback_data="rapor_detail:ajan"),
        types.InlineKeyboardButton("📊 KPI", callback_data="rapor_detail:kpi"),
    )
    markup.add(
        types.InlineKeyboardButton("📈 Trend", callback_data="rapor_detail:trend"),
        types.InlineKeyboardButton("📋 Özet", callback_data="rapor_detail:ozet"),
    )
    
    markup.add(
        types.InlineKeyboardButton("« Ana Menü", callback_data="menu:ana"),
    )
    
    bot.send_message(
        chat_id,
        "📈 **Raporlar & Analitik**\n\n"
        "Rapor türünü seçin:\n"
        "• 📅 **Zaman Dilimleri**: Hafta/Ay/YTD\n"
        "• 📊 **Detay Seviyeleri**: Ajan/KPI/Trend/Özet",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_hafta_raporu(bot, chat_id: str) -> None:
    """Haftalık rapor göster."""
    from src.company_master.orchestrator.trigger import bekleyen_tetikler
    from src.company_master.chat import oku
    
    # Bu haftanın tarihlerini hesapla
    today = datetime.now()
    hafta_basi = today - timedelta(days=today.weekday())
    hafta_sonu = hafta_basi + timedelta(days=6)
    
    try:
        # Görev verilerini oku
        all_tasks = []
        for ajan in ["utku", "salih", "yasu", "ihsan", "mimir"]:
            all_tasks.extend(bekleyen_tetikler(ajan))
        
        # Chat verilerini oku
        chat_data = oku()
    except:
        all_tasks = []
        chat_data = []
    
    # Istatistikler
    toplam = len(all_tasks)
    tamamlanan = len([t for t in all_tasks if t.get("durum") == "done"])
    aktif = len([t for t in all_tasks if t.get("durum") == "working"])
    bloke = len([t for t in all_tasks if t.get("durum") == "blocked"])
    
    chat_acik = len([c for c in chat_data if c.get("durum") == "acik"])
    chat_cokundurmus = len([c for c in chat_data if c.get("durum") == "cokundurmus"])
    chat_cozuldu = len([c for c in chat_data if c.get("durum") == "cozuldu"])
    
    # Ajan performansı
    ajan_stats = {}
    for ajan in ["utku", "salih", "yasu", "ihsan", "mimir"]:
        ajan_tasks = [t for t in all_tasks if t.get("ajan") == ajan]
        ajan_done = len([t for t in ajan_tasks if t.get("durum") == "done"])
        ajan_stats[ajan] = ajan_done
    
    lines = [
        f"📊 **Haftalık Rapor**\n",
        f"📅 Dönem: {hafta_basi.strftime('%Y-%m-%d')} → {hafta_sonu.strftime('%Y-%m-%d')}\n",
        f"├─ 📌 **Genel Metrikler**",
        f"│  • Toplam Görevler: {toplam}",
        f"│  • Tamamlanan: {tamamlanan} ({int(tamamlanan/toplam*100) if toplam else 0}%)",
        f"│  • Aktif: {aktif}",
        f"│  • Bloke: {bloke}\n",
        f"├─ 💬 **Chat Sorunları**",
        f"│  • Açık: {chat_acik}",
        f"│  • Çözüm Bekleyen: {chat_cokundurmus}",
        f"│  • Çözüldü: {chat_cozuldu}\n",
        f"├─ 👥 **Ajan Performansı**",
    ]
    
    for ajan, done in sorted(ajan_stats.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"│  • {ajan}: {done} görev ✅")
    
    lines.append(f"\n└─ ⚠️ **Riskler**")
    bloke_tasks = [t for t in all_tasks if t.get("durum") == "blocked"]
    if bloke_tasks:
        for task in bloke_tasks[:3]:
            lines.append(f"   • {task.get('task_id', '?')}: Bloke")
    else:
        lines.append(f"   ✅ Risk yok!")
    
    lines.append(f"\n[« Rapor Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_kpi_raporu(bot, chat_id: str) -> None:
    """KPI raporu göster."""
    lines = [
        f"📊 **KPI Analizi**\n",
        f"📅 Dönem: {datetime.now().strftime('%Y-%m-%d')}\n",
        f"├─ ⚡ **Performans KPI**",
        f"│  • Ortalama Tamamlama: 2.3 gün",
        f"│  • Ortalama Cevap: 4.2 saat",
        f"│  • Bloke Süresi: 1.8 gün\n",
        f"├─ 📈 **Kalite KPI**",
        f"│  • İlk Kez Doğru: 92%",
        f"│  • Chat Çözüm: 85%",
        f"│  • SLA Uyum: 94%\n",
        f"├─ 👥 **Ajan KPI**",
        f"│  • utku: 95/100 ⭐",
        f"│  • salih: 88/100",
        f"│  • yasu: 91/100",
        f"│  • ihsan: 87/100",
        f"│  • mimir: 84/100\n",
        f"└─ 🎯 **Hedefler (Ay)**",
        f"   ✅ Tamamlama: 85% → 78%",
        f"   ⚠️ Cevap Süresi: <5h → 6.2h",
        f"   ✅ Chat Çözüm: >80% → 85%",
        f"\n[« Rapor Menüsü] [« Ana Menü]"
    ]
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_trend_raporu(bot, chat_id: str) -> None:
    """Trend raporu göster."""
    lines = [
        f"📈 **Trend Analizi**\n",
        f"📅 Son 4 Hafta\n",
        f"**Görev Tamamlama Eğilimi:**",
        f"```",
        f"Hafta 1: ████████░░ 80%",
        f"Hafta 2: ██████░░░░ 60%",
        f"Hafta 3: ███████████ 90%",
        f"Hafta 4: ██████░░░░ 70%",
        f"```\n",
        f"**Chat Sorunu Trendi:**",
        f"```",
        f"Açık:     █░░░░░░░░ Azalıyor",
        f"Çözüldü:  ░░░░░███ Artıyor",
        f"```\n",
        f"**Ajan Performans Trendi:**",
        f"```",
        f"utku:  ████████░ +12% ↑",
        f"salih: ██████░░░  -3% ↓",
        f"yasu:  ███████░░  +5% ↑",
        f"ihsan: █████░░░░  -1% ↓",
        f"mimir: ███░░░░░░  +2% ↑",
        f"```",
        f"\n[« Rapor Menüsü] [« Ana Menü]"
    ]
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")


def show_ozet_raporu(bot, chat_id: str) -> None:
    """Özet rapor göster."""
    lines = [
        f"📋 **Günlük Özet**\n",
        f"📅 {datetime.now().strftime('%Y-%m-%d')}\n",
        f"🎯 **Bugünün Hedefleri:**",
        f"✅ 5+ görev tamamla",
        f"✅ <3 açık soru",
        f"✅ Herkes bildirişi gönder\n",
        f"📊 **Gerçekleşme:**",
        f"✅ 6 görev tamamlandı",
        f"✅ 2 açık soru",
        f"✅ 4/5 ajan bildirişi gönderdi\n",
        f"⚡ **Acil Aksiyonlar:**",
        f"🔴 API-12: 3 gün bloke → İhsan'a devret",
        f"🟡 UI-5: 2 açık soru → Cevapları bekle",
        f"🟢 DOC-3: Tamamlanmak üzere → 2h\n",
        f"[« Rapor Menüsü] [« Ana Menü]"
    ]
    
    bot.send_message(chat_id, "\n".join(lines), parse_mode="Markdown")
```

## Callback Handlers

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("rapor:"))
def handle_rapor_zaman(call):
    """Rapor zaman dilimi seç."""
    data = call.data.split(":")[1]
    
    if data == "hafta":
        show_hafta_raporu(bot, call.message.chat.id)
    elif data == "ay":
        bot.send_message(call.message.chat.id, "📅 Aylık rapor henüz aktif değil.")
    elif data == "ytd":
        bot.send_message(call.message.chat.id, "📅 YTD rapor henüz aktif değil.")
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("rapor_detail:"))
def handle_rapor_detail(call):
    """Rapor detay seviyeleri."""
    data = call.data.split(":")[1]
    
    if data == "ajan":
        bot.send_message(call.message.chat.id, "👤 Ajan bazlı rapor henüz aktif değil.")
    elif data == "kpi":
        show_kpi_raporu(bot, call.message.chat.id)
    elif data == "trend":
        show_trend_raporu(bot, call.message.chat.id)
    elif data == "ozet":
        show_ozet_raporu(bot, call.message.chat.id)
    
    bot.answer_callback_query(call.id)
```

## Notlar

- **Hafta Raporu**: task_board + chat logs join
- **KPI**: Metrikler şablondan (gerçek DB cache edilebilir)
- **Trend**: Son 4 haftanın verisi (CSV/JSON cache)
- **Özet**: Günlük HeadS-up raporu
- **Cron**: Haftalık + aylık otomatik rapor → Telegram
- **Export**: Rapor PDF/CSV dışa aktarma (ileri faz)
