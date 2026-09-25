# D-216: Telegram Menü — 📊 PANO MENÜSÜ

## Görüntü

```
╔═════════════════════════════════╗
║  📊 Pano Menüsü                ║
╚═════════════════════════════════╝

┌─ DURUM FİLTRESİ ──────────────────┐
│ [✅ Tamamlandı]  [✔️ Aktif]       │
│ [🔴 Bloke]       [📋 Plan]        │
│ [🔍 Tümü]                          │
└────────────────────────────────────┘

┌─ SORGU ───────────────────────────┐
│ [👤 Ajan Ara]  [🏷️ Tag Ara]      │
└────────────────────────────────────┘

[« Ana Menü]
```

## Durum Tanımları

| Durum | Buton | callback_data | Anlamı |
|-------|-------|---------------|--------|
| Tamamlandı | ✅ Tamamlandı | `pano:done` | Kapalı görevler |
| Aktif | ✔️ Aktif | `pano:active` | Devam eden görevler |
| Bloke | 🔴 Bloke | `pano:blocked` | Beklenen görevler |
| Plan | 📋 Plan | `pano:plan` | Henüz başlamayan görevler |
| Tümü | 🔍 Tümü | `pano:all` | Tüm görevler |
| Ajan Ara | 👤 Ajan Ara | `pano:ajan_input` | Prompt: ajan adı sor |
| Tag Ara | 🏷️ Tag Ara | `pano:tag_input` | Prompt: tag sor |

## Çıkış Örneği (✅ Tamamlandı)

```
✅ Tamamlandı Görevler (12)

📌 Hafta: 2026-09-15 → 2026-09-21

1. API-15 [utku]
   Başlık: "Token refresh optimize"
   Bitiş: 2026-09-24
   
2. UI-8 [salih]
   Başlık: "Dark theme ekle"
   Bitiş: 2026-09-23
   
3. DOC-4 [yasu]
   Başlık: "API docs güncelleştir"
   Bitiş: 2026-09-22

... (9 daha)

[« Pano Menüsü] [« Ana Menü]
```

## Python Kodu (telebot)

```python
from telebot import types

def send_pano_menu(bot, chat_id: str) -> None:
    """Pano menüsünü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Durum filtreleri
    markup.add(
        types.InlineKeyboardButton("✅ Tamamlandı", callback_data="pano:done"),
        types.InlineKeyboardButton("✔️ Aktif", callback_data="pano:active"),
    )
    markup.add(
        types.InlineKeyboardButton("🔴 Bloke", callback_data="pano:blocked"),
        types.InlineKeyboardButton("📋 Plan", callback_data="pano:plan"),
    )
    markup.add(
        types.InlineKeyboardButton("🔍 Tümü", callback_data="pano:all"),
    )
    
    # Sorgu butonları
    markup.add(
        types.InlineKeyboardButton("👤 Ajan Ara", callback_data="pano:ajan_input"),
        types.InlineKeyboardButton("🏷️ Tag Ara", callback_data="pano:tag_input"),
    )
    
    # Geri dön
    markup.add(
        types.InlineKeyboardButton("« Ana Menü", callback_data="menu:ana"),
    )
    
    bot.send_message(
        chat_id,
        "📊 **Pano Menüsü**\n\n"
        "Görevleri durum veya ajana göre filtrele.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_pano_status(bot, chat_id: str, status: str) -> None:
    """Pano görevlerini durum bazında göster."""
    from src.company_master.orchestrator.trigger import tetik_ekle, bekleyen_tetikler
    from pathlib import Path
    
    # DB'den verileri oku
    try:
        tasks = bekleyen_tetikler("*")  # Tüm ajanları al
    except:
        tasks = []
    
    # Duruma göre filtrele
    status_map = {
        "done": "done",
        "active": "working",
        "blocked": "blocked",
        "plan": "plan",
        "all": None  # Tüm durumlar
    }
    
    filtered = tasks
    if status != "all":
        filtered = [t for t in tasks if t.get("durum") == status_map[status]]
    
    # Formatla
    lines = [f"**{status.upper()} Görevler ({len(filtered)})**\n"]
    
    for i, task in enumerate(filtered[:10], 1):  # İlk 10'u göster
        task_id = task.get("task_id", "?")
        ajan = task.get("ajan", "?")
        baslik = task.get("talimat", "")[:50]
        lines.append(f"{i}. {task_id} [{ajan}]\n   {baslik}")
    
    if len(filtered) > 10:
        lines.append(f"\n... (+{len(filtered) - 10} daha)")
    
    lines.append("\n[« Pano Menüsü] [« Ana Menü]")
    
    bot.send_message(
        chat_id,
        "\n\n".join(lines),
        parse_mode="Markdown"
    )


def handle_ajan_input(bot, chat_id: str) -> None:
    """Ajan adı sorgusu için input iste."""
    msg = bot.send_message(
        chat_id,
        "👤 **Ajan adını girin** (örn: utku, salih, yasu, ihsan, mimir)"
    )
    bot.register_next_step_handler(msg, lambda m: process_ajan_filter(bot, chat_id, m))


def process_ajan_filter(bot, chat_id: str, message) -> None:
    """Ajan filtresi uygula."""
    ajan = message.text.strip().lower()
    
    from src.company_master.orchestrator.trigger import bekleyen_tetikler
    try:
        tasks = bekleyen_tetikler(ajan)
    except:
        tasks = []
    
    lines = [f"**{ajan.upper()} İçin Görevler ({len(tasks)})**\n"]
    for i, task in enumerate(tasks[:10], 1):
        task_id = task.get("task_id", "?")
        durum = task.get("durum", "?")
        lines.append(f"{i}. {task_id} [{durum}]")
    
    if len(tasks) > 10:
        lines.append(f"... (+{len(tasks) - 10} daha)")
    
    lines.append("\n[« Pano Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")
```

## Callback Handler

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("pano:"))
def handle_pano_menu(call):
    """Pano menü butonlarını işle."""
    data = call.data.split(":")[1]
    
    if data in ["done", "active", "blocked", "plan", "all"]:
        show_pano_status(bot, call.message.chat.id, data)
    elif data == "ajan_input":
        handle_ajan_input(bot, call.message.chat.id)
    elif data == "tag_input":
        bot.send_message(call.message.chat.id, "🏷️ Tag arama henüz aktif değil.")
    elif data == "ana":
        send_ana_menu(bot, call.message.chat.id)
    
    bot.answer_callback_query(call.id)
```

## Notlar

- **Pagination**: 10 görev göster, "... (+X daha)"
- **DB Bağlantı**: `orchestrator/trigger.py` → `bekleyen_tetikler()`
- **Geri dön**: `[« Pano Menüsü]` → pano menüyü tekrar gönder
- **Ana menü**: `[« Ana Menü]` → ana menüye dön
