#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Admin panel production test: gorev_at.py import check.
Tests whether the Streamlit page loads without [Errno 22] error.
"""

import sys
import subprocess
from pathlib import Path

# Change to project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

def test_gorev_at_import():
    """Test: gorev_at.py imports successfully without [Errno 22] error."""
    try:
        # This is the exact import chain that admin panel uses
        from scripts.gorev_at import _orkestrator_oku
        print("✓ gorev_at.py imports successfully")
        print(f"  _orkestrator_oku callable: {callable(_orkestrator_oku)}")
        return True
    except OSError as e:
        if "Errno 22" in str(e):
            print(f"✗ [Errno 22] Import failed: {e}")
            return False
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise

def test_abrakadabra_tab_import():
    """Test: abrakadabra.py can import gorev_at without errors."""
    try:
        from web_dashboard.tabs.abrakadabra import render_abrakadabra_tab
        print("✓ abrakadabra.py imports successfully")
        print(f"  render_abrakadabra_tab callable: {callable(render_abrakadabra_tab)}")
        return True
    except Exception as e:
        print(f"✗ abrakadabra import failed: {e}")
        raise

def test_admin_panel_import():
    """Test: admin_panel.py imports successfully."""
    try:
        from web_dashboard.tabs.admin_panel import render_chat_summary
        print("✓ admin_panel.py imports successfully")
        print(f"  render_chat_summary callable: {callable(render_chat_summary)}")
        return True
    except Exception as e:
        print(f"✗ admin_panel import failed: {e}")
        raise

if __name__ == "__main__":
    print("=" * 70)
    print("ADMIN PANEL PRODUCTION TEST")
    print("=" * 70)
    
    results = []
    
    print("\n[Test 1] gorev_at.py import (core issue)")
    results.append(test_gorev_at_import())
    
    print("\n[Test 2] abrakadabra.py import chain")
    results.append(test_abrakadabra_tab_import())
    
    print("\n[Test 3] admin_panel.py import")
    results.append(test_admin_panel_import())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✓ All imports successful — admin panel should load")
        sys.exit(0)
    else:
        print("✗ Some imports failed — admin panel will crash")
        sys.exit(1)
