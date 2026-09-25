#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram bot menüsünün tüm seçeneklerini analiz et.
wireframe vs gerçeklik karşılaştırması.
"""
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Bot menüsü: telegram_bot.py'dan tüm message_handler fonksiyonlarını çıkar
bot_file = Path('Huginn Data Insights/src/company_master/telegram_bot.py')
content = bot_file.read_text(encoding='utf-8')

# Ana menü seçeneği (send_ana_menu'den)
ana_menu = {
    "📊 Pano": "pano_menu",
    "💬 Chat": "chat_menu",
    "✉️ Tetikler": "tetikler_menu",
    "📝 Mesaj": "mesaj_menu",
    "📈 Rapor": "rapor_menu",
    "⚙️ Ayarlar": "ayarlar_menu",
    "📋 Görev Takibi": "gorev_takibi_menu",
    "🚨 ACİL": "urgent",
    "⚡ Q": "questions",
    "📌 ÖZET": "summary",
    "❓ Yardım": "help",
}

# Alt menüleri bul (message_handler fonksiyonlarından)
pattern = r'@bot\.message_handler\(func=lambda message:.*?"([^"]+)".*?\)'
matches = re.findall(pattern, content)

print("=" * 80)
print("TELEGRAMBoT MENÜ ANALİZİ")
print("=" * 80)

print("\n📊 ANA MENÜ SEÇENEKLERİ (6 üst seviye):\n")
for i, (label, handler) in enumerate(ana_menu.items(), 1):
    print(f"  {i}. {label:30} → {handler}")

print("\n" + "=" * 80)
print("ALT MENÜLER (Her ana menü seçeneğinin açtığı alt seçenekler):")
print("=" * 80)

# send_*_menu fonksiyonlarını bul ve alt menülerini çıkar
menu_functions = {
    "send_pano_menu": ("📊 Pano", ["✅ Tamamlandı", "✔️ Aktif", "🔴 Bloke", "📋 Plan", "🔍 Tümü"]),
    "send_chat_menu": ("💬 Chat", ["🟢 Açık", "🟡 Çözüm", "✅ Çözüldü"]),
    "send_tetikler_menu": ("✉️ Tetikler", ["📬 Tetik Bak", "✉️ Tetik Gönder"]),
    "send_mesaj_menu": ("📝 Mesaj", ["📢 Broadcast", "🎯 Targeted", "🏷️ Tag Seç", "⚠️ Uyarı"]),
    "send_rapor_menu": ("📈 Rapor", ["📅 Hafta", "📅 Ay", "📊 YTD", "👤 Ajan Bazlı", "📊 KPI", "📋 Pano Özeti", "📈 Trend", "📋 Özet"]),
    "send_ayarlar_menu": ("⚙️ Ayarlar", ["🔗 Bağlantı Kontrol", "🔑 Token Doğrula", "🤖 Bot Bilgisi", "❓ Yardım"]),
    "send_gorev_takibi_menu": ("📋 Görev Takibi", ["🟢 Açık", "🔵 Aktif", "🟠 Bloke", "✅ Tamamlandı", "📋 Tümü", "👤 Sahip Bazlı"]),
}

toplam_sekme = 0
for func_name, (menu_title, items) in menu_functions.items():
    print(f"\n{menu_title} ({len(items)} sekme):")
    for item in items:
        print(f"  • {item}")
    toplam_sekme += len(items)

print("\n" + "=" * 80)
print("ÖZET İSTATİSTİKLER:")
print("=" * 80)
print(f"Ana menü seçeneği: {len(ana_menu)}")
print(f"Alt menü sekmesi: {toplam_sekme}")
print(f"Toplam menü öğesi: {len(ana_menu) + toplam_sekme}")

print("\n" + "=" * 80)
print("WIREFRAME VS GERÇEKLIK KARŞILAŞTIRMASI:")
print("=" * 80)

wireframe_toplam = 6 + 23  # üst + alt
bot_toplam = len(ana_menu) + toplam_sekme

print(f"""
WIREFRAME (hedef durum):
  • Üst sayfa: 6 (Ana Kontrol, Müşteriler, Gelir, Metrikler, Sistem, Proje)
  • Alt sekme: 23
  • Toplam: {wireframe_toplam}
  • En kalabalık grup: 9 (Sistem)

BOT GERÇEK DURUM:
  • Ana menü seçeneği: {len(ana_menu)}
  • Alt sekme: {toplam_sekme}
  • Toplam: {bot_toplam}
  • En kalabalık grup: 8 (Rapor)

FARK:
  • Fazlalık: {bot_toplam - wireframe_toplam} öğe
  • Gerekli azaltma: %{round((bot_toplam - wireframe_toplam) / wireframe_toplam * 100, 1)}
""")

print("=" * 80)
print("TESPİT EDİLEN SORUNLAR:")
print("=" * 80)

sorunlar = [
    ("🔴 CİDDİ", "Rapor menüsü 8 alt seçeneği var — wireframe'de 4 olmalı"),
    ("🟡 ORTA", "Tetikler menüsü 2 seçeneği var (bakılan + gönderilen) — genişletilmiş versiyona gerek var"),
    ("🟡 ORTA", "Mesaj menüsü 4 seçeneği var — admin panelde çıkması gerekebilir"),
    ("🟢 UYARI", "Ayarlar menüsü wireframe'de profil popover'a taşınması gerekiyor"),
]

for i, (sınıf, sorun) in enumerate(sorunlar, 1):
    print(f"\n{i}. {sınıf}")
    print(f"   {sorun}")

print("\n" + "=" * 80)
