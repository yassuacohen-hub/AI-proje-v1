#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRAPH-INDEX-BUILD: Tür-Bazlı Index Oluşturma (Plan C Tur 3, Seri)

1. Orphan listesi çıkar (431 baseline, backup dosyaları hariç)
2. Frontmatter/dosya adı/klasör pattern'ına göre 4 tür index oluştur
3. Her index'e ilgili orphan/az-bağlı dosyaları wikilink ile ekle
4. Ölçüm: orphan 431 → hedef ~150
"""

import sys
import io
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE_ROOT = Path('c:\\Huginn Data Projesi').resolve()
HDI_ROOT = WORKSPACE_ROOT / 'Huginn Data Insights'
# ponytail: ROOT = WORKSPACE_ROOT (resmi vault_saglik_genis.py ile aynı taban) —
# file_map anahtarları wikilink'lerle ("Huginn Data Insights/...") birebir eşleşsin diye.
ROOT = WORKSPACE_ROOT

# Worktree ve yedek dosyaları IGNORE et
IGNORE = {
    '.kilo', '.agents', '.claude', '.cursor', '.continue', '.kombai',
    '.vscode', '.pytest_cache', '.roo', '.obsidian', '.github',
    '.streamlit', '.venv', '.git', 'node_modules', '__pycache__',
    'worktree klasoru', '_ARSIV_', '_backup_', '_old', '.bak'
}

# Canonical redirect dosyaları (GRAPH-CANONICAL sonrası)
CANONICAL_BACKUP_PATTERN = re.compile(r'\.md\.backup_\d{4}-\d{2}-\d{2}$')

# Tür sınıflandırması: (klasör pattern, dosya adı pattern) → tür
TYPE_PATTERNS = {
    'teknik': {
        'klasor': ['docs', 'architecture', 'schema', 'config', 'design', 'code', 'script', 'teknik'],
        'dosya': ['architecture', 'design', 'pattern', 'guide', 'tutorial', 'config', 'schema', 'teknik']
    },
    'osint': {
        'klasor': ['osint', 'intelligence', 'research', 'investigation'],
        'dosya': ['osint', 'scraper', 'scrape', 'intelligence', 'research', 'vendor', 'company', 'kariyer']
    },
    'plan': {
        'klasor': ['plans', 'roadmap', 'sprint', 'strategy', 'gorev', 'pano'],
        'dosya': ['plan', 'roadmap', 'sprint', 'strategy', 'gorev', 'panosu', 'milestone', 'timeline']
    },
    'rapor': {
        'klasor': ['reports', 'rapor', 'audit', 'metrics', 'analysis', 'orchestrator'],
        'dosya': ['rapor', 'report', 'audit', 'analysis', 'metric', 'denetim', 'log', 'ozet']
    }
}

def scan_vault():
    """Tüm workspace'te .md dosyaları tara (worktree/yedek/dev-araç hariç) — resmi baseline ile aynı taban."""
    md_files = []
    for p in ROOT.rglob('*.md'):
        if any(part in IGNORE for part in p.parts):
            continue
        if CANONICAL_BACKUP_PATTERN.search(p.name):
            continue
        md_files.append(p)
    return sorted(md_files)

def extract_frontmatter(content):
    """YAML frontmatter çıkart."""
    if not content.startswith('---'):
        return {}
    try:
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
    except:
        pass
    return {}

def extract_refs(content):
    """Wikilink referanslarını çıkart."""
    refs = set()
    for match in re.finditer(r'\[\[([^\]]+)\]\]', content):
        target = match.group(1).split('|')[0].strip().split('#')[0].strip()
        if target:
            refs.add(target)
    return refs

def resolve_target(target, file_map, by_name):
    """Hedef dosyayı çözümle (vault_saglik_genis.py mantığı)."""
    target = target.replace('\\', '/').strip().lstrip('./')
    if not target:
        return None
    if target.lower().startswith('http://') or target.lower().startswith('https://'):
        return '__EXTERNAL__'
    
    target_md = target if target.lower().endswith('.md') else target + '.md'
    
    # Tam yol eşleşmesi
    hit = file_map.get(target_md.lower())
    if hit:
        return hit
    
    # İsim eşleşmesi
    hits = by_name.get(Path(target_md).name.lower())
    if hits:
        return hits[0]
    
    return None

