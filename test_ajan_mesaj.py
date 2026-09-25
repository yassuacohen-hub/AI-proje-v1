#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Ajan kayıt → Mesaj gönder → Kontrol
Simüle eder: /register Utku → Targeted mesaj gönder → agent_chats.json kontrol
"""

import json
import sys
from pathlib import Path

# Setup path
_base = Path(__file__).parent / "src"
_company = _base / "company_master"
if str(_base) not in sys.path:
    sys.path.insert(0, str(_base))
if str(_company) not in sys.path:
    sys.path.insert(0, str(_company))

def test_agent_registration():
    """1. Ajan kaydı simülasyonu"""
    print("=" * 60)
    print("TEST 1: Ajan Kayıt Simulasyonu (/register Utku)")
    print("=" * 60)
    
    agent_chats_path = Path(__file__).parent / "data" / "orchestrator" / "agent_chats.json"
    agent_chats_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Simüle: Utku kaydolsun (chat_id = 123456789)
    agent_chats = {
        "Utku": "123456789",
        "Yasu": "987654321",
        "Ihsan": "555666777",
    }
    
    with open(agent_chats_path, "w", encoding="utf-8") as f:
        json.dump(agent_chats, f, ensure_ascii=False, indent=2)
    
    print("OK Agent chats kaydedildi: " + str(agent_chats_path))
    print("   Kayitli ajanlar: " + str(list(agent_chats.keys())))
    return agent_chats

def test_agent_chats_file():
    """2. agent_chats.json dosyası kontrol"""
    print("\n" + "=" * 60)
    print("TEST 2: agent_chats.json Okunabilirlik Kontrol")
    print("=" * 60)
    
    agent_chats_path = Path(__file__).parent / "data" / "orchestrator" / "agent_chats.json"
    
    if not agent_chats_path.exists():
        print("HATA: agent_chats.json bulunamadi!")
        return None
    
    with open(agent_chats_path, "r", encoding="utf-8") as f:
        agent_chats = json.load(f)
    
    print("OK agent_chats.json okundu")
    print("   Dosya: " + str(agent_chats_path))
    print("   Kayitli ajanlar:")
    for ajan, chat_id in agent_chats.items():
        print("     - " + ajan + " => chat_id: " + str(chat_id))
    
    return agent_chats

def test_message_sending(agent_chats):
    """3. Mesaj gönderme fonksiyonu testi"""
    print("\n" + "=" * 60)
    print("TEST 3: Mesaj Gonder Simulasyonu (Targeted)")
    print("=" * 60)
    
    try:
        from telegram_bot import send_agent_message
        
        # Utku'ya test mesajı gönder
        test_ajan = "Utku"
        test_mesaj = "TEST mesaji: Gorev P7-123 tamamlandi!"
        
        print("Hedef: " + test_ajan)
        print("Mesaj: " + test_mesaj)
        print("Chat ID: " + agent_chats.get(test_ajan, "BULUNAMADI"))
        print("")
        print("send_agent_message() cagiriliyor...")
        
        # Dikkat: Bu gerçek Telegram API çağrısı yapacak!
        # Mock chat_id olduğu için hata döner ama fonksiyon calisti mu bunu test edebiliriz
        result = send_agent_message(test_ajan, test_mesaj)
        
        print("OK Fonksiyon tamamlandi: result=" + str(result))
        print("   Not: Mock chat_id olduğu icin hata donebilir - bu normal")
        
        return result
    except Exception as e:
        print("HATA: " + str(e))
        print("   Sebep: send_agent_message() cagrilirken hata olustu")
        return False

def test_workflow():
    """4. Tam workflow dokümantasyonu"""
    print("\n" + "=" * 60)
    print("TEST 4: Telegram Mesaj Workflow Akisi")
    print("=" * 60)
    print("")
    print("Sahip (KAHİN) Tarafından:")
    print("  1. Telegram Bot'ta: Mesaj -> Targeted")
    print("  2. Ajan sec: Utku")
    print("  3. Önem sec: Acil / Orta / Düşük")
    print("  4. Mesaj yaz: Örn. 'P7-123 kontrol et'")
    print("  5. Gönder")
    print("")
    print("Arka Taraf (Backend):")
    print("  1. /register komutu -> agent_chats.json'e Utku => 123456789 yazılır")
    print("  2. Targeted mesaj -> _mesaj_ajan_gonder() çagrilir")
    print("  3. send_agent_message('Utku', 'mesaj') -> Telegram Bot API")
    print("  4. Bot: chat_id=123456789 ile Utku'ya mesaj gönder")
    print("")
    print("Ajan Tarafından:")
    print("  1. Telegram Bot'ta /register Utku komutu gönder")
    print("  2. Bot: Kaydı onayla, chat_id kaydet")
    print("  3. Mesajları Telegram üzerinden al")
    print("  4. Cevap gönder")

def main():
    print("\n" + "=" * 70)
    print("AJAN TELEGRAM MESAJLASMA TESTI")
    print("=" * 70)
    
    try:
        # Test 1: Kaydı simüle et
        agent_chats = test_agent_registration()
        
        # Test 2: Dosya kontrol
        agent_chats = test_agent_chats_file()
        
        if agent_chats:
            # Test 3: Mesaj gönder
            result = test_message_sending(agent_chats)
            
            # Test 4: Workflow göster
            test_workflow()
            
            print("\n" + "=" * 70)
            print("TESTLER TAMAMLANDI")
            print("=" * 70)
            print("")
            print("Sonraki Adimlar (Manual Test):")
            print("  1. Telegram'da: /register Utku komutu gönder")
            print("  2. Bot: Kayit onaylandi mesajini al")
            print("  3. Telegram'da: Mesaj -> Targeted -> Utku -> mesaj gönder")
            print("  4. Utku: Telegram'da mesajı al")
            print("  5. Utku: Cevap gönder (opsiyonel)")
            print("")
            print("Hatalar:")
            print("  - Mock chat_id: TEST icin 123456789 kullanildigi icin gercek")
            print("    Telegram API cagrisinda hata verir (bu normal)")
            print("  - Gerçek test: Gerçek /register komutu gönder ve chat_id kontrol et")
            
    except Exception as e:
        print("\nFATAL ERROR: " + str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
