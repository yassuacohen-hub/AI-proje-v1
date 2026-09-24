#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRAPH-CANONICAL: HDI iç-ikizlik canonical seçimi
- 156 grup, 426 dosya (155 grup HDI-içi, 1 grup HDI-dışı)
- A3 (100+ wikilink): canonical
- A2 (10-100 wikilink): canonical aday
- A1 (<10 wikilink): redirect → A3 veya A2
- Tiebreaker: en fazla gelen link > mtime eski > kısa ad
- Kural: HDI dosyaları güncelle; worktree klasoru/ dosyaları OLDUĞU GİBİ kalır
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE_ROOT = Path('c:/Huginn Data Projesi').resolve()

def load_ikiz_ve_links():
    """VAULT-SAGLIK-GENIS JSON'dan ikizlik + incoming link verisi yükle."""
    vault_json = WORKSPACE_ROOT / 'data/orchestrator/VAULT-SAGLIK-GENIS_2026-09-21_orkestrator.json'
    with open(vault_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ikiz_grup: {dosya_adi: [path1, path2, ...]}
    ikiz_grup = data['ikiz_grup']
    
    # ref_count'ı yeniden hesapla (JSON'da yoksa backupten al)
    # Alternatif: büyük_nodlar'dan ref_almayan_sayisi'ni kullan
    ref_count = {}
    for nod in data.get('buyuk_nodlar', []):
        # lowercase normalize et
        dosya_lower = nod['dosya'].replace('\\', '/').lower()
        ref_count[dosya_lower] = nod['referans_alinma_sayisi']
    
    return ikiz_grup, ref_count, data

def extract_wikilinks(content):
    """[[...]] sayısını say."""
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, content)
    return len(matches)

def select_canonical(grup_dosyalar, ref_count):
    """
    Tiebreaker sırası: 
    1. En fazla incoming link (gelen_link)
    2. mtime eski (authoritative)
    3. Ad kısa (simplicity)
    """
    candidates = []
    
    for yol in grup_dosyalar:
        abs_path = WORKSPACE_ROOT / yol
        
        if not abs_path.exists():
            continue
        
        try:
            content = abs_path.read_text(encoding='utf-8-sig', errors='ignore')
            wikilink_count = extract_wikilinks(content)
            mtime = abs_path.stat().st_mtime
            name_len = len(Path(yol).name)
            
            # Normalize yol lowercase
            yol_lower = yol.replace('\\', '/').lower()
            incoming = ref_count.get(yol_lower, 0)
            
            candidates.append({
                'yol': yol,
                'abs_path': abs_path,
                'wikilink': wikilink_count,
                'incoming': incoming,
                'mtime': mtime,
                'name_len': name_len,
                'content_size': len(content)
            })
        except Exception as e:
            continue
    
    if not candidates:
        return None, []
    
    # Sort: incoming desc, mtime asc, name_len asc
    candidates.sort(
        key=lambda x: (-x['incoming'], x['mtime'], x['name_len'])
    )
    
    canonical = candidates[0]
    others = candidates[1:]
    
    return canonical, others

def classify_rule(wikilink_count):
    """A3/A2/A1 sınıflandırması."""
    if wikilink_count >= 100:
        return 'A3'
    elif wikilink_count >= 10:
        return 'A2'
    else:
        return 'A1'

def create_redirect(canonical_path, other_yol):
    """Redirect backlink oluştur: [[canonical]] başına ekle."""
    # canonical_path: absolute Path
    # other_yol: vault relatif yol string
    
    # other_yol'ün dirini oku
    other_abs = WORKSPACE_ROOT / other_yol
    
    try:
        content = other_abs.read_text(encoding='utf-8-sig', errors='ignore')
    except:
        return None, "Oku başarısız"
    
    # Canonicali full path + link syntax'te yaz
    # Örn: Huginn Data Insights/CHANGELOG.md
    canonical_rel = canonical_path.relative_to(WORKSPACE_ROOT).as_posix()
    
    # Redirect link: [[Huginn Data Insights/path/to/canonical]]
    redirect_line = f"[[{canonical_rel}]]\n"
    
    # Başa ekle (frontmatter sonrası)
    lines = content.split('\n')
    
    # Frontmatter saç: --- ile başlayıp --- ile biter
    insert_idx = 0
    if lines and lines[0].strip() == '---':
        # Frontmatter bulundu
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                insert_idx = i + 1
                break
    
    # Eğer zaten redirect varsa ekleme
    if redirect_line in content:
        return content, "Zaten var"
    
    # Ekle
    new_lines = lines[:insert_idx] + [redirect_line] + lines[insert_idx:]
    new_content = '\n'.join(new_lines)
    
    return new_content, "OK"

