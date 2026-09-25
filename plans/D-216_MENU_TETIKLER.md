# D-216: Telegram Menü — ✉️ TETIKLER MENÜSÜ

## Görüntü

```
╔═════════════════════════════════╗
║  ✉️ Tetikler (Posta Kutusu)     ║
╚═════════════════════════════════╝

┌─ AJAN SEÇ ────────────────────────┐
│ [👨 Utku]    [👨 Salih]           │
│ [👨 Yasu]    [👨 İhsan]           │
│ [👨 Mimir]   [🔍 Tümü]            │
└────────────────────────────────────┘

[« Ana Menü]
```

## Ajan Tanımları

| Ajan | Buton | callback_data |
|------|-------|---------------|
| Utku | 👨 Utku | `tetikler:utku` |
| Salih | 👨 Salih | `tetikler:salih` |
| Yasu | 👨 Yasu | `tetikler:yasu` |
| İhsan | 👨 İhsan | `tetikler:ihsan` |
| Mimir | 👨 Mimir | `tetikler:mimir` |
| Tümü | 🔍 Tümü | `tetikler:all` |

## Çıkış Örneği (utku)

```
📬 Utku'nun Bekleyen Tetikleri (2)

📌 Posta Kutusu | 2026-09-25

📬 T-1 (API-12)
   Talimat: "API v2 uyumlu hale getir"
   ⚠️ 2 açık soru (chat_acik_sorular)
   📅 Başlangıç: 2026-09-25 14:00
   
📬 T-2 (UI-3)
   Talimat: "Dark theme ekle"
   ✅ 0 açık soru
   📅 Başlangıç: 2026-09-25 13:00

[« Tetikler Menüsü] [« Ana Menü]
```

## Python Kodu (telebot)

```python
from telebot import types

def send_tetikler_menu(bot, chat_id: str) -> None:
    """Tetikler menüsünü gönder."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Ajan butonları
    ajanlar = [
        ("👨 Utku", "tetikler:utku"),
        ("👨 Salih", "tetikler:salih"),
        ("👨 Yasu", "tetikler:yasu"),
        ("👨 İhsan", "tetikler:ihsan"),
        ("👨 Mimir", "tetikler:mimir"),
        ("🔍 Tümü", "tetikler:all"),
    ]
    
    for label, callback in ajanlar:
        markup.add(types.InlineKeyboardButton(label, callback_data=callback))
    
    # Geri dön
    markup.add(
        types.InlineKeyboardButton("« Ana Menü", callback_data="menu:ana"),
    )
    
    bot.send_message(
        chat_id,
        "✉️ **Tetikler Menüsü**\n\n"
        "Ajanın posta kutusunu görmek için ajan seçin.\n\n"
        "💡 Tetikler = Bekleyen görevler\n"
        "⚠️ Eğer açık sorular varsa, cevaplar alınana kadar görev başlamaz.",
        reply_markup=markup,
        parse_mode="Markdown"
    )


def show_tetikler_ajan(bot, chat_id: str, ajan: str) -> None:
    """Ajanın tetiklerini göster."""
    from src.company_master.orchestrator.trigger import bekleyen_tetikler
    
    # DB'den tetikleri oku
    try:
        tetikler = bekleyen_tetikler(ajan)
    except:
        tetikler = []
    
    # Formatla
    if not tetikler:
        msg = f"✅ **{ajan.upper()} İçin Tetik Yok!**\n\n" \
              "Tüm görevler tamamlandı veya devam ediyor.\n\n" \
              "[« Tetikler Menüsü] [« Ana Menü]"
        bot.send_message(chat_id, msg, parse_mode="Markdown")
        return
    
    lines = [f"📬 **{ajan.upper()} Posta Kutusu ({len(tetikler)})**\n"]
    
    for i, tetik in enumerate(tetikler[:10], 1):
        task_id = tetik.get("task_id", "?")
        talimat = tetik.get("talimat", "")[:40]
        acik_sorular = tetik.get("chat_acik_sorular", 0)
        
        # Sorun durumu emojisi
        if acik_sorular > 0:
            emoji_sorun = f"⚠️ {acik_sorular} açık soru"
        else:
            emoji_sorun = "✅ Sorular çözüldü"
        
        lines.append(
            f"{i}. 📬 {task_id}\n"
            f"   Talimat: {talimat}\n"
            f"   {emoji_sorun}"
        )
    
    if len(tetikler) > 10:
        lines.append(f"\n... (+{len(tetikler) - 10} daha)")
    
    lines.append("\n[« Tetikler Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")


def show_tetikler_all(bot, chat_id: str) -> None:
    """Tüm ajanların tetiklerini özetli göster."""
    from src.company_master.orchestrator.trigger import bekleyen_tetikler
    
    ajanlar = ["utku", "salih", "yasu", "ihsan", "mimir"]
    
    lines = ["📬 **Tüm Tetikler (Özet)**\n"]
    
    toplam = 0
    for ajan in ajanlar:
        try:
            tetikler = bekleyen_tetikler(ajan)
        except:
            tetikler = []
        
        if tetikler:
            acik_toplam = sum(t.get("chat_acik_sorular", 0) for t in tetikler)
            lines.append(
                f"👨 **{ajan.upper()}**: {len(tetikler)} tetik "
                f"({acik_toplam} açık soru)"
            )
            toplam += len(tetikler)
    
    if toplam == 0:
        lines.append("✅ Tüm ajanlar için tetik yok!")
    else:
        lines.append(f"\n**Toplam: {toplam} tetik**")
    
    lines.append("\n[« Tetikler Menüsü] [« Ana Menü]")
    
    bot.send_message(chat_id, "\n\n".join(lines), parse_mode="Markdown")
```

