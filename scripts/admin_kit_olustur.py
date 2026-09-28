#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN-KİT pano kaydı oluşturması.
6 görev: UI-ADMIN-SAHTE-KPI-01 → ... → DOC-ADMIN-ARSIV-12
Pano JSON'ına görev kaydı eklemek (D-77 orkestratör görev).
"""

import json
import os
import sys
from datetime import datetime

# UTF-8 output encoding fix for Windows cmd
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Pano dosyası
PANO_PATH = "data/orchestrator/task_board.json"

# 6 ADMIN-KİT görev tanımı
ADMIN_KIT_GOREVLER = [
    {
        "task_id": "UI-ADMIN-SAHTE-KPI-01",
        "id": "UI-ADMIN-SAHTE-KPI-01",
        "baslik": "[UI] Sahte API KPI kartını düzelt → admin_kpi.py rozetli boş kart (2s)",
        "sahip": "utku",
        "oncelik": 1,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/web_dashboard/tabs/admin_kpi.py",
            "Huginn Data Insights/tests/test_admin_kpi.py"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_UI-ADMIN-SAHTE-KPI-01.md",
        "talimat": "tablo_var_mi() yardımcı yaz, test ekle, SSOT §7/§14 güncelle",
        "dependencies": []
    },
    {
        "task_id": "UI-ADMIN-SAHTE-EXEC-02",
        "id": "UI-ADMIN-SAHTE-EXEC-02",
        "baslik": "[UI] Sahte Exec kartını düzelt → admin_executive.py rozetli boş kart (2s)",
        "sahip": "utku",
        "oncelik": 2,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/web_dashboard/tabs/admin_executive.py",
            "Huginn Data Insights/tests/test_admin_executive.py"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_UI-ADMIN-SAHTE-EXEC-02.md",
        "talimat": "tablo_var_mi() kullan, test ekle, SSOT §7/§14 güncelle",
        "dependencies": ["UI-ADMIN-SAHTE-KPI-01"]
    },
    {
        "task_id": "UI-ADMIN-KULLANICI-BIRLESTIR-09",
        "id": "UI-ADMIN-KULLANICI-BIRLESTIR-09",
        "baslik": "[UI] Kullanıcı birleştirme kartını düzelt",
        "sahip": "utku",
        "oncelik": 3,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/web_dashboard/tabs/admin_kullanici_birlestir.py",
            "Huginn Data Insights/tests/test_admin_kullanici_birlestir.py"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_UI-ADMIN-KULLANICI-BIRLESTIR-09.md",
        "talimat": "Tablo kontrol, test ekle, SSOT §7/§14 güncelle",
        "dependencies": ["UI-ADMIN-SAHTE-EXEC-02"]
    },
    {
        "task_id": "UI-ADMIN-GUNCELLIK-KOVA-10",
        "id": "UI-ADMIN-GUNCELLIK-KOVA-10",
        "baslik": "[UI] Güncellik kova kartını düzelt",
        "sahip": "utku",
        "oncelik": 4,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/web_dashboard/tabs/admin_guncellik_kova.py",
            "Huginn Data Insights/tests/test_admin_guncellik_kova.py"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_UI-ADMIN-GUNCELLIK-KOVA-10.md",
        "talimat": "Tablo kontrol, test ekle, SSOT §7/§14 güncelle",
        "dependencies": ["UI-ADMIN-KULLANICI-BIRLESTIR-09"]
    },
    {
        "task_id": "UI-ADMIN-MALIYET-ANOMALI-11",
        "id": "UI-ADMIN-MALIYET-ANOMALI-11",
        "baslik": "[UI] Maliyet anomali kartını düzelt",
        "sahip": "utku",
        "oncelik": 5,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/web_dashboard/tabs/admin_cost.py",
            "Huginn Data Insights/tests/test_admin_maliyet_anomali.py"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_UI-ADMIN-MALIYET-ANOMALI-11.md",
        "talimat": "Tablo kontrol, test ekle, SSOT §7/§14 güncelle",
        "dependencies": ["UI-ADMIN-GUNCELLIK-KOVA-10"]
    },
    {
        "task_id": "DOC-ADMIN-ARSIV-12",
        "id": "DOC-ADMIN-ARSIV-12",
        "baslik": "[DOC] Admin pano arşiv günlüğü oluştur",
        "sahip": "utku",
        "oncelik": 6,
        "durum": "beklemede",
        "dosyalar": [
            "Huginn Data Insights/data/orchestrator/OTURUM_SONU_2026-09-24.md"
        ],
        "brief": "Huginn Data Insights/plans/brief_utku_DOC-ADMIN-ARSIV-12.md",
        "talimat": "Tümünü arşiv log'una ekle, SSOT §7/§14 güncelle",
        "dependencies": ["UI-ADMIN-MALIYET-ANOMALI-11"]
    }
]

def main():
    """Pano JSON'ına 6 görev ekle."""
    # Pano dosyasını oku
    try:
        with open(PANO_PATH, 'r', encoding='utf-8') as f:
            pano = json.load(f)
    except FileNotFoundError:
        print(f"Hata: {PANO_PATH} bulunamadı")
        return False
    except json.JSONDecodeError as e:
        print(f"Hata: {PANO_PATH} JSON parse hatası: {e}")
        return False

    # Var olan görev ID'lerini kontrol et
    var_olan_ids = {g.get("task_id") for g in pano}

    # Eklenecek görevleri say
    eklenen = 0
    for gorev in ADMIN_KIT_GOREVLER:
        task_id = gorev["task_id"]
        if task_id not in var_olan_ids:
            pano.append(gorev)
            eklenen += 1
            print(f"✓ {task_id} panoya eklendi")
        else:
            print(f"⚠ {task_id} zaten panoda var, atlandı")

    # Pano JSON'ını yaz
    try:
        with open(PANO_PATH, 'w', encoding='utf-8') as f:
            json.dump(pano, f, ensure_ascii=False, indent=2)
        print(f"\n✓ {eklenen} görev panoya başarıyla eklendi")
        print(f"✓ Pano dosyası güncellendi: {PANO_PATH}")
        return True
    except Exception as e:
        print(f"Hata: Pano dosyası yazılırken: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