def should_update_file(yol):
    """
    D-172: worktree klasoru/ altındaki dosyalar OLDUĞU GİBİ kalır.
    Diğerleri (HDI içinde) güncelleniyor.
    """
    yol_lower = yol.replace('\\', '/').lower()
    if yol_lower.startswith('worktree klasoru/'):
        return False
    return True

def main():
    print("=" * 80)
    print("GRAPH-CANONICAL: HDI İç-İkizlik Canonical Seçimi")
    print("=" * 80)
    
    # Veri yükle
    ikiz_grup, ref_count, vault_data = load_ikiz_ve_links()
    print(f"\n✓ {len(ikiz_grup)} ikizlik grubu yüklendi")
    print(f"✓ {vault_data['istatistik']['ikiz_dosya_toplam']} toplam ikiz dosya")
    
    # Sonuç raporu
    rapor = {
        'metadata': {
            'olusturulma': datetime.now(timezone.utc).isoformat(),
            'kaynak': 'VAULT-SAGLIK-GENIS_2026-09-21_orkestrator.json',
            'kural': 'A3≥100wikilink:canonical | A2[10-100]:aday | A1<10:redirect',
            'tiebreaker': 'incoming_links desc > mtime asc > name_len asc',
            'constraint': 'worktree klasoru/ OLDUĞU GİBİ, HDI dosyaları güncelle'
        },
        'istatistik': {
            'toplam_grup': len(ikiz_grup),
            'hdi_disi_grup': 0,
            'a3_sayi': 0,
            'a2_sayi': 0,
            'a1_sayi': 0,
            'redirect_yapilacak': 0,
            'guncelleme_yapilacak': 0
        },
        'grupplar': []
    }
    
    updated_files = {}  # yol -> new_content
    
    # Grup analizi
    for grup_adi, dosyalar in ikiz_grup.items():
        canonical_data, others = select_canonical(dosyalar, ref_count)
        
        if not canonical_data:
            continue
        
        canonical_yol = canonical_data['yol']
        canonical_rule = classify_rule(canonical_data['wikilink'])
        
        # Grup türü (HDI-içi vs dışı)
        hdi_icinde = all(d.startswith('Huginn Data Insights') for d in dosyalar)
        grup_turu = 'HDI-içi' if hdi_icinde else 'HDI-dışı'
        
        if not hdi_icinde:
            rapor['istatistik']['hdi_disi_grup'] += 1
        
        # Rule sayısını artır
        if canonical_rule == 'A3':
            rapor['istatistik']['a3_sayi'] += 1
        elif canonical_rule == 'A2':
            rapor['istatistik']['a2_sayi'] += 1
        else:
            rapor['istatistik']['a1_sayi'] += 1
        
        grup_rapor = {
            'grup_adi': grup_adi,
            'turu': grup_turu,
            'dosya_sayisi': len(dosyalar),
            'canonical': {
                'yol': canonical_yol,
                'kural': canonical_rule,
                'incoming_link': canonical_data['incoming'],
                'wikilink_sayisi': canonical_data['wikilink'],
                'mtime': datetime.fromtimestamp(canonical_data['mtime']).isoformat(),
                'gupdater_degistirilecek': should_update_file(canonical_yol)
            },
            'redirect': []
        }
        
        # Diğer dosyalar → redirect
        for other in others:
            other_yol = other['yol']
            should_update = should_update_file(other_yol)
            
            if should_update:
                rapor['istatistik']['redirect_yapilacak'] += 1
                rapor['istatistik']['guncelleme_yapilacak'] += 1
                
                # Redirect oluştur
                new_content, status = create_redirect(canonical_data['abs_path'], other_yol)
                if status == "OK":
                    updated_files[other_yol] = new_content
                
                grup_rapor['redirect'].append({
                    'yol': other_yol,
                    'kural': classify_rule(other['wikilink']),
                    'incoming_link': other['incoming'],
                    'wikilink_sayisi': other['wikilink'],
                    'durum': status,
                    'guncellenecek': True
                })
            else:
                # worktree klasoru/ — skip
                grup_rapor['redirect'].append({
                    'yol': other_yol,
                    'durum': 'SKIP (D-172: worktree SSOT)',
                    'guncellenecek': False
                })
        
        rapor['grupplar'].append(grup_rapor)
    
    # Rapor yaz
    rapor_path = WORKSPACE_ROOT / 'data/orchestrator/GRAPH-CANONICAL_rapor_2026-09-21.md'
    
    # Markdown biçimi
    md_rapor = generate_markdown_rapor(rapor)
    rapor_path.write_text(md_rapor, encoding='utf-8')
    print(f"\n✓ Rapor yazıldı: {rapor_path.relative_to(WORKSPACE_ROOT)}")
    
    # JSON rapor da yaz
    json_rapor_path = WORKSPACE_ROOT / 'data/orchestrator/GRAPH-CANONICAL_rapor_2026-09-21.json'
    with open(json_rapor_path, 'w', encoding='utf-8') as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON rapor yazıldı: {json_rapor_path.relative_to(WORKSPACE_ROOT)}")
    
    # İstatistik
    print(f"\n📊 İstatistik:")
    print(f"   A3 (100+ wikilink): {rapor['istatistik']['a3_sayi']}")
    print(f"   A2 (10-100 wikilink): {rapor['istatistik']['a2_sayi']}")
    print(f"   A1 (<10 wikilink): {rapor['istatistik']['a1_sayi']}")
    print(f"   Redirect eklenecek: {rapor['istatistik']['redirect_yapilacak']}")
    print(f"   Güncelleme yapılacak: {rapor['istatistik']['guncelleme_yapilacak']}")
    print(f"   HDI-dışı grup: {rapor['istatistik']['hdi_disi_grup']}")
    
    # Dosya güncelleme prompt
    if updated_files:
        print(f"\n⚠️  {len(updated_files)} dosya güncelleme hazır (teyit bekleniyor)")
        print("\nGÜNCELLEME YAPILACAK:")
        for yol in sorted(updated_files.keys())[:10]:  # İlk 10'u göster
            print(f"  - {yol}")
        if len(updated_files) > 10:
            print(f"  ... ve {len(updated_files) - 10} diğer dosya")