## Callback Handler

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("tetikler:"))
def handle_tetikler_menu(call):
    """Tetikler menü butonlarını işle."""
    data = call.data.split(":")[1]
    
    if data == "all":
        show_tetikler_all(bot, call.message.chat.id)
    else:
        # ajan = data (utku, salih, yasu, ihsan, mimir)
        show_tetikler_ajan(bot, call.message.chat.id, data)
    
    bot.answer_callback_query(call.id)
```

## İş Akışı Tanımı (D-211 Entegrasyonu)

### Tetik Kaydı Yapısı

```python
{
    "task_id": "API-12",
    "ajan": "utku",
    "talimat": "API v2 uyumlu hale getir",
    "durum": "bekliyor",
    "chat_acik_sorular": 2,  # ← D-211: Açık soru sayısı
    "tarih_olustur": "2026-09-25T14:00:00Z",
    "tarih_basla": None,
    "cmd_basla_kilit": False,  # ← D-211: Başlamadan önce chat kontrol
    "cmd_teslim_kilit": False  # ← D-211: Teslimden önce chat kontrol
}
```

### Kontrol Mekanizması

1. **Görev Başlangıcı (`cmd_basla`)**:
   - Tetik kontrol: `chat_acik_sorular > 0` mı?
   - Evet → Hata: "Açık sorular var, önce çözün"
   - Hayır → Başla, `durum` = "working"

2. **Görev Teslimi (`cmd_teslim`)**:
   - Tetik kontrol: `chat_acik_sorular > 0` mı?
   - Evet → Hata: "Açık sorular var, önce çözün"
   - Hayır → Teslim, `durum` = "done"

3. **Chat Sorusu Kapatıldığında**:
   - `ajan-chat.jsonl`: `durum` = "cozuldu"
   - `bekleyen_tetikler()`: `chat_acik_sorular` otomatik azalır
   - Tetik otomatik güncellenir

## Notlar

- **Posta Kutusu**: Bekleyen tetikler listesi
- **Açık Sorular**: D-211 tarafından otomatik kontrol
- **Kilit Sistemi**: Chat + Tetik senkronizasyonu
- **Pagination**: 10 tetik göster
- **Emoji**: ⚠️ (sorular var), ✅ (sorular çözüldü)
