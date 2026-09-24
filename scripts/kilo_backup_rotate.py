#!/usr/bin/env python3
"""
KILO Yedek Rotasyon Politikası (D-176)
- En yeni N yedek tut, kalanları arşive taşı (silme yok)
- Idempotent: tekrar çalıştırılırsa hata vermesin
- Log çıktısı üretsin
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# Konfigürasyon
SCRIPT_DIR = Path(__file__).parent.parent  # c:/Huginn Data Projesi
BACKUPS_DIR = SCRIPT_DIR / ".kilo" / "backups"
ARCHIVE_DIR = SCRIPT_DIR / ".kilo" / "backups_arşiv"
KEEP_COUNT = 3
LOG_FILE = SCRIPT_DIR / "data" / "orchestrator" / ".kilo_rotate_log.txt"

def get_backup_files():
    """Yedek dosyalarını oluşturulma tarihine göre sırala (en yeni son)"""
    if not BACKUPS_DIR.exists():
        return []
    
    files = []
    for item in BACKUPS_DIR.iterdir():
        if item.is_file():
            stat = item.stat()
            files.append({
                'path': item,
                'name': item.name,
                'mtime': stat.st_mtime,
                'size': stat.st_size
            })
    
    # Oluşturulma tarihine göre ters sırala (en yeni ilk)
    return sorted(files, key=lambda x: x['mtime'], reverse=True)

def rotate_backups():
    """Rotasyonu gerçekleştir"""
    files = get_backup_files()
    
    if len(files) <= KEEP_COUNT:
        return {
            'status': 'noop',
            'message': f'Yedek sayısı ({len(files)}) limit ({KEEP_COUNT}) altında, taşıma gerekli değil',
            'kept': len(files),
            'moved': 0,
            'files_kept': [f['name'] for f in files],
            'files_moved': []
        }
    
    # Arşiv klasörünü oluştur (varsa sorun yok)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    kept_files = files[:KEEP_COUNT]
    to_archive = files[KEEP_COUNT:]
    
    moved_count = 0
    moved_files = []
    errors = []
    
    for item in to_archive:
        src = item['path']
        dest = ARCHIVE_DIR / item['name']
        
        try:
            # Hedef zaten varsa, taşıma (idempotent)
            if dest.exists():
                # Aynı dosya zaten arşivde
                try:
                    src.unlink()  # Kaynağı sil (artık gerek yok)
                    moved_count += 1
                    moved_files.append(item['name'])
                except Exception as e:
                    errors.append(f"{item['name']}: sil hatası - {e}")
            else:
                # Yeni taşıma
                shutil.move(str(src), str(dest))
                moved_count += 1
                moved_files.append(item['name'])
        except Exception as e:
            errors.append(f"{item['name']}: taşıma hatası - {e}")
    
    return {
        'status': 'success',
        'message': f'{moved_count} dosya arşive taşındı, {KEEP_COUNT} tutuldu',
        'kept': KEEP_COUNT,
        'moved': moved_count,
        'files_kept': [f['name'] for f in kept_files],
        'files_moved': moved_files,
        'errors': errors if errors else None
    }

def log_result(result):
    """Sonucu log dosyasına yaz ve konsola yazdır"""
    timestamp = datetime.now().isoformat()

    # Log ÖNCE yazılır: konsol encoding hatası logu engellemesin
    log_entry = {
        'timestamp': timestamp,
        'status': result['status'],
        'kept': result['kept'],
        'moved': result['moved'],
        'files_moved': result['files_moved'],
        'errors': result.get('errors')
    }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Uyari: Log yazilamadi - {e}")

    # Konsol ciktisi saf ASCII: Task Scheduler cp850 konsolunda UnicodeEncodeError olmaz
    print(f"\n{'='*70}")
    print(f"KILO Yedek Rotasyon - {timestamp}")
    print(f"{'='*70}")
    print(f"Durum: {result['status'].upper()}")
    print(f"Tutulan: {result['kept']} dosya")
    print(f"Tasinan: {result['moved']} dosya")

    if result['files_kept']:
        print("\nTutulan dosyalar:")
        for name in result['files_kept']:
            print(f"  [+] {name}")

    if result['files_moved']:
        print("\nArsive tasinan dosyalar:")
        for name in result['files_moved']:
            print(f"  [>] {name}")

    if result.get('errors'):
        print("\nHatalar:")
        for err in result['errors']:
            print(f"  [!] {err}")

    print(f"Log: {LOG_FILE}")
    print(f"{'='*70}\n")

def main():
    """Ana işlem"""
    try:
        result = rotate_backups()
        log_result(result)
        return 0 if result['status'] in ['noop', 'success'] else 1
    except Exception as e:
        print(f"HATA: Rotasyon başarısız - {e}")
        return 1

if __name__ == '__main__':
    exit(main())
