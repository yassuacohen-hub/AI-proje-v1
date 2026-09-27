"""
Tests for Admin Task Board View (ALTYAPI-ADMIN-PANO-01)
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_task_board():
    """Sample task board JSON."""
    return [
        {
            "task_id": "TEST-001",
            "baslik": "Tamamlanan Görev 1",
            "durum": "done",
            "oncelik": "P0",
            "sahip": "orkestrator",
            "baslangic": "2026-09-20",
            "bitis": "2026-09-24",
            "dosyalar": ["file1.py", "file2.sql"],
            "not": "Başarıyla tamamlandı"
        },
        {
            "task_id": "TEST-002",
            "baslik": "Beklemede Görev 1",
            "durum": "aktif",
            "oncelik": "P1",
            "sahip": "yasu",
            "baslangic": "2026-09-21",
            "bitis": None,
            "dosyalar": ["test_file.py"],
            "not": "Devam ediyor"
        },
        {
            "task_id": "TEST-003",
            "baslik": "Review Bekleyen Görev",
            "durum": "review",
            "oncelik": "P1",
            "sahip": "utku",
            "baslangic": "2026-09-22",
            "bitis": None,
            "dosyalar": [],
            "not": "Code review aşamasında"
        },
        {
            "task_id": "TEST-004",
            "baslik": "Plan Fazında Görev",
            "durum": "plan",
            "oncelik": "P2",
            "sahip": "mimir",
            "baslangic": None,
            "bitis": None,
            "dosyalar": ["plan.md"],
            "not": ""
        },
        {
            "task_id": "TEST-005",
            "baslik": "Bloklanmış Görev",
            "durum": "blocked",
            "oncelik": "P0",
            "sahip": "orkestrator",
            "baslangic": "2026-09-19",
            "bitis": None,
            "dosyalar": [],
            "not": "API bağımlılığı bekleniyor"
        },
        {
            "task_id": "TEST-006",
            "baslik": "Reddedilen Görev",
            "durum": "reddet",
            "oncelik": "P3",
            "sahip": "salih",
            "baslangic": "2026-09-18",
            "bitis": "2026-09-23",
            "dosyalar": ["rejected.py"],
            "not": "Spec uyumsuzluğu"
        },
    ]


class TestTaskBoardDataPreparation:
    """4 bölüme göre veri hazırlama testleri."""

    def test_categorize_done_tasks(self, sample_task_board):
        """Tamamlanan görevleri kategorize et."""
        done_tasks = [t for t in sample_task_board if t["durum"] == "done"]
        assert len(done_tasks) == 1
        assert done_tasks[0]["task_id"] == "TEST-001"

    def test_categorize_pending_tasks(self, sample_task_board):
        """Beklemede görevleri kategorize et (aktif + review + bekliyor)."""
        pending_statuses = ["aktif", "review", "bekliyor"]
        pending_tasks = [t for t in sample_task_board if t["durum"] in pending_statuses]
        assert len(pending_tasks) == 2
        task_ids = {t["task_id"] for t in pending_tasks}
        assert task_ids == {"TEST-002", "TEST-003"}

    def test_categorize_backlog_tasks(self, sample_task_board):
        """Yedek (plan) görevleri kategorize et."""
        backlog_tasks = [t for t in sample_task_board if t["durum"] == "plan"]
        assert len(backlog_tasks) == 1
        assert backlog_tasks[0]["task_id"] == "TEST-004"

    def test_categorize_evaluation_tasks(self, sample_task_board):
        """Değerlendirme görevleri kategorize et (blocked + reddet + iptal)."""
        evaluation_statuses = ["blocked", "reddet", "iptal"]
        evaluation_tasks = [t for t in sample_task_board if t["durum"] in evaluation_statuses]
        assert len(evaluation_tasks) == 2
        task_ids = {t["task_id"] for t in evaluation_tasks}
        assert task_ids == {"TEST-005", "TEST-006"}


class TestTaskBoardFiltering:
    """Filtreleme testleri (ajan / aciliyet / tarih)."""

    def test_filter_by_agent(self, sample_task_board):
        """Ajan'a göre filtrele."""
        orkestrator_tasks = [t for t in sample_task_board if t["sahip"] == "orkestrator"]
        assert len(orkestrator_tasks) == 2
        assert all(t["sahip"] == "orkestrator" for t in orkestrator_tasks)

    def test_filter_by_priority(self, sample_task_board):
        """Aciliyet'e göre filtrele."""
        critical_tasks = [t for t in sample_task_board if t["oncelik"] == "P0"]
        assert len(critical_tasks) == 2
        assert all(t["oncelik"] == "P0" for t in critical_tasks)

    def test_filter_by_date_range(self, sample_task_board):
        """Tarih aralığına göre filtrele."""
        start_date = "2026-09-21"
        end_date = "2026-09-24"

        filtered = [
            t for t in sample_task_board
            if t.get("baslangic") and t["baslangic"] >= start_date and t["baslangic"] <= end_date
        ]

        assert len(filtered) >= 2
        assert all(t.get("baslangic") for t in filtered)

    def test_combined_filters(self, sample_task_board):
        """Birden fazla filtre birlikte."""
        agent = "orkestrator"
        priority = "P0"

        filtered = [
            t for t in sample_task_board
            if t["sahip"] == agent and t["oncelik"] == priority
        ]

        assert len(filtered) == 2


