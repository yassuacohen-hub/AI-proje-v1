#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D-223: show_pano_status() handler fix — task_board.json oku, triggers/*.jsonl değil.

Sorun: show_pano_status() bekleyen_tetikler() çağrıyor ama trigger dosyaları boş/eski.
task_board.json gerçek görev kaynağı. Düzeltme: task_board.json'dan oku.
"""

import re

file_path = "src/company_master/telegram_bot.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# show_pano_status() fonksiyonunu bul ve değiştir
old_pattern = r'''def show_pano_status\(chat_id: str, status: str\) -> None:
    """Pano görevlerini durum bazında göster\."""
    try:
        logger\.info\(f"\[PANO_START\] chat_id=\{chat_id\}, status=\{status\}"\)
        
        from src\.company_master\.orchestrator\.trigger import bekleyen_tetikler
        logger\.info\(f"\[PANO\] Import OK, calling bekleyen_tetikler\('\*'\)"\)
        
        # TIMEOUT: 5 saniye
        import signal
        
        def timeout_handler\(signum, frame\):
            raise TimeoutError\("bekleyen_tetikler\(\) timeout - 5 saniye aşıldı"\)
        
        # Windows'ta signal\.SIGALRM yok; basit timeout yap
        try:
            tasks = bekleyen_tetikler\("\*"\)
            logger\.info\(f"\[PANO\] Got tasks: type=\{type\(tasks\).__name__\}, len=\{len\(tasks\) if tasks else 0\}"\)
        except TimeoutError as te:
            logger\.error\(f"\[PANO_TIMEOUT\] \{te\}"\)
            tasks = None
        
        if tasks is None:
            logger\.info\(f"\[PANO\] tasks=None, setting to \[\]"\)
            tasks = \[\]
        
        # Duruma göre filtrele
        status_map = \{
            "done": "done",
            "active": "working",
            "blocked": "blocked",
            "plan": "plan",
            "all": None
        \}
        
        logger\.info\(f"\[PANO\] Filtering \{len\(tasks\)\} tasks for status=\{status\}"\)
        filtered = tasks
        if status != "all":
            filtered = \[t for t in tasks if t\.get\("durum"\) == status_map\[status\]\]
        
        logger\.info\(f"\[PANO\] Filtered: \{len\(filtered\)\} tasks"\)'''

new_code = '''def show_pano_status(chat_id: str, status: str) -> None:
    """Pano görevlerini durum bazında göster. D-223: task_board.json'dan oku."""
    try:
        logger.info(f"[PANO_START] chat_id={chat_id}, status={status}")
        
        import json
        from pathlib import Path
        
        # task_board.json oku
        task_board_path = Path(__file__).parent.parent.parent / "data" / "orchestrator" / "task_board.json"
        logger.info(f"[PANO] Reading {task_board_path}")
        
        tasks = []
        try:
            with open(task_board_path, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            logger.info(f"[PANO] Loaded {len(tasks)} tasks from task_board.json")
        except Exception as read_err:
            logger.error(f"[PANO_READ_ERROR] {read_err}")
            tasks = []
        
        # Duruma göre filtrele
        status_map = {
            "done": "done",
            "active": "aktif",
            "blocked": "bloke",
            "plan": "plan",
            "all": None
        }
        
        logger.info(f"[PANO] Filtering {len(tasks)} tasks for status={status}")
        filtered = tasks
        if status != "all":
            target_durum = status_map.get(status, status)
            filtered = [t for t in tasks if t.get("durum") == target_durum]
        
        logger.info(f"[PANO] Filtered: {len(filtered)} tasks")'''

# Basit string replacement (regex karmaşık olduğu için)
start_idx = content.find("def show_pano_status(chat_id: str, status: str) -> None:")
if start_idx == -1:
    print("ERROR: show_pano_status() bulunamadı")
    exit(1)

# Fonksiyonun sonunu bul (next @bot.message_handler veya def)
next_func_idx = content.find("\n\ndef show_chat_status", start_idx)
if next_func_idx == -1:
    next_func_idx = content.find("\n\n@bot.message_handler", start_idx)
if next_func_idx == -1:
    print("ERROR: Fonksiyon sonu bulunamadı")
    exit(1)

# Yalnızca ilk 900 karakteri değiştir (show_pano_status başlangıç kısmı)
end_of_section = start_idx + 900
section_end = content.find("\n        lines = [f", start_idx)

old_section = content[start_idx:section_end]
new_section = new_code

content_new = content[:start_idx] + new_section + content[section_end:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content_new)

print("✅ show_pano_status() fixed — task_board.json okuma aktif")
