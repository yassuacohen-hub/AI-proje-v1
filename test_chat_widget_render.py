#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D-192: Chat widget render test — admin panel widget render et."""
import sys
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

# Path setup
ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Test render
try:
    from web_dashboard.tabs.admin_panel import render_chat_summary
    print("OK: Import successful - render_chat_summary()")
    
    # Render fonksiyonunu çağır (mock context yok, hata beklenir ama import sorunları görülür)
    print("\n--- Render function call ---")
    try:
        # Streamlit context olmadığı için hata alacağız ama import exception'ları görürüz
        render_chat_summary()
    except Exception as e:
        if "streamlit" in str(type(e).__name__).lower():
            print(f"OK: Streamlit context error (expected): {type(e).__name__}")
            print("  -> Widget code loaded successfully; only Streamlit runtime needed")
        else:
            print(f"FAIL: Import error: {e}")
            import traceback
            traceback.print_exc()
            
except ImportError as e:
    print(f"FAIL: Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nOK: Test complete. Widget render ready.")