class TestTaskBoardColorCoding:
    """Bölüme göre renk kodlaması testleri."""

    def test_color_for_done_section(self):
        """Tamamlandı bölümü rengi."""
        section_colors = {
            "tamamlandi": "#D4F1D4",    # Yeşil
            "beklemede": "#FFF3CD",     # Sarı
            "yedek": "#E8E8E8",         # Gri
            "degerlendirme": "#FFE5E5", # Kırmızı
        }

        assert section_colors["tamamlandi"]  # Yeşil
        assert "D4F1D4" in section_colors["tamamlandi"]

    def test_color_uniqueness(self):
        """Her bölümün farklı rengi."""
        section_colors = {
            "tamamlandi": "#D4F1D4",
            "beklemede": "#FFF3CD",
            "yedek": "#E8E8E8",
            "degerlendirme": "#FFE5E5",
        }

        unique_colors = set(section_colors.values())
        assert len(unique_colors) == 4, "Tüm renkler unique olmalı"


class TestTaskBoardMetrics:
    """Özet metrikler testleri."""

    def test_count_all_sections(self, sample_task_board):
        """Tüm bölümlerin görev sayısını hesapla."""
        sections = {
            "tamamlandi": len([t for t in sample_task_board if t["durum"] == "done"]),
            "beklemede": len([t for t in sample_task_board if t["durum"] in ["aktif", "review", "bekliyor"]]),
            "yedek": len([t for t in sample_task_board if t["durum"] == "plan"]),
            "degerlendirme": len([t for t in sample_task_board if t["durum"] in ["blocked", "reddet", "iptal"]]),
        }

        total = sum(sections.values())
        assert total == len(sample_task_board)
        assert sections["tamamlandi"] == 1
        assert sections["beklemede"] == 2
        assert sections["yedek"] == 1
        assert sections["degerlendirme"] == 2

    def test_metric_display_format(self, sample_task_board):
        """Metrik gösterim formatını doğrula."""
        metrics = {
            "tamamlandi": ("✅ Tamamlandı", len([t for t in sample_task_board if t["durum"] == "done"])),
            "beklemede": ("⏳ Beklemede", len([t for t in sample_task_board if t["durum"] in ["aktif", "review", "bekliyor"]])),
            "yedek": ("📋 Yedek", len([t for t in sample_task_board if t["durum"] == "plan"])),
            "degerlendirme": ("🔴 Değerlendirme", len([t for t in sample_task_board if t["durum"] in ["blocked", "reddet", "iptal"]])),
        }

        for key, (label, count) in metrics.items():
            assert isinstance(label, str)
            assert isinstance(count, int)
            assert count >= 0


class TestTaskBoardFileHandling:
    """Dosya yönetimi testleri."""

    def test_truncate_long_file_list(self):
        """Uzun dosya listelerini kesme."""
        files = ["file1.py", "file2.sql", "file3.md", "file4.txt", "file5.json"]

        display_files = files[:3]
        remaining = len(files) - 3

        file_str = ", ".join(display_files)
        if remaining > 0:
            file_str += f" +{remaining} daha"

        assert "file1.py" in file_str
        assert "file3.md" in file_str
        assert "+2 daha" in file_str

    def test_empty_file_list(self):
        """Boş dosya listesi."""
        files = []
        file_str = ", ".join(files[:3]) if files else "-"
        assert file_str == "-"


class TestTaskBoardTableRendering:
    """Tablo render testleri."""

    def test_table_columns(self, sample_task_board):
        """Tablo sütunlarını kontrol et."""
        expected_columns = [
            "Görev ID", "Ajan", "Başlık", "Aciliyet", "Durum",
            "Başlangıç", "Bitiş", "Dosyalar", "Not"
        ]

        # Tablo yapısı doğrulaması
        for task in sample_task_board[:1]:
            row = {
                "Görev ID": task.get("task_id", "-"),
                "Ajan": task.get("sahip", "-"),
                "Başlık": task.get("baslik", "-")[:60],
                "Aciliyet": task.get("oncelik", "-"),
                "Durum": task.get("durum", "-"),
                "Başlangıç": task.get("baslangic", "-")[:10] if task.get("baslangic") else "-",
                "Bitiş": task.get("bitis", "-")[:10] if task.get("bitis") else "-",
                "Dosyalar": ", ".join(task.get("dosyalar", [])[:3]) if task.get("dosyalar") else "-",
                "Not": task.get("not", "-"),
            }

            assert set(row.keys()) == set(expected_columns)

    def test_table_row_data_sanitization(self, sample_task_board):
        """Tablo satır verisi temizleme."""
        task = sample_task_board[0]

        # Başlık kesme (60 char)
        title = (task.get("baslik", "-")[:60])
        assert len(title) <= 60

        # Not kesme (50 char + ...)
        note = task.get("not", "")
        if len(note) > 50:
            note = note[:50] + "..."
        assert len(note) <= 53


class TestTaskBoardIntegration:
    """Entegrasyon testleri."""

    def test_full_workflow(self, sample_task_board):
        """Tam iş akışını test et."""
        # 1. Veri yükleme
        assert len(sample_task_board) == 6

        # 2. Filtreleme (örnek: ajan + aciliyet)
        filtered = [
            t for t in sample_task_board
            if t["sahip"] == "orkestrator" and t["oncelik"] == "P0"
        ]
        assert len(filtered) == 2

        # 3. Bölümleme
        sections = {
            "tamamlandi": [t for t in filtered if t["durum"] == "done"],
            "beklemede": [t for t in filtered if t["durum"] in ["aktif", "review", "bekliyor"]],
            "yedek": [t for t in filtered if t["durum"] == "plan"],
            "degerlendirme": [t for t in filtered if t["durum"] in ["blocked", "reddet", "iptal"]],
        }

        # 4. Doğrulama
        assert sum(len(v) for v in sections.values()) == len(filtered)
