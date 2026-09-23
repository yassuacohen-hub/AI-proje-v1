#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D-195 Direct Groq API test — validates NineRouter + Groq free tier.
No browser needed, just API connectivity.
"""

import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from company_master.ai_chat import sohbet, Mesaj, model_zinciri

def test_groq_api():
    """Test Groq API connection via NineRouter."""
    
    print("=" * 60)
    print("D-195: Groq Model Zinciri Live Test")
    print("=" * 60)
    
    # 1. Check model chain
    models = model_zinciri()
    print(f"\n✅ Model zinciri yüklendi:")
    for i, m in enumerate(models, 1):
        print(f"   {i}. {m}")
    
    # 2. Test with mock admin token
    admin_token = "test-token-d195"
    
    # 3. Create test messages
    mesajlar = [
        Mesaj("user", "Merhaba! Sen kim?")
    ]
    
    print(f"\n📝 Test mesajı: '{mesajlar[-1].icerik}'")
    print(f"🔐 Admin token: {admin_token[:15]}...")
    
    # 4. Call sohbet() with tracking
    print(f"\n🚀 Groq API'ye çağrı yapılıyor...")
    errors = []
    
    def track_error(model, error_msg):
        """Track fallback errors."""
        full_msg = f"{model}: {error_msg}"
        errors.append(full_msg)
        print(f"   ⚠️  {full_msg}")
    
    try:
        yanit, used_model = sohbet(
            mesajlar,
            admin_token,
            modeller=models,
            hata_kaydi=track_error
        )
        
        print(f"\n✅ Yanıt alındı!")
        print(f"📋 Kullanılan model: {used_model}")
        print(f"💬 Yanıt ({len(yanit)} karakter):")
        print(f"   {yanit[:200]}{'...' if len(yanit) > 200 else ''}")
        
        # Validate response
        if not yanit or not yanit.strip():
            print("\n❌ HATA: Boş yanıt")
            return False
        
        # Validate model
        if "groq/" not in used_model:
            print(f"\n⚠️  UYARI: Groq modeli kullanılmadı: {used_model}")
            print(f"   Fallback modeller denendi: {errors}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ TEST BAŞARILI: Groq modeli aktif ve çalışıyor")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print(f"\nFallback hatalar:")
        for err in errors:
            print(f"   - {err}")
        print("\n" + "=" * 60)
        print("❌ TEST BAŞARISIZ")
        print("=" * 60)
        return False

if __name__ == "__main__":
    try:
        success = test_groq_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Kültür hatası: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)