def classify_file(rel_path, filename, content):
    """Dosyayı tür'e göre sınıflandır."""
    path_lower = rel_path.lower()
    name_lower = filename.lower().replace('.md', '')
    fm = extract_frontmatter(content)
    tags = fm.get('tags', []) if isinstance(fm.get('tags'), list) else []
    tags_str = ' '.join(tags).lower() if tags else ''
    
    scores = {'teknik': 0, 'osint': 0, 'plan': 0, 'rapor': 0}
    
    for tip, patterns in TYPE_PATTERNS.items():
        # Klasör pattern'i
        for pat in patterns['klasor']:
            if pat in path_lower:
                scores[tip] += 2
        # Dosya adı pattern'i
        for pat in patterns['dosya']:
            if pat in name_lower:
                scores[tip] += 3
        # Tag'ler
        if tip in tags_str:
            scores[tip] += 2
    
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return None

def build_indexes():
    """Index'leri oluştur ve dosyaları sınıflandır. Sadece HDI altındaki orphan'lar sınıflandırılır."""
    print("🔍 Vault taranıyor...")
    md_files = scan_vault()
    print(f"   Toplam .md: {len(md_files)}")
    
    # File map oluştur (WORKSPACE_ROOT-relative — wikilink'lerle birebir eşleşsin)
    file_map = {p.relative_to(ROOT).as_posix().lower(): p for p in md_files}
    by_name = defaultdict(list)
    for p in md_files:
        by_name[p.name.lower()].append(p)
    
    # Referans analiz
    print("📊 Referanslar analiz ediliyor...")
    referenced = set()
    ref_count = defaultdict(int)
    
    for p in md_files:
        try:
            content = p.read_text(encoding='utf-8-sig', errors='ignore')
            refs = extract_refs(content)
            for target in refs:
                resolved = resolve_target(target, file_map, by_name)
                if resolved and resolved != '__EXTERNAL__':
                    rel = resolved.relative_to(ROOT).as_posix().lower()
                    referenced.add(rel)
                    ref_count[rel] += 1
        except:
            pass
    
    # Orphan listesi (referans almayan) — sadece HDI kapsamlı dosyalar sınıflandırma adayı
    orphan_list = []
    classified = defaultdict(list)
    
    for p in md_files:
        rel_path = p.relative_to(ROOT).as_posix().lower()
        if rel_path not in referenced:
            try:
                content = p.read_text(encoding='utf-8-sig', errors='ignore')
                is_hdi = p.is_relative_to(HDI_ROOT) if hasattr(p, 'is_relative_to') else str(p).startswith(str(HDI_ROOT))
                tip = classify_file(rel_path, p.name, content) if is_hdi else None
                
                entry = {
                    'path': p.relative_to(HDI_ROOT).as_posix() if is_hdi else p.relative_to(ROOT).as_posix(),
                    'type': tip,
                    'ref_count': ref_count[rel_path],
                    'size': p.stat().st_size
                }
                orphan_list.append(entry)
                if tip:
                    classified[tip].append(entry)
            except:
                pass
    
    print(f"\n📈 Orphan: {len(orphan_list)} dosya")
    print(f"   Teknik: {len(classified['teknik'])}")
    print(f"   OSINT: {len(classified['osint'])}")
    print(f"   Plan: {len(classified['plan'])}")
    print(f"   Rapor: {len(classified['rapor'])}")
    
    return classified, orphan_list, md_files

def create_index_file(index_type, files, index_dir):
    """Index dosyası oluştur."""
    index_names = {
        'teknik': 'teknik_index',
        'osint': 'osint_index',
        'plan': 'plan_index',
        'rapor': 'rapor_index'
    }
    
    descriptions = {
        'teknik': 'Teknik dokümantasyon, mimari kararlar, kod yapısı, geliştirme rehberleri',
        'osint': 'Açık kaynak istihbaratı, veri toplama, araştırma, vendor analizi',
        'plan': 'Roadmap, sprint planları, görev panosu, stratejik kararlar',
        'rapor': 'Raporlar, denetim çıktıları, metrikler, analiz dokumanları'
    }
    
    index_file = index_dir / f'{index_names[index_type]}.md'
    
    # Header
    lines = [
        f'# {index_type.upper()} Index',
        '',
        f'**Tür**: {index_type.capitalize()}',
        f'**Açıklama**: {descriptions[index_type]}',
        f'**Dosya Sayısı**: {len(files)}',
        f'**Oluşturulma**: {datetime.utcnow().isoformat()}Z',
        '',
        '## Bağlı Dosyalar',
        ''
    ]
    
    # Dosyaları ekle
    for entry in sorted(files, key=lambda x: x['path']):
        # Full path (workspace-relative), uzantısız — ölçüm sistemi WORKSPACE_ROOT'tan tarar
        path = 'Huginn Data Insights/' + entry['path']
        if path.lower().endswith('.md'):
            path = path[:-3]
        lines.append(f'- [[{path}]]')
    
    content = '\n'.join(lines)
    index_file.write_text(content, encoding='utf-8')
    
    return index_file

