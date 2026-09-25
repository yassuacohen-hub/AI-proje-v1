#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent kaydi automation — her ajan icin unique mock chat_id ata.
Telegram bot uzerinden `/register_admin ajan_adi chat_id` komutu simule et.
"""

import json
import sys
import requests
from pathlib import Path

# Windows cp1254 encoding sorunu cozumü
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bot token — telegram_bot.py'den alınan
BOT_TOKEN = "7693886476:AAHYHp9tP34mwbvf8gRvRLgJvM4HkHxJjzM"
OWNER_CHAT_ID = "801855376"  # Sahip (sen)

# Her ajana farklı, geçerli Telegram chat_id'si ata
# Production'da, her ajan kendi Telegram account'ından /register çalıştıracak
# Test'te, sahip olarak her ajana mock ID ata
AGENTS = {
    "Utku": "801855376",      # Utku — sahibin chat_id (test için)
    "Yasu": "801855376",      # Yasu — sahibin chat_id (test için)
    "Ihsan": "801855376",     # İhsan — sahibin chat_id (test için)
    "Salih": "801855376",     # Salih — sahibin chat_id (test için)
    "Mirmir": "801855376",    # Mimir — sahibin chat_id (test için)
    "Orkestrator": "801855376", # Orkestrator — sahibin chat_id (test için)
    "Kahin": "801855376"      # KAHİN — sahibin chat_id (test için)
}

def register_agent_direct(ajan_adi: str, chat_id: str) -> bool:
    """
    Agent chat_id'sini agent_chats.json'a doğrudan yaz.
    (Telegram bot'a komut göndermek yerine, JSON'u doğrudan güncelle)
    """
    try:
        agent_chats_path = Path(__file__).parent / "data" / "orchestrator" / "agent_chats.json"
        agent_chats_path.parent.mkdir(parents=True, exist_ok=True)
        
        if agent_chats_path.exists():
            with open(agent_chats_path, encoding="utf-8") as f:
                agent_chats = json.load(f)
        else:
            agent_chats = {}
        
        agent_chats[ajan_adi] = str(chat_id)
        
        with open(agent_chats_path, "w", encoding="utf-8") as f:
            json.dump(agent_chats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {ajan_adi:15} → chat_id: {chat_id}")
        return True
    
    except Exception as e:
        print(f"❌ {ajan_adi}: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("AGENT CHAT ID KAYIT AUTOMATION")
    print("="*70 + "\n")
    
    print("Test ortamı: Tüm ajanlar sahibin chat_id'sini (801855376) kullanıyor.")
    print("(Production'da her ajan kendi Telegram hesabından /register çalıştıracak)\n")
    
    success_count = 0
    for ajan_adi, chat_id in AGENTS.items():
        if register_agent_direct(ajan_adi, chat_id):
            success_count += 1
    
    print(f"\n{success_count}/{len(AGENTS)} ajan kaydedildi.\n")
    
    # Kaydedilen ajanları göster
    agent_chats_path = Path(__file__).parent / "data" / "orchestrator" / "agent_chats.json"
    with open(agent_chats_path, encoding="utf-8") as f:
        agent_chats = json.load(f)
    
    print("Kaydedilen ajanlar:")
    print(json.dumps(agent_chats, ensure_ascii=False, indent=2))
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
