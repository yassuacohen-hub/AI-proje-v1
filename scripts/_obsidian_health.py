# -*- coding: utf-8 -*-
"""Obsidian vault saglik kontrolu"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    from wiki_automation.wiki_lint import run_lint
    
    print("=== Obsidian Vault Saglik Kontrolu ===\n")
    
    result = run_lint()
    
    print(f"Sayfa sayisi:       {result['pages']}")
    print(f"Hub sayisi:         {result['hubs']}")
    print(f"Orphan dosyalar:    {result['orphans']}")
    print(f"Kirik linkler:      {result['broken_links']}")
    print(f"Frontmatter eksik:  {result['frontmatter_missing']}")
    print(f"Bayat sayfalar:     {result['stale']}")
    print(f"Celiskiler:         {result['contradictions']}")
    
    # Kritik sorun var mi?
    issues = []
    if result['orphans'] > 0:
        issues.append(f"{result['orphans']} orphan dosya")
    if result['broken_links'] > 0:
        issues.append(f"{result['broken_links']} kirik link")
    if result['frontmatter_missing'] > 0:
        issues.append(f"{result['frontmatter_missing']} frontmatter eksik")
    
    if issues:
        print(f"\n⚠️  KRITIK SORUNLAR: {', '.join(issues)}")
        return 1
    else:
        print("\n✓ Vault saglikli")
        return 0

if __name__ == "__main__":
    sys.exit(main())