def generate_markdown_rapor(rapor):
    """Markdown format rapor oluştur."""
    md = []
    md.append("# GRAPH-CANONICAL Rapor")
    md.append(f"**Tarih:** {rapor['metadata']['olusturulma']}")
    md.append(f"**Kural:** {rapor['metadata']['kural']}")
    md.append(f"**Tiebreaker:** {rapor['metadata']['tiebreaker']}")
    md.append("")
    
    st = rapor['istatistik']
    md.append("## İstatistik")
    md.append(f"| Metrik | Değer |")
    md.append("|--------|-------|")
    md.append(f"| Toplam grup | {st['toplam_grup']} |")
    md.append(f"| A3 (100+ wikilink) | {st['a3_sayi']} |")
    md.append(f"| A2 (10-100 wikilink) | {st['a2_sayi']} |")
    md.append(f"| A1 (<10 wikilink) | {st['a1_sayi']} |")
    md.append(f"| Redirect eklenecek | {st['redirect_yapilacak']} |")
    md.append(f"| Güncellenecek dosya | {st['guncelleme_yapilacak']} |")
    md.append(f"| HDI-dışı grup | {st['hdi_disi_grup']} |")
    md.append("")
    
    md.append("## Gruplar (ilk 10)")
    for i, grup in enumerate(rapor['grupplar'][:10], 1):
        md.append(f"### {i}. {grup['grup_adi']} ({grup['turu']}) — {grup['dosya_sayisi']} dosya")
        md.append(f"**Canonical:** `{grup['canonical']['yol']}` ({grup['canonical']['kural']})")
        md.append(f"- Gelen link: {grup['canonical']['incoming_link']}")
        md.append(f"- Wikilink: {grup['canonical']['wikilink_sayisi']}")
        md.append("")
        
        if grup['redirect']:
            md.append("**Redirect:**")
            for r in grup['redirect']:
                durum = "✓" if r['guncellenecek'] else "⊘"
                md.append(f"- {durum} `{r['yol']}` ({r['durum']})")
        md.append("")
    
    if len(rapor['grupplar']) > 10:
        md.append(f"... ve {len(rapor['grupplar']) - 10} diğer grup")
    
    return '\n'.join(md)

if __name__ == '__main__':
    main()
