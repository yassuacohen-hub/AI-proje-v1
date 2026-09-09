# -*- coding: utf-8 -*-
"""İç ajan otomatik görev atama motoru.

task_board.json üzerinden görevleri anahtar kelime eşleşmesiyle
ajanlara otomatik atar.
"""

import json
import logging
from pathlib import Path
from sqlalchemy import text
from company_master.db.connection import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TASK_BOARD_PATH = Path("data/orchestrator/task_board.json")
COMPANIES_DB = "companies"
KEYWORD_MAP = {
    "ostim": "P0-1",
    "vedik": "P1-1",
    "baskent": "P1-2",
    "aso": "P1-3",
    "merge": "P1-4",
    "nace": "P1-5",
    "telegram": "P1-6",
    "quality": "P0-3",
    "recalc": "P0-2",
    "vkn": "P0-1",
    "scraper": "P0-1",
}


def load_task_board():
    """task_board.json dosyasını yükle."""
    with open(TASK_BOARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_task_board(board):
    """task_board.json dosyasını kaydet."""
    with open(TASK_BOARD_PATH, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)


def auto_assign():
    """Ana görev atama fonksiyonu."""
    board = load_task_board()
    engine = get_engine()

    # Tüm ajansları al
    with engine.connect() as conn:
        ajanslar = conn.execute(
            text("SELECT DISTINCT ajans FROM ajanslar WHERE aktif = TRUE")
        ).fetchall()

    for ajans_row in ajanslar:
        ajans = ajans_row[0]
        # Ajansa göre keyword eşleşme
        assigned_task = None
        for keyword, task_id in KEYWORD_MAP.items():
            if keyword.lower() in ajans.lower():
                assigned_task = task_id
                break

        if assigned_task:
            # Görevi ajansa ata
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "UPDATE ayarlar SET aktif_gorev = :task WHERE ajansi = :ans"
                    ),
                    {"task": assigned_task, "ans": ajans},
                )
            logger.info(f"✓ {ajans} -> {assigned_task} atandı")
        else:
            logger.warning(f"⚠ {ajans} için görev eşleşme bulunamadı")

    # Board güncelleme (tüm aktif görevleri yansıt)
    for task in board:
        if task.get("task_id") in KEYWORD_MAP.values():
            task["durum"] = "assigned"
    save_task_board(board)
    logger.info("✓ Task board güncellendi")


if __name__ == "__main__":
    auto_assign()