def main():
    print("\n" + "="*60)
    print("GRAPH-INDEX-BUILD — Tür-Bazlı Index Oluşturma")
    print("="*60)
    
    # Index klasörü oluştur
    index_dir = HDI_ROOT / 'indexes'
    index_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Index klasörü: {index_dir}")

    # ponytail: idempotanlik — eski index'ler kendi linklerini referans saydırıp
    # listeyi boşaltıyordu. ÖNCE ölçümden evvel sil, temiz baseline al.
    for old in index_dir.glob('*_index.md'):
        old.unlink()
        print(f"   🗑️  Eski index silindi: {old.name}")
    
    # ÖNCE ölçüm + sınıflandırma (index'ler yokken)
    classified, orphan_list, all_files = build_indexes()
    orphan_once = len(orphan_list)
    
    print(f"\n✍️  Index dosyaları oluşturuluyor...")
    created_indexes = {}
    for tip in ['teknik', 'osint', 'plan', 'rapor']:
        if classified[tip]:
            idx_file = create_index_file(tip, classified[tip], index_dir)
            created_indexes[tip] = idx_file
            print(f"   ✅ {idx_file.name} ({len(classified[tip])} dosya)")

    # SONRA ölçüm (index'ler yazıldıktan sonra)
    print(f"\n🔁 SONRA ölçümü...")
    _, orphan_sonra_list, _ = build_indexes()
    orphan_sonra = len(orphan_sonra_list)
    print(f"\n📉 Orphan: {orphan_once} → {orphan_sonra} "
          f"(−{orphan_once - orphan_sonra}, %{100*(orphan_once-orphan_sonra)/max(orphan_once,1):.1f})")
    
    # Rapor oluştur
    rapor_file = Path('data/orchestrator/GRAPH-INDEX-BUILD_rapor_2026-09-21.md')
    rapor_lines = [
        '# GRAPH-INDEX-BUILD — Tür-Bazlı Index Oluşturma (2026-09-21)',
        '',
        '> **Plan C Tur 3, Seri**: 431 orphan dosyasını tür-bazlı index dosyalarına yerleştir.',
        '',
        '## Ölçüm Özeti',
        '',
        '| Metrik | Değer |',
        '|--------|-------|',
        f'| Orphan (baseline, GRAPH-HUB-EXPAND sonrası) | 431 |',
        f'| **Orphan ÖNCE** (bu görev, backup hariç) | **{orphan_once}** |',
        f'| **Orphan SONRA** | **{orphan_sonra}** |',
        f'| **İyileşme** | **−{orphan_once - orphan_sonra} (%{100*(orphan_once-orphan_sonra)/max(orphan_once,1):.1f})** |',
        f'| Index oluşturulan | {len(created_indexes)} |',
        f'| Sınıflandırılan dosya | {sum(len(v) for v in classified.values())} |',
        f'| Teknik Index | {len(classified["teknik"])} |',
        f'| OSINT Index | {len(classified["osint"])} |',
        f'| Plan Index | {len(classified["plan"])} |',
        f'| Rapor Index | {len(classified["rapor"])} |',
        '',
        '## Oluşturulan Index Dosyaları',
        ''
    ]
    
    for tip, idx_file in sorted(created_indexes.items()):
        rapor_lines.append(f'### {tip.upper()}')
        rapor_lines.append(f'- **Yol**: `{idx_file.relative_to(WORKSPACE_ROOT).as_posix()}`')
        rapor_lines.append(f'- **Dosya**: {len(classified[tip])}')
        rapor_lines.append('')
    
    rapor_lines.extend([
        '## Teknik Notlar',
        '',
        '- **Sınıflandırma**: Klasör pattern, dosya adı, YAML frontmatter tags',
        '- **Wikilink**: Full path format: `[[Huginn Data Insights/path/to/file]]`',
        '- **Atlanmış**: Canonical backup dosyaları (`.md.backup_YYYY-MM-DD`), worktree klasoru/',
        '- **SSOT**: Huginn Data Insights/ (D-172, D-177)',
        '',
        f'**Oluşturulma**: {datetime.utcnow().isoformat()}Z',
        f'**Rapor**: {rapor_file}'
    ])
    
    rapor_file.write_text('\n'.join(rapor_lines), encoding='utf-8')
    print(f"\n📄 Rapor: {rapor_file}")
    print("✅ Tamamlandı!")

if __name__ == '__main__':
    main()
